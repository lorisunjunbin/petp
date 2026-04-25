import json
import logging
import re
from typing import Any, Dict, List, Optional

import requests
try:
    import wx
except ImportError:
    wx = None

from core.processor import Processor

"""
REQUIREMENTS:

pip install google-genai
pip install requests

"""


class AI_LLM_GEMINI_QANDA_MCPProcessor(Processor):
    TPL: str = '{"llm_data_key":"llmgemini", "prompt":"prompt", "petp_mcp_url":"http://localhost:8888", "resp_content_key":"gemini_response","convert_resp_2_json":"yes","show_in_popup":"yes"}'

    DESC: str = f'''
        Ask Google Gemini LLM a question with tool-use capabilities via the PETP MCP server. Depends on AI_LLM_GEMINI_SETUPProcessor
        to have previously initialized the LLM instance. Fetches available tools from the MCP server, and if the LLM decides
        to use a tool, executes it via the MCP endpoint and returns the refined answer.

        - llm_data_key: Key to retrieve the pre-configured Gemini LLM instance from the data chain (default: "llmgemini")
        - prompt: The question or prompt text to send to the LLM (supports expression, default: "prompt")
        - petp_mcp_url: The base URL of the PETP MCP server for tool discovery and execution (default: "http://localhost:8888")
        - resp_content_key: The data chain key under which the final response content will be stored (default: "gemini_response")
        - convert_resp_2_json: If "yes", attempts to parse the final response as JSON from a markdown code block (default: "yes")
        - show_in_popup: Whether to display the Q&A result in a popup dialog, "yes" or "no" (default: "yes")

        {TPL}
    '''

    def get_category(self) -> str:
        return super().CATE_AI_LLM

    def process(self):
        llm_data_key = self.get_param('llm_data_key')
        existed_llm = self.get_data(llm_data_key)

        if existed_llm is None:
            msg = 'LLM Gemini is not setup yet, please add task AI_LLM_GEMINI_SETUPProcessor as a previous Task.'
            if wx is not None:
                wx.MessageDialog(None, msg, "AI_LLM_GEMINI_Q&A Error").ShowModal()
            else:
                logging.info(f"[Notification] AI_LLM_GEMINI_Q&A Error: {msg}")
            return

        prompt = self.expression2str(self.get_param('prompt'))
        petp_mcp_url = self.get_param('petp_mcp_url')
        resp_content_key = self.get_param('resp_content_key')
        convert_resp_2_json = self.get_param('convert_resp_2_json') == 'yes'
        show_in_popup = self.get_param('show_in_popup') == 'yes'

        available_tools = self.get_available_tools(petp_mcp_url) or []
        available_tools_prompt = self.build_tools_message(available_tools)

        logging.debug(f'Initial prompt to Gemini: {prompt}')
        logging.debug(f'System message with tools: {available_tools_prompt}')

        try:
            initial_prompt = f"{available_tools_prompt}\n\nUser question:\n{prompt}"
            logging.info('Calling Gemini LLM with combined system+user prompt')
            response_obj = existed_llm.invoke(initial_prompt)
            answer = self._extract_content(response_obj)

            tool_call_result = self.process_llm_response(answer, petp_mcp_url, available_tools)
            final_answer = answer

            if tool_call_result != answer:
                follow_up_prompt = (
                    f"Original question:\n{prompt}\n\n"
                    f"Tool result:\n{tool_call_result}\n\n"
                    "Please answer strictly based on the tool result. "
                    "Prefer to use the language of the original question."
                )
                logging.info('Calling Gemini LLM after tool call')
                final_response_obj = existed_llm.invoke(follow_up_prompt)
                final_answer = self._extract_content(final_response_obj)

            content = self.read_json_from_markdown(final_answer) if convert_resp_2_json else final_answer
            content_text = content if isinstance(content, str) else json.dumps(content, ensure_ascii=False)
            alert_message = f"Q:\n{prompt}\n\nA:\n{content_text}"
            logging.info('Gemini MCP response received')
            logging.debug('Final Q and A:\n%s', alert_message)

            if show_in_popup and wx is not None:
                dlg = wx.MessageDialog(None, alert_message, "AI LLM GEMINI Q&A (MCP)")
                dlg.ShowModal()
                dlg.Destroy()
            else:
                logging.info(f"[Notification] AI LLM GEMINI Q&A (MCP): {alert_message}")

            self.populate_data(resp_content_key, content)

        except Exception as e:
            error_msg = f'Unexpected error: {str(e)}'
            logging.error(error_msg)
            if wx is not None:
                wx.MessageDialog(None, error_msg, "AI LLM GEMINI Q&A (MCP) Error").ShowModal()
            else:
                logging.info(f"[Notification] AI LLM GEMINI Q&A (MCP) Error: {error_msg}")

    def _extract_content(self, response_obj: Any) -> str:
        if hasattr(response_obj, 'content'):
            return response_obj.content
        if hasattr(response_obj, 'text'):
            return response_obj.text
        return str(response_obj)

    def read_json_from_markdown(self, markdown_content: str) -> Any:
        """Extract JSON from markdown code blocks."""
        try:
            json_match = re.search(r'```json\n([\s\S]*?)\n```', markdown_content)
            if json_match:
                json_str = json_match.group(1)
                return json.loads(json_str)
            logging.warning("No JSON found in the Response.")
            return markdown_content
        except json.JSONDecodeError:
            logging.warning("Failed to parse JSON.")
            return markdown_content

    def get_available_tools(self, petp_mcp_url: str) -> Optional[List[Dict[str, Any]]]:
        """Call the MCP server to list all available tools."""
        try:
            response = requests.get(f"{petp_mcp_url}/petp/tools")
            if response.status_code == 200:
                resp_json = response.json()
                logging.debug(f"Available tools response: {resp_json}")
                return resp_json['data']
            logging.error(f"Failed to list tools: {response.status_code}")
            return None
        except requests.RequestException as e:
            logging.error(f"Request failed: {str(e)}")
            return None

    def build_tools_message(self, available_tools: List[Dict[str, Any]]) -> str:
        """Build the system message with available tools description."""
        if not available_tools:
            return "You are a helpful assistant. No external tools are available at the moment."

        try:
            system_message = (
                "You are a helpful assistant with access to these tools:\n\n"
                f"{available_tools}\n"
                "Choose the appropriate tool based on the user's question. "
                "If no tool is needed, reply directly.\n\n"
                "IMPORTANT: When you need to use a tool, you must ONLY respond with "
                "the exact JSON markdown object format below, nothing else:\n"
                "```json\n{"
                '    "tool": "tool-name",\n'
                '    "arguments": {\n'
                '        "argument-name": "value"\n'
                "    }\n"
                "}\n```"
                "After receiving a tool's response:\n"
                "1. Transform the raw data into a natural, conversational response\n"
                "2. Keep responses concise but informative\n"
                "3. Focus on the most relevant information\n"
                "4. Use appropriate context from the user's question\n"
                "5. Make sure tool-name is identical\n"
                "6. Avoid simply repeating the raw data\n\n"
                "Please use only the tools that are explicitly defined above."
            )
            return system_message
        except Exception as e:
            logging.error(f"Failed to build tools message: {str(e)}")
            return "You are a helpful assistant. There was an issue preparing tool information."

    def process_llm_response(self, answer: str, petp_mcp_url: str, available_tools: List[Dict[str, Any]]) -> str:
        """Process the LLM response and execute tools if needed."""
        try:
            tool_call = self.read_json_from_markdown(answer)
            if isinstance(tool_call, dict) and "tool" in tool_call and "arguments" in tool_call:
                tool_name = tool_call['tool']
                tool_args = tool_call['arguments']

                logging.info(f"Executing tool: {tool_name}")
                logging.info(f"With arguments: {tool_args}")

                params = {"execution": tool_name, "fromHTTPService": True}
                for key, value in tool_args.items():
                    if isinstance(value, str):
                        params[key] = value
                    elif isinstance(value, list):
                        params[key] = ",".join(map(str, value))
                    else:
                        params[key] = value

                tool_names = {tool.get('name') for tool in available_tools if isinstance(tool, dict)}
                if tool_name in tool_names:
                    try:
                        payload = {"action": "execution", "params": params}
                        result = requests.post(
                            f"{petp_mcp_url}/petp/exec",
                            json=payload,
                            headers={"Content-Type": "application/json"},
                        )
                        logging.info(f"Tool request payload: {payload}")
                        result.raise_for_status()

                        try:
                            response_content = result.json()
                        except json.JSONDecodeError:
                            response_content = result.text

                        logging.info(f"Tool response: {response_content}")
                        return f"Tool execution result: {response_content}"
                    except requests.exceptions.RequestException as e:
                        error_msg = f"Error executing tool: {str(e)}"
                        logging.error(error_msg)
                        return f"Failed to execute tool: {error_msg}"
            return answer
        except json.JSONDecodeError:
            logging.error("JSON decode error in LLM response")
            return answer
        except Exception as e:
            logging.error(f"Error processing LLM response: {str(e)}")
            return answer
