#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────────────────────
# Build PETP Web App Docker image and export as tar
#
# Usage:
#   ./build/script/docker_build_webapp.sh                  # build amd64, export tar
#   ./build/script/docker_build_webapp.sh --no-tar         # build only, skip tar export
#   ./build/script/docker_build_webapp.sh --run            # build + run container
#   ./build/script/docker_build_webapp.sh --push repo:tag  # build dual-arch and push
# ──────────────────────────────────────────────────────────────────────────────
set -euo pipefail

cd "$(dirname "$0")/../.."

IMAGE_NAME="petp-webapp"
LOCAL_TAG="${IMAGE_NAME}:amd64-local"
TAR_OUTPUT="build/petp-webapp-amd64.tar"
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
BUILD_CONTEXT="webapp"
CLEANUP_CONTEXT=""

if [[ "${USE_GIT_ARCHIVE}" == "true" ]]; then
  BUILD_CONTEXT=$(mktemp -d)
  CLEANUP_CONTEXT="${BUILD_CONTEXT}"
  echo "[0/4] Exporting git-tracked webapp/ files to clean build context ..."
  git archive HEAD -- webapp/ | tar -x -C "${BUILD_CONTEXT}" --strip-components=1
  # Also include staged but uncommitted webapp files (overwrite on top)
  git diff --cached --name-only --diff-filter=ACM -- webapp/ | while IFS= read -r f; do
    if [[ -n "$f" && -f "$f" ]]; then
      local_path="${f#webapp/}"
      mkdir -p "${BUILD_CONTEXT}/$(dirname "$local_path")"
      cp "$f" "${BUILD_CONTEXT}/$local_path"
    fi
  done
  # Also include unstaged modified/added webapp files
  git diff --name-only --diff-filter=ACM -- webapp/ | while IFS= read -r f; do
    if [[ -n "$f" && -f "$f" ]]; then
      local_path="${f#webapp/}"
      mkdir -p "${BUILD_CONTEXT}/$(dirname "$local_path")"
      cp "$f" "${BUILD_CONTEXT}/$local_path"
    fi
  done
  echo "       Context: ${BUILD_CONTEXT} (git-tracked + modified files)"
fi

trap '[[ -n "${CLEANUP_CONTEXT}" ]] && rm -rf "${CLEANUP_CONTEXT}"' EXIT

# Sync image assets from project image/ → build context build_assets/
echo "[0/4] Syncing image assets to build context ..."
python webapp/scripts/prepare_assets.py \
  --source image \
  --target "${BUILD_CONTEXT}/build_assets" \
  --files PETP_overview.png PETP_overview_windows.png \
          HTTP_SERVICE_ENABLED.png petp_as_standard_mcp_server.png \
          claude-code-mcp-tool.png DEEPSEEK-MCP.png user_manual.png

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
    -f "${BUILD_CONTEXT}/Dockerfile" \
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
  -f "${BUILD_CONTEXT}/Dockerfile" \
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
  echo "[4/4] Starting container on port 5555 ..."
  docker run --rm -d -p 5555:5555 --name petp-webapp "${LOCAL_TAG}"
  sleep 5
  if curl -sf http://localhost:5555/ >/dev/null 2>&1; then
    echo "       Health check passed: http://localhost:5555/"
    echo "       Stop with: docker stop petp-webapp"
  else
    echo "       Warning: health check failed, checking logs ..."
    docker logs petp-webapp 2>&1 | tail -10
  fi
else
  echo ""
  echo "[4/4] Done."
  echo ""
  echo "To load on target machine:"
  echo "  docker load -i ${TAR_OUTPUT}"
  echo "  docker run --rm -p 5555:5555 ${LOCAL_TAG}"
fi
