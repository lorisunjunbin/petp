#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────────────────────
# Refresh Tailscale Funnel routes for PETP services
#
# Usage:
#   ./build/script/tailscale_funnel_refresh.sh          # reset + reconfigure
#   ./build/script/tailscale_funnel_refresh.sh --status # show current status only
#
# Routes configured:
#   /       → localhost:8088 (webapp)
#   /mcp    → localhost:8866 (petp background MCP)
#
# Environment variables (override defaults):
#   WEBAPP_PORT    Webapp port   (default: 8088)
#   BG_PORT        BG port       (default: 8866)
# ──────────────────────────────────────────────────────────────────────────────
set -euo pipefail

WEBAPP_PORT="${WEBAPP_PORT:-8088}"
BG_PORT="${BG_PORT:-8866}"

if [[ "${1:-}" == "--status" ]]; then
  tailscale status
  echo ""
  tailscale funnel status
  exit 0
fi

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
  echo "Usage: $0 [--status]"
  echo ""
  echo "Resets Tailscale Funnel and reconfigures:"
  echo "  /     → localhost:${WEBAPP_PORT} (webapp)"
  echo "  /mcp  → localhost:${BG_PORT} (petp bg)"
  exit 0
fi

echo "[1/4] Tailscale status ..."
tailscale status

echo ""
echo "[2/4] Resetting funnel ..."
tailscale funnel reset

echo ""
echo "[3/4] Configuring funnel: / → localhost:${WEBAPP_PORT} (webapp) ..."
tailscale funnel --bg "${WEBAPP_PORT}"

echo ""
echo "[4/4] Configuring funnel: /mcp → localhost:${BG_PORT} (petp bg) ..."
tailscale funnel --set-path /mcp --bg "${BG_PORT}"

echo ""
echo "Done. Current funnel status:"
tailscale funnel status
