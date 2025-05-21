import json
import logging
import re
from typing import Any, Dict, List, Optional, Union

import requests
import wx
import ollama

from core.processor import Processor

"""
Refer: https://github.com/ollama/ollama-python

1, install ollama:
> pip install ollama

2, pull the model you want to use, for example:
> ollama pull qwen3:latest
> ollama pull deepseek-r1:7b

3, run ollama:
> ollama run deepseek-r1:7b
"""


class AI_LLM_OLLAMA_QANDA_MCPProcessor(Processor):
    TPL: str = '{"model":"deepseek-r1:latest","show_thinking":"no", "prompt":"prompt","petp_mcp_url":"http://localhost:8888", "resp_content_key":"","convert_resp_2_json":"yes","show_in_popup":"yes"}'

    DESC: str = f'''
            This processor will call OLLAMA LLM locally, and then call the PETP MCP server to get the available tools.

            Run another PETP as mcp server, http endpoint: http://localhost:8888

            Ask ollama llm a question associated with available tools, if tool is available, call tool then give the response accordingly.

            {TPL}
        '''

    def get_category(self) -> str:
        return super().CATE_AI_LLM

    def process(self) -> None:
        """Process the LLM request with available tools and handle the response."""
        # Get parameters
        model = self.get_param('model')
        prompt = self.expression2str(self.get_param('prompt'))
        petp_mcp_url = self.get_param('petp_mcp_url')
        resp_content_key = self.get_data("resp_content_key")
        convert_resp_2_json = self.get_param("convert_resp_2_json") == 'yes'
        show_thinking = self.get_param("show_thinking") == 'yes'
        show_in_popup = self.get_param("show_in_popup") == 'yes'

        try:
            # Get available tools and build prompt
            available_tools = self.get_available_tools(petp_mcp_url)
            tools_prompt = self.build_tools_message(available_tools)

            # Prepare initial conversation
            messages = [
                {"role": "system", "content": tools_prompt},
                {"role": "user", "content": prompt},
            ]

            logging.info(f'Calling LLM with model: {model}')
            logging.debug(f'Prompt: {prompt}')

            # Initial LLM call
            response = ollama.chat(model=model, messages=messages, stream=False)
            answer = response.message.content

            # Process response for tool calls
            new_answer = self.process_llm_response(answer, petp_mcp_url, available_tools)
            final_answer = answer

            # If tool was used, get a refined answer
            if new_answer != answer:
                messages = [
                    {"role": "user", "content": prompt},
                    {"role": "system", "content": f'Prefer to use Chinese. Please answer strictly based on this information: {new_answer}'}
                ]

                logging.info('Calling LLM after tool execution')
                final_response = ollama.chat(model=model, messages=messages, stream=False)
                final_answer = final_response.message.content

            # Process the result
            result_content = self.read_json_from_markdown(final_answer) if convert_resp_2_json else final_answer
            self.populate_data(resp_content_key, result_content)

            # Display results
            display_answer = final_answer if show_thinking else self.remove_think_tags(final_answer)
            alert_message = f"Q:\n{prompt}\n\nA:\n{display_answer}"
            logging.info(f'Q and A:\n{alert_message}')

            if show_in_popup:
                wx.MessageDialog(None, alert_message, f"AI_LLM_OLLAMA_QANDA_MCP via: {model}").ShowModal()

        except Exception as e:
            error_msg = f'Error processing request: {str(e)}'
            logging.error(error_msg)
            wx.MessageDialog(None, error_msg, f"AI_LLM_OLLAMA_QANDA_MCP via: {model}").ShowModal()

    def remove_think_tags(self, text: str) -> str:
        """Remove content within <think></think> tags from text."""
        return re.sub(r'<think>[\s\S]*?</think>', '', text).strip()

    def read_json_from_markdown(self, markdown_content: str) -> Optional[Dict[str, Any]]:
        """Extract JSON from markdown code blocks, removing any thinking tag content."""
        try:
            # Remove thinking tags content
            clean_content = self.remove_think_tags(markdown_content)

            # Try to find JSON code block with explicit json tag
            json_match = re.search(r'```json\n([\s\S]*?)\n```', clean_content)
            if json_match:
                json_str = json_match.group(1)
            else:
                # Try alternative format that might be used
                json_match = re.search(r'```(\s*json)?\n([\s\S]*?)\n```', clean_content)
                if not json_match:
                    logging.warning("No JSON found in the response")
                    return None
                json_str = json_match.group(2)

            return json.loads(json_str.strip())

        except json.JSONDecodeError as e:
            logging.warning(f"Failed to parse JSON: {str(e)}")
            return None
        except Exception as e:
            logging.error(f"Error processing markdown content: {str(e)}")
            return None

    def get_available_tools(self, petp_mcp_url: str) -> Optional[Dict[str, Any]]:
        """Call the MCP server to list all available tools."""
        try:
            response = requests.get(f"{petp_mcp_url}/petp/tools")
            response.raise_for_status()
            resp_json = response.json()
            logging.debug(f"Available tools: {resp_json}")
            return resp_json['data']
        except requests.RequestException as e:
            logging.error(f"Failed to fetch tools: {str(e)}")
            return None

    def build_tools_message(self, available_tools: Dict[str, Any]) -> str:
        """Build the system message with available tools description."""
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

    def process_llm_response(self, answer: str, petp_mcp_url: str, available_tools: Dict[str, Any]) -> str:
        """Process the LLM response and execute tools if needed."""
        try:
            tool_call = self.read_json_from_markdown(answer)
            if not tool_call or "tool" not in tool_call or "arguments" not in tool_call:
                return answer

            tool_name = tool_call['tool']
            tool_args = tool_call['arguments']

            if tool_name not in available_tools:
                logging.warning(f"Tool '{tool_name}' not found in available tools")
                return answer

            logging.info(f"Executing tool: {tool_name} with arguments: {tool_args}")

            # Prepare parameters
            params = {"execution": tool_name, "fromHTTPService": True}
            for key, value in tool_args.items():
                if isinstance(value, list):
                    params[key] = ",".join(str(v) for v in value)
                else:
                    params[key] = value

            # Execute tool
            payload = {
                "action": "execution",
                "params": params
            }

            response = requests.post(
                f"{petp_mcp_url}/petp/exec",
                json=payload,
                headers={"Content-Type": "application/json"}
            )

            response.raise_for_status()
            result = response.json() if response.content else response.text
            logging.debug(f"Tool execution result: {result}")

            return str(result)

        except requests.RequestException as e:
            error_msg = f"Error executing tool: {str(e)}"
            logging.error(error_msg)
            return f"Failed to execute tool: {error_msg}"
        except Exception as e:
            logging.error(f"Error processing LLM response: {str(e)}")
            return answer
