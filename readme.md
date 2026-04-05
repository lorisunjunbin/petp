# ![image](./image/petp_small.png) PET-P

This is a techno-person RPA toolkit, a configurable handy task runner/execution engine built by Python, friendly for
DevOps, and automation tests.

**PET** is short for Pipeline-Execution-Task, which represents the execution unit up-down, the pipeline may combine
multiple
executions,
and each one contains various tasks. The last **P** means processor, which handles the specific task one-to-one.

    Pipeline  1:n Execution
    Execution 1:n Task
    Task      1:1 Processor

## What-Can-Do:

    Orchestrate below available task(s) as Execution, dataset-based loop and time-based loop.
    Combine Execution(s) as pipeline, run once, or as cron.

    🌐 Browser Automation (Selenium)
    - Navigate to pages, go back, enter fullscreen, close Chrome
    - Find element(s) then click / key-in / collect data
    - Find multiple elements then click or collect in batch (with optional skip function)
    - Move into iFrame, get cookies, take screenshot
    - Convert Selenium IDE recordings directly to PETP tasks

    🔒 SSH / SFTP (Paramiko)
    - Create SSH / SFTP client sessions
    - Run remote SSH commands
    - Upload (PUT) and download (GET) files via SFTP

    🗂 File & Folder Operations
    - Open, write, delete files; read plain text from file
    - Find files / find latest file in a folder
    - Watch and auto-move files or folders on change
    - ZIP and UNZIP archives
    - Choose file interactively via file-chooser dialog

    📊 Data & Spreadsheet
    - Read records from CSV / Excel
    - Write data to Excel; convert CSV to XLSX
    - Data collect, filter, groupby, mapping, masking (single & multi-field)
    - Data type conversion and nested-to-flat conversion
    - Merge multiple collections into one

    🗃 Database CRUD
    - MySQL, PostgreSQL, SAP HANA, SQLite — all via a unified DB_ACCESS processor

    🤖 AI / LLM Integration
    - DeepSeek: setup + Q&A + MCP-tool calling
    - Google Gemini: setup + Q&A + MCP-tool calling
    - Ollama (local): setup + Q&A + MCP-tool calling
    - Zhipu Z.AI: setup + Q&A + MCP-tool calling

    🔗 MCP (Model Context Protocol)
    - Expose PETP as a standard MCP Tool Server via Streamable-HTTP
    - MCP client processors for DeepSeek / Gemini / Ollama / Zhipu

    🌍 HTTP / Network
    - Send HTTP requests (GET / POST / etc.) with configurable headers, params, body
    - Extract specific keys from HTTP responses
    - Built-in HTTP service (port 8866) — return execution results as HTTP responses
    - OAuth2 / PKCE authorization endpoint for MCP clients

    🔤 String Utilities
    - Encode / decode strings (Base64, URL, etc.)
    - Hash strings (MD5, SHA256, etc.)

    🖱 Mouse & GUI Automation (PyAutoGUI)
    - Mouse click and scroll at absolute or relative positions
    - Query current mouse position

    📬 Messaging & Interaction
    - Send email (SMTP)
    - Show result dialog / input dialog for interactive prompts
    - Advanced input dialog for structured user input

    📈 Data Visualization
    - Render charts and plots via Matplotlib

    🎬 Media & Download
    - Download YouTube videos (PyTube)

    ⚙ Execution Control & Utilities
    - Initialize or check parameters (CHECK_PARAM / INITIAL_PARAMS)
    - Run a nested Execution from within another Execution
    - Stop execution conditionally (STOPPER)
    - Wait for a condition or wait N seconds
    - Reload log configuration at runtime
    - Read JSON data from file or data-chain
    - Run any OS-level shell/CMD command
    - Data Visualization: Matplotlib

MacOS

![image](https://raw.githubusercontent.com/lorisunjunbin/petp/master/image/PETP_overview.png)

Windows

![image](https://raw.githubusercontent.com/lorisunjunbin/petp/master/image/PETP_overview_windows.png)

HTTP Enabled

![image](https://raw.githubusercontent.com/lorisunjunbin/petp/master/image/HTTP_SERVICE_ENABLED.png)

## Run first Execution within 4 steps:

![image](https://raw.githubusercontent.com/lorisunjunbin/petp/master/image/user_manual.png)

## LLM MCP Server, Client & host:

![image](https://raw.githubusercontent.com/lorisunjunbin/petp/master/image/DEEPSEEK-MCP.png)

## MCP Tool Server , Streamable-HTTP

![image](https://raw.githubusercontent.com/lorisunjunbin/petp/master/image/petp_as_standard_mcp_server.png)

## Install & Run

### Prerequisites

| Requirement | Version | Notes |
|-------------|---------|-------|
| Python | 3.13 / 3.14 | [Download](https://www.python.org/downloads/) |
| wxPython | 4.2.x / 4.3.x | Must match your Python version — see step 2 |
| ChromeDriver | 134+ | Only needed for Selenium browser tasks |

---

### Step 1 — Install Python

Download and install Python 3.13 or 3.14 from [python.org](https://www.python.org/downloads/).

> ✅ Make sure to check **"Add Python to PATH"** during installation on Windows.

---

### Step 2 — Install wxPython

wxPython must match your exact Python version and OS. Download the correct `.whl` from
[wxpython.org/Phoenix/snapshot-builds](https://wxpython.org/Phoenix/snapshot-builds/), then install it:

**macOS (Apple Silicon, Python 3.14)**
```bash
pip3.14 install --force-reinstall wxpython-4.3.0a16047+70fc073f-cp314-cp314-macosx_11_0_arm64.whl
```

**Windows (Python 3.14)**
```bash
pip install --force-reinstall wxpython-4.3.0a16047+70fc073f-cp314-cp314-win_amd64.whl
```

**Windows (Python 3.13)**
```bash
pip3.13 install --force-reinstall wxpython-4.2.4a15955+4320e9da-cp313-cp313-win_amd64.whl
```

> 💡 Always download the **latest snapshot** from [wxpython snapshots](https://wxpython.org/Phoenix/snapshot-builds/) for the best compatibility.

---

### Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

> ⚠️ If you encounter a missing package error, install it manually:
> ```bash
> pip install <package-name>
> ```

---

### Step 4 — Run PETP

```bash
python PETP.py
```

The GUI window will launch. On first run, PETP creates a default config under `./config/petpconfig.yaml`.

### Step 4B — Run PETP in Background (No UI)

Use the new no-GUI entrypoint:

```bash
python PETP_backgroud.py
```

Run one execution and exit:

```bash
python PETP_backgroud.py --run-execution ENDECODER --no-http
```

Important no-GUI config in `./config/petpconfig.yaml`:

- `nogui_enabled: true`
- `nogui_ui_processor_policy: skip`

`nogui_ui_processor_policy` supports:

- `skip`: skip GUI processors and continue
- `abort`: stop execution when a GUI processor is encountered

Current GUI processor types in no-GUI mode:

- `SHOW_RESULT`
- `INPUT_DIALOG`
- `MATPLOTLIB`

---

### Step 5 — (Optional) Enable HTTP Service

PETP includes a built-in HTTP server on port **8866** for remote execution triggering and MCP tool access.

Once started from the UI, you can access:

| Endpoint | Description |
|----------|-------------|
| `http://localhost:8866/` | PETP HTTP service home |
| `http://localhost:8866/mcp` | MCP Tool Server (Streamable HTTP) |

For MCP Inspector, use Transport Type: **Streamable HTTP** and URL: `http://localhost:8866/mcp`

---

### Step 6 — (Optional) Build Standalone Executable

Build a native executable for **macOS or Windows** (output goes to `./dist/`):

```bash
python PETP_build.py
```

> 🍎 On macOS this produces `PETP.app`; on Windows it produces `PETP.exe`.

### Step 6B — (Optional) Run in Docker (No-GUI)

Build image:

```bash
docker build -t petp-nogui .
```

Run container:

```bash
docker run --rm -p 8866:8866 petp-nogui
```

---

### Step 7 — (Optional) Update All Dependencies

Keep all installed packages up to date on macOS/Linux:

```bash
pip list --outdated | grep -v '^\-e' | cut -d = -f 1 | xargs -n1 pip install -U
```

---

### Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError: No module named 'xxx'` | Run `pip install xxx` |
| wxPython import error | Ensure the `.whl` matches your exact Python version and OS arch |
| ChromeDriver version mismatch | Download the matching driver from [Chrome for Testing](https://googlechromelabs.github.io/chrome-for-testing/) |
| Port 8866 already in use | Change the port in `./config/petpconfig.yaml` |

## TO-DO:

- Able to easily create customized processors.

## DONE

---

### 🗓 2026

| Date | What's New |
|------|------------|
| 2026-04 | ✨ Support NO_GUI mode, [`PETP_backgroud.py`](./PETP_backgroud.py), easy to run in [`Docker`](./Dockerfile).
| 2026-04 | 🖱 New handy toolbar buttons: append `date_str`, append `os.sep`; added **Skip Task** checkbox on execution run |
| 2026-03 | 📦 Two new OOTB Executions: `OOTB_DOWNLOAD_LATEST_WXPYTHON_mac_arm` & `OOTB_DOWNLOAD_LATEST_WXPYTHON_win_amd64` |
| 2026-03 | 🖱 Enhanced [`FIND_MULTI_XXXProcessor`](./core/processors/FIND_MULTI_THEN_CLICKProcessor.py) with **skip function** support for flexible element handling |
| 2026-03 | ⏱ Added **page load timeout** support in Selenium utility |
| 2026-02 | 🔗 Support standard **MCP Tool Server** (Streamable-HTTP) — see [mcp_client_4_petp](./httpservice/mcp_client_4_petp.py) or MCP Inspector: `http://localhost:8866/mcp` |
| 2026-01 | 🤖 New OOTB Executions: `OOTB_AI_LLM_ZHIPU`, `OOTB_AI_LLM_ZHIPU_MCP` |
| 2026-01 | 🧠 Added **Zhipu Z.AI** support: [SETUP](./core/processors/AI_LLM_ZHIPU_SETUPProcessor.py) · [Q&A](./core/processors/AI_LLM_ZHIPU_QANDAProcessor.py) · [MCP](./core/processors/AI_LLM_ZHIPU_QANDA_MCPProcessor.py) |

---

### 🗓 2025

| Date | What's New |
|------|------------|
| 2025-10 | 🛑 New processors: [STOPPERProcessor](./core/processors/STOPPERProcessor.py) · [RELOAD_LOGProcessor](./core/processors/RELOAD_LOGProcessor.py) |
| 2025-10 | ⬆️ Upgraded to **Python 3.14** and **wxPython 4.2.4a15981** |
| 2025-06 | 🤖 New OOTB Execution: `OOTB_AI_LLM_GEMINI_MCP` — [AI_LLM_GEMINI_QANDA_MCPProcessor](./core/processors/AI_LLM_GEMINI_QANDA_MCPProcessor.py) |
| 2025-05 | 🌐 Switched to `ThreadingHTTPServer`; added **AdvancedInputDialog** |
| 2025-05 | 🤖 New OOTB Execution: `OOTB_AI_LLM_OLLAMA_MCP` — [AI_LLM_OLLAMA_QANDA_MCPProcessor](./core/processors/AI_LLM_OLLAMA_QANDA_MCPProcessor.py) |
| 2025-05 | 🤖 New OOTB Execution: `OOTB_AI_LLM_DEEPSEEK_MCP` — dual PETP instances as MCP server + client |
| 2025-05 | 🌍 Enabled **HTTP Service** for PETP — execution results exposed as HTTP responses (port 8866) |
| 2025-04 | 🔍 Added execution **search** and improved dropdown handling |
| 2025-03 | 🚗 Upgraded **ChromeDriver** to v134 |
| 2025-03 | 📦 New wxPython snapshot for Python 3.13 / Windows: [wxPython-4.2.3a1.dev5840](https://wxpython.org/Phoenix/snapshot-builds/wxPython-4.2.3a1.dev5840+45f9e89f-cp313-cp313-win_amd64.whl) |
| 2025-01 | 🧠 Initial **AI LLM** support: DeepSeek · Gemini · Ollama (local) |

---

### 🗓 2024

| Date | What's New |
|------|------------|
| 2024-10 | ⬆️ Upgraded to **Python 3.13** and ChromeDriver 130; fixed PyInstaller build issues |
| 2024-08 | 📊 New: [MATPLOTLIBProcessor](./core/processors/MATPLOTLIBProcessor.py) — data visualization with Matplotlib |
| 2024-08 | 🤖 New: [AI_LLM_OLLAMA_QANDAProcessor](./core/processors/AI_LLM_OLLAMA_QANDAProcessor.py) |
| 2024-08 | 🔁 New: [RUN_EXECUTIONProcessor](./core/processors/RUN_EXECUTIONProcessor.py) — nest and invoke executions |
| 2024-07 | 🔒 New: [DATA_MULTI_MASKINGProcessor](./core/processors/DATA_MULTI_MASKINGProcessor.py) |
| 2024-07 | 🧠 AI-LLM Gemini: [SETUP](./core/processors/AI_LLM_GEMINI_SETUPProcessor.py) · [Q&A](./core/processors/AI_LLM_GEMINI_QANDAProcessor.py) |
| 2024-07 | ⏭ Task skipping via `{"skipped":"yes"}`; upgraded ChromeDriver to v126; widened execution chooser |
| 2024-06 | 🗃 New: [DATA_GROUPBYProcessor](./core/processors/DATA_GROUPBYProcessor.py) · [DATA_MASKINGProcessor](./core/processors/DATA_MASKINGProcessor.py) |
| 2024-05 | 🌐 Introduced **HttpServer** (Python 3.12) — GET/POST support, JSON responses (port 8866) |
| 2024-04 | 📂 On-demand loading of processors from `./core/processors` folder after PyInstaller build |
| 2024-03 | 🏗 Build PETP executable for **macOS & Windows** via [PETP_build.py](./PETP_build.py) |
| 2024-02 | 🖥 Introduced [PETP File Viewer](./webapp/README.md) web app (Flask, basic auth) |
| 2024-01 | 🚀 New feature: **execute on startup** |

---

### 🗓 2023

| Date | What's New |
|------|------------|
| 2023-12 | ➕ New processors: `DATA_COLLECTProcessor` · `DATA_MAPPINGProcessor` · `FIND_MULTI_THEN_CLICKProcessor` · `FOLDER_WATCH_MOVEProcessor` |
| 2023-11 | 🎚 On-demand **log level** change at runtime |
| 2023-11 | 🔤 New: [ENCODE_DECODE_STRProcessor](./core/processors/ENCODE_DECODE_STRProcessor.py) · [HASH_STRProcessor](./core/processors/HASH_STRProcessor.py); OOTB execution: `ootb_encode_decode_hash_str` |
| 2023-11 | 📋 Optimized logging: configurable log level + rotating file handler |
| 2023-11 | 🔀 New: [DATA_FILTERProcessor](./core/processors/DATA_FILTERProcessor.py) · [COLLECTION_MERGEProcessor](./core/processors/COLLECTION_MERGEProcessor.py) |
| 2023-10 | ⬆️ Upgraded to **Python 3.12** |
| 2023-09 | 🗃 `DB_ACCESSProcessor` now supports: MySQL · PostgreSQL · SAP HANA · SQLite |
| 2023-04 | 🎬 New: `PYTUBEProcessor` — download YouTube videos |

---

### 🗓 2022

| Date | What's New |
|------|------------|
| 2022-11 | 🎨 Simplified & optimized entire [UI](./mvp/view) |
| 2022-11 | 🧹 Clean & restructured UI event bindings |
| 2022-10 | ⚡ Non-blocking execution in [GUI](./mvp) |
| 2022-09 | 💾 **Last run** feature — restore previous execution state on startup |
| 2022-09 | 🖱 New: `MOUSE_CLICKProcessor` · `MOUSE_SCROLLProcessor`; OOTB: `ootb_keep_screen_unlocked` |
| 2022-07 | 🗃 `DB_ACCESSProcessor` — initial MySQL support |
| 2022-07 | ⬆️ Upgraded to **Selenium 4.3.0** |
| 2022-06 | ⬆️ Upgraded to **Python 3.10** and **wxPython 4.1.2** |
| 2022-05 | 🍎 Fixed wxPython install issue on **Mac M1**; built wheel locally |
| 2022-04 | 🗜 New: `ZIPProcessor` — verified on Windows |
| 2022-03 | 🔁 New loop mode: **Loop for N times** |

---

### 🗓 2021

| Date | What's New |
|------|------------|
| 2021-10 | 🌐 New: [BEAUTIFUL_SOUPProcessor](./core/processors/BEAUTIFUL_SOUPProcessor.py) — HTML/XML parsing |
| 2021-09 | 📋 Execution grid **copy & paste** via right-click context menu |

## Appreciate for

- [wxpython](https://www.wxpython.org/) & [wxglade](https://wxglade.sourceforge.net/)
- [selenium](https://selenium-python.readthedocs.io/) & [chromedriver](https://googlechromelabs.github.io/chrome-for-testing/)

