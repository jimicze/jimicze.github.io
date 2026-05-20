# ATS-CV Optimizer

AI-assisted CV pipeline. Renders an ATS-optimized PDF, live HTML, and recruiter-editable DOCX from a single structured data file.

---

## Install

```bash
bash <(curl -sSf https://raw.githubusercontent.com/jimicze/jimicze.github.io/main/install.sh)
```

The script will:
- Clone the repo to `~/.ats-cv`
- Set up a Python virtual environment and install all dependencies
- Install the Playwright Chromium browser
- Create the `ats-cv` command in `~/.local/bin`

**Prerequisites:** Python ≥ 3.11, Node.js ≥ 20, git  
macOS: `brew install python node git`

After install, ensure `~/.local/bin` is on your PATH:

```bash
# zsh
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc && source ~/.zshrc

# bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc && source ~/.bashrc
```

---

## Usage

```
ats-cv <command> [options]
```

### Render HTML

```bash
ats-cv html --variant ats --out ~/cv.html
```

| Flag | Default | Description |
|------|---------|-------------|
| `--variant` | `ats` | `ats` · `color` · `simple` · `full` |
| `--out` | `public/index.html` | Output file path |
| `--cv` | `~/.ats-cv/data/cv.json` | Override CV data source |

| Variant | Description |
|---------|-------------|
| `ats` | Single-column, no photo, no color — strictest ATS compliance |
| `simple` | Minimal color, no photo |
| `color` | Brand colors, no photo |
| `full` | Color + photo |

### Export PDF

```bash
ats-cv pdf --variant ats --out ~/cv.pdf
```

Renders HTML to a temp file then converts with WeasyPrint. Hyperlinks are preserved as clickable PDF annotations.

Use an already-built HTML file to skip re-rendering:

```bash
ats-cv pdf --html ~/cv.html --out ~/cv.pdf
```

| Flag | Default | Description |
|------|---------|-------------|
| `--variant` | `ats` | Template variant for intermediate HTML |
| `--html` | _(none)_ | Skip rendering — use this HTML file directly |
| `--out` | `output/cv-ats-safe.pdf` | Output file path |
| `--cv` | `~/.ats-cv/data/cv.json` | Override CV data source |

### Export DOCX

```bash
ats-cv docx --template ~/.ats-cv/templates/docx/cv-recruiter.docx --out ~/cv.docx
```

| Flag | Default | Description |
|------|---------|-------------|
| `--template` | `templates/docx/cv-recruiter.docx` | docxtpl Word template |
| `--out` | `output/cv-recruiter.docx` | Output file path |
| `--cv` | `~/.ats-cv/data/cv.json` | Override CV data source |

### Help

```bash
ats-cv --help
ats-cv html --help
ats-cv pdf --help
ats-cv docx --help
```

---

## Update

Re-run the installer at any time — it will pull the latest changes and reinstall:

```bash
bash <(curl -sSf https://raw.githubusercontent.com/jimicze/jimicze.github.io/main/install.sh)
```

---

## Data

`~/.ats-cv/data/cv.json` is the single source of truth (JSON Resume schema). It is gitignored and stays local. All renderers read from it — never edit it by hand.

---

## Source Documents (read-only)

| File | Notes |
|------|-------|
| `docs/CV-Lasak-EN-Dec-2025.pdf` | Canonical source PDF — never overwrite |
| `docs/CV-Lasak-EN 18.docx` | Canonical source DOCX — filename has a space, always quote the path |
