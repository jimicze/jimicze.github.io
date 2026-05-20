"""
CV renderer — Jinja2 HTML, WeasyPrint PDF, docxtpl DOCX.

Usage:
    python -m src.render html  --variant ats  --out public/index.html
    python -m src.render pdf   --variant ats  --out output/cv-ats-safe.pdf
    python -m src.render docx  --template templates/docx/cv-recruiter.docx \\
                               --out output/cv-recruiter.docx

All subcommands accept an optional --cv flag to override the default
data/cv.json path.
"""
from __future__ import annotations

import argparse
import json
import re
import tempfile
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from src.models import CvData, WorkEntry

# ── Default paths ─────────────────────────────────────────────────────────────

REPO_ROOT = Path(__file__).resolve().parent.parent
CV_JSON = REPO_ROOT / "data" / "cv.json"
TEMPLATES_DIR = REPO_ROOT / "templates" / "html"

# ── Jinja2 filters ────────────────────────────────────────────────────────────

_MONTH_ABBR: dict[int, str] = {
    1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
    7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec",
}


def _fmt_date(value: str | None) -> str:
    """Format a YYYY-MM or YYYY date string for human display.

    Examples::

        _fmt_date("2025-07")  # → "Jul 2025"
        _fmt_date("2009")     # → "2009"
        _fmt_date(None)       # → "Present"
        _fmt_date("")         # → "Present"
    """
    value = (value or "").strip()
    if not value:
        return "Present"
    if re.fullmatch(r"\d{4}-\d{2}", value):
        year, month = int(value[:4]), int(value[5:7])
        return f"{_MONTH_ABBR[month]} {year}"
    if re.fullmatch(r"\d{4}", value):
        return value
    # Fallback — return as-is (unexpected format)
    return value


def _fmt_year(value: str | None) -> str:
    """Return only the year portion of a date string (used for education).

    Examples::

        _fmt_year("2009")     # → "2009"
        _fmt_year("2009-09")  # → "2009"
        _fmt_year(None)       # → ""
    """
    if not value:
        return ""
    value = value.strip()
    if re.fullmatch(r"\d{4}-\d{2}", value):
        return value[:4]
    return value


def _format_phone(value: str | None) -> str:
    """Format a phone number string for display.

    Czech mobile (+420XXXXXXXXX) → "+420 XXX XXX XXX".
    Falls back to inserting spaces every 3 digits after the country code.

    Examples::

        _format_phone("+420739820982")  # → "+420 739 820 982"
    """
    if not value:
        return value or ""
    digits = re.sub(r"\s+", "", value)  # strip any existing whitespace
    # Czech: +420 followed by exactly 9 digits
    m = re.fullmatch(r"(\+420)(\d{3})(\d{3})(\d{3})", digits)
    if m:
        return f"{m.group(1)} {m.group(2)} {m.group(3)} {m.group(4)}"
    # Generic: country code + remaining digits in groups of 3
    m2 = re.fullmatch(r"(\+\d{1,3})(\d+)", digits)
    if m2:
        cc, rest = m2.group(1), m2.group(2)
        groups = [rest[i : i + 3] for i in range(0, len(rest), 3)]
        return f"{cc} {' '.join(groups)}"
    return value


# ── Work grouping ─────────────────────────────────────────────────────────────


def _group_work(work: list[WorkEntry]) -> list[dict]:
    """Group consecutive work entries at the same company.

    Returns a list of dicts — one of two shapes:

    Single-role entry::

        {"grouped": False, "entry": <WorkEntry>}

    Multi-role group (e.g. three roles at Vendavo)::

        {
            "grouped":    True,
            "name":       str,
            "url":        str | None,
            "location":   str | None,
            "start_date": str | None,   # earliest startDate across all roles
            "end_date":   str | None,   # latest endDate (None = Present)
            "entries":    list[WorkEntry],  # original order from cv.json
        }

    Entries within each group keep the cv.json order (newest first).
    """
    if not work:
        return []

    groups: list[dict] = []
    current_name = work[0].name
    current_entries: list[WorkEntry] = [work[0]]

    for entry in work[1:]:
        if entry.name == current_name:
            current_entries.append(entry)
        else:
            groups.append(_flush_group(current_entries))
            current_name = entry.name
            current_entries = [entry]

    groups.append(_flush_group(current_entries))
    return groups


def _flush_group(entries: list[WorkEntry]) -> dict:
    """Convert a list of same-company WorkEntry objects into a group dict."""
    if len(entries) == 1:
        return {"grouped": False, "entry": entries[0]}

    # Determine overall date span (entries in cv.json are newest-first)
    start_dates = [e.startDate for e in entries if e.startDate]
    end_dates_raw = [e.endDate for e in entries]

    start_date: str | None = min(start_dates) if start_dates else None
    # None end_date means "Present" — if any entry is open, the group is open
    end_date: str | None = (
        None
        if any(d is None for d in end_dates_raw)
        else max(d for d in end_dates_raw if d)  # type: ignore[type-var]
    )

    first = entries[0]  # use first (newest) entry for url/location metadata
    return {
        "grouped": True,
        "name": first.name,
        "url": first.url,
        "location": first.location,
        "start_date": start_date,
        "end_date": end_date,
        "entries": entries,
    }


# ── Data loading ──────────────────────────────────────────────────────────────


def load_cv(path: Path = CV_JSON) -> CvData:
    """Load and validate cv.json against the CvData Pydantic model.

    Raises:
        FileNotFoundError: If the CV JSON file does not exist.
        pydantic.ValidationError: If the JSON does not match the schema.
    """
    if not path.exists():
        raise FileNotFoundError(
            f"CV data file not found: {path}\n"
            "Run the extraction pipeline first: python -m src.extract"
        )
    raw = json.loads(path.read_text(encoding="utf-8"))
    return CvData.model_validate(raw)


# ── Jinja2 environment ────────────────────────────────────────────────────────


def _make_jinja_env(variant: str) -> Environment:
    """Return a Jinja2 Environment with custom filters for the given variant.

    The loader is pointed at ``templates/html/<variant>/`` so that
    ``{% extends "base.html.j2" %}`` resolves within the same directory.

    Raises:
        FileNotFoundError: If the variant template directory does not exist.
    """
    variant_dir = TEMPLATES_DIR / variant
    if not variant_dir.is_dir():
        available = [d.name for d in TEMPLATES_DIR.iterdir() if d.is_dir()]
        raise FileNotFoundError(
            f"Template directory not found: {variant_dir}\n"
            f"Available variants: {available}"
        )
    env = Environment(
        loader=FileSystemLoader(str(variant_dir)),
        undefined=StrictUndefined,
        autoescape=False,   # CV content is trusted; autoescape would mangle special chars
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.filters["fmt_date"] = _fmt_date
    env.filters["fmt_year"] = _fmt_year
    env.filters["format_phone"] = _format_phone
    return env


# ── Renderers ─────────────────────────────────────────────────────────────────


def render_html(cv: CvData, variant: str, output_path: Path) -> None:
    """Render CV data to HTML using the Jinja2 template for the given variant.

    Args:
        cv:          Validated CvData instance.
        variant:     Template variant folder name (e.g. ``"ats"``, ``"color"``).
        output_path: Destination path for the rendered HTML file.
    """
    env = _make_jinja_env(variant)
    template = env.get_template("index.html.j2")
    context = {
        "cv": cv,
        "grouped_work": _group_work(cv.work),
        "variant": variant,
    }
    html = template.render(**context)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")
    print(f"✅ HTML written → {output_path}")


def export_pdf_ats(html_path: Path, pdf_path: Path) -> None:
    """Export an ATS-safe PDF from a rendered HTML file using WeasyPrint.

    WeasyPrint preserves hyperlinks natively (``<a href="">`` → clickable PDF
    annotations).  The output is a clean, single-column, machine-readable PDF
    that passes common ATS text-extraction checks.

    Args:
        html_path: Path to the source HTML file (produced by :func:`render_html`).
        pdf_path:  Destination path for the output PDF.

    Raises:
        ImportError:      If WeasyPrint is not installed.
        FileNotFoundError: If ``html_path`` does not exist.
    """
    try:
        from weasyprint import HTML as WeasyprintHTML  # noqa: PLC0415
    except ImportError as exc:
        raise ImportError(
            "WeasyPrint is not installed. Run: pip install weasyprint"
        ) from exc

    if not html_path.exists():
        raise FileNotFoundError(f"Source HTML not found: {html_path}")

    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    WeasyprintHTML(filename=str(html_path)).write_pdf(str(pdf_path))
    print(f"✅ PDF written  → {pdf_path}")


def export_docx(cv: CvData, template_path: Path, output_path: Path) -> None:
    """Render a DOCX file from a docxtpl template and the CV data.

    The template uses ``{{ }}`` Jinja2-style placeholders.  See
    ``templates/docx/cv-recruiter.docx`` for the placeholder schema.

    Args:
        cv:            Validated CvData instance.
        template_path: Path to the ``.docx`` template with ``{{ }}`` placeholders.
        output_path:   Destination path for the generated ``.docx`` file.

    Raises:
        ImportError:       If docxtpl is not installed.
        FileNotFoundError: If ``template_path`` does not exist.
    """
    try:
        from docxtpl import DocxTemplate  # noqa: PLC0415
    except ImportError as exc:
        raise ImportError(
            "docxtpl is not installed. Run: pip install docxtpl"
        ) from exc

    if not template_path.exists():
        raise FileNotFoundError(f"DOCX template not found: {template_path}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc = DocxTemplate(str(template_path))
    context: dict = {
        "cv": cv,
        "grouped_work": _group_work(cv.work),
        "fmt_date": _fmt_date,
        "fmt_year": _fmt_year,
    }
    doc.render(context)
    doc.save(str(output_path))
    print(f"✅ DOCX written → {output_path}")


# ── CLI ───────────────────────────────────────────────────────────────────────


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m src.render",
        description="ATS-CV renderer — produce HTML, PDF, or DOCX from data/cv.json",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--cv",
        type=Path,
        default=CV_JSON,
        metavar="PATH",
        help="Path to the source cv.json",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # ── html ──────────────────────────────────────────────────────────────────
    html_p = sub.add_parser("html", help="Render an HTML CV")
    html_p.add_argument(
        "--variant",
        default="ats",
        choices=["ats", "color", "simple", "full"],
        help="Template variant to use",
    )
    html_p.add_argument(
        "--out",
        type=Path,
        default=REPO_ROOT / "public" / "index.html",
        metavar="PATH",
        help="Output HTML file path",
    )

    # ── pdf ───────────────────────────────────────────────────────────────────
    pdf_p = sub.add_parser(
        "pdf",
        help="Export an ATS-safe PDF via WeasyPrint (renders HTML first if needed)",
    )
    pdf_p.add_argument(
        "--variant",
        default="ats",
        choices=["ats", "color", "simple", "full"],
        help="Template variant to use when rendering the intermediate HTML",
    )
    pdf_p.add_argument(
        "--html",
        type=Path,
        default=None,
        metavar="PATH",
        help="Use an already-rendered HTML file instead of re-rendering",
    )
    pdf_p.add_argument(
        "--out",
        type=Path,
        default=REPO_ROOT / "output" / "cv-ats-safe.pdf",
        metavar="PATH",
        help="Output PDF file path",
    )

    # ── docx ──────────────────────────────────────────────────────────────────
    docx_p = sub.add_parser("docx", help="Export a recruiter-editable DOCX")
    docx_p.add_argument(
        "--template",
        type=Path,
        default=REPO_ROOT / "templates" / "docx" / "cv-recruiter.docx",
        metavar="PATH",
        help="Path to the docxtpl .docx template",
    )
    docx_p.add_argument(
        "--out",
        type=Path,
        default=REPO_ROOT / "output" / "cv-recruiter.docx",
        metavar="PATH",
        help="Output DOCX file path",
    )

    return parser


def main() -> None:
    """CLI entry point — parse arguments and dispatch to the appropriate renderer."""
    parser = _build_parser()
    args = parser.parse_args()
    cv = load_cv(args.cv)

    if args.command == "html":
        render_html(cv, args.variant, args.out)

    elif args.command == "pdf":
        if args.html:
            html_path = args.html
            export_pdf_ats(html_path, args.out)
        else:
            # Render HTML to a temporary file, then convert to PDF
            with tempfile.NamedTemporaryFile(
                suffix=".html", delete=False, mode="w", encoding="utf-8"
            ) as tmp:
                tmp_path = Path(tmp.name)
            try:
                render_html(cv, args.variant, tmp_path)
                export_pdf_ats(tmp_path, args.out)
            finally:
                if tmp_path.exists():
                    tmp_path.unlink()

    elif args.command == "docx":
        export_docx(cv, args.template, args.out)


if __name__ == "__main__":
    main()
