#!/usr/bin/env bash
# GP800 Pi Setup — Raspberry Pi 4, Raspberry Pi OS (Bookworm)
# Runt één keer na een verse installatie.
# Installeer Tailscale apart via: curl -fsSL https://tailscale.com/install.sh | sh
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TOOL_DIR="$REPO_DIR/gp800-tool"
SERVICE_FILE="$REPO_DIR/pi-setup/gp800-api.service"
LOG_DIR="$HOME/gp800-logs"
SERIAL_PORT="${GP800_PORT:-/dev/ttyUSB0}"

echo "=== GP800 Pi Setup ==="
echo "Repo:    $REPO_DIR"
echo "Poort:   $SERIAL_PORT"
echo "Logs:    $LOG_DIR"
echo ""

# --- System deps ---
sudo apt-get update -q
sudo apt-get install -y -q python3-pip python3-venv git

# --- Python venv ---
if [ ! -d "$HOME/gp800-venv" ]; then
    python3 -m venv "$HOME/gp800-venv"
fi
source "$HOME/gp800-venv/bin/activate"

pip install --upgrade pip -q
pip install -e "$TOOL_DIR[api,kline]" -q

echo "gp800-tool geinstalleerd: $(gp800-tool --version)"

# --- Log directory ---
mkdir -p "$LOG_DIR"

# --- Seriële poort permissies ---
sudo usermod -aG dialout "$USER"
echo "Toegevoegd aan dialout groep (herstart vereist)"

# --- Systemd service ---
# Vervang placeholder in service file en installeer
sed "s|__USER__|$USER|g; s|__REPO_DIR__|$REPO_DIR|g; s|__SERIAL_PORT__|$SERIAL_PORT|g; s|__LOG_DIR__|$LOG_DIR|g" \
    "$SERVICE_FILE" | sudo tee /etc/systemd/system/gp800-api.service > /dev/null

sudo systemctl daemon-reload
sudo systemctl enable gp800-api
sudo systemctl start gp800-api

echo ""
echo "=== Klaar! ==="
echo "Service status: sudo systemctl status gp800-api"
echo "Logs bekijken:  sudo journalctl -u gp800-api -f"
echo ""
echo "Dashboard bereikbaar op:"
echo "  http://$(hostname -I | awk '{print $1}'):8000"
echo ""
echo "Verbind je iPhone via Tailscale en ga naar:"
echo "  http://$(hostname).your-tailnet.ts.net:8000"
echo ""
echo "Herstart de Pi voor dialout groep te activeren: sudo reboot"
