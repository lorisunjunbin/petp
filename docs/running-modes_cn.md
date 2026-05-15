# 运行模式与脚本

桌面、后台和 Docker 模式的完整参考，包括启动脚本和环境变量。

---

## 模式概览

| 模式 | 入口 | GUI | Selenium | 适用场景 |
|------|------|-----|----------|----------|
| 桌面 | `python PETP.py` | 是 | 是 | 本地开发、交互式 RPA |
| 后台 | `python PETP_backgroud.py` | 否 | 是（可 `--headless`） | CLI、定时任务 |
| Docker | 容器内 `PETP_backgroud.py` | 否 | 无头（自动） | 服务器部署、CI/CD |

---

## 后台模式

```bash
# 启动为持久 HTTP/MCP 服务（端口 8866）
python PETP_background.py

# 运行单个 Execution 后退出（不启动 HTTP 服务）
python PETP_background.py --run-execution ENDECODER --no-http

# 运行单个 Pipeline 后退出
python PETP_background.py --run-pipeline OOTB_TEST_PIPLINE_BG --no-http

# 传入初始数据（JSON）
python PETP_background.py --run-execution MY_EXEC --init-data '{"key":"value"}' --no-http

# Selenium 无头模式运行（不显示浏览器窗口）
python PETP_background.py --run-execution MY_SELENIUM_EXEC --headless --no-http

# 覆盖 UI 策略和日志级别
python PETP_background.py --ui-policy abort --log-level DEBUG

# 自定义 HTTP 端口和认证令牌
python PETP_background.py --http-port 9090 --http-token my_secret_token

# 组合：无头 + 自定义端口 + 启动时运行
python PETP_background.py --headless --http-port 9090 --run-execution STARTUP_TASK
```

### 进程管理

```bash
# 后台运行（终端关闭后继续）
nohup python PETP_background.py > petp_bg.log 2>&1 &

# 后台运行 + 无头 Selenium
nohup python PETP_background.py --headless > petp_bg.log 2>&1 &

# 停止运行中的后台实例（读取 PID 文件，发送 SIGTERM）
python PETP_background.py --stop
```

---

## macOS 启动脚本

```bash
chmod +x scripts/macos/start_petp.sh scripts/macos/start_petp_gui.sh scripts/macos/start_petp_background.sh

# ─── 统一启动器（推荐） ──────────────────────────────────────────────────────

# GUI 模式
./scripts/macos/start_petp.sh gui

# 后台模式（附加到终端）
./scripts/macos/start_petp.sh bg
./scripts/macos/start_petp.sh bg --run-execution ENDECODER --no-http
./scripts/macos/start_petp.sh bg --run-pipeline MY_PIPELINE --no-http
./scripts/macos/start_petp.sh bg --run-execution MY_EXEC --headless --no-http
./scripts/macos/start_petp.sh bg --headless --http-port 9090

# 后台守护模式（nohup，终端关闭后继续）
./scripts/macos/start_petp.sh bgd
./scripts/macos/start_petp.sh bgd --headless
./scripts/macos/start_petp.sh bgd --headless --http-port 9090

# 停止运行中的后台实例
./scripts/macos/start_petp.sh stop

# 查看帮助
./scripts/macos/start_petp.sh help

# ─── 旧版包装器（仍然支持） ──────────────────────────────────────────────────

./scripts/macos/start_petp_gui.sh
./scripts/macos/start_petp_background.sh --run-execution ENDECODER --no-http
```

默认值（仅在未设置时生效）：
- `PYTHONMALLOC=malloc`
- `PYTHONUNBUFFERED=1`
- `PYTHONDONTWRITEBYTECODE=1`

自定义覆盖：

```bash
PYTHON_BIN=python3.14 PETP_ECHO_ENV=1 ./scripts/macos/start_petp.sh gui
PYTHONMALLOC=malloc ./scripts/macos/start_petp.sh background --run-pipeline OOTB_TEST_PIPLINE_BG --no-http
```

---

## Windows 启动脚本

> **首次设置** — 允许 PowerShell 脚本运行（每台机器一次）：
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
> ```

```powershell
# ─── 统一启动器（推荐） ──────────────────────────────────────────────────────

# GUI 模式
.\scripts\windows\start_petp.ps1 gui

# 后台模式（附加到终端）
.\scripts\windows\start_petp.ps1 bg
.\scripts\windows\start_petp.ps1 bg --run-execution ENDECODER --no-http
.\scripts\windows\start_petp.ps1 bg --run-pipeline MY_PIPELINE --no-http
.\scripts\windows\start_petp.ps1 bg --run-execution MY_EXEC --headless --no-http
.\scripts\windows\start_petp.ps1 bg --headless --http-port 9090

# 后台守护模式（隐藏窗口，终端关闭后继续）
.\scripts\windows\start_petp.ps1 bgd
.\scripts\windows\start_petp.ps1 bgd --headless
.\scripts\windows\start_petp.ps1 bgd --headless --http-port 9090

# 停止运行中的后台实例
.\scripts\windows\start_petp.ps1 stop

# 查看帮助
.\scripts\windows\start_petp.ps1 help

# ─── 专用包装器 ──────────────────────────────────────────────────────────────

.\scripts\windows\start_petp_gui.ps1
.\scripts\windows\start_petp_background.ps1 --run-execution ENDECODER --no-http
```

默认值（仅在未设置时生效）：
- `PYTHONUNBUFFERED=1`
- `PYTHONDONTWRITEBYTECODE=1`

自定义覆盖：

```powershell
$env:PYTHON_BIN = '.\.venv\Scripts\python.exe'
$env:PETP_ECHO_ENV = '1'
.\scripts\windows\start_petp.ps1 gui
```

---

## 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `PYTHON_BIN` | `python` | Python 可执行文件路径 |
| `PYTHONUNBUFFERED` | `1` | 实时日志输出 |
| `PYTHONDONTWRITEBYTECODE` | `1` | 禁止生成 `.pyc` |
| `PETP_ECHO_ENV` | _(未设置)_ | 设为 `1` 打印运行时设置 |
| `PETP_HEADLESS` | _(未设置)_ | 设为 `true` 强制无头 Selenium（等同 `--headless`） |
| `PETP_BG_LOG` | `petp_bg.log` | 守护模式（`bgd`）的日志文件路径 |

---

## Docker

完全支持 **Apple M1 (arm64) 构建** 并 **在 x86 (amd64) 运行**。

```bash
# 构建并本地运行
./build/docker_build.sh
docker run --rm -p 8866:8866 petp-background:amd64-local

# 推送到镜像仓库
./build/docker_build.sh --push yourrepo/petp-background:1.0

# 启动时运行 Execution
docker run --rm petp-background:amd64-local python PETP_background.py --run-execution MY_EXEC --no-http

# 自定义端口和初始数据
docker run --rm -p 9090:9090 petp-background:amd64-local \
  python PETP_background.py --http-port 9090 --run-execution MY_EXEC --init-data '{"env":"prod"}'
```

Docker 自动启用无头模式（Dockerfile 中 `PETP_HEADLESS=true`）。

| 文件 | 用途 |
|------|------|
| `Dockerfile` | 多架构镜像（Python 3.14-slim） |
| `build/docker_build.sh` | 一键构建（buildx + QEMU） |
| `requirements-docker.txt` | 无头依赖 |

### 运行测试

```bash
# pytest 单元和集成测试
python -m pytest testcoverage/ -v

# 旧版测试脚本
python testcoverage/test_bg_runtime.py   # 17 个 BG 模式测试用例
python testcoverage/nogui_smoke.py       # 单次执行冒烟测试
```
