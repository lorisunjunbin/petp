# Dependencies

PETP uses a modular dependency structure — split by processor category for flexible installation and minimal packaging.

---

## Install with `uv` (Recommended)

[`uv`](https://docs.astral.sh/uv/) is a fast Python package manager (10-100x faster than pip). Drop-in compatible with existing requirements files.

```bash
pip install -U uv

# Option A (recommended): create and use a virtual environment
uv venv
uv pip install -r requirements.txt

# Option B: install into system Python explicitly
uv pip install --system -r requirements.txt
```

## Install Profiles

```bash
# Full (GUI desktop)
uv pip install -r requirements.txt

# Background service (no GUI)
uv pip install -r requirements-nogui.txt

# Docker (headless, no browser automation)
uv pip install -r requirements-docker.txt

# Custom combination
uv pip install -r requirements/core.txt -r requirements/ssh-sftp.txt -r requirements/http-client.txt
```

---

## Dependency Groups

| File | Category | Packages |
|------|----------|----------|
| `core.txt` | Core framework | pyyaml, cryptocode, croniter, cron-descriptor, python-dateutil |
| `http-client.txt` | HTTP requests | requests, httpx, httpx-sse |
| `web-automation.txt` | Browser automation | selenium, urllib3, Pillow |
| `web-scraping.txt` | Web scraping | beautifulsoup4, lxml |
| `data-processing.txt` | JSON processing | jsonpath-python |
| `excel-data.txt` | Excel & data | openpyxl, pandas |
| `chart.txt` | Visualization | matplotlib |
| `document.txt` | Document processing | python-docx |
| `ssh-sftp.txt` | SSH / SFTP | paramiko |
| `gui-automation.txt` | Desktop automation | pyautogui, pyperclip |
| `gui-wxpython.txt` | Desktop GUI | wxpython |
| `database.txt` | Database | psycopg, mysql-connector-python, hdbcli (enable as needed) |
| `ai-gemini.txt` | Google Gemini AI | google-genai |
| `ai-deepseek.txt` | DeepSeek AI | openai |
| `ai-ollama.txt` | Ollama local LLM | ollama |
| `ai-zhipu.txt` | Zhipu Z.AI | zai |
| `mcp.txt` | MCP Protocol | mcp |
| `ocr.txt` | OCR recognition | rapidocr-onnxruntime, numpy, scipy (paddleocr, easyocr optional) |
| `captcha.txt` | Captcha recognition | ddddocr |
| `javascript.txt` | JS engine | pythonmonkey |
| `video-download.txt` | Video download | pytubefix |
| `http-service.txt` | HTTP server | fastapi, uvicorn |
| `webapp.txt` | Web application | Flask, flask-httpauth, werkzeug, gunicorn |
| `system-build.txt` | System tools | psutil, pyinstaller |

---

## Lock Versions with `uv pip compile`

Generate pinned requirement files for reproducible builds:

```bash
# Compile a specific group
uv pip compile requirements/core.txt -o requirements/core.lock

# Compile the full set
uv pip compile requirements.txt -o requirements.lock
```

---

## Update Dependencies

```bash
# With uv
uv pip install --upgrade -r requirements.txt

# With pip
pip list --outdated | grep -v '^\-e' | cut -d = -f 1 | xargs -n1 pip install -U
```
