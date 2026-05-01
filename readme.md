# ![image](./image/petp_small.png) PET-P

**[中文](./readme_cn.md)** | English

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE.txt)

A techno-person RPA toolkit — configurable task runner, execution engine, and MCP Tool Server built with Python.
Friendly for AI Agents, DevOps, and automation testing.

**Project Sites:** [PETP Intro](https://petp.tail138025.ts.net/?lang=en) | [Web App Guide](./webapp/README.md)

**PET** = **P**ipeline-**E**xecution-**T**ask, the hierarchical execution model. The trailing **P** stands for **Processor**, which handles each task one-to-one.

```
Pipeline  1:n Execution
Execution 1:n Task
Task      1:1 Processor
```

---

## Table of Contents

- [Features](#features)
- [Screenshots](#screenshots)
- [Quick Start](#quick-start)
- [Dependency Management](#dependency-management)
- [Running Modes](#running-modes)
  - [Pipeline Cron Mode](#pipeline-cron-mode)
- [HTTP Service & MCP](#http-service--mcp)
- [Build & Docker](#build--docker)
- [Web App (Docker & UGOS)](#web-app-docker--ugos)
- [Project Structure](#project-structure)
- [Troubleshooting](#troubleshooting)
- [Acknowledgements](#acknowledgements)
- [Changelog](#changelog)

---

## Features

Orchestrate tasks as Executions (with dataset-loop or time-loop), combine Executions as Pipelines, run once or on cron.

| Category | Capabilities |
|----------|-------------|
| **Browser Automation** (Selenium) | Navigate, go back, fullscreen, close Chrome. Find element(s) then click / key-in / collect. Find multiple elements in batch (with skip). iFrame, cookies, screenshot. Convert Chrome DevTools Recorder recordings to PETP tasks. |
| **SSH / SFTP** (Paramiko) | Create SSH / SFTP sessions. Run remote commands. Upload / download files. |
| **File & Folder** | Open, write, delete, read text. Find files / latest file. Watch & auto-move. ZIP / UNZIP. File-chooser dialog. |
| **Data & Spreadsheet** | Read CSV / Excel. Write to Excel. CSV to XLSX. Collect, filter, group-by, mapping, masking, conversion. Merge collections. |
| **Database CRUD** | MySQL, PostgreSQL, SAP HANA, SQLite — unified `DB_ACCESS` processor. |
| **AI / LLM** | DeepSeek, Google Gemini, Ollama (local), Zhipu Z.AI — each with setup + Q&A + MCP-tool calling. |
| **MCP** | Expose PETP as standard MCP Tool Server (Streamable-HTTP). MCP client processors for all LLM providers. |
| **HTTP / Network** | Configurable HTTP requests. Extract response keys. Built-in HTTP service (port 8866). OAuth2 / PKCE. |
| **String Utilities** | Encode / decode (Base64, URL...). Hash (MD5, SHA256...). |
| **Mouse & GUI** (PyAutoGUI) | Click, scroll, query position at absolute or relative coordinates. |
| **Email** | Send email via SMTP with attachments. |
| **Data Visualization** | Charts and plots via Matplotlib. |
| **Media** | Download YouTube videos (PyTube). |
| **Execution Control** | Initialize / check params. Nested execution. Conditional stop. Wait / sleep. Reload log config. Read JSON. Run shell commands. Conditional jump (`GO_TO_TASK`). Declarative if/else branching (`IF_ELSE`). |
| **Theme** | 9 themes including "System" (auto-follows OS dark/light mode); Forest, Ocean, Monokai, Solarized, Nord, Dracula, Sakura, Cyberpunk with live switching; persisted in config. Covers grid selection, property grid, log panel, search highlights, Run button, and MCP toggle. |

---

## Screenshots

**macOS**

![image](https://raw.githubusercontent.com/lorisunjunbin/petp/master/image/PETP_overview.png)

**Windows**

![image](https://raw.githubusercontent.com/lorisunjunbin/petp/master/image/PETP_overview_windows.png)

**HTTP Service Enabled**

![image](https://raw.githubusercontent.com/lorisunjunbin/petp/master/image/HTTP_SERVICE_ENABLED.png)

**Run first Execution within 4 steps:**

![image](https://raw.githubusercontent.com/lorisunjunbin/petp/master/image/user_manual.png)

**LLM MCP Server, Client & Host:**

![image](https://raw.githubusercontent.com/lorisunjunbin/petp/master/image/DEEPSEEK-MCP.png)

**MCP Tool Server (Streamable-HTTP):**

![image](https://raw.githubusercontent.com/lorisunjunbin/petp/master/image/petp_as_standard_mcp_server.png)

**Integrate with Claude Code:**

![image](https://raw.githubusercontent.com/lorisunjunbin/petp/master/image/claude-code-mcp-tool.png)

---

## Quick Start

### Prerequisites

| Requirement | Version | Notes |
|-------------|---------|-------|
| Python | 3.14 | [Download](https://www.python.org/downloads/) |
| wxPython | 4.3.x | Must match your Python version — see Step 2 |
| ChromeDriver | Match Chrome version | Download from [Chrome for Testing](https://googlechromelabs.github.io/chrome-for-testing/), place in `webdriver/<platform>/` |

> ChromeDriver location: `webdriver/darwin/chromedriver` (macOS) or `webdriver/win32/chromedriver.exe` (Windows)

### Step 1 — Install Python

Download and install Python 3.14 from [python.org](https://www.python.org/downloads/).

> On Windows, check **"Add Python to PATH"** during installation.

### Step 2 — Install wxPython

wxPython must match your exact Python version and OS.

- **Python 3.14**: The official stable release (4.2.x on PyPI) does **not** support Python 3.14. You must use a **development snapshot** (4.3.0 alpha) from [wxpython.org/Phoenix/snapshot-builds](https://wxpython.org/Phoenix/snapshot-builds/). Pick the `.whl` matching your Python version and platform:

| Platform | Example |
|----------|---------|
| macOS (Apple Silicon) | `uv pip install wxPython-4.3.0a1XXXX-cp314-cp314-macosx_11_0_arm64.whl` |
| macOS (Intel) | `uv pip install wxPython-4.3.0a1XXXX-cp314-cp314-macosx_10_15_x86_64.whl` |
| Windows (64-bit) | `uv pip install wxPython-4.3.0a1XXXX-cp314-cp314-win_amd64.whl` |
| Linux (x86_64) | `uv pip install wxPython-4.3.0a1XXXX-cp314-cp314-linux_x86_64.whl` |

> Replace `1XXXX` with the actual build number from the snapshot page. Always use the **latest snapshot** for best stability.
>
> **Tip:** PETP includes built-in executions to auto-download the latest wxPython snapshot:
> - `OOTB_DOWNLOAD_LATEST_WXPYTHON_mac_arm` (macOS Apple Silicon)
> - `OOTB_DOWNLOAD_LATEST_WXPYTHON_win_amd64` (Windows 64-bit)
>
> Run via background mode (no wxPython required):
> ```bash
> python PETP_backgroud.py --run-execution OOTB_DOWNLOAD_LATEST_WXPYTHON_mac_arm
> ```
> The `.whl` will be downloaded to `download/`, then install with `uv pip install download/<timestamp>/<file>.whl`.

- **Python 3.12 / 3.13**: You can install the stable release directly from PyPI:

```bash
uv pip install wxPython
# or
pip install wxPython
```

### Step 3 — Install Dependencies

See [Dependency Management](#dependency-management) for full details. Quick install:

```bash
# Recommended: install with uv
pip install -U uv

# If you see: "No virtual environment found"
uv venv
# Creating virtual environment at: .venv
# Activate with: .venv\Scripts\activate

uv pip install -r requirements.txt

# Or install only what you need (see [Dependency Groups](#dependency-groups))
uv pip install -r requirements/core.txt -r requirements/ssh-sftp.txt

# Alternative: install with pip
pip install -r requirements.txt

# Or install only what you need (see [Dependency Groups](#dependency-groups))
pip install -r requirements/core.txt -r requirements/ssh-sftp.txt
```

### Step 4 — Run

```bash
python PETP.py
```

The GUI launches. On first run, a default config is created at `./config/petpconfig.yaml`.

### macOS helper scripts (recommended for long-running sessions)

```bash
chmod +x scripts/macos/start_petp.sh scripts/macos/start_petp_gui.sh scripts/macos/start_petp_background.sh

# ─── Unified launcher (recommended) ─────────────────────────────────────────

# GUI mode
./scripts/macos/start_petp.sh gui

# Background mode (attached to terminal)
./scripts/macos/start_petp.sh bg
./scripts/macos/start_petp.sh bg --run-execution ENDECODER --no-http
./scripts/macos/start_petp.sh bg --run-pipeline MY_PIPELINE --no-http
./scripts/macos/start_petp.sh bg --run-execution MY_EXEC --headless --no-http
./scripts/macos/start_petp.sh bg --headless --http-port 9090

# Background detached mode (nohup, survives terminal close)
./scripts/macos/start_petp.sh bgd
./scripts/macos/start_petp.sh bgd --headless
./scripts/macos/start_petp.sh bgd --headless --http-port 9090

# Stop running background instance
./scripts/macos/start_petp.sh stop

# Show help
./scripts/macos/start_petp.sh help

# ─── Legacy wrappers (still supported) ──────────────────────────────────────

./scripts/macos/start_petp_gui.sh
./scripts/macos/start_petp_background.sh --run-execution ENDECODER --no-http
```

Defaults used by both scripts (only when not already set):
- `PYTHONMALLOC=malloc`
- `PYTHONUNBUFFERED=1`
- `PYTHONDONTWRITEBYTECODE=1`

Optional overrides:

```bash
PYTHON_BIN=python3.14 PETP_ECHO_ENV=1 ./scripts/macos/start_petp.sh gui
PYTHONMALLOC=malloc ./scripts/macos/start_petp.sh background --run-pipeline OOTB_TEST_PIPLINE_BG --no-http
```

### Windows helper scripts (recommended for long-running sessions)

> **First-time setup** — allow PowerShell scripts to run (once per machine):
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
> ```

```powershell
# ─── Unified launcher (recommended) ─────────────────────────────────────────

# GUI mode
.\scripts\windows\start_petp.ps1 gui

# Background mode (attached to terminal)
.\scripts\windows\start_petp.ps1 bg
.\scripts\windows\start_petp.ps1 bg --run-execution ENDECODER --no-http
.\scripts\windows\start_petp.ps1 bg --run-pipeline MY_PIPELINE --no-http
.\scripts\windows\start_petp.ps1 bg --run-execution MY_EXEC --headless --no-http
.\scripts\windows\start_petp.ps1 bg --headless --http-port 9090

# Background detached mode (hidden window, survives terminal close)
.\scripts\windows\start_petp.ps1 bgd
.\scripts\windows\start_petp.ps1 bgd --headless
.\scripts\windows\start_petp.ps1 bgd --headless --http-port 9090

# Stop running background instance
.\scripts\windows\start_petp.ps1 stop

# Show help
.\scripts\windows\start_petp.ps1 help

# ─── Dedicated wrappers ─────────────────────────────────────────────────────

.\scripts\windows\start_petp_gui.ps1
.\scripts\windows\start_petp_background.ps1 --run-execution ENDECODER --no-http
```

Defaults applied automatically (only when not already set):
- `PYTHONUNBUFFERED=1`
- `PYTHONDONTWRITEBYTECODE=1`

Optional overrides (set env vars before calling):

```powershell
$env:PYTHON_BIN = '.\.venv\Scripts\python.exe'
$env:PETP_ECHO_ENV = '1'
.\scripts\windows\start_petp.ps1 gui

# Background mode with custom Python
$env:PYTHON_BIN = 'python3.14'
.\scripts\windows\start_petp.ps1 bg --run-pipeline OOTB_TEST_PIPLINE_BG --no-http
```

| Variable | Default | Description |
|---|---|---|
| `PYTHON_BIN` | `python` | Python executable path |
| `PYTHONUNBUFFERED` | `1` | Real-time log output |
| `PYTHONDONTWRITEBYTECODE` | `1` | Suppress `.pyc` generation |
| `PETP_ECHO_ENV` | _(unset)_ | Set to `1` to print runtime settings |
| `PETP_HEADLESS` | _(unset)_ | Set to `true` to force headless Selenium (same as `--headless`) |
| `PETP_BG_LOG` | `petp_bg.log` | Log file path for detached (`bgd`) mode |

---

## Dependency Management

PETP uses a **modular dependency structure** — split by processor category for flexible installation and minimal packaging.

### Install with `uv` (Recommended)

[`uv`](https://docs.astral.sh/uv/) is a fast Python package manager (10-100x faster than pip). Drop-in compatible with existing requirements files — **zero migration needed**.

```bash

# Option A (recommended): create and use a virtual environment
uv pip install -r requirements.txt

# Option B: install into system Python explicitly
uv pip install --system -r requirements.txt

# Full (GUI desktop)
uv pip install -r requirements.txt

# Background service (no GUI)
uv pip install -r requirements-nogui.txt

# Docker (headless, no browser automation)
uv pip install -r requirements-docker.txt

# Custom combination
uv pip install -r requirements/core.txt -r requirements/ssh-sftp.txt -r requirements/http-client.txt
```

#### Lock versions with `uv pip compile`

Generate pinned requirement files for reproducible builds:

```bash
# Compile a specific group
uv pip compile requirements/core.txt -o requirements/core.lock

# Compile the full set
uv pip compile requirements.txt -o requirements.lock
```

### Dependency Groups

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
| `video-download.txt` | Video download | pytube |
| `http-service.txt` | HTTP server | fastapi, uvicorn |
| `webapp.txt` | Web application | Flask, flask-httpauth, werkzeug, gunicorn |
| `system-build.txt` | System tools | psutil, pyinstaller |

### Update Dependencies

```bash
# With pip
pip list --outdated | grep -v '^\-e' | cut -d = -f 1 | xargs -n1 pip install -U

# With uv
uv pip install --upgrade -r requirements.txt
```

---

## Running Modes

| Mode | Entry Point | GUI | Selenium | Use Case |
|------|------------|-----|----------|----------|
| Desktop | `python PETP.py` | Yes | Yes | Local development, interactive RPA |
| Background | `python PETP_backgroud.py` | No | Yes (`--headless` optional) | CLI, scheduled tasks |
| Docker | `PETP_backgroud.py` in container | No | Headless (auto) | Server deployment, CI/CD |

### Background Mode

```bash
# ─── Basic usage ─────────────────────────────────────────────────────────────

# Start as persistent HTTP / MCP service (port 8866)
python PETP_backgroud.py

# Run one execution then exit (no HTTP server)
python PETP_backgroud.py --run-execution ENDECODER --no-http

# Run one pipeline then exit
python PETP_backgroud.py --run-pipeline OOTB_TEST_PIPLINE_BG --no-http

# Pass initial data (JSON) into the execution
python PETP_backgroud.py --run-execution MY_EXEC --init-data '{"key":"value"}' --no-http

# ─── Selenium (headless) ─────────────────────────────────────────────────────

# Run Selenium tasks in headless mode (no visible browser window)
python PETP_backgroud.py --run-execution MY_SELENIUM_EXEC --headless --no-http

# Headless pipeline
python PETP_backgroud.py --run-pipeline MY_PIPELINE --headless --no-http

# Headless persistent service
python PETP_backgroud.py --headless

# ─── Overrides ───────────────────────────────────────────────────────────────

# Override UI policy and log level
python PETP_backgroud.py --ui-policy abort --log-level DEBUG

# Custom HTTP port and auth token
python PETP_backgroud.py --http-port 9090 --http-token my_secret_token

# Combine: headless + custom port + execution on startup
python PETP_backgroud.py --headless --http-port 9090 --run-execution STARTUP_TASK

# ─── Process management ──────────────────────────────────────────────────────

# Start detached from terminal (survives terminal close)
nohup python PETP_backgroud.py > petp_bg.log 2>&1 &

# Start detached with headless Selenium
nohup python PETP_backgroud.py --headless > petp_bg.log 2>&1 &

# Stop the running background instance (reads PID file, sends SIGTERM)
python PETP_backgroud.py --stop

# ─── Using helper scripts (macOS) ───────────────────────────────────────────

./scripts/macos/start_petp.sh bg --run-execution ENDECODER --no-http
./scripts/macos/start_petp.sh bg --headless --run-pipeline MY_PIPELINE --no-http
./scripts/macos/start_petp.sh bgd                    # detached (nohup)
./scripts/macos/start_petp.sh bgd --headless         # detached + headless
./scripts/macos/start_petp.sh stop                   # stop running instance

# ─── Using helper scripts (Windows) ─────────────────────────────────────────

# .\scripts\windows\start_petp.ps1 bg --run-execution ENDECODER --no-http
# .\scripts\windows\start_petp.ps1 bg --headless --run-pipeline MY_PIPELINE --no-http
# .\scripts\windows\start_petp.ps1 bgd                    # detached (hidden window)
# .\scripts\windows\start_petp.ps1 bgd --headless         # detached + headless
# .\scripts\windows\start_petp.ps1 stop                   # stop running instance

# ─── Docker ──────────────────────────────────────────────────────────────────

# Docker auto-enables headless (PETP_HEADLESS=true in Dockerfile)
docker run --rm -p 8866:8866 petp-background:amd64-local

# Docker with execution on startup
docker run --rm petp-background:amd64-local python PETP_backgroud.py --run-execution MY_EXEC --no-http

# Docker with custom port and initial data
docker run --rm -p 9090:9090 petp-background:amd64-local \
  python PETP_backgroud.py --http-port 9090 --run-execution MY_EXEC --init-data '{"env":"prod"}'
```

### Pipeline Cron Mode

Pipelines can run on a cron schedule. Setup in the GUI:

1. Switch to **Pipelines** tab → select or create a pipeline
2. Check **as cron** → enter a cron expression (e.g. `0 9 * * 1-5`)
3. Click **Execute** — runs on schedule until stopped via **Stop** / **Stop All**

The tooltip on the cron input shows a human-readable description (e.g. "At 09:00 AM, Monday through Friday").

**Example YAML:**

```yaml
!!python/object:core.pipeline.Pipeline
pipeline: DAILY_REPORT
cronEnabled: true
cronExp: 0 9 * * 1-5
cronDesc: At 09:00 AM, Monday through Friday
list:
- execution: fetch_data
  input: ''
- execution: generate_report
  input: ''
- execution: send_email
  input: '{"to":"team@example.com"}'
```

**Running examples:**

```bash
# GUI — cron managed via checkbox + expression input, persisted in YAML

# Background — run a pipeline once (cron fields are saved but not auto-scheduled in BG mode)
python PETP_backgroud.py --run-pipeline DAILY_REPORT --no-http

# Background — run with initial data
python PETP_backgroud.py --run-pipeline DAILY_REPORT --init-data '{"to":"ops@example.com"}' --no-http

# Background — persistent HTTP service (pipelines triggered via POST /petp/exec)
python PETP_backgroud.py

# Docker
docker run --rm -p 8866:8866 petp-background:amd64-local
# then: POST http://localhost:8866/petp/exec  {"pipeline":"DAILY_REPORT","wait_for_result":true}
```

#### CLI Arguments

| Argument | Values | Default | Description |
|----------|--------|---------|-------------|
| `--run-execution NAME` | any execution name | — | Run the named execution immediately on startup |
| `--run-pipeline NAME` | any pipeline name | — | Run the named pipeline immediately on startup |
| `--init-data JSON` | JSON object string | `{}` | Key-value pairs injected into `data_chain` before the run; MCP `default` values fill in any missing keys |
| `--no-http` | flag | off | Skip starting the HTTP/MCP server; process exits after the job finishes |
| `--headless` | flag | off | Run Selenium tasks in headless mode (auto-enabled in Docker) |
| `--stop` | flag | — | Stop a running background instance by reading its PID file and sending SIGTERM |
| `--nogui-enabled {true,false}` | `true` / `false` | `true` | Enable or disable no-GUI background mode |
| `--ui-policy {skip,abort}` | `skip` / `abort` | `skip` | What to do when a GUI-only processor is encountered: `skip` continues silently, `abort` raises an error |
| `--log-level LEVEL` | `DEBUG` / `INFO` / `WARNING` / `ERROR` | from config | Override the log level for this run |
| `--http-port PORT` | integer | `8866` | Override the HTTP service port |
| `--http-token TOKEN` | string | from config | Override the Bearer token for HTTP authentication |

#### `petpconfig.yaml` — Background-relevant keys

| Key | Default | Description |
|-----|---------|-------------|
| `nogui_enabled` | `true` | Must be `true` for background mode to activate |
| `nogui_ui_processor_policy` | `skip` | `skip` silently skips GUI processors; `abort` stops the execution on the first GUI processor |
| `http_port` | `8866` | Port for the built-in HTTP / MCP service |
| `http_request_token` | _(base64 string)_ | Bearer token required for all HTTP API calls |
| `http_request_timeout` | `600` | Seconds before an HTTP request times out |
| `log_level` | `INFO` | Runtime log verbosity |
| `execute_on_startup` | `false` | Name of an execution to run automatically when the service starts |

#### `BackgroundRuntime` result structure

Every `run_execution` / `run_pipeline` call returns:

```json
{
  "ok": true,
  "data": { "<data_key>": "<value>", "..." : "..." },
  "error": null,
  "meta": {
    "duration_ms": 42,
    "skipped_tasks": [{ "task_index": 2, "task_type": "SHOW_RESULT", "reason": "task.skipped" }],
    "aborted_tasks": []
  }
}
```

- `ok` — `true` if the execution completed without an unhandled exception
- `data` — public subset of `data_chain` (excludes `__m`, `__p`, and non-serialisable values such as WebDriver instances); if the execution sets a `response_key`, only that key's value is returned
- `error` — error message string on failure, `null` on success
- `meta.duration_ms` — wall-clock execution time in milliseconds
- `meta.skipped_tasks` — list of tasks that were bypassed (either `task.skipped = true` or filtered by `ui_policy`)

#### Processors skipped in no-GUI mode

Only processors that **require OS-level GUI interaction with no headless alternative** are skipped:

| Processor | Reason |
|-----------|--------|
| `FILE_CHOOSER` | Uses `pyautogui` to interact with OS file chooser dialog; no programmatic alternative |

The following processors use `self.view is not None` guard and **degrade gracefully** in BG mode (log/fallback, not skipped):

| Processor | BG mode behavior |
|-----------|-----------------|
| `SHOW_RESULT` | Logs title + message |
| `INPUT_DIALOG` | Uses `default_value` param, continues execution |
| `MATPLOTLIB` | Logs chart params |

All **Selenium** processors (`GO_TO_PAGE`, `FIND_THEN_CLICK`, etc.) run normally in BG mode. All **Mouse** processors (`MOUSE_CLICK`, `MOUSE_POSITION`, `MOUSE_SCROLL`) run normally via pyautogui.

> Force headless Selenium outside Docker: `--headless` flag or `PETP_HEADLESS=true` env var (auto-enabled in Docker).

#### Running the test suite

```bash
# pytest unit & integration tests (expression2str, data_chain, loop state, processors, runtime)
python -m pytest testcoverage/ -v

# Legacy test scripts
python testcoverage/test_bg_runtime.py   # 17 BG-mode cases covering ENDECODER, DB_ACCESS, pipeline, tools cache, result structure
python testcoverage/nogui_smoke.py       # single-execution smoke test, exits non-zero on failure
```

---

## HTTP Service & MCP

PETP includes a built-in HTTP server on port **8866**.

| Endpoint | Description |
|----------|-------------|
| `GET /` | PETP HTTP service home |
| `GET /mcp` | MCP Tool Server (Streamable-HTTP) |

For MCP Inspector: Transport Type = **Streamable HTTP**, URL = `http://localhost:8866/mcp`

---

## Build & Docker

### Build Standalone Executable

```bash
python build/PETP_build.py
```

Output: `PETP.app` (macOS) or `PETP.exe` (Windows) in `./dist/`.

### Docker

Fully supports **building on Apple M1 (arm64)** and **running on x86 (amd64)**.

| File | Purpose |
|------|---------|
| `Dockerfile` | Multi-arch image (Python 3.14-slim) |
| `build/docker_build.sh` | One-command build (buildx + QEMU) |
| `requirements-docker.txt` | Headless dependencies |

```bash
# Build & run locally
./build/docker_build.sh
docker run --rm -p 8866:8866 petp-background:amd64-local

# Push to registry
./build/docker_build.sh --push yourrepo/petp-background:1.0
```

**Container endpoints:**

| Endpoint | Description |
|----------|-------------|
| `GET /health` | Health check |
| `GET /petp/tools` | List MCP tools |
| `POST /petp/exec` | Trigger execution / pipeline |
| `GET /petp/result?request_id=<id>` | Check async result |
| `POST /mcp` | MCP Tool Server |

## Web App (Docker & UGOS)

The standalone Web App (`webapp/`) has its own Docker packaging guide, including UGOS (`linux/amd64`) build/export/import steps:

- [`webapp/README.md`](./webapp/README.md)
- UGOS quick path: build `linux/amd64` with `buildx`, verify architecture, export tar, then `docker load` on NAS.

---

## Project Structure

### Root Files

| Category | File | Description |
|----------|------|-------------|
| Entry | `PETP.py` | GUI desktop entry |
| | `PETP_backgroud.py` | Headless / background entry |
| Build | `build/PETP_build.py` | PyInstaller build (GUI) |
| | `build/PETP_background_build.py` | PyInstaller build (background) |
| | `build/build_common.py` | Shared build utilities |
| | `build/*.spec` | PyInstaller spec templates |
| | `build/debug_runtime.py` | Debug helper for packaged apps |
| Docker | `Dockerfile` | Multi-arch image |
| | `build/docker_build.sh` | Build script |
| | `.dockerignore` | Exclude list |
| Deps | `requirements.txt` | Full install (references all groups) |
| | `requirements-nogui.txt` | No-GUI / background |
| | `requirements-docker.txt` | Docker / headless |
| | `requirements/*.txt` | Modular dependency groups |

### Directories

| Directory | Description |
|-----------|-------------|
| `build/` | PyInstaller spec templates and debug helper |
| `config/` | Configuration (`petpconfig.yaml`) |
| `core/` | Core engine — execution, pipeline, task, processor, loop, cron |
| `core/executions/` | YAML execution definitions |
| `core/processors/` | Processor implementations (one `.py` per task type) |
| `core/pipelines/` | YAML pipeline definitions |
| `core/runtime/` | Background / no-GUI runtime logic |
| `core/definition/` | YAML reader, Chrome DevTools Recorder converter |
| `httpservice/` | HTTP server, MCP handler, request routing |
| `mvp/` | GUI layer (Model-View-Presenter) |
| `utils/` | Utilities — Selenium, Excel, Date, OS, Logger, Paramiko, decorators |
| `webapp/` | Flask web application (see [`webapp/README.md`](./webapp/README.md) for Docker and UGOS usage) |
| `webdriver/` | Platform ChromeDriver binaries |
| `resources/` | Static resources |
| `download/` | Default download directory |
| `testcoverage/` | Test scripts |
| `log/` | Runtime logs |

---

## Troubleshooting

| Problem | Solution                                                                                   |
|---------|--------------------------------------------------------------------------------------------|
| `ModuleNotFoundError` | `pip install <package>` or install the corresponding requirements group                    |
| wxPython import error | Ensure `.whl` matches your Python version and OS,[Phoenix-snapshot-builds](https://wxpython.org/Phoenix/snapshot-builds/)                                          |
| ChromeDriver mismatch | Download from [Chrome for Testing](https://googlechromelabs.github.io/chrome-for-testing/) |
| Port 8866 in use | Change port in `petpconfig.yaml`                                                           |

---

## Acknowledgements

- [wxPython](https://www.wxpython.org/) & [wxGlade](https://wxglade.sourceforge.net/)
- [Selenium](https://selenium-python.readthedocs.io/) & [ChromeDriver](https://googlechromelabs.github.io/chrome-for-testing/) & [Chrome DevTool Recorder](https://developer.chrome.com/docs/devtools/recorder)

---

## Changelog

### 2026

| Date | What's New                                                                                                                                                                                        |
|------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 2026-05 | UI streamlining: removed DC viewer; moved log-level and clean-log controls into LogSearchBar; new reusable `PopupMenuButton` component for theme/lang/log-level choosers; 5 new themes (Nord, Dracula, Sakura, Cyberpunk + total 9); DEBUG-level `data_chain` JSON dump after each task |
| 2026-05 | New `IF_ELSE` processor: declarative conditional branching — skip "then" or "else" task blocks based on a Python condition evaluated against `data_chain`; works correctly inside loops |
| 2026-05 | Cron execution history dialog (History button in Pipeline tab): browse last 50 runs with status, duration, error details; filter by pipeline name |
| 2026-05 | `INPUT_DIALOG` BG mode: respect existing `data_chain` value instead of overwriting with `default_value`; GUI mode pre-fills dialog with existing value |
| 2026-05 | Task progress display in status bar; LRU execution cache; persistent log file descriptor; fix exit SEGFAULT caused by wx.Timer firing after window destruction |
| 2026-04 | Status bar (`highlightInfo`): displays key execution events — `[START]`, `[DONE]` with duration, `[ERROR]` with message, `[STOP]`; color follows theme accent. `Executor` DONE event now carries error info |
| 2026-04 | "System" auto theme: follows OS dark/light mode (Monokai for dark, Ocean for light); responds to real-time system appearance changes via `wx.EVT_SYS_COLOUR_CHANGED` |
| 2026-04 | Theme system: 4 built-in color themes (Forest, Ocean, Monokai, Solarized) with real-time switching via toolbar dropdown; selection persisted in `petpconfig.yaml`. Covers grid selection, property grid, log panel, search highlights, Run button gradient, and MCP tool toggle accent |
| 2026-04 | Recording converter switched from Selenium IDE (`.side`) to Chrome DevTools Recorder (`.json`); supports navigate, click, doubleClick→collect, change, keyDown/keyUp merge, waitForElement |
| 2026-04 | `GO_TO_TASK` processor: conditional jump to any task within an execution; `loop_condition` attribute for programmatic break/continue based on data state; dynamic function caching in `CodeExplainerUtil` |
| 2026-04 | `OCR` image preprocessing (binarize, denoise, sharpen, upscale, adaptive, auto); `CAPTCHA` processor (ddddocr: ocr/slide/det modes) |
| 2026-04 | Log panel: search & highlight with prev/next navigation (Ctrl+F / Cmd+F); property hint popup via right-click; `FIND_THEN_CLICK` by_condition parameter |
| 2026-04 | Loop Editor: right-click context menu with param hint and complex value editor; `explain_param_or_default` helper across all processors |
| 2026-04 | Unified MCP handling logic between GUI and BG modes via `McpMixin`; fixed `structuredContent` format; `outputSchema` supports `mapKey` field mapping |
| 2026-04 | MCP tool schema supports `default` values for inputs and `mapKey` output field mapping; `McpDescEditor` enhancements |
| 2026-04 | Task grid right-click menu adds "View Processor Usage" and "Find Referencing Executions" options |
| 2026-04 | MCP tool toggle replaced with custom `ToggleSwitch`; added state labels and response-key warning |
| 2026-04 | Execution description editor replaced with structured `McpDescEditor` for visual MCP tool schema editing |
| 2026-04 | `HTTP_REQUEST` processor: built-in Basic Auth, OAuth2, and XSRF/CSRF token support |
| 2026-04 | New `RUN_JAVASCRIPT` processor (PythonMonkey) for executing JS functions |
| 2026-04 | Execution snapshots button; `SearchableComboBox` real-time filter and keyboard navigation with tool/nav icon prefixes |
| 2026-04 | Loop Editor: right-click or ⚙️ button to edit loop attributes via key-value dialog; snapshot & undo/redo support for loop changes. Save button dirty-state fix for skip toggle, paste, add/delete row, and loop edits. |
| 2026-04 | GUI Undo & Redo & snapshot history. enhance handy tools.                                                                                                                                          |
| 2026-04 | internationalization support: Chinese & EN                                                                                                                                                        |
| 2026-04 | Modular dependency management with `requirements/` groups; `uv` support                                                                                                                           |
| 2026-04 | NO_GUI mode, [`PETP_backgroud.py`](./PETP_backgroud.py), [`Docker`](./Dockerfile) support                                                                                                         |
| 2026-04 | Toolbar: append `date_str`, `os.sep`; **Skip Task** checkbox                                                                                                                                      |
| 2026-03 | OOTB: `OOTB_DOWNLOAD_LATEST_WXPYTHON` for macOS & Windows                                                                                                                                         |
| 2026-03 | [`FIND_MULTI_XXXProcessor`](./core/processors/FIND_MULTI_THEN_CLICKProcessor.py) skip function                                                                                                    |
| 2026-03 | Page load timeout in Selenium                                                                                                                                                                     |
| 2026-02 | **MCP Tool Server** (Streamable-HTTP) — [mcp_client_4_petp](./testcoverage/mcp_client_4_petp.py)                                                                                                   |
| 2026-01 | **Zhipu Z.AI**: [SETUP](./core/processors/AI_LLM_ZHIPU_SETUPProcessor.py) / [Q&A](./core/processors/AI_LLM_ZHIPU_QANDAProcessor.py) / [MCP](./core/processors/AI_LLM_ZHIPU_QANDA_MCPProcessor.py) |

### 2025

| Date | What's New |
|------|------------|
| 2025-10 | [STOPPERProcessor](./core/processors/STOPPERProcessor.py) / [RELOAD_LOGProcessor](./core/processors/RELOAD_LOGProcessor.py); Python 3.14 |
| 2025-06 | OOTB: `OOTB_AI_LLM_GEMINI_MCP` |
| 2025-05 | `ThreadingHTTPServer`; **AdvancedInputDialog**; HTTP Service (port 8866) |
| 2025-05 | OOTB: `OOTB_AI_LLM_OLLAMA_MCP` / `OOTB_AI_LLM_DEEPSEEK_MCP` |
| 2025-04 | Execution search, improved dropdowns |
| 2025-03 | ChromeDriver v134 |
| 2025-01 | Initial **AI LLM**: DeepSeek / Gemini / Ollama |

### 2024

| Date | What's New |
|------|------------|
| 2024-10 | Python 3.13, ChromeDriver 130 |
| 2024-08 | [MATPLOTLIBProcessor](./core/processors/MATPLOTLIBProcessor.py), [AI_LLM_OLLAMA_QANDAProcessor](./core/processors/AI_LLM_OLLAMA_QANDAProcessor.py), [RUN_EXECUTIONProcessor](./core/processors/RUN_EXECUTIONProcessor.py) |
| 2024-07 | Gemini AI-LLM; [DATA_MULTI_MASKINGProcessor](./core/processors/DATA_MULTI_MASKINGProcessor.py); task skipping |
| 2024-06 | [DATA_GROUPBYProcessor](./core/processors/DATA_GROUPBYProcessor.py), [DATA_MASKINGProcessor](./core/processors/DATA_MASKINGProcessor.py) |
| 2024-05 | HttpServer (GET/POST, JSON) |
| 2024-04 | On-demand processor loading after PyInstaller build |
| 2024-03 | PyInstaller build for macOS & Windows |
| 2024-02 | [PETP File Viewer](./webapp/README.md) web app (Flask) |
| 2024-01 | Execute on startup |

### 2023

| Date | What's New |
|------|------------|
| 2023-12 | `DATA_COLLECT`, `DATA_MAPPING`, `FIND_MULTI_THEN_CLICK`, `FOLDER_WATCH_MOVE` processors |
| 2023-11 | [ENCODE_DECODE_STRProcessor](./core/processors/ENCODE_DECODE_STRProcessor.py), [HASH_STRProcessor](./core/processors/HASH_STRProcessor.py), [DATA_FILTERProcessor](./core/processors/DATA_FILTERProcessor.py), [COLLECTION_MERGEProcessor](./core/processors/COLLECTION_MERGEProcessor.py); runtime log level; rotating file handler |
| 2023-10 | Python 3.12 |
| 2023-09 | DB_ACCESS: MySQL / PostgreSQL / SAP HANA / SQLite |
| 2023-04 | `PYTUBEProcessor` — YouTube download |

### 2022

| Date | What's New |
|------|------------|
| 2022-11 | UI simplification and event binding cleanup |
| 2022-10 | Non-blocking GUI execution |
| 2022-09 | Last-run restore; `MOUSE_CLICKProcessor`, `MOUSE_SCROLLProcessor` |
| 2022-07 | MySQL support; Selenium 4.3.0 |
| 2022-06 | Python 3.10, wxPython 4.1.2 |
| 2022-05 | Mac M1 wxPython fix |
| 2022-04 | `ZIPProcessor` |
| 2022-03 | Loop N-times mode |

### 2021

| Date | What's New |
|------|------------|
| 2021-10 | [BEAUTIFUL_SOUPProcessor](./core/processors/BEAUTIFUL_SOUPProcessor.py) |
| 2021-09 | Grid copy & paste |

