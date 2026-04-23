# PRD — ATS-CV Optimizer

> **Author:** Ondřej Lasák (ondra.lasak@gmail.com)  
> **Last updated:** 2026-04-23  
> **Status:** Draft v0.1 — pre-code

---

## 1. Problem Statement

Job applications in 2024–2026 flow through Applicant Tracking Systems (ATS) before a human ever reads them. Research shows 75% of qualified candidates are rejected by ATS before recruiter review — primarily due to formatting issues, not a lack of skill. Ondřej Lasák has 13+ years of QA/automation engineering experience but currently maintains his CV manually in Europass PDF format, with no structured data model, no ATS optimization, and no easy way to generate variants for different application contexts.

**The goal is to build a personal AI-assisted CV pipeline that:**
1. Reads the existing CV from PDF/DOCX once.
2. Converts it into an editable structured form (the user never hand-edits raw data files).
3. Optimizes it for ATS pass rate.
4. Generates beautiful, link-preserving outputs: ATS-optimized PDF, live HTML5 CV, and recruiter-editable DOCX.
5. Supports variants: photo/no-photo, color/simple, Europass-style.
6. Later: generates tailored cover letters from job description documents.

---

## 2. Users & Context

| Actor | Description |
|-------|-------------|
| **Primary user** | Ondřej Lasák — applies to senior QA/automation engineering roles; tech-savvy but does not want to hand-edit JSON/TOML/Markdown |
| **Recruiters** | Receive DOCX or PDF; may want to make small edits before forwarding |
| **ATS systems** | Greenhouse, Workday, Lever, iCIMS, Taleo — parse uploaded documents automatically |
| **AI agents** | OpenCode/Claude agents that operate the pipeline within this repository |

---

## 3. Epics & Feature Breakdown

### Epic 1 — CV Conversion & ATS Optimization _(primary)_

#### 3.1.1 CV Ingestion

**Goal:** Accept the existing CV in PDF or DOCX and convert it into the internal structured data model.

**Requirements:**
- [ ] Accept PDF input (`docs/CV-Lasak-EN-Dec-2025.pdf`)
- [ ] Accept DOCX input (future upload path)
- [ ] Extract all CV sections: contact, summary, work experience, education, skills, certifications, languages, projects, publications, awards
- [ ] Map extracted data to **JSON Resume schema** (jsonresume.org) + product extensions
- [ ] Store result in `data/cv.json` — this becomes the single source of truth
- [ ] Flag any extraction uncertainty for user review (do not silently lose data)
- [ ] Preserve all URLs: LinkedIn, GitHub, portfolio, email

**Extraction approach (agent-executable):**
1. Use `anthropics/skills@pdf` + `pdfplumber` for text and layout extraction
2. Use LLM (Claude/Anthropic) to structure raw text → JSON Resume fields
3. Validate output against JSON Resume schema
4. Output `data/cv.json`

**Extended JSON Resume fields needed:**
```json
{
  "$schema": "https://jsonresume.org/schema",
  "_meta": {
    "version": "1.0",
    "lastUpdated": "2026-04-23",
    "sourceFile": "docs/CV-Lasak-EN-Dec-2025.pdf"
  },
  "basics": {
    "name": "Ondřej Lasák",
    "label": "Senior Software Automation Quality Engineer",
    "image": "<base64 or URL — optional>",
    "email": "ondra.lasak@gmail.com",
    "phone": "+420739820982",
    "url": "https://cz.linkedin.com/in/lasakondrej/",
    "summary": "...",
    "location": { "city": "Prague", "countryCode": "CZ" },
    "profiles": [
      { "network": "LinkedIn", "url": "https://cz.linkedin.com/in/lasakondrej/" },
      { "network": "GitHub", "url": "https://github.com/jimicze" }
    ]
  },
  "work": [...],
  "education": [...],
  "skills": [...],
  "languages": [...],
  "certificates": [...],
  "projects": [...],
  "publications": [...],
  "awards": [...],
  "volunteer": [...],
  "references": []
}
```

#### 3.1.2 ATS Optimizer

**Goal:** Score the CV against ATS rules and a specific job description, then suggest improvements.

**Scoring dimensions (weighted):**
| Dimension | Weight | Description |
|-----------|--------|-------------|
| Keyword match | 40% | JD keywords found in CV text |
| Section completeness | 20% | Required sections present and named correctly |
| Contact completeness | 10% | Name, email, phone, LinkedIn all present in body |
| Quantified achievements | 15% | Bullet points containing numbers/metrics |
| Skills density | 15% | JD-required skills present in skills section + work experience |

**Requirements:**
- [ ] Accept job description text (paste or uploaded PDF/DOCX)
- [ ] Extract JD requirements using spaCy NER + LLM
- [ ] Compare JD keywords vs. CV text (exact + semantic matching via `sentence-transformers`)
- [ ] Return score 0–100 with breakdown by dimension
- [ ] Generate prioritized list of optimization suggestions
- [ ] Suggest reordered or reworded bullet points (never fabricate facts)
- [ ] Detect ATS formatting violations in any generated output

**ATS formatting rules the optimizer enforces:**
- No multi-column layout in ATS-safe variant
- No tables used for layout (data tables allowed)
- No text boxes
- No images/icons in main content flow
- Contact info in body, not header/footer
- Standard section heading names
- No icon fonts — Unicode or inline SVG only
- Hyperlinks as actual anchors (not plain text URLs)

#### 3.1.3 Output Variants

**Goal:** Generate multiple output formats and visual variants from the single `data/cv.json`.

**Variants matrix:**

| Variant ID | Photo | Color | Column | Use case |
|------------|-------|-------|--------|----------|
| `ats-safe` | ❌ | ❌ Greyscale | Single | Upload to ATS |
| `simple` | ❌ | Minimal | Single | Clean human read |
| `color` | ❌ | Brand colors | Single | Email attachment |
| `full` | ✅ | Brand colors | Single | LinkedIn, portfolio |
| `europass` | Optional | Minimal | Single | EU public sector / HR |

> **Note:** All variants use single-column layout. No multi-column layouts are offered — they fail ATS parsing even when a human will also read the document.

**Output formats per variant:**
- **HTML** — live-editable in browser, shareable link
- **PDF** — generated via Playwright (`page.pdf()`) from the HTML variant
- **DOCX** — generated via `docxtpl` from a Word template, for recruiter editing

**Requirements:**
- [ ] Implement at minimum: `ats-safe`, `color`, `full` variants
- [ ] `europass` variant in V2 (same data model, different section labels and structure)
- [ ] Photo toggle: CSS class + `basics.image` presence gate
- [ ] Color toggle: CSS custom properties (`--accent-color`, `--text-color`, etc.)
- [ ] All variants produce valid, accessible HTML5
- [ ] All variants preserve hyperlinks in PDF and DOCX output
- [ ] ATS-safe variant must pass the formatting checklist (§3.1.2)

#### 3.1.4 Hyperlink Preservation

**Goal:** All clickable links must survive conversion to HTML, PDF, and DOCX.

**Links to preserve (from source CV):**
- Email: `ondra.lasak@gmail.com` → `mailto:ondra.lasak@gmail.com`
- LinkedIn: `cz.linkedin.com/in/lasakondrej/`
- GitHub: https://github.com/jimicze
- Portfolio: (if any)
- Certification URLs (if any)

**Requirements:**
- [ ] HTML output: `<a href="...">` with `target="_blank"` for external links
- [ ] PDF (Playwright): links render as clickable in the exported PDF
- [ ] DOCX (docxtpl): links use Word hyperlink fields (not plain text) — requires XML manipulation
- [ ] Regression test: open generated PDF and verify links are clickable

#### 3.1.5 Live HTML5 CV Editor

**Goal:** The user can view and edit their CV in a browser without touching raw data files.

**Requirements:**
- [ ] Serve the HTML CV variant from a local dev server
- [ ] Structured fields (name, dates, URLs, skill list) edit via form controls
- [ ] Rich text fields (summary, bullet points) edit via **Tiptap** editor
- [ ] Changes write back to `data/cv.json` (not a separate file)
- [ ] Real-time preview: regenerate HTML on change
- [ ] Export buttons: Download PDF / Download DOCX / Copy HTML
- [ ] Variant switcher: dropdown to select `ats-safe`, `color`, `full` etc.
- [ ] Photo upload: drag-and-drop, stored as base64 in `data/cv.json`

> **Constraint:** The user must never see raw JSON, TOML, YAML, or Markdown as part of the normal editing flow.

---

### Epic 2 — Cover Letter Generator _(future)_

#### 3.2.1 Job Description Ingestion

**Goal:** Accept a job description document and extract structured requirements.

**Input formats:**
- Paste from clipboard (text)
- PDF upload
- DOCX upload
- URL (scrape from LinkedIn/Workable/Greenhouse — future)

**Extracted fields:**
- Company name
- Role title
- Required skills/technologies
- Nice-to-have skills
- Key responsibilities
- Seniority level
- Culture keywords

#### 3.2.2 Cover Letter Generation

**Goal:** Generate a tailored, ATS-aware cover letter using the CV data + JD.

**Algorithm:**
1. Extract top 5–8 JD requirements
2. Map each requirement to the strongest matching CV achievement
3. Flag unmatched requirements (honest gap analysis — do not fabricate)
4. Generate structured letter: opening → 2–3 achievement paragraphs → cultural fit + CTA
5. Inject JD keywords naturally (they're scored by some ATS)
6. Return structured JSON output before rendering (enables user review)

**Requirements:**
- [ ] Cover letter length: 250–400 words (longer letters are truncated by many ATS)
- [ ] Tone options: professional, conversational
- [ ] User review step before final rendering: show matched achievements, gaps, keywords used
- [ ] Output formats: HTML, PDF, DOCX (same pipeline as CV)
- [ ] "Never fabricate" constraint: all achievement claims must be traceable to `data/cv.json`

---

## 4. Architecture

### 4.1 System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Browser / Local UI                      │
│  ┌─────────────────┐   ┌───────────────────────────────┐   │
│  │   CV Editor     │   │       ATS Score Panel         │   │
│  │  (Tiptap forms) │   │  Score: 78 | Gap analysis     │   │
│  └────────┬────────┘   └───────────────────────────────┘   │
│           │                        ▲                        │
│  ┌────────▼────────────────────────┴───────────────────┐   │
│  │                  HTML Preview (iframe)               │   │
│  │   Real-time CV render — what you see ≈ PDF output   │   │
│  └──────────────────────────────────────────────────────┘   │
│           │ REST API                                        │
└───────────┼────────────────────────────────────────────────┘
            │
┌───────────▼────────────────────────────────────────────────┐
│                   Python Backend (FastAPI)                   │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ CV Extractor │  │ ATS Scorer   │  │ Cover Letter Gen │  │
│  │ pdfplumber   │  │ spaCy +      │  │ LLM (Claude)     │  │
│  │ + LLM        │  │ keybert      │  │ + JD parser      │  │
│  └──────┬───────┘  └──────┬───────┘  └────────┬─────────┘  │
│         │                 │                    │            │
│  ┌──────▼─────────────────▼────────────────────▼─────────┐  │
│  │              data/cv.json  (JSON Resume schema)        │  │
│  │              Single source of truth — never            │  │
│  │              hand-edited by the user                   │  │
│  └──────┬──────────────────────────────────────────────┘  │
│         │                                                   │
│  ┌──────▼──────────────────────────────────────────────┐   │
│  │               Renderer / Template Engine             │   │
│  │  Jinja2 templates → HTML variants                   │   │
│  │     → Playwright PDF                                │   │
│  │     → WeasyPrint PDF (ATS-safe, compliance)         │   │
│  │     → docxtpl DOCX                                  │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 Data Flow

```
INPUT: docs/CV-Lasak-EN-Dec-2025.pdf
  │
  ▼ (one-time extraction, agent-executed)
data/cv.json  ← JSON Resume schema (single source of truth)
  │
  ├──► [ATS Optimizer] ← job_description.txt (optional)
  │         │  keyword scoring + formatting checks
  │         ▼
  │    ats_report.json  (suggestions, score, gaps)
  │
  ├──► [Template Engine]
  │         │  Jinja2 renders variant HTML
  │         ├── output/cv-ats-safe.html
  │         ├── output/cv-color.html
  │         └── output/cv-full.html
  │                  │
  │                  ├── Playwright → output/cv-ats-safe.pdf
  │                  ├── WeasyPrint → output/cv-ats-compliance.pdf
  │                  └── docxtpl   → output/cv-recruiter.docx
  │
  └──► [Cover Letter Generator] ← job_description.pdf/txt
            │  LLM-assisted draft
            ▼
       output/cover-letter-<company>.html → PDF + DOCX
```

### 4.3 Key Architectural Boundaries

| Boundary | Rule |
|----------|------|
| `data/cv.json` | Written by extraction + editor only; NEVER hardcode CV data in templates or scripts |
| `docs/` directory | Read-only. The source PDF is never overwritten |
| `output/` directory | Generated files only. Git-ignored. Never committed |
| Templates | Must be data-driven. No hardcoded personal data |
| ATS-safe variant | Must pass: single-column, no images, standard headings, no layout tables |
| Hyperlinks | Must be preserved in all output formats (not plain text) |
| User editing | MUST NOT require opening a raw JSON/YAML/Markdown file |

### 4.4 Tech Stack Decision

| Layer | Choice | Rationale |
|-------|--------|-----------|
| Backend language | Python 3.11+ | Best PDF/NLP ecosystem (`pdfplumber`, `spaCy`, `WeasyPrint`) |
| Backend framework | FastAPI | Async, typed, fast to stand up |
| Frontend language | TypeScript + React | Live editing, preview, form controls |
| Frontend bundler | Vite | Fast dev, simple config |
| CV data schema | JSON Resume + extensions | Widest ecosystem, open standard |
| HTML templating | Jinja2 (server) | Simple, powerful, well-documented |
| CSS framework | Tailwind CSS with print config | Utility classes + `@media print` |
| PDF export (primary) | Playwright `page.pdf()` | Best CSS3/modern layout support |
| PDF export (ATS safe) | WeasyPrint | Best CSS Paged Media, link preservation |
| DOCX generation | `docxtpl` | Template-driven, maintainable Word output |
| DOCX parsing | `python-docx` | Read uploaded DOCX CVs |
| PDF parsing | `pdfplumber` + `pypdf` | Layout-aware text extraction |
| ATS keyword scoring | `spaCy` + `keybert` | Local, no API dependency |
| Semantic matching | `sentence-transformers` | Synonym/semantic skill matching |
| Rich text editor | Tiptap v2 | React-native ProseMirror wrapper, MIT |
| LLM — local (primary) | **LM Studio** or **Ollama** | No API cost; runs on-device; works offline |
| LLM — cloud (secondary) | **GitHub Copilot** subscription | Already available; no extra API key needed |
| Photo processing | Pillow | Resize, compress, base64 encode |
| Schema validation | `pydantic` v2 | JSON Resume validation |
| CV Docker base image | `mcr.microsoft.com/playwright/python:latest` | Chromium included |

---

## 5. Output Formats Specification

### 5.1 ATS-Safe PDF

**Purpose:** Upload directly to ATS portals (Workday, Greenhouse, Lever, iCIMS, Taleo).

**Hard constraints:**
- Single column layout
- No photos, illustrations, or decorative graphics
- No tables used for layout (data tables in Experience OK if simple)
- No text in headers/footers — all content in body
- Standard section headings: "Work Experience", "Education", "Skills", "Certifications", "Summary"
- Fonts: Arial or Calibri only (universal ATS support)
- Clickable hyperlinks (Playwright preserves them in PDF)
- Font size: 10–12pt body, 14–16pt name/headings
- Margins: 15mm minimum
- No background colors (greyscale only)

**Generation:** WeasyPrint from `ats-safe` HTML template.

### 5.2 Visual PDF (Color / Full)

**Purpose:** Email attachment, portfolio share, LinkedIn profile PDF.

**Constraints relaxed vs. ATS-safe:**
- Brand color accent allowed (single color — e.g., teal/blue)
- Profile photo optional (controlled by variant)
- Subtle visual hierarchy (colored section bars, icons)
- Still single-column (ATS-safe even if used in application)

**Generation:** Playwright from `color` or `full` HTML template.

### 5.3 DOCX (Recruiter-Editable)

**Purpose:** Recruiters sometimes reformat CVs before forwarding to clients. DOCX allows that.

**Requirements:**
- Uses proper Word heading styles (Heading 1, Heading 2) — not bold-formatted body text
- Hyperlinks as Word hyperlink fields (clickable)
- Single column layout
- No complex graphics (DOCX renderers vary)
- Generated via `docxtpl` from a Word template

### 5.4 HTML5 Live CV

**Purpose:** A URL-shareable, browser-viewable CV with in-page editing.

**Requirements:**
- Semantically valid HTML5
- Responsive layout (desktop primary, mobile graceful)
- `@media print` styles that mirror the PDF output
- Accessible (WCAG 2.1 AA — use semantic elements)
- Links open in new tab
- Photo shown only in `full` variant

### 5.5 Europass Variant (V2)

**Purpose:** EU public sector applications, HR portals that request Europass format.

**Requirements:**
- Section structure matches Europass: Personal Information, Job Application, Work Experience, Education, Language Skills (with CEFR levels), Digital Skills
- CEFR language levels: Czech (native/C2), English (B2), Polish (B2), Slovak (B2)
- Photo optional (EU law discourages mandatory photos to prevent discrimination)
- Single column, Europass typography style

---

## 6. User Experience Flow

### 6.1 First-Time Setup (Agent-Assisted)

```
1. Agent reads docs/CV-Lasak-EN-Dec-2025.pdf
2. Agent extracts structured data → data/cv.json
3. Agent presents: "Here's what I extracted — please review"
4. User reviews via browser UI (not JSON)
5. User confirms or makes edits
6. Agent generates all output variants
7. User downloads what they need
```

### 6.2 Updating the CV

```
1. User opens dev server (browser)
2. User edits CV via form/rich-text UI
3. Changes auto-save to data/cv.json
4. Preview refreshes in real-time
5. User clicks "Export" → chooses format + variant
6. Download ready
```

### 6.3 ATS Optimization for a Specific Job

```
1. User pastes or uploads job description
2. System extracts JD requirements
3. System scores current CV against JD
4. System highlights: matched keywords (green), missing (red), suggestions (yellow)
5. User accepts suggestions (or edits manually)
6. User exports ATS-safe PDF for that application
```

### 6.4 Cover Letter Generation (Epic 2)

```
1. User uploads JD document
2. System shows: "I matched 8 of 11 requirements from your CV"
3. System shows gap list: "These 3 requirements aren't in your CV — I won't include them"
4. User confirms or selects which to address
5. System generates draft letter in JSON structured form
6. User reviews + edits via rich text
7. User exports PDF + DOCX
```

---

## 7. Non-Functional Requirements

| Requirement | Target |
|-------------|--------|
| PDF generation speed | < 5 seconds per variant |
| ATS score accuracy | Comparable to Jobscan results (within ±10 points) |
| Extraction accuracy | ≥ 95% fields correctly mapped from source PDF |
| Local-only operation | No CV data sent to external services by default |
| LLM usage | Only for: extraction structuring, ATS keyword optimization, cover letter generation |
| Privacy | No CV data stored in cloud; all outputs in `output/` (gitignored) |
| Link integrity | 100% — all links must be clickable in PDF and DOCX outputs |
| DOCX compatibility | Must open cleanly in Microsoft Word 2019+ and LibreOffice |

---

## 8. ATS Compatibility Research Summary

_(Key findings from domain research — full findings in `.opencode/LEARNINGS.md`)_

### Most Common ATS and Their Quirks

| ATS | File Format Preference | Key Gotchas |
|-----|----------------------|-------------|
| Workday | DOCX or PDF | Skills taxonomy (Workday Skills Cloud); re-entry required |
| Greenhouse | PDF preferred | Uses Textkernel parser; great PDF handling |
| Lever | PDF or DOCX | Modern parser; good with standard layouts |
| iCIMS | DOCX strongly preferred | Weakest PDF parser; two-column = failure |
| Taleo (Oracle) | DOCX | Oldest/strictest parser; non-standard headings dropped |
| SmartRecruiters | PDF or DOCX | Modern parser; handles most layouts |

### Universal ATS Safety Rules

1. **Single column** — multi-column fails across Taleo, iCIMS, legacy systems
2. **Standard section names** — "Work Experience" not "My Career Journey"
3. **No tables for layout** — table content is read out of order by all parsers
4. **Contact in body** — headers/footers are stripped by many parsers
5. **Real text links** — icon fonts render as garbage characters in ATS
6. **Date format: "Month YYYY"** — e.g., "March 2023 – Present" (not "03/23")
7. **Bullet points via list elements** — not em-dashes or manual bullet characters

### ATS Scoring Tools

| Tool | API? | Cost | Notes |
|------|------|------|-------|
| Jobscan | No public API | ~$50/mo | Best UX; SaaS only |
| Affinda | ✅ Yes (REST) | Free tier: 3 docs/mo | Best parse API; structured JSON output |
| Textkernel/Sovren | ✅ Yes | Enterprise pricing | Powers Greenhouse; 29 languages |
| RChilli | ✅ Yes | Starts ~$0.10/parse | Powers iCIMS integrations |
| EMSI Skills API | ✅ Yes | Free | Skill extraction + taxonomy |
| pyresparser | N/A (OSS) | Free | Python; basic NER; sufficient for MVP |

**MVP approach:** Build custom ATS scorer (no external API dependency). Affinda API optionally for advanced parsing of uploaded CVs.

---

## 9. Open Questions

| # | Question | Priority | Notes |
|---|----------|----------|-------|
| 1 | Should the dev server be a local CLI tool or a full web app? | High | Affects frontend framework choice depth |
| 2 | Should `data/cv.json` be committed to git? (Contains personal data) | High | Privacy consideration — likely `.gitignored` or separate private repo |
| 3 | ~~Which LLM to use?~~ **✅ Resolved** | ~~High~~ | **Local** via LM Studio or Ollama (primary) + **GitHub Copilot** subscription (secondary). No Anthropic API key required. |
| 4 | ~~Live HTML CV — local or public?~~ **✅ Resolved** | ~~Medium~~ | **Local-only for now.** Hosted/public URL is a future nice-to-have (location TBD). |
| 5 | ~~Europass variant — V1 or V2?~~ **✅ Resolved** | ~~Medium~~ | **V2.** Not required for initial release. |
| 6 | Should the cover letter generator support multiple languages? | Medium | Ondřej speaks Czech, English, Polish, Slovak |
| 7 | ~~GitHub profile URL~~ **✅ Resolved** | ~~Low~~ | **https://github.com/jimicze** |
| 8 | Should photo be stored in `data/cv.json` (base64) or as a file in `data/assets/`? | Low | Base64 bloats JSON; separate file is cleaner |
| 9 | ~~Is there an existing DOCX version of the CV?~~ **✅ Resolved** | ~~Low~~ | **`docs/CV-Lasak-EN 18.docx`** — ingestion path now validated. |

---

## 10. Milestones

### Milestone 1 — Data Foundation (unblocks everything)
- [ ] Extract `data/cv.json` from source PDF (`docs/CV-Lasak-EN-Dec-2025.pdf`) AND/OR DOCX (`docs/CV-Lasak-EN 18.docx`) — cross-validate both
- [ ] Validate against JSON Resume schema
- [ ] User reviews extracted data in browser

### Milestone 2 — First Output
- [ ] ATS-safe HTML template rendered from `data/cv.json`
- [ ] PDF export via Playwright
- [ ] All hyperlinks clickable in PDF

### Milestone 3 — Variant System
- [ ] Color + Full variants
- [ ] Photo toggle
- [ ] DOCX export via `docxtpl`

### Milestone 4 — Live Editor
- [ ] Dev server with Tiptap-based CV editor
- [ ] Real-time preview
- [ ] Variant switcher + export buttons

### Milestone 5 — ATS Optimizer
- [ ] JD paste input
- [ ] Keyword extraction + scoring
- [ ] Optimization suggestions UI

### Milestone 6 — Cover Letter Generator (Epic 2)
- [ ] JD document ingestion
- [ ] LLM-generated cover letter with gap analysis
- [ ] HTML/PDF/DOCX output

---

## 11. Reference Projects

| Project | URL | What to borrow |
|---------|-----|----------------|
| Reactive Resume | https://github.com/AmruthPillai/Reactive-Resume | Live editor UX, template structure |
| Open Resume | https://github.com/xitanggg/open-resume | ATS-focused PDF builder, client-side parser |
| JSON Resume | https://jsonresume.org / https://github.com/jsonresume/resume-schema | Data schema, theme ecosystem |
| CoverLetterGPT | https://github.com/vincanger/coverlettergpt | Cover letter generation pattern |
| Resume Matcher | https://github.com/srbhr/Resume-Matcher | JD ↔ CV matching approach |

---

## 12. Out of Scope (for now)

- Multi-user / SaaS — this is a personal tool
- Mobile app
- Direct LinkedIn API import (requires OAuth partnership)
- Browser extension
- Video CV / infographic CV
- Automatic job application submission
- Tracking application status
- Salary negotiation features
