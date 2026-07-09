# Changelog

All notable changes to PETP are documented here.

## 2026

| Date | What's New |
|------|------------|
| 2026-07 | **Docker headless Selenium + click robustness + disconnect log noise reduction**: (1) Docker image now ships Selenium deps (`requirements-docker.txt` includes `web-automation`) so Selenium-based executions (e.g. `T_Supplier_Creation`) run inside the container without `No module named PIL`. Chromium/chromium-driver split into their own Dockerfile layer behind `ARG CHROMIUM_CACHEBUST`; `build/script/docker_build_bg.sh --refresh-chromium` forces only that layer to re-pull the latest Chromium from debian-security, keeping the (expensive) Python-deps layer cached. Image refreshed to Chromium 150 / chromedriver 150. (2) Click robustness for headless: `SeleniumUtil.move_to_ele` now `scrollIntoView({block:'center'})` before hovering and swallows non-fatal `MoveTargetOutOfBoundsException`; `move_to_ele_then_click`'s final fallback changed from `ele.click()` (same coordinate hit-test, fails the same way) to a **JavaScript click** (`execute_script("arguments[0].click()")`) which dispatches the event without coordinate hit-test — fixes `ElementClickInterceptedException` on off-viewport / covered elements in headless. `FIND_THEN_CLICK` now honors `skip_timeout_error='yes'` for the click-intercepted case too (previously only covered element-not-found), so conditional buttons (error-dialog "ignore & submit") that fail to click no longer abort the whole execution. (3) `MOVE_TO_IFRAME` gains `wait` / `timeout` / `skip_timeout_error` params; `SeleniumUtil.move_to_target_frame` no longer `chrome.quit()` on a frame-not-visible failure (it previously killed the entire driver, paralyzing the rest of the execution). (4) HTTP disconnect noise: both "Client disconnected before the request was fully read" and the streaming-response `BrokenPipeError` during `end_headers()` are now caught and logged at DEBUG (were INFO / full traceback) — routine client-side timeouts/cancels no longer pollute the default INFO log. 329 tests green |
| 2026-05 | **Observability**: new `GET /petp/metrics` endpoint (token-protected) returns a JSON snapshot of HTTP service health for both BG/Docker and GUI modes — per-endpoint counters (total / success / failed / in_flight / last_called_at / avg_ms / p50_ms / p95_ms / p99_ms), executor introspection (max_workers / active_workers / queue_depth, with `-1` fallback if Python's private `_work_queue`/`_threads` change), and the most recent 20 slow requests above `metrics_slow_threshold_ms`. The same JSON is also written to log every `metrics_log_interval_seconds` (default 60s) with the `METRICS ` prefix for `grep` consumption. New stdlib-only `httpservice/HttpMetrics.py` (per-endpoint locks, deque-backed quantile sample window) — zero new dependencies. Hook is wired into `HttpRequestHandler.process_request` and `send_streaming_response` so SSE flows are timed end-to-end (peer disconnects included). Configurable via 4 keys (`metrics_enabled`, `metrics_slow_threshold_ms`, `metrics_log_interval_seconds`, `metrics_quantile_window`); set `metrics_enabled: false` to short-circuit all hooks at zero overhead. **Tests:** 9 new (counts, quantiles, concurrent record, slow log, snapshot fields, executor introspection failure, disabled mode); 329 total green |
| 2026-05 | **Refactor (clean code)**: `PETPPresenter` shrunk by 128 lines — Snapshot/Undo/Redo state and 10 methods extracted into `mvp/presenter/sub/SnapshotManager.py` (Execution + Pipeline stacks); thin wrappers preserved on the Presenter so the ~30 existing call sites are unchanged. New `httpservice/HttpServerBaseMixin.py` shares 4 stateless handlers (`_require_token`, `_handle_health`, `_handle_mcp_get`, `_status_code_for_result`) between `HttpServer` and `BackgroundHttpServer`, eliminating the GUI/BG twin duplication. Side cleanup: dead `_AUTHED_PATHS` constant removed; lazy-init `hasattr` guards on `_pipeline_snapshots` retired. Behavior-preserving — all 320 tests green |
| 2026-05 | **🔒 SECURITY (Phase 2 P0)**: closed three remaining RCE/info-disclosure vectors. (1) `CMDProcessor` hardcoded `shell=True` ignored the user-set `shell` flag — any `;|&` in `cmdstr` was interpreted by the shell (CWE-78). Now defaults to `shlex.split` (no shell, metacharacters become literal arguments); set `shell="yes"` explicitly to opt back into shell mode. (2) `CodeExplainerUtil.create_and_execute_func` ran `_fn` / `_func_body` / `lambda_*` parameters via `exec(func, globals())`, exposing full `__builtins__` (`__import__`, `open`, `eval`, `exec`, `compile`) — completely bypassing the Phase 1 `_SAFE_BUILTINS` sandbox. Now exec into a restricted namespace with whitelisted modules (`re`, `json`, `datetime`, `math`); module globals isolated. (3) `Processor.SALT` was hardcoded public — `cryptocode` ciphertext from any deployment was trivially decryptable (CWE-321). Salt now resolves via env `PETP_SALT` → `~/.petp/secret` (mode 0600) → default with WARNING. Default kept for pre-2026-05 ciphertext compatibility; operators are alerted to migrate. **Tests:** 32 new (CMD injection PoC, sandbox escape PoC, salt resolution); 260 total green |
| 2026-05 | **🔒 SECURITY (BREAKING — fail-closed auth)**: closed unauthenticated remote RCE on `/petp/exec` + `/mcp`. `expression2str` evaluated user-controlled f-strings via `eval()`, and the HTTP service accepted requests anonymously when `http_request_token` was unset. Combined with the public Tailscale Funnel exposure, an attacker could execute arbitrary OS commands without credentials. **Fixes:** (1) HTTP auth is now **fail-closed** — when `http_request_token` is empty, every protected endpoint returns `501 Not Configured` instead of allowing anonymous access; (2) deleted `GET /mcp/.well-known/openid-configuration` route and `_handle_mcp_auth` method which leaked the bearer token to any caller; (3) all protected handlers now use a single `_require_token()` helper with `hmac.compare_digest` (constant-time); (4) `expression2str` rejects any `__<letter>` token inside f-string fields (blocks `__import__`, `__class__`, `__globals__`, `__subclasses__` object-graph escapes — string literals like CSS `Items__abc` and `__session_key` outside `{...}` remain valid); (5) `eval()` now runs with a whitelisted `__builtins__` (`len`, `str`, `int`, `range`, `getattr`, etc. — `open`, `eval`, `exec`, `compile`, `__import__` removed). **Action required for self-hosted users:** set `http_request_token` in `petpconfig.yaml` before upgrading; deployments without a token will reject all requests by design |
| 2026-05 | **Stability**: long-run resource hardening — `_expr_code_cache` switched from unbounded dict to `LRUCache(2048)` (loops with unique f-strings no longer leak compiled code objects); BG `Executor` and `BackgroundRuntime` now `quit()` selenium chrome drivers parked in `data_chain` on the exception path (prevents Chrome process drift in 24/7 BG/Docker deployments); `BackgroundRuntime.get_tools()` drops the 60s TTL since BG yaml is immutable post-startup |
| 2026-05 | **Cron reliability**: circuit breaker — `Cron` suspends a pipeline after N consecutive failures (`cron_max_consecutive_failures`, default 5) until manually restarted; structured `on_record` callback persists every run (success and failure) to history; `get_running_info()` exposes `consecutive_failures`, `last_status`, `last_error`, and `suspended` state for ops visibility |
| 2026-05 | **Security**: hardened YAML loader — `YamlRO` now uses `PETPSafeLoader` (built on `SafeLoader`) that only constructs the four allowed classes (`Execution`, `Task`, `Pipeline`, `Loop`); any other `!!python/object/apply:...` or `!!python/name:...` tag is rejected with `ConstructorError`, closing an arbitrary-code-execution path on malicious YAML files |
| 2026-05 | **Pipeline tab UX overhaul**: row context menu (copy / paste / duplicate / move up-down / delete / edit input / fill skeleton / clear input); double-click → ProcessorPalette (col 0) or JSON InputDialog with auto-skeleton + validation (col 1); Pipeline-only undo/redo snapshot stack (Ctrl+Z / Ctrl+Y); per-step run highlighting with status colors; pipeline chooser context menu (New / Copy) + Ctrl+C/X/V; Add button; Down-arrow auto-appends empty row (also for taskGrid); auto-load `last_pipeline` on startup |
| 2026-05 | **Pipeline context & reentrant safety**: `__pipeline_context` (pipeline_name, step_index, step_total, is_pipeline) injected into `data_chain` for both GUI and BG/Docker; reentrant lock prevents the same Pipeline from running twice concurrently in BG mode (matches existing cron dedup); thread-safe `petpconfig.yaml` writes via `SystemConfig._write_lock` |
| 2026-05 | **Performance**: `expression2str` fast path skips f-string evaluation when the input has no `{`; MCP `tools/call` batch requests now execute in parallel via the shared executor with `as_completed` |
| 2026-05 | **Layout**: `WrapSizer` for both Execution and Pipeline action panels — buttons wrap to multiple rows on narrow screens instead of being clipped |
| 2026-05 | **MCP Server Performance**: shared ThreadPoolExecutor (eliminates per-request pool creation); static-mode execution cache (BG/Docker skips filesystem stat/scan entirely); outputSchema parse cache; `_public_data` lazy serialization via `json.dumps` replacing recursive checks; Processor class warm-up on server start; real-time task-level SSE progress notifications during `tools/call` |
| 2026-05 | **Global Cache**: `CHECK_GLOBAL_CACHE` / `POPULATE_GLOBAL_CACHE` processors — in-memory cross-execution cache with TTL expiry; new `__end_execution` engine signal for early termination; `utils/GlobalCache.py` thread-safe storage with write-time eviction |
| 2026-05 | **macOS .app data externalization**: user-mutable data (executions, pipelines, config) stored in `~/.petp/`; incremental sync on upgrade (new files copied, conflicts get single timestamped variant); config key merge for new settings; execution version diff dialog (right-click compare) |
| 2026-05 | Build improvements: PyInstaller codesign tolerance (monkey-patch); build-time `${ENV_VAR}` expansion in config; lazy matplotlib import (~0.5s startup savings); API key priority fix (plain key over env var) |
| 2026-05 | MCP output expression: `mapKey` evaluates `{expr}` via f-string against data_chain; `McpDescEditor` adds `⇡` output sync button; both sync buttons use selected task row (fallback first/last); dynamic MCP panel sash based on property count; fix add-property on empty input; `os.getenv()` HandyTool snippet; webapp Docker self-containment via `build_assets/` |
| 2026-05 | MCP tool expansion: `T_SEND_EMAIL` (send email with CC, attachments) and `T_RECEIVE_EMAIL` (receive email with sender/subject filtering) exposed as MCP Tools; `McpDescEditor` adds `⇣` sync button to selectively sync parameters from first task input into MCP inputSchema |
| 2026-05 | Email processors enhanced: `SEND_EMAIL` supports CC/BCC, HTML, multi-attachments, TLS/SSL, timeout and fail policy; `RECEIVE_EMAIL` supports IMAP sender + subject filtering, attachment download, and exported saved paths via `attachments_key` |
| 2026-05 | **Processor system full optimization**: all 81 processors standardized to snake_case parameter naming; full i18n coverage (English + Chinese); improved DESC documentation quality. Migration script `tools/migrate_params.py` provided for existing YAML files |
| 2026-05 | UI streamlining: removed DC viewer; LogSearchBar; `PopupMenuButton` component; 5 new themes (Nord, Dracula, Sakura, Cyberpunk — 9 total); DEBUG-level `data_chain` dump |
| 2026-05 | New `IF_ELSE` processor: declarative conditional branching based on `data_chain` evaluation; works inside loops |
| 2026-05 | Cron execution history dialog: browse last 50 runs with status, duration, error details; filter by pipeline name |
| 2026-05 | `INPUT_DIALOG` BG mode: respect existing `data_chain` value; GUI mode pre-fills with existing value |
| 2026-05 | Task progress in status bar; LRU execution cache; fix exit SEGFAULT caused by wx.Timer |
| 2026-04 | Status bar: `[START]`, `[DONE]` with duration, `[ERROR]`, `[STOP]`; theme-aware colors |
| 2026-04 | "System" auto theme: follows OS dark/light mode via `wx.EVT_SYS_COLOUR_CHANGED` |
| 2026-04 | Theme system: 9 themes with live switching; persisted in config |
| 2026-04 | Recording converter: Chrome DevTools Recorder (`.json`) replacing Selenium IDE |
| 2026-04 | `GO_TO_TASK` processor; `loop_condition` for programmatic break/continue |
| 2026-04 | `OCR` processor with image preprocessing; `CAPTCHA` processor (ddddocr) |
| 2026-04 | Log panel search & highlight; property hint popup; `FIND_THEN_CLICK` by_condition |
| 2026-04 | Unified MCP handling via `McpMixin`; `outputSchema` mapKey field mapping |
| 2026-04 | `McpDescEditor`: structured visual MCP tool schema editing |
| 2026-04 | `HTTP_REQUEST`: Basic Auth, OAuth2, XSRF/CSRF token support |
| 2026-04 | `RUN_JAVASCRIPT` processor (PythonMonkey) |
| 2026-04 | Execution snapshots; undo/redo; `SearchableComboBox` |
| 2026-04 | Loop Editor: key-value dialog, snapshot support |
| 2026-04 | i18n: Chinese & English |
| 2026-04 | Modular dependency management; `uv` support |
| 2026-04 | NO_GUI mode, `PETP_background.py`, Docker support |
| 2026-03 | OOTB: `OOTB_DOWNLOAD_LATEST_WXPYTHON` for macOS & Windows |
| 2026-03 | `FIND_MULTI_XXX` skip function; page load timeout in Selenium |
| 2026-02 | **MCP Tool Server** (Streamable-HTTP) |
| 2026-01 | **Zhipu Z.AI** LLM integration |

## 2025

| Date | What's New |
|------|------------|
| 2025-10 | `STOPPER` / `RELOAD_LOG` processors; Python 3.14 |
| 2025-06 | OOTB: `OOTB_AI_LLM_GEMINI_MCP` |
| 2025-05 | ThreadingHTTPServer; AdvancedInputDialog; HTTP Service (port 8866) |
| 2025-05 | OOTB: `OOTB_AI_LLM_OLLAMA_MCP` / `OOTB_AI_LLM_DEEPSEEK_MCP` |
| 2025-04 | Execution search, improved dropdowns |
| 2025-03 | ChromeDriver v134 |
| 2025-01 | Initial AI LLM: DeepSeek / Gemini / Ollama |

## 2024

| Date | What's New |
|------|------------|
| 2024-10 | Python 3.13, ChromeDriver 130 |
| 2024-08 | Matplotlib, Ollama Q&A, nested RUN_EXECUTION |
| 2024-07 | Gemini AI-LLM; DATA_MULTI_MASKING; task skipping |
| 2024-06 | DATA_GROUPBY, DATA_MASKING |
| 2024-05 | HttpServer (GET/POST, JSON) |
| 2024-04 | On-demand processor loading after PyInstaller build |
| 2024-03 | PyInstaller build for macOS & Windows |
| 2024-02 | PETP File Viewer web app (Flask) |
| 2024-01 | Execute on startup |

## 2023

| Date | What's New |
|------|------------|
| 2023-12 | DATA_COLLECT, DATA_MAPPING, FIND_MULTI_THEN_CLICK, FOLDER_WATCH_MOVE |
| 2023-11 | ENCODE_DECODE_STR, HASH_STR, DATA_FILTER, COLLECTION_MERGE; rotating file handler |
| 2023-10 | Python 3.12 |
| 2023-09 | DB_ACCESS: MySQL / PostgreSQL / SAP HANA / SQLite |
| 2023-04 | YouTube download processor |

## 2022

| Date | What's New |
|------|------------|
| 2022-11 | UI simplification and event binding cleanup |
| 2022-10 | Non-blocking GUI execution |
| 2022-09 | Last-run restore; Mouse processors |
| 2022-07 | MySQL support; Selenium 4.3.0 |
| 2022-06 | Python 3.10, wxPython 4.1.2 |
| 2022-04 | ZIP processor |
| 2022-03 | Loop N-times mode |

## 2021

| Date | What's New |
|------|------------|
| 2021-10 | BEAUTIFUL_SOUP processor |
| 2021-09 | Grid copy & paste |
