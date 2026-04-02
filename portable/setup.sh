#!/usr/bin/env bash
# GP800 Tool — Linux Setup (run once on laptop)

set -e

echo "============================================"
echo " GP800 Tool - Setup for Linux"
echo "============================================"
echo

# Check Python
if ! command -v python3 &>/dev/null; then
    echo "[ERROR] Python 3 is not installed."
    echo "Install with: sudo apt install python3 python3-pip"
    exit 1
fi

echo "[OK] Python found: $(python3 --version)"

# Install dependencies
echo
echo "Installing gp800-tool dependencies..."
cd "$(dirname "$0")/gp800-tool"
pip install --user -e ".[kline]" --quiet --no-build-isolation
cd "$(dirname "$0")"

echo "[OK] gp800-tool installed"

# Verify
echo
echo "Verifying installation..."
if gp800-tool --version 2>/dev/null; then
    echo "[OK] gp800-tool works!"
else
    echo "[INFO] gp800-tool not in PATH — try: python3 -m gp800_tool"
fi

# Check Claude Code
echo
if command -v claude &>/dev/null; then
    echo "[OK] Claude Code found"
else
    echo "[INFO] Claude Code is not installed."
    echo "Install: npm install -g @anthropic-ai/claude-code"
    echo "Or download from: https://claude.ai/download"
fi

echo
echo "============================================"
echo " Setup complete! Run ./start.sh to begin."
echo "============================================"
