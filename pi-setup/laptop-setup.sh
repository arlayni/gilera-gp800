#!/usr/bin/env bash
# GP800 Laptop Setup — eenmalig uitvoeren op je laptop
# Configureert SSH toegang tot de Raspberry Pi
set -euo pipefail

PI_HOST="${1:-raspberrypi.local}"
PI_USER="${2:-pi}"
KEY_FILE="$HOME/.ssh/gp800_pi"

echo "=== GP800 Laptop Setup ==="
echo "Pi adres: $PI_HOST"
echo "Pi user:  $PI_USER"
echo ""

# --- SSH key aanmaken ---
if [ ! -f "$KEY_FILE" ]; then
  echo "SSH key aanmaken..."
  ssh-keygen -t ed25519 -f "$KEY_FILE" -C "gp800-laptop" -N ""
  echo "Key aangemaakt: $KEY_FILE"
else
  echo "SSH key bestaat al: $KEY_FILE"
fi

# --- SSH config toevoegen ---
SSH_CONFIG="$HOME/.ssh/config"
if ! grep -q "Host gp800-pi" "$SSH_CONFIG" 2>/dev/null; then
  cat >> "$SSH_CONFIG" << EOF

Host gp800-pi
  HostName $PI_HOST
  User $PI_USER
  IdentityFile $KEY_FILE
  ServerAliveInterval 30
  ServerAliveCountMax 3
EOF
  echo "SSH config toegevoegd (alias: gp800-pi)"
else
  echo "SSH config bestaat al (alias: gp800-pi)"
fi

# --- Key naar Pi kopiëren ---
echo ""
echo "SSH key naar Pi kopiëren (wachtwoord van Pi vereist)..."
ssh-copy-id -i "$KEY_FILE.pub" "$PI_USER@$PI_HOST"

# --- Verbinding testen ---
echo ""
echo "Verbinding testen..."
if ssh gp800-pi "echo 'Verbinding OK'" 2>/dev/null; then
  echo "SSH verbinding werkt."
else
  echo "Verbinding mislukt. Controleer of Pi aanstaat en op hetzelfde netwerk zit."
  exit 1
fi

# --- tune-session.sh installeren op Pi ---
echo ""
echo "tune-session.sh installeren op Pi..."
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
scp "$SCRIPT_DIR/tune-session.sh" "gp800-pi:~/tune-session.sh"
ssh gp800-pi "chmod +x ~/tune-session.sh"
echo "Geinstalleerd op Pi: ~/tune-session.sh"

# --- Claude Code check ---
echo ""
if command -v claude &>/dev/null; then
  echo "Claude Code: $(claude --version 2>/dev/null || echo 'gevonden')"
else
  echo "Claude Code niet gevonden."
  echo "Installeer via: npm install -g @anthropic-ai/claude-code"
fi

echo ""
echo "=== Setup klaar! ==="
echo ""
echo "Verbinden met Pi:     ssh gp800-pi"
echo "Tuning starten:       ssh gp800-pi './tune-session.sh start'"
echo "Live data bekijken:   ssh gp800-pi './tune-session.sh log'"
echo "ECU map ophalen:      ssh gp800-pi './tune-session.sh read' && scp gp800-pi:/tmp/current.bin ."
echo "Map flashen:          scp nieuw.bin gp800-pi:/tmp/ && ssh gp800-pi './tune-session.sh flash /tmp/nieuw.bin'"
echo ""
echo "Start Claude Code in de project map en typ:"
echo "  claude"
