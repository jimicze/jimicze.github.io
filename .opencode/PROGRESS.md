# Progress

<!-- Agent: update this file when starting, completing, or pausing any task. Include the date for each entry. -->

---

## Current Sprint

> Started: 2026-04-23

- [ ] **[BLOCKING]** Extract `data/cv.json` using BOTH source files (cross-validate):
  - PDF: `docs/CV-Lasak-EN-Dec-2025.pdf` via `anthropics/skills@pdf` + `pdfplumber`
  - DOCX: `docs/CV-Lasak-EN 18.docx` via `anthropics/skills@docx` + `python-docx`
  - Structure result into JSON Resume schema via local LLM (LM Studio / Ollama)
- [ ] User reviews extracted `data/cv.json` via browser (not raw JSON)
- [x] **[BLOCKING]** Extract `data/cv.json` ✅ done 2026-04-23 — cross-validated from both sources, full JSON Resume schema
- [ ] User reviews extracted `data/cv.json` via browser (not raw JSON)
- [ ] Create GitHub repo on `jimicze` account + enable GitHub Pages for live HTML CV
- [x] Scaffold project directory structure (`src/`, `templates/`, `data/`, `output/`, `tests/`)
- [x] Set up `pyproject.toml` + `package.json` (hybrid Python + Node stack)
- [x] Add `output/`, `data/cv.json`, `.env` to `.gitignore`
- [ ] Update AGENTS.md commands table once first build tooling is introduced

---

## Completed

### 2026-04-23

- [x] Searched skills ecosystem for PDF and DOCX capabilities
- [x] Installed `anthropics/skills@pdf` globally (`~/.agents/skills/pdf`)
- [x] Installed `anthropics/skills@docx` globally (`~/.agents/skills/docx`)
- [x] Defined project epics: (1) CV conversion & ATS optimisation, (2) cover-letter generation
- [x] Researched ATS scoring systems, data models, PDF generation, HTML CV frameworks, cover letter generation, tech stack
- [x] Wrote `AGENTS.md` to project root (all required sections)
- [x] Wrote `PRD.md` to project root (full product requirements)
- [x] Restructured all `.opencode/` memory files with proper sections and research findings
- [x] Confirmed GitHub username: **jimicze** → https://github.com/jimicze
- [x] Confirmed LLM strategy: **local via LM Studio/Ollama** (primary) + **GitHub Copilot** (secondary) — no API key needed
- [x] Confirmed live CV deployment: **GitHub Pages on `github.com/jimicze`** (updated from local-only)
- [x] Confirmed Europass variant: **V2** (not required for initial release)
- [x] Confirmed DOCX source exists: **`docs/CV-Lasak-EN 18.docx`** — both PDF and DOCX now available for extraction
- [x] Scaffolded project directory structure: `src/`, `src/cover_letter/`, `data/`, `templates/html/{ats,color,simple,full}/`, `templates/docx/`, `output/`, `tests/`
- [x] Created `.gitignore` (excludes `output/`, `data/cv.json`, `.env`, `__pycache__/`, `node_modules/`, etc.)
- [x] Created `pyproject.toml` (Python 3.11+, FastAPI, pdfplumber, WeasyPrint, spaCy, Pydantic v2, etc.)
- [x] Created `package.json` (React 18, TypeScript, Vite, Tiptap v2, Playwright, Vitest)
- [x] Updated `AGENTS.md` commands table with actual install/dev/test commands
- [x] Extracted `data/cv.json` from both source documents (pypdf + DOCX XML unpack); cross-validated; full JSON Resume schema with `_meta` extensions; 11 work entries, 4 education entries, 11 certificates, 10 skill categories, 4 languages, 6 projects

---

## Backlog

### Epic 1 — CV Conversion & ATS Optimisation

| # | Task | Priority | Depends on | Notes |
|---|------|----------|------------|-------|
| 1 | Extract structured data from source PDF → `data/cv.json` | 🔴 Critical | — | Uses skills@pdf + pdfplumber + LLM |
| 2 | Validate `data/cv.json` against JSON Resume schema | 🔴 Critical | #1 ✅ | `npm install resume-schema` or `pip install jsonresume` |
| 3 | Build Jinja2 HTML template: `ats-safe` variant | 🟠 High | #1 | Single col, no photo, greyscale, standard headings |
| 4 | PDF export from ats-safe template via WeasyPrint | 🟠 High | #3 | Best @page + link support |
| 5 | Verify all hyperlinks are clickable in generated PDF | 🟠 High | #4 | LinkedIn, GitHub, email at minimum |
| 6 | Build Jinja2 HTML template: `color` variant | 🟡 Medium | #1 | Brand colors, single col, no photo |
| 7 | Build Jinja2 HTML template: `full` variant | 🟡 Medium | #1 | Photo, color, single col |
| 8 | PDF export for color/full variants via Playwright | 🟡 Medium | #6, #7 | |
| 9 | DOCX output via `docxtpl` | 🟡 Medium | #1 | Recruiter-editable; use Word Heading styles |
| 10 | ATS optimizer: keyword extraction from JD (spaCy + keybert) | 🟡 Medium | — | No external API dependency for MVP |
| 11 | ATS optimizer: CV vs. JD scoring (0–100 with breakdown) | 🟡 Medium | #1, #10 | |
| 12 | ATS optimizer: formatting checklist (single col, standard headings, etc.) | 🟡 Medium | #3 | |
| 13 | FastAPI backend with REST endpoints | 🟡 Medium | #1 | `/extract`, `/score`, `/export`, `/render` |
| 14 | React/TypeScript frontend: CV editor (Tiptap + forms) | 🟢 Low | #13 | Structured forms + rich text; never expose JSON |
| 15 | Frontend: real-time HTML preview iframe | 🟢 Low | #14 | |
| 16 | Frontend: variant switcher + export buttons | 🟢 Low | #14 | |
| 17 | Photo upload + base64 storage in cv.json | 🟢 Low | #1 | |
| 18 | Europass output variant | 🟢 Low | #1 | CEFR language levels, Europass section order |

### Epic 2 — Cover Letter Generator

| # | Task | Priority | Depends on | Notes |
|---|------|----------|------------|-------|
| 19 | JD document parser (PDF/DOCX/text → structured requirements) | 🟡 Medium | — | spaCy NER + LLM |
| 20 | LLM cover letter generation (structured JSON output first) | 🟡 Medium | #19, E1#1 | Claude API; "never fabricate" constraint |
| 21 | Gap analysis: unmatched JD requirements flagging | 🟡 Medium | #19, #20 | Show user what's missing |
| 22 | Cover letter HTML template + PDF/DOCX export | 🟢 Low | #20 | Reuse same pipeline as CV |

### Infrastructure

| # | Task | Priority | Notes |
|---|------|----------|-------|
| 23 | ~~Project scaffolding: directories, pyproject.toml/package.json~~ | ~~🔴 Critical~~ | ✅ Done 2026-04-23 |
| 24 | ~~`.gitignore`: exclude `output/`, `data/cv.json`, `.env`, `__pycache__/`~~ | ~~🔴 Critical~~ | ✅ Done 2026-04-23 |
| 25 | Create GitHub repo on `jimicze` account + enable GitHub Pages | 🔴 Critical | Repo name TBD (ask user); needs user approval before making public |
| 26 | Configure GitHub Pages: `gh-pages` branch or `docs/` folder; deploy on push to main | 🟠 High | Use `gh-pages` npm package or GitHub Actions |
| 27 | Makefile or npm scripts: `make extract`, `make build`, `make export-pdf`, `make dev` | 🟠 High | |
| 28 | Docker setup: `mcr.microsoft.com/playwright/python:latest` base image | 🟢 Low | Includes Chromium for Playwright PDF |
| 29 | Minimal CI (lint + build check) | 🟢 Low | |

---

## Known Issues

| # | Description | Status | Blocking |
|---|-------------|--------|---------|
| 1 | `anthropics/skills@pdf` flagged **Snyk High Risk** — investigate before CI/automated use | Open | No (dev-only for now) |
| 2 | `data/cv.json` does not exist yet — all Epic 1 tasks depend on this | **Blocking** | Yes |
| 3 | GitHub username: **jimicze** → https://github.com/jimicze | ✅ Resolved | No |
| 4 | No build system or `.gitignore` yet — `output/` files risk accidental commit | Open | No |
| 5 | Tech stack confirmed: Python FastAPI + React/Vite (see PRD §4.4) | ✅ Resolved | No |
| 6 | LLM strategy confirmed: local LM Studio/Ollama + GitHub Copilot sub — no API key needed | ✅ Resolved | No |
| 7 | DOCX filename has a space: `"docs/CV-Lasak-EN 18.docx"` — always quote path in scripts | Open | No (awareness) |
