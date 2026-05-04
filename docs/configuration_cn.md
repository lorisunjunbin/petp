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
