# ![image](./image/petp_small.png) PET-P

中文 | **[English](./readme.md)**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE.txt)

Python RPA 工具包，80+ 处理器编排浏览器自动化、AI/LLM（10 家供应商）、数据库、SSH、邮件和 HTTP 任务。可配置的 Pipeline 支持 cron 定时与循环。支持 wxPython GUI、无头服务和 Docker 容器三种运行模式。内置 MCP 工具服务器（Streamable-HTTP）供 AI Agent 集成。

```
Pipeline  1:n  Execution
Execution 1:n  Task
Task      1:1  Processor
```

**链接：** [项目介绍](https://petp.tail138025.ts.net/?lang=zh) | [Web App](./webapp/README.md) | [更新日志](./CHANGELOG.md)

---

## AI 执行生成器

通过自然语言对话与 LLM 生成和修改 PETP 任务流程。

**入口：**
- 创建 Execution → 选择 "AI 生成" 模板
- taskGrid 右键 → "AI 协助"（对话式修改现有 Execution）
- MCP 编辑器 → "AI" 按钮（自动生成工具描述 JSON）

**亮点：**
- 多轮对话 — 咨询 Processor 用法、生成流程、增量修改任务
- Processor 浏览器 — 可展开的 TreeListCtrl，内置完整文档、搜索和过滤
- 选择性上下文 — 只有勾选的 Processor 发送给 LLM（节省 Token）
- 连接缓存 — 首次验证后即时复用，对话历史保留
- 10 家 LLM — 最简配置：只需设置 `ai_provider`

**AI 驱动的 MCP Tool 发布：**
- 一键生成 `mcp_desc` JSON，将 Execution 发布为 MCP 工具
- 自动从 INITIAL_PARAMS 提取输入参数，从结果任务提取输出键
- 生成 AI Agent 可理解的描述，帮助大模型判断何时调用此工具
- 智能合并 — 新字段补充到已有配置中，不覆盖已有内容
- 进度弹窗实时显示状态，预览结果后再应用

**AI 错误分析与自动修复：**
- 执行失败时，AI 自动分析错误上下文（失败任务、周边任务、堆栈信息）
- 定位根因并给出具体修复建议
- 一键"打开 AI 助手"预填诊断结果——在多轮对话中继续修复

**视觉模型支持（Ollama）：**
- `AI_LLM_QANDA` 新增 `image_path` 参数，支持多模态提问
- 适配 Ollama 视觉模型（gemma4、llava、moondream 等）
- 图片路径支持表达式——可动态引用 `data_chain` 中前序任务产出的文件路径

**配置**（仅 `ai_provider` 必填，其余自动从 provider 默认值填充）：

```yaml
application:
  ai_provider: zhipu       # 或: deepseek, anthropic, gemini, ollama 等
  ai_model: ""             # 留空 = 使用 provider 默认模型（如 GLM-5）
  ai_api_key: ""           # 留空 = 从默认环境变量读取（如 ZHIPU_ACCESS_KEY）
  ai_base_url: ""          # 留空 = 使用 provider 默认地址
```

详见 [配置文档](./docs/configuration_cn.md#ai-助手配置)。

---

## 快速开始

### 1. 安装 Python 3.14

从 [python.org](https://www.python.org/downloads/) 下载。Windows 安装时勾选"Add Python to PATH"。

### 2. 安装 wxPython（仅 GUI 模式）

<details>
<summary>Python 3.14 需要开发快照版本（点击展开）</summary>

PyPI 稳定版（4.2.x）**不支持** Python 3.14。从 [wxpython.org/Phoenix/snapshot-builds](https://wxpython.org/Phoenix/snapshot-builds/) 下载匹配平台的 4.3.0-alpha `.whl`：

```bash
# macOS Apple Silicon
uv pip install wxPython-4.3.0a1XXXX-cp314-cp314-macosx_11_0_arm64.whl

# Windows 64-bit
uv pip install wxPython-4.3.0a1XXXX-cp314-cp314-win_amd64.whl
```

或通过 PETP 自动下载（无需预装 wxPython）：
```bash
python PETP_background.py --run-execution OOTB_DOWNLOAD_LATEST_WXPYTHON_mac_arm
```

</details>

Python 3.12/3.13 直接：`pip install wxPython`

### 3. 安装依赖

```bash
pip install -U uv
uv pip install -r requirements.txt        # 完整（GUI）
# 或: uv pip install -r requirements-nogui.txt   # 无头
# 或: uv pip install -r requirements-docker.txt  # Docker
```

<details>
<summary>按需安装 — 只装你需要的</summary>

```bash
uv pip install -r requirements/core.txt -r requirements/ssh-sftp.txt -r requirements/http-client.txt
```

`requirements/` 目录下可选分组：`ai-deepseek.txt`、`ai-gemini.txt`、`ai-ollama.txt`、`database.txt`、`excel-data.txt`、`mcp.txt`、`ocr.txt`、`web-automation.txt` 等。

</details>

### 4. 运行

```bash
python PETP.py          # GUI 模式
python PETP_background.py   # 无头服务（端口 8866）
```

---

## 截图

## Mac OS

![PETP Overview macOS](https://raw.githubusercontent.com/lorisunjunbin/petp/master/image/PETP_overview.png)

## Windows

![PETP Overview Windows](https://raw.githubusercontent.com/lorisunjunbin/petp/master/image/PETP_overview_windows.png)


**MCP 工具服务器 — 集成 Claude Code、Cursor 等 AI Agent：**

![image](https://raw.githubusercontent.com/lorisunjunbin/petp/master/image/petp_as_standard_mcp_server.png)

---

## 功能特性

| 分类 | 能力 |
|------|------|
| **浏览器自动化** (Selenium) | 导航、点击、输入、采集、批量查找、iFrame、Cookie、截图。支持 Chrome DevTools Recorder 导入。 |
| **SSH / SFTP** (Paramiko) | SSH/SFTP 会话、远程命令、文件上传下载。 |
| **文件与文件夹** | 打开、写入、删除、读取、查找、监控自动移动、ZIP/UNZIP。 |
| **数据与表格** | CSV/Excel 读写、采集、过滤、分组、映射、脱敏、合并。 |
| **数据库** | MySQL、PostgreSQL、SAP HANA、SQLite — 统一 `DB_ACCESS` 处理器。 |
| **AI / LLM**（10 家供应商） | DeepSeek、Gemini、Ollama、智谱、Anthropic、千帆、MiniMax、豆包、月之暗面、OpenAI 兼容。初始化 + 问答 + MCP 工具调用。 |
| **AI 执行生成器** | 自然语言 → 任务流程生成。多轮对话、Processor 浏览器、选择性上下文、连接缓存。 |
| **MCP** | 标准 MCP 工具服务器（Streamable-HTTP）。支持所有 LLM 供应商的 MCP 客户端。 |
| **HTTP / 网络** | 可配置请求、响应提取、OAuth2/PKCE、Basic Auth、XSRF。 |
| **邮件** | SMTP 发送（抄送/密送、HTML、附件）。IMAP 接收（过滤、附件下载）。 |
| **OCR & 验证码** | 图像文字提取（paddleocr/rapidocr/easyocr）。验证码识别（ddddocr）。 |
| **鼠标与 GUI** (PyAutoGUI) | 点击、滚动、位置查询。 |
| **执行控制** | 初始化参数、嵌套执行、条件停止/跳转、`IF_ELSE` 分支、循环、Shell 命令。 |
| **主题** | 9 套主题（System 自动 + 8 个命名主题）实时切换。 |

---

## 运行模式

| 模式 | 命令 | GUI | 用途 |
|------|------|-----|------|
| 桌面 | `python PETP.py` | 是 | 交互式开发 |
| 后台 | `python PETP_background.py` | 否 | CLI、HTTP/MCP 服务 |
| Docker | `docker run -p 8866:8866 petp` | 否 | 服务器部署 |

```bash
# 运行单个 Execution 后退出
python PETP_background.py --run-execution ENDECODER --no-http

# 带初始数据运行 Execution
python PETP_background.py --run-execution MY_EXEC --init-data '{"key":"value"}' --no-http

# 运行 Pipeline 后退出
python PETP_background.py --run-pipeline DAILY_REPORT --no-http

# 带初始数据运行 Pipeline
python PETP_background.py --run-pipeline MY_PIPELINE --init-data '{"param":"value"}' --no-http

# 启动 HTTP/MCP 服务（默认端口 8866）
python PETP_background.py

# 自定义端口和认证令牌
python PETP_background.py --http-port 9090 --http-token my-secret-token

# 无头 Selenium 浏览器（Chrome 不显示窗口）
python PETP_background.py --run-execution BROWSER_TASK --headless --no-http

# 覆盖日志级别
python PETP_background.py --log-level DEBUG

# GUI 处理器策略：skip（跳过）或 abort（遇到 GUI 任务时失败）
python PETP_background.py --run-execution HAS_GUI_TASK --ui-policy skip --no-http
python PETP_background.py --run-execution HAS_GUI_TASK --ui-policy abort --no-http

# 停止运行中的后台实例
python PETP_background.py --stop
```

<details>
<summary>完整 CLI 参数</summary>

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--run-execution NAME` | — | 启动时运行指定 Execution，然后继续 HTTP 或退出 |
| `--run-pipeline NAME` | — | 启动时运行指定 Pipeline（同名重复调用会被拒绝） |
| `--init-data JSON` | `{}` | 运行前注入 JSON 对象到 `data_chain` |
| `--no-http` | 关 | 立即任务完成后退出（不启动 HTTP 服务） |
| `--headless` | 关 | Selenium 无头浏览器（Docker 中自动启用） |
| `--stop` | — | 通过 PID 停止运行中的后台实例 |
| `--http-port PORT` | `8866` | HTTP/MCP 服务端口 |
| `--http-token TOKEN` | 配置文件 | HTTP API 的 Bearer 认证令牌 |
| `--ui-policy {skip,abort}` | `skip` | `skip`：静默跳过 GUI 任务；`abort`：遇到 GUI 任务则失败 |
| `--log-level LEVEL` | 配置文件 | `DEBUG`、`INFO`、`WARNING`、`ERROR` |
| `--nogui-enabled {true,false}` | `true` | 设为 `false` 则后台模式立即退出 |

</details>

**说明：**
- `--run-execution` 和 `--run-pipeline` 可组合使用——两者按顺序执行
- Pipeline 防重入保护：同名 Pipeline 正在运行时，第二次调用返回 `{"ok": false, "error": "Pipeline already running"}`
- cron 模式 Pipeline（YAML 中 `cronEnabled: true`）会注册为定时任务而非立即运行

长时间运行可用辅助脚本：`scripts/macos/start_petp.sh` 和 `scripts/windows/start_petp.ps1`。

---

## MCP 与 AI 集成

PETP 通过 Streamable-HTTP（端口 8866）将 Execution 暴露为 MCP 工具。

> **🔒 鉴权 fail-closed。** `petpconfig.yaml` 未设置 `http_request_token` 时,所有受保护端点(`/petp/*`、`/mcp`)返回 `501 Not Configured`。对外暴露(如经 Tailscale Funnel)前必须配置 token,且每次请求通过 `Authorization: Bearer <token>` 头携带。

> **🔒 安全加固（Phase 2）。**
> - **`CMD` processor**：默认走 `shlex.split`（不进 shell）。仅在需要管道/重定向且命令可信时才设 `shell="yes"`。
> - **动态 `_fn` / `lambda_*` 参数**：运行在沙箱里，`__import__`、`open`、`eval`、`exec`、`compile`、`getattr`、`hasattr` 被移除。白名单模块：`re`、`json`、`datetime`、`math`。
> - **加密密码 salt**：通过环境变量 `PETP_SALT` 或 `~/.petp/secret`（POSIX 文件权限 `0600`）覆盖公开默认值。默认 salt 启动时打 WARNING —— 不设自定义 salt，`cryptocode` 密文等同明文。
> - **路径遍历守卫（opt-in)**:设置 `PETP_PATH_ALLOW_ROOTS=/path1:/path2` 后,所有文件 IO processor(`READ_*`、`WRITE_*`、`OPEN_FILE`、`FILE_DELETE`、`UNZIP`)被限制在白名单根目录内。默认关闭——保留现有用绝对路径的 yaml 行为不变。
> - **请求大小限制**:HTTP body 上限 4 MiB(`PETP_MAX_BODY_BYTES`);JSON-RPC 批量数组上限 64 项(`PETP_MAX_BATCH_ITEMS`)。超限直接 `413` / `400`,不再解析 body。
> - **日志脱敏(默认开)**:`process start` / `[Type] input` 日志中,敏感 key(`api_key`、`password`、`token`、`authorization`、`secret`...)的值替换为 `***REDACTED***`。临时调试可设 `PETP_LOG_REDACT=off` 关闭。

**性能优化（无头/Docker 模式）：**
- 共享线程池处理并发工具调用（消除每次请求创建 Executor 的开销）
- 静态模式 Execution 缓存——BG/Docker 完全跳过文件系统 stat/扫描
- Processor 类启动时预加载（消除冷启动延迟）
- 实时任务级 SSE 进度通知（长时间运行的 `tools/call`）
- outputSchema 解析缓存（同一工具重复调用无需重新解析 mcp_desc JSON）

**Claude Code / Cursor / 任何 MCP 客户端：**

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

**HTTP API（无需 MCP 客户端）：**

```bash
# 列出工具
curl -H "Authorization: Bearer $TOKEN" http://localhost:8866/petp/tools

# 触发执行
curl -X POST http://localhost:8866/petp/exec \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"action":"execution","params":{"execution":"MY_EXEC"},"wait_for_result":"true"}'

# 触发 Pipeline（同步等待结果）
curl -X POST http://localhost:8866/petp/exec \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"action":"pipeline","params":{"pipeline":"MY_PIPELINE"},"wait_for_result":"true"}'

# 触发 Pipeline（异步，用 /petp/result 轮询）
curl -X POST http://localhost:8866/petp/exec \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"action":"pipeline","params":{"pipeline":"MY_PIPELINE"},"wait_for_result":"false"}'
```

| 端点 | 说明 |
|------|------|
| `GET /health` | 健康检查 |
| `GET,POST /mcp` | MCP 工具服务器（Streamable-HTTP） |
| `GET /petp/tools` | 列出已暴露的工具 |
| `POST /petp/exec` | 触发 Execution 或 Pipeline |
| `GET /petp/result?request_id=<id>` | 轮询异步结果 |

---

## 打包与 Docker

```bash
# 独立可执行文件
python build/PETP_build.py   # → dist/PETP.app 或 dist/PETP.exe

# Docker（支持 Apple M1 → amd64 交叉编译）
./build/docker_build.sh
docker run --rm -p 8866:8866 petp-background:amd64-local
```

---

## 项目结构

| 目录 | 说明 |
|------|------|
| `core/executions/` | YAML Execution 定义 |
| `core/processors/` | 80+ 处理器实现（每个任务类型一个 `.py`） |
| `core/pipelines/` | YAML Pipeline 定义 |
| `core/runtime/` | 后台运行时逻辑 |
| `httpservice/` | HTTP 服务器与 MCP 处理 |
| `mvp/` | GUI 层（Model-View-Presenter，wxPython） |
| `config/` | 运行时配置（`petpconfig.yaml`） |
| `docs/` | 详细文档（[中文](docs/screenshots_cn.md) / [EN](docs/)） |
| `webapp/` | Flask Web 应用（[文档](./webapp/README.md)） |
| `scripts/` | macOS 与 Windows 启动脚本 |
| `requirements/` | 模块化依赖分组 |
| `build/` | PyInstaller 与 Docker 构建脚本 |
| `tools/` | 维护脚本（迁移、同步） |
| `testcoverage/` | 测试与冒烟脚本（含 `petp_http_endpoints.http` HTTP/MCP 接口测试） |

---

## 常见问题

| 问题 | 解决方案 |
|------|----------|
| `ModuleNotFoundError` | 安装对应的 `requirements/*.txt` 分组 |
| wxPython 导入失败 | 确保 `.whl` 匹配 Python 版本 — 见[快照构建](https://wxpython.org/Phoenix/snapshot-builds/) |
| ChromeDriver 版本不匹配 | 从 [Chrome for Testing](https://googlechromelabs.github.io/chrome-for-testing/) 下载 |
| 端口 8866 被占用 | 修改 `config/petpconfig.yaml` 中的 `http_port` |

---

## 详细文档

| 文档 | 说明 |
|------|------|
| [截图展示](docs/screenshots_cn.md) | 各平台完整截图 |
| [运行模式与脚本](docs/running-modes_cn.md) | 后台模式、Docker、启动脚本、环境变量 |
| [依赖管理](docs/dependencies_cn.md) | 模块化分组、自定义安装、锁定版本 |
| [配置参考](docs/configuration_cn.md) | 配置项、CLI 参数、运行时返回结构 |
| [MCP 与 HTTP API](docs/mcp-integration_cn.md) | 完整 API 参考、MCP Inspector、工具 Schema |
| [Pipeline 与 Cron](docs/pipeline-cron_cn.md) | 定时调度、YAML 格式、示例 |
| [参数迁移](docs/migration_cn.md) | 2026-05 之前用户的重命名指南 |

---

## 致谢

- [wxPython](https://www.wxpython.org/) & [wxGlade](https://wxglade.sourceforge.net/)
- [Selenium](https://selenium-python.readthedocs.io/) & [ChromeDriver](https://googlechromelabs.github.io/chrome-for-testing/)

---

[完整更新日志 →](./CHANGELOG.md)
