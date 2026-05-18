#!/usr/bin/env bash
# GP800 Tuning Session — draait op de Raspberry Pi
# Gestart door Claude Code via SSH vanaf laptop
# Gebruik: ./tune-session.sh [start|stop|status|log|read|flash]
set -euo pipefail

VENV="$HOME/gp800-venv"
PORT="${GP800_PORT:-/dev/ttyUSB0}"
SESSION_DIR="$HOME/gp800-logs/sessions"
SESSION_FILE="$SESSION_DIR/$(date +%Y%m%d_%H%M%S)_session.jsonl"
PID_FILE="/tmp/gp800-live.pid"

gp800() { "$VENV/bin/gp800-tool" "$@"; }

cmd="${1:-status}"
shift || true

case "$cmd" in

  start)
    mkdir -p "$SESSION_DIR"
    echo "=== GP800 Tuning Sessie gestart ==="
    echo "Poort:  $PORT"
    echo "Log:    $SESSION_FILE"
    echo ""
    # Start live logging op achtergrond
    "$VENV/bin/gp800-tool" live "$PORT" --interval 1 \
      | tee "$SESSION_FILE" &
    echo $! > "$PID_FILE"
    echo "PID: $(cat $PID_FILE)"
    echo "Stop met: tune-session.sh stop"
    ;;

  stop)
    if [ -f "$PID_FILE" ]; then
      kill "$(cat $PID_FILE)" 2>/dev/null && echo "Sessie gestopt." || echo "Proces al gestopt."
      rm -f "$PID_FILE"
    else
      echo "Geen actieve sessie gevonden."
    fi
    ;;

  status)
    echo "=== GP800 Status ==="
    echo "Poort:  $PORT"
    if [ -f "$PID_FILE" ] && kill -0 "$(cat $PID_FILE)" 2>/dev/null; then
      echo "Live:   ACTIEF (PID $(cat $PID_FILE))"
    else
      echo "Live:   gestopt"
    fi
    echo ""
    echo "Laatste log regels:"
    ls -t "$SESSION_DIR"/*.jsonl 2>/dev/null | head -1 | xargs tail -5 2>/dev/null || echo "(geen logs)"
    ;;

  log)
    # Stream live log naar stdout — Claude Code leest dit via SSH
    LATEST=$(ls -t "$SESSION_DIR"/*.jsonl 2>/dev/null | head -1)
    if [ -z "$LATEST" ]; then
      echo "Geen log beschikbaar. Start eerst een sessie."
      exit 1
    fi
    echo "Streaming: $LATEST"
    tail -f "$LATEST"
    ;;

  read)
    # ECU map uitlezen → /tmp/current.bin
    OUTPUT="${1:-/tmp/current.bin}"
    echo "ECU map uitlezen naar $OUTPUT..."
    gp800 read "$PORT" --output "$OUTPUT"
    echo "Klaar: $OUTPUT ($(wc -c < "$OUTPUT") bytes)"
    ;;

  dtc)
    # Foutcodes uitlezen
    gp800 dtc "$PORT"
    ;;

  clear-dtc)
    gp800 dtc "$PORT" --clear
    ;;

  flash)
    # Map flashen — vereist bestandsnaam als argument
    FILE="${1:-}"
    if [ -z "$FILE" ]; then
      echo "Gebruik: tune-session.sh flash <bestand.bin>"
      exit 1
    fi
    if [ ! -f "$FILE" ]; then
      echo "Bestand niet gevonden: $FILE"
      exit 1
    fi
    echo "=== FLASH ==="
    echo "Bestand: $FILE"
    echo "Validatie..."
    gp800 validate "$FILE" || { echo "GEBLOKKEERD — validatie mislukt"; exit 1; }
    echo ""
    echo "Flashen..."
    gp800 flash "$PORT" "$FILE"
    ;;

  validate)
    FILE="${1:-}"
    [ -z "$FILE" ] && { echo "Gebruik: tune-session.sh validate <bestand>"; exit 1; }
    gp800 validate "$FILE"
    ;;

  *)
    echo "Gebruik: tune-session.sh [start|stop|status|log|read|dtc|clear-dtc|flash <file>|validate <file>]"
    exit 1
    ;;
esac
