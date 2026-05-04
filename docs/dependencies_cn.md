# 依赖管理

PETP 使用模块化依赖结构 — 按处理器类别拆分，便于灵活安装和最小化打包。

---

## 使用 `uv` 安装（推荐）

[`uv`](https://docs.astral.sh/uv/) 是高速 Python 包管理器（比 pip 快 10-100 倍），兼容现有 requirements 文件。

```bash
pip install -U uv

# 方式 A（推荐）：创建并使用虚拟环境
uv venv
uv pip install -r requirements.txt

# 方式 B：显式安装到系统 Python
uv pip install --system -r requirements.txt
```

## 安装配置

```bash
# 完整安装（GUI 桌面）
uv pip install -r requirements.txt

# 后台服务（无 GUI）
uv pip install -r requirements-nogui.txt

# Docker（无头，无浏览器自动化）
uv pip install -r requirements-docker.txt

# 自定义组合
uv pip install -r requirements/core.txt -r requirements/ssh-sftp.txt -r requirements/http-client.txt
```

---

## 依赖分组

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
| `ocr.txt` | OCR 识别 | rapidocr-onnxruntime, numpy, scipy（paddleocr, easyocr 可选） |
| `captcha.txt` | 验证码识别 | ddddocr |
| `javascript.txt` | JS 引擎 | pythonmonkey |
| `video-download.txt` | 视频下载 | pytubefix |
| `http-service.txt` | HTTP 服务器 | fastapi, uvicorn |
| `webapp.txt` | Web 应用 | Flask, flask-httpauth, werkzeug, gunicorn |
| `system-build.txt` | 系统工具 | psutil, pyinstaller |

---

## 锁定版本（`uv pip compile`）

生成固定版本的 requirements 文件，确保可复现构建：

```bash
# 编译单个分组
uv pip compile requirements/core.txt -o requirements/core.lock

# 编译全部
uv pip compile requirements.txt -o requirements.lock
```

---

## 更新依赖

```bash
# 使用 uv
uv pip install --upgrade -r requirements.txt

# 使用 pip
pip list --outdated | grep -v '^\-e' | cut -d = -f 1 | xargs -n1 pip install -U
```
