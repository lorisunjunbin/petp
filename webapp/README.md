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

### Config via Environment Variables

- `PORT` (default: `5555`)
- `SHARED_FOLDER` (default: `shared`)
- `WEBAPP_USERS` format: `user1:pass1,user2:pass2`
