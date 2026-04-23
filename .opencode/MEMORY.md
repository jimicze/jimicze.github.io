# Memory

<!-- Agent: update this file when making architectural decisions, discovering patterns, or recording user preferences. -->

---

## Decisions

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-23 | **JSON Resume** as internal CV data model | Open standard, MIT, active ecosystem (50+ themes), good tooling, supports all needed fields. Extended with `_meta` prefix fields. |
| 2026-04-23 | **LLM = local first** (LM Studio / Ollama), GitHub Copilot as secondary | No API key or external cost. LM Studio on `localhost:1234` (OpenAI-compatible). Ollama on `localhost:11434`. |
| 2026-04-23 | **Live HTML CV = GitHub Pages** on `github.com/jimicze` | User requested hosting on their GitHub profile (jimicze). GitHub Pages is free, version-controlled, and co-located with their profile. Replaces the earlier "local-only" decision. |
| 2026-04-23 | **Europass variant = V2** | Not required for V1. Will reuse the same data model with a different Jinja2 template. |
| 2026-04-23 | **HTML + CSS + @media print** as primary output pipeline | Live editing, variant switching via CSS classes, PDF via Playwright/WeasyPrint. Avoids DOCX-to-PDF complexity. |
| 2026-04-23 | **Playwright** for visual PDF variants, **WeasyPrint** for ATS-safe/compliance variant | Playwright has best CSS3 support; WeasyPrint has best CSS Paged Media + explicit link preservation. |
| 2026-04-23 | **DOCX via `docxtpl`** (template-based) not `python-docx` (code-based) | docxtpl lets us maintain a designed Word template and inject data via Jinja2 — much better for complex formatting. |
| 2026-04-23 | **Tiptap v2** for rich-text editing in CV editor | React-native ProseMirror wrapper, MIT, best UX/ecosystem balance. |
| 2026-04-23 | **No multi-column layouts** in any output variant | Multi-column fails across Taleo, iCIMS, and legacy ATS. All variants are single-column. |
| 2026-04-23 | **Custom ATS scorer** (spaCy + keybert) not external API dependency | MVP independence; Affinda optionally added later for advanced parsing. |
| 2026-04-23 | **Europass = output variant only** (not internal model) | No public Europass CV API. Internal model is JSON Resume; Europass is just a template with different section structure. |
| 2026-04-23 | JSON/TOML/YAML/Markdown as **internal data layer only** | User explicitly does not want to hand-edit raw data formats. |
| 2026-04-23 | `docs/CV-Lasak-EN-Dec-2025.pdf` is **read-only** canonical source | This is the ground truth. All work derives from it. Never overwrite. |
| 2026-04-23 | Skills: install PDF and DOCX as **separate official skills** | No combined skill exists; `anthropics/skills@pdf` + `@docx` are highest-install and best-coverage options. |

---

## Patterns

### Data → Template → Output (core pipeline)
Extract structured CV data once from the source PDF → store in `data/cv.json` (JSON Resume) → feed multiple templates from one source. Never duplicate data across templates.

### Variant switching via CSS classes + build flag
```css
/* Photo toggle */
.variant-no-photo .profile-photo { display: none; }

/* Color toggle */
:root {
  --accent-color: #2E75B6;   /* color variants */
  --accent-color: #555;       /* simple/ats-safe variants */
}
```
Single HTML template; variant driven by class on `<html>` or `<body>`. No separate template files per variant.

### ATS-safe = strictest constraints, others relax from there
- `ats-safe`: single col, no photo, no color, standard headings, no graphics, no icon fonts, contact in body
- `simple`: add minimal color, still no photo
- `color`: add brand color, still no photo, still single col
- `full`: add photo + color, still single col

### Cover letter = same pipeline
Cover letter generation reuses the same data model + Jinja2 + PDF/DOCX pipeline. Input: `data/cv.json` + job description → LLM output → render.

### Hyperlink preservation is a first-class requirement
All output formats must preserve clickable links:
- HTML: `<a href="..." target="_blank">`
- PDF (WeasyPrint): handles automatically; Playwright preserves in practice
- DOCX: requires Word hyperlink XML fields (not plain text) — use docxtpl or python-docx XML injection

### LLM usage is bounded
LLM is used for:
1. Structuring extracted CV text → JSON Resume fields (one-time extraction)
2. JD keyword extraction and requirement parsing
3. Cover letter generation

LLM is NOT used for:
- ATS scoring (rule-based + spaCy)
- Template rendering
- PDF/DOCX generation

### "Never fabricate" rule for LLM operations
All LLM-generated content (cover letters, rewritten bullets) must be traceable to facts in `data/cv.json`. The system must flag when a JD requirement has no matching CV evidence and must not invent experiences.

---

## User Preferences

- **No hand-editing of raw data files** — never expose JSON/TOML/YAML/Markdown as the primary editing surface.
- **Editing via browser UI** — HTML live editor (Tiptap + structured forms) is the target UX.
- **Multiple CV variants required**: at minimum `ats-safe`, `color`, `full`. Europass for EU applications.
- **Cover letter generator** is a future epic, driven by job-description document input.
- **Hyperlinks are critical**: LinkedIn, GitHub, email, portfolio must be clickable in all output formats.
- **ATS score first** — primary value is ATS pass rate; visual design is secondary.
- **Privacy**: no CV data to external services by default. LLM API calls are opt-in.

---

## Project Notes

### Owner
- **Name**: Ondřej Lasák (Ondrej Lasak)
- **Email**: ondra.lasak@gmail.com
- **LinkedIn**: cz.linkedin.com/in/lasakondrej/
- **GitHub**: https://github.com/jimicze
- **Location**: Prague, Czech Republic
- **Role**: Senior Software Automation Quality Engineer
- **Specialty**: Playwright (TS + C#), Selenium, K6, JMeter, BDD/SpecFlow, GenAI/MCP/RAG, Azure DevOps
- **Experience**: 13+ years QA/test automation
- **Languages**: Czech (native), English B2, Polish B2, Slovak B2

### Source CV (both files READ-ONLY — never overwrite)
| File | Format | Notes |
|------|--------|-------|
| `docs/CV-Lasak-EN-Dec-2025.pdf` | PDF 1.3, macOS Quartz, Europass EN, 6 pages | Primary source; text-based (not scanned) |
| `docs/CV-Lasak-EN 18.docx` | Word DOCX, EN | ⚠️ Filename has a space — always quote path |

Cross-validate extracted `data/cv.json` against both files for completeness.

### Installed Global Agent Skills
| Skill | Risk | Path | Purpose |
|-------|------|------|---------|
| `anthropics/skills@pdf` | ⚠️ Snyk High Risk | `~/.agents/skills/pdf` | PDF read/extract/manipulate |
| `anthropics/skills@docx` | ✅ Snyk Low Risk | `~/.agents/skills/docx` | DOCX read/create/edit |

### Tech Stack (decided in PRD §4.4)
| Layer | Tool |
|-------|------|
| Backend | Python 3.11+ + FastAPI |
| Frontend | TypeScript + React + Vite |
| CV data | JSON Resume schema + `_meta` extensions |
| HTML templates | Jinja2 + Tailwind CSS (print-optimized) |
| PDF (visual) | Playwright `page.pdf()` |
| PDF (ATS-safe) | WeasyPrint |
| DOCX | `docxtpl` (template-based) |
| CV parsing | `pdfplumber` + `pypdf` + LLM structuring |
| ATS scoring | `spaCy` + `keybert` + `sentence-transformers` |
| Rich text editor | Tiptap v2 |
| LLM | Anthropic Claude API |
| Docker base | `mcr.microsoft.com/playwright/python:latest` |

### Repo State (2026-04-23)
- No source code yet.
- `docs/CV-Lasak-EN-Dec-2025.pdf` is the only content artifact.
- `AGENTS.md`, `PRD.md` written in first session.
- `.opencode/*.md` fully structured and populated with research.
- **Directory scaffold in place**: `src/`, `data/`, `templates/html/{ats,color,simple,full}/`, `templates/docx/`, `output/`, `tests/`
- **`pyproject.toml`** and **`package.json`** written; deps declared but NOT yet installed.
- **`.gitignore`** in place.
- **Hard dependency**: extracting `data/cv.json` unlocks all Epic 1 work.

### Key Reference Projects
| Project | URL | What to borrow |
|---------|-----|----------------|
| Reactive Resume | https://github.com/AmruthPillai/Reactive-Resume | Live editor UX, template structure |
| Open Resume | https://github.com/xitanggg/open-resume | ATS PDF builder, client-side parser |
| JSON Resume | https://jsonresume.org | Data schema, theme ecosystem |
| CoverLetterGPT | https://github.com/vincanger/coverlettergpt | Cover letter gen pattern |
| Resume Matcher | https://github.com/srbhr/Resume-Matcher | JD ↔ CV matching |
