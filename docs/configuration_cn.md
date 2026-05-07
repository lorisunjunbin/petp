# 配置参考

运行时配置、CLI 参数和后台模式行为说明。

---

## CLI 参数

| 参数 | 取值 | 默认值 | 说明 |
|------|------|--------|------|
| `--run-execution NAME` | 任意 Execution 名称 | — | 启动时立即运行指定 Execution |
| `--run-pipeline NAME` | 任意 Pipeline 名称 | — | 启动时立即运行指定 Pipeline |
| `--init-data JSON` | JSON 对象字符串 | `{}` | 注入到 `data_chain` 的键值对；MCP `default` 值会填充缺失的键 |
| `--no-http` | 标志 | 关 | 不启动 HTTP/MCP 服务；任务完成后退出 |
| `--headless` | 标志 | 关 | Selenium 无头模式运行（Docker 中自动启用） |
| `--stop` | 标志 | — | 停止运行中的后台实例（读取 PID 文件，发送 SIGTERM） |
| `--nogui-enabled {true,false}` | `true` / `false` | `true` | 启用或禁用无 GUI 后台模式 |
| `--ui-policy {skip,abort}` | `skip` / `abort` | `skip` | 遇到 GUI 处理器时的处理方式：`skip` 静默跳过，`abort` 抛出错误 |
| `--log-level LEVEL` | `DEBUG` / `INFO` / `WARNING` / `ERROR` | 配置文件 | 覆盖日志级别 |
| `--http-port PORT` | 整数 | `8866` | 覆盖 HTTP 服务端口 |
| `--http-token TOKEN` | 字符串 | 配置文件 | 覆盖 HTTP 认证 Bearer 令牌 |

---

## `petpconfig.yaml` 配置项

所有配置位于 `config/petpconfig.yaml` 的 `application:` 键下：

| 键 | 默认值 | 说明 |
|-----|--------|------|
| `nogui_enabled` | `true` | 必须为 `true` 才能激活后台模式 |
| `nogui_ui_processor_policy` | `skip` | `skip` 静默跳过 GUI 处理器；`abort` 在遇到第一个 GUI 处理器时停止 |
| `http_port` | `8866` | 内置 HTTP/MCP 服务端口 |
| `http_request_token` | _(base64 字符串)_ | 所有 HTTP API 调用需要的 Bearer 令牌 |
| `http_request_timeout` | `600` | HTTP 请求超时秒数 |
| `log_level` | `INFO` | 运行时日志详细程度 |
| `execute_on_startup` | `false` | 服务启动时自动运行的 Execution 名称 |
| `ai_provider` | `""` | AI 助手使用的 LLM 提供商（见下方说明） |
| `ai_model` | `""` | LLM 模型名称；留空则使用 provider 默认值 |
| `ai_api_key` | `""` | API 密钥；支持 `${ENV_VAR}` 从环境变量读取；留空则从 provider 默认环境变量读取 |
| `ai_base_url` | `""` | API 地址；留空则使用 provider 默认值 |

---

## AI 助手配置

AI 助手功能（AI Execution Generator）用于通过自然语言生成和修改 PETP Execution 任务流。

### 最简配置

只需设置 `ai_provider`，其余字段留空将从 `AI_LLM_SETUPProcessor.PROVIDER_DEFAULTS` 自动填充：

```yaml
application:
  ai_provider: zhipu
  ai_model: ""
  ai_api_key: ""
  ai_base_url: ""
```

等价于：

```yaml
application:
  ai_provider: zhipu
  ai_model: GLM-5
  ai_api_key: "${ZHIPU_ACCESS_KEY}"
  ai_base_url: "https://open.bigmodel.cn/api/paas/v4/"
```

### 支持的 Provider 及默认值

| Provider | 默认模型 | 默认环境变量 | 默认 Base URL |
|----------|---------|-------------|--------------|
| `deepseek` | deepseek-chat | DEEPSEEK_API_KEY | https://api.deepseek.com |
| `zhipu` | GLM-5 | ZHIPU_ACCESS_KEY | https://open.bigmodel.cn/api/paas/v4/ |
| `qianfan` | ernie-4.5-8k | QIANFAN_API_KEY | https://qianfan.baidubce.com/v2 |
| `minimax` | MiniMax-Text-01 | MINIMAX_API_KEY | https://api.minimaxi.com/v1 |
| `anthropic` | claude-sonnet-4-20250514 | ANTHROPIC_API_KEY | — |
| `doubao` | doubao-1.5-pro-32k | DOUBAO_API_KEY | https://ark.cn-beijing.volces.com/api/v3 |
| `moonshot` | moonshot-v1-8k | MOONSHOT_API_KEY | https://api.moonshot.cn/v1 |
| `gemini` | gemini-1.5-pro | GOOGLE_API_KEY | — |
| `ollama` | deepseek-r1:7b | — | — |
| `openai_compatible` | gpt-4o | OPENAI_API_KEY | https://api.openai.com/v1 |

### `ai_api_key` 环境变量解析

如果值匹配 `${...}` 模式（如 `${DEEPSEEK_API_KEY}`），运行时从 `os.environ` 读取。否则作为字面量 API 密钥使用。

---

## AI 助手功能

### 入口

- **创建 Execution** → 模板选择中选 "AI 生成"
- **taskGrid 右键** → "AI 协助"（对现有 Execution 进行对话式修改）
- **MCP 描述编辑器** → "AI" 按钮（自动生成 mcp_desc JSON）

### 功能

| 功能 | 说明 |
|------|------|
| 咨询 Processor | 询问哪些 Processor 适合你的场景，AI 用自然语言推荐 |
| 生成任务流 | 描述自动化需求，AI 生成完整 Task 序列并加载到 taskGrid |
| 修改任务 | 对现有任务进行增量修改（插入、删除、替换） |
| 生成 MCP 描述 | 根据当前 Execution 的任务自动生成 mcp_desc JSON |

### Processor 选择器

- TreeListCtrl 显示所有 Processor 分类树，支持展开查看完整 DESC 文档
- 支持搜索过滤、全选/全不选、展开/收起所有
- 只有勾选的 Processor 会作为上下文发送给 LLM（节省 Token）
- "General" 分类始终包含在内

### 操作按钮

| 按钮 | 功能 |
|------|------|
| 撤销 | 回退 taskGrid 到 AI 修改前的快照状态（等同 Ctrl+Z） |
| 重做 | 恢复被撤销的操作（等同 Ctrl+Y） |
| 完成 | 关闭 AI 对话窗口，taskGrid 内容保留但不自动保存，需手动 Ctrl+S |

每次 AI 生成或修改任务后自动记录快照。关闭窗口后 LLM 连接和对话历史保留，下次打开时复用。

### 连接缓存

首次打开 AI 助手窗口时验证 LLM 连接，后续复用已有连接（瞬间打开）。配置变更时自动重新初始化。对话历史在本次启动期间保留。

---

## BackgroundRuntime 返回结构

每次 `run_execution` / `run_pipeline` 调用返回：

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

| 字段 | 说明 |
|------|------|
| `ok` | `true` 表示执行完成且无未处理异常 |
| `data` | `data_chain` 的公开子集（排除 `__m`、`__p` 和不可序列化值如 WebDriver 实例）；若 Execution 设置了 `response_key`，仅返回该键的值 |
| `error` | 失败时为错误消息字符串，成功时为 `null` |
| `meta.duration_ms` | 墙钟执行时间（毫秒） |
| `meta.skipped_tasks` | 被跳过的任务列表（`task.skipped = true` 或被 `ui_policy` 过滤） |

---

## 无 GUI 模式中跳过的处理器

仅**需要操作系统级 GUI 交互且无无头替代方案**的处理器会被跳过：

| 处理器 | 原因 |
|--------|------|
| `FILE_CHOOSER` | 使用 `pyautogui` 与操作系统文件选择对话框交互；无编程替代方案 |

以下处理器使用 `self.view is not None` 保护，在 BG 模式下**优雅降级**（记录日志/回退，不跳过）：

| 处理器 | BG 模式行为 |
|--------|------------|
| `SHOW_RESULT` | 记录标题 + 消息 |
| `INPUT_DIALOG` | 使用 `default_value` 参数，继续执行 |
| `MATPLOTLIB` | 记录图表参数 |

所有 **Selenium** 处理器（`GO_TO_PAGE`、`FIND_THEN_CLICK` 等）在 BG 模式下正常运行。所有 **Mouse** 处理器（`MOUSE_CLICK`、`MOUSE_POSITION`、`MOUSE_SCROLL`）通过 pyautogui 正常运行。

> 在 Docker 外强制无头 Selenium：使用 `--headless` 标志或设置 `PETP_HEADLESS=true` 环境变量（Docker 中自动启用）。
