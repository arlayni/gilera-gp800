#!/usr/bin/env bash
# Build portable GP800 USB stick package (Linux + Windows)
# Run this on your development PC to create the USB package.
#
# Usage: ./build-portable.sh /path/to/usb-stick
#
# Prerequisites: pip install pyinstaller pyserial click

set -e

DEST="${1:-./GP800-USB}"
SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo "=== Building GP800 Portable Package ==="
echo "Source: $SCRIPT_DIR"
echo "Destination: $DEST"
echo

# Create directory structure
mkdir -p "$DEST"/{map-files/{original,stock,working,modified},knowledge/schemas,backups}

# Copy knowledge base and schemas
cp -r "$SCRIPT_DIR/knowledge/schemas/"*.json "$DEST/knowledge/schemas/"
cp -r "$SCRIPT_DIR/knowledge/reference" "$DEST/knowledge/" 2>/dev/null || true
cp -r "$SCRIPT_DIR/knowledge/procedures" "$DEST/knowledge/" 2>/dev/null || true

# Copy map files
cp "$SCRIPT_DIR/map-files/original/"*.bin "$DEST/map-files/original/" 2>/dev/null || true
cp "$SCRIPT_DIR/map-files/stock/"*.ddg "$DEST/map-files/stock/" 2>/dev/null || true
cp "$SCRIPT_DIR/map-files/working/"*.bin "$DEST/map-files/working/" 2>/dev/null || true

# Copy tool source (for pip install fallback)
cp -r "$SCRIPT_DIR/gp800-tool" "$DEST/gp800-tool"

# Copy CLAUDE.md
cp "$SCRIPT_DIR/CLAUDE.md" "$DEST/"

# Build standalone executable for current platform
echo "Building standalone executable..."
cd "$SCRIPT_DIR/gp800-tool"
python3 -m PyInstaller \
    --onefile \
    --name gp800-tool \
    --hidden-import serial \
    --hidden-import serial.tools \
    --hidden-import serial.tools.list_ports \
    src/gp800_tool/cli.py \
    2>/dev/null || {
    echo "PyInstaller build failed — including source only (use setup scripts)"
}

# Copy executable if built
if [ -f dist/gp800-tool ]; then
    cp dist/gp800-tool "$DEST/gp800-tool-linux"
    echo "Linux executable: $DEST/gp800-tool-linux"
fi

cd "$SCRIPT_DIR"

echo
echo "=== Package created at $DEST ==="
echo "Copy this folder to a USB stick."
echo "On the target laptop, run setup.bat (Windows) or setup.sh (Linux)."
