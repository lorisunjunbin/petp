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
        "en": "MCP Tool Server · Task Orchestration · LLM-Native · AI-Powered Generation",
        "zh": "MCP 工具服务器 · 任务编排 · LLM 原生 · AI 驱动生成",
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
    "feat_ai_gen_title":     {"en": "AI Execution Generator", "zh": "AI Execution生成器"},
    "feat_ai_gen_desc":      {"en": "Generate and modify task flows through natural language. Multi-turn chat with LLM, expandable Processor browser with search, selective context to save tokens. One-click MCP tool description generation with smart merge. AI-powered error analysis with fix suggestions. Vision model support for image understanding via Ollama. Supports 10 LLM providers — only <code>ai_provider</code> config needed.", "zh": "通过自然语言生成和修改任务流程。多轮 LLM 对话、可展开的 Processor 浏览器（支持搜索）、选择性上下文节省 Token。一键生成 MCP 工具描述并智能合并。AI 驱动的错误分析与修复建议。通过 Ollama 支持视觉模型图像理解。支持 10 家 LLM 供应商——只需配置 <code>ai_provider</code>。"},

    # ── Index — AI workflow ──────────────────────────────────────
    "ai_flow_divider":       {"en": "AI-Powered Workflow",     "zh": "AI 驱动工作流"},
    "ai_flow_step1_title":   {"en": "Describe",               "zh": "描述"},
    "ai_flow_step1_desc":    {"en": "Tell AI what you want in natural language — create new or modify existing Execution flows through multi-turn chat.", "zh": "用自然语言告诉 AI 你想要什么——通过多轮对话创建新 Execution 或修改已有流程。"},
    "ai_flow_step2_title":   {"en": "Generate",               "zh": "生成"},
    "ai_flow_step2_desc":    {"en": "AI builds task flows from 80+ processor types. Browse, search, and selectively include processor context to save tokens.", "zh": "AI 从 80+ 处理器类型中构建任务流程。支持浏览、搜索并选择性包含处理器上下文以节省 Token。"},
    "ai_flow_step3_title":   {"en": "Publish",                "zh": "发布"},
    "ai_flow_step3_desc":    {"en": "One-click MCP tool description generation. Auto-extracts input/output schema and generates agent-friendly descriptions. Smart merge preserves existing config.", "zh": "一键生成 MCP 工具描述。自动提取输入/输出 Schema，生成 Agent 可理解的描述。智能合并不覆盖已有配置。"},
    "ai_flow_step4_title":   {"en": "Auto-Fix",               "zh": "自动修复"},
    "ai_flow_step4_desc":    {"en": "When execution fails, AI analyzes the error in context — pinpoints root cause, suggests fixes, and opens AI Assist pre-filled with the diagnosis.", "zh": "执行失败时，AI 自动分析上下文错误——定位根因、建议修复方案，并预填诊断结果打开 AI 助手。"},
    "ai_flow_footer":        {"en": "All AI features activate with a single config: <code>ai_provider</code>. Supports 10 LLM providers including DeepSeek, Claude, Gemini, and OpenAI-compatible.", "zh": "所有 AI 功能只需一项配置：<code>ai_provider</code>。支持 10 家 LLM 供应商，包括 DeepSeek、Claude、Gemini 及 OpenAI 兼容接口。"},

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
    "stat_ai":         {"en": "AI/LLM providers",         "zh": "AI/LLM 供应商"},
    "stat_modes":      {"en": "Running modes",            "zh": "运行模式"},
    "stat_cron":       {"en": "Cron scheduling",          "zh": "定时调度"},

    # ── Index — How It Works ─────────────────────────────────────
    "howto_divider":     {"en": "How It Works",                       "zh": "工作原理"},
    "howto_step1_title": {"en": "Define",                             "zh": "定义"},
    "howto_step1_desc":  {"en": "Configure tasks visually in GUI or write YAML directly", "zh": "在 GUI 中可视化配置任务，或直接编写 YAML"},
    "howto_step2_title": {"en": "Run",                                "zh": "运行"},
    "howto_step2_desc":  {"en": "Desktop, headless service, or Docker container", "zh": "桌面应用、后台服务或 Docker 容器"},
    "howto_step3_title": {"en": "Integrate",                          "zh": "集成"},
    "howto_step3_desc":  {"en": "Expose as MCP tools for AI agents to discover and invoke", "zh": "暴露为 MCP 工具，供 AI Agent 发现与调用"},

    # ── Index — YAML example ─────────────────────────────────────
    "yaml_section_title": {"en": "Simple Configuration",              "zh": "简洁配置"},
    "yaml_section_desc":  {"en": "Define a complete automation in YAML — no code, no SDK, just declare what to do.", "zh": "用 YAML 定义完整自动化——无需代码，无需 SDK，只需声明要做什么。"},

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
    "about_quickstart_title": {"en": "Quick Start",               "zh": "快速开始"},
    "about_first_run_title":  {"en": "Run Your First Execution in 4 Steps", "zh": "4 步运行你的第一个执行任务"},
    "about_mcp_screenshots_title": {"en": "AI Agent Integration in Action", "zh": "AI Agent 集成实战"},
    "about_http_mcp":         {"en": "HTTP Service & MCP Endpoints", "zh": "HTTP 服务与 MCP 端点"},
    "about_http_server_label":{"en": "Built-in HTTP server — port 8866", "zh": "内置 HTTP 服务器 — 端口 8866"},
    "about_dep_groups":       {"en": "Dependency Groups",         "zh": "依赖分组"},
    "about_project_struct":   {"en": "Project Structure",         "zh": "项目结构"},
    "about_changelog":        {"en": "Changelog",                 "zh": "更新日志"},
    "about_changelog_show_earlier": {"en": "Show earlier updates", "zh": "显示更早的更新"},

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
    "cl_2026_05_ai_workflow": {
        "en": "<strong>AI-Powered Workflow</strong>: AI generates &amp; modifies Executions via multi-turn chat; one-click MCP tool publishing with auto-extracted input/output schemas and smart merge; AI error analysis — on failure, automatically diagnoses root cause, suggests fixes, and pre-fills AI Assist for one-click repair.",
        "zh": "<strong>AI 驱动工作流</strong>：AI 通过多轮对话生成和修改 Execution；一键发布 MCP 工具，自动提取输入/输出 Schema 并智能合并；AI 错误分析——执行失败时自动诊断根因、建议修复方案，并预填 AI 助手实现一键修复。",
    },
    "cl_2026_05_vision_model": {
        "en": "<strong>Vision model support</strong>: <code>AI_LLM_QANDA</code> new <code>image_path</code> parameter for multimodal prompts. Works with Ollama vision models (gemma4, llava, moondream). Image path supports expressions — dynamically reference files from prior tasks in <code>data_chain</code>.",
        "zh": "<strong>视觉模型支持</strong>：<code>AI_LLM_QANDA</code> 新增 <code>image_path</code> 参数，支持多模态提问。适配 Ollama 视觉模型（gemma4、llava、moondream）。图片路径支持表达式——可动态引用 <code>data_chain</code> 中前序任务产出的文件。",
    },
    "cl_2026_05_create_execution": {
        "en": "New <strong>Create Execution</strong> button (+): create blank execution or from template via dialog; chooser and all grids properly cleared on delete.",
        "zh": "新增<strong>新建 Execution</strong>按钮（+）：通过对话框空白新建或从模板创建；删除后正确清空选择器与所有编辑区域。",
    },
    "cl_2026_05_mcp_sync_input": {
        "en": "McpDescEditor <strong>⇣ Sync</strong> button: reads first task's input JSON and lets user selectively sync parameters into MCP inputSchema via checkbox dialog.",
        "zh": "McpDescEditor <strong>⇣ 同步</strong>按钮：读取首个任务的输入 JSON，通过复选框对话框选择性同步参数到 MCP inputSchema。",
    },
    "cl_2026_05_email_mcp_tools": {
        "en": "Email MCP tools: <code>T_SEND_EMAIL</code> (SMTP with attachments) and <code>T_RECEIVE_EMAIL</code> (IMAP with filters) exposed as MCP tools with full inputSchema/outputSchema.",
        "zh": "邮件 MCP 工具：<code>T_SEND_EMAIL</code>（SMTP 发送含附件）和 <code>T_RECEIVE_EMAIL</code>（IMAP 接收含过滤）已作为 MCP 工具开放，配有完整 inputSchema/outputSchema。",
    },
    "cl_2026_05_pytube_fix": {
        "en": "YouTube downloader migrated from <code>pytube</code> (abandoned) to <code>pytubefix</code> (actively maintained); <code>file_download_path_key</code> now stores file path string directly.",
        "zh": "YouTube 下载器从 <code>pytube</code>（已废弃）迁移至 <code>pytubefix</code>（活跃维护）；<code>file_download_path_key</code> 现直接存储文件路径字符串。",
    },
    "cl_2026_05_ai_llm_unify": {
        "en": "Unified AI LLM processors: 10 providers (DeepSeek, Zhipu, Qianfan, MiniMax, Anthropic, Doubao, Moonshot, Gemini, Ollama, OpenAI-compatible) with MCP tool-calling support.",
        "zh": "统一 AI LLM 处理器：支持 10 个供应商（DeepSeek、智谱、千帆、MiniMax、Anthropic、豆包、月之暗面、Gemini、Ollama、OpenAI 兼容），含 MCP 工具调用能力。",
    },
    "cl_2026_05_palette_chooser": {
        "en": "<code>ExecutionChooser</code> / <code>PipelineChooser</code> migrated to palette mode: replaced <code>SearchableComboBox</code> with <code>TextCtrl</code> + <code>ProcessorPalette</code> popup; supports tag-based filtering. Snapshot &amp; save button now correctly triggered for all execution edits: processor selection, cell change, property move, and property key rename.",
        "zh": "<code>ExecutionChooser</code> / <code>PipelineChooser</code> 迁移为 Palette 模式：用 <code>TextCtrl</code> + <code>ProcessorPalette</code> 弹出窗口替换 <code>SearchableComboBox</code>，支持 tag 筛选。快照与保存按钮现可在所有编辑操作中正确触发：处理器选择、单元格更改、属性移动和属性键重命名。",
    },
    "cl_2026_05_command_palette": {
        "en": "<code>ProcessorPalette</code>: new command-palette processor selector replacing the ComboBox editor in taskGrid col 0 — case-insensitive filter on name &amp; category, name-first ordering, keyboard navigation (Up/Down/Enter/Esc), auto-dismiss on focus loss. <code>TaskInfoRenderer</code>: taskGrid col 1 now shows localized description, category badge, skip indicator, and param count instead of raw JSON.",
        "zh": "<code>ProcessorPalette</code>：新的命令面板处理器选择器，替换 taskGrid 第 0 列的 ComboBox 编辑器——名称与分类大小写不敏感过滤，名称优先排序，键盘导航（上/下/Enter/Esc），失焦自动关闭。<code>TaskInfoRenderer</code>：taskGrid 第 1 列现显示本地化描述、分类标签、跳过指示符和参数数量，替代原始 JSON。",
    },
    "cl_2026_05_i18n_split": {
        "en": "I18N refactor: processor descriptions split into <code>i18n/desc_translations.py</code>; GUI look &amp; feel polish — <code>PopupMenuButton</code> enhanced with configurable width, icons, and hover style.",
        "zh": "I18N 重构：处理器描述迁移至独立的 <code>i18n/desc_translations.py</code>；GUI 视觉优化 —— <code>PopupMenuButton</code> 新增可配置宽度、图标与悬停样式。",
    },
    "cl_2026_05_ui_streamline": {
        "en": "UI streamlining: removed DC viewer; log-level and clean-log controls moved into <code>LogSearchBar</code>; new reusable <code>PopupMenuButton</code> for theme / lang / log-level choosers; 5 new themes (Nord, Dracula, Sakura, Cyberpunk — 9 total); DEBUG-level <code>data_chain</code> JSON dump after each task.",
        "zh": "界面精简：删除 DC 查看器；日志级别与清除控件并入 <code>LogSearchBar</code>；新增可复用 <code>PopupMenuButton</code> 组件（主题 / 语言 / 日志级别选择器）；新增 5 套主题（Nord、Dracula、Sakura、Cyberpunk，共 9 套）；每个任务执行后以 DEBUG 级别输出 <code>data_chain</code> JSON。",
    },
    "cl_2026_05_if_else": {
        "en": "New <code>IF_ELSE</code> processor: declarative conditional branching — skip \"then\" or \"else\" task blocks based on a Python condition evaluated against <code>data_chain</code>; works correctly inside loops.",
        "zh": "新增 <code>IF_ELSE</code> 处理器：声明式条件分支——根据对 <code>data_chain</code> 求值的 Python 条件跳过 then 或 else 任务块；循环内可正确运行。",
    },
    "cl_2026_05_cron_history": {
        "en": "Cron execution history dialog (History button in Pipeline tab): browse last 50 runs with status, duration, and error details; filter by pipeline name.",
        "zh": "Cron 执行历史对话框（Pipeline 标签页 History 按钮）：浏览最近 50 次运行记录，含状态、耗时与错误详情；支持按 Pipeline 名称过滤。",
    },
    "cl_2026_05_input_dialog_bg": {
        "en": "<code>INPUT_DIALOG</code> BG mode: respects existing <code>data_chain</code> value instead of overwriting with <code>default_value</code>; GUI mode pre-fills dialog with existing value.",
        "zh": "<code>INPUT_DIALOG</code> BG 模式：优先保留 <code>data_chain</code> 已有值，不再覆盖为 <code>default_value</code>；GUI 模式预填已有值。",
    },
    "cl_2026_05_task_progress": {
        "en": "Task progress display in status bar; LRU execution cache; persistent log file descriptor; fix exit SEGFAULT caused by <code>wx.Timer</code> firing after window destruction.",
        "zh": "状态栏显示任务进度；LRU 执行缓存；持久化日志文件描述符；修复 <code>wx.Timer</code> 在窗口销毁后触发导致的退出 SEGFAULT。",
    },
    "cl_2026_04_highlight_info": {
        "en": "Status bar (<code>highlightInfo</code>): displays key execution events — <code>[START]</code>, <code>[DONE]</code> with duration, <code>[ERROR]</code> with message, <code>[STOP]</code>; color follows theme accent. <code>Executor</code> DONE event now carries error info.",
        "zh": "状态栏（<code>highlightInfo</code>）：展示关键执行事件 — <code>[START]</code>、<code>[DONE]</code>（含耗时）、<code>[ERROR]</code>（含错误信息）、<code>[STOP]</code>；颜色跟随主题 accent 色。<code>Executor</code> DONE 事件现携带错误信息。",
    },
    "cl_2026_04_system_theme": {
        "en": "\"System\" auto theme: follows OS dark / light mode (Monokai for dark, Ocean for light); responds to real-time system appearance changes via <code>wx.EVT_SYS_COLOUR_CHANGED</code>.",
        "zh": "\"System\" 自动主题：跟随系统深浅色模式（深色→Monokai，浅色→Ocean），通过 <code>wx.EVT_SYS_COLOUR_CHANGED</code> 实时响应系统外观切换。",
    },
    "cl_2026_04_theme": {
        "en": "Theme system: 9 built-in color themes (System, Forest, Ocean, Monokai, Solarized, Nord, Dracula, Sakura, Cyberpunk) with real-time switching via <code>PopupMenuButton</code>; selection persisted in <code>petpconfig.yaml</code>. Covers grid selection, property grid, log panel, search highlights, Run button gradient, and MCP tool toggle accent.",
        "zh": "主题系统：9 套配色主题（System、Forest、Ocean、Monokai、Solarized、Nord、Dracula、Sakura、Cyberpunk），通过 <code>PopupMenuButton</code> 实时切换，选择持久化到 <code>petpconfig.yaml</code>。覆盖表格选中色、属性编辑器、日志面板、搜索高亮、运行按钮渐变色、MCP 工具开关强调色。",
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
