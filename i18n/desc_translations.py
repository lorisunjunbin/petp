# -*- coding: UTF-8 -*-
# Processor description translations (zh only).
# EN descriptions are the authoritative source in each processor's DESC attribute.
# Key format: desc_<TYPE>  →  {"zh": "..."}.

DESC_TRANSLATIONS: dict[str, dict[str, str]] = {
    # === Processor descriptions (i18n) ===

    "desc_AI_LLM_DEEPSEEK_QANDA": {
        "zh": (
            
             "\u5411 DeepSeek LLM \u63d0\u95ee\u5e76\u83b7\u53d6\u56de\u7b54\u3002\u4f9d\u8d56 AI_LLM_DEEPSEEK_SETUP \u5148\u521d\u59cb\u5316 LLM \u5b9e\u4f8b\u3002\n"
             "\n"
             "- llm_data_key: data_chain \u4e2d\u5b58\u50a8 LLM \u5ba2\u6237\u7aef\u5b9e\u4f8b\u7684\u952e\uff08\u9ed8\u8ba4: \"llmdeepseek\"\uff09\n"
             "- prompt: \u53d1\u9001\u7ed9 LLM \u7684\u63d0\u793a/\u95ee\u9898\uff08\u652f\u6301\u8868\u8fbe\u5f0f\uff09\n"
             "- model: DeepSeek 模型名称（默认: \"deepseek-chat\"）\n"
             "- temperature: 采样温度，编程/数学: 0.0，数据分析: 1.0，对话: 1.3，创意写作: 1.5（默认: \"1.0\"）\n"
             "- resp_content_key: data_chain 中存储响应内容的键\n"
             "- convert_resp_2_json: \"yes\" 解析 markdown 代码块中的 JSON 响应（默认: \"yes\"）\n"
             "- show_in_popup: \"yes\" 在弹窗中显示问答结果（默认: \"yes\"）\n"
        ),
    },

    "desc_AI_LLM_DEEPSEEK_QANDA_MCP": {
        "zh": (
            
             "\u5411 DeepSeek LLM \u63d0\u95ee\u5e76\u652f\u6301 MCP \u5de5\u5177\u8c03\u7528\u3002\u4f9d\u8d56 AI_LLM_DEEPSEEK_SETUP \u5148\u521d\u59cb\u5316 LLM \u5b9e\u4f8b\u3002\n"
             "\u8fd0\u884c\u53e6\u4e00\u4e2a PETP \u4f5c\u4e3a MCP \u670d\u52a1\u5668\u3002\u5982\u679c LLM \u51b3\u5b9a\u4f7f\u7528\u5de5\u5177\uff0c\u4f1a\u8c03\u7528 MCP \u7aef\u70b9\u5e76\u5c06\u7ed3\u679c\u53cd\u9988\u3002\n"
             "\n"
             "- llm_data_key: data_chain \u4e2d\u5b58\u50a8 LLM \u5ba2\u6237\u7aef\u5b9e\u4f8b\u7684\u952e\uff08\u9ed8\u8ba4: \"llmdeepseek\"\uff09\n"
             "- prompt: \u53d1\u9001\u7ed9 LLM \u7684\u63d0\u793a/\u95ee\u9898\uff08\u652f\u6301\u8868\u8fbe\u5f0f\uff09\n"
             "- petp_mcp_url: PETP MCP 服务器的基础 URL（默认: \"http://localhost:8888\"）\n"
             "- model: DeepSeek 模型名称（默认: \"deepseek-chat\"）\n"
             "- temperature: 采样温度，编程/数学: 0.0，数据分析: 1.0，对话: 1.3，创意写作: 1.5（默认: \"1.0\"）\n"
             "- resp_content_key: data_chain 中存储最终响应内容的键\n"
             "- convert_resp_2_json: \"yes\" 解析 markdown 代码块中的 JSON 响应（默认: \"yes\"）\n"
             "- show_in_popup: \"yes\" 在弹窗中显示问答结果（默认: \"yes\"）\n"
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
            "- llm_data_key: data_chain 中存储客户端的键（默认: \"llmdeepseek\"）"
        ),
    },

    "desc_AI_LLM_GEMINI_QANDA": {
        "zh": (
            
             "\u4f7f\u7528\u5df2\u914d\u7f6e\u7684 Gemini \u5b9e\u4f8b\u5411 Google Gemini LLM \u63d0\u95ee\uff08\u7531 AI_LLM_GEMINI_SETUP \u521d\u59cb\u5316\uff09\u3002\n"
             "\u63d0\u793a\u8bcd\u53d1\u9001\u5230\u6a21\u578b\uff0c\u54cd\u5e94\u53ef\u9009\u62e9\u89e3\u6790\u4e3a JSON \u548c/\u6216\u5728\u5f39\u7a97\u4e2d\u663e\u793a\u3002\n"
             "\n"
             "- llm_data_key: data_chain \u4e2d\u5b58\u50a8 LLM \u5b9e\u4f8b\u7684\u952e\uff08\u9ed8\u8ba4: \"llmgemini\"\uff09\n"
             "- prompt: \u53d1\u9001\u7ed9 LLM \u7684\u63d0\u793a/\u95ee\u9898\uff08\u652f\u6301\u8868\u8fbe\u5f0f\uff09\n"
             "- resp_content_key: data_chain 中存储响应内容的键；若为空则不存储（支持表达式，默认: \"\"）\n"
             "- convert_resp_2_json: 若为 \"yes\"，则从 markdown 响应中提取 JSON（支持表达式，默认: \"yes\"）\n"
             "- show_in_popup: 若为 \"yes\"，在弹窗中显示问答结果（支持表达式，默认: \"yes\"）\n"
        ),
    },

    "desc_AI_LLM_GEMINI_QANDA_MCP": {
        "zh": (
            
             "\u5411 Google Gemini LLM \u63d0\u95ee\u5e76\u652f\u6301\u901a\u8fc7 PETP MCP \u670d\u52a1\u5668\u8fdb\u884c\u5de5\u5177\u8c03\u7528\u3002\n"
             "\u4f9d\u8d56 AI_LLM_GEMINI_SETUP \u5df2\u521d\u59cb\u5316 LLM \u5b9e\u4f8b\u3002\u4ece MCP \u670d\u52a1\u5668\u83b7\u53d6\u53ef\u7528\u5de5\u5177\uff0c\u5982\u679c LLM \u51b3\u5b9a\u4f7f\u7528\u5de5\u5177\uff0c\n"
             "\u901a\u8fc7 MCP \u7aef\u70b9\u6267\u884c\u5e76\u8fd4\u56de\u4f18\u5316\u540e\u7684\u7b54\u6848\u3002\n"
             "\n"
             "- llm_data_key: data_chain \u4e2d\u5b58\u50a8 LLM \u5b9e\u4f8b\u7684\u952e\uff08\u9ed8\u8ba4: \"llmgemini\"\uff09\n"
             "- prompt: \u53d1\u9001\u7ed9 LLM \u7684\u63d0\u793a/\u95ee\u9898\uff08\u652f\u6301\u8868\u8fbe\u5f0f\uff09\n"
             "- petp_mcp_url: 用于工具发现和执行的 PETP MCP 服务器基础 URL（默认: \"http://localhost:8888\"）\n"
             "- resp_content_key: 存储最终响应内容的 data_chain 键（默认: \"gemini_response\"）\n"
             "- convert_resp_2_json: 若为 \"yes\"，尝试将最终响应作为 JSON 从 markdown 代码块中解析（默认: \"yes\"）\n"
             "- show_in_popup: 是否在弹窗中显示问答结果，\"yes\" 或 \"no\"（默认: \"yes\"）\n"
        ),
    },

    "desc_AI_LLM_GEMINI_SETUP": {
        "zh": (
            
             "\u521d\u59cb\u5316\u5e76\u914d\u7f6e Google Gemini LLM \u5b9e\u4f8b\uff0c\u8bbe\u7f6e\u6307\u5b9a\u7684\u6a21\u578b\u3001\u6e29\u5ea6\u548c top_p \u53c2\u6570\uff0c\n"
             "\u7136\u540e\u5b58\u50a8\u5728 data_chain \u4e2d\u4f9b\u540e\u7eed\u5904\u7406\u5668\u4f7f\u7528\u3002\u9700\u8981\u8bbe\u7f6e GOOGLE_API_KEY \u73af\u5883\u53d8\u91cf\u3002\n"
             "\n"
             "- api_key_env: \u5305\u542b API \u5bc6\u94a5\u7684\u73af\u5883\u53d8\u91cf\u540d\uff08\u9ed8\u8ba4: \"GOOGLE_API_KEY\"\uff09\n"
             "- model: Gemini \u6a21\u578b\u540d\u79f0\uff08\u9ed8\u8ba4: \"gemini-2.0-flash\"\uff09\n"
             "- llm_data_key: data_chain \u4e2d\u5b58\u50a8\u5ba2\u6237\u7aef\u7684\u952e\uff08\u9ed8\u8ba4: \"llmgemini\"\uff09\n"
             "- top_p: Top-p \u91c7\u6837\u53c2\u6570\uff08\u9ed8\u8ba4: 0.95\uff09\n"
             "- temperature: \u91c7\u6837\u6e29\u5ea6\uff0c0-2\uff08\u9ed8\u8ba4: 1.0\uff09\n"
        ),
    },

    "desc_AI_LLM_OLLAMA_QANDA": {
        "zh": (
            
             "\u901a\u8fc7\u672c\u5730\u8fd0\u884c\u7684 Ollama \u5b9e\u4f8b\u5411 LLM \u63d0\u95ee\uff0c\u83b7\u53d6\u56de\u7b54\uff0c\u6309\u9700\u89e3\u6790\u4e3a JSON\uff0c\n"
             "\u5e76\u53ef\u9009\u62e9\u5728\u5f39\u7a97\u4e2d\u663e\u793a\u3002\u9700\u8981 Ollama \u5728\u672c\u5730\u8fd0\u884c\u3002\n"
             "\n"
             "- model: Ollama \u6a21\u578b\u540d\u79f0\uff08\u9ed8\u8ba4: \"deepseek-r1:1.5b\"\uff09\n"
             "- prompt: \u53d1\u9001\u7ed9 LLM \u7684\u63d0\u793a/\u95ee\u9898\uff08\u652f\u6301\u8868\u8fbe\u5f0f\uff09\n"
             "- role: 消息的聊天角色，通常为 \"user\" 或 \"system\"（默认: \"user\"）\n"
             "- show_in_popup: 是否在弹窗中显示问答结果，\"yes\" 或 \"no\"（默认: \"yes\"）\n"
             "- resp_content_key: 存储原始 LLM 响应的 data_chain 键（默认: \"ollama_resp\"）\n"
        ),
    },

    "desc_AI_LLM_OLLAMA_QANDA_MCP": {
        "zh": (
            
             "\u901a\u8fc7 PETP MCP \u670d\u52a1\u5668\u8c03\u7528\u672c\u5730 Ollama LLM \u5e76\u652f\u6301\u5de5\u5177\u8c03\u7528\u3002\n"
             "\u4ece MCP \u670d\u52a1\u5668\u83b7\u53d6\u53ef\u7528\u5de5\u5177\uff0c\u5411 LLM \u63d0\u95ee\uff0c\u5982\u679c LLM \u51b3\u5b9a\u4f7f\u7528\u5de5\u5177\uff0c\n"
             "\u901a\u8fc7 MCP \u670d\u52a1\u5668\u6267\u884c\u5e76\u8fd4\u56de\u4f18\u5316\u540e\u7684\u7b54\u6848\u3002\n"
             "\n"
             "- model: Ollama \u6a21\u578b\u540d\u79f0\uff08\u9ed8\u8ba4: \"qwen2.5:7b\"\uff09\n"
             "- show_thinking: 是否在输出中显示思考/推理标签，\"yes\" 或 \"no\"（默认: \"no\"）\n"
             "- prompt: \u53d1\u9001\u7ed9 LLM \u7684\u63d0\u793a/\u95ee\u9898\uff08\u652f\u6301\u8868\u8fbe\u5f0f\uff09\n"
             "- petp_mcp_url: 用于工具发现和执行的 PETP MCP 服务器基础 URL（默认: \"http://localhost:8888\"）\n"
             "- resp_content_key: 存储最终响应内容的 data_chain 键（默认: \"\"）\n"
             "- convert_resp_2_json: 若为 \"yes\"，尝试将最终响应作为 JSON 从 markdown 代码块中解析（默认: \"yes\"）\n"
             "- show_in_popup: 是否在弹窗中显示问答结果，\"yes\" 或 \"no\"（默认: \"yes\"）\n"
        ),
    },

    "desc_AI_LLM_ZHIPU_QANDA": {
        "zh": (
            
             "\u5411\u667a\u8c31 AI (GLM) \u5927\u6a21\u578b\u63d0\u95ee\uff0c\u83b7\u53d6\u56de\u7b54\uff0c\u53ef\u9009\u4ece markdown \u4ee3\u7801\u5757\u4e2d\u89e3\u6790 JSON\uff0c\n"
             "\u5e76\u53ef\u9009\u5728\u5f39\u7a97\u4e2d\u663e\u793a\u95ee\u7b54\u5185\u5bb9\u3002\u4f9d\u8d56 AI_LLM_ZHIPU_SETUP \u5df2\u521d\u59cb\u5316\u5ba2\u6237\u7aef\u5b9e\u4f8b\u3002\n"
             "\n"
             "- llm_data_key: data_chain \u4e2d\u5b58\u50a8 LLM \u5b9e\u4f8b\u7684\u952e\uff08\u9ed8\u8ba4: \"llmzhipu\"\uff09\n"
             "- prompt: \u53d1\u9001\u7ed9 LLM \u7684\u63d0\u793a/\u95ee\u9898\uff08\u652f\u6301\u8868\u8fbe\u5f0f\uff09\n"
             "- model: \u6a21\u578b\u540d\u79f0\uff08\u9ed8\u8ba4: \"glm-4-flash\"\uff09\n"
             "- temperature: 作为浮点字符串的采样温度，值越高输出越具创意（默认: \"1.0\"）\n"
             "- resp_content_key: 存储最终响应内容的 data_chain 键（默认: \"\"）\n"
             "- convert_resp_2_json: 若为 \"yes\"，尝试将响应作为 JSON 从 markdown 代码块中解析（默认: \"yes\"）\n"
             "- show_in_popup: 是否在弹窗中显示问答结果，\"yes\" 或 \"no\"（默认: \"yes\"）\n"
        ),
    },

    "desc_AI_LLM_ZHIPU_QANDA_MCP": {
        "zh": (
            
             "\u901a\u8fc7 PETP MCP \u670d\u52a1\u5668\u8c03\u7528\u667a\u8c31 AI (GLM) LLM \u5e76\u652f\u6301\u5de5\u5177\u8c03\u7528\u3002\n"
             "\u4f9d\u8d56 AI_LLM_ZHIPU_SETUP \u5df2\u521d\u59cb\u5316\u5ba2\u6237\u7aef\u3002\u4ece MCP \u670d\u52a1\u5668\u83b7\u53d6\u53ef\u7528\u5de5\u5177\uff0c\u5411 LLM \u63d0\u95ee\uff0c\n"
             "\u5982\u679c LLM \u51b3\u5b9a\u4f7f\u7528\u5de5\u5177\uff0c\u901a\u8fc7 MCP \u7aef\u70b9\u6267\u884c\u5e76\u8fd4\u56de\u4f18\u5316\u540e\u7684\u7b54\u6848\u3002\n"
             "\n"
             "- llm_data_key: data_chain \u4e2d\u5b58\u50a8 LLM \u5b9e\u4f8b\u7684\u952e\uff08\u9ed8\u8ba4: \"llmzhipu\"\uff09\n"
             "- prompt: \u53d1\u9001\u7ed9 LLM \u7684\u63d0\u793a/\u95ee\u9898\uff08\u652f\u6301\u8868\u8fbe\u5f0f\uff09\n"
             "- model: \u6a21\u578b\u540d\u79f0\uff08\u9ed8\u8ba4: \"glm-4-flash\"\uff09\n"
             "- temperature: 作为浮点字符串的采样温度，值越高输出越具创意（默认: \"1.0\"）\n"
             "- show_thinking: 是否在输出中显示思考/推理标签，\"yes\" 或 \"no\"（默认: \"no\"）\n"
             "- petp_mcp_url: 用于工具发现和执行的 PETP MCP 服务器基础 URL（默认: \"http://localhost:8888\"）\n"
             "- resp_content_key: 存储最终响应内容的 data_chain 键（默认: \"\"）\n"
             "- convert_resp_2_json: 若为 \"yes\"，尝试将最终响应作为 JSON 从 markdown 代码块中解析（默认: \"yes\"）\n"
             "- show_in_popup: 是否在弹窗中显示问答结果，\"yes\" 或 \"no\"（默认: \"yes\"）\n"
        ),
    },

    "desc_AI_LLM_ZHIPU_SETUP": {
        "zh": (
            
             "\u521d\u59cb\u5316\u5e76\u914d\u7f6e\u667a\u8c31 AI LLM \u5ba2\u6237\u7aef\u5b9e\u4f8b\uff0c\u4ece\u73af\u5883\u53d8\u91cf\uff08api_key_env \u6307\u5b9a\uff09\u6216 api_key \u53c2\u6570\n"
             "\u76f4\u63a5\u8bfb\u53d6 API \u5bc6\u94a5\u3002\u5ba2\u6237\u7aef\u5b58\u50a8\u5728 data_chain \u4e2d\u4f9b\u540e\u7eed\u5904\u7406\u5668\u4f7f\u7528\u3002\u5982\u679c\u5b9e\u4f8b\u5df2\u5b58\u5728\u5219\u8df3\u8fc7\u8bbe\u7f6e\u3002\n"
             "\n"
             "- api_key_env: \u5305\u542b API \u5bc6\u94a5\u7684\u73af\u5883\u53d8\u91cf\u540d\uff08\u9ed8\u8ba4: \"ZHIPU_API_KEY\"\uff09\n"
             "- api_key: \u76f4\u63a5\u63d0\u4f9b\u7684 API \u5bc6\u94a5\uff08\u4f18\u5148\u4e8e api_key_env\uff09\n"
             "- base_url: 智谱 AI API 端点的基础 URL（默认: \"https://open.bigmodel.cn/api/paas/v4/\"）\n"
             "- llm_data_key: data_chain \u4e2d\u5b58\u50a8\u5ba2\u6237\u7aef\u7684\u952e\uff08\u9ed8\u8ba4: \"llmzhipu\"\uff09\n"
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
            
             "\u901a\u8fc7 subprocess.check_output \u8fd0\u884c\u7cfb\u7edf\u547d\u4ee4\uff0c\u5c06\u8f93\u51fa\u4fdd\u5b58\u5230 data_chain \u7684 data_key \u4e2d\u3002\n"
             "\n"
             "- cmdstr: \u8981\u6267\u884c\u7684\u547d\u4ee4\u5b57\u7b26\u4e32\uff08\u652f\u6301\u8868\u8fbe\u5f0f\uff09\n"
             "- cmddir: \u547d\u4ee4\u5de5\u4f5c\u76ee\u5f55\uff08\u652f\u6301\u8868\u8fbe\u5f0f\uff0c\u53ef\u9009\uff09\n"
             "- data_key: data_chain \u4e2d\u5b58\u50a8\u547d\u4ee4\u8f93\u51fa\u7684\u952e\n"
             "- timeout: \u547d\u4ee4\u8d85\u65f6\u79d2\u6570\uff08\u9ed8\u8ba4: 60\uff09\n"
             "- shell: 设为 \"yes\" 以启用 shell 模式（默认: disabled）\n"
             "- encoding: \u8f93\u51fa\u7f16\u7801\uff08\u9ed8\u8ba4: \"utf-8\"\uff09\n"
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
            "- frame_ids: frame 标识符列表（索引、名称或 id），如 [\"frame1\", \"frame2\"]"
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
             "- chrome_name: data_chain \u4e2d Chrome \u9a71\u52a8\u7684\u952e\uff08\u9ed8\u8ba4: \"chrome\"\uff09\n"
        ),
    },

    "desc_SEND_EMAIL": {
        "zh": (
            "通过 SMTP 发送电子邮件。支持 HTML 正文和附件。\n"
            "\n"
            "- smtp: SMTP 服务器地址（支持表达式）\n"
            "- port: SMTP 服务器端口（默认: 465）\n"
            "- name: SMTP 用户名/发件人（支持表达式）\n"
            "- pwd: SMTP 密码（支持表达式和加密值）\n"
            "- to: 收件人地址，多个用逗号分隔（支持表达式）\n"
            "- subject: 邮件主题（支持表达式）\n"
            "- content: 邮件正文内容（支持表达式）\n"
            "- attachment: 附件文件路径，多个用逗号分隔（支持表达式，可选）"
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

}
