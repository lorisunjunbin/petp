"""
Lightweight i18n for PETP webapp.
Locale priority: session > ?lang= query param > Accept-Language header.
Supported locales: 'en', 'zh' (default).
"""
from flask import request, session

TRANSLATIONS: dict[str, dict[str, str]] = {
    # ── Navigation ───────────────────────────────────────────────
    "nav_home":        {"en": "Home",        "zh": "首页"},
    "nav_docs":        {"en": "Docs",        "zh": "文档"},
    "nav_fileviewer":  {"en": "File Viewer 🔒", "zh": "文件管理 🔒"},
    "nav_github":      {"en": "GitHub",      "zh": "GitHub"},
    "nav_signout":     {"en": "Sign Out",    "zh": "退出"},

    # ── Index — hero ─────────────────────────────────────────────
    "index_overline":  {
        "en": "MCP Tool Server · Task Orchestration · LLM-Native",
        "zh": "MCP 工具服务器 · 任务编排 · LLM 原生",
    },
    "index_title": {
        "en": "Turn any workflow into an MCP tool — callable by any Agent.",
        "zh": "将任意工作流变成 MCP 工具 — 可被任何 Agent 调用。",
    },
    "index_hero_text": {
        "en": "PETP is a pipeline execution runtime that exposes every automation as a typed MCP tool. AI agents can discover, invoke, and chain your real business operations — while processors inside each task can call LLMs themselves for intelligent decision-making. Now with built-in OCR, captcha handling, and conditional flow control.",
        "zh": "PETP 是一个流水线执行运行时，将每个自动化任务暴露为带类型的 MCP 工具。AI Agent 可以发现、调用并编排你的真实业务操作——同时任务内部的处理器也可以自主调用 LLM 进行智能决策。现已内置 OCR、验证码处理与条件流程控制。",
    },
    "index_cta_primary":   {"en": "Explore Architecture", "zh": "了解架构"},
    "index_cta_secondary": {"en": "Browse Shared Files",  "zh": "浏览共享文件"},

    # ── Index — metrics ──────────────────────────────────────────
    "metric_llm_inside":   {"en": "LLM Inside",   "zh": "内置 LLM"},
    "metric_llm_desc":     {"en": "processors can call LLMs", "zh": "处理器可调用 LLM"},
    "metric_scenario":     {"en": "Any Scenario",  "zh": "任意场景"},
    "metric_scenario_desc":{"en": "personal & enterprise toolsets", "zh": "个人与企业工具集"},

    # ── Index — MCP banner ───────────────────────────────────────
    "mcp_banner_title": {
        "en": "Every Execution becomes an MCP Tool",
        "zh": "每个执行任务都自动成为 MCP 工具",
    },
    "mcp_banner_text": {
        "en": "PETP starts an MCP server that advertises all configured executions as named tools with typed input/output schemas. Any MCP-compatible LLM client — Claude, Cursor, VS Code Copilot, or your own agent — can <strong>discover and invoke</strong> your real business workflows without any extra glue code.",
        "zh": "PETP 启动 MCP 服务器，将所有已配置的执行任务注册为带有类型化输入/输出 Schema 的命名工具。任何支持 MCP 的 LLM 客户端——Claude、Cursor、VS Code Copilot 或自定义 Agent——均可<strong>发现并调用</strong>你的真实业务流程，无需任何额外代码。",
    },
    "mcp_server_label": {"en": "MCP Server",             "zh": "MCP 服务器"},
    "mcp_server_desc":  {"en": "expose executions as tools", "zh": "将执行任务暴露为工具"},

    # ── Index — arch flow ────────────────────────────────────────
    "arch_title":       {"en": "Request-to-Result flow", "zh": "请求到结果的完整流程"},
    "arch_mcp_client":  {"en": "MCP Client",             "zh": "MCP 客户端"},
    "arch_mcp_client_desc": {
        "en": "Claude · Claude Code · Copilot<br>PETP self-call · any HTTP Streaming MCP client",
        "zh": "Claude · Claude Code · Copilot<br>PETP 自调用 · 任意 HTTP Streaming MCP 客户端",
    },
    "arch_mcp_server":      {"en": "MCP Server",      "zh": "MCP 服务器"},
    "arch_mcp_server_desc": {"en": "tools/list · tools/call<br>", "zh": "tools/list · tools/call<br>"},
    "arch_petp_runtime":    {"en": "PETP Runtime",    "zh": "PETP 运行时"},
    "arch_petp_desc":       {"en": "Pipeline → Execution → Tasks", "zh": "流水线 → 执行 → 任务"},
    "arch_processors":      {"en": "Processors",      "zh": "处理器"},
    "arch_processors_desc": {"en": "Selenium · HTTP · SSH · LLM · Email…", "zh": "Selenium · HTTP · SSH · LLM · 邮件…"},
    "arch_result":          {"en": "JSON Result",     "zh": "JSON 结果"},
    "arch_result_desc":     {"en": "Typed output returned to LLM", "zh": "结构化输出返回给 LLM"},

    # ── Index — feature cards ────────────────────────────────────
    "feat_divider":          {"en": "Core Capabilities",      "zh": "核心能力"},
    "feat_orch_title":       {"en": "Flexible Orchestration", "zh": "灵活编排"},
    "feat_orch_desc":        {"en": "Chain any mix of processors in a single execution. Conditional jump with <code>GO_TO_TASK</code>, loop with programmatic break / continue via <code>loop_condition</code>, or branch on LLM output — all in YAML, no code required.", "zh": "在单次执行中自由组合任意处理器。通过 <code>GO_TO_TASK</code> 条件跳转、<code>loop_condition</code> 编程式 break / continue，或基于 LLM 输出分支——全部用 YAML 配置，无需编写代码。"},
    "feat_llm_title":        {"en": "LLM Inside Tasks",       "zh": "任务内置 LLM"},
    "feat_llm_desc":         {"en": "Any task step can invoke an LLM processor: summarise, classify, generate, or decide. Results flow as variables into downstream steps.", "zh": "任意任务步骤均可调用 LLM 处理器：摘要、分类、生成或决策。结果作为变量流入下游步骤。"},
    "feat_toolset_title":    {"en": "Tool-Set per Scenario",  "zh": "场景化工具集"},
    "feat_toolset_desc":     {"en": "Package a curated set of executions for a specific domain — procurement, finance, DevOps, HR — and expose them as a focused MCP tool-set.", "zh": "为特定领域（采购、财务、DevOps、HR）打包精选执行任务，作为聚焦的 MCP 工具集对外暴露。"},
    "feat_pe_title":         {"en": "Personal & Enterprise", "zh": "个人与企业"},
    "feat_pe_desc":          {"en": "Run a personal assistant on your laptop, or deploy enterprise tool-sets on Docker. Same engine, same YAML, different scale.", "zh": "在笔记本上运行个人助手，或将企业工具集部署到 Docker。同一引擎，同一 YAML，不同规模。"},
    "feat_editor_title":     {"en": "Visual Editor with Undo / Redo", "zh": "可视化编辑器（撤销 / 重做）"},
    "feat_editor_desc":      {"en": "GUI editor with full undo / redo and snapshot history. 5 color themes including System (auto-follows OS dark / light mode). Status bar shows execution events in real time — start, done with duration, errors, and manual stops. Search &amp; highlight logs (Ctrl+F). Right-click the task grid for processor usage and reference lookup.", "zh": "图形编辑器支持完整撤销 / 重做与快照历史。5 套配色主题，含 System（自动跟随系统深浅色模式）。状态栏实时展示执行事件——启动、完成耗时、错误和手动停止。日志搜索高亮（Ctrl+F）。任务网格右键可查看处理器用法与引用查找。"},

    # ── Index — scenarios ────────────────────────────────────────
    "scenario_divider":    {"en": "Scenario Examples",        "zh": "场景示例"},
    "scenario_proc_name":  {"en": "Procurement Automation",   "zh": "采购自动化"},
    "scenario_proc_desc":  {"en": "Download sourcing request documents, merge contracts by creation date, classify by type using LLM, then send a summary email — all triggered by a single Claude message.", "zh": "下载采购申请文件、按创建日期合并合同、通过 LLM 分类，最后发送摘要邮件——全部由一条 Claude 消息触发。"},
    "scenario_fin_name":   {"en": "Finance Report Builder",   "zh": "财务报表生成"},
    "scenario_fin_desc":   {"en": "Pull data from multiple spreadsheets via SSH/SFTP, merge and pivot, call an LLM to write the executive summary section, and export as a final Excel report.", "zh": "通过 SSH/SFTP 从多个表格拉取数据，合并透视，调用 LLM 撰写执行摘要，最终导出 Excel 报表。"},
    "scenario_devops_name":{"en": "DevOps Task Toolkit",      "zh": "DevOps 工具集"},
    "scenario_devops_desc":{"en": "Expose CI pipeline triggers, deployment scripts, log fetchers, and health-checks as MCP tools. Let Copilot or a chat agent coordinate complex release workflows.", "zh": "将 CI 触发、部署脚本、日志拉取和健康检查暴露为 MCP 工具，让 Copilot 或对话 Agent 协调复杂发布流程。"},
    "scenario_pa_name":    {"en": "Personal Productivity",    "zh": "个人生产力"},
    "scenario_pa_desc":    {"en": "A lightweight personal MCP tool-set on your MacBook: web scraping, local file management, calendar data extraction, and LLM-powered daily brief generation.", "zh": "MacBook 上的轻量个人 MCP 工具集：网页抓取、本地文件管理、日历数据提取与 LLM 驱动的每日简报生成。"},
    "scenario_ocr_name":   {"en": "Web Form & Captcha Bot",   "zh": "表单填写与验证码自动化"},
    "scenario_ocr_desc":   {"en": "Use OCR to extract text from scanned documents or screen captures, and the CAPTCHA processor to handle login gates. Combine with Selenium and GO_TO_TASK to automate form workflows end-to-end — retrying on failure without writing a line of code.", "zh": "通过 OCR 从扫描件或截图中提取文字，CAPTCHA 处理器应对登录验证码。结合 Selenium 与 GO_TO_TASK 实现端到端表单自动化——失败自动重试，无需编写一行代码。"},

    # ── Index — stats ────────────────────────────────────────────
    "stat_processors": {"en": "Built-in processor types", "zh": "内置处理器类型"},
    "stat_config":     {"en": "Low-code configuration",  "zh": "少代码配置"},
    "stat_mcp":        {"en": "Native tool server",       "zh": "原生工具服务器"},
    "stat_toolsets":   {"en": "Composable tool-sets",     "zh": "可组合工具集"},

    # ── Index — bottom CTA ───────────────────────────────────────
    "cta_home_title": {
        "en": "Build your own MCP tool-set with PETP",
        "zh": "用 PETP 构建你的专属 MCP 工具集",
    },
    "cta_home_text": {
        "en": "Define executions in YAML, start the MCP server, and any LLM agent can immediately discover and orchestrate your real-world workflows. No SDK. No boilerplate.",
        "zh": "用 YAML 定义执行任务，启动 MCP 服务器，任何 LLM Agent 即可立刻发现并编排你的真实工作流。无需 SDK，无需样板代码。",
    },
    "cta_learn_more": {"en": "Learn how it works", "zh": "了解工作原理"},

    # ── About — header ───────────────────────────────────────────
    "about_overline": {"en": "Technical Reference",                     "zh": "技术参考文档"},
    "about_title":    {"en": "PETP — Pipeline · Execution · Task · Processor", "zh": "PETP — 流水线 · 执行 · 任务 · 处理器"},
    "about_hero_text":{
        "en": "A Python-based configurable task runner, execution engine, and MCP Tool Server. <strong>PET</strong> = <strong>P</strong>ipeline-<strong>E</strong>xecution-<strong>T</strong>ask, the hierarchical model. The trailing <strong>P</strong> = <strong>P</strong>rocessor, handling each task one-to-one.",
        "zh": "基于 Python 的可配置任务运行器、执行引擎和 MCP 工具服务器。<strong>PET</strong> = <strong>P</strong>ipeline-<strong>E</strong>xecution-<strong>T</strong>ask，层级模型。末尾的 <strong>P</strong> = <strong>P</strong>rocessor，与每个任务一一对应。",
    },

    # ── About — sections ─────────────────────────────────────────
    "about_processor_lib":    {"en": "Processor Library",         "zh": "处理器库"},
    "about_running_modes":    {"en": "Running Modes",             "zh": "运行模式"},
    "about_http_mcp":         {"en": "HTTP Service & MCP Endpoints", "zh": "HTTP 服务与 MCP 端点"},
    "about_http_server_label":{"en": "Built-in HTTP server — port 8866", "zh": "内置 HTTP 服务器 — 端口 8866"},
    "about_dep_groups":       {"en": "Dependency Groups",         "zh": "依赖分组"},
    "about_project_struct":   {"en": "Project Structure",         "zh": "项目结构"},
    "about_changelog":        {"en": "Changelog",                 "zh": "更新日志"},

    # ── About — table headers ────────────────────────────────────
    "th_category":    {"en": "Category",    "zh": "分类"},
    "th_capability":  {"en": "Capabilities","zh": "能力"},
    "th_method":      {"en": "Method",      "zh": "方法"},
    "th_endpoint":    {"en": "Endpoint",    "zh": "端点"},
    "th_description": {"en": "Description", "zh": "说明"},
    "th_dir":         {"en": "Directory / File", "zh": "目录 / 文件"},
    "th_date":        {"en": "Date",        "zh": "日期"},
    "th_whatsnew":    {"en": "What's New",  "zh": "更新内容"},

    # ── About — running mode cards ───────────────────────────────
    "mode_desktop_title": {"en": "Desktop GUI",          "zh": "桌面 GUI"},
    "mode_desktop_desc":  {"en": "Full visual runtime with wxPython UI. Interactive RPA, local development, manual execution trigger.", "zh": "基于 wxPython 的完整可视化运行时。支持交互式 RPA、本地开发和手动触发执行。"},
    "mode_bg_title":      {"en": "Background / Headless","zh": "后台 / JOB模式"},
    "mode_bg_desc":       {"en": "No GUI. Auto-detect headless Chrome. Ideal for scheduled tasks, CLI pipelines, and server automation.", "zh": "无 GUI，自动检测后台 Chrome，适用于定时任务、CLI 流水线和服务器自动化。"},
    "mode_docker_title":  {"en": "Docker",               "zh": "Docker"},
    "mode_docker_desc":   {"en": "Multi-arch image (arm64 build → amd64 run). Headless, no browser automation. Supports CI/CD and NAS deployment.", "zh": "多架构镜像（arm64 构建 → amd64 运行），无头模式，支持 CI/CD 和 NAS 部署。"},
    "mode_mcp_title":     {"en": "MCP Tool Server",      "zh": "MCP 工具服务器"},
    "mode_mcp_desc":      {"en": "Exposes executions as typed MCP tools. Supports both <strong>stdio</strong> and <strong>Streamable-HTTP</strong> transports.", "zh": "将执行任务暴露为带类型的 MCP 工具，同时支持 <strong>stdio</strong> 和 <strong>Streamable-HTTP</strong> 传输方式。"},

    # ── About — MCP inspector ────────────────────────────────────
    "mcp_inspector_title": {"en": "MCP Inspector setup",  "zh": "MCP Inspector 配置"},
    "mcp_inspector_desc":  {"en": "Connect any MCP Inspector or MCP-compatible client directly to PETP's HTTP server.", "zh": "将任何 MCP Inspector 或兼容 MCP 的客户端直接连接到 PETP 的 HTTP 服务器。"},
    "mcp_cap_transport":   {"en": "Transport Type: <strong>Streamable HTTP</strong>", "zh": "传输类型：<strong>Streamable HTTP</strong>"},
    "mcp_cap_url":         {"en": "URL: <strong>http://localhost:8866/mcp</strong>",   "zh": "URL：<strong>http://localhost:8866/mcp</strong>"},
    "mcp_cap_noauth":      {"en": "No authentication required for local dev",          "zh": "本地开发无需身份验证"},
    "mcp_cap_clients":     {"en": "Claude Code, Cursor, VS Code Copilot — add as MCP server in settings", "zh": "Claude Code、Cursor、VS Code Copilot——在设置中添加为 MCP 服务器"},

    # ── About — install ──────────────────────────────────────────
    "install_options_title": {"en": "Install options", "zh": "安装选项"},
    "install_full":    {"en": "Full (GUI desktop):",  "zh": "完整版（桌面 GUI）："},
    "install_bg":      {"en": "Background service:",  "zh": "后台服务："},
    "install_docker":  {"en": "Docker / headless:",   "zh": "Docker / 无头："},
    "install_custom":  {"en": "Custom: combine any group files with", "zh": "自定义：任意组合分组文件，使用"},

    # ── About — changelog entries (2026) ────────────────────────────
    "cl_2026_04_highlight_info": {
        "en": "Status bar (<code>highlightInfo</code>): displays key execution events — <code>[START]</code>, <code>[DONE]</code> with duration, <code>[ERROR]</code> with message, <code>[STOP]</code>; color follows theme accent. <code>Executor</code> DONE event now carries error info.",
        "zh": "状态栏（<code>highlightInfo</code>）：展示关键执行事件 — <code>[START]</code>、<code>[DONE]</code>（含耗时）、<code>[ERROR]</code>（含错误信息）、<code>[STOP]</code>；颜色跟随主题 accent 色。<code>Executor</code> DONE 事件现携带错误信息。",
    },
    "cl_2026_04_system_theme": {
        "en": "\"System\" auto theme: follows OS dark / light mode (Monokai for dark, Ocean for light); responds to real-time system appearance changes via <code>wx.EVT_SYS_COLOUR_CHANGED</code>.",
        "zh": "\"System\" 自动主题：跟随系统深浅色模式（深色→Monokai，浅色→Ocean），通过 <code>wx.EVT_SYS_COLOUR_CHANGED</code> 实时响应系统外观切换。",
    },
    "cl_2026_04_theme": {
        "en": "Theme system: 5 built-in color themes (System, Forest, Ocean, Monokai, Solarized) with real-time switching via toolbar dropdown; selection persisted in <code>petpconfig.yaml</code>. Covers grid selection, property grid, log panel, search highlights, Run button gradient, and MCP tool toggle accent.",
        "zh": "主题系统：5 套配色主题（System、Forest、Ocean、Monokai、Solarized），工具栏下拉实时切换，选择持久化到 <code>petpconfig.yaml</code>。覆盖表格选中色、属性编辑器、日志面板、搜索高亮、运行按钮渐变色、MCP 工具开关强调色。",
    },
    "cl_2026_04_goto_loopond": {
        "en": "<code>GO_TO_TASK</code> processor: conditional jump to any task within an execution; <code>loop_condition</code> attribute for programmatic break / continue based on data state; dynamic function caching in <code>CodeExplainerUtil</code>.",
        "zh": "<code>GO_TO_TASK</code> 处理器：条件跳转到执行内任意 task；<code>loop_condition</code> 属性支持编程式 break / continue；<code>CodeExplainerUtil</code> 动态函数缓存优化。",
    },
    "cl_2026_04_ocr_captcha": {
        "en": "<code>OCR</code> image preprocessing (binarize, denoise, sharpen, upscale, adaptive, auto); <code>CAPTCHA</code> processor (ddddocr: ocr / slide / det modes).",
        "zh": "<code>OCR</code> 图像预处理（二值化、去噪、锐化、放大、自适应、自动）；新增 <code>CAPTCHA</code> 处理器（ddddocr：ocr / slide / det 模式）。",
    },
    "cl_2026_04_log_search": {
        "en": "Log panel: search &amp; highlight with prev / next navigation (Ctrl+F / Cmd+F); property hint popup via right-click; <code>FIND_THEN_CLICK</code> <code>by_condition</code> parameter.",
        "zh": "日志面板：搜索高亮 + 上/下一个导航（Ctrl+F / Cmd+F）；属性介绍右键弹窗；<code>FIND_THEN_CLICK</code> 新增 <code>by_condition</code> 参数。",
    },
    "cl_2026_04_mcp_unify": {
        "en": "Unified MCP handling between GUI and BG modes via <code>McpMixin</code>; fixed <code>structuredContent</code> format; <code>outputSchema</code> supports <code>mapKey</code> field mapping.",
        "zh": "GUI 与 BG 模式 MCP 处理逻辑统一，提取 <code>McpMixin</code>；修复 <code>structuredContent</code> 格式；<code>outputSchema</code> 支持 <code>mapKey</code> 字段映射。",
    },
    "cl_2026_04_mcp_schema": {
        "en": "MCP tool schema supports <code>default</code> values for inputs and <code>mapKey</code> output field mapping; <code>McpDescEditor</code> enhancements.",
        "zh": "MCP 工具 schema 支持输入 <code>default</code> 默认值与输出 <code>mapKey</code> 字段映射；<code>McpDescEditor</code> 编辑器增强。",
    },
    "cl_2026_04_taskgrid_menu": {
        "en": "Task grid right-click menu: <em>View Processor Usage</em> and <em>Find Referencing Executions</em> options.",
        "zh": "任务网格右键菜单新增「查看处理器用法」与「查找引用执行」选项。",
    },
    "cl_2026_04_mcp_toggle": {
        "en": "MCP tool toggle replaced with custom <code>ToggleSwitch</code>; added state labels and response-key warning.",
        "zh": "MCP 工具开关改为自定义 <code>ToggleSwitch</code> 组件；新增状态标签与响应键警告提示。",
    },
    "cl_2026_04_mcp_desc_editor": {
        "en": "Execution description editor replaced with structured <code>McpDescEditor</code> for visual MCP tool schema editing.",
        "zh": "Execution 描述编辑器改为结构化 <code>McpDescEditor</code>，支持 MCP 工具 schema 可视化编辑。",
    },
    "cl_2026_04_http_auth": {
        "en": "<code>HTTP_REQUEST</code> processor: built-in Basic Auth, OAuth2, and XSRF / CSRF token support.",
        "zh": "<code>HTTP_REQUEST</code> 处理器新增内置 Basic Auth、OAuth2 与 XSRF / CSRF token 支持。",
    },
    "cl_2026_04_js": {
        "en": "New <code>RUN_JAVASCRIPT</code> processor (PythonMonkey) for executing JS functions.",
        "zh": "新增 <code>RUN_JAVASCRIPT</code> 处理器（基于 PythonMonkey），支持执行 JS 函数。",
    },
    "cl_2026_04_snapshot_combo": {
        "en": "Execution snapshots button; <code>SearchableComboBox</code> real-time filter and keyboard navigation with tool / nav icon prefixes.",
        "zh": "新增执行快照按钮；<code>SearchableComboBox</code> 支持实时过滤与键盘导航，工具 / 导航图标前缀。",
    },
    "cl_2026_04_loop": {
        "en": "Loop Editor: right-click or ⚙️ button to edit loop attributes via key-value dialog; snapshot &amp; undo / redo support for loop changes. Save button dirty-state fix for skip toggle, paste, add / delete row, and loop edits.",
        "zh": "循环编辑器：右键或 ⚙️ 按钮打开键值表单编辑循环属性；循环变更支持快照与撤销 / 重做。修复跳过任务、粘贴、增删行、循环编辑后保存按钮未启用的问题。",
    },
    "cl_2026_04_undo": {
        "en": "GUI Undo &amp; Redo &amp; snapshot history. Enhanced handy tools menu.",
        "zh": "图形界面支持撤销、重做和快照历史。增强实用工具菜单。",
    },
    "cl_2026_04_i18n": {
        "en": "Internationalization support: Chinese &amp; English.",
        "zh": "国际化支持：中文与英文。",
    },
    "cl_2026_04_deps": {
        "en": "Modular dependency management with <code>requirements/</code> groups; <code>uv</code> support.",
        "zh": "模块化依赖管理（<code>requirements/</code> 分组）；<code>uv</code> 支持。",
    },
    "cl_2026_04_nogui": {
        "en": "NO_GUI mode, <code>PETP_backgroud.py</code>, Docker support.",
        "zh": "无 GUI 模式、<code>PETP_backgroud.py</code>、Docker 支持。",
    },
    "cl_2026_04_toolbar": {
        "en": "Toolbar: append <code>date_str</code>, <code>os.sep</code>; Skip Task checkbox.",
        "zh": "工具栏：追加 <code>date_str</code>、<code>os.sep</code>；跳过任务复选框。",
    },
    "cl_2026_03_wxpython": {
        "en": "OOTB: <code>OOTB_DOWNLOAD_LATEST_WXPYTHON</code> for macOS &amp; Windows.",
        "zh": "开箱即用：<code>OOTB_DOWNLOAD_LATEST_WXPYTHON</code>（macOS 和 Windows）。",
    },
    "cl_2026_03_findmulti": {
        "en": "<code>FIND_MULTI_XXXProcessor</code> skip function.",
        "zh": "<code>FIND_MULTI_XXXProcessor</code> 跳过功能。",
    },
    "cl_2026_03_timeout": {
        "en": "Page load timeout in Selenium.",
        "zh": "Selenium 页面加载超时支持。",
    },
    "cl_2026_02_mcp": {
        "en": "MCP Tool Server (Streamable-HTTP).",
        "zh": "MCP 工具服务器（Streamable-HTTP）。",
    },
    "cl_2026_01_zhipu": {
        "en": "Zhipu Z.AI: Setup / Q&amp;A / MCP processors.",
        "zh": "智谱 Z.AI：初始化 / 问答 / MCP 处理器。",
    },

    # ── About — bottom CTA ───────────────────────────────────────
    "about_cta_title": {"en": "Python 3.14 · MIT License", "zh": "Python 3.14 · MIT 许可证"},
    "about_cta_text":  {
        "en": "Cross-platform — macOS (Apple Silicon &amp; Intel) and Windows. ChromeDriver in <code>webdriver/darwin/</code> or <code>webdriver/win32/</code>. Port 8866 configurable in <code>petpconfig.yaml</code>.",
        "zh": "跨平台——macOS（Apple Silicon 和 Intel）及 Windows。ChromeDriver 放在 <code>webdriver/darwin/</code> 或 <code>webdriver/win32/</code>。端口 8866 可在 <code>petpconfig.yaml</code> 中配置。",
    },
    "view_on_github":  {"en": "View on GitHub", "zh": "在 GitHub 上查看"},
    "back_to_home":    {"en": "Back to Home",   "zh": "返回首页"},

    # ── File Viewer ──────────────────────────────────────────────
    "fv_overline":     {"en": "Shared Workspace",    "zh": "共享工作区"},
    "fv_title":        {"en": "File Viewer",          "zh": "文件管理"},
    "fv_hero_text":    {"en": "Search files and open any result directly from the shared PETP workspace.", "zh": "搜索文件并直接从 PETP 共享工作区打开任意结果。"},
    "fv_placeholder":  {"en": "Search file name...",  "zh": "搜索文件名..."},

    # ── Login ────────────────────────────────────────────────────
    "login_subtitle":  {"en": "Sign in to access the shared workspace", "zh": "登录以访问共享工作区"},
    "login_username":  {"en": "Username",          "zh": "用户名"},
    "login_password":  {"en": "Password",          "zh": "密码"},
    "login_username_ph":{"en": "Enter username",   "zh": "请输入用户名"},
    "login_password_ph":{"en": "Enter password",   "zh": "请输入密码"},
    "login_submit":    {"en": "Sign In",            "zh": "登录"},
    "login_error":     {"en": "Invalid username or password.", "zh": "用户名或密码错误。"},
    "login_back":      {"en": "← Back to Home",    "zh": "← 返回首页"},

    # ── Page titles ──────────────────────────────────────────────
    "title_home":      {"en": "PETP - Home",        "zh": "PETP - 首页"},
    "title_about":     {"en": "About PETP",          "zh": "关于 PETP"},
    "title_fileviewer":{"en": "PETP File Viewer",    "zh": "PETP 文件管理"},
    "title_login":     {"en": "PETP — Sign In",      "zh": "PETP — 登录"},
}


def get_locale() -> str:
    """
    Locale priority:
    1. session['lang']  — set by a previous ?lang= switch
    2. ?lang= query param — saves to session for subsequent requests
    3. Accept-Language header
    4. Default: 'zh'
    """
    # 1. explicit switch via query param → persist to session
    param = request.args.get("lang", "").strip().lower()
    if param in ("zh", "en"):
        session["lang"] = param
        return param

    # 2. remembered in session
    if session.get("lang") in ("zh", "en"):
        return session["lang"]

    # 3. browser preference
    accept = request.headers.get("Accept-Language", "")
    for part in accept.replace(",", ";").split(";"):
        lang = part.strip().split("-")[0].lower()
        if lang in ("zh", "en"):
            return lang

    return "zh"


def make_translator(locale: str):
    """Return a t(key) function bound to the given locale."""
    def t(key: str) -> str:
        entry = TRANSLATIONS.get(key)
        if entry is None:
            return key
        return entry.get(locale) or entry.get("en") or key
    return t
