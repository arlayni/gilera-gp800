#!/usr/bin/env bash
# GP800 Tool — Dubbelklik en klaar! (Linux/Mac)
# Installeert automatisch, opent GUI + Claude Code

cd "$(dirname "$0")"

# Check Python
if ! command -v python3 &>/dev/null; then
    echo "Python 3 is niet geinstalleerd!"
    echo "Install: sudo apt install python3 python3-pip python3-tk"
    read -p "Press enter..."
    exit 1
fi

# Auto-install
if ! python3 -m gp800_tool.cli --version &>/dev/null; then
    echo "Eerste keer? Installeren..."
    cd gp800-tool
    pip install --user --no-build-isolation -e ".[kline]" --quiet 2>/dev/null
    cd ..
    echo "Installatie compleet!"
fi

# Start GUI op achtergrond
python3 -m gp800_tool.gui &
echo "GP800 GUI gestart"

# Start Claude Code
if command -v claude &>/dev/null; then
    echo "Starting Claude Code..."
    claude
else
    echo "Claude Code niet geinstalleerd. Terminal mode:"
    echo "  gp800-tool --help"
    exec bash
fi
