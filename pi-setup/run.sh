#!/usr/bin/env bash
# Gestart door systemd — activeer venv en start de API.
set -euo pipefail

source "$HOME/gp800-venv/bin/activate"

PORT="${GP800_PORT:-/dev/ttyUSB0}"
LOG_DIR="${GP800_LOG_DIR:-$HOME/gp800-logs}"

exec gp800-tool serve "$PORT" \
    --host 0.0.0.0 \
    --api-port 8000 \
    --log-dir "$LOG_DIR"
