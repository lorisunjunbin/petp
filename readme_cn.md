# ![image](./image/petp_small.png) PET-P

中文 | **[English](./readme.md)**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE.txt)

一个技术人员的 RPA 工具包 — 可配置的任务运行器、执行引擎、MCP 工具服务器，基于 Python 构建。
适用于 AI Agent、DevOps 和自动化测试。

**项目站点：** [PETP 项目介绍](https://petp.tail138025.ts.net/?lang=zh) | [WebApp 使用说明](./webapp/README.md)

**PET** = **P**ipeline-**E**xecution-**T**ask，层级化执行模型。末尾的 **P** 代表 **Processor**，每个处理器一一对应处理具体任务。

```
Pipeline  1:n Execution
Execution 1:n Task
Task      1:1 Processor
```

---

## 目录

- [功能特性](#功能特性)
- [截图](#截图)
- [快速开始](#快速开始)
- [依赖管理](#依赖管理)
- [运行模式](#运行模式)
  - [Pipeline 定时模式](#pipeline-定时模式)
- [HTTP 服务与 MCP](#http-服务与-mcp)
- [打包与 Docker](#打包与-docker)
- [Web App（Docker & UGOS）](#web-appdocker--ugos)
- [项目结构](#项目结构)
- [常见问题](#常见问题)
- [致谢](#致谢)
- [更新日志](#更新日志)

---

## 功能特性

将任务编排为 Execution（支持数据集循环、时间循环），将多个 Execution 组合为 Pipeline，单次运行或定时执行。

| 分类 | 能力 |
|------|------|
| **浏览器自动化** (Selenium) | 页面导航、后退、全屏、关闭 Chrome。查找元素后点击 / 输入 / 采集。批量查找（支持跳过）。iFrame、Cookie、截图。支持 Chrome DevTools Recorder 录制转换。 |
| **SSH / SFTP** (Paramiko) | 创建 SSH / SFTP 会话。执行远程命令。上传 / 下载文件。 |
| **文件与文件夹** | 打开、写入、删除、读取文本。查找文件 / 最新文件。监控并自动移动。ZIP / UNZIP。文件选择对话框。 |
| **数据与表格** | 读取 CSV / Excel。写入 Excel。CSV 转 XLSX。采集、过滤、分组、映射、脱敏、转换。合并集合。 |
| **数据库 CRUD** | MySQL、PostgreSQL、SAP HANA、SQLite — 统一的 `DB_ACCESS` 处理器。 |
| **AI / LLM** | DeepSeek、Google Gemini、Ollama（本地）、智谱 Z.AI — 各支持初始化 + 问答 + MCP 工具调用。 |
| **MCP** | 将 PETP 作为标准 MCP 工具服务器暴露（Streamable-HTTP）。支持所有 LLM 提供商的 MCP 客户端处理器。 |
| **HTTP / 网络** | 可配置的 HTTP 请求。提取响应字段。内置 HTTP 服务（端口 8866）。OAuth2 / PKCE。 |
| **字符串工具** | 编码 / 解码（Base64、URL...）。哈希（MD5、SHA256...）。 |
| **鼠标与 GUI** (PyAutoGUI) | 在绝对或相对坐标位置点击、滚动、查询鼠标位置。 |
| **邮件** | 通过 SMTP 发送带附件的邮件。 |
| **数据可视化** | 通过 Matplotlib 生成图表。 |
| **媒体** | 下载 YouTube 视频（PyTube）。 |
| **执行控制** | 初始化 / 校验参数。嵌套执行。条件停止。等待 / 延时。运行时重载日志配置。读取 JSON。执行 Shell 命令。条件跳转（`GO_TO_TASK`）。声明式条件分支（`IF_ELSE`）。 |
| **主题** | 9 套主题，含 "System"（自动跟随系统深浅色模式）；Forest、Ocean、Monokai、Solarized、Nord、Dracula、Sakura、Cyberpunk 实时切换并持久化到配置文件。覆盖表格选中、属性编辑器、日志面板、搜索高亮、运行按钮和 MCP 开关。 |

---

## 截图

**macOS**

![image](https://raw.githubusercontent.com/lorisunjunbin/petp/master/image/PETP_overview.png)

**Windows**

![image](https://raw.githubusercontent.com/lorisunjunbin/petp/master/image/PETP_overview_windows.png)

**HTTP 服务已启用**

![image](https://raw.githubusercontent.com/lorisunjunbin/petp/master/image/HTTP_SERVICE_ENABLED.png)

**4 步运行第一个 Execution：**

![image](https://raw.githubusercontent.com/lorisunjunbin/petp/master/image/user_manual.png)

**LLM MCP 服务器、客户端与宿主：**

![image](https://raw.githubusercontent.com/lorisunjunbin/petp/master/image/DEEPSEEK-MCP.png)

**MCP 工具服务器（Streamable-HTTP）：**

![image](https://raw.githubusercontent.com/lorisunjunbin/petp/master/image/petp_as_standard_mcp_server.png)

**集成 Claude Code：**

![image](https://raw.githubusercontent.com/lorisunjunbin/petp/master/image/claude-code-mcp-tool.png)

---

## 快速开始

### 前置条件

| 需求 | 版本 | 说明 |
|------|------|------|
| Python | 3.14 | [下载](https://www.python.org/downloads/) |
| wxPython | 4.3.x | 须匹配 Python 版本 — 见第 2 步 |
| ChromeDriver | 与 Chrome 版本匹配 | 从 [Chrome for Testing](https://googlechromelabs.github.io/chrome-for-testing/) 下载，放入 `webdriver/<平台>/` |

> ChromeDriver 位置：`webdriver/darwin/chromedriver`（macOS）或 `webdriver/win32/chromedriver.exe`（Windows）

### 第 1 步 — 安装 Python

从 [python.org](https://www.python.org/downloads/) 下载安装 Python 3.14。

> Windows 安装时请勾选 **"Add Python to PATH"**。

### 第 2 步 — 安装 wxPython

wxPython 须精确匹配 Python 版本和操作系统。

- **Python 3.14**：PyPI 上的官方稳定版（4.2.x）**不支持** Python 3.14，须使用**开发快照版**（4.3.0 alpha），从 [wxpython.org/Phoenix/snapshot-builds](https://wxpython.org/Phoenix/snapshot-builds/) 下载对应的 `.whl` 文件：

| 平台 | 示例 |
|------|------|
| macOS (Apple Silicon) | `uv pip install wxPython-4.3.0a1XXXX-cp314-cp314-macosx_11_0_arm64.whl` |
| macOS (Intel) | `uv pip install wxPython-4.3.0a1XXXX-cp314-cp314-macosx_10_15_x86_64.whl` |
| Windows (64位) | `uv pip install wxPython-4.3.0a1XXXX-cp314-cp314-win_amd64.whl` |
| Linux (x86_64) | `uv pip install wxPython-4.3.0a1XXXX-cp314-cp314-linux_x86_64.whl` |

> 将 `1XXXX` 替换为快照页面上的实际构建号。建议始终使用**最新快照版**以获得最佳稳定性。
>
> **提示：** PETP 内置了自动下载最新 wxPython 快照版的 Execution：
> - `OOTB_DOWNLOAD_LATEST_WXPYTHON_mac_arm`（macOS Apple Silicon）
> - `OOTB_DOWNLOAD_LATEST_WXPYTHON_win_amd64`（Windows 64位）
>
> 通过后台模式运行（无需预装 wxPython）：
> ```bash
> python PETP_backgroud.py --run-execution OOTB_DOWNLOAD_LATEST_WXPYTHON_mac_arm
> ```
> `.whl` 文件将下载到 `download/` 目录，然后执行 `uv pip install download/<时间戳>/<文件名>.whl` 安装。

- **Python 3.12 / 3.13**：可直接从 PyPI 安装官方稳定版：

```bash
uv pip install wxPython
# 或
pip install wxPython
```

### 第 3 步 — 安装依赖

详见 [依赖管理](#依赖管理)。快速安装：

```bash
# 推荐：使用 uv 安装
pip install -U uv

# 如果出现："No virtual environment found"
uv venv
# 创建虚拟环境于：.venv
# 激活方式：.venv\Scripts\activate

uv pip install -r requirements.txt

# 或只安装需要的分组（见[依赖分组](#依赖分组)）
uv pip install -r requirements/core.txt -r requirements/ssh-sftp.txt

# 备选：使用 pip 安装
pip install -r requirements.txt

# 或只安装需要的分组（见[依赖分组](#依赖分组)）
pip install -r requirements/core.txt -r requirements/ssh-sftp.txt
```

### 第 4 步 — 运行

```bash
python PETP.py
```

GUI 窗口将启动。首次运行会在 `./config/petpconfig.yaml` 创建默认配置。

### macOS 启动脚本（建议长时间运行时使用）

```bash
chmod +x scripts/macos/start_petp.sh scripts/macos/start_petp_gui.sh scripts/macos/start_petp_background.sh

# ─── 统一入口（推荐）─────────────────────────────────────────────────────────

# GUI 模式
./scripts/macos/start_petp.sh gui

# 后台模式（绑定终端）
./scripts/macos/start_petp.sh bg
./scripts/macos/start_petp.sh bg --run-execution ENDECODER --no-http
./scripts/macos/start_petp.sh bg --run-pipeline MY_PIPELINE --no-http
./scripts/macos/start_petp.sh bg --run-execution MY_EXEC --headless --no-http
./scripts/macos/start_petp.sh bg --headless --http-port 9090

# 后台脱离终端模式（nohup，终端关闭不影响运行）
./scripts/macos/start_petp.sh bgd
./scripts/macos/start_petp.sh bgd --headless
./scripts/macos/start_petp.sh bgd --headless --http-port 9090

# 停止运行中的后台实例
./scripts/macos/start_petp.sh stop

# 查看帮助
./scripts/macos/start_petp.sh help

# ─── 兼容旧脚本（仍可用）─────────────────────────────────────────────────────

./scripts/macos/start_petp_gui.sh
./scripts/macos/start_petp_background.sh --run-execution ENDECODER --no-http
```

两个脚本默认使用（仅在未预先设置时生效）：
- `PYTHONMALLOC=malloc`
- `PYTHONUNBUFFERED=1`
- `PYTHONDONTWRITEBYTECODE=1`

可选覆盖示例：

```bash
PYTHON_BIN=python3.14 PETP_ECHO_ENV=1 ./scripts/macos/start_petp.sh gui
PYTHONMALLOC=malloc ./scripts/macos/start_petp.sh background --run-pipeline OOTB_TEST_PIPLINE_BG --no-http
```

### Windows 启动脚本（建议长时间运行时使用）

> **首次使用** — 允许 PowerShell 执行脚本（每台机器执行一次）：
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
> ```

```powershell
# ─── 统一入口（推荐）─────────────────────────────────────────────────────────

# GUI 模式
.\scripts\windows\start_petp.ps1 gui

# 后台模式（绑定终端）
.\scripts\windows\start_petp.ps1 bg
.\scripts\windows\start_petp.ps1 bg --run-execution ENDECODER --no-http
.\scripts\windows\start_petp.ps1 bg --run-pipeline MY_PIPELINE --no-http
.\scripts\windows\start_petp.ps1 bg --run-execution MY_EXEC --headless --no-http
.\scripts\windows\start_petp.ps1 bg --headless --http-port 9090

# 后台脱离终端模式（隐藏窗口，终端关闭不影响运行）
.\scripts\windows\start_petp.ps1 bgd
.\scripts\windows\start_petp.ps1 bgd --headless
.\scripts\windows\start_petp.ps1 bgd --headless --http-port 9090

# 停止运行中的后台实例
.\scripts\windows\start_petp.ps1 stop

# 查看帮助
.\scripts\windows\start_petp.ps1 help

# ─── 独立快捷脚本 ────────────────────────────────────────────────────────────

.\scripts\windows\start_petp_gui.ps1
.\scripts\windows\start_petp_background.ps1 --run-execution ENDECODER --no-http
```

默认自动应用（仅在未预先设置时生效）：
- `PYTHONUNBUFFERED=1`
- `PYTHONDONTWRITEBYTECODE=1`

可选覆盖示例（在调用脚本前设置环境变量）：

```powershell
$env:PYTHON_BIN = '.\.venv\Scripts\python.exe'
$env:PETP_ECHO_ENV = '1'
.\scripts\windows\start_petp.ps1 gui

# 后台模式，指定 Python 版本
$env:PYTHON_BIN = 'python3.14'
.\scripts\windows\start_petp.ps1 bg --run-pipeline OOTB_TEST_PIPLINE_BG --no-http
```

| 变量 | 默认值 | 说明 |
|---|---|---|
| `PYTHON_BIN` | `python` | Python 可执行文件路径 |
| `PYTHONUNBUFFERED` | `1` | 实时输出日志 |
| `PYTHONDONTWRITEBYTECODE` | `1` | 禁止生成 `.pyc` 文件 |
| `PETP_ECHO_ENV` | _(未设置)_ | 设为 `1` 可打印运行时配置 |
| `PETP_HEADLESS` | _(未设置)_ | 设为 `true` 强制 Selenium headless 运行（等同 `--headless`） |
| `PETP_BG_LOG` | `petp_bg.log` | 脱离终端模式（`bgd`）的日志文件路径 |

---

## 依赖管理

PETP 采用**模块化依赖结构** — 按处理器类别拆分，灵活安装，按需打包。

### 使用 `uv` 安装（推荐）

[`uv`](https://docs.astral.sh/uv/) 是高性能 Python 包管理器（比 pip 快 10-100 倍）。与现有 requirements 文件完全兼容 — **零迁移成本**。

```bash

# 方案 A（推荐）：创建并使用虚拟环境
uv pip install -r requirements.txt

# 方案 B：显式安装到系统 Python
uv pip install --system -r requirements.txt

# 全量安装（GUI 桌面版）
uv pip install -r requirements.txt

# 后台服务（无 GUI）
uv pip install -r requirements-nogui.txt

# Docker（无头模式，无浏览器自动化）
uv pip install -r requirements-docker.txt

# 自定义组合
uv pip install -r requirements/core.txt -r requirements/ssh-sftp.txt -r requirements/http-client.txt
```

#### 使用 `uv pip compile` 锁定版本

生成带版本锁定的依赖文件，确保可复现构建：

```bash
# 编译单个分组
uv pip compile requirements/core.txt -o requirements/core.lock

# 编译全量依赖
uv pip compile requirements.txt -o requirements.lock
```

### 依赖分组

| 文件 | 分类 | 包 |
|------|------|-----|
| `core.txt` | 核心框架 | pyyaml, cryptocode, croniter, cron-descriptor, python-dateutil |
| `http-client.txt` | HTTP 请求 | requests, httpx, httpx-sse |
| `web-automation.txt` | 浏览器自动化 | selenium, urllib3, Pillow |
| `web-scraping.txt` | 网页抓取 | beautifulsoup4, lxml |
| `data-processing.txt` | JSON 处理 | jsonpath-python |
| `excel-data.txt` | Excel 与数据 | openpyxl, pandas |
| `chart.txt` | 可视化 | matplotlib |
| `document.txt` | 文档处理 | python-docx |
| `ssh-sftp.txt` | SSH / SFTP | paramiko |
| `gui-automation.txt` | 桌面自动化 | pyautogui, pyperclip |
| `gui-wxpython.txt` | 桌面 GUI | wxpython |
| `database.txt` | 数据库 | psycopg, mysql-connector-python, hdbcli（按需启用） |
| `ai-gemini.txt` | Google Gemini AI | google-genai |
| `ai-deepseek.txt` | DeepSeek AI | openai |
| `ai-ollama.txt` | Ollama 本地 LLM | ollama |
| `ai-zhipu.txt` | 智谱 Z.AI | zai |
| `mcp.txt` | MCP 协议 | mcp |
| `ocr.txt` | OCR 识别 | rapidocr-onnxruntime, numpy, scipy（paddleocr、easyocr 可选） |
| `captcha.txt` | 验证码识别 | ddddocr |
| `javascript.txt` | JS 引擎 | pythonmonkey |
| `video-download.txt` | 视频下载 | pytube |
| `http-service.txt` | HTTP 服务端 | fastapi, uvicorn |
| `webapp.txt` | Web 应用 | Flask, flask-httpauth, werkzeug, gunicorn |
| `system-build.txt` | 系统工具 | psutil, pyinstaller |

### 更新依赖

```bash
# 使用 pip
pip list --outdated | grep -v '^\-e' | cut -d = -f 1 | xargs -n1 pip install -U

# 使用 uv
uv pip install --upgrade -r requirements.txt
```

---

## 运行模式

| 模式 | 入口 | GUI | Selenium | 适用场景 |
|------|------|-----|----------|----------|
| 桌面 | `python PETP.py` | 有 | 有 | 本地开发、交互式 RPA |
| 后台 | `python PETP_backgroud.py` | 无 | 有（`--headless` 可选） | CLI、定时任务 |
| Docker | 容器内 `PETP_backgroud.py` | 无 | Headless（自动） | 服务器部署、CI/CD |

### 后台模式

```bash
# ─── 基本用法 ────────────────────────────────────────────────────────────────

# 启动为持久化 HTTP / MCP 服务（端口 8866）
python PETP_backgroud.py

# 运行单个 Execution 后退出（不启动 HTTP 服务）
python PETP_backgroud.py --run-execution ENDECODER --no-http

# 运行单个 Pipeline 后退出
python PETP_backgroud.py --run-pipeline OOTB_TEST_PIPLINE_BG --no-http

# 传入初始数据（JSON）到执行中
python PETP_backgroud.py --run-execution MY_EXEC --init-data '{"key":"value"}' --no-http

# ─── Selenium（headless 模式）────────────────────────────────────────────────

# 以 headless 模式运行 Selenium 任务（无可见浏览器窗口）
python PETP_backgroud.py --run-execution MY_SELENIUM_EXEC --headless --no-http

# Headless Pipeline
python PETP_backgroud.py --run-pipeline MY_PIPELINE --headless --no-http

# Headless 持久化服务
python PETP_backgroud.py --headless

# ─── 参数覆盖 ────────────────────────────────────────────────────────────────

# 覆盖 UI 策略和日志级别
python PETP_backgroud.py --ui-policy abort --log-level DEBUG

# 自定义 HTTP 端口和鉴权 Token
python PETP_backgroud.py --http-port 9090 --http-token my_secret_token

# 组合：headless + 自定义端口 + 启动时执行
python PETP_backgroud.py --headless --http-port 9090 --run-execution STARTUP_TASK

# ─── 进程管理 ────────────────────────────────────────────────────────────────

# 脱离终端启动（终端关闭后不影响运行）
nohup python PETP_backgroud.py > petp_bg.log 2>&1 &

# 脱离终端 + headless Selenium
nohup python PETP_backgroud.py --headless > petp_bg.log 2>&1 &

# 停止运行中的后台实例（读取 PID 文件，发送 SIGTERM）
python PETP_backgroud.py --stop

# ─── 使用启动脚本（macOS）────────────────────────────────────────────────────

./scripts/macos/start_petp.sh bg --run-execution ENDECODER --no-http
./scripts/macos/start_petp.sh bg --headless --run-pipeline MY_PIPELINE --no-http
./scripts/macos/start_petp.sh bgd                    # 脱离终端（nohup）
./scripts/macos/start_petp.sh bgd --headless         # 脱离终端 + headless
./scripts/macos/start_petp.sh stop                   # 停止运行中的实例

# ─── 使用启动脚本（Windows）──────────────────────────────────────────────────

# .\scripts\windows\start_petp.ps1 bg --run-execution ENDECODER --no-http
# .\scripts\windows\start_petp.ps1 bg --headless --run-pipeline MY_PIPELINE --no-http
# .\scripts\windows\start_petp.ps1 bgd                    # 脱离终端（隐藏窗口）
# .\scripts\windows\start_petp.ps1 bgd --headless         # 脱离终端 + headless
# .\scripts\windows\start_petp.ps1 stop                   # 停止运行中的实例

# ─── Docker ──────────────────────────────────────────────────────────────────

# Docker 自动启用 headless（Dockerfile 中设置 PETP_HEADLESS=true）
docker run --rm -p 8866:8866 petp-background:amd64-local

# Docker + 启动时运行 Execution
docker run --rm petp-background:amd64-local python PETP_backgroud.py --run-execution MY_EXEC --no-http

# Docker + 自定义端口 + 初始数据
docker run --rm -p 9090:9090 petp-background:amd64-local \
  python PETP_backgroud.py --http-port 9090 --run-execution MY_EXEC --init-data '{"env":"prod"}'
```

### Pipeline 定时模式

Pipeline 支持按 cron 表达式定时运行。GUI 设置步骤：

1. 切换到 **Pipelines** 标签页 → 选择或新建 Pipeline
2. 勾选 **as cron** → 输入 cron 表达式（如 `0 9 * * 1-5`）
3. 点击 **Execute** — 按计划运行，直到通过 **Stop** / **Stop All** 停止

cron 输入框的 tooltip 会显示可读描述（如 "At 09:00 AM, Monday through Friday"）。

**YAML 示例：**

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

**运行用例：**

```bash
# GUI — 通过复选框 + 表达式输入管理 cron 调度，配置持久化到 YAML

# 后台 — 单次运行 Pipeline（cron 字段会保存但不会在后台模式自动调度）
python PETP_backgroud.py --run-pipeline DAILY_REPORT --no-http

# 后台 — 带初始数据运行
python PETP_backgroud.py --run-pipeline DAILY_REPORT --init-data '{"to":"ops@example.com"}' --no-http

# 后台 — 持久化 HTTP 服务（通过 POST /petp/exec 触发 Pipeline）
python PETP_backgroud.py

# Docker
docker run --rm -p 8866:8866 petp-background:amd64-local
# 然后: POST http://localhost:8866/petp/exec  {"pipeline":"DAILY_REPORT","wait_for_result":true}
```

#### CLI 参数说明

| 参数 | 可选值 | 默认值 | 说明 |
|------|--------|--------|------|
| `--run-execution NAME` | 任意 Execution 名称 | — | 启动时立即运行指定的 Execution |
| `--run-pipeline NAME` | 任意 Pipeline 名称 | — | 启动时立即运行指定的 Pipeline |
| `--init-data JSON` | JSON 对象字符串 | `{}` | 运行前注入 `data_chain` 的键值对；MCP `default` 值会填充其中未设置的键 |
| `--no-http` | 标志位 | 关闭 | 不启动 HTTP/MCP 服务器，任务完成后进程直接退出 |
| `--headless` | 标志位 | 关闭 | 以 headless 模式运行 Selenium 任务（Docker 中自动启用） |
| `--stop` | 标志位 | — | 通过 PID 文件向运行中的后台实例发送 SIGTERM 信号以停止 |
| `--nogui-enabled {true,false}` | `true` / `false` | `true` | 启用或禁用无 GUI 后台模式 |
| `--ui-policy {skip,abort}` | `skip` / `abort` | `skip` | 遇到 GUI 专属处理器时的处理策略：`skip` 静默跳过，`abort` 抛出错误 |
| `--log-level LEVEL` | `DEBUG` / `INFO` / `WARNING` / `ERROR` | 读取配置 | 覆盖本次运行的日志级别 |
| `--http-port PORT` | 整数 | `8866` | 覆盖 HTTP 服务端口 |
| `--http-token TOKEN` | 字符串 | 读取配置 | 覆盖 HTTP 接口鉴权 Bearer Token |

#### `petpconfig.yaml` — 后台模式相关配置项

| 配置键 | 默认值 | 说明 |
|--------|--------|------|
| `nogui_enabled` | `true` | 必须为 `true` 才能激活后台模式 |
| `nogui_ui_processor_policy` | `skip` | `skip` 静默跳过 GUI 处理器；`abort` 遇到第一个 GUI 处理器时终止执行 |
| `http_port` | `8866` | 内置 HTTP / MCP 服务的监听端口 |
| `http_request_token` | _(base64 字符串)_ | HTTP API 接口所有请求所需的 Bearer Token |
| `http_request_timeout` | `600` | HTTP 请求超时秒数 |
| `log_level` | `INFO` | 运行时日志详细程度 |
| `execute_on_startup` | `false` | 服务启动时自动执行的 Execution 名称 |

#### `BackgroundRuntime` 返回结构

每次 `run_execution` / `run_pipeline` 调用均返回：

```json
{
  "ok": true,
  "data": { "<data_key>": "<value>", "...": "..." },
  "error": null,
  "meta": {
    "duration_ms": 42,
    "skipped_tasks": [{ "task_index": 2, "task_type": "SHOW_RESULT", "reason": "task.skipped" }],
    "aborted_tasks": []
  }
}
```

- `ok` — 执行过程中无未处理异常则为 `true`
- `data` — `data_chain` 的公开子集（排除 `__m`、`__p` 及 WebDriver 等不可序列化的值）；如果执行设置了 `response_key`，则只返回该键对应的值
- `error` — 失败时的错误信息字符串，成功时为 `null`
- `meta.duration_ms` — 执行的墙钟耗时（毫秒）
- `meta.skipped_tasks` — 被跳过任务的列表（`task.skipped = true` 或被 `ui_policy` 过滤）

#### 无 GUI 模式下跳过的处理器

仅**需要操作系统级 GUI 交互且无 headless 替代方案**的处理器会被跳过：

| 处理器 | 原因 |
|--------|------|
| `FILE_CHOOSER` | 使用 `pyautogui` 操作 OS 文件选择对话框，无程序化替代方案 |

以下处理器通过 `self.view is not None` 判断，在后台模式下**优雅降级**（日志/回退，不跳过）：

| 处理器 | 后台模式行为 |
|--------|-------------|
| `SHOW_RESULT` | 记录标题和消息到日志 |
| `INPUT_DIALOG` | 使用 `default_value` 参数值，继续执行 |
| `MATPLOTLIB` | 记录图表参数到日志 |

所有 **Selenium** 处理器（`GO_TO_PAGE`、`FIND_THEN_CLICK` 等）在后台模式下正常运行。所有**鼠标**处理器（`MOUSE_CLICK`、`MOUSE_POSITION`、`MOUSE_SCROLL`）通过 pyautogui 正常运行。

> 在 Docker 外强制 headless Selenium：使用 `--headless` 标志或设置 `PETP_HEADLESS=true` 环境变量（Docker 中自动启用）。

#### 运行测试套件

```bash
# pytest 单元 & 集成测试（expression2str、data_chain、loop 状态机、processor、runtime）
python -m pytest testcoverage/ -v

# 传统测试脚本
python testcoverage/test_bg_runtime.py   # 17 个 BG 模式用例，覆盖 ENDECODER、DB_ACCESS、Pipeline、工具缓存、返回结构
python testcoverage/nogui_smoke.py       # 单 Execution 冒烟测试，失败时以非零退出码退出
```

---

## HTTP 服务与 MCP

PETP 内置 HTTP 服务器，端口 **8866**。

| 端点 | 说明 |
|------|------|
| `GET /` | PETP HTTP 服务首页 |
| `GET /mcp` | MCP 工具服务器（Streamable-HTTP） |

MCP Inspector 设置：Transport Type = **Streamable HTTP**，URL = `http://localhost:8866/mcp`

---

## 打包与 Docker

### 打包可执行文件

```bash
python build/PETP_build.py
```

输出到 `./dist/`：macOS 生成 `PETP.app`，Windows 生成 `PETP.exe`。

### Docker

支持在 **Apple M1 (arm64) 构建**、在 **x86 (amd64) 运行**。

| 文件 | 用途 |
|------|------|
| `Dockerfile` | 多架构镜像（Python 3.14-slim） |
| `build/docker_build.sh` | 一键构建脚本（buildx + QEMU） |
| `requirements-docker.txt` | 无头模式依赖 |

```bash
# 本地构建并运行
./build/docker_build.sh
docker run --rm -p 8866:8866 petp-background:amd64-local

# 推送到仓库
./build/docker_build.sh --push yourrepo/petp-background:1.0
```

**容器端点：**

| 端点 | 说明 |
|------|------|
| `GET /health` | 健康检查 |
| `GET /petp/tools` | 列出 MCP 工具 |
| `POST /petp/exec` | 触发 Execution / Pipeline |
| `GET /petp/result?request_id=<id>` | 查询异步结果 |
| `POST /mcp` | MCP 工具服务器 |

## Web App（Docker & UGOS）

独立 Web App（`webapp/`）提供了完整的 Docker 打包说明，包含 UGOS（`linux/amd64`）的构建、导出、导入步骤：

- [`webapp/README.md`](./webapp/README.md)
- UGOS 快速路径：使用 `buildx` 构建 `linux/amd64`，校验架构后导出 tar，并在 NAS 使用 `docker load` 导入。

---

## 项目结构

### 根目录文件

| 分类 | 文件 | 说明 |
|------|------|------|
| 入口 | `PETP.py` | GUI 桌面入口 |
| | `PETP_backgroud.py` | 无头 / 后台入口 |
| 构建 | `build/PETP_build.py` | PyInstaller 构建（GUI） |
| | `build/PETP_background_build.py` | PyInstaller 构建（后台） |
| | `build/build_common.py` | 共享构建工具 |
| | `build/*.spec` | PyInstaller 规格模板 |
| | `build/debug_runtime.py` | 打包应用调试辅助 |
| Docker | `Dockerfile` | 多架构镜像 |
| | `build/docker_build.sh` | 构建脚本 |
| | `.dockerignore` | 排除列表 |
| 依赖 | `requirements.txt` | 全量安装（引用所有分组） |
| | `requirements-nogui.txt` | 无 GUI / 后台服务 |
| | `requirements-docker.txt` | Docker / 无头模式 |
| | `requirements/*.txt` | 模块化依赖分组 |

### 目录结构

| 目录 | 说明 |
|------|------|
| `build/` | PyInstaller 规格模板与调试辅助 |
| `config/` | 配置（`petpconfig.yaml`） |
| `core/` | 核心引擎 — execution、pipeline、task、processor、loop、cron |
| `core/executions/` | YAML 执行定义 |
| `core/processors/` | 处理器实现（每个任务类型一个 `.py` 文件） |
| `core/pipelines/` | YAML 流水线定义 |
| `core/runtime/` | 后台 / 无 GUI 运行时逻辑 |
| `core/definition/` | YAML 读写器、Chrome DevTools Recorder 转换器 |
| `httpservice/` | HTTP 服务器、MCP 处理器、请求路由 |
| `mvp/` | GUI 层（Model-View-Presenter） |
| `utils/` | 工具模块 — Selenium、Excel、Date、OS、Logger、Paramiko、decorators |
| `webapp/` | Flask Web 应用（Docker 与 UGOS 使用说明见 [`webapp/README.md`](./webapp/README.md)） |
| `webdriver/` | 平台 ChromeDriver 二进制文件 |
| `resources/` | 静态资源 |
| `download/` | 默认下载目录 |
| `testcoverage/` | 测试脚本 |
| `log/` | 运行日志 |

---

## 常见问题

| 问题 | 解决方案                                                                                                    |
|------|---------------------------------------------------------------------------------------------------------|
| `ModuleNotFoundError` | `pip install <包名>` 或安装对应的依赖分组                                                                           |
| wxPython 导入错误 | 确保 `.whl` 文件匹配 Python 版本和操作系统, [Phoenix-snapshot-builds](https://wxpython.org/Phoenix/snapshot-builds/) |
| ChromeDriver 版本不匹配 | 从 [Chrome for Testing](https://googlechromelabs.github.io/chrome-for-testing/) 下载对应版本                   |
| 端口 8866 被占用 | 在 `petpconfig.yaml` 中修改端口                                                                               |

---

## 致谢

- [wxPython](https://www.wxpython.org/) & [wxGlade](https://wxglade.sourceforge.net/)
- [Selenium](https://selenium-python.readthedocs.io/) & [ChromeDriver](https://googlechromelabs.github.io/chrome-for-testing/) & [Chrome DevTool Recorder](https://developer.chrome.com/docs/devtools/recorder)

---

## 更新日志

### 2026

| 日期 | 更新内容                                                                                                                                                                                          |
|------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 2026-05 | 界面精简：移除 DC 查看器；日志级别和清除日志控件整合进 LogSearchBar；新增通用 `PopupMenuButton` 组件用于主题/语言/日志级别选择；新增 5 套主题（Nord、Dracula、Sakura、Cyberpunk，总计 9 套）；DEBUG 级别下每个 Task 执行后输出 `data_chain` JSON |
| 2026-05 | 新增 `IF_ELSE` 处理器：声明式条件分支 — 根据 Python 条件表达式（基于 `data_chain`）跳过 "then" 或 "else" 任务块；支持在循环内正确运行 |
| 2026-05 | 定时任务执行历史弹窗（Pipeline 标签页 History 按钮）：浏览最近 50 次执行记录，含状态、耗时、错误详情；支持按流水线名称过滤 |
| 2026-05 | `INPUT_DIALOG` 后台模式：尊重 `data_chain` 中已有的值，不再用 `default_value` 覆盖；GUI 模式下将已有值预填到输入框 |
| 2026-05 | 状态栏任务进度显示；LRU 执行缓存；持久化日志文件描述符；修复退出时 wx.Timer 触发导致的 SEGFAULT 崩溃 |
| 2026-04 | 状态栏（`highlightInfo`）：展示关键执行事件 — `[START]`、`[DONE]`（含耗时）、`[ERROR]`（含错误信息）、`[STOP]`；颜色跟随主题 accent 色。`Executor` DONE 事件现携带错误信息 |
| 2026-04 | "System" 自动主题：跟随系统深浅色模式（深色→Monokai，浅色→Ocean），通过 `wx.EVT_SYS_COLOUR_CHANGED` 实时响应系统外观切换 |
| 2026-04 | 主题系统：4 套内置配色主题（Forest、Ocean、Monokai、Solarized），工具栏下拉实时切换，选择持久化到 `petpconfig.yaml`。覆盖表格选中色、属性编辑器、日志面板、搜索高亮、运行按钮渐变色、MCP 工具开关强调色 |
| 2026-04 | 录制转换器从 Selenium IDE（`.side`）切换为 Chrome DevTools Recorder（`.json`）；支持 navigate、click、doubleClick→collect、change、keyDown/keyUp 合并、waitForElement |
| 2026-04 | 新增 `GO_TO_TASK` 处理器：条件跳转到执行内任意 task；循环新增 `loop_condition` 属性，支持编程式 break/continue；`CodeExplainerUtil` 动态函数缓存优化 |
| 2026-04 | `OCR` 图像预处理（二值化、去噪、锐化、放大、自适应、自动）；新增 `CAPTCHA` 处理器（ddddocr：ocr/slide/det 模式） |
| 2026-04 | 日志面板：搜索高亮 + 上/下一个导航（Ctrl+F / Cmd+F）；属性介绍右键弹窗；`FIND_THEN_CLICK` 新增 by_condition 参数 |
| 2026-04 | 循环编辑器：右键菜单支持属性介绍和编辑复杂值；全处理器推广 `explain_param_or_default` 简化参数读取 |
| 2026-04 | GUI 与 BG 模式 MCP 处理逻辑统一，提取 `McpMixin`；修复 `structuredContent` 格式；`outputSchema` 支持 `mapKey` 字段映射 |
| 2026-04 | MCP 工具 schema 支持输入 `default` 默认值与输出 `mapKey` 字段映射；`McpDescEditor` 编辑器增强 |
| 2026-04 | 任务网格右键菜单新增"查看处理器用法"与"查找引用执行"选项 |
| 2026-04 | MCP 工具开关改为自定义 `ToggleSwitch` 组件；新增状态标签与响应键警告提示 |
| 2026-04 | Execution 描述编辑器改为结构化 `McpDescEditor`，支持 MCP 工具 schema 可视化编辑 |
| 2026-04 | `HTTP_REQUEST` 处理器新增内置 Basic Auth、OAuth2 与 XSRF/CSRF token 支持 |
| 2026-04 | 新增 `RUN_JAVASCRIPT` 处理器（基于 PythonMonkey），支持执行 JS 函数 |
| 2026-04 | 新增执行快照按钮；`SearchableComboBox` 支持实时过滤与键盘导航，工具/导航图标前缀 |
| 2026-04 | 循环编辑器：右键或 ⚙️ 按钮打开键值表单编辑循环属性；循环变更支持快照与撤销/重做。修复跳过任务、粘贴、增删行、循环编辑后保存按钮未启用的问题。 |
| 2026-04 | 图形用户界面具备撤销、重做和历史记录功能。还增强了实用工具。 |
| 2026-04 | 国际化支持 : 中文 和 英文，界面语言可动态切换                                                                                                                                                                     |
| 2026-04 | 模块化依赖管理（`requirements/` 分组）；`uv` 支持                                                                                                                                                           |
| 2026-04 | 无 GUI 模式、[`PETP_backgroud.py`](./PETP_backgroud.py)、[`Docker`](./Dockerfile) 支持                                                                                                               |
| 2026-04 | 工具栏：追加 `date_str`、`os.sep`；**跳过任务**复选框                                                                                                                                                        |
| 2026-03 | 开箱即用：`OOTB_DOWNLOAD_LATEST_WXPYTHON`（macOS & Windows）                                                                                                                                         |
| 2026-03 | [`FIND_MULTI_XXXProcessor`](./core/processors/FIND_MULTI_THEN_CLICKProcessor.py) 跳过功能                                                                                                         |
| 2026-03 | Selenium 页面加载超时支持                                                                                                                                                                             |
| 2026-02 | **MCP 工具服务器**（Streamable-HTTP）— [mcp_client_4_petp](./testcoverage/mcp_client_4_petp.py)                                                                                                       |
| 2026-01 | **智谱 Z.AI**：[SETUP](./core/processors/AI_LLM_ZHIPU_SETUPProcessor.py) / [Q&A](./core/processors/AI_LLM_ZHIPU_QANDAProcessor.py) / [MCP](./core/processors/AI_LLM_ZHIPU_QANDA_MCPProcessor.py) |

### 2025

| 日期 | 更新内容 |
|------|----------|
| 2025-10 | [STOPPERProcessor](./core/processors/STOPPERProcessor.py) / [RELOAD_LOGProcessor](./core/processors/RELOAD_LOGProcessor.py)；升级 Python 3.14 |
| 2025-06 | 开箱即用：`OOTB_AI_LLM_GEMINI_MCP` |
| 2025-05 | `ThreadingHTTPServer`；**高级输入对话框**；HTTP 服务（端口 8866） |
| 2025-05 | 开箱即用：`OOTB_AI_LLM_OLLAMA_MCP` / `OOTB_AI_LLM_DEEPSEEK_MCP` |
| 2025-04 | Execution 搜索、改进下拉框 |
| 2025-03 | ChromeDriver v134 |
| 2025-01 | 初始 **AI LLM** 支持：DeepSeek / Gemini / Ollama |

### 2024

| 日期 | 更新内容 |
|------|----------|
| 2024-10 | Python 3.13，ChromeDriver 130 |
| 2024-08 | [MATPLOTLIBProcessor](./core/processors/MATPLOTLIBProcessor.py)、[AI_LLM_OLLAMA_QANDAProcessor](./core/processors/AI_LLM_OLLAMA_QANDAProcessor.py)、[RUN_EXECUTIONProcessor](./core/processors/RUN_EXECUTIONProcessor.py) |
| 2024-07 | Gemini AI-LLM；[DATA_MULTI_MASKINGProcessor](./core/processors/DATA_MULTI_MASKINGProcessor.py)；任务跳过 |
| 2024-06 | [DATA_GROUPBYProcessor](./core/processors/DATA_GROUPBYProcessor.py)、[DATA_MASKINGProcessor](./core/processors/DATA_MASKINGProcessor.py) |
| 2024-05 | HttpServer（GET/POST、JSON） |
| 2024-04 | PyInstaller 构建后按需加载处理器 |
| 2024-03 | PyInstaller 打包 macOS & Windows 可执行文件 |
| 2024-02 | [PETP 文件查看器](./webapp/README.md) Web 应用（Flask） |
| 2024-01 | 启动时自动执行 |

### 2023

| 日期 | 更新内容 |
|------|----------|
| 2023-12 | `DATA_COLLECT`、`DATA_MAPPING`、`FIND_MULTI_THEN_CLICK`、`FOLDER_WATCH_MOVE` 处理器 |
| 2023-11 | [ENCODE_DECODE_STRProcessor](./core/processors/ENCODE_DECODE_STRProcessor.py)、[HASH_STRProcessor](./core/processors/HASH_STRProcessor.py)、[DATA_FILTERProcessor](./core/processors/DATA_FILTERProcessor.py)、[COLLECTION_MERGEProcessor](./core/processors/COLLECTION_MERGEProcessor.py)；运行时日志级别；滚动文件处理器 |
| 2023-10 | Python 3.12 |
| 2023-09 | DB_ACCESS：MySQL / PostgreSQL / SAP HANA / SQLite |
| 2023-04 | `PYTUBEProcessor` — YouTube 下载 |

### 2022

| 日期 | 更新内容 |
|------|----------|
| 2022-11 | UI 简化与事件绑定清理 |
| 2022-10 | 非阻塞 GUI 执行 |
| 2022-09 | 恢复上次运行；`MOUSE_CLICKProcessor`、`MOUSE_SCROLLProcessor` |
| 2022-07 | MySQL 支持；Selenium 4.3.0 |
| 2022-06 | Python 3.10、wxPython 4.1.2 |
| 2022-05 | Mac M1 wxPython 修复 |
| 2022-04 | `ZIPProcessor` |
| 2022-03 | 循环 N 次模式 |

### 2021

| 日期 | 更新内容 |
|------|----------|
| 2021-10 | [BEAUTIFUL_SOUPProcessor](./core/processors/BEAUTIFUL_SOUPProcessor.py) |
| 2021-09 | 表格复制粘贴 |
