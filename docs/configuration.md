# Configuration Reference

Runtime configuration, CLI arguments, and background mode behavior.

---

## CLI Arguments

| Argument | Values | Default | Description |
|----------|--------|---------|-------------|
| `--run-execution NAME` | any execution name | — | Run the named execution immediately on startup |
| `--run-pipeline NAME` | any pipeline name | — | Run the named pipeline immediately on startup |
| `--init-data JSON` | JSON object string | `{}` | Key-value pairs injected into `data_chain` before the run; MCP `default` values fill in any missing keys |
| `--no-http` | flag | off | Skip starting the HTTP/MCP server; process exits after the job finishes |
| `--headless` | flag | off | Run Selenium tasks in headless mode (auto-enabled in Docker) |
| `--stop` | flag | — | Stop a running background instance by reading its PID file and sending SIGTERM |
| `--nogui-enabled {true,false}` | `true` / `false` | `true` | Enable or disable no-GUI background mode |
| `--ui-policy {skip,abort}` | `skip` / `abort` | `skip` | What to do when a GUI-only processor is encountered: `skip` continues silently, `abort` raises an error |
| `--log-level LEVEL` | `DEBUG` / `INFO` / `WARNING` / `ERROR` | from config | Override the log level for this run |
| `--http-port PORT` | integer | `8866` | Override the HTTP service port |
| `--http-token TOKEN` | string | from config | Override the Bearer token for HTTP authentication |

---

## `petpconfig.yaml` Keys

All settings are under the `application:` key in `config/petpconfig.yaml`:

| Key | Default | Description |
|-----|---------|-------------|
| `nogui_enabled` | `true` | Must be `true` for background mode to activate |
| `nogui_ui_processor_policy` | `skip` | `skip` silently skips GUI processors; `abort` stops the execution on the first GUI processor |
| `http_port` | `8866` | Port for the built-in HTTP / MCP service |
| `http_request_token` | _(base64 string)_ | Bearer token required for all HTTP API calls |
| `http_request_timeout` | `600` | Seconds before an HTTP request times out |
| `log_level` | `INFO` | Runtime log verbosity |
| `execute_on_startup` | `false` | Name of an execution to run automatically when the service starts |
| `ai_provider` | `""` | LLM provider for AI assistant (see below) |
| `ai_model` | `""` | LLM model name; empty uses provider default |
| `ai_api_key` | `""` | API key; supports `${ENV_VAR}` for env var lookup; empty reads from provider's default env var |
| `ai_base_url` | `""` | API base URL; empty uses provider default |

---

## AI Assistant Configuration

The AI assistant (AI Execution Generator) generates and modifies PETP Execution task flows from natural language.

### Minimal Configuration

Only `ai_provider` is required. All other fields auto-fill from `AI_LLM_SETUPProcessor.PROVIDER_DEFAULTS`:

```yaml
application:
  ai_provider: zhipu
  ai_model: ""
  ai_api_key: ""
  ai_base_url: ""
```

### Supported Providers

| Provider | Default Model | Default Env Var | Default Base URL |
|----------|--------------|----------------|-----------------|
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

### `ai_api_key` Environment Variable Resolution

If the value matches `${...}` pattern (e.g., `${DEEPSEEK_API_KEY}`), it is resolved from `os.environ` at runtime. Otherwise treated as a literal API key.

---

## AI Assistant Features

### Entry Points

- **Create Execution** → select "AI Generate" from template choices
- **taskGrid right-click** → "AI Assist" (modify existing Execution via chat)
- **MCP Description Editor** → "AI" button (auto-generate mcp_desc JSON)

### Capabilities

| Feature | Description |
|---------|-------------|
| Processor consulting | Ask which Processors suit your use case; AI replies in natural language |
| Task flow generation | Describe automation needs; AI generates complete Task sequence into taskGrid |
| Task modification | Incremental changes (insert, delete, replace) via natural language |
| MCP desc generation | Auto-generate mcp_desc JSON from current Execution tasks |

### Processor Selector

- TreeListCtrl displays all Processor categories with expand-to-view full DESC documentation
- Search, select all/none, expand/collapse all
- Only checked Processors are sent as LLM context (saves tokens)
- "General" category always included

### Action Buttons

| Button | Function |
|--------|----------|
| Undo | Revert taskGrid to the snapshot before AI modification (same as Ctrl+Z) |
| Redo | Restore an undone operation (same as Ctrl+Y) |
| Done | Close AI dialog; taskGrid content is preserved but not auto-saved — use Ctrl+S to save |

A snapshot is pushed automatically after each AI generation or modification. LLM connection and conversation history persist after closing — reused on next open.

### Connection Caching

LLM connection is validated on first open and reused across dialog sessions. Config changes trigger re-initialization. Conversation history is preserved within the current app session.

---

## BackgroundRuntime Result Structure

Every `run_execution` / `run_pipeline` call returns:

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

| Field | Description |
|-------|-------------|
| `ok` | `true` if the execution completed without an unhandled exception |
| `data` | Public subset of `data_chain` (excludes `__m`, `__p`, and non-serialisable values such as WebDriver instances); if the execution sets a `response_key`, only that key's value is returned |
| `error` | Error message string on failure, `null` on success |
| `meta.duration_ms` | Wall-clock execution time in milliseconds |
| `meta.skipped_tasks` | List of tasks that were bypassed (either `task.skipped = true` or filtered by `ui_policy`) |

---

## Processors Skipped in No-GUI Mode

Only processors that **require OS-level GUI interaction with no headless alternative** are skipped:

| Processor | Reason |
|-----------|--------|
| `FILE_CHOOSER` | Uses `pyautogui` to interact with OS file chooser dialog; no programmatic alternative |

The following processors use `self.view is not None` guard and **degrade gracefully** in BG mode (log/fallback, not skipped):

| Processor | BG mode behavior |
|-----------|-----------------|
| `SHOW_RESULT` | Logs title + message |
| `INPUT_DIALOG` | Uses `default_value` param, continues execution |
| `MATPLOTLIB` | Logs chart params |

All **Selenium** processors (`GO_TO_PAGE`, `FIND_THEN_CLICK`, etc.) run normally in BG mode. All **Mouse** processors (`MOUSE_CLICK`, `MOUSE_POSITION`, `MOUSE_SCROLL`) run normally via pyautogui.

> Force headless Selenium outside Docker: `--headless` flag or `PETP_HEADLESS=true` env var (auto-enabled in Docker).
