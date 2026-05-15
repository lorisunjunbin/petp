# Running Modes & Scripts

Full reference for Desktop, Background, and Docker modes including helper scripts and environment variables.

---

## Modes Overview

| Mode | Entry Point | GUI | Selenium | Use Case |
|------|------------|-----|----------|----------|
| Desktop | `python PETP.py` | Yes | Yes | Local development, interactive RPA |
| Background | `python PETP_backgroud.py` | No | Yes (`--headless` optional) | CLI, scheduled tasks |
| Docker | `PETP_backgroud.py` in container | No | Headless (auto) | Server deployment, CI/CD |

---

## Background Mode

```bash
# Start as persistent HTTP / MCP service (port 8866)
python PETP_background.py

# Run one execution then exit (no HTTP server)
python PETP_background.py --run-execution ENDECODER --no-http

# Run one pipeline then exit
python PETP_background.py --run-pipeline OOTB_TEST_PIPLINE_BG --no-http

# Pass initial data (JSON) into the execution
python PETP_background.py --run-execution MY_EXEC --init-data '{"key":"value"}' --no-http

# Run Selenium tasks in headless mode (no visible browser window)
python PETP_background.py --run-execution MY_SELENIUM_EXEC --headless --no-http

# Override UI policy and log level
python PETP_background.py --ui-policy abort --log-level DEBUG

# Custom HTTP port and auth token
python PETP_background.py --http-port 9090 --http-token my_secret_token

# Combine: headless + custom port + execution on startup
python PETP_background.py --headless --http-port 9090 --run-execution STARTUP_TASK
```

### Process Management

```bash
# Start detached from terminal (survives terminal close)
nohup python PETP_background.py > petp_bg.log 2>&1 &

# Start detached with headless Selenium
nohup python PETP_background.py --headless > petp_bg.log 2>&1 &

# Stop the running background instance (reads PID file, sends SIGTERM)
python PETP_background.py --stop
```

---

## macOS Helper Scripts

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

Defaults (set only when not already defined):
- `PYTHONMALLOC=malloc`
- `PYTHONUNBUFFERED=1`
- `PYTHONDONTWRITEBYTECODE=1`

Optional overrides:

```bash
PYTHON_BIN=python3.14 PETP_ECHO_ENV=1 ./scripts/macos/start_petp.sh gui
PYTHONMALLOC=malloc ./scripts/macos/start_petp.sh background --run-pipeline OOTB_TEST_PIPLINE_BG --no-http
```

---

## Windows Helper Scripts

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

Defaults (set only when not already defined):
- `PYTHONUNBUFFERED=1`
- `PYTHONDONTWRITEBYTECODE=1`

Optional overrides:

```powershell
$env:PYTHON_BIN = '.\.venv\Scripts\python.exe'
$env:PETP_ECHO_ENV = '1'
.\scripts\windows\start_petp.ps1 gui
```

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `PYTHON_BIN` | `python` | Python executable path |
| `PYTHONUNBUFFERED` | `1` | Real-time log output |
| `PYTHONDONTWRITEBYTECODE` | `1` | Suppress `.pyc` generation |
| `PETP_ECHO_ENV` | _(unset)_ | Set to `1` to print runtime settings |
| `PETP_HEADLESS` | _(unset)_ | Set to `true` to force headless Selenium (same as `--headless`) |
| `PETP_BG_LOG` | `petp_bg.log` | Log file path for detached (`bgd`) mode |

---

## Docker

Fully supports **building on Apple M1 (arm64)** and **running on x86 (amd64)**.

```bash
# Build & run locally
./build/docker_build.sh
docker run --rm -p 8866:8866 petp-background:amd64-local

# Push to registry
./build/docker_build.sh --push yourrepo/petp-background:1.0

# Docker with execution on startup
docker run --rm petp-background:amd64-local python PETP_background.py --run-execution MY_EXEC --no-http

# Docker with custom port and initial data
docker run --rm -p 9090:9090 petp-background:amd64-local \
  python PETP_background.py --http-port 9090 --run-execution MY_EXEC --init-data '{"env":"prod"}'
```

Docker auto-enables headless mode (`PETP_HEADLESS=true` in Dockerfile).

| File | Purpose |
|------|---------|
| `Dockerfile` | Multi-arch image (Python 3.14-slim) |
| `build/docker_build.sh` | One-command build (buildx + QEMU) |
| `requirements-docker.txt` | Headless dependencies |

### Running the Test Suite

```bash
# pytest unit & integration tests
python -m pytest testcoverage/ -v

# Legacy test scripts
python testcoverage/test_bg_runtime.py   # 17 BG-mode cases
python testcoverage/nogui_smoke.py       # single-execution smoke test
```
