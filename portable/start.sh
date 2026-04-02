#!/usr/bin/env bash
# GP800 Tool — Start Session (Linux)

echo "============================================"
echo " GP800 Tool - Live Session"
echo "============================================"
echo

# Detect USB-KKL adapter
echo "Detecting serial ports..."
python3 -c "
import serial.tools.list_ports
for p in serial.tools.list_ports.comports():
    print(f'  {p.device}: {p.description}')
" 2>/dev/null || echo "  [Could not list ports]"
echo

cd "$(dirname "$0")"

if command -v claude &>/dev/null; then
    echo "Starting Claude Code..."
    echo "Claude can run gp800-tool commands and analyze ECU data in real-time."
    echo
    claude
else
    echo "Claude Code not installed — manual mode."
    echo
    echo "Commands:"
    echo "  gp800-tool connect /dev/ttyUSB0"
    echo "  gp800-tool read /dev/ttyUSB0 backup.bin"
    echo "  gp800-tool dtc /dev/ttyUSB0"
    echo "  gp800-tool live /dev/ttyUSB0"
    echo "  gp800-tool flash /dev/ttyUSB0 modified.bin"
    echo
    exec bash
fi
