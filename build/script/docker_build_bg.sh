#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────────────────────
# Build PETP Background Docker image and export as tar
#
# Usage:
#   ./build/script/docker_build_bg.sh                  # build amd64, export tar
#   ./build/script/docker_build_bg.sh --no-tar         # build only, skip tar export
#   ./build/script/docker_build_bg.sh --run            # build + run container
#   ./build/script/docker_build_bg.sh --push repo:tag  # build dual-arch and push
# ──────────────────────────────────────────────────────────────────────────────
set -euo pipefail

cd "$(dirname "$0")/../.."

IMAGE_NAME="petp-background"
LOCAL_TAG="${IMAGE_NAME}:amd64-local"
TAR_OUTPUT="build/petp-background-amd64.tar"
BUILDER_NAME="petp-multiarch"
PUSH_TARGET=""
SKIP_TAR=false
RUN_AFTER=false
USE_GIT_ARCHIVE=true

while [[ $# -gt 0 ]]; do
  case "$1" in
    --no-tar)   SKIP_TAR=true; shift ;;
    --run)      RUN_AFTER=true; shift ;;
    --push)     PUSH_TARGET="$2"; shift 2 ;;
    --dirty)    USE_GIT_ARCHIVE=false; shift ;;
    --help|-h)
      echo "Usage: $0 [--no-tar] [--run] [--push <registry/image:tag>] [--dirty]"
      exit 0
      ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

# Check Docker is running
if ! docker info >/dev/null 2>&1; then
  echo "Error: Docker is not running. Please start Docker Desktop and try again."
  exit 1
fi

# ── Preflight: clean previous tar ─────────────────────────────────────────────
if [[ -f "${TAR_OUTPUT}" ]]; then
  echo "[0/4] Removing previous tar: ${TAR_OUTPUT}"
  rm -f "${TAR_OUTPUT}"
fi

# Prepare clean build context (git-tracked files only)
BUILD_CONTEXT="."
CLEANUP_CONTEXT=""

if [[ "${USE_GIT_ARCHIVE}" == "true" ]]; then
  BUILD_CONTEXT=$(mktemp -d)
  CLEANUP_CONTEXT="${BUILD_CONTEXT}"
  echo "[0/4] Exporting git-tracked files to clean build context ..."
  git archive HEAD | tar -x -C "${BUILD_CONTEXT}"
  # Also include staged but uncommitted files (overwrite on top)
  git diff --cached --name-only --diff-filter=ACM | while IFS= read -r f; do
    if [[ -n "$f" && -f "$f" ]]; then
      mkdir -p "${BUILD_CONTEXT}/$(dirname "$f")"
      cp "$f" "${BUILD_CONTEXT}/$f"
    fi
  done
  # Also include unstaged modified/added files (working directory changes)
  git diff --name-only --diff-filter=ACM | while IFS= read -r f; do
    if [[ -n "$f" && -f "$f" ]]; then
      mkdir -p "${BUILD_CONTEXT}/$(dirname "$f")"
      cp "$f" "${BUILD_CONTEXT}/$f"
    fi
  done
  echo "       Context: ${BUILD_CONTEXT} (git-tracked + modified files)"
  # Remove unreleased executions (reuse EXECUTIONS_RELEASED from build_common.py)
  echo "       Filtering executions to released-only ..."
  python -c "
import sys, os
sys.path.insert(0, 'build')
from build_common import EXECUTIONS_RELEASED
exec_dir = os.path.join('${BUILD_CONTEXT}', 'core', 'executions')
if os.path.isdir(exec_dir):
    for f in os.listdir(exec_dir):
        if f.endswith('.yaml') and f not in EXECUTIONS_RELEASED:
            os.remove(os.path.join(exec_dir, f))
            print(f'  removed: {f}')
"
fi

trap '[[ -n "${CLEANUP_CONTEXT}" ]] && rm -rf "${CLEANUP_CONTEXT}"' EXIT

# Ensure buildx builder exists
if ! docker buildx inspect "${BUILDER_NAME}" >/dev/null 2>&1; then
  echo "[1/4] Creating buildx builder '${BUILDER_NAME}' ..."
  docker buildx create --name "${BUILDER_NAME}" --driver docker-container --use
fi
docker buildx use "${BUILDER_NAME}"

if [[ -n "${PUSH_TARGET}" ]]; then
  echo ""
  echo "Building linux/amd64 + linux/arm64 and pushing to: ${PUSH_TARGET}"
  docker buildx build \
    --platform linux/amd64,linux/arm64 \
    --tag "${PUSH_TARGET}" \
    --push \
    "${BUILD_CONTEXT}"
  echo "Done. Pull with: docker pull ${PUSH_TARGET}"
  exit 0
fi

# Build amd64 image
echo ""
echo "[1/4] Building linux/amd64 image -> '${LOCAL_TAG}'"
docker buildx build \
  --platform linux/amd64 \
  --tag "${LOCAL_TAG}" \
  --load \
  "${BUILD_CONTEXT}"

# Show image size
SIZE=$(docker images "${LOCAL_TAG}" --format "{{.Size}}")
echo ""
echo "[2/4] Image built: ${LOCAL_TAG} (${SIZE})"

# Export tar
if [[ "${SKIP_TAR}" == "false" ]]; then
  echo ""
  echo "[3/4] Exporting to ${TAR_OUTPUT} ..."
  docker save "${LOCAL_TAG}" -o "${TAR_OUTPUT}"
  TAR_SIZE=$(ls -lh "${TAR_OUTPUT}" | awk '{print $5}')
  echo "       Tar exported: ${TAR_OUTPUT} (${TAR_SIZE})"
else
  echo ""
  echo "[3/4] Skipped tar export (--no-tar)"
fi

# Run container
if [[ "${RUN_AFTER}" == "true" ]]; then
  echo ""
  echo "[4/4] Starting container on port 8866 ..."
  docker run --rm -d -p 8866:8866 --name petp-bg "${LOCAL_TAG}"
  sleep 8
  if curl -sf http://localhost:8866/health >/dev/null 2>&1; then
    echo "       Health check passed: http://localhost:8866/health"
    echo "       Stop with: docker stop petp-bg"
  else
    echo "       Warning: health check failed, checking logs ..."
    docker logs petp-bg 2>&1 | tail -10
  fi
else
  echo ""
  echo "[4/4] Done."
  echo ""
  echo "To load on target machine:"
  echo "  docker load -i ${TAR_OUTPUT}"
  echo "  docker run --rm -p 8866:8866 ${LOCAL_TAG}"
fi
