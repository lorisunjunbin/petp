#!/usr/bin/env zsh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

: "${PYTHON_BIN:=python}"
: "${PYTHONMALLOC:=malloc}"
: "${PYTHONUNBUFFERED:=1}"
: "${PYTHONDONTWRITEBYTECODE:=1}"

mode="${1:-gui}"
if [[ "$#" -gt 0 ]]; then
  shift
fi

entry=""
mode_label=""
case "$mode" in
  gui)
    entry="PETP.py"
    mode_label="gui"
    ;;
  bg|background)
    entry="PETP_backgroud.py"
    mode_label="background"
    ;;
  bgd|bg-detach|detach)
    entry="PETP_backgroud.py"
    mode_label="background-detached"
    ;;
  stop)
    cd "$ROOT_DIR"
    exec "$PYTHON_BIN" PETP_background.py --stop
    ;;
  -h|--help|help)
    cat <<'EOF'
Usage:
  ./scripts/macos/start_petp.sh [gui|bg|bgd|stop] [args...]

Modes:
  gui          Launch desktop GUI (default)
  bg           Launch background mode (attached to terminal)
  bgd          Launch background mode detached (nohup, survives terminal close)
  stop         Stop a running background instance (via PID file)

Examples:
  ./scripts/macos/start_petp.sh gui
  ./scripts/macos/start_petp.sh bg --run-execution ENDECODER --no-http
  ./scripts/macos/start_petp.sh bg --run-execution MY_EXEC --headless --no-http
  ./scripts/macos/start_petp.sh bgd
  ./scripts/macos/start_petp.sh bgd --headless
  ./scripts/macos/start_petp.sh stop

Environment variables (optional):
  PYTHON_BIN              Python executable (default: python)
  PYTHONMALLOC            Memory allocator strategy (default: malloc)
  PYTHONUNBUFFERED        Unbuffered stdout/stderr (default: 1)
  PYTHONDONTWRITEBYTECODE Disable .pyc writes (default: 1)
  PETP_ECHO_ENV           Set to 1 to print effective settings
EOF
    exit 0
    ;;
  *)
    echo "Unsupported mode: $mode" >&2
    echo "Try: ./scripts/macos/start_petp.sh --help" >&2
    exit 2
    ;;
esac

if [[ "${PETP_ECHO_ENV:-0}" == "1" ]]; then
  echo "[PETP] mode=$mode_label"
  echo "[PETP] root=$ROOT_DIR"
  echo "[PETP] python_bin=$PYTHON_BIN"
  echo "[PETP] PYTHONMALLOC=$PYTHONMALLOC"
  echo "[PETP] PYTHONUNBUFFERED=$PYTHONUNBUFFERED"
  echo "[PETP] PYTHONDONTWRITEBYTECODE=$PYTHONDONTWRITEBYTECODE"
fi

cd "$ROOT_DIR"

if [[ "$mode_label" == "background-detached" ]]; then
  LOG_FILE="${PETP_BG_LOG:-petp_bg.log}"
  nohup "$PYTHON_BIN" "$entry" "$@" > "$LOG_FILE" 2>&1 &
  echo "[PETP] Background started (PID=$!, log=$LOG_FILE)"
else
  exec "$PYTHON_BIN" "$entry" "$@"
fi

