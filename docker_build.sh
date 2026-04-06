#!/usr/bin/env bash
# docker_build.sh
# Build the PETP background Docker image on M1 (arm64).
# Default: builds linux/amd64 image and loads it locally.
# With --push: builds linux/amd64 + linux/arm64 and pushes to a registry.
#
# Usage:
#   ./docker_build.sh                           # amd64 local image
#   ./docker_build.sh --push myrepo/petp:1.0    # push dual-arch to registry
#   ./docker_build.sh --help
set -euo pipefail

IMAGE_NAME="petp-background"
BUILDER_NAME="petp-multiarch"
PUSH_TARGET=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --push)
      PUSH_TARGET="$2"
      shift 2
      ;;
    --help|-h)
      echo "Usage: $0 [--push <registry/image:tag>]"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

# Ensure a buildx builder with QEMU emulation support exists
if ! docker buildx inspect "${BUILDER_NAME}" >/dev/null 2>&1; then
  echo "Creating buildx builder '${BUILDER_NAME}' ..."
  docker buildx create --name "${BUILDER_NAME}" --driver docker-container --use
fi
docker buildx use "${BUILDER_NAME}"
docker buildx inspect --bootstrap 2>&1 | grep -E "^(Name|Platforms)" || true

if [[ -n "${PUSH_TARGET}" ]]; then
  echo ""
  echo "Building linux/amd64 + linux/arm64 and pushing to: ${PUSH_TARGET}"
  docker buildx build \
    --platform linux/amd64,linux/arm64 \
    --tag "${PUSH_TARGET}" \
    --push \
    .
  echo ""
  echo "Done. On any x86 host run:"
  echo "  docker pull ${PUSH_TARGET}"
  echo "  docker run --rm -p 8866:8866 ${PUSH_TARGET}"
else
  LOCAL_TAG="${IMAGE_NAME}:amd64-local"
  echo ""
  echo "Building linux/amd64 image -> '${LOCAL_TAG}' (QEMU cross-compile, ~5 min first run)"
  docker buildx build \
    --platform linux/amd64 \
    --tag "${LOCAL_TAG}" \
    --load \
    .
  echo ""
  echo "Done. Test with:"
  echo "  docker run --rm -p 8866:8866 ${LOCAL_TAG}"
  echo "  curl http://localhost:8866/health"
fi

