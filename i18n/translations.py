TRANSLATIONS: dict[str, dict[str, str]] = {

    # === Window / Tab ===
    "win_title": {"en": "PET-P", "zh": "PET-P"},
    "tab_executions": {"en": "Executions", "zh": "Executions"},
    "tab_pipelines": {"en": "Pipelines", "zh": "Pipelines"},

    # === Buttons — Execution tab ===
    "btn_delete": {"en": "🗑", "zh": "🗑"},
    "btn_copy": {"en": "📋", "zh": "📋"},
    "btn_save": {"en": "Save", "zh": "保存"},
    "btn_run_execution": {"en": "Execute", "zh": "运 行"},
    "btn_run_pipeline": {"en": "Execute", "zh": "运 行"},
    "btn_stop": {"en": "Stop", "zh": "停 止"},
    "btn_stop_all": {"en": "Stop All", "zh": "全部停止"},
    "btn_reload": {"en": "Reload", "zh": "重载日志"},
    "btn_clean": {"en": "Clean", "zh": "清空日志"},
    "tip_log_search": {"en": "Search log", "zh": "搜索日志"},
    "tip_find_prev": {"en": "Previous match (Shift+Enter)", "zh": "上一个匹配 (Shift+Enter)"},
    "label_find_prev": {"en": "▲", "zh": "▲"},
    "tip_find_next": {"en": "Next match (Enter)", "zh": "下一个匹配 (Enter)"},
    "label_find_next": {"en": "▼", "zh": "▼"},
    "tip_filter_log": {"en": "Filter: show only lines matching keyword", "zh": "过滤：只显示含关键字的行"},
    "log_match_count": {"en": "{count} matches", "zh": "{count}个匹配"},
    "btn_select": {"en": "Select", "zh": "选择"},
    "btn_convert": {"en": "Convert", "zh": "转换"},

    # === Processor descriptions (i18n) ===

    "desc_AI_LLM_DEEPSEEK_QANDA": {
        "zh": (
            "向 DeepSeek LLM 提问并获取回答。依赖 AI_LLM_DEEPSEEK_SETUP 先初始化 LLM 实例。\n"
            "\n"
            "- llm_data_key: data_chain 中存储 LLM 客户端实例的键（默认: \"llmdeepseek\"）\n"
            "- question: 发送给 LLM 的提示/问题（支持表达式）\n"
            "- data_key: data_chain 中存储回答的键（默认: \"llm_response\"）\n"
            "- is_json: \"yes\" 则从 markdown 代码块中解析 JSON 结果（默认: \"no\"）\n"
            "- json_key: 当 is_json=\"yes\" 时，从解析后的 JSON 中提取的键（可选）\n"
            "- show_popup: \"yes\" 则在弹窗中显示问答内容（默认: \"no\"）\n"
            "- question_format: 发送前应用于 question 的 f-string 模板（默认: 直接使用 question）\n"
            "- system_prompt: LLM 的系统角色提示词（可选）"
        ),
    },

    "desc_AI_LLM_DEEPSEEK_QANDA_MCP": {
        "zh": (
            "向 DeepSeek LLM 提问并支持 MCP 工具调用。依赖 AI_LLM_DEEPSEEK_SETUP 先初始化 LLM 实例。\n"
            "运行另一个 PETP 作为 MCP 服务器。如果 LLM 决定使用工具，会调用 MCP 端点并将结果反馈。\n"
            "\n"
            "- llm_data_key: data_chain 中存储 LLM 客户端实例的键（默认: \"llmdeepseek\"）\n"
            "- question: 发送给 LLM 的提示/问题（支持表达式）\n"
            "- data_key: data_chain 中存储回答的键（默认: \"llm_response\"）\n"
            "- mcp_server_url: PETP MCP 服务器的 URL（默认: \"http://localhost:8866/mcp\"）\n"
            "- system_prompt: LLM 的系统角色提示词（可选）"
        ),
    },

    "desc_AI_LLM_DEEPSEEK_SETUP": {
        "zh": (
            "设置 DeepSeek LLM 客户端实例（OpenAI 兼容）。API 密钥可直接提供或从环境变量读取。\n"
            "客户端存储在 data_chain 中供后续任务使用。如果实例已存在则跳过设置。\n"
            "\n"
            "- api_key_env: 包含 API 密钥的环境变量名（默认: \"DEEPSEEK_API_KEY\"）\n"
            "- api_key: 直接提供的 API 密钥（优先于 api_key_env）\n"
            "- base_url: DeepSeek API 基础 URL（默认: \"https://api.deepseek.com\"）\n"
            "- model: 模型名称（默认: \"deepseek-chat\"）\n"
            "- temperature: 采样温度（默认: 1.0）\n"
            "- llm_data_key: data_chain 中存储客户端的键（默认: \"llmdeepseek\"）"
        ),
    },

    "desc_AI_LLM_GEMINI_QANDA": {
        "zh": (
            "使用已配置的 Gemini 实例向 Google Gemini LLM 提问（由 AI_LLM_GEMINI_SETUP 初始化）。\n"
            "提示词发送到模型，响应可选择解析为 JSON 和/或在弹窗中显示。\n"
            "\n"
            "- llm_data_key: data_chain 中存储 LLM 实例的键（默认: \"llmgemini\"）\n"
            "- question: 发送给 LLM 的提示/问题（支持表达式）\n"
            "- data_key: data_chain 中存储回答的键（默认: \"llm_response\"）\n"
            "- is_json: \"yes\" 则从 markdown 代码块中解析 JSON 结果（默认: \"no\"）\n"
            "- json_key: 当 is_json=\"yes\" 时，从解析后的 JSON 中提取的键（可选）\n"
            "- show_popup: \"yes\" 则在弹窗中显示问答内容（默认: \"no\"）\n"
            "- question_format: 发送前应用于 question 的 f-string 模板\n"
            "- system_prompt: LLM 的系统角色提示词（可选）"
        ),
    },

    "desc_AI_LLM_GEMINI_QANDA_MCP": {
        "zh": (
            "向 Google Gemini LLM 提问并支持通过 PETP MCP 服务器进行工具调用。\n"
            "依赖 AI_LLM_GEMINI_SETUP 已初始化 LLM 实例。从 MCP 服务器获取可用工具，如果 LLM 决定使用工具，\n"
            "通过 MCP 端点执行并返回优化后的答案。\n"
            "\n"
            "- llm_data_key: data_chain 中存储 LLM 实例的键（默认: \"llmgemini\"）\n"
            "- question: 发送给 LLM 的提示/问题（支持表达式）\n"
            "- data_key: data_chain 中存储回答的键（默认: \"llm_response\"）\n"
            "- mcp_server_url: PETP MCP 服务器的 URL（默认: \"http://localhost:8866/mcp\"）\n"
            "- system_prompt: LLM 的系统角色提示词（可选）"
        ),
    },

    "desc_AI_LLM_GEMINI_SETUP": {
        "zh": (
            "初始化并配置 Google Gemini LLM 实例，设置指定的模型、温度和 top_p 参数，\n"
            "然后存储在 data_chain 中供后续处理器使用。需要设置 GOOGLE_API_KEY 环境变量。\n"
            "\n"
            "- api_key_env: 包含 API 密钥的环境变量名（默认: \"GOOGLE_API_KEY\"）\n"
            "- model: Gemini 模型名称（默认: \"gemini-2.0-flash\"）\n"
            "- temperature: 采样温度，0-2（默认: 1.0）\n"
            "- top_p: Top-p 采样参数（默认: 0.95）\n"
            "- llm_data_key: data_chain 中存储客户端的键（默认: \"llmgemini\"）\n"
            "- system_prompt: LLM 的系统角色提示词（可选）"
        ),
    },

    "desc_AI_LLM_OLLAMA_QANDA": {
        "zh": (
            "通过本地运行的 Ollama 实例向 LLM 提问，获取回答，按需解析为 JSON，\n"
            "并可选择在弹窗中显示。需要 Ollama 在本地运行。\n"
            "\n"
            "- question: 发送给 LLM 的提示/问题（支持表达式）\n"
            "- data_key: data_chain 中存储回答的键（默认: \"llm_response\"）\n"
            "- model: Ollama 模型名称（默认: \"deepseek-r1:1.5b\"）\n"
            "- is_json: \"yes\" 则从 markdown 代码块中解析 JSON 结果（默认: \"no\"）\n"
            "- show_popup: \"yes\" 则在弹窗中显示问答内容（默认: \"no\"）"
        ),
    },

    "desc_AI_LLM_OLLAMA_QANDA_MCP": {
        "zh": (
            "通过 PETP MCP 服务器调用本地 Ollama LLM 并支持工具调用。\n"
            "从 MCP 服务器获取可用工具，向 LLM 提问，如果 LLM 决定使用工具，\n"
            "通过 MCP 服务器执行并返回优化后的答案。\n"
            "\n"
            "- question: 发送给 LLM 的提示/问题（支持表达式）\n"
            "- data_key: data_chain 中存储回答的键（默认: \"llm_response\"）\n"
            "- model: Ollama 模型名称（默认: \"qwen2.5:7b\"）\n"
            "- mcp_server_url: PETP MCP 服务器的 URL（默认: \"http://localhost:8866/mcp\"）\n"
            "- system_prompt: LLM 的系统角色提示词（可选）\n"
            "- ollama_url: Ollama 服务器 URL（默认: \"http://localhost:11434\"）"
        ),
    },

    "desc_AI_LLM_ZHIPU_QANDA": {
        "zh": (
            "向智谱 AI (GLM) 大模型提问，获取回答，可选从 markdown 代码块中解析 JSON，\n"
            "并可选在弹窗中显示问答内容。依赖 AI_LLM_ZHIPU_SETUP 已初始化客户端实例。\n"
            "\n"
            "- llm_data_key: data_chain 中存储 LLM 实例的键（默认: \"llmzhipu\"）\n"
            "- question: 发送给 LLM 的提示/问题（支持表达式）\n"
            "- data_key: data_chain 中存储回答的键（默认: \"llm_response\"）\n"
            "- model: 模型名称（默认: \"glm-4-flash\"）\n"
            "- is_json: \"yes\" 则从 markdown 代码块中解析 JSON 结果（默认: \"no\"）\n"
            "- json_key: 当 is_json=\"yes\" 时，从解析后的 JSON 中提取的键（可选）\n"
            "- show_popup: \"yes\" 则在弹窗中显示问答内容（默认: \"no\"）\n"
            "- question_format: 发送前应用于 question 的 f-string 模板\n"
            "- system_prompt: LLM 的系统角色提示词（可选）"
        ),
    },

    "desc_AI_LLM_ZHIPU_QANDA_MCP": {
        "zh": (
            "通过 PETP MCP 服务器调用智谱 AI (GLM) LLM 并支持工具调用。\n"
            "依赖 AI_LLM_ZHIPU_SETUP 已初始化客户端。从 MCP 服务器获取可用工具，向 LLM 提问，\n"
            "如果 LLM 决定使用工具，通过 MCP 端点执行并返回优化后的答案。\n"
            "\n"
            "- llm_data_key: data_chain 中存储 LLM 实例的键（默认: \"llmzhipu\"）\n"
            "- question: 发送给 LLM 的提示/问题（支持表达式）\n"
            "- data_key: data_chain 中存储回答的键（默认: \"llm_response\"）\n"
            "- model: 模型名称（默认: \"glm-4-flash\"）\n"
            "- mcp_server_url: PETP MCP 服务器的 URL（默认: \"http://localhost:8866/mcp\"）\n"
            "- system_prompt: LLM 的系统角色提示词（可选）\n"
            "- tools_filter: 工具名称过滤字符串，逗号分隔（可选，默认使用全部工具）\n"
            "- max_tool_calls: 最大工具调用次数（默认: 5）"
        ),
    },

    "desc_AI_LLM_ZHIPU_SETUP": {
        "zh": (
            "初始化并配置智谱 AI LLM 客户端实例，从环境变量（api_key_env 指定）或 api_key 参数\n"
            "直接读取 API 密钥。客户端存储在 data_chain 中供后续处理器使用。如果实例已存在则跳过设置。\n"
            "\n"
            "- api_key_env: 包含 API 密钥的环境变量名（默认: \"ZHIPU_API_KEY\"）\n"
            "- api_key: 直接提供的 API 密钥（优先于 api_key_env）\n"
            "- llm_data_key: data_chain 中存储客户端的键（默认: \"llmzhipu\"）"
        ),
    },

    "desc_BEAUTIFUL_SOUP": {
        "zh": (
            "使用 BeautifulSoup 解析 HTML 或 XML 内容，并执行自定义函数体来提取数据。\n"
            "解析后的 soup 对象和原始数据在函数体内可用，支持灵活处理。\n"
            "参见: https://beautiful-soup-4.readthedocs.io/en/latest/\n"
            "\n"
            "- data_key: data_chain 中存储 HTML/XML 内容的键\n"
            "- value_key: data_chain 中存储提取结果的键\n"
            "- func_body: Python 函数体字符串，可用变量: soup (BeautifulSoup 对象), data (原始字符串)\n"
            "- parser: BeautifulSoup 解析器（默认: \"html.parser\"）"
        ),
    },

    "desc_CAPTCHA": {
        "zh": (
            "使用 ddddocr 在本地识别验证码图片（无需 API 密钥）。\n"
            "pip install ddddocr\n"
            "\n"
            "支持的模式:\n"
            "- ocr: 标准文字/数字验证码识别（默认），返回识别的字符串\n"
            "- slide: 滑块验证码：在背景图中找到缺口位置，返回 {\"target\": [x, y]} 像素偏移\n"
            "- det: 目标检测模式：定位图片中所有文字区域，返回边界框列表\n"
            "\n"
            "- image_path: 验证码图片文件路径（支持表达式）\n"
            "- image_path_key: data_chain 中图片路径的键；优先于 image_path\n"
            "- mode: 识别模式 — ocr | slide | det（默认: \"ocr\"）\n"
            "- slide_target_key: data_chain 中滑块背景图路径的键（mode=slide 时必需）\n"
            "- data_key: data_chain 中存储结果的键（默认: \"captcha_result\"）"
        ),
    },

    "desc_CHECK_PARAM": {
        "zh": (
            "检查 data_chain 中必需的属性是否存在且非空。不满足条件时终止执行。\n"
            "\n"
            "- param_not_empty: 要检查的属性名，使用 \";\" 进行嵌套访问，如 \"name1;name2\""
        ),
    },

    "desc_CLOSE_CHROME": {
        "zh": (
            "根据给定的 chrome_name 关闭 data_chain 中对应的 Chrome 驱动。在流水线中运行时可跳过。\n"
            "\n"
            "- chrome_name: data_chain 中存储 Chrome 驱动实例的键（默认: \"chrome\"）\n"
            "- skip_when_pipeline: \"yes\" 在流水线模式下跳过关闭（默认: \"no\"）"
        ),
    },

    "desc_CMD": {
        "zh": (
            "通过 subprocess.check_output 运行系统命令，将输出保存到 data_chain 的 data_key 中。\n"
            "\n"
            "- cmdstr: 要执行的命令字符串（支持表达式）\n"
            "- data_key: data_chain 中存储命令输出的键\n"
            "- encoding: 输出编码（默认: \"utf-8\"）\n"
            "- timeout: 命令超时秒数（默认: 60）\n"
            "- cwd: 命令工作目录（支持表达式，可选）"
        ),
    },

    "desc_COLLECTION_MERGE": {
        "zh": (
            "从两个集合中查找匹配行并合并到结果集合中。\n"
            "\n"
            "- c_one_name: data_chain 中指向第一个集合的键\n"
            "- c_two_name: data_chain 中指向第二个集合的键\n"
            "- value_key: data_chain 中存储合并结果的键\n"
            "- match_column_one: 第一个集合中用于匹配的列索引\n"
            "- match_column_two: 第二个集合中用于匹配的列索引"
        ),
    },

    "desc_CREATE_SFTP_CLIENT": {
        "zh": (
            "创建 paramiko SFTP 客户端，保存到 data_chain 的 sftp_client_key 中。\n"
            "\n"
            "- sftp_ip: SFTP 服务器 IP 地址（支持表达式）\n"
            "- sftp_port: SFTP 服务器端口（默认: 22）\n"
            "- sftp_user: SFTP 用户名（支持表达式）\n"
            "- sftp_pwd: SFTP 密码（支持表达式和加密值）\n"
            "- sftp_client_key: data_chain 中存储 SFTP 客户端的键（默认: \"sftpclient\"）"
        ),
    },

    "desc_CREATE_SSH_CLIENT": {
        "zh": (
            "创建 paramiko SSH 客户端，保存到 data_chain 的 ssh_client_key 中。\n"
            "\n"
            "- ssh_ip: SSH 服务器 IP 地址（支持表达式）\n"
            "- ssh_port: SSH 服务器端口（默认: 22）\n"
            "- ssh_user: SSH 用户名（支持表达式）\n"
            "- ssh_pwd: SSH 密码（支持表达式和加密值）\n"
            "- ssh_client_key: data_chain 中存储 SSH 客户端的键（默认: \"sshclient\"）"
        ),
    },

    "desc_CSV_2_XLSX": {
        "zh": (
            "将 CSV 文件转换为 XLSX 格式。从 source_path 读取，写入 target_path，\n"
            "然后将目标 xlsx 路径通过 data_key 保存到 data_chain。\n"
            "\n"
            "- source_path: 源 CSV 文件路径（支持表达式）\n"
            "- target_path: 目标 XLSX 文件路径（支持表达式）\n"
            "- data_key: data_chain 中存储目标路径的键\n"
            "- delimiter: CSV 分隔符（默认: \",\"）"
        ),
    },

    "desc_DATA_COLLECT": {
        "zh": (
            "通过 lambda 表达式将数据收集到 data_chain 中的列表或字典。支持收集前清空。\n"
            "\n"
            "- clean_before_collect: \"yes\" 收集前清空目标，\"no\" 追加（默认: \"no\"）\n"
            "- collect_key: data_chain 中存储收集结果的键\n"
            "- lambda: Python 表达式，可用 data_chain 变量\n"
            "- collect_type: 收集类型 — \"list\" 或 \"dict\"（默认: \"list\"）\n"
            "- dict_key_lambda: dict 模式下用于生成键的表达式\n"
            "- dict_value_lambda: dict 模式下用于生成值的表达式"
        ),
    },

    "desc_DATA_CONVERT": {
        "zh": (
            "从 data_chain 中按键取值，通过自定义 Python 函数转换，将结果存回 data_chain 的目标键。\n"
            "\n"
            "- source_key: data_chain 中读取源数据的键（支持表达式）\n"
            "- target_key: data_chain 中存储结果的键（支持表达式）\n"
            "- func_body: Python 函数体字符串，参数为 \"source_data\"（支持表达式）"
        ),
    },

    "desc_DATA_FILTER": {
        "zh": (
            "使用 filter_fn 表达式过滤 source_key，将结果存入 target_key。\n"
            "如果未指定 target_key，则替换 source_key。\n"
            "\n"
            "- source_key: data_chain 中指向源列表的键\n"
            "- target_key: data_chain 中存储过滤结果的键（可选，默认替换源）\n"
            "- filter_fn: Python 函数体，参数为 \"item\"，应返回 bool\n"
            "- start_idx: 起始索引（可选）\n"
            "- end_idx: 结束索引（可选）"
        ),
    },

    "desc_DATA_GROUPBY": {
        "zh": (
            "按键函数对 source_key 进行分组，可选映射和收集分组结果到字典中。\n"
            "\n"
            "- source_key: data_chain 中指向输入列表的键\n"
            "- data_key: data_chain 中存储分组结果字典的键\n"
            "- key_fn: Python 表达式，用于生成分组键，变量 \"item\" 可用\n"
            "- value_fn: Python 表达式，用于转换每个元素（可选，默认使用原始 item）\n"
            "- collect_fn: Python 表达式，用于聚合每组的值列表（可选）"
        ),
    },

    "desc_DATA_MAPPING": {
        "zh": (
            "使用 map_fn 表达式对 source_key 中的每个元素进行映射/转换，结果存入 target_key。\n"
            "支持通过 start_idx/end_idx 进行切片。如果未指定 target_key，则替换 source_key。\n"
            "\n"
            "- source_key: data_chain 中指向源列表的键\n"
            "- target_key: data_chain 中存储映射结果的键（可选，默认替换源）\n"
            "- map_fn: Python 函数体，参数为 \"item\"，返回转换后的值\n"
            "- start_idx: 起始索引（可选）\n"
            "- end_idx: 结束索引（可选）"
        ),
    },

    "desc_DATA_MASKING": {
        "zh": (
            "对集合（行列表）执行单列数据脱敏。每行是一个列表，指定列被清洗后\n"
            "用自定义函数生成的脱敏值替换。维护脱敏字典确保相同原始值映射到相同脱敏值。\n"
            "\n"
            "- source_key: data_chain 中指向输入集合的键\n"
            "- masking_column: 要脱敏的列索引\n"
            "- masking_fn: Python 函数体，生成脱敏值，参数为 (row, col_idx, masking_dict, counter)\n"
            "- clean_fn: Python 函数体，清洗原始值后再匹配（可选）\n"
            "- masking_dict_key: data_chain 中存储脱敏字典的键\n"
            "- masking_dict_inverted: \"yes\" 则反转字典输出（默认: \"no\"）"
        ),
    },

    "desc_DATA_MULTI_MASKING": {
        "zh": (
            "对集合（行列表）执行多列数据脱敏。与单列 DATA_MASKING 不同，\n"
            "此处理器支持同时脱敏多个列。每个指定列被清洗后用脱敏值替换。\n"
            "\n"
            "- source_key: data_chain 中指向输入集合的键\n"
            "- masking_columns: 要脱敏的列索引列表，如 \"0,2,5\"\n"
            "- masking_fn: Python 函数体，生成脱敏值\n"
            "- clean_fn: Python 函数体，清洗原始值（可选）\n"
            "- masking_dict_key: data_chain 中存储脱敏字典的键"
        ),
    },

    "desc_DB_ACCESS": {
        "zh": (
            "提供通用数据库访问能力。连接数据库，执行 SQL 查询，\n"
            "将结果集存入 data_chain 的指定键。\n"
            "\n"
            "- db_type: 数据库类型 — sqlite, mysql, mssql, oracle, postgres（默认: \"sqlite\"）\n"
            "- db_host: 数据库主机地址（支持表达式）\n"
            "- db_port: 数据库端口（支持表达式）\n"
            "- db_name: 数据库名称/路径（支持表达式）\n"
            "- db_user: 数据库用户名（支持表达式）\n"
            "- db_pwd: 数据库密码（支持表达式和加密值）\n"
            "- sql: SQL 查询语句（支持表达式）\n"
            "- data_key: data_chain 中存储结果集的键\n"
            "- db_client_key: data_chain 中缓存数据库连接的键（可选）"
        ),
    },

    "desc_ENCODE_DECODE_STR": {
        "zh": (
            "使用指定算法对字符串进行编码或解码。支持 base64、base85、hexlify、\n"
            "a85 (Ascii85)、base16、base32 和 base32hex 等编码方案。\n"
            "\n"
            "- inbound: 输入字符串（支持表达式）\n"
            "- mode: \"encode\" 或 \"decode\"（默认: \"encode\"）\n"
            "- algorithm: 编码算法（默认: \"base64\"）\n"
            "- data_key: data_chain 中存储结果的键"
        ),
    },

    "desc_ENTER_FULLSCREEN": {
        "zh": (
            "将 chrome_name 对应的 Chrome 浏览器设为全屏模式。\n"
            "\n"
            "- chrome_name: data_chain 中存储 Chrome 驱动实例的键（默认: \"chrome\"）"
        ),
    },

    "desc_FIB": {
        "zh": (
            "计算从 0 到给定 seed 值的斐波那契数列。支持缓存（快速）和非缓存（慢速/递归）两种计算模式。\n"
            "结果以格式化字符串列表存储在 data_chain 中。\n"
            "\n"
            "- seed: 计算斐波那契数列的上限值（支持表达式）\n"
            "- use_cache: \"yes\" 使用缓存快速模式，\"no\" 使用递归慢速模式（默认: \"yes\"）\n"
            "- data_key: data_chain 中存储结果的键（默认: \"fib_result\"）"
        ),
    },

    "desc_FILE_CHOOSER": {
        "zh": (
            "通过 Selenium 找到文件上传元素，然后使用系统文件选择对话框选择要上传的文件。\n"
            "支持通过复制粘贴机制处理 Unicode 文件名。\n"
            "\n"
            "- file_path: 要上传的文件路径（支持表达式）\n"
            "- file_path_key: data_chain 中文件路径的键（优先于 file_path）\n"
            "- find_by: 定位上传元素的方式 — xpath 或 css\n"
            "- identity: 上传元素的定位值\n"
            "- chrome_name: data_chain 中 Chrome 驱动的键（默认: \"chrome\"）"
        ),
    },

    "desc_FILE_DELETE": {
        "zh": (
            "删除给定绝对路径下的文件。\n"
            "\n"
            "- file_path: 要删除的文件的绝对路径（支持表达式）"
        ),
    },

    "desc_FILE_WATCH_MOVE": {
        "zh": (
            "在超时时间内监视源文件出现，然后将其复制到目标位置。\n"
            "目标文件路径存储在 data_chain 的指定键中。\n"
            "\n"
            "- source_path: 源文件路径（支持表达式）\n"
            "- target_path: 目标文件路径（支持表达式）\n"
            "- data_key: data_chain 中存储目标路径的键\n"
            "- timeout: 等待文件出现的最大秒数（默认: 60）\n"
            "- overwrite: \"yes\" 覆盖已存在的目标文件（默认: \"yes\"）"
        ),
    },

    "desc_FIND_FILES": {
        "zh": (
            "使用可配置的 lambda 过滤器递归收集目录中的文件，按文件名和目录深度筛选。\n"
            "找到的文件路径列表存储在 data_chain 的指定键中。\n"
            "\n"
            "- path: 要搜索的目录路径（支持表达式）\n"
            "- data_key: data_chain 中存储文件列表的键\n"
            "- filter_fn: Python 函数体，按文件名过滤，参数为 \"filename\"（默认: \"return True\"）\n"
            "- depth_fn: Python 函数体，按目录深度过滤，参数为 \"depth\"（默认: \"return True\"）"
        ),
    },

    "desc_FIND_LATEST_FILE": {
        "zh": (
            "在指定文件夹中查找最近修改的指定类型的文件。\n"
            "\n"
            "- path_to_find: 要搜索的文件夹路径（支持表达式）\n"
            "- file_type: 文件扩展名过滤（如 \".csv\"、\".xlsx\"）\n"
            "- data_key: data_chain 中存储找到的文件路径的键"
        ),
    },

    "desc_FIND_MULTI_THEN_CLICK": {
        "zh": (
            "通过 Selenium 在超时时间内查找多个元素，然后逐个点击。\n"
            "\n"
            "- skip_fn: Python 函数体，决定是否跳过某元素，变量 \"ele\" 可用（默认: \"return ele is None\"）\n"
            "- find_by: 定位类型，\"xpath\" 或 \"css\"\n"
            "- identity: 目标元素的定位值（支持表达式）\n"
            "- wait: 点击之间的额外等待秒数（默认: 3）\n"
            "- timeout: 等待元素出现的最大秒数（默认: 10）"
        ),
    },

    "desc_FIND_MULTI_THEN_COLLECT": {
        "zh": (
            "通过 Selenium 查找多个元素，将其 text、value 或任意属性收集到列表中。\n"
            "\n"
            "- find_by: 定位类型，\"xpath\" 或 \"css\"\n"
            "- identity: 目标元素的定位值\n"
            "- value_type: 收集内容 — \"text\" 取 element.text，\"value\" 取输入值，\"ele\" 取元素本身，或任意属性名\n"
            "- value_key: data_chain 中存储收集列表的键（支持表达式）\n"
            "- wait: 定位前的额外等待秒数（默认: 5）\n"
            "- timeout: 等待元素出现的最大秒数（默认: 10）\n"
            "- skip_fn: Python 函数体，跳过元素的条件，变量 \"ele\" 可用（默认: \"return ele is None\"）\n"
            "- sort_lambda: Python 表达式，用于排序，变量 \"item\" 可用（默认: \"item\"）\n"
            "- sort_reverse: \"yes\" 降序排列（默认: \"no\"）"
        ),
    },

    "desc_FIND_THEN_CLICK": {
        "zh": (
            "通过 Selenium 使用指定的定位策略查找 Web 元素并点击。\n"
            "如果在超时时间内未找到元素，除非设置了 skip_timeout_error 否则抛出异常。\n"
            "\n"
            "- find_by: 定位类型 — id、xpath 或 css\n"
            "- identity: 目标元素的定位值（支持表达式）\n"
            "- condition_fn: Python 函数体，点击前的条件检查，参数为 \"ele\"（可选）\n"
            "- timeout: 等待元素出现的最大秒数（默认: 10）\n"
            "- wait: 点击后的额外等待秒数（默认: 0）\n"
            "- skip_timeout_error: \"yes\" 超时不报错（默认: \"no\"）\n"
            "- chrome_name: data_chain 中 Chrome 驱动的键（默认: \"chrome\"）"
        ),
    },

    "desc_FIND_THEN_COLLECT": {
        "zh": (
            "通过 Selenium 查找单个元素，收集其 text、value 或任意属性，存入 data_chain。\n"
            "\n"
            "- find_by: 定位类型 — id、xpath 或 css\n"
            "- identity: 目标元素的定位值\n"
            "- value_type: 收集内容 — \"text\" 取 element.text，\"value\" 取输入值，或任意属性/属性名（默认: \"text\"）\n"
            "- value_key: data_chain 中存储收集值的键（支持表达式）\n"
            "- timeout: 等待元素出现的最大秒数（默认: 10）\n"
            "- wait: 定位前的额外等待秒数（默认: 1）"
        ),
    },

    "desc_FIND_THEN_KEYIN": {
        "zh": (
            "调用 Chrome 驱动定位 Web 元素，然后通过 send_keys 模拟键盘输入。\n"
            "支持输入字符串或按特殊键（KEY_ENTER、KEY_TAB 等）。\n"
            "\n"
            "- find_by: 元素定位策略 — id、xpath 或 css（支持表达式）\n"
            "- identity: 用于定位元素的值（支持表达式）\n"
            "- value: 要输入的字符串或 KEY_* 常量（支持表达式）\n"
            "- value_key: data_chain 中读取输入值的键；支持 \";\" 嵌套访问（支持表达式）\n"
            "- clear_before_input: \"yes\" 输入前清除已有内容（默认: \"yes|no\"）\n"
            "- wait: 定位后输入前的额外等待秒数（默认: 1）"
        ),
    },

    "desc_FOLDER_WATCH_MOVE": {
        "zh": (
            "将文件从源文件夹移动到目标文件夹。支持等待预期文件数量或超时后移动。\n"
            "\n"
            "- source_path: 要监视的源文件夹路径（支持表达式）\n"
            "- target_path: 目标文件夹路径（支持表达式）\n"
            "- data_key: data_chain 中存储目标文件路径列表的键\n"
            "- expect_count: 预期文件数量（默认: 1）\n"
            "- timeout: 等待文件的最大秒数（默认: 60）"
        ),
    },

    "desc_GET_COOKIE": {
        "zh": (
            "从 Chrome 驱动获取 Cookie 并存入 data_chain 的 value_key 中。\n"
            "当 get_all 为 \"yes\" 时，返回所有 Cookie 的 \"name=value; name=value;\" 格式字符串。\n"
            "\n"
            "- chrome_name: data_chain 中 Chrome 驱动的键（默认: \"chrome\"）\n"
            "- value_key: data_chain 中存储 Cookie 的键\n"
            "- cookie_name: 要获取的特定 Cookie 名称（get_all=\"no\" 时使用）\n"
            "- get_all: \"yes\" 获取所有 Cookie（默认: \"no\"）"
        ),
    },

    "desc_GO_BACK": {
        "zh": (
            "使浏览器导航到上一页，等同于点击浏览器后退按钮。\n"
            "\n"
            "- chrome_name: data_chain 中存储 Chrome 驱动实例的键（默认: \"chrome\"）"
        ),
    },

    "desc_GO_TO_PAGE": {
        "zh": (
            "通过 Selenium 启动 Chrome 浏览器并导航到指定 URL。通常是 Web 相关执行的第一个任务。\n"
            "\n"
            "- page_load_timeout_seconds: 等待页面加载的最大秒数（默认: \"180\"）\n"
            "- url: 目标 URL（支持表达式）\n"
            "- chrome_name: data_chain 中存储 Chrome 驱动的键（默认: \"chrome\"）\n"
            "- headless: \"yes\" 使用无头模式（默认: \"no\"）\n"
            "- user_data_dir: Chrome 用户数据目录路径（可选，支持表达式）\n"
            "- profile_directory: Chrome 配置文件目录名（可选）"
        ),
    },

    "desc_GO_TO_TASK": {
        "zh": (
            "在当前执行中有条件地跳转到指定任务。\n"
            "当条件评估为 True 时，从目标任务继续执行而非下一个顺序任务。为 False 时正常继续。\n"
            "\n"
            "- condition: Python 表达式，评估为 True 时执行跳转\n"
            "- task_idx: 要跳转到的目标任务索引（从 0 开始）\n"
            "- max_times: 最大跳转次数限制，防止无限循环（默认: 100）"
        ),
    },

    "desc_HASH_STR": {
        "zh": (
            "使用指定算法对字符串进行哈希并将十六进制摘要存入 data_chain。\n"
            "\n"
            "- inbound: 要哈希的输入字符串（支持表达式）\n"
            "- algorithm: 哈希算法（默认: \"sha256\"）\n"
            "- data_key: data_chain 中存储结果的键"
        ),
    },

    "desc_HTTP_REQUEST": {
        "zh": (
            "发送 HTTP 请求 (get/post 等) 到 request_url，通过 resp_fn 处理响应，结果存入 value_key。\n"
            "支持通过 session_key 持久化会话，内置 Basic Auth 和 OAuth 认证。\n"
            "\n"
            "- timeout: 请求超时秒数（默认: 60）\n"
            "- session_key: data_chain 中存储/获取 requests.Session 的键（默认: \"__session_key\"）\n"
            "- resp_fn: Python 函数体处理响应，变量 \"response\" 可用\n"
            "- request_url: HTTP 请求目标 URL（支持表达式）\n"
            "- headers: HTTP 头部，\"key[>value|key2[>value2\" 格式（支持表达式）\n"
            "- method: HTTP 方法 — get、post、put、delete（默认: \"get\"）\n"
            "- params: URL 查询参数（支持表达式）\n"
            "- data_raw: 原始请求体字符串（支持表达式）\n"
            "- data: 表单数据（支持表达式）\n"
            "- data_key: data_chain 中获取请求体数据的键\n"
            "- value_key: data_chain 中存储处理后响应的键（支持表达式）\n"
            "- verify: \"yes\" 启用 SSL 验证，\"no\" 跳过（默认: \"yes\"）\n"
            "- is_zip_response: \"yes\" 将响应作为 zip 文件提取内容（默认: \"no\"）\n"
            "- filter_fn: zip 响应时按文件名过滤的函数体\n"
            "- convert_fn: zip 响应时转换文件内容的函数体\n"
            "- basic_auth_user: Basic Auth 用户名（支持表达式）\n"
            "- basic_auth_pwd: Basic Auth 密码（支持表达式和加密值）\n"
            "- oauth_token_url: OAuth 令牌端点 URL（支持表达式）\n"
            "- oauth_client_id: OAuth client_id（支持表达式）\n"
            "- oauth_client_secret: OAuth client_secret（支持表达式和加密值）\n"
            "- oauth_scope: OAuth scope（可选）\n"
            "- oauth_token: Bearer 令牌值或缓存键（支持表达式）\n"
            "- xsrf_token_url: XSRF/CSRF 令牌获取 URL（支持表达式）\n"
            "- xsrf_token_header: XSRF 令牌头名称（默认: \"X-CSRF-Token\"）"
        ),
    },

    "desc_HTTP_RESPONSE_KEY": {
        "zh": (
            "从 HTTP 服务调用 PETP 时必需。指定哪个 data_chain 键的值作为 HTTP 响应体返回。\n"
            "\n"
            "- response_key: data_chain 中作为 HTTP 响应返回的数据键"
        ),
    },

    "desc_INITIAL_PARAMS": {
        "zh": (
            "初始化键值对并保存到 data_chain。所有参数都作为键值对处理。\n"
            "值支持 expression2str 进行动态求值。\n"
            "\n"
            "- (任意键): 要初始化的键名及其对应值（支持表达式）"
        ),
    },

    "desc_INPUT_DIALOG": {
        "zh": (
            "在运行时显示弹窗文本输入对话框以收集用户输入，将输入值存入 data_chain。\n"
            "支持在用户取消对话框时停止执行。\n"
            "\n"
            "- title: 对话框标题（支持表达式）\n"
            "- message: 提示消息（支持表达式）\n"
            "- data_key: data_chain 中存储输入值的键\n"
            "- default_value: 默认输入值（支持表达式）\n"
            "- stop_if_cancel: \"yes\" 用户取消时停止执行（默认: \"yes\"）\n"
            "- multiline: \"yes\" 显示多行文本框（默认: \"no\"）"
        ),
    },

    "desc_MATPLOTLIB": {
        "zh": (
            "发送 PETPEvent 在弹窗中启动 Matplotlib 图表视图。\n"
            "支持 PIE（饼图）、LINE（折线图）和 BAR（柱状图）类型。\n"
            "\n"
            "- chart_type: 图表类型 — PIE、LINE 或 BAR\n"
            "- title: 图表标题（支持表达式）\n"
            "- data_key: data_chain 中图表数据的键\n"
            "- labels_key: data_chain 中标签数据的键\n"
            "- x_label: X 轴标签（可选）\n"
            "- y_label: Y 轴标签（可选）\n"
            "- position: 窗口位置 \"x,y\"（可选）\n"
            "- size: 窗口尺寸 \"w,h\"（可选）"
        ),
    },

    "desc_MOUSE_CLICK": {
        "zh": (
            "在位置 (x, y) 执行鼠标点击。如果 x 和 y 都为 -1，使用 data_chain 中的位置。\n"
            "\n"
            "- x_from: data_chain 中存储 x 坐标的键（默认: \"mouse_at_x\"）\n"
            "- y_from: data_chain 中存储 y 坐标的键（默认: \"mouse_at_y\"）\n"
            "- x: 点击的 x 坐标，-1 使用 data_chain 位置（默认: -1）\n"
            "- y: 点击的 y 坐标，-1 使用 data_chain 位置（默认: -1）\n"
            "- clicks: 点击次数（默认: 1）"
        ),
    },

    "desc_MOUSE_POSITION": {
        "zh": (
            "获取当前鼠标位置 (x, y)，通过 data_key_x 和 data_key_y 保存到 data_chain。\n"
            "\n"
            "- data_key_x: data_chain 中存储 x 坐标的键（默认: \"mouse_at_x\"）\n"
            "- data_key_y: data_chain 中存储 y 坐标的键（默认: \"mouse_at_y\"）\n"
            "- wait: 获取位置前的等待秒数（默认: 3）"
        ),
    },

    "desc_MOUSE_SCROLL": {
        "zh": (
            "在位置 (x, y) 执行鼠标滚动。如果 x 和 y 都为 -1，使用 data_chain 中的位置。\n"
            "\n"
            "- x_from: data_chain 中存储 x 坐标的键（默认: \"mouse_at_x\"）\n"
            "- y_from: data_chain 中存储 y 坐标的键（默认: \"mouse_at_y\"）\n"
            "- x: 滚动位置的 x 坐标，-1 使用 data_chain 位置（默认: -1）\n"
            "- y: 滚动位置的 y 坐标，-1 使用 data_chain 位置（默认: -1）\n"
            "- scroll: 垂直滚动量，正数向上，负数向下（默认: 0）\n"
            "- clicks: 滚动次数（默认: 1）"
        ),
    },

    "desc_MOVE_TO_IFRAME": {
        "zh": (
            "将 Chrome 驱动上下文切换到指定 iframe，支持通过多个 frame ID 访问嵌套 iframe。\n"
            "\n"
            "- frame_ids: frame 标识符列表（索引、名称或 id），如 [\"frame1\", \"frame2\"]"
        ),
    },

    "desc_NESTED_TO_FLAT_CONVERTOR": {
        "zh": (
            "将嵌套字典转换为扁平字典。支持嵌套的字典和列表。\n"
            "\n"
            "- data: 要转换的嵌套 JSON 字符串（data_key 未设置时使用）\n"
            "- data_key: data_chain 中嵌套数据的键（优先于 data）\n"
            "- value_key: data_chain 中存储扁平化结果的键\n"
            "- separator: 键连接分隔符（默认: \".\"）\n"
            "- prefix: 扁平键的前缀（可选）"
        ),
    },

    "desc_OCR": {
        "zh": (
            "使用本地 OCR 从图片中提取文字（无需 API 密钥）。\n"
            "支持中文、英文及多种其他语言。\n"
            "\n"
            "支持的引擎（按优先级）:\n"
            "- paddleocr: 高精度，推荐用于中文（pip install paddleocr paddlepaddle）\n"
            "- rapidocr: 轻量级替代方案（pip install rapidocr_onnxruntime）\n"
            "- easyocr: 多语言支持（pip install easyocr）\n"
            "\n"
            "- image_path: 图片文件路径（支持表达式）\n"
            "- image_path_key: data_chain 中图片路径的键（优先于 image_path）\n"
            "- data_key: data_chain 中存储结果的键（默认: \"ocr_result\"）\n"
            "- lang: 识别语言（默认: \"ch\"）\n"
            "- engine: OCR 引擎 — paddleocr、rapidocr 或 easyocr（默认: 自动选择）"
        ),
    },

    "desc_OPEN_FILE": {
        "zh": (
            "使用系统默认应用程序打开文件。在给定超时内等待文件存在。\n"
            "文件路径可直接提供或通过 data_chain 键获取。\n"
            "\n"
            "- file_path: 要打开的文件路径（支持表达式）\n"
            "- file_path_key: data_chain 中文件路径的键（优先于 file_path）\n"
            "- timeout: 等待文件存在的最大秒数（默认: 10）\n"
            "- wait_after: 打开后的等待秒数（默认: 1）"
        ),
    },

    "desc_PYTUBE": {
        "zh": (
            "通过 pytube 下载指定链接的 YouTube 视频，支持不同的视频格式和分辨率。\n"
            "\n"
            "- video_url: YouTube 视频 URL（支持表达式）\n"
            "- output_path: 下载输出目录路径（支持表达式）\n"
            "- data_key: data_chain 中存储下载路径的键\n"
            "- resolution: 视频分辨率（如 \"720p\"、\"1080p\"，默认: \"720p\"）\n"
            "- file_extension: 视频格式（默认: \"mp4\"）\n"
            "- only_audio: \"yes\" 只下载音频（默认: \"no\"）"
        ),
    },

    "desc_READ_CSV": {
        "zh": (
            "从指定位置加载 CSV 文件，将数据读入二维数组并保存到 data_chain。\n"
            "\n"
            "- file_path: CSV 文件路径（支持表达式）\n"
            "- data_key: data_chain 中存储数据的键\n"
            "- encoding: 文件编码（默认: \"utf-8\"）\n"
            "- delimiter: CSV 分隔符（默认: \",\"）\n"
            "- skip_first: \"yes\" 跳过首行（默认: \"no\"）"
        ),
    },

    "desc_READ_EXCEL": {
        "zh": (
            "加载 MS Excel 文件，将数据读入二维数组并保存到 data_chain。支持字段过滤和跳行。\n"
            "\n"
            "- file_path: Excel 文件路径（支持表达式）\n"
            "- data_key: data_chain 中存储数据的键\n"
            "- sheet_name: 工作表名称（可选，默认第一个）\n"
            "- fields: 要读取的列索引列表，如 \"0,1,3\"（可选，默认全部）\n"
            "- skip_first: \"yes\" 跳过首行（默认: \"no\"）\n"
            "- max_rows: 最大读取行数（可选）"
        ),
    },

    "desc_READ_JSON": {
        "zh": (
            "从文件加载 JSON，可选通过 json_path 提取数据，然后保存到 data_chain。\n"
            "\n"
            "- file_path: JSON 文件路径（支持表达式）\n"
            "- data_key: data_chain 中存储数据的键\n"
            "- json_path: JSONPath 表达式提取特定数据（可选）\n"
            "- encoding: 文件编码（默认: \"utf-8\"）"
        ),
    },

    "desc_READ_TEXT_FROM_FILE": {
        "zh": (
            "读取文本文件的全部内容并存入 data_chain 的指定键。\n"
            "\n"
            "- file_path: 要读取的文本文件路径（支持表达式）\n"
            "- data_key: data_chain 中存储内容的键\n"
            "- encoding: 文件编码（默认: \"utf-8\"）"
        ),
    },

    "desc_RELOAD_LOG": {
        "zh": (
            "触发 PETP UI 中日志窗口的刷新以显示最新日志条目。\n"
            "在一系列任务后确保日志视图是最新的。\n"
            "\n"
            "- (无参数)"
        ),
    },

    "desc_RUN_EXECUTION": {
        "zh": (
            "按名称运行（触发）指定的执行，支持可选参数。如果 if_stop 设为 \"yes\"，执行将被完全跳过。\n"
            "\n"
            "- execution: 要运行的执行名称（支持表达式）\n"
            "- if_stop: \"yes\" 跳过执行（默认: \"no\"）\n"
            "- init_data: 初始化数据 JSON 字符串（可选）"
        ),
    },

    "desc_RUN_JAVASCRIPT": {
        "zh": (
            "使用 PythonMonkey 运行时执行外部 .js 文件中的 JavaScript 函数。\n"
            "JS 文件应导出一个接受单个参数（对象/字典）并返回单个结果对象的模块函数。\n"
            "JS 代码段全局缓存以提高性能。\n"
            "\n"
            "- js_file: JavaScript 文件路径（支持表达式）\n"
            "- func_name: 要调用的导出函数名（支持表达式）\n"
            "- input_key: data_chain 中作为输入传递的数据键\n"
            "- data_key: data_chain 中存储 JS 执行结果的键\n"
            "- source_type: \"file\" 或 \"inline\"（默认: \"file\"）"
        ),
    },

    "desc_RUN_SFTP_GET": {
        "zh": (
            "通过 paramiko SFTP 客户端从远程服务器下载文件到本地。\n"
            "\n"
            "- from_remote: 远程文件路径（支持表达式）\n"
            "- to_local: 本地目标文件路径（支持表达式）\n"
            "- sftp_client_key: data_chain 中 SFTP 客户端的键（默认: \"sftpclient\"）\n"
            "- close_after_run: \"yes\" 下载后关闭 SFTP 连接（默认: \"yes\"）\n"
            "- data_key: data_chain 中存储本地路径的键（可选）"
        ),
    },

    "desc_RUN_SFTP_PUT": {
        "zh": (
            "通过 paramiko SFTP 客户端从本地上传文件到远程服务器。\n"
            "\n"
            "- from_local: 本地文件路径（支持表达式）\n"
            "- to_remote: 远程目标文件路径（支持表达式）\n"
            "- sftp_client_key: data_chain 中 SFTP 客户端的键（默认: \"sftpclient\"）\n"
            "- close_after_run: \"yes\" 上传后关闭 SFTP 连接（默认: \"yes\"）"
        ),
    },

    "desc_RUN_SSH_COMMAND": {
        "zh": (
            "通过 paramiko 运行 SSH 命令，将结果保存到 data_chain 的 data_key 中。\n"
            "\n"
            "- ssh_client_key: data_chain 中存储 SSH 客户端实例的键（默认: \"sshclient\"）\n"
            "- cmd: 要执行的 SSH 命令（支持表达式）\n"
            "- data_key: data_chain 中存储命令输出的键\n"
            "- close_after_run: \"yes\" 运行后关闭 SSH 客户端（默认: \"yes\"）"
        ),
    },

    "desc_SCREENSHOT": {
        "zh": (
            "对当前浏览器页面或指定元素进行截图并保存到文件。\n"
            "\n"
            "- file_path: 截图保存路径（支持表达式）\n"
            "- file_path_key: data_chain 中截图路径的键（优先于 file_path）\n"
            "- chrome_name: data_chain 中 Chrome 驱动的键（默认: \"chrome\"）\n"
            "- element_xpath: 要截图的元素 xpath（可选，默认整个页面）"
        ),
    },

    "desc_SEND_EMAIL": {
        "zh": (
            "通过 SMTP 发送电子邮件。支持 HTML 正文和附件。\n"
            "\n"
            "- smtp_host: SMTP 服务器地址（支持表达式）\n"
            "- smtp_port: SMTP 服务器端口（默认: 465）\n"
            "- smtp_user: SMTP 用户名/发件人（支持表达式）\n"
            "- smtp_pwd: SMTP 密码（支持表达式和加密值）\n"
            "- to: 收件人地址，多个用逗号分隔（支持表达式）\n"
            "- subject: 邮件主题（支持表达式）\n"
            "- body: 邮件正文内容（支持表达式）\n"
            "- is_html: \"yes\" 正文为 HTML 格式（默认: \"no\"）\n"
            "- attachments: 附件文件路径，多个用逗号分隔（支持表达式，可选）"
        ),
    },

    "desc_SHOW_RESULT": {
        "zh": (
            "在 PETP UI 中显示弹窗对话框展示结果信息。在后台模式下记录日志。\n"
            "\n"
            "- title: 弹窗标题（支持表达式）\n"
            "- message: 弹窗消息内容（支持表达式）"
        ),
    },

    "desc_STOPPER": {
        "zh": (
            "停止当前执行。可通过条件控制是否停止。\n"
            "\n"
            "- condition: Python 表达式，为 True 时停止执行（可选，默认无条件停止）\n"
            "- message: 停止时的日志消息（支持表达式，可选）"
        ),
    },

    "desc_UNZIP": {
        "zh": (
            "将 zip 文件从 path_to_zip_file 解压到 directory_to_extract。如有密码保护，使用 pwd。\n"
            "path_after_extract_key 是 data_chain 的键，指向解压后的最终路径。\n"
            "\n"
            "- path_to_zip_file: 要解压的源 zip 文件路径（支持表达式）\n"
            "- directory_to_extract: 文件解压到的目标目录（支持表达式）\n"
            "- path_after_extract_key: data_chain 中存储最终解压路径的键（默认: \"path_after_extract\"）\n"
            "- pwd: 受保护 zip 文件的密码（支持表达式）\n"
            "- name_appended: 附加到 directory_to_extract 形成最终路径的子路径（默认: \"\"）"
        ),
    },

    "desc_WAIT_FOR": {
        "zh": (
            "等待指定条件满足或超时。通过轮询 data_chain 检查条件。\n"
            "\n"
            "- condition: Python 表达式，为 True 时结束等待\n"
            "- timeout: 最大等待秒数（默认: 60）\n"
            "- interval: 轮询间隔秒数（默认: 1）\n"
            "- message: 等待时的日志消息（可选）"
        ),
    },

    "desc_WAIT_SECONDS": {
        "zh": (
            "暂停执行指定的秒数。\n"
            "\n"
            "- seconds: 等待秒数（支持表达式，默认: 1）"
        ),
    },

    "desc_WRITE_TO_EXCEL": {
        "zh": (
            "将二维数组数据写入 Excel 文件。\n"
            "\n"
            "- file_path: Excel 文件输出路径（支持表达式）\n"
            "- data_key: data_chain 中二维数组数据的键\n"
            "- sheet_name: 工作表名称（默认: \"Sheet1\"）\n"
            "- headers: 列标题列表（可选）"
        ),
    },

    "desc_WRITE_TO_FILE": {
        "zh": (
            "将文本内容写入文件。\n"
            "\n"
            "- file_path: 目标文件路径（支持表达式）\n"
            "- content: 要写入的文本内容（支持表达式）\n"
            "- content_key: data_chain 中内容的键（优先于 content）\n"
            "- mode: 写入模式 — \"w\" 覆盖，\"a\" 追加（默认: \"w\"）\n"
            "- encoding: 文件编码（默认: \"utf-8\"）"
        ),
    },

    "desc_ZIP": {
        "zh": (
            "将文件或文件夹压缩为 zip 文件。\n"
            "\n"
            "- source_path: 要压缩的源文件夹路径（支持表达式）\n"
            "- source_list: data_chain 中文件路径列表的键（替代 source_path）\n"
            "- zip_name: 输出 zip 文件名（支持表达式）\n"
            "- target_path: 输出 zip 文件的目标目录（支持表达式）\n"
            "- path_in_zip: zip 内部的路径前缀（可选）\n"
            "- path_to_replace: 从文件路径中移除的前缀（可选）"
        ),
    },


    # === Tooltips — task editor ===
    "tip_add_row": {"en": "Add new row", "zh": "添加新行"},
    "tip_delete_row": {"en": "delete selected row(s)", "zh": "删除选中行"},
    "tip_select_recording": {
        "en": "Select the recording file exported from Chrome DevTools Recorder.",
        "zh": "选择由 Chrome DevTools Recorder 导出的录制文件。",
    },
    "tip_convert_recording": {
        "en": "Convert recording into PETP Task(s), insert before selected task, otherwise append to the tail",
        "zh": "将录制内容转换为 PETP 任务, 在选中任务前依次插入，不选追加到任务列表尾部",
    },

    # === Tooltips — loop editor ===
    "tip_add_property": {"en": "Add property", "zh": "添加属性"},
    "tip_delete_property": {"en": "delete selected property", "zh": "删除选中属性"},
    "tip_edit_loop": {"en": "Edit selected loop", "zh": "编辑选中循环"},
    "btn_edit_loop": {"en": "⚙️", "zh": "⚙️"},

    # === Tooltips — input editor ===
    "tip_available_properties": {"en": "Available Properties", "zh": "可用属性"},
    "tip_add_prop": {"en": "Add propery", "zh": "添加属性"},
    "tip_delete_prop": {"en": "delete selected property", "zh": "删除选中属性"},
    "tip_skip_task": {"en": "check to skip current task", "zh": "勾选以跳过当前任务"},
    "tip_fill_date": {"en": "Fill date to selected property", "zh": "将日期填入选中属性"},

    # === Tooltips — handy buttons ===
    "tip_handy_tools": {"en": "Quick insert helpers", "zh": "快捷插入工具"},
    "tip_rdir": {"en": "get resources dir ", "zh": "获取资源目录"},
    "tip_ddir": {"en": "get download dir ", "zh": "获取下载目录"},
    "tip_pwd": {"en": "Prevent to save password into files", "zh": "防止将密码保存到文件中"},

    # === Handy tools menu items ===
    "handy_rdir": {"en": "Resources Dir\t{self.get_rdir()}/", "zh": "资源目录\t{self.get_rdir()}/"},
    "handy_ddir": {"en": "Download Dir\t{self.get_ddir()}/", "zh": "下载目录\t{self.get_ddir()}/"},
    "handy_tdir": {"en": "Test Dir\t{self.get_tdir()}/", "zh": "测试目录\t{self.get_tdir()}/"},
    "handy_encrypt": {"en": "Encrypt / Decrypt Password", "zh": "加密 / 解密密码"},
    "handy_get_data": {"en": "get_data(\"\")", "zh": "get_data(\"\")"},
    "handy_get_data_by_loop": {"en": "get_data_by_loop(\"\")", "zh": "get_data_by_loop(\"\")"},
    "handy_get_deep_data": {"en": "get_deep_data([\"\",\"\"])", "zh": "get_deep_data([\"\",\"\"])"},
    "handy_date_str": {"en": "Date String\t{self.get_now_str()}", "zh": "日期字符串\t{self.get_now_str()}"},
    "handy_os_sep": {"en": "OS Separator\t{os.sep}", "zh": "系统路径分隔符\t{os.sep}"},
    "handy_str2dict": {"en": "str2dict(\"k1|>v1\")", "zh": "str2dict(\"k1|>v1\")"},
    "handy_feed_tpl": {"en": "feed_tpl(\"tpl\", {})", "zh": "feed_tpl(\"tpl\", {})"},
    "handy_prop2dict": {"en": "prop2dict(\"k=v\")", "zh": "prop2dict(\"k=v\")"},
    "handy_json2dict": {"en": "json2dict(\"json\")", "zh": "json2dict(\"json\")"},
    "handy_json_dumps": {"en": "json.dumps(obj)", "zh": "json.dumps(obj)"},
    "handy_json_loads": {"en": "json.loads(str)", "zh": "json.loads(str)"},
    "handy_str2list": {"en": "str2list(\"a|>b\")", "zh": "str2list(\"a|>b\")"},
    "handy_get_sdir": {"en": "Shared Dir\t{self.get_sdir()}/", "zh": "共享目录\t{self.get_sdir()}/"},
    "btn_handy_tools": {"en": "🧰", "zh": "🧰"},

    # === Tooltips — execution actions ===
    "tip_delete_execution": {"en": "Delete selected Execution", "zh": "删除选中的Execution"},
    "tip_copy_execution": {"en": "Copy selected Execution", "zh": "复制选中Execution"},
    "tip_save_execution": {"en": "Save or Update selected Execution", "zh": "保存或更新选中的Execution"},
    "tip_execute_on_startup": {"en": "Execute on startup", "zh": "启动时运行"},
    "tip_change_log_level": {"en": "Change Log Level", "zh": "更改日志级别"},
    "tip_reload_log": {"en": "reload log ", "zh": "重新加载日志"},
    "tip_clean_log": {"en": "Clean log console", "zh": "清空日志控制台"},
    "tip_change_lang": {"en": "Change Language", "zh": "切换语言"},
    "tip_change_theme": {"en": "Change Theme", "zh": "切换主题"},
    "tip_exec_desc": {"en": "Execution description", "zh": "Execution描述"},
    "tip_as_mcp_tool": {
        "en": "Publish current Execution as PETP MCP tool ",
        "zh": "发布当前Execution PETP MCP Tool",
    },
    "astool_on": {
        "en": "Published as MCP Tool",
        "zh": "已发布为 MCP Tool",
    },
    "astool_off": {
        "en": "Not published as MCP Tool",
        "zh": "尚未发布为 MCP Tool",
    },
    "only_tool_on": {
        "en": "Tool",
        "zh": "工具",
    },
    "only_tool_off": {
        "en": "All",
        "zh": "全部",
    },
    "tip_only_tool": {
        "en": "Show only executions published as MCP tools",
        "zh": "仅显示已发布为 MCP Tool 的 Execution",
    },
    "warn_missing_response_key": {
        "en": "The last Task should be HTTP_RESPONSE_KEY to provide the final result, otherwise please specify Output Parameters instead.",
        "zh": "最后一个 Task 应为 HTTP_RESPONSE_KEY 以提供最终结果，或者请配置输出参数作为替代。",
    },
    "warn_astool_no_output_config": {
        "en": "This execution is marked as MCP tool but has neither HTTP_RESPONSE_KEY as last task nor Output Parameters configured. Please add one of them before saving.",
        "zh": "此执行被标记为 MCP 工具，但既没有 HTTP_RESPONSE_KEY 作为最后一个 Task，也没有配置输出参数。请先添加其中之一再保存。",
    },
    "prompt_sync_initial_params": {
        "en": "The first task is not INITIAL_PARAMS. Convert Input Parameters to an INITIAL_PARAMS task as the first task?",
        "zh": "第一个 Task 不是 INITIAL_PARAMS。是否将输入参数转换为首个 INITIAL_PARAMS Task？",
    },

    # === MCP Description Editor ===
    "mcp_lbl_tool_desc": {"en": "Description:", "zh": "工具描述："},
    "mcp_lbl_input_params": {"en": "Input Parameters:", "zh": "输入参数："},
    "mcp_lbl_output_params": {"en": "Output Parameters:", "zh": "输出参数："},
    "mcp_col_name": {"en": "Name", "zh": "名称"},
    "mcp_col_type": {"en": "Type", "zh": "类型"},
    "mcp_col_desc": {"en": "Description", "zh": "描述"},
    "mcp_col_required": {"en": "Required", "zh": "必填"},
    "mcp_col_default": {"en": "Default", "zh": "默认值"},
    "mcp_col_map_key": {"en": "Map To DataChain Key", "zh": "映射DataChain键"},
    "mcp_tip_add_input": {"en": "Add input parameter", "zh": "添加输入参数"},
    "mcp_tip_del_input": {"en": "Remove selected input parameter", "zh": "删除选中的输入参数"},
    "mcp_tip_add_output": {"en": "Add output parameter", "zh": "添加输出参数"},
    "mcp_tip_del_output": {"en": "Remove selected output parameter", "zh": "删除选中的输出参数"},
    "mcp_tip_tool_desc": {"en": "Brief description of what this tool does", "zh": "简要描述此工具的功能"},
    "mcp_tip_preview_json": {"en": "Preview generated JSON", "zh": "预览生成的JSON"},

    # === Tooltips — pipeline actions ===
    "tip_add_row_p": {"en": "Add row", "zh": "添加行"},
    "tip_delete_row_p": {"en": "Delete selected row(s)", "zh": "删除选中行"},
    "tip_delete_pipeline": {"en": "Delete selected Pipeline", "zh": "删除选中的流水线"},
    "tip_save_pipeline": {"en": "Save or Update selected Pipeline", "zh": "保存或更新选中的流水线"},
    "tip_stop_cron": {
        "en": "Stop selected Pipeline which is running as cron",
        "zh": "停止以定时任务运行的选中流水线",
    },
    "tip_stop_all_cron": {"en": "Stop all pipelines running as cron.", "zh": "停止所有以定时任务运行的流水线。"},
    "btn_cron_history": {"en": "History", "zh": "历史记录"},
    "tip_cron_history": {"en": "View cron execution history", "zh": "查看定时任务执行历史"},

    # === Cron Dashboard dialog ===
    "dlg_cron_dashboard_title": {"en": "Cron Execution History", "zh": "定时任务执行历史"},
    "cron_col_start_time": {"en": "Start Time", "zh": "开始时间"},
    "cron_col_pipeline": {"en": "Pipeline", "zh": "流水线"},
    "cron_col_cron_exp": {"en": "Cron Exp", "zh": "Cron 表达式"},
    "cron_col_status": {"en": "Status", "zh": "状态"},
    "cron_col_duration": {"en": "Duration", "zh": "耗时"},
    "cron_col_error": {"en": "Error", "zh": "错误"},
    "cron_filter_hint": {"en": "Filter by pipeline name…", "zh": "按流水线名称过滤…"},
    "cron_lbl_filter": {"en": "Filter:", "zh": "过滤："},
    "btn_refresh": {"en": "Refresh", "zh": "刷新"},

    # === IF_ELSE processor ===
    "desc_IF_ELSE": {
        "zh": (
            "条件分支 — 根据条件跳过 'then' 或 'else' 任务块。\n"
            "- condition_fn: Python 函数体 (data_chain) → bool。True 执行 then 块，False 执行 else 块。\n"
            "- then_tasks: 紧随本任务之后组成 'then' 块的任务数量（默认: 1）\n"
            "- else_tasks: then 块之后组成 'else' 块的任务数量（默认: 0）\n\n"
            "支持在循环内使用：每次迭代重新评估条件，可访问循环变量（loop_idx、loop_item）。\n\n"
            "约束：\n"
            "- then/else 块不能跨越循环边界（必须在同一 loop 范围内）\n"
            "- 不支持嵌套 IF_ELSE（内层会覆盖外层的跳过范围）\n"
            "- 不要与 GO_TO_TASK 跳入/跳出 then/else 块组合使用\n"
            "- then_tasks + else_tasks 计数必须准确"
        ),
    },

    # === Tooltips — chooser ===
    "tip_exec_chooser": {
        "en": "Select or search Execution (type to filter)",
        "zh": "选择或搜索Execution（输入以筛选）",
    },
    "tip_pipeline_chooser": {
        "en": "Select or search Pipeline (type to filter)",
        "zh": "选择或搜索Pipeline（输入以筛选）",
    },

    # === Grid column headers ===
    "grid_task_chooser": {"en": "Task Chooser", "zh": "Task选择"},
    "grid_task_desc": {"en": "Description", "zh": "描述"},
    "grid_input": {"en": "Input", "zh": "输入"},
    "grid_exec_chooser": {"en": "Execution Chooser", "zh": "Execution选择"},

    # === Context menu ===
    "menu_copy": {"en": "Copy", "zh": "复制"},
    "menu_paste": {"en": "Paste", "zh": "粘贴"},
    "menu_skip_task": {"en": "Skip", "zh": "跳过"},
    "menu_unskip_task": {"en": "Unskip", "zh": "取消跳过"},
    "menu_view_processor_usage": {"en": "View Processor Usage", "zh": "查看Processor用法"},
    "menu_find_referencing_executions": {"en": "Find References of {name}", "zh": "查找{name}的引用"},
    "dlg_processor_usage_title": {"en": "Processor Usage", "zh": "Processor 用法"},
    "dlg_referencing_executions_title": {"en": "References of {name}", "zh": "{name}的引用"},
    "dlg_no_referencing_executions": {"en": "No executions reference {name}.",
                                      "zh": "没有Execution引用{name}。"},
    "menu_copy_name": {"en": "Copy Name", "zh": "复制名"},
    "menu_copy_value": {"en": "Copy Value", "zh": "复制值"},
    "menu_copy_pair": {"en": "Copy Name+Value", "zh": "复制Name+Value"},
    "menu_paste_pair": {"en": "Paste Name+Value", "zh": "粘贴Name+Value"},
    "menu_edit_complex": {"en": "Edit Complex Value", "zh": "编辑复杂值"},
    "menu_rename_key": {"en": "Edit Name", "zh": "修改名"},
    "menu_param_hint": {"en": "Property Description", "zh": "属性介绍"},
    "param_hint_not_found": {"en": "No description found for \"{name}\".", "zh": "未找到\"{name}\"的属性介绍。"},
    "dlg_rename_key_title": {"en": "Edit Property Name", "zh": "修改属性名"},
    "dlg_rename_key_msg": {"en": "New name:", "zh": "新名："},
    "menu_move_up": {"en": "Move Up\tShift+Up", "zh": "上移\tShift+Up"},
    "menu_move_down": {"en": "Move Down\tShift+Down", "zh": "下移\tShift+Down"},
    "menu_edit_loop": {"en": "Edit Loop...", "zh": "编辑循环..."},
    "loop_dlg_title": {"en": "Loop Editor", "zh": "循环编辑器"},
    "loop_dlg_col_key": {"en": "Key", "zh": "键"},
    "loop_dlg_col_value": {"en": "Value", "zh": "值"},
    "loop_tip_task_start":     {"en": "task_start: row number (1-based) in the task grid where the loop body begins", "zh": "task_start: 循环体起始任务行号（从1开始）"},
    "loop_tip_task_end":       {"en": "task_end: row number (1-based) in the task grid where the loop body ends (inclusive)", "zh": "task_end: 循环体结束任务行号（含，从1开始）"},
    "loop_tip_loop_key":       {"en": "loop_key: data_chain key whose value is the collection to iterate over; set loop_times to \"0\" when using this", "zh": "loop_key: data_chain 中作为遍历集合的键；使用此项时 loop_times 须设为 \"0\""},
    "loop_tip_loop_times":     {"en": "loop_times: fixed number of iterations; set to \"0\" to use loop_key instead", "zh": "loop_times: 固定循环次数；设为 \"0\" 则改用 loop_key 遍历集合"},
    "loop_tip_loop_index_key": {"en": "loop_index_key: data_chain key that receives the current 0-based iteration index", "zh": "loop_index_key: 接收当前迭代下标（从0开始）的 data_chain 键"},
    "loop_tip_item_key":       {"en": "item_key: data_chain key that receives the current collection item each iteration", "zh": "item_key: 每次迭代时接收当前集合元素的 data_chain 键"},
    "loop_tip_exception_then":  {"en": "exception_then: what to do when a task inside the loop raises an exception — \"break\" stops the loop, \"continue\" skips to next iteration", "zh": "exception_then: 循环内任务出错时的处理方式 — \"break\" 终止循环，\"continue\" 跳过本次继续"},
    "loop_tip_loop_condition":  {"en": "loop_condition: Python function body (data_chain) → (bool, str); return True,'break' to exit loop; return True,'continue' to skip to next iteration; return False,'' to proceed normally", "zh": "loop_condition: Python方法体 (data_chain)，return True,'break' 终止循环；return True,'continue' 跳到下一次迭代；return False,'' 正常继续"},
    "menu_undo": {"en": "Undo\tCtrl+Z", "zh": "撤销\tCtrl+Z"},
    "menu_redo": {"en": "Redo\tCtrl+Y", "zh": "重做\tCtrl+Y"},
    "menu_snapshots": {"en": "Snapshots", "zh": "快 照"},
    "tip_snapshots": {"en": "View and apply editing snapshots", "zh": "查看并应用编辑快照"},

    # === Snapshot dialog ===
    "dlg_snapshot_title": {"en": "Execution Snapshots", "zh": "Execution 快照"},
    "btn_apply_snapshot": {"en": "Apply", "zh": "应用"},
    "btn_close": {"en": "Close", "zh": "关闭"},

    # === Unsaved changes dialog ===
    "dlg_unsaved_title": {"en": "Unsaved Changes", "zh": "未保存的更改"},
    "dlg_unsaved_msg": {
        "en": "Current execution has unsaved changes.",
        "zh": "当前Execution有未保存的更改。",
    },
    "btn_dismiss": {"en": "Dismiss", "zh": "知道了"},
    "btn_save_and_run": {"en": "Save and Run", "zh": "保存并继续运行"},
    "dlg_unsaved_on_close_msg": {
        "en": "Current execution has unsaved changes. What would you like to do?",
        "zh": "当前Execution有未保存的更改，是否继续退出？",
    },
    "btn_save_and_exit": {"en": "Save and Exit", "zh": "保存并退出"},
    "btn_exit_without_save": {"en": "Exit Without Saving", "zh": "直接退出"},
    "btn_cancel_exit": {"en": "Cancel", "zh": "取消退出"},

    # === Property grid categories ===
    "pgrid_input_editor": {"en": "Input Editor", "zh": "输入编辑器"},
    "pgrid_input_editor_of": {"en": "Input Editor of T", "zh": "任务 T"},
    "pgrid_loop_editor": {"en": "Loop Editor", "zh": "循环编辑器"},

    # === Dialog titles ===
    "dlg_input_title": {"en": "PETP - Input", "zh": "PETP - 请输入"},
    "dlg_result_title": {"en": "PETP - Message Box", "zh": "PETP - 消息框"},
    "dlg_copy_exec_title": {"en": "Copy Execution", "zh": "复制Execution"},
    "dlg_copy_exec_msg": {"en": "Enter name for the copy:", "zh": "请输入副本名称："},
    "dlg_copy_exec_dup": {"en": "Name already exists, please choose a different name.",
                          "zh": "名称已存在，请选择其他名称。"},
    "dlg_delete_exec_title": {"en": "Delete Execution", "zh": "删除Execution"},
    "dlg_delete_exec_msg": {
        "en": "Delete \"{name}\"?\n\nThe file will be moved to core/executions/trash/ and can be restored manually.",
        "zh": "确定删除 \"{name}\"？\n\n文件将移至 core/executions/trash/，可手动恢复。",
    },

    # === Dialog buttons ===
    "dlg_save_json": {"en": "Save as JSON", "zh": "另存为 JSON"},
    "dlg_save_csv": {"en": "Save as CSV", "zh": "另存为 CSV"},
    "dlg_copy": {"en": "Copy", "zh": "复制"},
    "dlg_ok": {"en": "&OK", "zh": "确定(&O)"},
    "dlg_cancel": {"en": "&Cancel", "zh": "取消(&C)"},

    # === Dialog messages ===
    "dlg_saved_to": {"en": "Saved to:\n{path}", "zh": "已保存至:\n{path}"},
    "dlg_failed_to_save": {"en": "Failed to save:\n{error}", "zh": "保存失败:\n{error}"},
    "dlg_error": {"en": "Error", "zh": "错误"},

    # === File dialog ===
    "fdlg_open_recording": {
        "en": "Open Chrome DevTools Recorder file",
        "zh": "打开 Chrome DevTools Recorder 录制文件",
    },

    # === Status / validation messages (presenter) ===
    "msg_cron_invalid": {"en": "Invalid CRON", "zh": "CRON 表达式无效"},
    "msg_cron_cannot_save": {
        "en": "CRON is invalid, cron can not be saved",
        "zh": "CRON 无效，无法保存",
    },
    "msg_exec_list_empty": {
        "en": "Execution list should NOT be empty",
        "zh": "Execution列表不能为空",
    },
    "msg_pipeline_name_empty": {
        "en": "Pipeline: cron name should not be empty",
        "zh": "流水线：名称不能为空",
    },
    "msg_pipeline_overwrite": {
        "en": "Pipeline: {name} already existed, overwrite!",
        "zh": "流水线：{name} 已存在，将覆盖！",
    },
    "msg_execution_overwrite": {
        "en": "Execution: {name} already existed, overwrite!",
        "zh": "Execution：{name} 已存在，将覆盖！",
    },
    "msg_execution_stopping": {
        "en": "Execution: [ {name} ] is manually stopping.",
        "zh": "Execution：[ {name} ] 正在手动停止。",
    },
    "msg_save_aborted": {
        "en": "Save aborted due to unresolved syntax errors.",
        "zh": "因未解决的语法错误，保存已中止。",
    },
    "msg_select_string_prop": {
        "en": "please select a string property.",
        "zh": "请选择一个字符串属性。",
    },
    "msg_no_task_row_bound": {
        "en": "No task row bound to property grid.",
        "zh": "没有任务行绑定到属性网格。",
    },
    "msg_select_task_row_first": {
        "en": "Please select a task row first before toggling skip.",
        "zh": "请先选择一个任务行再切换跳过状态。",
    },
    "msg_select_property_first": {
        "en": "pls select property first.",
        "zh": "请先选择属性。",
    },
    "msg_select_value_property": {
        "en": "pls select value property first.",
        "zh": "请先选择值属性。",
    },
    "msg_cron_invalid_hint": {
        "en": "{cron_invalid}: [ {cron} ] just try [ 0 * * * * ]",
        "zh": "{cron_invalid}: [ {cron} ] 请尝试 [ 0 * * * * ]",
    },
    "msg_convert_success": {
        "en": "Successfully converted from Chrome Recorder: {file_path}, {title}",
        "zh": "成功从 Chrome Recorder 录制转换：{file_path}, {title}",
    },
    "msg_recording_empty": {
        "en": "Recording location and test name should not be empty, also able to select the row where start to load.",
        "zh": "录制位置和测试名称不能为空，也可以选择开始加载的行。",
    },
    "msg_exec_not_tool": {
        "en": "Execution '{name}' is not available as a tool (astool=false)",
        "zh": "Execution '{name}' 不可用作工具（astool=false）",
    },
    "msg_unsupported_chart": {
        "en": "Unsupported chart type: {chart_type}",
        "zh": "不支持的图表类型：{chart_type}",
    },

    # === Checkbox labels ===
    "cb_as_cron": {"en": "as cron", "zh": "定时任务"},

    # === ProcessorPalette ===
    "palette_hint": {"en": "type to filter...", "zh": "输入筛选..."},
    "palette_footer_all": {"en": "{n} processors", "zh": "{n} 个处理器"},
    "palette_footer_filtered": {"en": "{total} / {n}  (name: {nm}  cat: {ct})", "zh": "{total} / {n}  (名称: {nm}  分类: {ct})"},
    "palette_sep_label": {"en": "── category matches ──", "zh": "── 分类匹配 ──"},

    # === Startup welcome / motivational messages ===
    "welcome_0": {
        "en": "Welcome back! Automation starts here.",
        "zh": "欢迎回来！自动化，从这里启程。",
    },
    "welcome_1": {
        "en": "Every great workflow begins with a single task.",
        "zh": "千里之行，始于一个任务。",
    },
    "welcome_2": {
        "en": "Let the robots work — you focus on what matters.",
        "zh": "让机器人干活，你来专注真正重要的事。",
    },
    "welcome_3": {
        "en": "Build once, run forever. Automate it with PETP.",
        "zh": "一次构建，永久运行。PETP 助你解放双手。",
    },
    "welcome_4": {
        "en": "Less repetition, more creation.",
        "zh": "少一分重复，多一分创造。",
    },
    "welcome_5": {
        "en": "Your pipeline is ready. Make today count.",
        "zh": "流水线已就绪，让今天的每一刻都有价值。",
    },
    "welcome_6": {
        "en": "Automate the boring stuff — dream bigger.",
        "zh": "自动化那些枯燥的事，然后去追更大的梦想。",
    },
    "welcome_7": {
        "en": "Consistency beats perfection. Ship your tasks.",
        "zh": "坚持胜过完美，跑起你的任务吧。",
    },
    "welcome_8": {
        "en": "Small automations, massive gains over time.",
        "zh": "小小的自动化，长期积累的巨大收益。",
    },
    "welcome_9": {
        "en": "You build the tools; the tools build the future.",
        "zh": "你创造工具，工具创造未来。",
    },
    "welcome_10": {
        "en": "The unexamined workflow is not worth running.",
        "zh": "未经审视的流程，不值得运行。",
    },
    "welcome_11": {
        "en": "I automate, therefore I am.",
        "zh": "我自动化，故我在。",
    },
    "welcome_12": {
        "en": "One cannot step into the same pipeline twice.",
        "zh": "人不能两次踏入同一条流水线。",
    },
    "welcome_13": {
        "en": "The only constant is change — so automate adaptively.",
        "zh": "唯一不变的是变化——所以要自适应地自动化。",
    },
    "welcome_14": {
        "en": "To do is to be; to automate is to transcend.",
        "zh": "行动即存在；自动化即超越。",
    },
    "welcome_15": {
        "en": "Simplicity is the ultimate sophistication.",
        "zh": "简约是终极的精妙。",
    },
    "welcome_16": {
        "en": "Between stimulus and response, there is a processor.",
        "zh": "在刺激与响应之间，有一个处理器。",
    },
    "welcome_17": {
        "en": "The task you automate today frees the mind of tomorrow.",
        "zh": "今日自动化的任务，是明日自由的心智。",
    },
    "welcome_18": {
        "en": "Knowing the path is not the same as running the pipeline.",
        "zh": "知道路在哪里，不等于跑通了流水线。",
    },
    "welcome_19": {
        "en": "All tasks are impermanent — but their output persists.",
        "zh": "诸行无常——但输出永存。",
    },

}

_current_locale = "zh"


def set_locale(locale: str):
    global _current_locale
    _current_locale = locale if locale in ("en", "zh") else "zh"


def get_locale() -> str:
    return _current_locale


def t(key: str, **kwargs) -> str:
    entry = TRANSLATIONS.get(key)
    if entry is None:
        return key
    text = entry.get(_current_locale) or entry.get("en") or key
    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, IndexError):
            pass
    return text
