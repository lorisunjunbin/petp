## PETP WEB

This web project is designed to introduce PETP from three perspectives: technical architecture, core features, and applicable scenarios.

Lightweight Flask web app for PETP with:
- public landing pages (`/`, `/about`)
- session-based login for the file viewer (`/login` -> `/fileviewer`)
- Basic Auth API for file search (`/api/v1/search/files/`)

### Local Run

```bash
pip install -r requirements.txt
python app.py
```

Open:
- Home: http://localhost:5555
- About: http://localhost:5555/about
- Login: http://localhost:5555/login
- File Viewer (after login): http://localhost:5555/fileviewer
- Default users: `petp` / `petp`, `petp-admin` / `petp-admin`

Tip:
- UI pages support language switch via `?lang=en` / `?lang=zh`.

### Route Overview

- `GET /` - home page
- `GET /about` - PETP intro page
- `GET|POST /login` - session login
- `GET /logout` - clear session and return home
- `GET /fileviewer` - session-protected file viewer
- `POST /<SHARED_FOLDER>/<path>` - session-protected file download endpoint used by the viewer
- `GET /api/v1/search/files/?q=<keyword>` - Basic Auth API for searching files
- `GET /petp-image/<path>` - project images (prefer `webapp/static/images`, fallback to repository `image/`)

### Docker (Standalone Image)

- Base image: `python:3.14-slim`
- Build step runs `scripts/prepare_assets.py` to copy required overview images from `build_assets/` to `static/images/`:
  - `PETP_overview.png`
  - `PETP_overview_windows.png`

Build from `webapp/` directory:

```bash
docker build -t petp-webapp:latest .
```

Run container:

```bash
docker run --rm -p 5555:5555 \
  -e PORT=5555 \
  -e SHARED_FOLDER=shared \
  -e WEBAPP_USERS='petp:petp,petp-admin:petp-admin' \
  -e WEBAPP_SECRET_KEY='change-me-in-production' \
  petp-webapp:latest
```

Run with host shared folder mounted:

```bash
docker run --rm -p 5555:5555 \
  -e PORT=5555 \
  -e SHARED_FOLDER=shared \
  -e WEBAPP_USERS='petp:petp' \
  -e WEBAPP_SECRET_KEY='change-me-in-production' \
  -v "$(pwd)/shared:/app/shared" \
  petp-webapp:latest
```

### Build for NAS (linux x64 / amd64)

On Apple Silicon or any non-x64 host, explicitly build `linux/amd64`; otherwise, the exported image may be rejected by NAS due to architecture mismatch.

1) Build an amd64 image from `webapp/`:

```bash
docker --context=desktop-linux buildx build \
  --builder desktop-linux \
  --platform linux/amd64 \
  -t petp-webapp:amd64 \
  --load \
  .
```

2) Verify image architecture (expected output includes `amd64/linux`):

```bash
docker image inspect petp-webapp:amd64 --format '{{.Architecture}}/{{.Os}}'
```

3) Export tar:

```bash
docker save -o petp-webapp_amd64.tar petp-webapp:amd64
```

4) Upload `petp-webapp_amd64.tar` to NAS, then import:

```bash
docker load -i petp-webapp_amd64.tar
```

5) Run on NAS (example):

```bash
docker run -d --name petp-webapp \
  -p 5555:5555 \
  -e PORT=5555 \
  -e SHARED_FOLDER=shared \
  -e WEBAPP_USERS='petp:petp,petp-admin:petp-admin' \
  -e WEBAPP_SECRET_KEY='change-me-in-production' \
  petp-webapp:amd64
```

6) Mount a NAS shared folder (example path):

```bash
docker run -d --name petp-webapp \
  -p 5555:5555 \
  -e PORT=5555 \
  -e SHARED_FOLDER=shared \
  -e WEBAPP_USERS='petp:petp' \
  -e WEBAPP_SECRET_KEY='change-me-in-production' \
  -v /volume1/docker/petp/shared:/app/shared \
  petp-webapp:amd64
```

### Config via Environment Variables

- `PORT` (default: `5555`)
- `SHARED_FOLDER` (default: `shared`)
- `WEBAPP_USERS` format: `user1:pass1,user2:pass2`
- `WEBAPP_SECRET_KEY` (optional but recommended in production)

### Notes

- Session login protects page routes (`/fileviewer` and shared-file endpoint).
- Basic Auth protects the search API (`/api/v1/search/files/`).
- If `WEBAPP_USERS` is not set, default users are generated from config defaults.
