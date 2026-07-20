# -*- coding: UTF-8 -*-
# Processor description translations (zh only).
# EN descriptions are the authoritative source in each processor's DESC attribute.
# Key format: desc_<TYPE>  →  {"zh": "..."}.

DESC_TRANSLATIONS: dict[str, dict[str, str]] = {
    # === Processor descriptions (i18n) ===

    "desc_AI_LLM_SETUP": {
        "zh": (
            "设置统一的 LLM 客户端实例。通过 provider 参数支持所有 LLM 提供商。\n"
            "支持的 provider: deepseek, zhipu, qianfan, minimax, anthropic, doubao, moonshot, gemini, ollama, openai_compatible。\n"
            "客户端实例存储在 data_chain 中供后续 QANDA/MCP 任务使用。\n"
            "\n"
            "- provider: LLM 提供商名称 — deepseek | zhipu | qianfan | minimax | doubao | moonshot | gemini | ollama | anthropic | openai_compatible（默认: \"deepseek\"）\n"
            "- api_key_env: 包含 API 密钥的环境变量名（默认值因 provider 而异）\n"
            "- api_key: 直接提供的 API 密钥（优先于 api_key_env，支持表达式）\n"
            "- base_url: API 基础 URL；若为空则使用 provider 默认值（支持表达式）\n"
            "- model: 模型名称；若为空则使用 provider 默认值（支持表达式）\n"
            "- llm_data_key: data_chain 中存储客户端实例的键（默认: \"llm_client\"）\n"
            "- top_p: Top-p 采样参数（默认: \"0.85\"）\n"
            "- temperature: 采样温度（默认: \"0.8\"）"
        ),
    },

    "desc_AI_LLM_QANDA": {
        "zh": (
            "向统一的 LLM 提问并获取回答。依赖 AI_LLM_SETUP 先初始化客户端。\n"
            "支持所有 provider: deepseek, zhipu, qianfan, minimax, anthropic, doubao, moonshot, gemini, ollama, openai_compatible。\n"
            "\n"
            "- llm_data_key: data_chain 中存储 LLM 客户端实例的键（默认: \"llm_client\"）\n"
            "- prompt: 发送给 LLM 的提示/问题（支持表达式）\n"
            "- model: 模型名称；若为空则使用 SETUP 时配置的模型（支持表达式，默认: \"\"）\n"
            "- temperature: 采样温度（默认: \"1.0\"）\n"
            "- system_prompt: 系统消息；若为空则不发送系统消息（支持表达式，默认: \"\"）\n"
            "- resp_content_key: data_chain 中存储响应内容的键（支持表达式，默认: \"\"）\n"
            "- convert_resp_2_json: \"yes\" 解析 markdown 代码块中的 JSON 响应（默认: \"no\"）\n"
            "- show_in_popup: \"yes\" 在弹窗中显示问答结果（默认: \"yes\"）\n"
            "- show_thinking: \"yes\" 保留 <think> 标签；\"no\" 去除（默认: \"no\"）"
        ),
    },

    "desc_AI_LLM_QANDA_MCP": {
        "zh": (
            "向统一的 LLM 提问并支持通过 MCP 服务器进行工具调用。使用官方 MCP SDK（Streamable HTTP 传输）。\n"
            "依赖 AI_LLM_SETUP 先初始化客户端。支持所有 provider。可连接任意标准 MCP server。\n"
            "从 MCP 服务器获取可用工具，如果 LLM 决定使用工具，通过 MCP 协议执行后返回优化答案。\n"
            "\n"
            "- llm_data_key: data_chain 中存储 LLM 客户端实例的键（默认: \"llm_client\"）\n"
            "- prompt: 发送给 LLM 的提示/问题（支持表达式）\n"
            "- mcp_server_url: MCP 服务器端点 URL，需支持 Streamable HTTP 传输（默认: \"http://localhost:8866/mcp\"）\n"
            "- model: 模型名称；若为空则使用 SETUP 时配置的模型（支持表达式，默认: \"\"）\n"
            "- temperature: 采样温度（默认: \"1.0\"）\n"
            "- system_prompt: 额外系统上下文（支持表达式，默认: \"\"）\n"
            "- resp_content_key: data_chain 中存储最终响应内容的键（支持表达式，默认: \"\"）\n"
            "- convert_resp_2_json: \"yes\" 解析 markdown 代码块中的 JSON 响应（默认: \"no\"）\n"
            "- show_in_popup: \"yes\" 在弹窗中显示问答结果（默认: \"yes\"）\n"
            "- show_thinking: \"yes\" 保留 <think> 标签；\"no\" 去除（默认: \"no\"）"
        ),
    },

    "desc_BEAUTIFUL_SOUP": {
        "zh": (
            
             "\u4f7f\u7528 BeautifulSoup \u89e3\u6790 HTML \u6216 XML \u5185\u5bb9\uff0c\u5e76\u6267\u884c\u81ea\u5b9a\u4e49\u51fd\u6570\u4f53\u6765\u63d0\u53d6\u6570\u636e\u3002\n"
             "\u89e3\u6790\u540e\u7684 soup \u5bf9\u8c61\u548c\u539f\u59cb\u6570\u636e\u5728\u51fd\u6570\u4f53\u5185\u53ef\u7528\uff0c\u652f\u6301\u7075\u6d3b\u5904\u7406\u3002\n"
             "\u53c2\u89c1: https://beautiful-soup-4.readthedocs.io/en/latest/\n"
             "\n"
             "- inbound_data_key: data_chain 中用于解析的 HTML/XML 字符串的键；优先于 inbound_data（支持表达式，默认: \"\"）\n"
             "- inbound_data: 当未设置 inbound_data_key 时用于解析的原始 HTML/XML 字符串（支持表达式，默认: \"\"）\n"
             "- parser: BeautifulSoup \u89e3\u6790\u5668\uff08\u9ed8\u8ba4: \"html.parser\"\uff09\n"
             "- outbound_data_key: data_chain 中存储函数体返回结果的键（支持表达式，默认: \"soup_outbound\"）\n"
             "- func_body: Python \u51fd\u6570\u4f53\u5b57\u7b26\u4e32\uff0c\u53ef\u7528\u53d8\u91cf: soup (BeautifulSoup \u5bf9\u8c61), data (\u539f\u59cb\u5b57\u7b26\u4e32)\n"
        ),
    },

    "desc_CAPTCHA": {
        "zh": (
            "使用 ddddocr 在本地识别验证码图片（无需 API 密钥）。\n"
            "pip install ddddocr\n"
            "\n"
            "支持的模式:\n"
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
            
             "\u6839\u636e\u7ed9\u5b9a\u7684 chrome_name \u5173\u95ed data_chain \u4e2d\u5bf9\u5e94\u7684 Chrome \u9a71\u52a8\u3002\u5728\u6d41\u6c34\u7ebf\u4e2d\u8fd0\u884c\u65f6\u53ef\u8df3\u8fc7\u3002\n"
             "\n"
             "- chrome_name: data_chain \u4e2d\u5b58\u50a8 Chrome \u9a71\u52a8\u5b9e\u4f8b\u7684\u952e\uff08\u9ed8\u8ba4: \"chrome\"\uff09\n"
             "- skip_in_pipeline: 设为 \"yes\" 在流水线中运行时跳过此任务（默认: \"no\"）\n"
        ),
    },

    "desc_CMD": {
        "zh": (

             "通过 subprocess.check_output 运行系统命令，将输出保存到 data_chain 的 data_key 中。\n"
             "\n"
             "默认行为通过 shlex 拆分 cmdstr（不走 shell，不解释元字符）—— 可防御 ;|& 等注入。\n"
             "仅在确实需要 shell 特性（管道、重定向、通配符）且命令完全可信时,才设 shell=\"yes\"。\n"
             "\n"
             "- cmdstr: 要执行的命令字符串（支持表达式）\n"
             "- cmddir: 命令工作目录（支持表达式，可选）\n"
             "- data_key: data_chain 中存储命令输出的键\n"
             "- timeout: 命令超时秒数（默认: 30）\n"
             "- shell: \"yes\" 通过 shell 执行 —— 危险,关闭注入防护（默认: \"no\"）\n"
             "- encoding: 输出编码（默认: \"utf-8\"）\n"
        ),
    },

    "desc_COLLECTION_MERGE": {
        "zh": (
            
             "\u4ece\u4e24\u4e2a\u96c6\u5408\u4e2d\u67e5\u627e\u5339\u914d\u884c\u5e76\u5408\u5e76\u5230\u7ed3\u679c\u96c6\u5408\u4e2d\u3002\n"
             "\n"
             "- c_one_name: data_chain \u4e2d\u6307\u5411\u7b2c\u4e00\u4e2a\u96c6\u5408\u7684\u952e\n"
             "- c_two_name: data_chain \u4e2d\u6307\u5411\u7b2c\u4e8c\u4e2a\u96c6\u5408\u7684\u952e\n"
             "- c_result_name: data_chain 中存储合并结果的键\n"
             "- lambda_finder: 用于匹配行的 Python 表达式，可用变量 \"rowc1\" 和 \"rowc2\"（默认: \"rowc1[0] == rowc2[0]\"）\n"
             "- lambda_merge_matched: 用于合并匹配行的 Python 表达式，可用变量 \"rowc1\" 和 \"rowc2\"（默认: \"rowc1 + rowc2\"）\n"
        ),
    },

    "desc_CREATE_SFTP_CLIENT": {
        "zh": (
            "创建 paramiko SFTP 客户端，保存到 data_chain 的 sftp_client_key 中。\n"
            "\n"
            "- sftp_ip: SFTP 服务器 IP 地址（支持表达式）\n"
            "- sftp_port: SFTP 服务器端口（默认: 22）\n"
            "- uname: SFTP 用户名（支持表达式）\n"
            "- pwd: SFTP 密码（支持表达式和加密值）\n"
            "- sftp_client_key: data_chain 中存储 SFTP 客户端的键（默认: \"sftpclient\"）"
        ),
    },

    "desc_CREATE_SSH_CLIENT": {
        "zh": (
            "创建 paramiko SSH 客户端，保存到 data_chain 的 ssh_client_key 中。\n"
            "\n"
            "- ssh_ip: SSH 服务器 IP 地址（支持表达式）\n"
            "- uname: SSH 用户名（支持表达式）\n"
            "- pwd: SSH 密码（支持表达式和加密值）\n"
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
            
             "\u901a\u8fc7 lambda \u8868\u8fbe\u5f0f\u5c06\u6570\u636e\u6536\u96c6\u5230 data_chain \u4e2d\u7684\u5217\u8868\u6216\u5b57\u5178\u3002\u652f\u6301\u6536\u96c6\u524d\u6e05\u7a7a\u3002\n"
             "\n"
             "- clean_before_collect: \"yes\" \u6536\u96c6\u524d\u6e05\u7a7a\u76ee\u6807\uff0c\"no\" \u8ffd\u52a0\uff08\u9ed8\u8ba4: \"no\"\uff09\n"
             "- target: data_chain \u4e2d\u5b58\u50a8\u6536\u96c6\u7ed3\u679c\u7684\u952e\n"
             "- type: \u6536\u96c6\u7c7b\u578b \u2014 \"list\" \u6216 \"dict\"\uff08\u9ed8\u8ba4: \"list\"\uff09\n"
             "- list_flatten: 如果为 \"yes\" 且收集行为列表则展开；\"no\" 保持不变（仅类型为 \"list\" 时适用，默认: \"no\"）\n"
             "- list_row_lambda: 针对列表行值的 Python 表达式，可用变量 \"me\" (当前处理器)（类型为 \"list\" 时必需）\n"
             "- dict_key_lambda: dict \u6a21\u5f0f\u4e0b\u7528\u4e8e\u751f\u6210\u952e\u7684\u8868\u8fbe\u5f0f\n"
             "- dict_value_lambda: dict \u6a21\u5f0f\u4e0b\u7528\u4e8e\u751f\u6210\u503c\u7684\u8868\u8fbe\u5f0f\n"
        ),
    },

    "desc_DATA_CONVERT": {
        "zh": (
            
             "\u4ece data_chain \u4e2d\u6309\u952e\u53d6\u503c\uff0c\u901a\u8fc7\u81ea\u5b9a\u4e49 Python \u51fd\u6570\u8f6c\u6362\uff0c\u5c06\u7ed3\u679c\u5b58\u56de data_chain \u7684\u76ee\u6807\u952e\u3002\n"
             "\n"
             "- p: 当前处理器实例（例如 p.get_now_str()）\n"
             "- given: 从 given_key 检索到的值\n"
             "- given_key: data_chain \u4e2d\u8bfb\u53d6\u6e90\u6570\u636e\u7684\u952e\uff08\u652f\u6301\u8868\u8fbe\u5f0f\uff09\n"
             "- convertor_func: Python \u51fd\u6570\u4f53\u5b57\u7b26\u4e32\uff0c\u53c2\u6570\u4e3a \"source_data\"\uff08\u652f\u6301\u8868\u8fbe\u5f0f\uff09\n"
             "- target_key: data_chain \u4e2d\u5b58\u50a8\u7ed3\u679c\u7684\u952e\uff08\u652f\u6301\u8868\u8fbe\u5f0f\uff09\n"
        ),
    },

    "desc_DATA_FILTER": {
        "zh": (
            
             "\u4f7f\u7528 filter_fn \u8868\u8fbe\u5f0f\u8fc7\u6ee4 source_key\uff0c\u5c06\u7ed3\u679c\u5b58\u5165 target_key\u3002\n"
             "\u5982\u679c\u672a\u6307\u5b9a target_key\uff0c\u5219\u66ff\u6362 source_key\u3002\n"
             "\n"
             "- source_key: data_chain \u4e2d\u6307\u5411\u6e90\u5217\u8868\u7684\u952e\n"
             "- filter_fn: Python \u51fd\u6570\u4f53\uff0c\u53c2\u6570\u4e3a \"item\"\uff0c\u5e94\u8fd4\u56de bool\n"
             "- target_key: data_chain \u4e2d\u5b58\u50a8\u8fc7\u6ee4\u7ed3\u679c\u7684\u952e\uff08\u53ef\u9009\uff0c\u9ed8\u8ba4\u66ff\u6362\u6e90\uff09\n"
        ),
    },

    "desc_DATA_GROUPBY": {
        "zh": (
            
             "\u6309\u952e\u51fd\u6570\u5bf9 source_key \u8fdb\u884c\u5206\u7ec4\uff0c\u53ef\u9009\u6620\u5c04\u548c\u6536\u96c6\u5206\u7ec4\u7ed3\u679c\u5230\u5b57\u5178\u4e2d\u3002\n"
             "\n"
             "- source_key: data_chain \u4e2d\u6307\u5411\u8f93\u5165\u5217\u8868\u7684\u952e\n"
             "- group_by_func: Python \u8868\u8fbe\u5f0f\uff0c\u7528\u4e8e\u751f\u6210\u5206\u7ec4\u952e\uff0c\u53d8\u91cf \"item\" \u53ef\u7528\n"
             "- mapping_func: Python \u8868\u8fbe\u5f0f\uff0c\u7528\u4e8e\u8f6c\u6362\u6bcf\u4e2a\u5143\u7d20\uff08\u53ef\u9009\uff0c\u9ed8\u8ba4\u4f7f\u7528\u539f\u59cb item\uff09\n"
             "- collect_func: Python \u8868\u8fbe\u5f0f\uff0c\u7528\u4e8e\u805a\u5408\u6bcf\u7ec4\u7684\u503c\u5217\u8868\uff08\u53ef\u9009\uff09\n"
             "- data_key: data_chain \u4e2d\u5b58\u50a8\u5206\u7ec4\u7ed3\u679c\u5b57\u5178\u7684\u952e\n"
        ),
    },

    "desc_DATA_MAPPING": {
        "zh": (
            
             "\u4f7f\u7528 map_fn \u8868\u8fbe\u5f0f\u5bf9 source_key \u4e2d\u7684\u6bcf\u4e2a\u5143\u7d20\u8fdb\u884c\u6620\u5c04/\u8f6c\u6362\uff0c\u7ed3\u679c\u5b58\u5165 target_key\u3002\n"
             "\u652f\u6301\u901a\u8fc7 start_idx/end_idx \u8fdb\u884c\u5207\u7247\u3002\u5982\u679c\u672a\u6307\u5b9a target_key\uff0c\u5219\u66ff\u6362 source_key\u3002\n"
             "\n"
             "- source_key: data_chain \u4e2d\u6307\u5411\u6e90\u5217\u8868\u7684\u952e\n"
             "- map_fn: Python \u51fd\u6570\u4f53\uff0c\u53c2\u6570\u4e3a \"item\"\uff0c\u8fd4\u56de\u8f6c\u6362\u540e\u7684\u503c\n"
             "- start_idx: \u8d77\u59cb\u7d22\u5f15\uff08\u53ef\u9009\uff09\n"
             "- end_idx: \u7ed3\u675f\u7d22\u5f15\uff08\u53ef\u9009\uff09\n"
             "- target_key: data_chain \u4e2d\u5b58\u50a8\u6620\u5c04\u7ed3\u679c\u7684\u952e\uff08\u53ef\u9009\uff0c\u9ed8\u8ba4\u66ff\u6362\u6e90\uff09\n"
        ),
    },

    "desc_DATA_MASKING": {
        "zh": (
            
             "\u5bf9\u96c6\u5408\uff08\u884c\u5217\u8868\uff09\u6267\u884c\u5355\u5217\u6570\u636e\u8131\u654f\u3002\u6bcf\u884c\u662f\u4e00\u4e2a\u5217\u8868\uff0c\u6307\u5b9a\u5217\u88ab\u6e05\u6d17\u540e\n"
             "\u7528\u81ea\u5b9a\u4e49\u51fd\u6570\u751f\u6210\u7684\u8131\u654f\u503c\u66ff\u6362\u3002\u7ef4\u62a4\u8131\u654f\u5b57\u5178\u786e\u4fdd\u76f8\u540c\u539f\u59cb\u503c\u6620\u5c04\u5230\u76f8\u540c\u8131\u654f\u503c\u3002\n"
             "\n"
             "- source_key: data_chain \u4e2d\u6307\u5411\u8f93\u5165\u96c6\u5408\u7684\u952e\n"
             "- content_clean_func: 在脱敏前用于清理/规范化单元格内容的 Python 函数体；接收 (content)（支持表达式，默认: \"return content\"）\n"
             "- masking_func: 用于生成脱敏替换值的 Python 函数体；接收 (mask_dict, row, rownum, colnum)（支持表达式，默认：\"return \'SJB-\' + str(colnum) + str(rownum)\"）\n"
             "- masking_column: \u8981\u8131\u654f\u7684\u5217\u7d22\u5f15\n"
             "- masking_dict_name: 处理后在 data_chain 中存储脱敏字典的键；为空则丢弃字典（支持表达式，默认: \"\"）\n"
             "- masking_dict_inverted: \"yes\" \u5219\u53cd\u8f6c\u5b57\u5178\u8f93\u51fa\uff08\u9ed8\u8ba4: \"no\"\uff09\n"
        ),
    },

    "desc_DATA_MULTI_MASKING": {
        "zh": (
            
             "\u5bf9\u96c6\u5408\uff08\u884c\u5217\u8868\uff09\u6267\u884c\u591a\u5217\u6570\u636e\u8131\u654f\u3002\u4e0e\u5355\u5217 DATA_MASKING \u4e0d\u540c\uff0c\n"
             "\u6b64\u5904\u7406\u5668\u652f\u6301\u540c\u65f6\u8131\u654f\u591a\u4e2a\u5217\u3002\u6bcf\u4e2a\u6307\u5b9a\u5217\u88ab\u6e05\u6d17\u540e\u7528\u8131\u654f\u503c\u66ff\u6362\u3002\n"
             "\n"
             "- source_key: data_chain \u4e2d\u6307\u5411\u8f93\u5165\u96c6\u5408\u7684\u952e\n"
             "- content_clean_func: Python \u51fd\u6570\u4f53\uff0c\u6e05\u6d17\u539f\u59cb\u503c\uff08\u53ef\u9009\uff09\n"
             "- masking_func: Python \u51fd\u6570\u4f53\uff0c\u751f\u6210\u8131\u654f\u503c\n"
             "- masking_columns: \u8981\u8131\u654f\u7684\u5217\u7d22\u5f15\u5217\u8868\uff0c\u5982 \"0,2,5\"\n"
             "- masking_dict_name: data_chain \u4e2d\u5b58\u50a8\u8131\u654f\u5b57\u5178\u7684\u952e\n"
             "- masking_dict_inverted: 若为 \"Yes\" 或 \"yes\"，则存储反向映射 (脱敏后 -> 原始) 而非 (原始 -> 脱敏后)（支持表达式，默认: \"Yes\"）\n"
        ),
    },

    "desc_DB_ACCESS": {
        "zh": (
            
             "\u63d0\u4f9b\u901a\u7528\u6570\u636e\u5e93\u8bbf\u95ee\u80fd\u529b\u3002\u8fde\u63a5\u6570\u636e\u5e93\uff0c\u6267\u884c SQL \u67e5\u8be2\uff0c\n"
             "\u5c06\u7ed3\u679c\u96c6\u5b58\u5165 data_chain \u7684\u6307\u5b9a\u952e\u3002\n"
             "\n"
             "- type: \u6570\u636e\u5e93\u7c7b\u578b \u2014 sqlite, mysql, mssql, oracle, postgres\uff08\u9ed8\u8ba4: \"sqlite\"\uff09\n"
             "- host: \u6570\u636e\u5e93\u4e3b\u673a\u5730\u5740\uff08\u652f\u6301\u8868\u8fbe\u5f0f\uff09\n"
             "- port: \u6570\u636e\u5e93\u7aef\u53e3\uff08\u652f\u6301\u8868\u8fbe\u5f0f\uff09\n"
             "- database: \u6570\u636e\u5e93\u540d\u79f0/\u8def\u5f84\uff08\u652f\u6301\u8868\u8fbe\u5f0f\uff09\n"
             "- user: \u6570\u636e\u5e93\u7528\u6237\u540d\uff08\u652f\u6301\u8868\u8fbe\u5f0f\uff09\n"
             "- pwd: \u6570\u636e\u5e93\u5bc6\u7801\uff08\u652f\u6301\u8868\u8fbe\u5f0f\u548c\u52a0\u5bc6\u503c\uff09\n"
             "- sql: SQL \u67e5\u8be2\u8bed\u53e5\uff08\u652f\u6301\u8868\u8fbe\u5f0f\uff09\n"
             "- param: 用于参数化 SQL 查询的逗号分隔参数值（支持表达式，默认: \"admin, id\"）\n"
             "- data_key: data_chain \u4e2d\u7f13\u5b58\u6570\u636e\u5e93\u8fde\u63a5\u7684\u952e\uff08\u53ef\u9009\uff09\n"
             "- param_key: data_chain 中用于检索 SQL 参数的键名；若提供则优先于 \"param\"（支持表达式，默认: \"sql_param\"）\n"
        ),
    },

    "desc_ENCODE_DECODE_STR": {
        "zh": (
            
             "\u4f7f\u7528\u6307\u5b9a\u7b97\u6cd5\u5bf9\u5b57\u7b26\u4e32\u8fdb\u884c\u7f16\u7801\u6216\u89e3\u7801\u3002\u652f\u6301 base64\u3001base85\u3001hexlify\u3001\n"
             "a85 (Ascii85)\u3001base16\u3001base32 \u548c base32hex \u7b49\u7f16\u7801\u65b9\u6848\u3002\n"
             "\n"
             "- type: 要执行的操作，\"ENCODE\" 或 \"DECODE\"（支持表达式，默认: \"ENCODE | DECODE\"）\n"
             "- inbound: \u8f93\u5165\u5b57\u7b26\u4e32\uff08\u652f\u6301\u8868\u8fbe\u5f0f\uff09\n"
             "- outbound_key: 存储编码/解码结果的 data_chain 键（默认: \"\"）\n"
             "- algorithms: 要使用的编码算法: base64, base85, hexlify, a85, base16, base32, 或 base32hex（默认: \"base64 | base85 | hexlify | a85 | base16 | base32 | base32hex\"）\n"
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
            
             "\u901a\u8fc7 Selenium \u627e\u5230\u6587\u4ef6\u4e0a\u4f20\u5143\u7d20\uff0c\u7136\u540e\u4f7f\u7528\u7cfb\u7edf\u6587\u4ef6\u9009\u62e9\u5bf9\u8bdd\u6846\u9009\u62e9\u8981\u4e0a\u4f20\u7684\u6587\u4ef6\u3002\n"
             "\u652f\u6301\u901a\u8fc7\u590d\u5236\u7c98\u8d34\u673a\u5236\u5904\u7406 Unicode \u6587\u4ef6\u540d\u3002\n"
             "\n"
             "- fileuploadby: 寻找上传元素的定位器类型，\"id\" 或 \"xpath\"\n"
             "- identity: \u4e0a\u4f20\u5143\u7d20\u7684\u5b9a\u4f4d\u503c\n"
             "- file_path: \u8981\u4e0a\u4f20\u7684\u6587\u4ef6\u8def\u5f84\uff08\u652f\u6301\u8868\u8fbe\u5f0f\uff09\n"
             "- file_path_key: data_chain \u4e2d\u6587\u4ef6\u8def\u5f84\u7684\u952e\uff08\u4f18\u5148\u4e8e file_path\uff09\n"
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
        ),
    },

    "desc_FIND_FILES": {
        "zh": (
            
             "\u4f7f\u7528\u53ef\u914d\u7f6e\u7684 lambda \u8fc7\u6ee4\u5668\u9012\u5f52\u6536\u96c6\u76ee\u5f55\u4e2d\u7684\u6587\u4ef6\uff0c\u6309\u6587\u4ef6\u540d\u548c\u76ee\u5f55\u6df1\u5ea6\u7b5b\u9009\u3002\n"
             "\u627e\u5230\u7684\u6587\u4ef6\u8def\u5f84\u5217\u8868\u5b58\u50a8\u5728 data_chain \u7684\u6307\u5b9a\u952e\u4e2d\u3002\n"
             "\n"
             "- path_to_find: \u8981\u641c\u7d22\u7684\u76ee\u5f55\u8def\u5f84\uff08\u652f\u6301\u8868\u8fbe\u5f0f\uff09\n"
             "- file_name_lambda: Python \u51fd\u6570\u4f53\uff0c\u6309\u6587\u4ef6\u540d\u8fc7\u6ee4\uff0c\u53c2\u6570\u4e3a \"filename\"\uff08\u9ed8\u8ba4: \"return True\"\uff09\n"
             "- depth_lambda: Python \u51fd\u6570\u4f53\uff0c\u6309\u76ee\u5f55\u6df1\u5ea6\u8fc7\u6ee4\uff0c\u53c2\u6570\u4e3a \"depth\"\uff08\u9ed8\u8ba4: \"return True\"\uff09\n"
             "- found_file_key: data_chain \u4e2d\u5b58\u50a8\u6587\u4ef6\u5217\u8868\u7684\u952e\n"
        ),
    },

    "desc_FIND_LATEST_FILE": {
        "zh": (
            "在指定文件夹中查找最近修改的指定类型的文件。\n"
            "\n"
            "- path_to_find: 要搜索的文件夹路径（支持表达式）\n"
            "- file_type: 文件扩展名过滤（如 \".csv\"、\".xlsx\"）\n"
            "- found_file_key: data_chain 中存储找到的文件路径的键"
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
            
             "\u901a\u8fc7 Selenium \u4f7f\u7528\u6307\u5b9a\u7684\u5b9a\u4f4d\u7b56\u7565\u67e5\u627e Web \u5143\u7d20\u5e76\u70b9\u51fb\u3002\n"
             "\u5982\u679c\u5728\u8d85\u65f6\u65f6\u95f4\u5185\u672a\u627e\u5230\u5143\u7d20\uff0c\u9664\u975e\u8bbe\u7f6e\u4e86 skip_timeout_error \u5426\u5219\u629b\u51fa\u5f02\u5e38\u3002\n"
             "\n"
             "- find_by: \u5b9a\u4f4d\u7c7b\u578b \u2014 id\u3001xpath \u6216 css\n"
             "- identity: \u76ee\u6807\u5143\u7d20\u7684\u5b9a\u4f4d\u503c\uff08\u652f\u6301\u8868\u8fbe\u5f0f\uff09\n"
             "- identity_key: data_chain 中用于定位器的键；优先于 identity（支持表达式，默认: \"\"）\n"
             "- wait: \u70b9\u51fb\u540e\u7684\u989d\u5916\u7b49\u5f85\u79d2\u6570\uff08\u9ed8\u8ba4: 0\uff09\n"
             "- timeout: \u7b49\u5f85\u5143\u7d20\u51fa\u73b0\u7684\u6700\u5927\u79d2\u6570\uff08\u9ed8\u8ba4: 10\uff09\n"
             "- skip_timeout_error: \"yes\" \u8d85\u65f6\u4e0d\u62a5\u9519\uff08\u9ed8\u8ba4: \"no\"\uff09\n"
             "- condition_fn: Python \u51fd\u6570\u4f53\uff0c\u70b9\u51fb\u524d\u7684\u6761\u4ef6\u68c0\u67e5\uff0c\u53c2\u6570\u4e3a \"ele\"\uff08\u53ef\u9009\uff09\n"
             "- skip_if_fn: Python \u51fd\u6570\u4f53\uff0c\u53c2\u6570\u4e3a (p)\uff1b\u8fd4\u56de True \u5219\u5728\u5b9a\u4f4d\u4e4b\u524d\u76f4\u63a5\u8df3\u8fc7\u6574\u4e2a processor\uff08\u4f8b\u5982 xpath \u7531\u53ef\u80fd\u4e0d\u5b58\u5728\u7684 data_chain \u503c\u62fc\u63a5\u65f6\uff09\uff08\u9ed8\u8ba4: \"return False\"\uff09\n"
        ),
    },

    "desc_FIND_THEN_MOVE": {
        "zh": (
            "\u901a\u8fc7 Selenium \u6309\u6307\u5b9a\u5b9a\u4f4d\u7b56\u7565\u67e5\u627e\u5143\u7d20\u5e76\u5c06\u9f20\u6807\u7126\u70b9(hover)\u79fb\u5230\u5176\u4e0a\u3002\n"
            "\u5e38\u7528\u4e8e\u89e6\u53d1 hover \u5c55\u5f00\u83dc\u5355/tooltip\u3001\u6216\u5728\u540e\u7eed\u52a8\u4f5c\u524d\u628a\u5143\u7d20\u6eda\u5165\u89c6\u53e3\u3002\n"
            "\u5e95\u5c42\u8c03\u7528 ActionChains.move_to_element(\u4e0e SeleniumUtil.wait_for_element_xpath_presence_then_move2 \u540c\u6e90)\u3002\n"
            "\n"
            "- find_by: \u5b9a\u4f4d\u7c7b\u578b \u2014 id\u3001xpath\u3001link \u6216 css\n"
            "- identity: \u76ee\u6807\u5143\u7d20\u7684\u5b9a\u4f4d\u503c(\u652f\u6301\u8868\u8fbe\u5f0f)\n"
            "- identity_key: data_chain \u4e2d\u7528\u4e8e\u5b9a\u4f4d\u5668\u7684\u952e;\u4f18\u5148\u4e8e identity(\u652f\u6301\u8868\u8fbe\u5f0f,\u9ed8\u8ba4: \"\")\n"
            "- wait: \u79fb\u52a8\u524d\u7684\u989d\u5916\u7b49\u5f85\u79d2\u6570(\u9ed8\u8ba4: 1)\n"
            "- timeout: \u7b49\u5f85\u5143\u7d20\u51fa\u73b0\u7684\u6700\u5927\u79d2\u6570(\u9ed8\u8ba4: 10)\n"
            "- skip_timeout_error: \"yes\" \u8d85\u65f6\u4e0d\u62a5\u9519(\u9ed8\u8ba4: \"no\")\n"
            "- chrome_name: data_chain \u4e2d Chrome driver \u7684\u952e(\u9ed8\u8ba4: \"chrome\")\n"
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
            "- wait: 定位元素前的额外等待秒数，等待仍在渲染的元素出现（如刚通过 MOVE_TO_IFRAME 切入的 Angular 表单）（默认: 1）\n"
            "- timeout: 等待元素出现的最长秒数（默认: 5）\n"
            "- skip_timeout_error: 超时未找到元素时是否忽略错误。\"yes\" 记录日志并静默返回（继续执行）；\"no\" 或缺省则抛异常（默认: \"yes|no\"）\n"
            "- skip_if_fn: Python 函数体，参数为 (p)；返回 True 则在定位之前直接跳过整个 processor（例如 xpath 由可能不存在的 data_chain 值拼接时）（默认: \"return False\"）"
        ),
    },

    "desc_FOLDER_WATCH_MOVE": {
        "zh": (
            
             "\u5c06\u6587\u4ef6\u4ece\u6e90\u6587\u4ef6\u5939\u79fb\u52a8\u5230\u76ee\u6807\u6587\u4ef6\u5939\u3002\u652f\u6301\u7b49\u5f85\u9884\u671f\u6587\u4ef6\u6570\u91cf\u6216\u8d85\u65f6\u540e\u79fb\u52a8\u3002\n"
             "\n"
             "- source_path: \u8981\u76d1\u89c6\u7684\u6e90\u6587\u4ef6\u5939\u8def\u5f84\uff08\u652f\u6301\u8868\u8fbe\u5f0f\uff09\n"
             "- target_path: \u76ee\u6807\u6587\u4ef6\u5939\u8def\u5f84\uff08\u652f\u6301\u8868\u8fbe\u5f0f\uff09\n"
             "- expect_count: \u9884\u671f\u6587\u4ef6\u6570\u91cf\uff08\u9ed8\u8ba4: 1\uff09\n"
             "- data_key: data_chain \u4e2d\u5b58\u50a8\u76ee\u6807\u6587\u4ef6\u8def\u5f84\u5217\u8868\u7684\u952e\n"
             "- timeout: \u7b49\u5f85\u6587\u4ef6\u7684\u6700\u5927\u79d2\u6570\uff08\u9ed8\u8ba4: 60\uff09\n"
        ),
    },

    "desc_GET_COOKIE": {
        "zh": (
            
             "\u4ece Chrome \u9a71\u52a8\u83b7\u53d6 Cookie \u5e76\u5b58\u5165 data_chain \u7684 value_key \u4e2d\u3002\n"
             "\u5f53 get_all \u4e3a \"yes\" \u65f6\uff0c\u8fd4\u56de\u6240\u6709 Cookie \u7684 \"name=value; name=value;\" \u683c\u5f0f\u5b57\u7b26\u4e32\u3002\n"
             "\n"
             "- chrome_name: data_chain \u4e2d Chrome \u9a71\u52a8\u7684\u952e\uff08\u9ed8\u8ba4: \"chrome\"\uff09\n"
             "- cookie_name: \u8981\u83b7\u53d6\u7684\u7279\u5b9a Cookie \u540d\u79f0\uff08get_all=\"no\" \u65f6\u4f7f\u7528\uff09\n"
             "- value_key: data_chain \u4e2d\u5b58\u50a8 Cookie \u7684\u952e\n"
             "- get_all: \"yes\" \u83b7\u53d6\u6240\u6709 Cookie\uff08\u9ed8\u8ba4: \"no\"\uff09\n"
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
            
             "\u901a\u8fc7 Selenium \u542f\u52a8 Chrome \u6d4f\u89c8\u5668\u5e76\u5bfc\u822a\u5230\u6307\u5b9a URL\u3002\u901a\u5e38\u662f Web \u76f8\u5173\u6267\u884c\u7684\u7b2c\u4e00\u4e2a\u4efb\u52a1\u3002\n"
             "\n"
             "- page_load_timeout_seconds: \u7b49\u5f85\u9875\u9762\u52a0\u8f7d\u7684\u6700\u5927\u79d2\u6570\uff08\u9ed8\u8ba4: \"180\"\uff09\n"
             "- url: \u76ee\u6807 URL\uff08\u652f\u6301\u8868\u8fbe\u5f0f\uff09\n"
             "- url_key: data_chain 中获取 URL 的键，被设置时优先于 url\n"
             "- chrome_name: data_chain \u4e2d\u5b58\u50a8 Chrome \u9a71\u52a8\u7684\u952e\uff08\u9ed8\u8ba4: \"chrome\"\uff09\n"
             "- skip_in_pipeline: 设为 \"yes\" 时在流水线运行中跳过此任务（默认: \"no\"）\n"
             "- download_folder: chrome 下载路径的文件夹（可选，支持表达式）\n"
        ),
    },

    "desc_GO_TO_TASK": {
        "zh": (
            
             "\u5728\u5f53\u524d\u6267\u884c\u4e2d\u6709\u6761\u4ef6\u5730\u8df3\u8f6c\u5230\u6307\u5b9a\u4efb\u52a1\u3002\n"
             "\u5f53\u6761\u4ef6\u8bc4\u4f30\u4e3a True \u65f6\uff0c\u4ece\u76ee\u6807\u4efb\u52a1\u7ee7\u7eed\u6267\u884c\u800c\u975e\u4e0b\u4e00\u4e2a\u987a\u5e8f\u4efb\u52a1\u3002\u4e3a False \u65f6\u6b63\u5e38\u7ee7\u7eed\u3002\n"
             "\n"
             "- target_task: \u8981\u8df3\u8f6c\u5230\u7684\u76ee\u6807\u4efb\u52a1\u7d22\u5f15\uff08\u4ece 0 \u5f00\u59cb\uff09\n"
             "- condition_fn: Python \u8868\u8fbe\u5f0f\uff0c\u8bc4\u4f30\u4e3a True \u65f6\u6267\u884c\u8df3\u8f6c\n"
        ),
    },

    "desc_HASH_STR": {
        "zh": (
            
             "\u4f7f\u7528\u6307\u5b9a\u7b97\u6cd5\u5bf9\u5b57\u7b26\u4e32\u8fdb\u884c\u54c8\u5e0c\u5e76\u5c06\u5341\u516d\u8fdb\u5236\u6458\u8981\u5b58\u5165 data_chain\u3002\n"
             "\n"
             "- inbound: \u8981\u54c8\u5e0c\u7684\u8f93\u5165\u5b57\u7b26\u4e32\uff08\u652f\u6301\u8868\u8fbe\u5f0f\uff09\n"
             "- outbound_key: data_chain \u4e2d\u5b58\u50a8\u7ed3\u679c\u7684\u952e\n"
             "- algorithms: \u54c8\u5e0c\u7b97\u6cd5\uff08\u9ed8\u8ba4: \"sha256\"\uff09\n"
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
            "- http_response_key: data_chain 中作为 HTTP 响应返回的数据键"
        ),
    },

    "desc_INITIAL_PARAMS": {
        "zh": (
            
             "\u521d\u59cb\u5316\u952e\u503c\u5bf9\u5e76\u4fdd\u5b58\u5230 data_chain\u3002\u6240\u6709\u53c2\u6570\u90fd\u4f5c\u4e3a\u952e\u503c\u5bf9\u5904\u7406\u3002\n"
             "\u503c\u652f\u6301 expression2str \u8fdb\u884c\u52a8\u6001\u6c42\u503c\u3002\n"
             "\n"
             "- (\u4efb\u610f\u952e): \u8981\u521d\u59cb\u5316\u7684\u952e\u540d\u53ca\u5176\u5bf9\u5e94\u503c\uff08\u652f\u6301\u8868\u8fbe\u5f0f\uff09\n"
             "\n"
             "- any_key: any_value - 在 data_chain 中初始化的任意键值对\n"
        ),
    },

    "desc_INPUT_DIALOG": {
        "zh": (
            "在运行时显示弹窗文本输入对话框以收集用户输入，将输入值存入 data_chain。\n"
            "支持在用户取消对话框时停止执行。\n"
            "\n"
            "- title: 对话框标题（支持表达式）\n"
            "- msg: 提示消息（支持表达式）\n"
            "- value_key: data_chain 中存储输入值的键\n"
            "- default_value: 默认输入值（支持表达式）\n"
            "- stop_on_cancel: \"yes\" 用户取消时停止执行（默认: \"yes\"）\n"
        ),
    },

    "desc_MATPLOTLIB": {
        "zh": (
            
             "\u53d1\u9001 PETPEvent \u5728\u5f39\u7a97\u4e2d\u542f\u52a8 Matplotlib \u56fe\u8868\u89c6\u56fe\u3002\n"
             "\u652f\u6301 PIE\uff08\u997c\u56fe\uff09\u3001LINE\uff08\u6298\u7ebf\u56fe\uff09\u548c BAR\uff08\u67f1\u72b6\u56fe\uff09\u7c7b\u578b\u3002\n"
             "\n"
             "- title: 标题（支持表达式）\n"
             "- chart_type: 图表类型 — PIE、LINE 或 BAR\n"
             "- top: 弹窗在屏幕的上方位置（像素）（支持表达式，默认: 100）\n"
             "- left: 弹窗在屏幕的左侧位置（像素）（支持表达式，默认: 100）\n"
             "- msg: 与图表一起显示的附加消息（支持表达式，默认: \"\"）\n"
             "- show_toolbar: 若为 \"True\"，显示工具栏（支持表达式，默认: \"True\"）\n"
             "- data_json: 图表数据的JSON格式字符串，例如 {\"x\":1,\"y\":2}（支持表达式，默认: \"{\\\"x\\\":1,\\\"y\\\":2}\"）\n"
        ),
    },

    "desc_MOUSE_CLICK": {
        "zh": (
            
             "\u5728\u4f4d\u7f6e (x, y) \u6267\u884c\u9f20\u6807\u70b9\u51fb\u3002\u5982\u679c x \u548c y \u90fd\u4e3a -1\uff0c\u4f7f\u7528 data_chain \u4e2d\u7684\u4f4d\u7f6e\u3002\n"
             "\n"
             "- x_from: data_chain \u4e2d\u5b58\u50a8 x \u5750\u6807\u7684\u952e\uff08\u9ed8\u8ba4: \"mouse_at_x\"\uff09\n"
             "- y_from: data_chain \u4e2d\u5b58\u50a8 y \u5750\u6807\u7684\u952e\uff08\u9ed8\u8ba4: \"mouse_at_y\"\uff09\n"
             "- x: \u70b9\u51fb\u7684 x \u5750\u6807\uff0c-1 \u4f7f\u7528 data_chain \u4f4d\u7f6e\uff08\u9ed8\u8ba4: -1\uff09\n"
             "- y: \u70b9\u51fb\u7684 y \u5750\u6807\uff0c-1 \u4f7f\u7528 data_chain \u4f4d\u7f6e\uff08\u9ed8\u8ba4: -1\uff09\n"
             "- wait: 点击后等待的秒数（默认: 5）\n"
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
            
             "\u5728\u4f4d\u7f6e (x, y) \u6267\u884c\u9f20\u6807\u6eda\u52a8\u3002\u5982\u679c x \u548c y \u90fd\u4e3a -1\uff0c\u4f7f\u7528 data_chain \u4e2d\u7684\u4f4d\u7f6e\u3002\n"
             "\n"
             "- x_from: data_chain \u4e2d\u5b58\u50a8 x \u5750\u6807\u7684\u952e\uff08\u9ed8\u8ba4: \"mouse_at_x\"\uff09\n"
             "- y_from: data_chain \u4e2d\u5b58\u50a8 y \u5750\u6807\u7684\u952e\uff08\u9ed8\u8ba4: \"mouse_at_y\"\uff09\n"
             "- x: \u6eda\u52a8\u4f4d\u7f6e\u7684 x \u5750\u6807\uff0c-1 \u4f7f\u7528 data_chain \u4f4d\u7f6e\uff08\u9ed8\u8ba4: -1\uff09\n"
             "- y: \u6eda\u52a8\u4f4d\u7f6e\u7684 y \u5750\u6807\uff0c-1 \u4f7f\u7528 data_chain \u4f4d\u7f6e\uff08\u9ed8\u8ba4: -1\uff09\n"
             "- vertical: 滚动量，正值向上，负值向下（默认: 10）\n"
             "- wait: 滚动后等待的秒数（默认: 5）\n"
        ),
    },

    "desc_MOVE_TO_IFRAME": {
        "zh": (
            "将 Chrome 驱动上下文切换到指定 iframe，支持通过多个 frame ID 访问嵌套 iframe。\n"
            "\n"
            "- frame_ids: frame 标识符列表（索引、名称或 id），如 [\"frame1\", \"frame2\"]。"
            "两个特殊值用于切出 frame 而非切入：\"$default$\" 切回最外层主文档，\"$parent$\" 切回上一层父 frame；"
            "可与真实 id 混用，如 [\"$default$\"] 回到主文档，或 [\"$default$\", \"SMFrame\"] 先重置再重新进入\n"
            "- wait: 切换前静态等待秒数，等 iframe 渲染完成（默认: 1）\n"
            "- timeout: 每个 iframe 变为可见的最大等待秒数（默认: 10）\n"
            "- skip_timeout_error: iframe 在 timeout 内不可见时 — \"yes\" 记日志并继续（chrome 保留）；\"no\" 抛异常。默认 \"no\"\n"
            "- chrome_name: data_chain 中 Chrome driver 的键（默认 \"chrome\"）"
        ),
    },

    "desc_NESTED_TO_FLAT_CONVERTOR": {
        "zh": (
            
             "\u5c06\u5d4c\u5957\u5b57\u5178\u8f6c\u6362\u4e3a\u6241\u5e73\u5b57\u5178\u3002\u652f\u6301\u5d4c\u5957\u7684\u5b57\u5178\u548c\u5217\u8868\u3002\n"
             "\n"
             "- data: \u8981\u8f6c\u6362\u7684\u5d4c\u5957 JSON \u5b57\u7b26\u4e32\uff08data_key \u672a\u8bbe\u7f6e\u65f6\u4f7f\u7528\uff09\n"
             "- data_key: data_chain \u4e2d\u5d4c\u5957\u6570\u636e\u7684\u952e\uff08\u4f18\u5148\u4e8e data\uff09\n"
             "- data_flat_key: data_chain \u4e2d\u5b58\u50a8\u6241\u5e73\u5316\u7ed3\u679c\u7684\u952e\n"
             "- prefix: \u6241\u5e73\u952e\u7684\u524d\u7f00\uff08\u53ef\u9009\uff09\n"
             "- separator: \u952e\u8fde\u63a5\u5206\u9694\u7b26\uff08\u9ed8\u8ba4: \".\"\uff09\n"
        ),
    },

    "desc_OCR": {
        "zh": (
            
             "\u4f7f\u7528\u672c\u5730 OCR \u4ece\u56fe\u7247\u4e2d\u63d0\u53d6\u6587\u5b57\uff08\u65e0\u9700 API \u5bc6\u94a5\uff09\u3002\n"
             "\u652f\u6301\u4e2d\u6587\u3001\u82f1\u6587\u53ca\u591a\u79cd\u5176\u4ed6\u8bed\u8a00\u3002\n"
             "\n"
             "\u652f\u6301\u7684\u5f15\u64ce\uff08\u6309\u4f18\u5148\u7ea7\uff09:\n"
             "\n"
             "- image_path: \u56fe\u7247\u6587\u4ef6\u8def\u5f84\uff08\u652f\u6301\u8868\u8fbe\u5f0f\uff09\n"
             "- image_path_key: data_chain \u4e2d\u56fe\u7247\u8def\u5f84\u7684\u952e\uff08\u4f18\u5148\u4e8e image_path\uff09\n"
             "- lang: \u8bc6\u522b\u8bed\u8a00\uff08\u9ed8\u8ba4: \"ch\"\uff09\n"
             "- backend: OCR \u5f15\u64ce \u2014 paddleocr\u3001rapidocr \u6216 easyocr\uff08\u9ed8\u8ba4: \u81ea\u52a8\u9009\u62e9\uff09\n"
             "- preprocess: OCR 前的图像预处理模式（默认: \"none\"）\n"
             "- filter_func: 用于过滤 OCR 行的 Python 函数体；接收 (line)\n"
             "- result_key: data_chain \u4e2d\u5b58\u50a8\u7ed3\u679c\u7684\u952e\uff08\u9ed8\u8ba4: \"ocr_result\"\uff09\n"
             "- text_key: 针对收集到的纯文本字符串的 data_chain 键\n"
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
        ),
    },

    "desc_PYTUBE": {
        "zh": (
            
             "\u901a\u8fc7 pytube \u4e0b\u8f7d\u6307\u5b9a\u94fe\u63a5\u7684 YouTube \u89c6\u9891\uff0c\u652f\u6301\u4e0d\u540c\u7684\u89c6\u9891\u683c\u5f0f\u548c\u5206\u8fa8\u7387\u3002\n"
             "\n"
             "- video_url: YouTube \u89c6\u9891 URL\uff08\u652f\u6301\u8868\u8fbe\u5f0f\uff09\n"
             "- file_extension: \u89c6\u9891\u683c\u5f0f\uff08\u9ed8\u8ba4: \"mp4\"\uff09\n"
             "- download_folder: \u4e0b\u8f7d\u8f93\u51fa\u76ee\u5f55\u8def\u5f84\uff08\u652f\u6301\u8868\u8fbe\u5f0f\uff09\n"
             "- specific_file_name: 下载文件的确切文件名（可选）\n"
             "- file_prefix: 添加到下载文件名前的前缀（可选）\n"
             "- quality: \u89c6\u9891\u5206\u8fa8\u7387\uff08\u5982 \"720p\"\u3001\"1080p\"\uff0c\u9ed8\u8ba4: \"720p\"\uff09\n"
             "- proxy_url: HTTP/HTTPS 代理 URL，例如 \"http://127.0.0.1:7890\"（可选，也读取环境变量 HTTP_PROXY/HTTPS_PROXY）\n"
             "- file_download_path_key: data_chain \u4e2d\u5b58\u50a8\u4e0b\u8f7d\u8def\u5f84\u7684\u952e\n"
             "- max_retries: 下载失败时的重试次数（默认: 3）\n"
             "- timeout: 下载超时秒数（可选）\n"
        ),
    },

    "desc_READ_CSV": {
        "zh": (
            
             "\u4ece\u6307\u5b9a\u4f4d\u7f6e\u52a0\u8f7d CSV \u6587\u4ef6\uff0c\u5c06\u6570\u636e\u8bfb\u5165\u4e8c\u7ef4\u6570\u7ec4\u5e76\u4fdd\u5b58\u5230 data_chain\u3002\n"
             "\n"
             "- file_path: CSV \u6587\u4ef6\u8def\u5f84\uff08\u652f\u6301\u8868\u8fbe\u5f0f\uff09\n"
             "- file_path_key: 从 data_chain 获取文件路径的键，被设置时优先于 file_path\n"
             "- skip_first: \"yes\" \u8df3\u8fc7\u9996\u884c\uff08\u9ed8\u8ba4: \"no\"\uff09\n"
             "- data_key: data_chain \u4e2d\u5b58\u50a8\u6570\u636e\u7684\u952e\n"
             "- delimiter: CSV \u5206\u9694\u7b26\uff08\u9ed8\u8ba4: \",\"\uff09\n"
        ),
    },

    "desc_READ_EXCEL": {
        "zh": (
            
             "\u52a0\u8f7d MS Excel \u6587\u4ef6\uff0c\u5c06\u6570\u636e\u8bfb\u5165\u4e8c\u7ef4\u6570\u7ec4\u5e76\u4fdd\u5b58\u5230 data_chain\u3002\u652f\u6301\u5b57\u6bb5\u8fc7\u6ee4\u548c\u8df3\u884c\u3002\n"
             "\n"
             "- file_path: Excel \u6587\u4ef6\u8def\u5f84\uff08\u652f\u6301\u8868\u8fbe\u5f0f\uff09\n"
             "- fields: \u8981\u8bfb\u53d6\u7684\u5217\u7d22\u5f15\u5217\u8868\uff0c\u5982 \"0,1,3\"\uff08\u53ef\u9009\uff0c\u9ed8\u8ba4\u5168\u90e8\uff09\n"
             "- sheet_index: 要读取的表单索引，从 0 开始（默认: 0）\n"
             "- file_path_key: 从 data_chain 获取文件路径的键，被设置时优先于 file_path\n"
             "- end_at: 要读取的最大行数（默认: 10）\n"
             "- skip_first: \"yes\" \u8df3\u8fc7\u9996\u884c\uff08\u9ed8\u8ba4: \"no\"\uff09\n"
             "- data_key: data_chain \u4e2d\u5b58\u50a8\u6570\u636e\u7684\u952e\n"
        ),
    },

    "desc_READ_JSON": {
        "zh": (
            
             "\u4ece\u6587\u4ef6\u52a0\u8f7d JSON\uff0c\u53ef\u9009\u901a\u8fc7 json_path \u63d0\u53d6\u6570\u636e\uff0c\u7136\u540e\u4fdd\u5b58\u5230 data_chain\u3002\n"
             "\n"
             "- file_path: JSON \u6587\u4ef6\u8def\u5f84\uff08\u652f\u6301\u8868\u8fbe\u5f0f\uff09\n"
             "- file_path_key: 从 data_chain 获取文件路径的键，被设置时优先于 file_path\n"
             "- json_path: JSONPath \u8868\u8fbe\u5f0f\u63d0\u53d6\u7279\u5b9a\u6570\u636e\uff08\u53ef\u9009\uff09\n"
             "- data_key: data_chain \u4e2d\u5b58\u50a8\u6570\u636e\u7684\u952e\n"
        ),
    },

    "desc_READ_TEXT_FROM_FILE": {
        "zh": (
            "读取文本文件的全部内容并存入 data_chain 的指定键。\n"
            "\n"
            "- file_path: 要读取的文本文件路径（支持表达式）\n"
            "- data_key: data_chain 中存储内容的键\n"
        ),
    },

    "desc_RELOAD_LOG": {
        "zh": (
            
             "\u89e6\u53d1 PETP UI \u4e2d\u65e5\u5fd7\u7a97\u53e3\u7684\u5237\u65b0\u4ee5\u663e\u793a\u6700\u65b0\u65e5\u5fd7\u6761\u76ee\u3002\n"
             "\u5728\u4e00\u7cfb\u5217\u4efb\u52a1\u540e\u786e\u4fdd\u65e5\u5fd7\u89c6\u56fe\u662f\u6700\u65b0\u7684\u3002\n"
             "\n"
             "- (\u65e0\u53c2\u6570)\n"
             "\n"
             "- name: 此任务步骤的描述性标签（支持表达式，默认: \"reload logger\"）\n"
        ),
    },

    "desc_RECEIVE_EMAIL": {
        "zh": (
            "通过 IMAP 从邮箱接收邮件，并将解析结果写入 data_chain。\n"
            "\n"
            "- host: IMAP 服务器地址（支持表达式）\n"
            "- port: IMAP 服务器端口（默认: 993）\n"
            "- name: IMAP 登录用户名/邮箱地址（支持表达式）\n"
            "- pwd: IMAP 登录密码或应用专用密码（支持表达式）\n"
            "- mailbox: 要读取的邮箱文件夹，如 \"INBOX\"（支持表达式，默认: \"INBOX\"）\n"
            "- criteria: IMAP 搜索条件，如 \"UNSEEN\"、\"ALL\"、\"FROM \\\"x@x.com\\\"\"（支持表达式，默认: \"UNSEEN\"）\n"
            "- sender: 可选的发件人邮箱过滤条件；支持用 \";\" 或 \",\" 分隔多个地址（支持表达式，默认: \"\"）\n"
            "- subject_contains: 可选的邮件主题关键字/短语过滤条件（支持表达式，默认: \"\"）\n"
            "- limit: 最多读取匹配到的最新邮件数；<=0 表示全部（支持表达式，默认: \"10\"）\n"
            "- use_ssl: \"yes\" 使用 IMAP SSL，\"no\" 使用普通 IMAP（默认: \"yes\"）\n"
            "- mark_seen: \"yes\" 将已读取邮件标记为已读（默认: \"yes\"）\n"
            "- save_attachments: \"yes\" 保存邮件附件到本地目录（默认: \"no\"）\n"
            "- attachments_dir: save_attachments=\"yes\" 时附件保存目录（支持表达式，默认: \"{p.get_ddir()}/email_attachments\"）\n"
            "- detail_level: \"detail\" 返回所有字段；\"summary\" 仅返回 subject/from/to/date/attachments(文件名)/text(前50字符)（默认: \"detail\"）\n"
            "- data_key: data_chain 中存储邮件列表的键（默认: \"emails\"）\n"
            "- attachments_key: data_chain 中存储所有已保存附件路径列表的键（默认: \"\"）\n"
            "- timeout: IMAP 连接超时秒数（支持表达式，默认: \"30\"）\n"
            "- fail_on_error: \"yes\" 出错时抛错；\"no\" 仅记录日志并继续（默认: \"yes\"）\n"
            "- result_key: data_chain 中存储接收结果 {\"ok\": bool, \"count\": int, \"error\": str|None} 的键；不填则不写入（默认: \"\"）"
        ),
    },

    "desc_RUN_EXECUTION": {
        "zh": (
            
             "\u6309\u540d\u79f0\u8fd0\u884c\uff08\u89e6\u53d1\uff09\u6307\u5b9a\u7684\u6267\u884c\uff0c\u652f\u6301\u53ef\u9009\u53c2\u6570\u3002\u5982\u679c if_stop \u8bbe\u4e3a \"yes\"\uff0c\u6267\u884c\u5c06\u88ab\u5b8c\u5168\u8df3\u8fc7\u3002\n"
             "\n"
             "- execution: \u8981\u8fd0\u884c\u7684\u6267\u884c\u540d\u79f0\uff08\u652f\u6301\u8868\u8fbe\u5f0f\uff09\n"
             "- params: \u521d\u59cb\u5316\u6570\u636e JSON \u5b57\u7b26\u4e32\uff08\u53ef\u9009\uff09\n"
             "- if_stop: \"yes\" \u8df3\u8fc7\u6267\u884c\uff08\u9ed8\u8ba4: \"no\"\uff09\n"
        ),
    },

    "desc_RUN_JAVASCRIPT": {
        "zh": (
            
             "\u4f7f\u7528 PythonMonkey \u8fd0\u884c\u65f6\u6267\u884c\u5916\u90e8 .js \u6587\u4ef6\u4e2d\u7684 JavaScript \u51fd\u6570\u3002\n"
             "JS \u6587\u4ef6\u5e94\u5bfc\u51fa\u4e00\u4e2a\u63a5\u53d7\u5355\u4e2a\u53c2\u6570\uff08\u5bf9\u8c61/\u5b57\u5178\uff09\u5e76\u8fd4\u56de\u5355\u4e2a\u7ed3\u679c\u5bf9\u8c61\u7684\u6a21\u5757\u51fd\u6570\u3002\n"
             "JS \u4ee3\u7801\u6bb5\u5168\u5c40\u7f13\u5b58\u4ee5\u63d0\u9ad8\u6027\u80fd\u3002\n"
             "\n"
             "- js_file: \u8981\u8c03\u7528\u7684\u5bfc\u51fa\u51fd\u6570\u540d\uff08\u652f\u6301\u8868\u8fbe\u5f0f\uff09\n"
             "- params: 传递给 JavaScript 函数的参数；如果适用则解析为 JSON（支持表达式，默认: \"\"）\n"
             "- data_key: data_chain \u4e2d\u5b58\u50a8 JS \u6267\u884c\u7ed3\u679c\u7684\u952e\n"
        ),
    },

    "desc_RUN_SFTP_GET": {
        "zh": (
            
             "\u901a\u8fc7 paramiko SFTP \u5ba2\u6237\u7aef\u4ece\u8fdc\u7a0b\u670d\u52a1\u5668\u4e0b\u8f7d\u6587\u4ef6\u5230\u672c\u5730\u3002\n"
             "\n"
             "- from_remote: \u8fdc\u7a0b\u6587\u4ef6\u8def\u5f84\uff08\u652f\u6301\u8868\u8fbe\u5f0f\uff09\n"
             "- to_local: \u672c\u5730\u76ee\u6807\u6587\u4ef6\u8def\u5f84\uff08\u652f\u6301\u8868\u8fbe\u5f0f\uff09\n"
             "- sftp_client_key: data_chain \u4e2d SFTP \u5ba2\u6237\u7aef\u7684\u952e\uff08\u9ed8\u8ba4: \"sftpclient\"\uff09\n"
             "- sftp_get_file_key: 存放下载后本地文件路径的 data_chain 键\n"
             "- close_after_run: \"yes\" \u4e0b\u8f7d\u540e\u5173\u95ed SFTP \u8fde\u63a5\uff08\u9ed8\u8ba4: \"yes\"\uff09\n"
        ),
    },

    "desc_RUN_SFTP_PUT": {
        "zh": (
            
             "\u901a\u8fc7 paramiko SFTP \u5ba2\u6237\u7aef\u4ece\u672c\u5730\u4e0a\u4f20\u6587\u4ef6\u5230\u8fdc\u7a0b\u670d\u52a1\u5668\u3002\n"
             "\n"
             "- from_local: \u672c\u5730\u6587\u4ef6\u8def\u5f84\uff08\u652f\u6301\u8868\u8fbe\u5f0f\uff09\n"
             "- to_remote: \u8fdc\u7a0b\u76ee\u6807\u6587\u4ef6\u8def\u5f84\uff08\u652f\u6301\u8868\u8fbe\u5f0f\uff09\n"
             "- sftp_client_key: data_chain \u4e2d SFTP \u5ba2\u6237\u7aef\u7684\u952e\uff08\u9ed8\u8ba4: \"sftpclient\"\uff09\n"
             "- sftp_put_file_key: 存放上传后远程文件路径的 data_chain 键\n"
             "- close_after_run: \"yes\" \u4e0a\u4f20\u540e\u5173\u95ed SFTP \u8fde\u63a5\uff08\u9ed8\u8ba4: \"yes\"\uff09\n"
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
            
             "\u5bf9\u5f53\u524d\u6d4f\u89c8\u5668\u9875\u9762\u6216\u6307\u5b9a\u5143\u7d20\u8fdb\u884c\u622a\u56fe\u5e76\u4fdd\u5b58\u5230\u6587\u4ef6\u3002\n"
             "\n"
             "- xpath: \u8981\u622a\u56fe\u7684\u5143\u7d20 xpath\uff08\u53ef\u9009\uff0c\u9ed8\u8ba4\u6574\u4e2a\u9875\u9762\uff09\n"
             "- padding: 在各个方向围绕 xpath 元素扩展的额外像素（默认: 0）\n"
             "- crop: 以 \"左|>上|>右|>下\" 绝对像素值裁剪区域（可选）；优先于 xpath\n"
             "- format: 图像格式，例如 \"png\"（默认: \"png\"）\n"
             "- show: 拍摄后若是 \"yes\" 则打开截图（默认: \"no\"）\n"
             "- file_path: \u622a\u56fe\u4fdd\u5b58\u8def\u5f84\uff08\u652f\u6301\u8868\u8fbe\u5f0f\uff09\n"
             "- file_path_key: data_chain \u4e2d\u622a\u56fe\u8def\u5f84\u7684\u952e\uff08\u4f18\u5148\u4e8e file_path\uff09\n"
             "- data_key: 存储保存的截图文件路径的 data_chain 键\n"
             "- wait: 截取前额外等待秒数（默认: 3）\n"
             "- chrome_name: \u5b58\u50a8 Chrome \u9a71\u52a8\u7684 data_chain \u952e\uff08\u9ed8\u8ba4: \"chrome\"\uff09\n"
        ),
    },
    "desc_SELECT_MULTI_DROPDOWN": {
        "zh": (
            "在可多选的复选框下拉框中勾选一个或多个选项（如 SAP Ariba 的“供应商属性”：制造商/代理商/贸易商）。\n"
            "需要时自动展开下拉，然后逐个勾选传入的值。选项文本按模糊（contains）且大小写不敏感匹配；已勾选的保持不变（幂等）；只勾选传入的值，不清除已有选择。\n"
            "\n"
            "- values: 要选择的选项文本，用 \",\" 或 \">\" 分隔，如 \"制造商,代理商\"；每项支持表达式，如 \"{types}\"（必填）\n"
            "- container_xpath: 限定下拉控件范围的 xpath，所有查找都在其内部。空=整页。建议用该字段的输入框/容器，如 \"//input[@aria-label='供应商属性']/ancestor::div[contains(@class,'input-drop-down-container')]\"（默认: \"\"）\n"
            "- expand_xpath: 打开下拉要点击的元素 xpath（container 给定时相对其内，否则绝对）。空=自动（点 expand_more 图标 / combobox 输入框）（默认: \"\"）\n"
            "- item_class: 标记每个带复选框选项行的 CSS 类（默认: \"drop-down-menu-item-with-checkbox\"）\n"
            "- wait: 开始前静态等待秒数（默认: 1）\n"
            "- timeout: 等待下拉/选项出现的最大秒数（默认: 10）\n"
            "- skip_timeout_error: \"yes\" 某选项找不到或点击失败时记日志并继续；\"no\" 抛异常（默认: \"yes|no\"）\n"
            "- close_xpath: 勾选完成后关闭下拉要点击的元素 xpath。以 \".\" 开头的相对 xpath 会限定在 container_xpath 内（只关闭本下拉的收起图标，不会误关外层面板）；绝对 xpath 原样使用。空=保持下拉当前状态；支持表达式（默认: \"\"）\n"
            "- skip_if_fn: Python 函数体，参数为 (p)；返回 True 则在定位之前直接跳过整个 processor（例如 values 由可能不存在的 data_chain 值拼接时）（默认: \"return False\"）\n"
            "- chrome_name: data_chain 中 Chrome driver 的键（默认: \"chrome\"）"
        ),
    },
    "desc_SELECT_SINGLE_DROPDOWN": {
        "zh": (
            "在单选 type-ahead 下拉中选中一个选项（如 SAP Ariba 的“企业注册性质”：国企/私企/有限责任公司）。\n"
            "需要时自动展开下拉，找到可见文本匹配（模糊 contains、大小写不敏感）的选项行并点击一次。\n"
            "单选点中后下拉会自行关闭，无需额外关闭步骤。\n"
            "\n"
            "- value: 要选中的选项文本，如 \"国企\"（支持表达式，如 \"{kind}\"）；若传入多个逗号分隔文本，只用第一个（必填）\n"
            "- container_xpath: 限定下拉控件范围的 xpath，所有查找都在其内部。空=整页。建议用该字段的输入框/容器，如 \"//input[@aria-label='企业注册性质']/ancestor::div[contains(@class,'input-drop-down-container')]\"（默认: \"\"）\n"
            "- expand_xpath: 打开下拉要点击的元素 xpath（container 给定时相对其内，否则绝对）。空=自动（点 expand_more 图标 / combobox 输入框）（默认: \"\"）\n"
            "- item_class: 标记每个选项行的 CSS 类（默认: \"type-ahead-list-item\"）\n"
            "- wait: 开始前静态等待秒数（默认: 1）\n"
            "- timeout: 等待下拉/选项出现的最大秒数（默认: 10）\n"
            "- skip_timeout_error: \"yes\" 选项找不到或点击失败时记日志并继续；\"no\" 抛异常（默认: \"yes|no\"）\n"
            "- skip_if_fn: Python 函数体，参数为 (p)；返回 True 则在定位之前直接跳过整个 processor（例如 value 由可能不存在的 data_chain 值拼接时）（默认: \"return False\"）\n"
            "- chrome_name: data_chain 中 Chrome driver 的键（默认: \"chrome\"）"
        ),
    },
    "desc_DATE_PICKER": {
        "zh": (
            "在 Angular Material 日期选择器（md-datepicker-content 日历弹层）中选中一个日期。\n"
            "传入形如 \"2026-07-20\" 的日期，自动打开日历，必要时点上/下月箭头导航到目标月份，再点中日期格。\n"
            "日期格按其英文 aria-label（如 \"July 20, 2026\"，Material 固定渲染的唯一可靠定位）匹配。\n"
            "适用于 readonly、无法 send_keys、只能从日历点选的日期输入框。\n"
            "\n"
            "- date: 目标日期（支持表达式，如 \"{reg_date}\"）（必填）\n"
            "- date_format: date 的 strptime 解析格式（默认: \"%Y-%m-%d\"）\n"
            "- open_xpath: 打开日历的按钮 xpath。空=认为已打开（默认: \"//button[@aria-label='Open calendar']\"）\n"
            "- calendar_xpath: 日历弹层根节点 xpath，导航与日期查找都限定其内（默认: \"//md-datepicker-content\"）\n"
            "- max_nav: 上/下月箭头最多点击次数的安全上限（默认: 24）\n"
            "- wait: 开始前静态等待秒数（默认: 1）\n"
            "- timeout: 等待日历/日期格出现的最大秒数（默认: 10）\n"
            "- skip_timeout_error: \"yes\" 日历/日期找不到或点击失败时记日志并继续；\"no\" 抛异常（默认: \"yes|no\"）\n"
            "- skip_if_fn: Python 函数体，参数为 (p)；返回 True 则在定位之前直接跳过整个 processor（例如 date 由可能不存在的 data_chain 值拼接时）（默认: \"return False\"）\n"
            "- chrome_name: data_chain 中 Chrome driver 的键（默认: \"chrome\"）"
        ),
    },
    "desc_BANK_INFO_FEEDER": {
        "zh": (
            "用一个以 \";\" 分隔的字符串填写 SAP Ariba 银行账户表单的四个必填字段，顺序为:国家;银行代码;账号;IBAN编号"
            "（例:\"中国;ICBC;400059399234u2;32341\"）。国家/地区是 type-ahead(md-autocomplete):先键入国家名，"
            "再从弹出列表中点击可见文本【完全等于】该国家的选项（键入\"中国\"也会列出\"中立区\"/\"中非共和国\"，故需精确匹配）。"
            "其余三项是普通文本框（清空后输入），按 aria-label 定位。\n"
            "\n"
            "- value: \";\" 分隔的\"国家;银行代码;账号;IBAN\"——四项全必填（支持表达式，如 \"{bank_info}\"）（必填）\n"
            "- country_label: 国家 type-ahead 输入框的 aria-label（默认: \"国家/地区\"）\n"
            "- bank_key_label: 银行代码输入框的 aria-label（默认: \"银行账户信息 银行代码/ABA 传送号码\"）\n"
            "- account_label: 帐号输入框的 aria-label（默认: \"银行账户信息 帐号\"）\n"
            "- iban_label: IBAN 输入框的 aria-label（默认: \"银行账户信息 IBAN 编号\"）\n"
            "- option_class: 自动完成选项行的 CSS 类（默认: \"mat-option\"）\n"
            "- wait: 开始前静态等待秒数（默认: 1）\n"
            "- timeout: 等待输入框/选项列表出现的最大秒数（默认: 10）\n"
            "- skip_timeout_error: \"yes\" 输入框/选项找不到时记日志并继续；\"no\" 抛异常（默认: \"yes|no\"）\n"
            "- skip_if_fn: Python 函数体，参数为 (p)；返回 True 则在定位之前直接跳过整个 processor（默认: \"return False\"）\n"
            "- chrome_name: data_chain 中 Chrome driver 的键（默认: \"chrome\"）"
        ),
    },
    "desc_CONTACT_FEEDER": {
        "zh": (
            "用一个以 \";\" 分隔的字符串填写 SAP Ariba 办公地址联系块的八个字段，顺序为:街道;地区;邮编;城市;国家;省;电话;邮箱"
            "（任一段可留空以跳过该字段）。其中六项是普通文本框，按 aria-label 定位（街道 / 地区 / 邮政编码 / 城市 / 电话 / 电子邮箱，清空后输入）。"
            "国家/地区 和 州/省/地区 都是 type-ahead(md-autocomplete):先键入值，再点击可见文本【完全等于】它的选项；"
            "若无精确匹配则点【唯一包含】它的选项（这样省份传\"辽宁\"能匹配下拉里的\"辽宁(070)\"，而\"中国\"精确命中不会误选\"中立区\"/\"中非共和国\"）。\n"
            "\n"
            "- value: \";\" 分隔的 街道;地区;邮编;城市;国家;省;电话;邮箱——共八个位置，留空则跳过该字段（支持表达式，如 \"{contact}\"）（必填）\n"
            "- option_class: 自动完成选项行的 CSS 类（默认: \"mat-option\"）\n"
            "- wait: 开始前静态等待秒数（默认: 1）\n"
            "- timeout: 等待输入框/选项列表出现的最大秒数（默认: 10）\n"
            "- skip_timeout_error: \"yes\" 输入框/选项找不到时记日志并继续；\"no\" 抛异常（默认: \"yes|no\"）\n"
            "- skip_if_fn: Python 函数体，参数为 (p)；返回 True 则在定位之前直接跳过整个 processor（默认: \"return False\"）\n"
            "- chrome_name: data_chain 中 Chrome driver 的键（默认: \"chrome\"）"
        ),
    },
    "desc_FILE_UPLOAD": {
        "zh": (
            "通过向 <input type=\"file\"> 发送文件的绝对路径来上传文件——WebDriver 的标准做法，绕过操作系统的文件选择对话框。"
            "支持【隐藏】的 file input（如 Angular\"上载文件\"控件里 class 含 hidden 的真实 input）:与 FIND_THEN_KEYIN 不同，"
            "本 processor 只等元素【存在(presence)】而非【可见】（隐藏 input 永远不可见，等可见必然超时），并可先移除其隐藏状态。\n"
            "\n"
            "- identity: file input 的 xpath，如 \"//sm-questionnaire-item[.//span[contains(.,'7.2')]]//input[@type='file']\"（支持表达式）（必填）\n"
            "- file_path: 要上传文件的【绝对路径】，须在运行 PETP 的机器上真实存在（浏览器在本地读取该文件）。支持表达式，如 \"{attached_sales_performance}\"（必填）\n"
            "- reveal_hidden: \"yes\" 上传前先用一小段 JS 移除 input 的 'hidden'/'hidden-input' 类并清除 display:none（部分环境拒绝对完全隐藏的 input send_keys）；\"no\" 保持原样（默认: \"yes|no\"）\n"
            "- wait: 开始前静态等待秒数（默认: 1）\n"
            "- timeout: 等待 file input 在 DOM 中【出现】的最大秒数（默认: 30）\n"
            "- skip_timeout_error: \"yes\" input 找不到或文件不存在时记日志并返回；\"no\" 抛异常（默认: \"yes|no\"）\n"
            "- skip_if_fn: Python 函数体，参数为 (p)；返回 True 则在定位之前直接跳过整个 processor（默认: \"return False\"）\n"
            "- chrome_name: data_chain 中 Chrome driver 的键（默认: \"chrome\"）"
        ),
    },
    "desc_SELECT_TREE_DROPDOWN": {
        "zh": (
            "\u64cd\u4f5c SAP Ariba \u7684\u591a\u7ea7\u7ea7\u8054\u6811\u5f62\u4e0b\u62c9\uff08smq-browse-lists / browse-pane / browse-entry\uff09\u3002\n"
            "\u6309\u987a\u5e8f\u4f20\u5165\u6bcf\u4e00\u7ea7\u7684\u9009\u9879\u6587\u672c\uff081~8 \u7ea7\uff09\uff0c\u9010\u7ea7\u70b9\u51fb\u9009\u9879\u7684 \">\" \u53f3\u7bad\u5934\uff08expansion-btn\uff09\u5c55\u5f00\u4e0b\u4e00\u7ea7\uff0c"
            "\u6700\u540e\u4e00\u7ea7\u70b9\u51fb\u5176\u590d\u9009\u6846\u5b8c\u6210\u52fe\u9009\u3002\u9009\u9879\u6587\u672c\u6309\u53ef\u89c1\u6587\u672c\uff08.wrapped-text-content\uff09\u505a\u6a21\u7cca\u5339\u914d\uff08contains\uff09\uff0c\u4f20\u5165\u90e8\u5206\u5173\u952e\u5b57\u5373\u53ef\uff0c\u5e76\u9650\u5b9a\u5728\u6811\u5bb9\u5668\u5185\u3002\n"
            "\n"
            "- selections: 用 \">\" 分隔的各级选项文本，最外层在前，如 \"支持和服务>海外>亚太>迪拜院\"，共 1~8 级；每级模糊匹配（可传部分关键字）；支持表达式，如 \"{level1}>{level2}\" 或整串 \"{path}\"（也兼容传列表）（必填）\n"
            "- open_xpath: 打开该下拉的按钮/元素的绝对 xpath（树容器要点击此按钮后才出现）；点击后等待第一级文本在 DOM 出现。空=认为已打开，跳过此步；支持表达式（默认: \"\"）\n"
            "- close_xpath: 勾选完成后关闭下拉要点击的按钮/元素的绝对 xpath（通常与 open_xpath 是同一个 toggle 按钮）。空=保持下拉当前状态；支持表达式（默认: \"\"）\n"
            "- select_last: \"yes\" \u70b9\u51fb\u6700\u540e\u4e00\u7ea7\u7684\u590d\u9009\u6846\u8fdb\u884c\u52fe\u9009\uff1b\"no\" \u4ec5\u5c55\u5f00\u6700\u540e\u4e00\u7ea7\uff08\u9ed8\u8ba4: \"yes|no\"\uff09\n"
            "- check_from_level: 从第几级（1 起）开始勾选复选框；之前的级别只展开不勾。如 \"All>油气新能源>科研业务>迪拜院\"，值为 1 时全勾（含 All），值为 2 时 All 不勾、其余勾选（默认: 1）\n"
            "- container_xpath: \u6811\u63a7\u4ef6\u6839\u8282\u70b9 xpath\uff0c\u6240\u6709\u67e5\u627e\u90fd\u9650\u5b9a\u5728\u5176\u5185\u90e8\uff08\u9ed8\u8ba4: \"//smq-browse-lists\"\uff09\n"
            "- entry_class: 标记每个选项节点的 CSS 类（默认: \"browse-entry\"）\n"
            "- pane_tag: 每级列的标签/选择器，用于同名跨级消歧（默认: \"browse-pane\"）\n"
            "- text_class: 承载选项可见文本的元素 CSS 类（默认: \"wrapped-text-content\"）\n"
            "- checked_state: 图标文本为该值表示“已勾选”（默认: \"check_box\"）\n"
            "- wait: \u5f00\u59cb\u524d\u9759\u6001\u7b49\u5f85\u79d2\u6570\uff0c\u7b49\u63a7\u4ef6\u6e32\u67d3\u5b8c\u6210\uff08\u9ed8\u8ba4: 1\uff09\n"
            "- timeout: \u7b49\u5f85\u6bcf\u4e00\u7ea7\u9009\u9879 / \u4e0b\u4e00\u7ea7\u9762\u677f\u51fa\u73b0\u7684\u6700\u5927\u79d2\u6570\uff08\u9ed8\u8ba4: 10\uff09\n"
            "- skip_timeout_error: \"yes\" \u67d0\u7ea7\u6587\u672c\u627e\u4e0d\u5230\u6216\u70b9\u51fb\u88ab\u62e6\u622a\u65f6\u8bb0\u65e5\u5fd7\u5e76\u7ee7\u7eed\uff1b\"no\" \u629b\u5f02\u5e38\uff08\u9ed8\u8ba4: \"yes|no\"\uff09\n"
            "- skip_if_fn: Python \u51fd\u6570\u4f53\uff0c\u53c2\u6570\u4e3a (p)\uff1b\u8fd4\u56de True \u5219\u5728\u5b9a\u4f4d\u4e4b\u524d\u76f4\u63a5\u8df3\u8fc7\u6574\u4e2a processor\uff08\u4f8b\u5982 selections \u7531\u53ef\u80fd\u4e0d\u5b58\u5728\u7684 data_chain \u503c\u62fc\u63a5\u65f6\uff09\uff08\u9ed8\u8ba4: \"return False\"\uff09\n"
            "- chrome_name: data_chain \u4e2d Chrome driver \u7684\u952e\uff08\u9ed8\u8ba4: \"chrome\"\uff09"
        ),
    },
    "desc_DUMP_DOM": {
        "zh": (
            "\u8c03\u8bd5\u8f85\u52a9\uff1adump \u5f53\u524d frame \u7684 DOM\uff0c\u7528\u4e8e\u6392\u67e5\u5b9a\u4f4d\u5668\u4e3a\u4f55\u5931\u8d25\uff08\u5c24\u5176 headless \u6a21\u5f0f\uff09\u3002"
            "\u628a\u5f53\u524d frame \u7684\u5b8c\u6574 HTML \u5199\u5165\u6587\u4ef6\uff0c\u53ef\u9009\u4fdd\u5b58\u622a\u56fe\uff0c\u5e76\u8bb0\u5f55\u5f53\u524d frame \u5185\u6bcf\u4e2a <input> \u7684 "
            "aria-label / id / name / \u53ef\u89c1\u6027\u3002\u63d2\u5728\u5b9a\u4f4d\u4e0d\u5230\u5143\u7d20\u7684 FIND_THEN_* \u4efb\u52a1\u4e4b\u524d\u4f7f\u7528\u3002\n"
            "\n"
            "- file_path: \u5199\u5165 frame HTML \u7684\u8def\u5f84\uff08\u652f\u6301\u8868\u8fbe\u5f0f\uff09\u3002\u9ed8\u8ba4 <\u4e0b\u8f7d\u76ee\u5f55>/dump_dom.html\uff0c\u540c\u540d .png \u7528\u4e8e\u622a\u56fe\n"
            "- screenshot: \"yes\" \u65f6\u540c\u65f6\u4fdd\u5b58\u622a\u56fe\uff08\u9ed8\u8ba4: \"yes\"\uff09\n"
            "- list_inputs: \"yes\" \u65f6\u8bb0\u5f55\u6240\u6709 <input>\uff08aria-label/id/name/\u53ef\u89c1\u6027\uff09\uff08\u9ed8\u8ba4: \"yes\"\uff09\n"
            "- wait: dump \u524d\u7684\u989d\u5916\u7b49\u5f85\u79d2\u6570\uff0c\u7b49 frame \u6e32\u67d3\u5b8c\u6210\uff08\u9ed8\u8ba4: 1\uff09\n"
            "- chrome_name: \u5b58\u50a8 Chrome \u9a71\u52a8\u7684 data_chain \u952e\uff08\u9ed8\u8ba4: \"chrome\"\uff09\n"
        ),
    },

    "desc_SELECT_YESNO": {
        "zh": (
            "\u6839\u636e\u5b57\u6bb5\u6807\u7b7e\u9009\u62e9 SAP Ariba \u662f/\u5426\u5355\u9009\u6846\uff08radio group\uff09\u4e2d\u7684 \u662f \u6216 \u5426\u3002\n"
            "\u901a\u8fc7 label \u6a21\u7cca\u5339\u914d\uff08contains\u3001\u5927\u5c0f\u5199\u4e0d\u654f\u611f\uff09radio group \u7684 aria-label \u6765\u5b9a\u4f4d\u5206\u7ec4\u2014\u2014"
            "\u6240\u4ee5\u540c\u4e00\u9875\u4e0a\u591a\u4e2a\u540c\u6837\u5f0f\u7684\u662f/\u5426\u5206\u7ec4\u9760\u5404\u81ea\u7684 label \u533a\u5206\u3002\u5206\u7ec4\u5185\u6309\u53ef\u89c1\u6587\u672c\uff08\u662f/\u5426\uff09\u9009\u4e2d\u5bf9\u5e94\u9879\uff0c"
            "\u4e0d\u7528 radio \u81ea\u8eab\u7684 aria-label\uff08Ariba \u628a\u4e24\u4e2a\u6309\u94ae\u90fd\u8bef\u6807\u6210\u201c\u5426\u201d\uff09\uff0c\u4e5f\u4e0d\u7528\u52a8\u6001 id\u3002"
            "\u70b9\u51fb\u5728\u6d4f\u89c8\u5668\u5185\u4e00\u6b21\u6027\u5b8c\u6210\uff0c\u89c4\u907f Angular Material \u70b9\u51fb\u76ee\u6807\u5728 label/input \u4e0a\u7684\u5751\u3002\n"
            "\n"
            "- label: \u7528\u4e8e\u5b9a\u4f4d radio group \u7684\u5b57\u6bb5\u6807\u7b7e\uff0c\u6309 aria-label \u6a21\u7cca\u5339\u914d\uff0c\u5982 \"\u662f\u5426\u6c11\u4f01\"\uff1b\u652f\u6301\u8868\u8fbe\u5f0f\uff0c\u5982 \"{field}\"\uff08\u5fc5\u586b\uff09\n"
            "- value: \u9009\u54ea\u4e2a\u2014\u2014\u63a5\u53d7 \u662f/\u5426\u3001yes/no\u3001y/n\u3001true/false\u30011/0\uff08\u5927\u5c0f\u5199\u4e0d\u654f\u611f\uff09\uff1b\u652f\u6301\u8868\u8fbe\u5f0f\uff0c\u5982 \"{is_private}\"\uff08\u5fc5\u586b\uff09\n"
            "- group_tag: \u5e26 aria-label \u7684 radio group \u5143\u7d20\u7684\u6807\u7b7e/CSS \u9009\u62e9\u5668\uff08\u9ed8\u8ba4: \"md-radio-group\"\uff09\n"
            "- button_tag: \u5206\u7ec4\u5185\u6bcf\u4e2a radio \u6309\u94ae\u5143\u7d20\u7684\u6807\u7b7e/CSS \u9009\u62e9\u5668\uff08\u9ed8\u8ba4: \"md-radio-button\"\uff09\n"
            "- text_class: \u627f\u8f7d radio \u53ef\u89c1 \u662f/\u5426 \u6587\u672c\u7684\u5143\u7d20 CSS \u7c7b\uff08\u9ed8\u8ba4: \"mat-radio-label-content\"\uff09\n"
            "- wait: \u5f00\u59cb\u524d\u9759\u6001\u7b49\u5f85\u79d2\u6570\uff0c\u7b49\u8868\u5355\u6e32\u67d3\u5b8c\u6210\uff08\u9ed8\u8ba4: 1\uff09\n"
            "- timeout: \u7b49\u5f85 radio group \u51fa\u73b0\u7684\u6700\u5927\u79d2\u6570\uff08\u9ed8\u8ba4: 10\uff09\n"
            "- skip_timeout_error: \"yes\" \u627e\u4e0d\u5230\u5206\u7ec4/\u9009\u9879\u65f6\u8bb0\u65e5\u5fd7\u5e76\u7ee7\u7eed\uff1b\"no\" \u629b\u5f02\u5e38\uff08\u9ed8\u8ba4: \"yes|no\"\uff09\n"
            "- chrome_name: \u5b58\u50a8 Chrome \u9a71\u52a8\u7684 data_chain \u952e\uff08\u9ed8\u8ba4: \"chrome\"\uff09"
        ),
    },

    "desc_SEND_EMAIL": {
        "zh": (
            "通过 SMTP 发送电子邮件。支持纯文本/HTML 正文、CC/BCC 和多附件。\n"
            "\n"
            "- smtp: SMTP 服务器地址（支持表达式）\n"
            "- port: SMTP 服务器端口（默认: 25）\n"
            "- name: SMTP 用户名/发件人（支持表达式）\n"
            "- pwd: SMTP 密码（支持表达式和加密值）\n"
            "- to: 收件人地址，多个用逗号分隔（支持表达式）\n"
            "- cc: 抄送地址，多个用逗号分隔（支持表达式，可选）\n"
            "- bcc: 密送地址，多个用逗号分隔（支持表达式，可选）\n"
            "- subject: 邮件主题（支持表达式）\n"
            "- content: 邮件正文内容（支持表达式）\n"
            "- content_type: 正文类型，\"plain\" 或 \"html\"（支持表达式，默认: \"plain\"）\n"
            "- attachment: 兼容旧版的单附件路径（支持表达式，可选）\n"
            "- attachments: 多附件路径，支持逗号/分号/换行分隔（支持表达式，可选）\n"
            "- use_tls: \"yes\" 启用 STARTTLS（默认: \"no\"）\n"
            "- use_ssl: \"yes\" 使用 SMTP SSL 直连（默认: \"no\"）\n"
            "- timeout: SMTP 连接超时秒数（支持表达式，默认: \"30\"）\n"
            "- fail_on_error: \"yes\" 发送失败时抛错；\"no\" 仅记录日志并继续（默认: \"yes\"）\n"
            "- result_key: data_chain 中存储发送结果 {\"ok\": bool, \"error\": str|None} 的键；不填则不写入（默认: \"\"）"
        ),
    },

    "desc_SHOW_RESULT": {
        "zh": (
            "在 PETP UI 中显示弹窗对话框展示结果信息。在后台模式下记录日志。\n"
            "\n"
            "- title: 弹窗标题（支持表达式）\n"
            "- msg: 弹窗消息内容（支持表达式）"
        ),
    },

    "desc_STOPPER": {
        "zh": (
            
             "\u505c\u6b62\u5f53\u524d\u6267\u884c\u3002\u53ef\u901a\u8fc7\u6761\u4ef6\u63a7\u5236\u662f\u5426\u505c\u6b62\u3002\n"
             "\n"
             "- stop_after: Python \u8868\u8fbe\u5f0f\uff0c\u4e3a True \u65f6\u505c\u6b62\u6267\u884c\uff08\u53ef\u9009\uff0c\u9ed8\u8ba4\u65e0\u6761\u4ef6\u505c\u6b62\uff09\n"
             "- stop_in_minutes: 允许执行的最大分钟数，超过将停止；设为 \"0\" 以禁用此检查（支持表达式，默认: \"0\"）\n"
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
            
             "\u7b49\u5f85\u6307\u5b9a\u6761\u4ef6\u6ee1\u8db3\u6216\u8d85\u65f6\u3002\u901a\u8fc7\u8f6e\u8be2 data_chain \u68c0\u67e5\u6761\u4ef6\u3002\n"
             "\n"
             "- waitfor: Python \u8868\u8fbe\u5f0f\uff0c\u4e3a True \u65f6\u7ed3\u675f\u7b49\u5f85\n"
             "- identity: 目标元素的定位器值\n"
             "- identity_key: 从 data_chain 获取定位器值的键，被设置时优先于 identity\n"
             "- timeout: \u6700\u5927\u7b49\u5f85\u79d2\u6570\uff08\u9ed8\u8ba4: 60\uff09\n"
             "- wait: 找到元素后额外等待秒数（默认: 1）\n"
        ),
    },

    "desc_WAIT_SECONDS": {
        "zh": (
            "暂停执行指定的秒数。\n"
            "\n"
            "- wait_seconds: 等待秒数（支持表达式，默认: 1）"
        ),
    },

    "desc_WRITE_TO_EXCEL": {
        "zh": (
            
             "\u5c06\u4e8c\u7ef4\u6570\u7ec4\u6570\u636e\u5199\u5165 Excel \u6587\u4ef6\u3002\n"
             "\n"
             "- file_path: Excel \u6587\u4ef6\u8f93\u51fa\u8def\u5f84\uff08\u652f\u6301\u8868\u8fbe\u5f0f\uff09\n"
             "- value_key: data_chain 中指向表单数据字典 [str:list] 或普通列表的键（支持表达式，默认: \"sheetname2list\"）\n"
             "- data_key: data_chain \u4e2d\u4e8c\u7ef4\u6570\u7ec4\u6570\u636e\u7684\u952e\n"
        ),
    },

    "desc_WRITE_TO_FILE": {
        "zh": (
            
             "\u5c06\u6587\u672c\u5185\u5bb9\u5199\u5165\u6587\u4ef6\u3002\n"
             "\n"
             "- file_path: \u76ee\u6807\u6587\u4ef6\u8def\u5f84\uff08\u652f\u6301\u8868\u8fbe\u5f0f\uff09\n"
             "- content: data_chain \u4e2d\u5185\u5bb9\u7684\u952e\uff08\u4f18\u5148\u4e8e content\uff09\n"
             "- data_key: 在 data_chain 中存储写入文件路径的键名；若为空，则不存储数据（支持表达式，默认: \"\"）\n"
        ),
    },

    "desc_ZIP": {
        "zh": (
            
             "\u5c06\u6587\u4ef6\u6216\u6587\u4ef6\u5939\u538b\u7f29\u4e3a zip \u6587\u4ef6\u3002\n"
             "\n"
             "- source_path: \u8981\u538b\u7f29\u7684\u6e90\u6587\u4ef6\u5939\u8def\u5f84\uff08\u652f\u6301\u8868\u8fbe\u5f0f\uff09\n"
             "- source_list: data_chain \u4e2d\u6587\u4ef6\u8def\u5f84\u5217\u8868\u7684\u952e\uff08\u66ff\u4ee3 source_path\uff09\n"
             "- zip_name: \u8f93\u51fa zip \u6587\u4ef6\u540d\uff08\u652f\u6301\u8868\u8fbe\u5f0f\uff09\n"
             "- path_in_zip: zip \u5185\u90e8\u7684\u8def\u5f84\u524d\u7f00\uff08\u53ef\u9009\uff09\n"
             "- path_to_replace: \u4ece\u6587\u4ef6\u8def\u5f84\u4e2d\u79fb\u9664\u7684\u524d\u7f00\uff08\u53ef\u9009\uff09\n"
             "- target_path: \u8f93\u51fa zip \u6587\u4ef6\u7684\u76ee\u6807\u76ee\u5f55\uff08\u652f\u6301\u8868\u8fbe\u5f0f\uff09\n"
             "- data_key: 在 data_chain 中存储结果 zip 文件路径的键（支持表达式，默认: \"\"）\n"
        ),
    },


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

    "desc_CHECK_GLOBAL_CACHE": {
        "zh": (
            "检查全局缓存中是否存在指定 key 的值（进程内内存缓存，跨 execution 共享）。\n"
            "缓存命中时，将缓存值绑定到 data_chain，并可选择控制执行流程。\n"
            "缓存未命中时不做任何操作，继续执行下一个 task。\n"
            "\n"
            "- cache_key: 要查找的缓存键（支持表达式，必填）\n"
            "- data_key: 命中时将缓存值绑定到 data_chain 的 key（必填）\n"
            "- on_hit: 命中时的动作 — \"end_execution\" / \"goto_task\" / \"continue\"（默认: \"end_execution\"）\n"
            "- target_task: on_hit=\"goto_task\" 时跳转的目标 task 序号，1-based（支持表达式）"
        ),
    },

    "desc_POPULATE_GLOBAL_CACHE": {
        "zh": (
            "将 data_chain 中的值存入全局缓存（进程内内存缓存，跨 execution 共享）。\n"
            "缓存值在进程生命周期内有效，或在 TTL 过期后失效。\n"
            "\n"
            "- cache_key: 存储的缓存键（支持表达式，必填）\n"
            "- value_key: 要缓存的 data_chain key（支持表达式，必填）\n"
            "- ttl: 过期时间（秒），留空则永不过期（支持表达式）"
        ),
    },

}
