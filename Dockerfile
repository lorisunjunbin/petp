# ──────────────────────────────────────────────────────────────────────────────
# PETP background service — multi-arch image
#
# ✅ Build on M1 (arm64), run on x86 (amd64) Docker containers.
#
# One-time buildx setup (run once per machine):
#   docker buildx create --name multiarch --driver docker-container --use
#   docker buildx inspect --bootstrap
#
# Build & push a dual-arch image (arm64 + amd64) to a registry:
#   docker buildx build \
#     --platform linux/amd64,linux/arm64 \
#     -t your-registry/petp-background:latest \
#     --push .
#
# Build amd64-only image and load it locally (for testing on M1):
#   docker buildx build --platform linux/amd64 --load -t petp-background:amd64 .
#
# Run the amd64 image locally on M1 (Rosetta/QEMU emulation):
#   docker run --rm -p 8866:8866 petp-background:amd64
# ──────────────────────────────────────────────────────────────────────────────

ARG PYTHON_VERSION=3.14
FROM --platform=$TARGETPLATFORM python:${PYTHON_VERSION}-slim

# Build-time metadata injected automatically by buildx
ARG TARGETPLATFORM
ARG BUILDPLATFORM
RUN echo "Building on $BUILDPLATFORM, targeting $TARGETPLATFORM"

# ── Runtime environment ────────────────────────────────────────────────────────
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    # Use non-interactive Agg backend so matplotlib never tries to open a window
    MPLBACKEND=Agg

WORKDIR /app

# ── System dependencies ────────────────────────────────────────────────────────
# curl        : health-check probe + general HTTP utility
# libgomp1    : OpenMP runtime required by numpy / pandas / scikit-learn
# libssl-dev  : cryptography / paramiko / requests TLS support
# libffi-dev  : cffi (cryptography dependency)
# git         : some langchain tooling resolves packages via git at install time
# chromium + chromium-driver : headless browser for Selenium tasks
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
        curl \
        libgomp1 \
        libssl-dev \
        libffi-dev \
        git \
        chromium \
        chromium-driver \
 && rm -rf /var/lib/apt/lists/* \
 && chromium --version \
 && chromedriver --version

# ── Python dependencies ────────────────────────────────────────────────────────
# Use requirements-docker.txt (strips X11-only packages: pyautogui, pyperclip)
COPY requirements-docker.txt /app/requirements-docker.txt
COPY requirements/ /app/requirements/
RUN pip install --upgrade pip setuptools wheel \
 && pip install -r /app/requirements-docker.txt

# ── Application source ─────────────────────────────────────────────────────────
COPY . /app

# ── Port & health-check ────────────────────────────────────────────────────────
EXPOSE 8866

HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
    CMD curl -sf http://localhost:8866/health || exit 1

# ── Entry point ────────────────────────────────────────────────────────────────
CMD ["python", "-u", "PETP_background.py"]

