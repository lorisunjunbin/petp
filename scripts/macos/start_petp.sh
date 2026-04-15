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
  -h|--help|help)
    cat <<'EOF'
Usage:
  ./scripts/macos/start_petp.sh [gui|bg|background] [args...]

Examples:
  ./scripts/macos/start_petp.sh gui
  ./scripts/macos/start_petp.sh bg --run-execution ENDECODER --no-http

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
exec "$PYTHON_BIN" "$entry" "$@"

