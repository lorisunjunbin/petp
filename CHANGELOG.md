# Changelog

All notable changes to PETP are documented here.

## 2026

| Date | What's New |
|------|------------|
| 2026-09 | **Remember main window size and position**: reopens at the rect the user left, saved as one config item `window_rect` ("w,h,x,y") on close. Falls back to 80%-of-screen when missing/malformed, below 1200×700, or no longer fitting the monitor; off-screen position re-centres; closing maximized skips the save; Windows restore rides the DPI-stable show path (no resize jump) |
| 2026-09 | **Startup window-size jump fixed (Windows, wxPython 4.3.1)**: on RDP the display DPI arrives seconds after process start, so a window shown immediately got migrated (`WM_DPICHANGED`) and visibly re-scaled; the frame is now kept hidden until its DPI settles (validated against the registry `AppliedDPI`), sized in physical pixels via `MoveWindow`, then shown once — no jump |
| 2026-09 | **Unified typography (Windows polish)**: `Segoe UI` 10pt applied to every child (wx never propagates font changes to already-created windows), bold grid headers, 14pt monospace log console with theme colours preserved through the `TE_RICH2` default-style reset, localized `find task` placeholder |
| 2026-09 | **Toolbar & custom controls restyle (Windows)**: native 3D buttons flattened via a central `PETPTheme` palette with hover states and hairline group separators, uniform 28-DIP heights; `PopupMenuButton` switchers match sibling buttons (8pt label, width auto-fits the longest choice); `ToggleSwitch` redrawn Win11-Fluent (40×20 track, borderless off-state, soft knob shadow); `RunButton`/`ThemedButton`/`ToggleSwitch` gained `wx.BORDER_NONE` (removes the default 2px system frame) |
| 2026-09 | **Grids & McpDescEditor fixes**: task/execution grid rows 34 DIP so two-line renderer text never clips; new `ProcessorNameRenderer` ellipsizes column 0 with a `⊖` skipped marker; `McpDescEditor` grids get font-aware row heights and a rewritten column fit — desired widths recomputed every pass (a narrow-panel shrink no longer sticks), headers never truncate at any width, `ForceRefresh` after resize |
| 2026-09 | Docs: V1.5.0 highlights synced across README + webapp; safe-YAML security note, portable runtime docs and supplier execution assets; wxPython install docs rewritten for the 4.3.1 stable release (PyPI direct install for Python 3.12–3.14, dev-snapshot instructions removed) |
| 2026-08 | **`READ_EXCEL` file_path expression fix**: the TPL placeholder (`str on data_chain`) hijacked the `file_path_key` branch, leaving expressions like `{input_data}` unevaluated — the key now wins only when it is a real `data_chain` value |
| 2026-08 | **`WRITE_TO_FILE` append mode**: write mode selectable (overwrite/append), `i18n` updated; `FIND_THEN_KEYIN` input handling tightened; `CLAUDE.md` synced with current LLM providers, MCP conventions and the portable runtime |
| 2026-07 | **`timeout_msg` business context + `[NOOP]` soft-skip logging**: `FIND_THEN_CLICK`/`KEYIN` gain `timeout_msg` (expression-capable, `{timeout}` var via `expression2str` `extra_locals` without mutating `data_chain`), appended to raised failures; steps that complete without doing their work (skip-on-timeout, `condition_fn` false, intercepted click, no-op iframe switch) log a distinct `[NOOP]` warning; rolled out across the Selenium finder family |
| 2026-07 | **SAP Ariba form processors (1) — `SELECT_YESNO` / `SELECT_TREE_DROPDOWN` / `SELECT_MULTI_DROPDOWN`**: yes/no `md-radio-group` by fuzzy label aria-match, picks by VISIBLE text (Ariba mislabels both buttons 否); cascading tree picker with `>`-separated 1–4 level paths and `check_from_level`; multi-select rewritten as one atomic `execute_script` — kills stale-reference mis-clicks in the Angular virtual-scroller |
| 2026-07 | **SAP Ariba form processors (2) — `SELECT_SINGLE_DROPDOWN` / `DATE_PICKER` + dropdown open/close control**: type-ahead option pick; Angular Material calendar via the year view for readonly date inputs (locale-independent `aria-label` day match); `SELECT_TREE`/`MULTI` gain `open_xpath`/`close_xpath` (toggle-guarded open, container-scoped close) with atomic `execute_script` tree logic, level cap 8 |
| 2026-07 | **Finders hardened + GUI search + cleanup**: `FIND_THEN_KEYIN` waits BEFORE locating, gains `timeout`/`skip_timeout_error`; `MOVE_TO_IFRAME` `$default$`/`$parent$` sentinels; task-search box jumps between tasks whose input contains the query (CJK-aware); `ProcessorPalette` popup no longer runs off-screen on low grid rows; /simplify hoisted repeated xpath literals and the click ladder into `SeleniumUtil` |
| 2026-07 | **Docker headless Selenium**: image ships Selenium deps (`requirements-docker` includes `web-automation`) so browser executions run in-container; chromium/chromedriver split into their own layer behind `ARG CHROMIUM_CACHEBUST` — `docker_build_bg.sh --refresh-chromium` re-pulls only that layer; refreshed to Chromium/driver 150 |
| 2026-07 | **Headless click robustness**: `move_to_ele` scrolls `block:center` and swallows non-fatal `MoveTargetOutOfBoundsException`; final click fallback switched to a JavaScript click (no coordinate hit-test — fixes `ElementClickInterceptedException` on off-viewport/covered elements); `FIND_THEN_CLICK` honours `skip_timeout_error` for intercepted clicks too; `MOVE_TO_IFRAME` no longer quits the driver on frame-not-visible |
| 2026-07 | **HTTP disconnect log noise**: client-disconnect-before-read and streaming `BrokenPipeError` demoted to DEBUG (were INFO/traceback) — routine client timeouts/cancels no longer pollute the log; 329 tests green |
| 2026-05 | **Observability — `GET /petp/metrics`**: token-protected JSON snapshot of HTTP health for GUI and BG modes — per-endpoint counters (total/success/failed/in-flight/avg/p50/p95/p99), executor introspection (workers/queue depth), last 20 slow requests; same JSON logged every `metrics_log_interval_seconds` with a `METRICS ` grep prefix; stdlib-only `HttpMetrics.py`, 4 config keys, zero overhead when disabled; 9 new tests, 329 green |
| 2026-05 | **Refactor**: `PETPPresenter` shrunk by 128 lines — snapshot/undo/redo state and 10 methods extracted into `sub/SnapshotManager.py` (thin wrappers keep ~30 call sites); `HttpServerBaseMixin` shares 4 stateless handlers between GUI and BG servers; dead `_AUTHED_PATHS` removed — behavior-preserving, 320 tests green |
| 2026-05 | 🔒 **SECURITY (Phase 2 P0)**: (1) `CMDProcessor` hardcoded `shell=True` (CWE-78) — now defaults to `shlex.split`, opt back in with `shell="yes"`; (2) `create_and_execute_func` exec'd `_fn` bodies with full `__builtins__` — now a restricted namespace with whitelisted modules; (3) hardcoded public `Processor.SALT` (CWE-321) — resolves via `PETP_SALT` env → `~/.petp/secret` (0600) → compat default with migration WARNING; 32 new tests |
| 2026-05 | 🔒 **SECURITY (BREAKING — fail-closed auth)**: closed unauthenticated RCE on `/petp/exec` + `/mcp`. Without `http_request_token` every protected endpoint returns 501 instead of anonymous access; bearer-token-leaking route deleted; single `_require_token` helper with `hmac.compare_digest`; `expression2str` rejects `__<letter>` tokens and `eval()` runs with whitelisted `__builtins__`. **Set `http_request_token` before upgrading** — tokenless deployments reject all requests by design |
| 2026-05 | **Stability**: long-run resource hardening — `_expr_code_cache` switched from unbounded dict to `LRUCache(2048)` (loops with unique f-strings no longer leak compiled code objects); BG `Executor` and `BackgroundRuntime` now `quit()` selenium chrome drivers parked in `data_chain` on the exception path (prevents Chrome process drift in 24/7 BG/Docker deployments); `BackgroundRuntime.get_tools()` drops the 60s TTL since BG yaml is immutable post-startup |
| 2026-05 | **Cron reliability**: circuit breaker — `Cron` suspends a pipeline after N consecutive failures (`cron_max_consecutive_failures`, default 5) until manually restarted; structured `on_record` callback persists every run (success and failure) to history; `get_running_info()` exposes `consecutive_failures`, `last_status`, `last_error`, and `suspended` state for ops visibility |
| 2026-05 | **Security**: hardened YAML loader — `YamlRO` now uses `PETPSafeLoader` (built on `SafeLoader`) that only constructs the four allowed classes (`Execution`, `Task`, `Pipeline`, `Loop`); any other `!!python/object/apply:...` or `!!python/name:...` tag is rejected with `ConstructorError`, closing an arbitrary-code-execution path on malicious YAML files |
| 2026-05 | **Pipeline tab UX**: row context menu (copy/paste/duplicate/move/edit/fill/clear); double-click → `ProcessorPalette` or JSON dialog with auto-skeleton; pipeline undo/redo (Ctrl+Z/Y); per-step run highlighting; chooser context menu + Ctrl+C/X/V; Add button; down-arrow appends empty row; auto-load `last_pipeline` |
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
| 2025-05 | **`astool` flag**: GUI checkbox "make current Execution as PETP MCP tool" — per-execution MCP exposure mechanism |
| 2025-05 | ThreadingHTTPServer; AdvancedInputDialog; HTTP Service (port 8866) |
| 2025-05 | OOTB: `OOTB_AI_LLM_OLLAMA_MCP` / `OOTB_AI_LLM_DEEPSEEK_MCP` |
| 2025-04 | **`HTTP_RESPONSE_KEY` processor**: picks the `data_chain` value returned by the HTTP API |
| 2025-04 | Execution search, improved dropdowns |
| 2025-03 | ChromeDriver v134 |
| 2025-01 | Initial AI LLM: DeepSeek / Gemini / Ollama |

## 2024

| Date | What's New |
|------|------------|
| 2024-10 | Python 3.13, ChromeDriver 130 |
| 2024-09 | `TRANSLATE` processor switched from fanyi.youdao to translate.google |
| 2024-08 | Matplotlib, Ollama Q&A, nested RUN_EXECUTION |
| 2024-08 | `enable_windows_hdpi` config flag (default off) + matplotlib view icon; pyautogui Windows display fix |
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
| 2023-11 | **Processor categories** (`get_category()`, the 16-category taxonomy) for metadata organization; on-demand log-level switching |
| 2023-10 | Python 3.12 |
| 2023-09 | DB_ACCESS: MySQL / PostgreSQL / SAP HANA / SQLite |
| 2023-06 | Python 3.11 + Selenium upgrade; `GO_BACK` processor and `FIND_MULTI_THEN_COLLECT`; `is_in_loop` flag on processors; FIND_THEN_COLLECT `append_data_for_loop` |
| 2023-04 | YouTube download processor |
| 2023-04 | Fix: INPUT_DIALOG could not run off the main thread — resolved via wx.PyEvent + threading.Condition |
| 2023-01 | `WRITE_TO_EXCEL` processor; `READ_JSON` (jsonpath-python); `READ_EXCEL` filter by given fields; CMD processor simplified |

## 2022

| Date | What's New |
|------|------------|
| 2022-11 | UI simplification and event binding cleanup |
| 2022-10 | Non-blocking GUI execution |
| 2022-10 | Stop button — able to stop a running (even infinite) execution |
| 2022-09 | Last-run restore; Mouse processors |
| 2022-07 | MySQL support; Selenium 4.3.0 |
| 2022-06 | Python 3.10, wxPython 4.1.2 |
| 2022-04 | ZIP processor |
| 2022-03 | Loop N-times mode |

## 2021

| Date | What's New |
|------|------------|
| 2021-10 | BEAUTIFUL_SOUP processor |
| 2021-09 | **Loop feature**: loops wrap a range of tasks within an Execution (`core/loop.py`) — e.g. iterate rows read by `READ_EXCEL` (`read_from_excel_show_each_row` sample); loop-index bugfix; macOS chromedriver upgraded to support loops; `CSV_2_XLSX` processor |
| 2021-09 | Grid copy & paste |
| 2021-07 | `NESTED_TO_FLAT_CONVERTOR` processor (nested dict → flat, with list support); fix missing trash folder that blocked execution/pipeline deletion; processor screenshot separator fix |
| 2021-06 | **Open-sourced on GitHub** — first commit shares the initial codebase (69 files, ~4.8k lines: ~20 processors spanning Selenium automation, SSH/SFTP, file ops, `HTTP_REQUEST`, `CMD`, Excel/CSV I/O, plus the GUI editor and bundled webdrivers); `HTTP_REQUEST` default-value support; logging added; missing-log-folder and separator-mismatch fixes |
| 2021-06 | First commit, share my efforts in the past few months.|
