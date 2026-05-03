import json
import logging

from core.processor import Processor
from core.processors.sub.llm.BaseLLMClient import BaseLLMClient, LLMResponse
from core.processors.sub.llm.McpClient import McpClient, McpTool, McpToolResult
from core.processors.sub.llm.llm_helpers import (
    build_tools_message_from_mcp,
    parse_tool_call_from_response,
    read_json_from_markdown,
    remove_think_tags,
    show_notification,
)


class AI_LLM_QANDA_MCPProcessor(Processor):
    TPL: str = '{"llm_data_key":"llm_client", "prompt":"", "mcp_server_url":"http://localhost:8866/mcp", "mcp_auth_token":"", "model":"", "temperature":"1.0", "system_prompt":"", "resp_content_key":"", "convert_resp_2_json":"no", "show_in_popup":"yes", "show_thinking":"no"}'

    DESC: str = '''
Ask a unified LLM a question with MCP tool-calling support. Depends on AI_LLM_SETUP to initialize the client first.

Connects to any standard MCP server via the official MCP SDK (Streamable HTTP transport).
Fetches available tools, lets the LLM decide whether to call one, executes it via MCP protocol,
and feeds the result back for a refined answer.

Works with all supported providers: deepseek, zhipu, qianfan, minimax, anthropic, doubao, moonshot, gemini, ollama, openai_compatible.

- llm_data_key: key in data_chain where the LLM client instance is stored (default: "llm_client")
- prompt: question to ask the LLM (supports expression)
- mcp_server_url: MCP server endpoint URL, must support Streamable HTTP transport (default: "http://localhost:8866/mcp")
- mcp_auth_token: Bearer token for MCP server authentication; if empty, no auth header is sent (supports expression, default: "")
- model: model name; if empty, uses the model configured during SETUP (supports expression, default: "")
- temperature: sampling temperature (default: "1.0")
- system_prompt: additional system context prepended before tools message (supports expression, default: "")
- resp_content_key: key in data_chain to store the final response content (supports expression, default: "")
- convert_resp_2_json: "yes" to parse JSON from markdown code block in response (default: "no")
- show_in_popup: "yes" to display Q&A in popup dialog (default: "yes")
- show_thinking: "yes" to keep <think> tags in displayed output; "no" to strip them (default: "no")
'''

    def get_category(self) -> str:
        return super().CATE_AI_LLM

    def process(self):
        llm_data_key = self.expression2str(self.get_param('llm_data_key'))
        client: BaseLLMClient = self.get_data(llm_data_key)

        if client is None:
            msg = f'LLM client not found at key "{llm_data_key}". Please add AI_LLM_SETUP as a previous task.'
            show_notification("AI_LLM_QANDA_MCP", msg)
            return

        prompt = self.expression2str(self.get_param('prompt'))
        mcp_server_url = self._resolve_mcp_url()
        mcp_auth_token = self.explain_param_or_default('mcp_auth_token', '')
        model = self.explain_param_or_default('model', '')
        temperature = self.explain_param_as_float('temperature', 1.0)
        system_prompt = self.explain_param_or_default('system_prompt', '')
        resp_content_key = self.explain_param_or_default('resp_content_key', '')
        convert_resp_2_json = self.get_param_bool_if_equal('convert_resp_2_json', 'yes')
        show_in_popup = self.get_param_bool_if_equal('show_in_popup', 'yes')
        show_thinking = self.get_param_bool_if_equal('show_thinking', 'yes')

        try:
            headers = {}
            if mcp_auth_token:
                headers['Authorization'] = f'Bearer {mcp_auth_token}'
            mcp_client = McpClient(mcp_server_url, headers=headers)
            available_tools = mcp_client.list_tools()
            logging.info('MCP tools discovered: %s', [t.name for t in available_tools])

            tools_message = build_tools_message_from_mcp(available_tools)
            messages = []
            if system_prompt:
                tools_message = f"{system_prompt}\n\n{tools_message}"
            messages.append({"role": "system", "content": tools_message})
            messages.append({"role": "user", "content": prompt})

            response: LLMResponse = client.chat(
                messages=messages, model=model, temperature=temperature,
            )
            answer = response.content or response.reasoning_content or ''
            logging.debug(f'Initial LLM answer: {answer}')

            tool_names = {t.name for t in available_tools}
            tool_call = parse_tool_call_from_response(answer, tool_names)
            final_answer = answer

            if tool_call:
                logging.info('Executing MCP tool: %s with args: %s',
                             tool_call['tool'], tool_call['arguments'])
                tool_result: McpToolResult = mcp_client.call_tool(
                    tool_call['tool'], tool_call['arguments']
                )

                if tool_result.structured_content:
                    result_text = json.dumps(tool_result.structured_content, ensure_ascii=False)
                else:
                    result_text = tool_result.content_text

                if tool_result.is_error:
                    result_text = f"[Tool Error] {result_text}"

                logging.debug(f'Tool result: {result_text}')

                follow_up_messages = [
                    {"role": "user", "content": prompt},
                    {"role": "system",
                     "content": f"Please answer strictly based on this information: {result_text}. "
                                "Prefer to use the language of the original question."},
                ]
                final_response: LLMResponse = client.chat(
                    messages=follow_up_messages, model=model, temperature=temperature,
                )
                final_answer = final_response.content or final_response.reasoning_content or ''

            content = read_json_from_markdown(final_answer) if convert_resp_2_json else final_answer
            display_text = final_answer if show_thinking else remove_think_tags(final_answer)
            alert_message = f"Q:\n{prompt}\n\nA:\n{display_text}"
            logging.info('LLM MCP response received (provider=%s, model=%s)', client.provider_name, model)

            if show_in_popup:
                show_notification(f"AI_LLM_QANDA_MCP ({client.provider_name})", alert_message)

            if resp_content_key:
                self.populate_data(resp_content_key, content)

        except Exception as e:
            error_msg = f'Error in MCP Q&A ({client.provider_name}): {e}'
            logging.error(error_msg)
            show_notification("AI_LLM_QANDA_MCP Error", error_msg)

    def _resolve_mcp_url(self) -> str:
        if self.has_param('mcp_server_url'):
            url = self.expression2str(self.get_param('mcp_server_url'))
        elif self.has_param('petp_mcp_url'):
            url = self.expression2str(self.get_param('petp_mcp_url'))
            logging.warning('Parameter "petp_mcp_url" is deprecated. Use "mcp_server_url" instead.')
        else:
            url = 'http://localhost:8866/mcp'

        if not url.rstrip('/').endswith('/mcp'):
            url = url.rstrip('/') + '/mcp'
        return url
