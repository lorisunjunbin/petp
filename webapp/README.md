## PETP WEB

Lightweight Flask web app with Basic Auth and a file viewer for searching/downloading files shared by PETP.

### Local Run

```bash
pip install -r requirements.txt
python app.py
```

Open:
- Home: http://localhost:5555
- File Viewer: http://localhost:5555/fileviewer?q=xlsx
- Default login: `petp` / `petp`

### Docker (Standalone Image)

- Base image: `python:3.14-slim`
- During build, a Python script copies required overview images from `build_assets/` to `static/images/`:
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
  petp-webapp:latest
```

Run with host shared folder mounted:

```bash
docker run --rm -p 5555:5555 \
  -e PORT=5555 \
  -e SHARED_FOLDER=shared \
  -e WEBAPP_USERS='petp:petp' \
  -v "$(pwd)/shared:/app/shared" \
  petp-webapp:latest
```

### Build for Nas (linux x64 / amd64)

On Apple Silicon or any non-x64 host, explicitly build `linux/amd64`; otherwise, the exported image may be rejected by Nas due to architecture mismatch.

1) Build an amd64 image from the `webapp/` directory:

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

3) Export image tar:

```bash
docker save -o petp-webapp_amd64.tar petp-webapp:amd64
```

4) Upload `petp-webapp_amd64.tar` to Nas, then import it on NAS:

```bash
docker load -i petp-webapp_amd64.tar
```

5) Run on Nas (example):

```bash
docker run -d --name petp-webapp \
  -p 5555:5555 \
  -e PORT=5555 \
  -e SHARED_FOLDER=shared \
  -e WEBAPP_USERS='petp:petp,petp-admin:petp-admin' \
  petp-webapp:amd64
```

6) If you need to mount a NAS shared folder (example path):

```bash
docker run -d --name petp-webapp \
  -p 5555:5555 \
  -e PORT=5555 \
  -e SHARED_FOLDER=shared \
  -e WEBAPP_USERS='petp:petp' \
  -v /volume1/docker/petp/shared:/app/shared \
  petp-webapp:amd64
```

### Config via Environment Variables

- `PORT` (default: `5555`)
- `SHARED_FOLDER` (default: `shared`)
- `WEBAPP_USERS` format: `user1:pass1,user2:pass2`
