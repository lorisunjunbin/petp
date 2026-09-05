# PETP Portable Runtime Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把 BG 模式运行 Execution 的核心逻辑整理成一个自包含、可 `cp -r` 迁移、可部署到 Cloud Foundry 的 `portable/` 运行单元。

**Architecture:** 主 repo 做两处向后兼容的最小改动(SeleniumUtil 的 chrome 二进制定位 + HTTP_RESPONSE_KEY 常量下沉),然后建 `portable/` 目录:一个 `os.chdir` 到自身目录的入口 `petp_run.py`(约定 cwd,零改动路径逻辑)、一个从主 repo 按显式清单重拷的 `sync_portable.py`(防 stale)、以及 CF 部署产物(manifest.yml/apt.yml/requirements.txt)。

**Tech Stack:** Python 3.14, selenium, Chrome for Testing (headless-shell), Cloud Foundry apt-buildpack + python-buildpack。

## Global Constraints

- 主 repo 改动必须**向后兼容**:Docker/桌面模式无 `PETP_CHROME_BINARY`、无 bundled chrome 时行为完全不变。
- 主 repo 现有测试(329)在改动后必须全绿。
- 测试运行方式:自定义 runner `python testcoverage/<name>.py`(exit 0 = pass),**不是** pytest。新测试沿用此风格。
- `chrome-headless-shell` 二进制**不能加** `--headless=new` 参数(它本身即 headless)。
- `webdriver/<system>/` 的 `<system>` = `OSUtils.get_system()` = `sys.platform`(`linux` / `darwin` / `win32`)。
- CF chrome 必须用 **Chrome for Testing linux64**(glibc ≤2.35);Docker 里 apt 的 chromium(glibc 2.41)不可用于 CF。
- 排除的 4 个 GUI 专属 processor:`FILE_CHOOSER`, `MOUSE_CLICK`, `MOUSE_POSITION`, `MOUSE_SCROLL`。
- 遵循项目 CLAUDE.md §5:每个 Task 末尾的 commit 步骤须先获用户同意后执行(实现者按 subagent-driven 流程时由 controller 处理)。

---

## File Structure

**主 repo 改动:**
- `core/constants.py`(新增)— 定义 `HTTP_RESPONSE_KEY` / `HTTP_REQUEST_ID_KEY`,作为常量单一来源。
- `httpservice/constants.py`(改)— re-export from `core.constants`,保持现有调用点不变。
- `core/runtime/BackgroundRuntime.py`(改 import)。
- `core/processors/HTTP_RESPONSE_KEYProcessor.py`(改 import)。
- `utils/SeleniumUtil.py`(改)— 新增 `_resolve_chrome_binary()`,`get_webdriver4_chrome()` 应用 binary_location + headless-shell 参数适配。

**portable/ 新增:**
- `portable/petp_run.py` — 入口 `run(name, init_data) -> dict`。
- `portable/sync_portable.py` — 从主 repo 重拷引擎/utils/事件类。
- `portable/config/petpconfig.yaml`、`requirements.txt`、`manifest.yml`、`apt.yml`、`README.md`。
- `portable/core/**`、`portable/utils/**`、`portable/mvp/presenter/event/PETPEvent.py`(由 sync 填充)。
- `portable/webdriver/{linux,darwin}/`(二进制手动放)。

---

### Task 1: `HTTP_RESPONSE_KEY` 常量下沉到 core

切断 `core.runtime → httpservice` 反向依赖,使 portable 无需带 httpservice 包。

**Files:**
- Create: `core/constants.py`
- Modify: `httpservice/constants.py`
- Modify: `core/runtime/BackgroundRuntime.py:17`
- Modify: `core/processors/HTTP_RESPONSE_KEYProcessor.py:4`
- Test: `testcoverage/test_portable_constants.py`

**Interfaces:**
- Produces: `core.constants.HTTP_RESPONSE_KEY == '__http_response_key__'`, `core.constants.HTTP_REQUEST_ID_KEY == '__http_request_id__'`。

- [ ] **Step 1: 写失败测试**

`testcoverage/test_portable_constants.py`:
```python
"""Verify HTTP_RESPONSE_KEY constant sunk into core and re-exported.
Run: python testcoverage/test_portable_constants.py  (exit 0 = pass)
"""
import os, sys
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


def test_core_constants_defined():
    from core.constants import HTTP_RESPONSE_KEY, HTTP_REQUEST_ID_KEY
    assert HTTP_RESPONSE_KEY == '__http_response_key__'
    assert HTTP_REQUEST_ID_KEY == '__http_request_id__'


def test_httpservice_reexports_same_object():
    from core.constants import HTTP_RESPONSE_KEY as core_k
    from httpservice.constants import HTTP_RESPONSE_KEY as http_k
    assert core_k == http_k


if __name__ == '__main__':
    fails = 0
    for name, fn in list(globals().items()):
        if name.startswith('test_') and callable(fn):
            try:
                fn(); print(f'PASS {name}')
            except Exception as e:
                fails += 1; print(f'FAIL {name}: {e}')
    sys.exit(1 if fails else 0)
```

- [ ] **Step 2: 跑测试确认失败**

Run: `python testcoverage/test_portable_constants.py`
Expected: FAIL — `ModuleNotFoundError: No module named 'core.constants'`

- [ ] **Step 3: 新建 `core/constants.py`**

```python
# Shared string constants used across engine, runtime and HTTP layer.
# Sunk here (from httpservice) so core.runtime need not import httpservice.
HTTP_RESPONSE_KEY = '__http_response_key__'
HTTP_REQUEST_ID_KEY = '__http_request_id__'
```

- [ ] **Step 4: `httpservice/constants.py` 改为 re-export**

整个文件替换为:
```python
# Re-export from core.constants (single source of truth) for backward compatibility.
from core.constants import HTTP_RESPONSE_KEY, HTTP_REQUEST_ID_KEY  # noqa: F401
```

- [ ] **Step 5: 改 `core/runtime/BackgroundRuntime.py:17`**

将
```python
from httpservice.constants import HTTP_RESPONSE_KEY
```
改为
```python
from core.constants import HTTP_RESPONSE_KEY
```

- [ ] **Step 6: 改 `core/processors/HTTP_RESPONSE_KEYProcessor.py:4`**

将
```python
from httpservice.constants import HTTP_RESPONSE_KEY
```
改为
```python
from core.constants import HTTP_RESPONSE_KEY
```

- [ ] **Step 7: 跑新测试 + 回归**

Run: `python testcoverage/test_portable_constants.py`
Expected: PASS (both)

Run: `python testcoverage/test_bg_runtime.py`
Expected: exit 0(BackgroundRuntime import 链完整,HTTP_RESPONSE_KEY 逻辑不变)

- [ ] **Step 8: Commit**（先经用户同意）

```bash
git add core/constants.py httpservice/constants.py core/runtime/BackgroundRuntime.py core/processors/HTTP_RESPONSE_KEYProcessor.py testcoverage/test_portable_constants.py
git commit -m "refactor: sink HTTP_RESPONSE_KEY into core.constants (decouple core from httpservice)"
```

---

### Task 2: `SeleniumUtil` chrome 二进制定位 + headless-shell 适配

让 selenium 能用 bundled / env 指定的 chrome(headless-shell 兼容),CF 上才能起浏览器。

**Files:**
- Modify: `utils/SeleniumUtil.py`(新增 `_resolve_chrome_binary`;改 `get_webdriver4_chrome` 的 `:73-84` 区段)
- Test: `testcoverage/test_selenium_chrome_binary.py`

**Interfaces:**
- Consumes: `os.environ['PETP_CHROME_BINARY']`(可选);bundled `webdriver/<system>/{chrome-headless-shell,chrome}`。
- Produces: `SeleniumUtil._resolve_chrome_binary() -> str | None`(返回二进制绝对路径或 None)。

- [ ] **Step 1: 写失败测试**

`testcoverage/test_selenium_chrome_binary.py`:
```python
"""Verify chrome binary resolution: env > bundled > None.
Run: python testcoverage/test_selenium_chrome_binary.py  (exit 0 = pass)
NOTE: does not launch Chrome — only tests path resolution logic.
"""
import os, sys, tempfile
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
from utils.SeleniumUtil import SeleniumUtil


def test_env_takes_priority():
    os.environ['PETP_CHROME_BINARY'] = '/tmp/my-chrome'
    try:
        assert SeleniumUtil._resolve_chrome_binary() == '/tmp/my-chrome'
    finally:
        del os.environ['PETP_CHROME_BINARY']


def test_none_when_nothing_available():
    os.environ.pop('PETP_CHROME_BINARY', None)
    # In a clean checkout there is no webdriver/<system>/chrome* bundled,
    # so resolution must return None (preserving legacy auto-detect).
    assert SeleniumUtil._resolve_chrome_binary() is None


if __name__ == '__main__':
    fails = 0
    for name, fn in list(globals().items()):
        if name.startswith('test_') and callable(fn):
            try:
                fn(); print(f'PASS {name}')
            except Exception as e:
                fails += 1; print(f'FAIL {name}: {e}')
    sys.exit(1 if fails else 0)
```

- [ ] **Step 2: 跑测试确认失败**

Run: `python testcoverage/test_selenium_chrome_binary.py`
Expected: FAIL — `AttributeError: type object 'SeleniumUtil' has no attribute '_resolve_chrome_binary'`

- [ ] **Step 3: 新增 `_resolve_chrome_binary()`**

在 `utils/SeleniumUtil.py` 的 `_resolve_chromedriver_path()`(当前 `:34-51`)之后插入:
```python
    @staticmethod
    def _resolve_chrome_binary():
        """Return the chrome binary path, or None to let selenium auto-detect.
        Priority: env PETP_CHROME_BINARY > bundled webdriver/<system>/{chrome-headless-shell,chrome}.
        """
        env_bin = os.environ.get('PETP_CHROME_BINARY')
        if env_bin:
            return env_bin
        base = os.path.realpath('webdriver') + os.sep + OSUtils.get_system() + os.sep
        for name in ('chrome-headless-shell', 'chrome'):
            candidate = base + name + ('.exe' if OSUtils.get_system() == 'win32' else '')
            if os.path.isfile(candidate):
                return candidate
        return None
```

- [ ] **Step 4: 跑测试确认通过**

Run: `python testcoverage/test_selenium_chrome_binary.py`
Expected: PASS (both)

- [ ] **Step 5: `get_webdriver4_chrome` 应用 binary_location + headless-shell 适配**

将 `utils/SeleniumUtil.py:73-84`（从 `options = webdriver.ChromeOptions()` 到 headless `else` 分支结束）替换为:
```python
        options = webdriver.ChromeOptions()

        chrome_bin = SeleniumUtil._resolve_chrome_binary()
        if chrome_bin:
            options.binary_location = chrome_bin

        # Auto-enable headless mode in Docker / headless environments
        if SeleniumUtil.is_running_in_docker() or os.environ.get('PETP_HEADLESS', '').lower() == 'true':
            logging.info('Headless mode enabled (Docker or PETP_HEADLESS=true)')
            # chrome-headless-shell is already headless — passing --headless=new errors.
            is_headless_shell = bool(chrome_bin) and 'headless-shell' in os.path.basename(chrome_bin)
            if not is_headless_shell:
                options.add_argument('--headless=new')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
        else:
            options.add_argument("--start-maximized")
```

- [ ] **Step 6: 回归验证（向后兼容）**

Run: `python testcoverage/test_selenium_chrome_binary.py`
Expected: PASS

Run: `python testcoverage/nogui_smoke.py`
Expected: exit 0（ENDECODER 不碰浏览器,SeleniumUtil 改动不影响它;此步确认无 import 破坏）

- [ ] **Step 7: Commit**（先经用户同意）

```bash
git add utils/SeleniumUtil.py testcoverage/test_selenium_chrome_binary.py
git commit -m "feat: SeleniumUtil resolves bundled/env chrome binary with headless-shell support"
```

---

### Task 3: `portable/` 骨架 + 入口 `petp_run.py` + sync 脚本

建 portable 目录、入口、同步脚本,并首次填充引擎/utils。

**Files:**
- Create: `portable/petp_run.py`
- Create: `portable/sync_portable.py`
- Create: `portable/config/petpconfig.yaml`
- Create: `portable/core/executions/SMOKE_TEST.yaml`
- Create: `portable/.gitignore`
- Test: 通过 `sync_portable.py` 自带的 import smoke check + 手动跑 SMOKE_TEST

**Interfaces:**
- Consumes: 主 repo 的 `core/**`, `utils/**`, `mvp/presenter/event/PETPEvent.py`（Task 1/2 改动后的版本）。
- Produces: `portable.petp_run.run(execution_name: str, init_data: dict = None) -> dict`。

- [ ] **Step 1: 写 `sync_portable.py`**（它是"测试"的一部分——末尾做 import smoke check)

`portable/sync_portable.py`:
```python
"""Sync engine/utils from the main repo into portable/ (prevents stale copies).
Run from repo root:  python portable/sync_portable.py
Overwrites engine code; never touches portable/core/executions, webdriver/, or CF config.
"""
import os, shutil, sys, subprocess

PORTABLE = os.path.dirname(os.path.realpath(__file__))
REPO = os.path.dirname(PORTABLE)

EXCLUDE_PROCESSORS = {
    'FILE_CHOOSERProcessor.py', 'MOUSE_CLICKProcessor.py',
    'MOUSE_POSITIONProcessor.py', 'MOUSE_SCROLLProcessor.py',
}

# (src_rel, dst_rel) directories copied wholesale
COPY_DIRS = [
    ('core/definition', 'core/definition'),
    ('core/runtime', 'core/runtime'),
    ('core/cron', 'core/cron'),
    ('utils', 'utils'),
]
# individual engine files (copied verbatim from main repo).
# NOTE: PETP uses implicit namespace packages (PEP 420) — the repo ships almost
# no __init__.py. portable/ relies on the same mechanism (petp_run.py puts
# portable/ on sys.path), so we neither copy nor create __init__.py files.
COPY_FILES = [
    'core/processor.py', 'core/execution.py', 'core/task.py',
    'core/executionstate.py', 'core/loop.py', 'core/pipeline.py', 'core/constants.py',
    'mvp/presenter/event/PETPEvent.py',
]


def _copy_file(rel):
    src = os.path.join(REPO, rel)
    dst = os.path.join(PORTABLE, rel)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)


def _copy_dir(src_rel, dst_rel):
    src = os.path.join(REPO, src_rel)
    dst = os.path.join(PORTABLE, dst_rel)
    if os.path.isdir(dst):
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def _copy_processors():
    src = os.path.join(REPO, 'core/processors')
    dst = os.path.join(PORTABLE, 'core/processors')
    if os.path.isdir(dst):
        shutil.rmtree(dst)
    def ignore(dirpath, names):
        return {n for n in names if n in EXCLUDE_PROCESSORS or n == '__pycache__'}
    shutil.copytree(src, dst, ignore=ignore)


def main():
    for rel in COPY_FILES:
        _copy_file(rel)
    for s, d in COPY_DIRS:
        _copy_dir(s, d)
    _copy_processors()
    print('sync: engine/utils copied.')

    # import smoke check — verifies the closure is complete
    r = subprocess.run([sys.executable, '-c', 'import petp_run'],
                       cwd=PORTABLE, capture_output=True, text=True)
    if r.returncode != 0:
        print('SMOKE IMPORT FAILED:\n' + r.stderr)
        sys.exit(1)
    print('sync: import smoke check PASS.')


if __name__ == '__main__':
    main()
```

- [ ] **Step 2: 写入口 `portable/petp_run.py`**

```python
"""PETP Portable Runtime entry. Copy the whole portable/ dir into your project.

    from portable.petp_run import run
    result = run("T_Supplier_Creation", {"supplier_name": "ACME"})
"""
import os, sys

_HERE = os.path.dirname(os.path.realpath(__file__))
os.chdir(_HERE)                       # make realpath('.')/realpath('core') land in portable/
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from core.runtime.BackgroundRuntime import BackgroundRuntime


def run(execution_name: str, init_data: dict = None) -> dict:
    """Run one Execution headlessly. Returns {"ok","data","error","meta"}."""
    os.environ.setdefault('PETP_HEADLESS', 'true')
    runtime = BackgroundRuntime(model=None)
    return runtime.run_execution(execution_name, init_data or {})


if __name__ == '__main__':
    import json
    name = sys.argv[1] if len(sys.argv) > 1 else 'SMOKE_TEST'
    data = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    print(json.dumps(run(name, data), ensure_ascii=False, default=str))
```

- [ ] **Step 3: 写 `portable/config/petpconfig.yaml`**（最小配置）

```yaml
application:
  app_name: petp-portable
  language: en
  log_level: INFO
  nogui_enabled: true
  nogui_ui_processor_policy: skip
  cron_history_max_records: 500
```

- [ ] **Step 4: 写 smoke execution `portable/core/executions/SMOKE_TEST.yaml`**

（复用 ENDECODER 逻辑,纯 base64 编码,无浏览器）
```yaml
!!python/object:core.execution.Execution
astool: false
execution: SMOKE_TEST
list:
- !!python/object:core.task.Task
  input: '{"type": "ENCODE", "inbound": "petp-portable", "outbound_key": "result", "algorithms": "base64"}'
  skipped: false
  type: ENCODE_DECODE_STR
loops: []
```

- [ ] **Step 5: 写 `portable/.gitignore`**

```
__pycache__/
*.pyc
webdriver/*/chrome-headless-shell
webdriver/*/chromedriver
download/
log/
```

- [ ] **Step 6: 首次同步并做 import smoke check**

Run: `python portable/sync_portable.py`
Expected: 输出 `sync: engine/utils copied.` 然后 `sync: import smoke check PASS.`，exit 0

- [ ] **Step 7: 跑 SMOKE_TEST execution 验证端到端**

Run: `python portable/petp_run.py SMOKE_TEST`
Expected: stdout 是 JSON,含 `"ok": true` 且 `data.result` 为 `petp-portable` 的 base64（`cGV0cC1wb3J0YWJsZQ==`）

- [ ] **Step 8: Commit**（先经用户同意）

```bash
git add portable/petp_run.py portable/sync_portable.py portable/config/petpconfig.yaml portable/core/executions/SMOKE_TEST.yaml portable/.gitignore
git commit -m "feat: portable runtime skeleton (entry + sync script + smoke execution)"
```

> 注:`portable/core/**`、`portable/utils/**`、`portable/mvp/**` 由 sync 脚本生成。是否将这些生成物一并 checkin，见 Task 5 的 README 说明与团队约定;本 commit 只提交手写的骨架文件。

---

### Task 4: CF 部署产物（manifest.yml / apt.yml / requirements.txt）

让 portable 可 `cf push`。此 Task 无自动化测试（CF 部署需真实环境），交付物是可用的部署配置 + README 中的验证步骤。

**Files:**
- Create: `portable/requirements.txt`
- Create: `portable/apt.yml`
- Create: `portable/manifest.yml`

**Interfaces:**
- Consumes: `portable/petp_run.py`（调用方 import 它）。
- Produces: `cf push` 可用的三件套。

- [ ] **Step 1: 写 `portable/requirements.txt`**

```
pyyaml
cachetools
python-dateutil
cryptocode
croniter
selenium
urllib3
Pillow
requests
```

- [ ] **Step 2: 写 `portable/apt.yml`**（apt-buildpack,只装 chrome 所需系统 .so 库）

```yaml
---
packages:
  - libnss3
  - libnspr4
  - libgbm1
  - libasound2
  - libxkbcommon0
  - libxcomposite1
  - libxdamage1
  - libxfixes3
  - libxrandr2
  - libatk1.0-0
  - libatk-bridge2.0-0
  - libcups2
  - libdbus-1-3
  - libdrm2
  - libpango-1.0-0
  - libcairo2
  - libatspi2.0-0
  - libx11-xcb1
  - libxext6
  - libxi6
  - libxrender1
  - libfontconfig1
  - libfreetype6
```

- [ ] **Step 3: 写 `portable/manifest.yml`**

```yaml
---
applications:
  - name: petp-portable-runner
    memory: 2G
    disk_quota: 2G
    buildpacks:
      - https://github.com/cloudfoundry/apt-buildpack
      - python_buildpack
    command: python petp_run.py SMOKE_TEST
    env:
      PETP_HEADLESS: "true"
      PETP_CHROME_BINARY: webdriver/linux/chrome-headless-shell
```

> `command` 默认跑 SMOKE_TEST 便于首次 push 验证;实际使用时改为调用方入口（如 `python your_app.py`）。

- [ ] **Step 4: 本地验证 requirements 可解析**

Run: `python -c "import pathlib; [print(l) for l in pathlib.Path('portable/requirements.txt').read_text().splitlines() if l.strip()]"`
Expected: 逐行打印 9 个包名,无异常

- [ ] **Step 5: Commit**（先经用户同意）

```bash
git add portable/requirements.txt portable/apt.yml portable/manifest.yml
git commit -m "feat: Cloud Foundry deploy artifacts for portable runtime (manifest/apt/requirements)"
```

---

### Task 5: `portable/README.md`（用法 + 二进制获取 + 防 stale 约定）

交付物是文档;验证方式是文档步骤可被跟随执行。

**Files:**
- Create: `portable/README.md`

- [ ] **Step 1: 写 README**

`portable/README.md`:
````markdown
# PETP Portable Runtime

自包含的 PETP Execution 运行单元,可 `cp -r portable/` 到任意 Python 项目,
或 `cf push` 到 Cloud Foundry。跑 headless(含 Selenium 浏览器自动化)。

## 用法(Python 代码调用)

```python
from portable.petp_run import run
result = run("YOUR_EXECUTION", {"key": "value"})
# result: {"ok": bool, "data": {...}, "error": str|None, "meta": {...}}
```

命令行:`python portable/petp_run.py SMOKE_TEST`

## Chrome 二进制(必须手动放置)

**不入 git**(见 .gitignore)。用 Chrome for Testing,chrome 与 chromedriver 主版本号必须一致。

- **CF (linux64)**:从 https://googlechromelabs.github.io/chrome-for-testing/ 下
  `chrome-headless-shell-linux64` + 匹配版本 `chromedriver-linux64`,解压后把
  **整个目录内容**放到 `portable/webdriver/linux/`(保留 .pak/.dat/locales 等资源,
  `chrome-headless-shell` 与 `chromedriver` 二进制置于该目录)。
- **本地 (mac-arm64)**:解压仓库 `download/chrome-headless-shell-mac-arm64.zip` +
  `download/chromedriver-mac-arm64.zip` 到 `portable/webdriver/darwin/`。

`PETP_CHROME_BINARY` 环境变量可覆盖自动查找(指向二进制绝对/相对路径)。

## 保持与主 repo 同步(防 stale)

引擎代码(`core/`、`utils/`、事件类)是主 repo 的**拷贝**。主 repo 改了这些后,
从 repo 根运行:

```bash
python portable/sync_portable.py
```

它会重拷引擎/utils 并做 import smoke check。**不会**覆盖你的
`core/executions/`、`webdriver/`、`config/`、CF 配置。

## Cloud Foundry 部署

```bash
cd portable
cf push
```

`manifest.yml` 用 apt-buildpack(装 chrome 所需 .so,见 `apt.yml`)+ python-buildpack。
若 push 后 chrome 启动报 `cannot open shared object file: libXXX.so`,把对应包名加进
`apt.yml` 重新 push。若报 `GLIBC_2.xx not found`,说明 chrome 二进制不是 linux64/glibc≤2.35
版本——换用 Chrome for Testing linux64。

## 已排除的 Processor

`FILE_CHOOSER`、`MOUSE_CLICK`、`MOUSE_POSITION`、`MOUSE_SCROLL`(GUI 专属,headless 无法运行)。
其余 73 个 Processor 全部可用。
````

- [ ] **Step 2: 验证 README 链接与文件引用一致**

Run: `grep -o "portable/[a-z_/.]*" portable/README.md | sort -u`
Expected: 引用的路径(petp_run.py, sync_portable.py, webdriver/linux, webdriver/darwin, apt.yml, manifest.yml, .gitignore)都在 portable/ 中存在

- [ ] **Step 3: Commit**（先经用户同意）

```bash
git add portable/README.md
git commit -m "docs: portable runtime README (usage, chrome binary, CF deploy, sync)"
```

---

## Self-Review

**1. Spec coverage:**
- §2 目录结构 → Task 3(骨架)+ Task 4/5(CF 产物/README);portable/mvp 事件类 → Task 3 sync 清单 ✅
- §3 改动 A(SeleniumUtil)→ Task 2 ✅;改动 B(常量下沉)→ Task 1 ✅
- §4 入口契约 → Task 3 ✅
- §5 Processor 排除清单 → Task 3 sync 的 `EXCLUDE_PROCESSORS` ✅
- §6 CF 产物 → Task 4 ✅
- §7 sync 脚本 → Task 3 ✅
- §8 验证策略 → 各 Task 的回归步骤 + Task 3 端到端 + Task 4/5 CF 步骤 ✅

**2. Placeholder scan:** 无 TBD/TODO;所有 code step 含完整代码;apt.yml 库清单为真实初版(README 写明按报错迭代)。✅

**3. Type consistency:**
- `_resolve_chrome_binary() -> str | None`:Task 2 定义,Task 2 Step 5 使用 ✅
- `run(name, init_data) -> dict`:Task 3 定义,README(Task 5)引用 ✅
- `HTTP_RESPONSE_KEY` 常量:Task 1 定义于 core.constants,Task 1 Step 5/6 引用一致 ✅
- `EXCLUDE_PROCESSORS` 4 个文件名与 §5、Global Constraints 一致 ✅
- SMOKE_TEST base64 期望值 `cGV0cC1wb3J0YWJsZQ==` = base64("petp-portable"),Task 3 Step 7 ✅

无遗漏,无占位符,类型一致。
