#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────────────────────
# Deploy PETP Web App Docker image to NAS
#
# Usage:
#   ./build/script/deploy_webapp_to_nas.sh                # full deploy (scp + load + run)
#   ./build/script/deploy_webapp_to_nas.sh --no-start     # scp + load only
#   ./build/script/deploy_webapp_to_nas.sh --keep-tar     # don't delete remote tar after load
#
# Environment variables (override defaults):
#   NAS_HOST       NAS IP/hostname       (default: 192.168.1.100)
#   NAS_USER       SSH username           (default: admin)
#   NAS_PORT       SSH port               (default: 22)
#   NAS_DOCKER_DIR Remote temp directory  (default: /tmp)
#   HOST_PORT      Host port mapping      (default: 8088)
# ──────────────────────────────────────────────────────────────────────────────
set -euo pipefail

cd "$(dirname "$0")/../.."

# ── Configuration ─────────────────────────────────────────────────────────────
NAS_HOST="${NAS_HOST:-192.168.0.103}"
NAS_USER="${NAS_USER:-sunjunbin}"
NAS_PORT="${NAS_PORT:-22}"
NAS_DOCKER_DIR="${NAS_DOCKER_DIR:-/home/sunjunbin/temp}"

IMAGE_TAG="petp-webapp:amd64-local"
LOCAL_TAR="build/petp-webapp-amd64.tar"
CONTAINER_NAME="petp-webapp"
HOST_PORT="${HOST_PORT:-8088}"
CONTAINER_PORT="5555"

START_CONTAINER=true
KEEP_TAR=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --no-start) START_CONTAINER=false; shift ;;
    --keep-tar) KEEP_TAR=true; shift ;;
    --help|-h)
      echo "Usage: $0 [--no-start] [--keep-tar]"
      echo ""
      echo "Environment variables:"
      echo "  NAS_HOST=$NAS_HOST  NAS_USER=$NAS_USER  NAS_PORT=$NAS_PORT"
      echo "  NAS_DOCKER_DIR=$NAS_DOCKER_DIR  HOST_PORT=$HOST_PORT"
      exit 0
      ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

TAR_FILENAME=$(basename "${LOCAL_TAR}")
REMOTE_TAR="${NAS_DOCKER_DIR}/${TAR_FILENAME}"
SSH_CMD="ssh -t -p ${NAS_PORT} ${NAS_USER}@${NAS_HOST}"

# ── Preflight ─────────────────────────────────────────────────────────────────
if [[ ! -f "${LOCAL_TAR}" ]]; then
  echo "Error: ${LOCAL_TAR} not found. Run ./build/script/docker_build_webapp.sh first."
  exit 1
fi

TAR_SIZE=$(ls -lh "${LOCAL_TAR}" | awk '{print $5}')
echo "Deploying ${IMAGE_TAG} to ${NAS_USER}@${NAS_HOST}"
echo "  Local tar: ${LOCAL_TAR} (${TAR_SIZE})"
echo "  Remote:    ${REMOTE_TAR}"
echo ""

# ── Step 1: Transfer ──────────────────────────────────────────────────────────
echo "[1/4] Uploading tar to NAS ..."
${SSH_CMD} "mkdir -p ${NAS_DOCKER_DIR}"
scp -O -P "${NAS_PORT}" "${LOCAL_TAR}" "${NAS_USER}@${NAS_HOST}:${REMOTE_TAR}"
echo "       Upload complete."

# ── Step 2: Docker load ───────────────────────────────────────────────────────
echo ""
echo "[2/4] Loading image on NAS ..."
${SSH_CMD} "sudo docker load -i ${REMOTE_TAR}"

# ── Step 3: Clean remote tar ─────────────────────────────────────────────────
if [[ "${KEEP_TAR}" == "false" ]]; then
  echo ""
  echo "[3/4] Removing remote tar ..."
  ${SSH_CMD} "rm -f ${REMOTE_TAR}"
else
  echo ""
  echo "[3/4] Keeping remote tar: ${REMOTE_TAR}"
fi

# ── Step 4: Start container ──────────────────────────────────────────────────
if [[ "${START_CONTAINER}" == "true" ]]; then
  echo ""
  echo "[4/4] Starting container (${HOST_PORT}:${CONTAINER_PORT}) ..."
  ${SSH_CMD} "sudo docker stop ${CONTAINER_NAME} 2>/dev/null || true; \
              sudo docker rm -f ${CONTAINER_NAME} 2>/dev/null || true; \
              sudo docker ps -q --filter publish=${HOST_PORT} | xargs -r sudo docker rm -f 2>/dev/null || true; \
              sleep 2; \
              sudo docker run -d --restart unless-stopped \
                --name ${CONTAINER_NAME} \
                -p ${HOST_PORT}:${CONTAINER_PORT} \
                ${IMAGE_TAG}"
  echo ""
  echo "       Container started. Verifying ..."
  ${SSH_CMD} "sudo docker ps --filter name=${CONTAINER_NAME} --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'"
else
  echo ""
  echo "[4/4] Skipped container start (--no-start)"
  echo "       To start manually on NAS:"
  echo "       docker run -d --restart unless-stopped --name ${CONTAINER_NAME} -p ${HOST_PORT}:${CONTAINER_PORT} ${IMAGE_TAG}"
fi

# ── Step 5: Refresh Tailscale Funnel ─────────────────────────────────────────
FUNNEL_SCRIPT="/home/sunjunbin/script/tailscale_funnel_refresh.sh"
echo ""
echo "[5/5] Refreshing Tailscale Funnel ..."
${SSH_CMD} "${FUNNEL_SCRIPT}"
