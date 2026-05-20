#!/usr/bin/env bash
# install.sh — ATS-CV Optimizer one-shot installer
# Usage:  bash <(curl -sSf https://raw.githubusercontent.com/jimicze/jimicze.github.io/main/install.sh)
set -euo pipefail

REPO_URL="https://github.com/jimicze/jimicze.github.io.git"
INSTALL_DIR="${ATS_CV_DIR:-$HOME/.ats-cv}"
BIN_DIR="$HOME/.local/bin"

# ── colours ───────────────────────────────────────────────────────────────────
bold="\033[1m"; reset="\033[0m"; green="\033[32m"; red="\033[31m"; dim="\033[2m"
ok()   { echo -e "${green}✔${reset} $*"; }
info() { echo -e "${bold}→${reset} $*"; }
err()  { echo -e "${red}✘ $*${reset}" >&2; exit 1; }

echo ""
echo -e "${bold}ATS-CV Optimizer — installer${reset}"
echo "────────────────────────────────"

# ── 1. Prerequisites ──────────────────────────────────────────────────────────
info "Checking prerequisites..."

if ! command -v python3 &>/dev/null; then
  err "Python 3 not found. Install with: brew install python"
fi
PY_VER=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
PY_MAJOR=$(echo "$PY_VER" | cut -d. -f1)
PY_MINOR=$(echo "$PY_VER" | cut -d. -f2)
if [ "$PY_MAJOR" -lt 3 ] || { [ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 11 ]; }; then
  err "Python ≥ 3.11 required (found $PY_VER). Install with: brew install python"
fi
ok "Python $PY_VER"

if ! command -v node &>/dev/null; then
  err "Node.js not found. Install with: brew install node"
fi
NODE_VER=$(node --version | sed 's/v//')
NODE_MAJOR=$(echo "$NODE_VER" | cut -d. -f1)
if [ "$NODE_MAJOR" -lt 20 ]; then
  err "Node.js ≥ 20 required (found $NODE_VER). Install with: brew install node"
fi
ok "Node.js $NODE_VER"

if ! command -v git &>/dev/null; then
  err "git not found. Install with: brew install git"
fi
ok "git $(git --version | awk '{print $3}')"

# ── 2. Clone or update ────────────────────────────────────────────────────────
if [ -d "$INSTALL_DIR/.git" ]; then
  info "Updating existing install at $INSTALL_DIR..."
  git -C "$INSTALL_DIR" pull --ff-only --quiet
  ok "Repository updated"
else
  info "Cloning repository to $INSTALL_DIR..."
  git clone --depth 1 --quiet "$REPO_URL" "$INSTALL_DIR"
  ok "Repository cloned"
fi

# ── 3. Python virtual environment ─────────────────────────────────────────────
VENV="$INSTALL_DIR/.venv"
if [ ! -d "$VENV" ]; then
  info "Creating Python virtual environment..."
  python3 -m venv "$VENV"
  ok "Virtual environment created"
fi

info "Installing Python dependencies (this may take a minute)..."
"$VENV/bin/pip" install --quiet --upgrade pip
"$VENV/bin/pip" install --quiet -e "$INSTALL_DIR"
ok "Python dependencies installed"

# ── 4. Node dependencies ──────────────────────────────────────────────────────
info "Installing Node dependencies..."
(cd "$INSTALL_DIR" && npm install --silent)
ok "Node dependencies installed"

# ── 5. Playwright browser ─────────────────────────────────────────────────────
info "Installing Playwright Chromium browser..."
(cd "$INSTALL_DIR" && "$VENV/bin/python" -m playwright install chromium --quiet 2>/dev/null \
  || npx playwright install chromium --quiet)
ok "Playwright Chromium ready"

# ── 6. Expose ats-cv on PATH ──────────────────────────────────────────────────
mkdir -p "$BIN_DIR"

# Write a wrapper script instead of a symlink so $INSTALL_DIR is baked in
cat > "$BIN_DIR/ats-cv" <<EOF
#!/usr/bin/env bash
exec "$VENV/bin/ats-cv" "\$@"
EOF
chmod +x "$BIN_DIR/ats-cv"
ok "ats-cv wrapper created at $BIN_DIR/ats-cv"

# ── 7. PATH hint ──────────────────────────────────────────────────────────────
if ! echo "$PATH" | grep -q "$BIN_DIR"; then
  echo ""
  echo -e "${bold}Add $BIN_DIR to your PATH:${reset}"
  echo ""
  echo "  # bash"
  echo '  echo '\''export PATH="$HOME/.local/bin:$PATH"'\'' >> ~/.bashrc && source ~/.bashrc'
  echo ""
  echo "  # zsh"
  echo '  echo '\''export PATH="$HOME/.local/bin:$PATH"'\'' >> ~/.zshrc && source ~/.zshrc'
fi

# ── Done ──────────────────────────────────────────────────────────────────────
echo ""
echo -e "${green}${bold}✔ Installation complete!${reset}"
echo ""
echo "  ats-cv html --variant ats --out ~/cv.html    # render HTML"
echo "  ats-cv pdf  --variant ats --out ~/cv.pdf     # export ATS PDF"
echo "  ats-cv --help                                 # full help"
echo ""
echo -e "${dim}CV data: $INSTALL_DIR/data/cv.json${reset}"
echo ""
