#!/usr/bin/env bash
# ScholarAIO plugin dependency check — runs on SessionStart (startup only)
#
# Design principles:
#   - NEVER exit non-zero (must not block session startup)
#   - NEVER silently fail (always tell user what happened)
#   - Diagnose first, install only what's safe, guide for the rest

PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"

# ---------- 1. Check if scholaraio CLI is already available ----------

if command -v scholaraio >/dev/null 2>&1; then
    # Already installed — quick config check
    if scholaraio setup check --lang en >/dev/null 2>&1; then
        exit 0
    fi
    # CLI works but config might be incomplete — let the skills handle it
    exit 0
fi

# ---------- 2. scholaraio CLI not found — attempt install ----------

echo ""
echo "[ScholarAIO] Setting up for first use..."
echo ""

# 2a. Find a working pip
PIP=""
if command -v pip >/dev/null 2>&1; then
    PIP="pip"
elif command -v pip3 >/dev/null 2>&1; then
    PIP="pip3"
elif python3 -m pip --version >/dev/null 2>&1; then
    PIP="python3 -m pip"
elif python -m pip --version >/dev/null 2>&1; then
    PIP="python -m pip"
fi

if [ -z "$PIP" ]; then
    echo "[ScholarAIO] pip not found. Please install Python 3.10+ with pip, then run:"
    echo "  pip install git+https://github.com/ZimoLiao/scholaraio.git"
    echo ""
    exit 0
fi

# 2b. Install from bundled source (plugin cache has the full repo)
if [ -f "$PLUGIN_ROOT/pyproject.toml" ]; then
    echo "[ScholarAIO] Installing from plugin bundle..."
    if $PIP install "$PLUGIN_ROOT" 2>&1 | tail -3; then
        :
    fi
else
    echo "[ScholarAIO] Installing from GitHub..."
    if $PIP install "git+https://github.com/ZimoLiao/scholaraio.git" 2>&1 | tail -3; then
        :
    fi
fi

# 2c. Verify installation
if ! command -v scholaraio >/dev/null 2>&1; then
    echo ""
    echo "[ScholarAIO] Auto-install did not succeed. Please install manually:"
    echo "  $PIP install git+https://github.com/ZimoLiao/scholaraio.git"
    echo ""
    echo "  After installing, run:  scholaraio setup"
    echo ""
    exit 0
fi

# ---------- 3. Post-install guidance ----------

echo ""
echo "[ScholarAIO] CLI installed successfully!"
echo ""
echo "  Next steps — tell Claude:"
echo "    /scholaraio:setup        Interactive setup wizard (config + API keys)"
echo ""
echo "  Or run manually:"
echo "    scholaraio setup         Interactive wizard"
echo "    scholaraio setup check   See what's configured"
echo ""

exit 0
