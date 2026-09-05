# PETP Portable Runtime 设计文档

**日期:** 2026-07-15
**目标:** 把 BG 模式下"在 headless/CF 环境运行一个 Execution"的核心逻辑,整理成一个自包含、可 `cp -r` 迁移到其他 Python 项目、并可部署到 Cloud Foundry 的轻量运行单元 `portable/`。

---

## 1. 背景与动机

PETP 目前只能作为完整仓库运行(GUI `PETP.py` / 后台 `PETP_background.py` / Docker)。业务方希望把"跑一个 Execution"这件事抽出来,做成一个能拷进**其他 Python 项目**、通过 **Python 代码直接调用**、最终**运行在 Cloud Foundry (CF)** 上的轻量单元,主要跑**含 Selenium 浏览器自动化**的 Execution(如 `T_Supplier_Creation`)。

### 关键探索结论(一手验证)

- **引擎已基本解耦**:`Processor` 基类顶层只 import stdlib + `cachetools`;wx 在 `TYPE_CHECKING` 下,运行时是 `Any`。所有重依赖(selenium/pandas/pyautogui)都在**按需动态加载**的 Processor 子类里。
- **`run_execution` 主体不读 `PETPModel` 任何字段**——`BackgroundRuntime(model=None)` 可用(`__init__` 的 `cron_history_max_records` 有 `if model else` 兜底)。`__m`/`__p` 注入对 BG 纯逻辑路径无消费者。
- **i18n 不在 run_execution 热路径**。
- **仅有的结构性耦合**:①cwd 硬编码路径(`os.path.realpath('.')` / `realpath('core')`)②Processor 从磁盘文件动态加载 ③`BackgroundRuntime` 顶层 `from httpservice.constants import HTTP_RESPONSE_KEY`。

### 已确认的决策(来自 brainstorming)

| 决策点 | 选择 |
|---|---|
| 运行单元形态 | 可移植目录模板(`cp -r`),放主 repo 根目录 |
| 调用方式 | Python 代码直接调用 `run(name, init_data) -> dict` |
| 目标场景 | 含 Selenium 浏览器自动化 |
| Processor 集合 | 全拷(77 个,排除 4 个 GUI 专属) |
| 路径解耦 | 约定 cwd(`petp_run.py` 内 `os.chdir` 到自身目录),零改动路径逻辑 |
| 防 stale | 手工拷 + `sync_portable.py` 一键同步脚本 |
| 部署环境 | Cloud Foundry (`cflinuxfs4`,基于 Ubuntu 22.04 / glibc 2.35) |
| Chrome 来源 | 二进制随 portable 分发;`.so` 系统库靠 CF `apt-buildpack` |
| Chrome 版本 | **Chrome for Testing (CfT)** linux64(glibc ≤2.35,兼容 CF);本地测试用 mac-arm64 `chrome-headless-shell` |

### 关键技术风险(已规避)

**Docker 里 apt 装的 chromium 不能直接搬到 CF。** 实测:Docker 内 chromium 为 **Debian 13 trixie 构建,依赖 glibc 2.41**;CF `cflinuxfs4` 只有 **glibc 2.35**。glibc 不向前兼容,该二进制在 CF 上启动即报 `GLIBC_2.xx not found`,且 apt-buildpack 无法替换 glibc(rootfs 核心)。因此 chrome 二进制必须选 **CfT linux64**(在 Ubuntu 22.04/glibc 2.35 上验证可跑)。

---

## 2. 目录结构

主 repo 根目录新增 `portable/`(checkin):

```
portable/
├── petp_run.py               # 入口:run(execution_name, init_data={}) -> dict
├── core/
│   ├── processor.py execution.py task.py executionstate.py loop.py pipeline.py
│   ├── constants.py          # 新增:HTTP_RESPONSE_KEY / HTTP_REQUEST_ID_KEY 下沉于此
│   ├── definition/
│   │   ├── __init__.py
│   │   └── yamlro.py
│   ├── runtime/
│   │   ├── __init__.py
│   │   ├── BackgroundRuntime.py
│   │   └── UiProcessorPolicy.py
│   ├── cron/                 # BackgroundRuntime 顶层 import,带上(不启用 cron)
│   │   ├── __init__.py  cron.py  cron_history.py  runnableascron.py
│   ├── processors/           # 全拷,排除 4 个 GUI 专属(见 §5)
│   │   └── sub/              # llm/ dbprocessors/ 等子目录一并拷
│   ├── executions/           # 业务 YAML(初始放 1 个 smoke 样例)
│   └── __init__.py
├── utils/                    # 整个 utils/ 全拷(轻量纯 py)
├── mvp/presenter/event/      # 仅 PETPEvent.py + __init__.py 链(满足 execution.py 顶层 import)
├── webdriver/
│   ├── linux/                # CF 用:chrome-headless-shell + chromedriver (linux64, CfT)
│   └── darwin/               # 本地测试用:chrome-headless-shell + chromedriver (mac-arm64)
├── config/petpconfig.yaml    # 最小配置(仅 application 段必要键)
├── requirements.txt          # core + web-automation 子集
├── manifest.yml              # CF push 清单
├── apt.yml                   # CF apt-buildpack:chrome 所需系统 .so 库
├── sync_portable.py          # 一键从主 repo 重拷(防 stale)
└── README.md                 # 用法 + chrome 二进制获取步骤 + "改主 repo 后跑 sync" 提醒
```

**目录命名说明**:`webdriver/<system>/` 中 `<system>` 取值需与 `OSUtils.get_system()` 返回值一致(`linux` / `darwin` / `win32`),以命中现有 `_resolve_chromedriver_path()` 的 bundled 查找逻辑。

---

## 3. 主 repo 改动(唯二两处,均向后兼容)

portable 的可移植性依赖对主 repo 的两处最小改动。**这两处改在主 repo 源文件上,不是只改 portable 副本**——这样 `sync_portable.py` 拷过去后天然带有该能力,且主 repo 的 Docker/桌面模式行为不变。

### 改动 A:`utils/SeleniumUtil.py` — chrome 二进制定位 + headless-shell 参数适配

**A1. 新增 `_resolve_chrome_binary()`**(静态方法),优先级:
1. 环境变量 `PETP_CHROME_BINARY`(显式路径,最高优先)
2. bundled:`webdriver/<system>/chrome-headless-shell` 或 `webdriver/<system>/chrome`(两个名都试,命中即用)
3. 都没有 → 返回 `None`(维持现状:不设 `binary_location`,selenium 自动查找)

**A2. `get_webdriver4_chrome()` 内应用**(当前 `utils/SeleniumUtil.py:73` `options = webdriver.ChromeOptions()` 之后):
```python
chrome_bin = SeleniumUtil._resolve_chrome_binary()
if chrome_bin:
    options.binary_location = chrome_bin
```

**A3. headless-shell 参数适配**(改当前 `utils/SeleniumUtil.py:76-82` 的 headless 分支):
`chrome-headless-shell` 本身即 headless 二进制,**不能再加 `--headless=new`**(会异常)。逻辑改为:
```python
if SeleniumUtil.is_running_in_docker() or os.environ.get('PETP_HEADLESS', '').lower() == 'true':
    is_headless_shell = bool(chrome_bin) and 'headless-shell' in os.path.basename(chrome_bin)
    if not is_headless_shell:
        options.add_argument('--headless=new')   # 完整 chrome 才需要
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
else:
    options.add_argument("--start-maximized")
```

**向后兼容验证**:Docker/桌面模式无 `PETP_CHROME_BINARY` 且无 bundled chrome → `chrome_bin=None` → 不设 `binary_location`、`is_headless_shell=False` → 走原 `--headless=new` 路径,行为完全不变。

### 改动 B:`HTTP_RESPONSE_KEY` 常量下沉,切断 `core → httpservice` 反向依赖

- **新增 `core/constants.py`**:定义 `HTTP_RESPONSE_KEY` 与 `HTTP_REQUEST_ID_KEY`(值与现 `httpservice/constants.py` 一致)。
- **`httpservice/constants.py`** 改为 re-export:`from core.constants import HTTP_RESPONSE_KEY, HTTP_REQUEST_ID_KEY`(保持 `from httpservice.constants import ...` 的所有现有调用点不变)。
- **`core/runtime/BackgroundRuntime.py:17`** 改 `from core.constants import HTTP_RESPONSE_KEY`。
- **`core/processors/HTTP_RESPONSE_KEYProcessor.py:4`** 同样改为 `from core.constants import HTTP_RESPONSE_KEY`。

这样 portable 只需带 `core/constants.py`,无需带整个 `httpservice/` 包。

> 注:`core/execution.py:25` 的 `from mvp.presenter.event.PETPEvent import PETPEvent` 顶层 import 保留不动——因为该 import 对无 wx 环境已优雅降级(`PETPEvent` 有纯 Python fallback),BG 路径不调用 `Execution.run()`/`post_log_reload()`。portable 通过在 `sync_portable.py` 中一并拷入一个**最小 `mvp/presenter/event/PETPEvent.py` 及其 `__init__.py` 链**来满足该 import(仅这一个文件,不带整个 mvp),避免改动主 repo 的顶层 import 结构。

---

## 4. `petp_run.py` 入口契约

```python
"""PETP Portable Runtime entry. Copy the whole portable/ dir into your project."""
import os, sys
_HERE = os.path.dirname(os.path.realpath(__file__))
os.chdir(_HERE)                       # 让所有 realpath('.')/realpath('core') 落到 portable/
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from core.runtime.BackgroundRuntime import BackgroundRuntime


def run(execution_name: str, init_data: dict = None) -> dict:
    """Run one Execution headlessly. Returns {"ok","data","error","meta"}."""
    os.environ.setdefault('PETP_HEADLESS', 'true')   # CF/headless 无显示器
    runtime = BackgroundRuntime(model=None)
    return runtime.run_execution(execution_name, init_data or {})


if __name__ == '__main__':
    import json
    name = sys.argv[1] if len(sys.argv) > 1 else 'SMOKE_TEST'
    data = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    print(json.dumps(run(name, data), ensure_ascii=False, default=str))
```

**调用方(其他项目)用法:**
```python
from portable.petp_run import run
result = run("T_Supplier_Creation", {"supplier_name": "ACME"})
if result["ok"]:
    ...
```

返回结构(来自 `BackgroundRuntime._result()`):`{"ok": bool, "data": {...}, "error": str|None, "meta": {"duration_ms","skipped_tasks",...}}`。

---

## 5. Processor 全拷 + 排除清单

拷 `core/processors/` 全部 77 个 `*Processor.py`(含 `sub/` 子目录),**排除 4 个 GUI 专属**(顶层裸 `import pyautogui`,无 X11 会崩):
- `FILE_CHOOSERProcessor.py`
- `MOUSE_CLICKProcessor.py`
- `MOUSE_POSITIONProcessor.py`
- `MOUSE_SCROLLProcessor.py`

**保留**含 `try: import wx` 的 Processor(`MATPLOTLIB`/`INPUT_DIALOG`/`SHOW_RESULT`/`RELOAD_LOG`)——BG 下 `view=None` 自动降级为 log,不崩。

`UiProcessorPolicy._PURE_GUI_TYPES` 当前只含 `FILE_CHOOSER`;portable 中即使 YAML 误引用被排除的 MOUSE_* 类型,会因文件不存在在 `get_processor_by_type` 抛 `FileNotFoundError`——可接受(明确报错优于静默)。

---

## 6. CF 部署产物

### `requirements.txt`
```
pyyaml
cachetools
python-dateutil
cryptocode
croniter
selenium
urllib3
Pillow
requests          # 若 execution 用 HTTP_REQUEST
```
(按目标 execution 实际用到的 Processor 增补,如 openpyxl/pandas/paramiko。)

### `apt.yml`(apt-buildpack,只装 chrome 所需系统 .so 库,不装 chrome 本身)
基于 §CF chrome-headless-shell 的 `ldd` 外部依赖,声明包:
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
> apt-buildpack 装到 `/home/vcap/deps/<idx>/apt/usr/lib/...`,CF staging 自动把这些目录加入运行时 `LD_LIBRARY_PATH`。最终库清单以 CF 上 `chrome-headless-shell` 实际启动报错为准迭代补齐(见 §7 CF 验证)。

### `manifest.yml`
```yaml
---
applications:
  - name: petp-portable-runner
    memory: 2G
    disk_quota: 2G
    buildpacks:
      - https://github.com/cloudfoundry/apt-buildpack
      - python_buildpack
    command: python your_app_entry.py          # 调用方自己的入口(内部 import portable.petp_run)
    env:
      PETP_HEADLESS: "true"
      PETP_CHROME_BINARY: webdriver/linux/chrome-headless-shell
```
> `disk_quota` ≥ 2G 因 chrome-headless-shell 二进制 ~160MB + chromedriver + 库。

### chrome 二进制获取(README 记录,不 checkin 大二进制到 git 的话可用 CF blobstore / 打包上传)
- **CF (linux64)**:从 `https://googlechromelabs.github.io/chrome-for-testing/` 下 `chrome-headless-shell-linux64` + 匹配版本 `chromedriver-linux64`,解压后放 `portable/webdriver/linux/`(保留整目录资源,二进制置于该目录下)。
- **本地 (mac-arm64)**:已下载于 `download/chrome-headless-shell-mac-arm64.zip` + `download/chromedriver-mac-arm64.zip`,解压放 `portable/webdriver/darwin/`。
- chrome 与 chromedriver **主版本号必须一致**。

---

## 7. `sync_portable.py`(防 stale)

从主 repo 按**显式清单**重拷到 `portable/`,拷完做 import smoke check。

**拷贝(覆盖)清单:**
- `core/{processor,execution,task,executionstate,loop,pipeline,constants}.py`
- `core/definition/`、`core/runtime/`、`core/cron/`
- `core/processors/**`(排除 §5 的 4 个文件)
- `utils/**`(全拷)
- 最小 `mvp/presenter/event/PETPEvent.py` 及其 `__init__.py` 链(满足 execution.py 顶层 import)

**不覆盖(portable 私有,sync 跳过):**
- `portable/core/executions/`(业务 YAML)
- `portable/webdriver/`(二进制)
- `portable/config/petpconfig.yaml`
- `portable/{manifest.yml, apt.yml, requirements.txt, petp_run.py, README.md}`

**smoke check**:sync 后 `cd portable && python -c "import petp_run"`(验证 import 闭包完整,无缺文件)。

---

## 8. 验证策略

1. **本地功能**:解压 mac-arm64 二进制到 `portable/webdriver/darwin/`,`PETP_CHROME_BINARY=webdriver/darwin/chrome-headless-shell python portable/petp_run.py SMOKE_TEST` → 返回 `{"ok": true, ...}`。再跑一个真实 Selenium execution(如 `GO_TO_PAGE` + `FIND_THEN_CLICK`)验证浏览器起得来、能点击。
2. **主 repo 回归**:改动 A/B 后,`python -m pytest testcoverage/ -q` 仍全绿(329 测试),证明 SeleniumUtil / constants 改动向后兼容。
3. **sync 幂等**:连跑两次 `python portable/sync_portable.py`,第二次 diff 为空(业务 YAML/二进制未被覆盖)。
4. **CF 部署**:`cf push` 后调用一次含 Selenium 的 execution,验证 chrome-headless-shell 在 CF 上启动成功(无 `GLIBC`/`cannot open shared object file` 报错);若报缺库,按报错补 `apt.yml` 迭代。

---

## 9. 风险与权衡

| 风险 | 缓解 |
|---|---|
| portable 副本与主 repo stale | `sync_portable.py` 一键重拷 + README 提醒;主 repo 是单一事实源 |
| CF rootfs 缺 chrome 运行库 | `apt.yml` 声明,按实际报错迭代补齐 |
| chrome-headless-shell 特性受限(扩展/复杂 prefs) | 目标是点击/填表类自动化,足够;若需完整 chrome,改下 `chrome-linux64` 并去掉 headless-shell 参数分支 |
| 大二进制入 git | README 建议:二进制不入 git,push 时随 CF 上传或走 blobstore;git 仅存获取脚本 |
| 被排除的 MOUSE_*/FILE_CHOOSER 被 YAML 引用 | `get_processor_by_type` 抛 FileNotFoundError,明确报错 |

---

## 10. 关键文件清单

**主 repo 改动:**
- `utils/SeleniumUtil.py`(改 `get_webdriver4_chrome` + 新增 `_resolve_chrome_binary`)
- `core/constants.py`(**新增**)
- `httpservice/constants.py`(改为 re-export)
- `core/runtime/BackgroundRuntime.py:17`(改 import)
- `core/processors/HTTP_RESPONSE_KEYProcessor.py:4`(改 import)

**portable/ 新增(全部 checkin,二进制除外):**
- `portable/petp_run.py`、`portable/sync_portable.py`、`portable/README.md`
- `portable/config/petpconfig.yaml`、`portable/requirements.txt`
- `portable/manifest.yml`、`portable/apt.yml`
- `portable/core/**`、`portable/utils/**`、`portable/webdriver/**`(由 sync 脚本填充引擎/utils;二进制手动放)
