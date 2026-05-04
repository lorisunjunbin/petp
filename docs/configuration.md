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
