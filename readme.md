# ![image](./image/petp_small.png) PET-P

**[中文](./readme_cn.md)** | English

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE.txt)

Python RPA toolkit with 80+ processors orchestrating browser automation, AI/LLM (10 providers), databases, SSH, email, and HTTP tasks. Configurable pipelines with cron scheduling and loops. Runs as wxPython GUI, headless service, or Docker container. Built-in MCP Tool Server (Streamable-HTTP) for AI agent integration.

```
Pipeline  1:n  Execution
Execution 1:n  Task
Task      1:1  Processor
```

**Links:** [Web Intro](https://petp.tail138025.ts.net/?lang=en) | [Web App](./webapp/README.md) | [Changelog](./CHANGELOG.md)

---

## AI Execution Generator

Generate and modify PETP task flows through natural language conversation with LLM.

**Entry Points:**
- Create Execution → "AI Generate" template
- Right-click taskGrid → "AI Assist" (modify existing)
- MCP Editor → "AI" button (auto-generate tool description)

**Highlights:**
- Multi-turn chat — ask questions, generate flows, modify tasks incrementally
- Processor browser — expandable TreeListCtrl with full documentation, search & filter
- Selective context — only checked Processors are sent to LLM (saves tokens)
- Connection caching — first-time validation, then instant reuse across sessions
- 10 LLM providers — minimal config: just set `ai_provider` in petpconfig.yaml

**AI-Powered MCP Tool Publishing:**
- One-click generation of `mcp_desc` JSON for exposing Executions as MCP tools
- Auto-extracts input parameters from INITIAL_PARAMS and output keys from result tasks
- Generates AI-agent-friendly descriptions that help LLMs understand when to call the tool
- Smart merge — new fields are added without overwriting existing configuration
- Progress dialog with live status and preview before applying

**Configuration** (only `ai_provider` required, rest auto-fills from provider defaults):

```yaml
application:
  ai_provider: zhipu       # or: deepseek, anthropic, gemini, ollama, etc.
  ai_model: ""             # empty = provider default (e.g. GLM-5)
  ai_api_key: ""           # empty = read from default env var (e.g. ZHIPU_ACCESS_KEY)
  ai_base_url: ""          # empty = provider default URL
```

See [Configuration Docs](./docs/configuration.md#ai-assistant-configuration) for full provider list and details.

---

## Quick Start

### 1. Install Python 3.14

Download from [python.org](https://www.python.org/downloads/). On Windows, check "Add Python to PATH".

### 2. Install wxPython (GUI only)

<details>
<summary>Python 3.14 requires a development snapshot (click to expand)</summary>

The stable release (4.2.x on PyPI) does **not** support Python 3.14. Download a 4.3.0-alpha `.whl` from [wxpython.org/Phoenix/snapshot-builds](https://wxpython.org/Phoenix/snapshot-builds/) matching your platform:

```bash
# macOS Apple Silicon
uv pip install wxPython-4.3.0a1XXXX-cp314-cp314-macosx_11_0_arm64.whl

# Windows 64-bit
uv pip install wxPython-4.3.0a1XXXX-cp314-cp314-win_amd64.whl
```

Or auto-download via PETP (no wxPython needed):
```bash
python PETP_backgroud.py --run-execution OOTB_DOWNLOAD_LATEST_WXPYTHON_mac_arm
```

</details>

For Python 3.12/3.13: `pip install wxPython`

### 3. Install Dependencies

```bash
pip install -U uv
uv pip install -r requirements.txt        # Full (GUI)
# or: uv pip install -r requirements-nogui.txt   # Headless
# or: uv pip install -r requirements-docker.txt  # Docker
```

<details>
<summary>Custom install — pick only what you need</summary>

```bash
uv pip install -r requirements/core.txt -r requirements/ssh-sftp.txt -r requirements/http-client.txt
```

See `requirements/` directory for all available groups: `ai-deepseek.txt`, `ai-gemini.txt`, `ai-ollama.txt`, `database.txt`, `excel-data.txt`, `mcp.txt`, `ocr.txt`, `web-automation.txt`, etc.

</details>

### 4. Run

```bash
python PETP.py          # GUI
python PETP_backgroud.py   # Headless service (port 8866)
```

---

## Screenshots

### macOS

![PETP Overview macOS](https://raw.githubusercontent.com/lorisunjunbin/petp/master/image/PETP_overview.png)

### Windows

![PETP Overview Windows](https://raw.githubusercontent.com/lorisunjunbin/petp/master/image/PETP_overview_windows.png)


**MCP Tool Server — integrate with Claude Code, Cursor, and other AI agents:**

![image](https://raw.githubusercontent.com/lorisunjunbin/petp/master/image/petp_as_standard_mcp_server.png)

---

## Features

| Category | Capabilities |
|----------|-------------|
| **Browser Automation** (Selenium) | Navigate, click, key-in, collect, batch find, iFrame, cookies, screenshot. Chrome DevTools Recorder import. |
| **SSH / SFTP** (Paramiko) | SSH/SFTP sessions, remote commands, file upload/download. |
| **File & Folder** | Open, write, delete, read, find, watch & auto-move, ZIP/UNZIP. |
| **Data & Spreadsheet** | CSV/Excel read & write, collect, filter, group-by, mapping, masking, merge. |
| **Database** | MySQL, PostgreSQL, SAP HANA, SQLite — unified `DB_ACCESS` processor. |
| **AI / LLM** (10 providers) | DeepSeek, Gemini, Ollama, Zhipu, Anthropic, Qianfan, MiniMax, Doubao, Moonshot, OpenAI-compatible. Setup + Q&A + MCP tool calling. |
| **AI Execution Generator** | Natural language → task flow generation. Multi-turn chat, Processor browser, selective context, connection caching. |
| **MCP** | Standard MCP Tool Server (Streamable-HTTP). MCP client for all LLM providers. |
| **HTTP / Network** | Configurable requests, response extraction, OAuth2/PKCE, Basic Auth, XSRF. |
| **Email** | SMTP send (CC/BCC, HTML, attachments). IMAP receive (filter, attachment download). |
| **OCR & Captcha** | Image text extraction (paddleocr/rapidocr/easyocr). Captcha solving (ddddocr). |
| **Mouse & GUI** (PyAutoGUI) | Click, scroll, position query. |
| **Execution Control** | Init params, nested execution, conditional stop/jump, `IF_ELSE` branching, loops, shell commands. |
| **Theme** | 9 themes (System auto + 8 named) with live switching. |

---

## Running Modes

| Mode | Command | GUI | Use Case |
|------|---------|-----|----------|
| Desktop | `python PETP.py` | Yes | Interactive development |
| Background | `python PETP_backgroud.py` | No | CLI, HTTP/MCP service |
| Docker | `docker run -p 8866:8866 petp` | No | Server deployment |

```bash
# Run one execution and exit
python PETP_backgroud.py --run-execution ENDECODER --no-http

# Run pipeline on schedule (cron managed in GUI or YAML)
python PETP_backgroud.py --run-pipeline DAILY_REPORT --no-http

# Pass data into execution
python PETP_backgroud.py --run-execution MY_EXEC --init-data '{"key":"value"}' --no-http
```

<details>
<summary>All CLI arguments</summary>

| Argument | Default | Description |
|----------|---------|-------------|
| `--run-execution NAME` | — | Run execution on startup |
| `--run-pipeline NAME` | — | Run pipeline on startup |
| `--init-data JSON` | `{}` | Inject data into `data_chain` |
| `--no-http` | off | Exit after job finishes (no HTTP server) |
| `--headless` | off | Headless Selenium (auto in Docker) |
| `--stop` | — | Stop running background instance |
| `--http-port PORT` | `8866` | HTTP service port |
| `--http-token TOKEN` | from config | Bearer token for auth |
| `--ui-policy {skip,abort}` | `skip` | Handle GUI-only processors |
| `--log-level LEVEL` | from config | Override log level |

</details>

Helper scripts for long-running sessions: see `scripts/macos/start_petp.sh` and `scripts/windows/start_petp.ps1`.

---

## MCP & AI Integration

PETP exposes executions as MCP tools via Streamable-HTTP on port 8866.

**Claude Code / Cursor / any MCP client:**

```json
{
  "mcpServers": {
    "petp": {
      "type": "http",
      "url": "http://localhost:8866/mcp"
    }
  }
}
```

**HTTP API (no MCP client needed):**

```bash
# List tools
curl http://localhost:8866/petp/tools

# Trigger execution
curl -X POST http://localhost:8866/petp/exec \
  -H "Content-Type: application/json" \
  -d '{"action":"execution","params":{"execution":"MY_EXEC"},"wait_for_result":"true"}'
```

| Endpoint | Description |
|----------|-------------|
| `GET /health` | Health check |
| `GET,POST /mcp` | MCP Tool Server (Streamable-HTTP) |
| `GET /petp/tools` | List exposed tools |
| `POST /petp/exec` | Trigger execution or pipeline |
| `GET /petp/result?request_id=<id>` | Poll async result |

---

## Build & Docker

```bash
# Standalone executable
python build/PETP_build.py   # → dist/PETP.app or dist/PETP.exe

# Docker (supports Apple M1 → amd64 cross-build)
./build/docker_build.sh
docker run --rm -p 8866:8866 petp-background:amd64-local
```

---

## Project Structure

| Directory | Description |
|-----------|-------------|
| `core/executions/` | YAML execution definitions |
| `core/processors/` | 80+ processor implementations (one `.py` per task type) |
| `core/pipelines/` | YAML pipeline definitions |
| `core/runtime/` | Background runtime logic |
| `httpservice/` | HTTP server & MCP handler |
| `mvp/` | GUI layer (Model-View-Presenter, wxPython) |
| `config/` | Runtime configuration (`petpconfig.yaml`) |
| `docs/` | Detailed guides ([EN](docs/) / [中文](docs/screenshots_cn.md)) |
| `webapp/` | Flask web app ([docs](./webapp/README.md)) |
| `scripts/` | macOS & Windows launcher scripts |
| `requirements/` | Modular dependency groups |
| `build/` | PyInstaller & Docker build scripts |
| `tools/` | Maintenance scripts (migration, sync) |
| `testcoverage/` | Tests and smoke scripts (incl. `petp_http_endpoints.http` for HTTP/MCP endpoint testing) |

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError` | Install the corresponding `requirements/*.txt` group |
| wxPython import error | Ensure `.whl` matches Python version — see [snapshot builds](https://wxpython.org/Phoenix/snapshot-builds/) |
| ChromeDriver mismatch | Download from [Chrome for Testing](https://googlechromelabs.github.io/chrome-for-testing/) |
| Port 8866 in use | Change `http_port` in `config/petpconfig.yaml` |

---

## Documentation

| Guide | Description |
|-------|-------------|
| [Screenshots & Visual Tour](docs/screenshots.md) | All platform screenshots with context |
| [Running Modes & Scripts](docs/running-modes.md) | Background mode, Docker, helper scripts, env vars |
| [Dependencies](docs/dependencies.md) | Modular groups, custom install, lock files |
| [Configuration Reference](docs/configuration.md) | Config keys, CLI arguments, runtime result format |
| [MCP & HTTP API](docs/mcp-integration.md) | Full API reference, MCP inspector, tool schema |
| [Pipeline & Cron](docs/pipeline-cron.md) | Cron scheduling, YAML format, examples |
| [Parameter Migration](docs/migration.md) | Rename guide for pre-2026-05 users |

---

## Acknowledgements

- [wxPython](https://www.wxpython.org/) & [wxGlade](https://wxglade.sourceforge.net/)
- [Selenium](https://selenium-python.readthedocs.io/) & [ChromeDriver](https://googlechromelabs.github.io/chrome-for-testing/)

---

[Full Changelog →](./CHANGELOG.md)
