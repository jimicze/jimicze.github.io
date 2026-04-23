# Learnings

<!-- Most recent entries first, grouped by category. Agent: update this file every time you resolve a bug, encounter a gotcha, or learn something non-obvious. -->

---

## ATS / CV Domain

### 2026-04-23 — ATS system-specific parsing quirks (CRITICAL)

- **Taleo (Oracle HCM)**: Oldest/strictest parser. Non-standard section headings are silently dropped. Multi-column = complete garble. Submit DOCX if given option.
- **iCIMS**: Historically uses RChilli parser. Weakest PDF parser in enterprise segment. DOCX strongly recommended. Two-column layouts fail catastrophically.
- **Workday**: Own in-house parser since 2022 (replaced Sovren). Uses Workday Skills Cloud taxonomy. Good PDF handling but struggles with decorative elements. Re-entry often required despite parsing.
- **Greenhouse**: Uses Textkernel (formerly Sovren) parser. Excellent PDF handling. Strong semantic matching for tech roles.
- **Lever**: Modern parser. Good with standard PDF typography. Handles both PDF and DOCX well.
- **SmartRecruiters**: Modern architecture. Good parser. Handles most single-column layouts.

### 2026-04-23 — ATS formatting rules (universal)

- **Single column is mandatory** for ATS-safe variant — multi-column fails across Taleo, iCIMS, and legacy systems (~34% worse parsing rate).
- **Standard section headings required**: "Work Experience", "Education", "Skills", "Certifications", "Summary" — never use creative alternatives.
- **No tables for layout** — table content is read out of order by all parsers.
- **No headers/footers with critical data** — many ATS strip them; put everything (name, contact) in the body.
- **No text boxes in DOCX** — text box content is completely invisible to all ATS.
- **No icon fonts** — render as garbage characters. Use Unicode symbols sparingly.
- **Date format**: "Month YYYY – Month YYYY" (e.g., "March 2023 – Present") — not "03/23".
- **Bullet points via list elements** — not em-dashes or manual bullet characters.
- **Keyword density sweet spot**: 60–80% JD keyword match rate (per Jobscan studies). Over-stuffing penalized.
- **Keywords in work experience > skills section** — keywords mentioned in context (work bullets) carry more weight.

### 2026-04-23 — Europass specifics

- Europass is an EU initiative under CEDEFOP; no public CV generation API exists as of 2025.
- The online editor at europass.europa.eu is a React SPA — no documented REST endpoints.
- Europass PDFs are generally ATS-readable (single-column) but have no special ATS benefit vs. a well-formatted standard CV.
- **Verdict**: Implement Europass as an output variant (template + section mapping), not as the internal data model.
- CEFR language levels (A1–C2) are a key Europass contribution — always include in the language model.
- EU law discourages mandatory photos in CVs (discrimination risk) — Europass photo is optional.
- Ondřej's languages: Czech (native/C2), English (B2), Polish (B2), Slovak (B2).

### 2026-04-23 — JSON Resume schema (internal data model)

- JSON Resume (jsonresume.org) is the recommended internal CV schema. MIT licensed, since 2013, active maintenance.
- Standard fields: `basics`, `work`, `education`, `skills`, `languages`, `certificates`, `projects`, `publications`, `volunteer`, `awards`, `references`.
- LinkedIn and GitHub URLs go in `basics.profiles[]` array.
- `basics.image` is the standard field for a profile photo (URL or base64).
- Extension fields (prefixed with `_`) for product metadata (variant, lastUpdated, atsScore) are allowed.
- No native CEFR level field — add as extension or use `fluency` field in `languages`.
- Validator: `npm install resume-schema` (Node) or `pip install jsonresume` (Python).

### 2026-04-23 — ATS scoring tools & APIs

- **Jobscan**: No public API. SaaS ~$50/month. Best UX for manual checks.
- **Affinda**: REST API, free tier (3 docs/month). Best for programmatic CV parsing → structured JSON.
- **Textkernel/Sovren**: Enterprise pricing. Powers Greenhouse. 29 languages. Production-grade.
- **EMSI Skills API** (now Lightcast): Free skills extraction API at skills.emsidata.com. Useful for skill taxonomy normalization.
- **pyresparser**: OSS Python. Basic NER. Last updated 2021. Sufficient for MVP only.
- **MVP approach**: Build custom ATS scorer (spaCy + keybert) with no external API dependency. Affinda optionally for advanced CV parsing.

---

## Output Formats & PDF Generation

### 2026-04-23 — PDF generation tool comparison

- **Playwright `page.pdf()`**: Best CSS3/modern layout support (uses real Chromium). Identical to browser "Print to PDF". Fast (~0.5–2s/page). Good for visual/color variants. Limited CSS Paged Media support.
- **WeasyPrint**: Best CSS Paged Media support (@page, running headers, page numbers). No JS execution. Pure Python. Slower (~2–5s/page). Best for ATS-safe compliance variant. Explicitly supports clickable hyperlinks in PDF.
- **wkhtmltopdf**: ABANDONED (last release 2020). Do not use.
- **Prince XML**: Best CSS Paged Media but commercial ($3,800/server). Overkill.
- **Recommendation**: Use Playwright for visual variants, WeasyPrint for ATS-safe and compliance variants.

### 2026-04-23 — DOCX generation

- **docxtpl**: Template-based DOCX generation (Jinja2 syntax in Word template). Best for maintaining complex formatting without code. Recommended primary approach.
- **python-docx**: Programmatic DOCX generation. Good for simple layouts. Hyperlinks require XML injection (no native API).
- **docx.js**: Node.js. Defaults to A4 — always set page size explicitly. Used by `anthropics/skills@docx`.
- **Heading styles matter**: Always use Word Heading styles (Heading 1, Heading 2) in generated DOCX — ATS parsers use these for section identification. Bolded body text is NOT recognized as a heading.

### 2026-04-23 — Live HTML editing

- **Tiptap v2**: Best React-native rich text editor (MIT). ProseMirror wrapper. Recommended for editing summary, bullet points.
- **contenteditable divs**: Too uncontrolled for structured CV editing.
- **Monaco Editor**: Good for developer mode (JSON editing), not for end-user CV editing.
- **Pattern**: Structured forms for metadata (name, dates, URLs), Tiptap for rich text fields (summary, bullets). Never expose raw JSON.

---

## Skills & Tooling

### 2026-04-23 — Skills discovery & installation

- `anthropics/skills@pdf`: 82.5K installs. Gen Safe + 0 Socket alerts but **Snyk High Risk**. Installed globally at `~/.agents/skills/pdf`.
- `anthropics/skills@docx`: 66.9K installs. Snyk Low Risk. Installed globally at `~/.agents/skills/docx`.
- `claude-office-skills/skills@docx-manipulation`: python-docx-based alternative. 958 installs.
- Global skills auto-available to OpenCode, Codex, GitHub Copilot.
- `npx skills` had ENOTEMPTY error on first run — resolved by running again (cached install).
- **Security reminder**: Treat `@pdf` with caution in automated/CI pipelines until Snyk High Risk is investigated.

---

## Project Context

### 2026-04-23 — Source CV files

- **PDF**: `docs/CV-Lasak-EN-Dec-2025.pdf` — PDF 1.3, macOS Quartz, Europass EN, 6 pages, Dec 2025. Text-based (not scanned) — direct text extraction works.
- **DOCX**: `docs/CV-Lasak-EN 18.docx` — Word document, same content. ⚠️ **Filename has a space** — always quote the path in scripts and shell commands: `"docs/CV-Lasak-EN 18.docx"`. Use `python-docx` to read.
- Use **both** for extraction and cross-validate output — DOCX often has cleaner structured text (no PDF layout noise).
- Owner: Ondřej Lasák, Senior Software Automation Quality Engineer, Prague CZ.
- GitHub: https://github.com/jimicze | LinkedIn: https://cz.linkedin.com/in/lasakondrej/
- 13+ years QA/test automation experience. Current focus: GenAI, MCP, agentic testing, RAG.
- Core skills: Playwright (TS + C#), Selenium, K6, JMeter, BDD/SpecFlow, Azure DevOps, GitHub Actions.
- Quantified achievements: 95% manual regression reduction (PwC), 60% Playwright execution time improvement (Vendavo).
- Languages: Czech (native/C2), English (B2), Polish (B2), Slovak (B2).

### 2026-04-23 — LLM configuration (local-first)

- **No external API key required.** User has: LM Studio (local models) + GitHub Copilot subscription.
- **LM Studio**: OpenAI-compatible API at `http://localhost:1234/v1`. Supports `llama3`, `mistral`, `phi3`, etc.
- **Ollama**: Alternative local runner at `http://localhost:11434`. Same model options.
- **GitHub Copilot**: Available for cloud-assisted code generation — not ideal for runtime CV data processing (privacy).
- **Recommendation**: Use local LLM (LM Studio/Ollama) for all CV data operations (extraction, ATS scoring, cover letter). Use Copilot only for coding assistance within the agent session.
- Privacy benefit: CV personal data never leaves the machine when using local models.
