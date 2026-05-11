# CLAUDE.md

Behavioral guidelines to reduce common LLM coding mistakes. Merge with project-specific instructions as needed.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

---

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.

## 5. No Auto-Commit

**Never run `git commit` unless the user explicitly asks.** Make code changes, report what was modified, and wait for the user to decide when to commit. This includes bug fixes, docs updates, and feature work — all of it.


## 6. What is PETP, about current project:

PETP is a Python-based RPA toolkit — a configurable task runner, execution engine, and MCP Tool Server. The acronym encodes the runtime hierarchy:

```
Pipeline  1:n  Execution
Execution 1:n  Task
Task      1:1  Processor
```

Each **Execution** is a YAML file (in `core/executions/`) that lists Tasks, only edit by GUI. Each Task has a `type` that maps directly to a `<type>Processor.py` file under `core/processors/`. **Pipelines** (in `core/pipelines/`) chain multiple Executions. Loops wrap a range of tasks within an Execution.

---

## Running PETP

### Desktop (GUI)
```bash
python PETP.py
```

### Background / Headless
```bash
python PETP_backgroud.py

# Run one execution and exit (no HTTP server)
python PETP_backgroud.py --run-execution ENDECODER --no-http

# Run one pipeline and exit
python PETP_backgroud.py --run-pipeline MY_PIPELINE --no-http

# Pass initial data as JSON
python PETP_backgroud.py --run-execution MY_EXEC --init-data '{"key":"value"}' --no-http
```

### Docker (headless)
```bash
./build/docker_build.sh
docker run --rm -p 8866:8866 petp-background:amd64-local
```

### Web App (separate Flask app in `webapp/`)
```bash
cd webapp
pip install -r requirements.txt
python app.py           # http://localhost:5555
```

---

## Dependencies

Uses `uv` (recommended) or `pip`. Dependencies are split into modular groups under `requirements/`:

```bash
# Full install
uv pip install -r requirements.txt

# Headless / no-GUI
uv pip install -r requirements-nogui.txt

# Docker / headless, no browser automation
uv pip install -r requirements-docker.txt

# Custom subset (example)
uv pip install -r requirements/core.txt -r requirements/http-service.txt
```

wxPython must be installed manually from a `.whl` matching your Python version and OS — it is **not** in `requirements.txt`.

---

## Build Standalone Executable

```bash
python build/PETP_build.py            # GUI app → dist/PETP.app or dist/PETP.exe
python build/PETP_background_build.py # Headless app
```

### Docker Images

```bash
./build/script/docker_build_bg.sh          # BG service → build/petp-background-amd64.tar (port 8866)
./build/script/docker_build_webapp.sh      # Web app → build/petp-webapp-amd64.tar (port 5555)
```

Both scripts support `--no-tar`, `--run`, `--push repo:tag`, `--dirty`. Default mode uses `git archive` (+ staged files) to exclude untracked files from build context. `--dirty` falls back to working dir + `.dockerignore`.

### Deploy to NAS

```bash
./build/script/deploy_bg_to_nas.sh         # scp + docker load + start (port 8866)
./build/script/deploy_webapp_to_nas.sh     # scp + docker load + start (port 8088)
```

Both support `--no-start`, `--keep-tar`. Connection via env vars: `NAS_HOST`, `NAS_USER`, `NAS_PORT`, `NAS_DOCKER_DIR`, `HOST_PORT`.

### Tailscale Funnel (run on NAS with sudo)

```bash
sudo ./build/script/tailscale_funnel_refresh.sh   # reset + configure / → 8088, /mcp → 8866
```

### Deployment Topology

NAS (192.168.0.103) runs Docker with two containers exposed via Tailscale Funnel:
- `petp-webapp` container (internal 5555) → NAS host port 8088 → Tailscale Funnel `/`
- `petp-bg` container (internal 8866) → NAS host port 8866 → Tailscale Funnel `/mcp`

Build flow: local `docker_build_*.sh` → tar → `deploy_*_to_nas.sh` (scp + load + run) → `tailscale_funnel_refresh.sh` (one-time on NAS)

---

## Smoke Test

```bash
python testcoverage/nogui_smoke.py
```

Runs the built-in `ENDECODER` execution via `BackgroundRuntime` with `ui_policy="skip"` and exits non-zero on failure.

### Testing a New Processor

Create a temp YAML in `core/executions/`, run via `python PETP_backgroud.py --run-execution NAME --no-http`, then delete the temp file. Direct `Processor()` instantiation skips `set_task()` setup and will fail on `get_param()`.

## HTTP / MCP Endpoint Testing

`testcoverage/petp_http_endpoints.http` — IntelliJ/VS Code REST Client file covering all HTTP service and MCP endpoints (health, tools list, sync/async exec, MCP initialize/tools/call).

---

## Architecture

### Core Engine (`core/`)

| File | Role                                                                                                                                                                                                                                                                                                                                                                                                                  |
|------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `core/processor.py` | Base class for all processors. Provides `process()` (override in subclass), `expression2str()` (f-string evaluation against `data_chain`), `populate_data(k, v)` / `get_data(k)` for the shared `data_chain` dict, and `get_processor_by_type(prefix)` (dynamic class loading from file), once add new dynmatic functionvia CodeExplainerUtil.create_and_execute_func, have to sync-up with utils/CodeExplainerUtil.DYNAMIC_FUNC_PARAMS |
| `core/execution.py` | Runs a list of Tasks sequentially, handles loop boundaries, posts wxPython events in GUI mode. Serializes to/from YAML.                                                                                                                                                                                                                                                                                               |
| `core/executionstate.py` | Tracks which task is next, manages loop cursor state.                                                                                                                                                                                                                                                                                                                                                                 |
| `core/loop.py` | Describes a loop scope: `task_start`, `task_end`, `loop_key` (collection) or `loop_times` (fixed count), `item_key`, `loop_index_key`.                                                                                                                                                                                                                                                                                |
| `core/pipeline.py` | Runs a sequence of Executions, passing `data_chain` through all of them. Supports cron scheduling via `cronEnabled`, `cronExp`, `cronDesc` fields. |
| `core/cron/cron.py` | Cron scheduler: manages pending/running pipelines with dedup, thread-safe locking, auto-retry on failure. |
| `core/task.py` | Data class: `type`, `input` (JSON string), `skipped`, `data_chain`.                                                                                                                                                                                                                                                                                                                                                   |
| `core/definition/yamlro.py` | YAML read/write using PyYAML with `!!python/object` tags for deserialization.                                                                                                                                                                                                                                                                                                                                         |

### Processor pattern

Each processor lives at `core/processors/<TYPE>Processor.py` and defines a class `<TYPE>Processor(Processor)` that overrides `process()`. Processors read task parameters via `self.get_param(name)` / `self.has_param(name)`, write results to the shared chain via `self.populate_data(k, v)`, and read prior results with `self.get_data(k)`.

The `TPL` class attribute is the JSON template shown in the GUI for that processor type.

`expression2str(expression)` evaluates any parameter value as a Python f-string with `data_chain` keys injected as local variables — enabling dynamic values like `{my_variable}` in task inputs.

#### Expression & Dynamic Function Context

`expression2str` local_vars: `{'self': self, 'os': os, 'json': json, 'p': self}` — use `p.xxx()` in both expression (`{p.get_data("")}`) and `_fn` function bodies. `self` still works for backward compatibility.

All `CodeExplainerUtil.create_and_execute_func` calls MUST pass `self` as parameter `p` (always the last argument in the function signature). When adding a new `_fn` parameter to a Processor, update both the Processor call site AND `CodeExplainerUtil.DYNAMIC_FUNC_PARAMS`.

Passwords can be stored encrypted with `Processor.encrypt_pwd(str)` / `Processor.decrypt_pwd(str)` (key: `petpisawesome`).

### HTTP Service & MCP (`httpservice/`)

`HttpServer` (GUI mode) and `BackgroundHttpServer` (headless mode) expose these endpoints on port **8866**:

| Endpoint | Description |
|----------|-------------|
| `GET /health` | Health check |
| `GET /petp/tools` | List executions marked `astool: true` |
| `POST /petp/exec` | Trigger an execution or pipeline; `wait_for_result: true` blocks, `false` returns a `request_id` |
| `GET /petp/result?request_id=<id>` | Poll async result |
| `GET /mcp` / `POST /mcp` | MCP Streamable-HTTP endpoint (JSON-RPC 2.0) |

An Execution is exposed as an MCP tool when its YAML has `astool: true` and a `mcp_desc` JSON field with `desc`, `params`, and optionally `outParams`.

#### MCP Transport Design Decision

PETP uses **Streamable HTTP** as the sole MCP transport (protocol version 2025-03-26). SSE transport is intentionally not implemented — it was deprecated by the MCP specification in favor of Streamable HTTP, which offers better security (per-request auth headers), infrastructure compatibility (stateless, load-balancer friendly), and simpler single-endpoint design.

#### MCP Server Compliance

The MCP server implementation (`McpMixin`) follows JSON-RPC 2.0 and MCP spec:

- **Content negotiation**: Returns `application/json` by default; returns `text/event-stream` (SSE) when client sends `Accept: text/event-stream`
- **Protocol version**: Read from `params.protocolVersion` in the `initialize` request body per spec
- **Notifications**: `notifications/initialized` returns 202 with empty body (no JSON-RPC response per spec)
- **Batch requests**: Supports JSON-RPC batch (array of requests in single POST)
- **Timeout**: `tools/call` executions are protected by configurable timeout (`http_request_timeout`)
- **Progress notifications**: Long-running tools emit periodic `notifications/message` SSE events every 5 seconds
- **Session management**: `Mcp-Session-Id` header generated on initialize and validated on subsequent requests
- **Only advertised capabilities**: `tools` only — no unimplemented `prompts`/`resources` claims

#### MCP Tool Input Schema

The `mcp_desc.inputSchema` is defined at the **Execution level**, not the Processor level. Processor `TPL` defines internal task parameters which often come from preceding tasks in the data_chain — these are not MCP inputs.

The convention for MCP tool inputs: if the first task in an Execution is `INITIAL_PARAMS`, its keys represent the Execution's external inputs. The `mcp_desc` JSON in the Execution YAML should mirror these as the tool's `inputSchema`. This mapping is maintained manually via `McpDescEditor` in the GUI; auto-generation from `INITIAL_PARAMS` is available as a scaffold when `mcp_desc` is first created.

#### MCP Tool Output Schema vs HTTP_RESPONSE_KEY

Two response mechanisms serve different callers:

| | `HTTP_RESPONSE_KEY` processor | `outputSchema` + `mapKey` |
|---|---|---|
| Caller | `POST /petp/exec` (HTTP API) | `/mcp` (MCP protocol) |
| Output | Single data_chain value (whole value returned) | Multi-field structured JSON with field mapping |
| Expression | Supports dynamic key names via f-string | Static property names |

Both are kept intentionally. `HTTP_RESPONSE_KEY` is still required for executions called via the HTTP API without MCP. `outputSchema` with `mapKey` handles MCP clients and provides richer field-level mapping. If an execution is only used via MCP, `HTTP_RESPONSE_KEY` can be omitted.

### AI LLM Subsystem (`core/processors/sub/llm/`)

Unified LLM integration via three processors: `AI_LLM_SETUP`, `AI_LLM_QANDA`, `AI_LLM_QANDA_MCP`.

#### Supported Providers (10)

| Provider | Client Class | Default Model |
|----------|-------------|---------------|
| `deepseek` | OpenAICompatibleClient | deepseek-chat |
| `zhipu` | OpenAICompatibleClient | GLM-5 |
| `qianfan` | OpenAICompatibleClient | ernie-4.5-8k |
| `minimax` | OpenAICompatibleClient | MiniMax-Text-01 |
| `anthropic` | AnthropicClient | claude-sonnet-4-20250514 |
| `doubao` | OpenAICompatibleClient | doubao-1.5-pro-32k |
| `moonshot` | OpenAICompatibleClient | moonshot-v1-8k |
| `gemini` | GeminiClient | gemini-1.5-pro |
| `ollama` | OllamaClient | deepseek-r1:7b |
| `openai_compatible` | OpenAICompatibleClient | gpt-4o |

#### Architecture

- `BaseLLMClient` — abstract base with `chat()`, `provider_name`, and `get_client_by_provider()` factory
- `OpenAICompatibleClient` — uses OpenAI SDK; handles deepseek, zhipu, qianfan, minimax, doubao, moonshot, openai_compatible
- `GeminiClient` — native `google.genai` SDK with message format conversion
- `AnthropicClient` — native `anthropic` SDK; separates system messages, supports thinking blocks; uses `auth_token` for proxy/Bearer auth when `base_url` is set
- `OllamaClient` — local Ollama, no auth required

#### Adding a New Provider

1. If OpenAI-compatible: add entry to `BaseLLMClient.provider_map` → `OpenAICompatibleClient` and to `AI_LLM_SETUPProcessor.PROVIDER_DEFAULTS`
2. If custom SDK: create `<Name>Client.py` in `sub/llm/`, implement `chat()` + `create()` + `provider_name`, add to `provider_map`
3. Update DESC in all three processors and `i18n/desc_translations.py`

### GUI Layer (`mvp/`)

Model-View-Presenter pattern using wxPython. `PETPPresenter` owns the interaction logic; `PETPView` is the wxPython frame. Communication between the HTTP thread and the GUI uses `wx.PostEvent` with `PETPEvent`. In background mode, `view` is `None` throughout.

**IMPORTANT**: Do NOT modify `mvp/view/PETPView.py` directly — it is generated by wxGlade. All layout changes must be made through the wxGlade designer, then re-generated. Runtime label/tooltip changes (e.g., i18n) belong in `PETPPresenter._apply_locale()`.

#### Key GUI Components

| Component | File | Role |
|-----------|------|------|
| `PETPView` | `mvp/view/PETPView.py` | Main wxPython frame with two notebook tabs: "Executions" and "Pipelines" |
| `PETPPresenter` | `mvp/presenter/PETPPresenter.py` | Business logic, event handlers, grid operations. **Model is `self.m` not `self.model`** |
| `PETPInteractor` | `mvp/presenter/PETPInteractor.py` | Event routing — binds wx events to presenter methods |
| `PETPModel` | `mvp/model/PETPModel.py` | Persistence layer, bound to `config/petpconfig.yaml` |
| `SearchableGridChoiceEditor` | `mvp/view/common/SearchableGridChoiceEditor.py` | Filterable dropdown for processor selection in taskGrid column 0 |
| `SearchableComboBox` | `mvp/view/common/SearchableComboBox.py` | Filterable combo box for execution/pipeline selection |
| `HandyToolButton` | `mvp/view/common/HandyToolButton.py` | Expression snippet menu for common `data_chain` operations |
| `ResultDialog` | `mvp/view/common/ResultDialog.py` | Scrollable monospace dialog with copy/export (JSON/CSV) |
| `InputDialog` | `mvp/view/common/InputDialog.py` | Scintilla code editor for runtime input prompts |
| `McpDescEditor` | `mvp/view/common/McpDescEditor.py` | Editor for MCP tool description JSON |
| `ToggleSwitch` | `mvp/view/common/ToggleSwitch.py` | Custom toggle for boolean settings (e.g., `astool`) |

#### Execution Editor Layout

The "Executions" tab has a left-right split:
- **Left**: `taskGrid` (wx.grid.Grid, 2 columns: "Task Chooser" + "Input") for editing tasks, plus a loop editor panel below
- **Right**: `taskProperty` (wx.propgrid.PropertyGridManager) for editing individual parameters of the selected task, plus `availableProperties` combo for adding missing parameters

#### taskGrid Right-Click Context Menu

Right-clicking a row in `taskGrid` shows: Copy, Paste, Skip/Unskip, AI Assist, and (when column 0 has a valid processor name) View Processor Usage and Find Referencing Executions. Right-clicking empty grid area shows AI Assist only (via `EVT_RIGHT_DOWN` on `GetGridWindow()`).

#### Processor Discovery in GUI

- `Processor.get_processors()` scans `core/processors/` for all `*Processor.py` files → flat sorted list
- Shown via `SearchableGridChoiceEditor` with type-to-filter in taskGrid column 0
- When a processor is selected, its `TPL` (JSON template) auto-populates column 1
- Processors define a `DESC` class attribute with usage docs — shown via right-click "View Processor Usage"
- Localized descriptions: `get_localized_desc()` checks `i18n/translations.py` for key `desc_<TYPE>`, falls back to `DESC`

#### Processor Categories

Each processor defines `get_category()` returning one of: `AI_LLM`, `Default`, `File`, `Zip`, `Selenium`, `Mouse`, `GUI`, `Email`, `Database`, `Paramiko`, `JSON`, `Excel`, `General`, `Youtube`, `DataProcessing`, `HTTP`, `JAVASCRIPT`. Currently used for metadata only — not yet surfaced as a filter in the dropdown.

#### Editing Snapshots

The presenter supports undo/redo via `_push_snapshot()` / `_undo()` / `_redo()`, storing grid state snapshots. Accessible via Ctrl+Z/Y and the Snapshots dialog.

#### Task Backward Compatibility

Task objects deserialized from old YAML files may lack the `skipped` attribute. Always use `getattr(tk, 'skipped', False)` when accessing it from loaded executions.

#### wxPython Gotchas

- `wx.EXPAND` conflicts with `wx.ALIGN_RIGHT`/`wx.ALIGN_LEFT` in BoxSizers — never combine them
- `wx.EVT_MENU` binding must use `id=menu_id` parameter, not `MenuItem` as source — the latter silently fails
- Child `wx.TextCtrl` (read-only) captures mousewheel events — forward to parent `ScrolledPanel` via `EVT_MOUSEWHEEL` binding
- `ScrolledPanel.Scroll()` takes scroll units not pixels — divide virtual size by `GetScrollPixelsPerUnit()[1]`
- `Processor.get_processor_by_type()` returns an instance, not a class — use `cls.__class__.__name__` for instance objects
- `EVT_GRID_CELL_RIGHT_CLICK` doesn't fire on empty grid areas — use `EVT_RIGHT_DOWN` on `GetGridWindow()` with `YToRow()` check
- English `DESC` multiline docstrings have empty first line — use `next(l for l in lines if l.strip())` for first meaningful line
- **[CRITICAL] `wx.Timer` must be explicitly stopped before window close/destroy** — a running timer on a destroyed window causes segfault. Always bind `EVT_CLOSE` to stop timers, and call `timer.Stop()` before `dlg.Destroy()` in modal dialogs
- **[CRITICAL] wxPython widget parent must match the sizer's containing window** — adding a Button with parent=Frame to a sizer owned by a Panel causes `CheckExpectedParentIs` assertion failure. Always use the Panel that owns the sizer as parent.
- Nested `wx.SplitterWindow` for 3+ resizable panes — wxSplitter only supports 2 panes, nest them for tree/chat/input layouts. Use `SplitHorizontally(pane1, pane2, sash_position)` with negative sash_position to measure from bottom.
- `resolve_api_key()` must handle `None` input — config values from `getattr(self.m, key, '')` can be `None` if yaml field exists but has no value

#### AI Apply Pattern

When AI generates/modifies tasks, update `self.execution.list` and refresh taskGrid directly — do NOT call `Execution.save()`. Let the user save manually (Ctrl+S). Always create clean `Task(type, input, getattr(tk, 'skipped', False))` copies to avoid YAML serialization errors from `data_chain` references.

### AI Generator (`core/ai/`)

| File | Role |
|------|------|
| `core/ai/ExecutionGenerator.py` | LLM prompt construction, chat, response parsing, task generation |
| `mvp/view/common/AIGeneratorDialog.py` | Non-modal chat window with TreeListCtrl processor selector |

- Entry points: "AI Generate" in Create Execution dialog; "AI Assist" in taskGrid right-click menu
- LLM connection cached in presenter (`_ai_cached_generator`) across dialog sessions
- System prompt built lazily on first chat with currently-selected processors
- Config: `ai_provider`, `ai_model`, `ai_api_key`, `ai_base_url` in petpconfig.yaml
- `ai_api_key` supports `${ENV_VAR}` pattern via `resolve_api_key()`
- `validate_connection()` sends minimal "hi" to verify API reachability before enabling input
- AI Error Analysis: on execution failure, `_prompt_ai_error_analysis()` auto-prompts user. Error context (task index, type, input, traceback) collected in `Executor.run()` via DONE event's 4th element.
- `_last_running_task_index` (updated by LOG event in `highlight_running_task`) provides accurate failed task position — more reliable than `execution.state`
- To pre-fill AI Assist input with error context: use `wx.CallLater(800, _prefill)` to ensure generator is initialized before setting text

### Background Runtime (`core/runtime/BackgroundRuntime.py`)

Headless re-implementation of the execution loop that skips or aborts GUI-only processors based on `ui_policy` (`skip` or `abort`). Returns a structured result dict: `{"ok": bool, "data": {...}, "error": str|None, "meta": {...}}`.

#### BG Mode Processor Skip Policy (`core/runtime/UiProcessorPolicy.py`)

Only processors that **require OS-level GUI interaction with no headless alternative** are skipped:

| Skipped | Reason |
|---------|--------|
| `FILE_CHOOSER` | Uses `pyautogui` to interact with OS file chooser dialog; no programmatic alternative |

The following processors use `self.view is not None` guard and degrade gracefully in BG mode (log/fallback, not skipped):

| Processor | BG mode behavior |
|-----------|-----------------|
| `SHOW_RESULT` | Logs title + message |
| `INPUT_DIALOG` | Uses `default_value` param, continues execution |
| `MATPLOTLIB` | Logs chart params |
| `RELOAD_LOG` | Logs event |
| `RUN_EXECUTION` | Logs execution params |
| AI_LLM_*_QANDA | Uses `wx is not None` guard; logs errors instead of showing dialogs |

All Selenium processors (`GO_TO_PAGE`, `FIND_THEN_CLICK`, etc.) run normally in BG mode. Use `--headless` flag or `PETP_HEADLESS=true` env var to run Chrome headless (auto-enabled in Docker).

All Mouse processors (`MOUSE_CLICK`, `MOUSE_POSITION`, `MOUSE_SCROLL`) run normally in BG mode via pyautogui.

### Configuration (`config/petpconfig.yaml`)

All settings are under the `application:` key, bound to `PETPModel` via `SystemConfig`. Key fields: `http_port`, `http_request_token`, `http_request_timeout`, `nogui_enabled`, `nogui_ui_processor_policy`, `log_level`, `execute_on_startup`, `last_run`.

### macOS .app Data Externalization (`utils/AppPaths.py`)

In frozen macOS mode (`sys.frozen + darwin`), all user-mutable data lives in `~/.petp/` instead of inside the `.app` bundle. `AppPaths.get_user_data_dir()` returns `~/.petp` (frozen+darwin) or `os.path.realpath('.')` (all other cases including Windows frozen, dev mode, Docker).

On first launch: full seed from bundle Resources to `~/.petp/`. On subsequent launches:
- New execution/pipeline YAML files: copied to user dir
- Changed files: one timestamped variant kept (e.g., `NAME_20260509.yaml`), overwritten on next launch if bundle changes again
- Config: missing keys merged from bundle defaults (never overwrite existing user values)

**Windows frozen mode**: no externalization — exe runs from its own directory, user edits files in-place. This is intentional (Windows "unzip and run" model).

**Key files**: `PETP.py` (top-level sync block), `utils/AppPaths.py` (path resolver), `build/build_common.py` (build steps)

### Execution YAML format

```yaml
!!python/object:core.execution.Execution
execution: MY_EXECUTION
astool: true          # expose as MCP tool
mcp_desc: '{"desc":"...", "params":["param1"], "outParams":["result"]}'
list:
- !!python/object:core.task.Task
  type: GO_TO_PAGE
  input: '{"url":"https://example.com"}'
  skipped: false
- !!python/object:core.task.Task
  type: FIND_THEN_CLICK
  input: '{"xpath":"//button"}'
  skipped: false
loops: []
```

The `input` field is a JSON string. Values support f-string expressions against `data_chain` (e.g., `"{my_url}"`).

### Pipeline Cron Mode

Pipelines support scheduled execution via cron. Managed by `core/cron/cron.py`.

#### Pipeline YAML format

```yaml
!!python/object:core.pipeline.Pipeline
pipeline: DAILY_REPORT
cronEnabled: true
cronExp: 0 9 * * 1-5
cronDesc: At 09:00 AM, Monday through Friday
list:
- execution: fetch_data
  input: ''
- execution: send_email
  input: '{"to":"team@example.com"}'
```

| Field | Description |
|-------|-------------|
| `cronEnabled` | `true` activates the cron schedule |
| `cronExp` | Standard 5-field cron expression |
| `cronDesc` | Auto-generated human-readable description; persisted whenever `cronExp` is valid, regardless of `cronEnabled` |

#### Architecture: `Cron` class (`core/cron/cron.py`)

- **`_loop_worker` thread**: pops from `_pending` queue, deduplicates by key, spawns per-pipeline `_check_and_run` threads
- **`_check_and_run` thread**: waits until the next cron tick via `_stop.wait(timeout=...)`, calls `pipeline.run_sync()` (GUI) or `on_run` callback (BG), catches exceptions to survive failures
- **Thread safety**: all shared state (`_pending`, `_running_keys`, `_threads`) guarded by `threading.Lock`; `threading.Event` replaces sleep-polling
- **Dedup**: `add_one()` rejects if key is already in `_running_keys` or `_pending`
- **Stop**: `stop_one()`/`stop_all()` clear both `_running_keys` and `_pending`, signal `_stop` event, and `join` all threads for clean shutdown
- **`on_run` callback**: optional `(cron_obj, init_data) -> None` passed to constructor; BG mode uses this to route execution through `BackgroundRuntime.run_execution()` which applies `ui_policy` to skip GUI processors

#### GUI integration

- `PIPELINE_STEP` event (`PETPEvent.PIPELINE_STEP = 88880007`) carries `[action, ...]` where action is `start`, `step`, or `done`
- `start`/`done`: update `highlightInfo` with pipeline name and elapsed time
- `step`: select the current row in `executionGrid` and show `[PIPELINE] name → execution`
- Cron tooltip on `cronInput` shows the human-readable description

#### BG mode (`BackgroundRuntime.run_pipeline`)

- Independent execution loop (does not call `Pipeline._run`)
- Logs pipeline start/step/done with `cronExp` and `cronDesc`
- `cronDesc` accessed via `getattr(pipeline, 'cronDesc', '')` for backward compatibility with old YAML files

### data_chain

The `data_chain` dict is the single shared state that flows through all tasks in an execution and across executions in a pipeline. Processors read from it (`get_data`) and write to it (`populate_data`). In loop mode, per-iteration data is stored under `data_chain[loop_code][iteration_index]`.

### Web App (`webapp/`)

Separate Flask application serving on port 5555. Provides a landing page (`index.html`), file viewer (`fileviewer.html`), and about/documentation pages. Uses session-based auth. No web-based execution editor — task editing is GUI-only.

### Documentation (`docs/`)

Detailed reference guides (EN + CN) covering screenshots, running modes, dependencies, configuration, MCP/HTTP API, pipeline cron, and parameter migration. README links here; each doc is self-contained.

### Tools (`tools/`)

| Script | Purpose |
|--------|---------|
| `migrate_params.py` | Rename old parameter names in YAML files to snake_case (idempotent) |
| `sync_processor_desc.py` | Sync English DESC from processor files into `i18n/translations.py`; `--check` validates, `--update` applies |

### i18n (`i18n/translations.py`)

All user-facing strings use `t("key")` from `i18n/translations.py`. Each key maps to `{"en": "...", "zh": "..."}`. Locale is set via `set_locale()`.

**Processor description i18n** uses a different mechanism — single source of truth:

- **English**: always comes from the `DESC` class attribute in the processor `.py` file (the authoritative source)
- **Chinese**: stored in `i18n/translations.py` under key `desc_<TYPE>` with only a `"zh"` field
- `get_localized_desc(cls_or_instance, locale)` returns `cls.DESC` for English, looks up `TRANSLATIONS[desc_<TYPE>]["zh"]` for Chinese, falls back to `DESC` if no translation exists
- The function handles both class objects and instances (uses `cls.__name__` or `cls.__class__.__name__`)
- Used by the AI Generator (`core/ai/ExecutionGenerator._load_processor_context`) to build LLM system prompts with processor documentation in the user's locale

This avoids duplication — editing `DESC` in the processor file is all that's needed for English; Chinese translations are maintained separately in `translations.py`.

#### DESC format requirements

The `DESC` string serves dual purpose: documentation AND data source for the GUI "Param Hint" feature (right-click a property in PropertyGrid → view description). Each parameter **must** follow this format:

```
<One-line summary of what the processor does.>

- param_name: description (supports expression, default: "value")
- param_name: description (default: "value")

{TPL}
```

The `_extract_param_hint()` method parses lines starting with `- <param_name>:` to show per-parameter hints in the GUI.

---

## Adding a New Processor

1. Create `core/processors/<TYPE>Processor.py` with class `<TYPE>Processor(Processor)`.
2. Set `TPL` (JSON parameter template), `DESC` (documentation following the format above), and override `process()`.
3. Call `self.populate_data(key, value)` to store output for subsequent tasks.
4. No registration needed — `Processor.get_processor_by_type(prefix)` loads it dynamically from the file system.
5. Add Chinese translation: in `i18n/desc_translations.py`, add a `"desc_<TYPE>": {"zh": "..."}` entry with the Chinese translation of `DESC` content (do NOT include `"en"` — it comes from `DESC` at runtime).

#### Adding a New Parameter to an Existing Processor

1. **`TPL`** — add the new key with default value in the JSON template string (position logically near related params).
2. **`DESC`** — add a `- param_name: description (default: "value")` line in the English docstring, following existing format.
3. **`i18n/desc_translations.py`** — update the `"desc_<TYPE>"` Chinese translation to include the new parameter line in the same position.
4. **`process()`** — read the param via `self.explain_param_or_default('param_name', 'default')` and implement logic.
5. If the param is a `_fn` type (dynamic function body): update `CodeExplainerUtil.DYNAMIC_FUNC_PARAMS` with the new function signature, and pass `self` as `p` in the `create_and_execute_func` call.

#### Parameter naming conventions

| Category | Convention | Examples |
|----------|-----------|----------|
| File paths | `file_path`, `source_path`, `target_path` | never `filepath`, `sourcefolder` |
| Output keys | `data_key` (general), `value_key` (Selenium collect) | never `target_xlsx_key`, `output_key` |
| Booleans | always `"yes\|no"` lowercase | never `"Y\|N"`, `"Yes\|No"` |
| Code params | suffix `_fn` for function bodies | `condition_fn`, `filter_fn`, `resp_fn`, `map_fn` |
| LLM API env | `api_key_env` | never `key_name_gemini`, `api_key_name` |
| All params | `snake_case` only | never `useCache`, `collectby` |
| Selenium locator | `find_by` | never `clickby`, `keyinby`, `collectby` |
| Collection ref | `source_key`, `target_key` | never `given_collection`, `target_collection` |