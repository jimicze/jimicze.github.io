# AGENTS.md — ATS-CV Optimizer

> **Last updated:** 2026-04-23
> **Repo status:** Scaffolded — directories, pyproject.toml, package.json, and .gitignore in place. No source code yet.
> Read [`.opencode/PROGRESS.md`](.opencode/PROGRESS.md) at session start to pick up where the last agent left off.

---

## Project Goal

Build an AI-assisted CV pipeline for **Ondřej Lasák** that:

1. **Ingests** an existing CV from PDF or DOCX.
2. **Converts** it to an internal structured data model (machine-writable, never hand-edited by the user).
3. **Optimizes** for ATS (Applicant Tracking Systems) — keyword density, section ordering, format rules.
4. **Outputs**:
   - ATS-optimized PDF (clean, single-column, machine-readable)
   - Live-editable HTML5 CV (in-browser editing, no raw data files)
   - Recruiter-editable DOCX
5. **Supports output variants**: `photo` / `no-photo`, `simple` (greyscale) / `color`.
6. **Preserves hyperlinks**: LinkedIn, GitHub, portfolio, email throughout all formats.
7. **Future epic**: Cover letter generator from a supplied job-description document.

> **User rule:** The user must NEVER need to hand-edit raw JSON, TOML, YAML, or Markdown to update their CV. All editing must happen through a UI, rich-text editor, or structured form.

---

## 1. Commands

| Action | Command |
|--------|---------|
| Install Python deps | `pip install -e ".[dev]"` |
| Install Node deps | `npm install` |
| Install Playwright browsers | `npx playwright install --with-deps chromium` |
| Install spaCy model | `python -m spacy download en_core_web_sm` |
| Dev server (frontend) | `npm run dev` |
| Typecheck frontend | `npm run typecheck` |
| Lint frontend | `npm run lint` |
| Run frontend tests | `npm test` |
| Run Python tests | `pytest` |
| Lint & format Python | `ruff check . && ruff format .` |
| Export PDF (Playwright) | _TBD — `src/render.py`_ |
| Export PDF (ATS/WeasyPrint) | _TBD — `src/render.py`_ |
| ATS score check | _TBD — `src/optimize.py`_ |
| Extract CV data | _TBD — `src/extract.py`_ |
| Deploy to GitHub Pages | `npm run build && gh-pages -d dist` |

---

## 2. Repository Structure

```
ATS-cv/
├── docs/
│   ├── CV-Lasak-EN-Dec-2025.pdf    ← canonical source CV PDF (READ-ONLY, never overwrite)
│   └── CV-Lasak-EN 18.docx         ← canonical source CV DOCX (READ-ONLY, never overwrite)
├── .opencode/
│   ├── LEARNINGS.md                ← bugs, gotchas, lessons learned
│   ├── PROGRESS.md                 ← task tracker across sessions
│   └── MEMORY.md                   ← decisions, patterns, user preferences
├── AGENTS.md                       ← this file
└── PRD.md                          ← product requirements document
```

**Target structure once development begins:**

```
ATS-cv/
├── docs/                           ← input documents (read-only)
│   └── CV-Lasak-EN-Dec-2025.pdf
├── data/
│   └── cv.json                     ← extracted structured CV data (JSON Resume schema)
├── templates/
│   ├── html/                       ← HTML+CSS CV templates
│   │   ├── ats/                    ← ATS-safe variant (no color, no photo, single column)
│   │   ├── color/                  ← color/branded variant
│   │   └── simple/                 ← minimal/clean variant
│   └── docx/                       ← DOCX template(s)
├── src/
│   ├── extract.py (or .ts)         ← PDF/DOCX → structured data
│   ├── optimize.py (or .ts)        ← ATS keyword optimizer
│   ├── render.py (or .ts)          ← structured data → HTML/DOCX/PDF
│   └── cover_letter/               ← cover letter generation (future epic)
├── output/                         ← generated files (gitignored)
├── tests/
├── .opencode/
├── AGENTS.md
└── PRD.md
```

---

## 3. Architecture Overview

### Data Flow

```
INPUT (PDF/DOCX)
     │
     ▼
[Extraction Layer]  ← uses anthropics/skills@pdf + @docx
     │  Parses raw document into structured CV data
     ▼
[Data Model]  ←── JSON Resume schema (jsonresume.org)
     │  Single source of truth — never hand-edited
     ├──────────────────────────────────────────┐
     ▼                                          ▼
[ATS Optimizer]                          [Cover Letter Generator]
     │  Keyword analysis,                      │  JD input + CV data
     │  section reordering,                    │  → LLM-assisted draft
     │  density scoring                        ▼
     ▼                                   [Cover Letter Output]
[Renderer / Template Engine]
     │
     ├── HTML Template (photo/no-photo, color/simple)
     │        └── @media print → PDF via headless browser (Playwright)
     ├── DOCX Generator (python-docx or docx.js)
     └── ATS PDF (strictest constraints, no graphics)
```

### Key Boundaries

- `data/cv.json` is the **single source of truth**. Templates and renderers MUST read from it; they must NOT contain hardcoded CV content.
- The extraction layer writes `data/cv.json`; nothing else should write to it without user review.
- ATS variant output MUST NOT contain: images/photos, multi-column layouts, tables for layout (data tables OK), decorative graphics, non-standard fonts.
- HTML templates must have `@media print` styles so PDF export works directly from the browser OR via Playwright `page.pdf()`.

### Installed Global Agent Skills

| Skill | Purpose | Load with |
|-------|---------|-----------|
| `anthropics/skills@pdf` | Read/extract/create/manipulate PDF | `skill("pdf")` |
| `anthropics/skills@docx` | Read/create/edit DOCX | `skill("docx")` |

> Always load the relevant skill before any PDF or DOCX file operation.
> Do NOT re-implement PDF/DOCX parsing from scratch.

---

## 4. Code Style & Conventions

> To be defined once the language/stack is chosen. Placeholder conventions:

### General
- **Language:** TBD (Python preferred for extraction/optimization; TypeScript preferred for HTML rendering and PDF generation).
- **Module size:** Single responsibility — one file per pipeline stage (extract, optimize, render, export).
- **No hardcoded CV content** in source files. All personal data lives in `data/cv.json`.

### Naming
- Files: `snake_case.py` / `kebab-case.ts`
- Functions: `snake_case` (Python) / `camelCase` (TypeScript)
- Constants: `UPPER_SNAKE_CASE`
- CV data fields: follow [JSON Resume schema](https://jsonresume.org/schema/) field names exactly

### Imports
- Python: stdlib → third-party → local (separated by blank lines)
- TypeScript: external packages → internal modules → types (separated by blank lines)

### Error handling
- Pipeline stages must fail loudly with clear error messages (not silently produce empty output).
- Any file read/write operation must handle missing files explicitly.

### Do NOT
- Hardcode personal data (name, email, phone) anywhere except `data/cv.json`.
- Use `any` type in TypeScript.
- Import circular dependencies.

---

## 5. Testing

> No test framework exists yet. When introduced, update this section with exact commands.

### Intended approach
- **Unit tests**: test extraction output against expected JSON schema fields.
- **Snapshot tests**: rendered HTML snapshots per variant (ATS, color, simple, photo, no-photo).
- **PDF smoke tests**: verify PDF is non-empty and contains expected strings.
- **ATS tests**: assert that ATS variant output contains no `<img>`, no multi-column layout, standard section headings.

### Minimal test example (future Python)
```python
def test_extraction_produces_valid_json_resume():
    result = extract("docs/CV-Lasak-EN-Dec-2025.pdf")
    assert result["basics"]["name"] == "Ondřej Lasák"
    assert "work" in result
    assert len(result["work"]) > 0
```

### What to test vs. skip
- **Test:** data extraction completeness, template rendering, ATS rule compliance.
- **Skip:** exact pixel-perfect PDF layout (brittle), LLM output content (non-deterministic).

---

## 6. Workflow Rules

### Agents may do automatically (no approval needed)
- Load and use installed skills (`pdf`, `docx`).
- Read any file in the repository.
- Create new files in `src/`, `templates/`, `tests/`, `data/`, `output/`.
- Update `.opencode/LEARNINGS.md`, `.opencode/PROGRESS.md`, `.opencode/MEMORY.md`.
- Reformat code (when a formatter is configured).
- Fix lint errors.
- Add/update comments and docstrings.

### Agents must ASK before doing
- Adding external dependencies (`npm install`, `pip install`, etc.) — confirm package name and version.
- Modifying `data/cv.json` (the structured CV data) after first extraction.
- Changing the JSON Resume schema or data model structure.
- Adding a new output variant or template.
- Modifying CI pipelines (when they exist).
- Deleting any file.
- Making any output publicly accessible (deploy, publish).

### Agents must NEVER do
- Overwrite or modify `docs/CV-Lasak-EN-Dec-2025.pdf` (read-only source document).
- Commit secrets, API keys, tokens, or personal credentials.
- Force-push to any branch.
- Hardcode personal data outside `data/cv.json`.
- Skip security review of new external dependencies.
- Use `any` type in TypeScript.
- Hand-craft or expose raw JSON/TOML/YAML/Markdown to the user as the editing interface.
- Commit files in `output/` to git.

---

## 7. Environment & Dependencies

### Required tools (global)
| Tool | Purpose | Install |
|------|---------|---------|
| Node.js ≥ 20 | JavaScript runtime (templates, PDF generation) | `brew install node` |
| Python ≥ 3.11 | Extraction, optimization scripts | `brew install python` |
| Playwright (Node) | Headless PDF export | `npm install playwright` |
| `anthropics/skills@pdf` | PDF skill (already installed globally) | pre-installed |
| `anthropics/skills@docx` | DOCX skill (already installed globally) | pre-installed |

### Python packages (to be installed when pipeline begins)
```bash
pip install pypdf pdfplumber python-docx reportlab
```

### Node packages (to be installed when pipeline begins)
```bash
npm install playwright docx
```

### LLM Configuration

Two LLM backends are available — no external API key required:

| Backend | Tool | Use case |
|---------|------|----------|
| **Local (primary)** | LM Studio or Ollama | CV extraction structuring, ATS scoring, offline use |
| **Cloud (secondary)** | GitHub Copilot subscription | Code assistance, cover letter generation |

**LM Studio** (https://lmstudio.ai) — run a local model server on `http://localhost:1234/v1` (OpenAI-compatible API).  
**Ollama** (https://ollama.com) — run models via `ollama serve` on `http://localhost:11434`.

Recommended models for CV/text tasks: `llama3`, `mistral`, `phi3`, `deepseek-coder`.

No `.env` file or API key needed for local operation. If cloud LLM is needed, GitHub Copilot is the existing subscription — no additional cost.

### Environment variables
```bash
# Optional — only needed if using a remote/cloud LLM
LLM_BACKEND=lmstudio          # or: ollama, copilot
LLM_BASE_URL=http://localhost:1234/v1   # LM Studio default
LLM_MODEL=llama3              # model name
```

### Gotchas
- `anthropics/skills@pdf` is flagged **High Risk by Snyk** (despite clean Socket scan). Review before use in any automated/CI pipeline.
- The source CV PDF is PDF 1.3 (macOS Quartz). Use `pdfplumber` for best text extraction fidelity; `pypdf` alone may lose layout information.
- The source CV DOCX (`docs/CV-Lasak-EN 18.docx`) has a **space in the filename** — always quote the path: `"docs/CV-Lasak-EN 18.docx"`.
- ATS systems heavily penalize multi-column PDFs — the ATS output variant must be strictly single-column.
- `docx.js` (used by `anthropics/skills@docx`) defaults to A4 page size; set explicitly to desired format (A4 or US Letter).
- Live HTML CV is **local-only** for now. Do not deploy or make publicly accessible without explicit user instruction.

---

## 8. Agent Execution Strategy

### Parallel Execution (mandatory)
- **Always spin up subagents for independent tasks and maximize parallel execution.** Never do sequentially what can be done in parallel. Examples: searching multiple directories, running lint and tests simultaneously, reading unrelated files.
- **Launch multiple subagents in a single message** when tasks are independent. Do not wait for one to finish before starting another.

### Subagent Nesting
- **General subagents MUST delegate further and maximize parallel execution** when they receive compound tasks. A General subagent should spin up Explore subagents for read-only research and additional General subagents for independent write tasks.
- **Explore subagents are leaf nodes.** They cannot spawn further subagents. Use them as fast, focused readers.
- **Nesting hierarchy:**
  ```
  Primary (Build/Plan/Orchestrator)
    -> General (can read + write + spawn further subagents)
         -> Explore (read-only, leaf node)
         -> General (recursive — can spawn more if needed)
    -> Explore (read-only, leaf node)
  ```

### Tool Preferences
- **Prefer the `playwright-cli` skill over Playwright MCP** for browser manipulation and debugging. The CLI skill provides better control, step-by-step visibility, and inline debugging. Reserve Playwright MCP for headless/CI scenarios where the skill is unavailable.
- **Use `anthropics/skills@pdf`** for all PDF operations. Load it with `skill("pdf")` before any PDF file work.
- **Use `anthropics/skills@docx`** for all DOCX operations. Load it with `skill("docx")` before any DOCX file work.

### Context Preservation
- **Delegate exploration to subagents.** Use Explore subagents for codebase searches, file discovery, and context gathering. This preserves the primary agent's context window for reasoning and code changes.
- **Minimize primary context usage.** Offload research, large file reads, and multi-step investigations to subagents. The primary agent should focus on planning, decision-making, and writing code.
- **Avoid triggering compaction.** Keep conversations lean by delegating aggressively. Compaction loses context — prevention is better than recovery.

---

## Persistent Memory

These files maintain context across agent sessions. Always read them at the start of a session and update them as you work.

| File | Purpose | Update when |
|------|---------|-------------|
| [.opencode/LEARNINGS.md](.opencode/LEARNINGS.md) | Bugs, errors, gotchas, lessons learned | Resolving an issue or discovering a non-obvious constraint |
| [.opencode/PROGRESS.md](.opencode/PROGRESS.md) | Task tracking & history | Starting, completing, or pausing any work |
| [.opencode/MEMORY.md](.opencode/MEMORY.md) | Decisions, patterns, user preferences | Making architectural decisions or discovering codebase patterns |
