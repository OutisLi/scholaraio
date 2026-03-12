#!/usr/bin/env bash
# ScholarAIO plugin dependency check — runs on SessionStart
# Checks if the scholaraio CLI is available, offers to install if not.

set -euo pipefail

PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"

# 1. Check if scholaraio CLI is on PATH
if command -v scholaraio >/dev/null 2>&1; then
    exit 0
fi

# 2. Not found — try to install from the plugin's bundled source
echo "[ScholarAIO] scholaraio CLI not found. Attempting install from plugin..."

if [ -f "$PLUGIN_ROOT/pyproject.toml" ]; then
    pip install "$PLUGIN_ROOT" 2>&1 | tail -1
    if command -v scholaraio >/dev/null 2>&1; then
        echo "[ScholarAIO] Installed successfully. Run 'scholaraio setup check' to verify environment."
        exit 0
    fi
fi

# 3. Fallback: print manual instructions
echo "[ScholarAIO] Auto-install failed. Please install manually:"
echo "  pip install git+https://github.com/ZimoLiao/scholaraio.git"
echo "  # or clone the repo and: pip install -e ."
echo ""
echo "After installing, run: scholaraio setup"
exit 0
