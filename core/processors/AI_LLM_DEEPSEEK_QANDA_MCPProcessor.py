import json
import logging
import re
from typing import Any, Dict, List, Optional

import requests
try:
    import wx
except ImportError:
    wx = None
from openai import OpenAI

from core.processor import Processor

"""
REQUIREMENTS:

pip install openai

reference: 
https://github.com/modelcontextprotocol/python-sdk
https://github.com/modelcontextprotocol/python-sdk/tree/main/examples/clients/simple-chatbot

"""


class AI_LLM_DEEPSEEK_QANDA_MCPProcessor(Processor):
	TPL: str = '{"llm_data_key":"llmdeepseek", "prompt":"prompt","petp_mcp_url":"http://localhost:8888", "model":"deepseek-chat","temperature":"1.0", "resp_content_key":"","convert_resp_2_json":"yes","show_in_popup":"yes"}'

	DESC: str = f'''
        Ask DeepSeek LLM a question with MCP tool support. Depends on AI_LLM_DEEPSEEK_SETUPProcessor to setup the LLM instance first.
        Runs another PETP as MCP server. If LLM decides to use a tool, it calls the MCP endpoint and feeds the result back.

        - llm_data_key: key of data_chain where the LLM client instance is stored (default: "llmdeepseek")
        - prompt: question to ask the LLM (supports expression)
        - petp_mcp_url: base URL of the PETP MCP server (default: "http://localhost:8888")
        - model: DeepSeek model name (default: "deepseek-chat")
        - temperature: sampling temperature, Coding/Math: 0.0, Data Analysis: 1.0, Conversation: 1.3, Creative Writing: 1.5 (default: "1.0")
        - resp_content_key: key of data_chain to store the final response content
        - convert_resp_2_json: "yes" to parse JSON from markdown code block in response (default: "yes")
        - show_in_popup: "yes" to display Q&A in popup dialog (default: "yes")

        {TPL}
    '''

	def get_category(self) -> str:
		return super().CATE_AI_LLM

	def process(self):
		"""Process the DeepSeek LLM request with available tools."""
		llm_data_key = self.get_param('llm_data_key')
		existed_llm: OpenAI = self.get_data(llm_data_key)
		if existed_llm is None:
			msg = 'LLM DeepSeek is not setup yet, please add task AI_LLM_DEEPSEEK_SETUPProcessor as previous Task.'
			if wx is not None:
				wx.MessageDialog(None, msg, "AI_LLM_DEEPSEEK_Q&A").ShowModal()
			else:
				logging.info(f"[Notification] AI_LLM_DEEPSEEK_Q&A: {msg}")
			return

		# get params
		petp_mcp_url = self.get_param('petp_mcp_url')
		prompt = self.expression2str(self.get_param('prompt'))
		resp_content_key = self.get_data("resp_content_key")
		convert_resp_2_json = self.get_param("convert_resp_2_json") == 'yes'
		show_in_popup = self.get_param("show_in_popup") == 'yes'
		model = self.get_param('model')
		temperature = float(self.get_param('temperature'))

		# get available tools
		available_tools = self.get_available_tools(petp_mcp_url)
		available_tools_prompt = self.build_tools_message(available_tools)

		messages = [
			{"role": "system", "content": available_tools_prompt},
			{"role": "user", "content": prompt},
		]

		logging.debug(f'prompt: {prompt}')
		logging.debug(f'available_tools: {available_tools_prompt}')

		try:
			logging.info(f'Calling LLM with messages: {messages}')
			response = existed_llm.chat.completions.create(
				model=model,
				messages=messages,
				temperature=temperature,
				stream=False,
				stop=None
			)

			answer = response.choices[0].message.content
			logging.debug(f'answer: {answer}')

			new_answer = self.process_llm_response(answer, petp_mcp_url, available_tools)
			final_answer = answer

			if new_answer != answer:
				messages.append({"role": "assistant", "content": answer})
				messages.append({"role": "system",
								 "content": f' Please answer strictly based on the result [ {new_answer} ], prefer to use Chinese'})

				logging.info(f'Calling LLM after tool call with messages: {messages}')
				final_response = existed_llm.chat.completions.create(
					model=model,
					messages=messages,
					temperature=temperature,
					stream=False,
					stop=None
				)
				logging.info("\nFinal response: %s", final_response)
				final_answer = final_response.choices[0].message.content

			messages.append({"role": "assistant", "content": final_answer})
			content = self.read_json_from_markdown(final_answer) if convert_resp_2_json else final_answer

			alert_message = f"Q:\n{prompt}\nA:\n{content}"
			logging.info(f'Q and A:\n {alert_message}')

			if show_in_popup:
				if wx is not None:
					wx.MessageDialog(None, alert_message, "AI_LLM_DEEPSEEK_QANDA_MCP").ShowModal()
				else:
					logging.info(f"[Notification] AI_LLM_DEEPSEEK_QANDA_MCP: {alert_message}")

			self.populate_data(resp_content_key, content)
		except Exception as e:
			error_msg = f'Unexpected error: {str(e)}'
			logging.error(error_msg)
			if wx is not None:
				wx.MessageDialog(None, error_msg, "AI_LLM_DEEPSEEK_QANDA_MCP").ShowModal()
			else:
				logging.info(f"[Notification] AI_LLM_DEEPSEEK_QANDA_MCP: {error_msg}")

	def read_json_from_markdown(self, markdown_content: str) -> Optional[Dict[str, Any]]:
		"""Extract JSON from markdown code blocks."""
		try:
			json_match = re.search(r'```json\n([\s\S]*?)\n```', markdown_content)
			if json_match:
				json_str = json_match.group(1)
				return json.loads(json_str)
			else:
				logging.warning("No JSON found in the Response.")
				return None
		except json.JSONDecodeError:
			logging.warning("Failed to parse JSON.")
			return None

	def get_available_tools(self, petp_mcp_url: str) -> Optional[List[Dict[str, Any]]]:
		"""Call the MCP server to list all available tools."""
		try:
			response = requests.get(f"{petp_mcp_url}/petp/tools")
			if response.status_code == 200:
				resp_json = response.json()
				logging.debug(f" get_available_tools - : {resp_json}")
				return resp_json['data']
			else:
				logging.error(f"Failed to list tools: {response.status_code}")
				return None
		except requests.RequestException as e:
			logging.error(f"Request failed: {str(e)}")
			return None

	def build_tools_message(self, available_tool: Dict[str, Any]) -> Optional[str]:
		"""Build the system message with available tools description."""
		try:
			system_message = (
				"You are a helpful assistant with access to these tools:\n\n"
				f"{available_tool}\n"
				"Choose the appropriate tool based on the user's question. "
				"If no tool is needed, reply directly.\n\n"
				"IMPORTANT: When you need to use a tool, you must ONLY respond with "
				"the exact JSON object format below, nothing else:\n"
				"{\n"
				'    "tool": "tool-name",\n'
				'    "arguments": {\n'
				'        "argument-name": "value"\n'
				"    }\n"
				"}\n\n"
				"After receiving a tool's response:\n"
				"1. Transform the raw data into a natural, conversational response\n"
				"2. Keep responses concise but informative\n"
				"3. Focus on the most relevant information\n"
				"4. Use appropriate context from the user's question\n"
				"5. Avoid simply repeating the raw data\n\n"
				"Please use only the tools that are explicitly defined above."
			)
			return system_message
		except Exception as e:
			logging.error(f"Fail to build_tools_message: {str(e)}")
			return None

	def process_llm_response(self, answer: str, petp_mcp_url: str, available_tools: Dict[str, Any]) -> str:
		"""Process the LLM response and execute tools if needed."""
		try:
			tool_call = self.read_json_from_markdown(answer)
			if tool_call and "tool" in tool_call and "arguments" in tool_call:
				tool_name = tool_call['tool']
				tool_args = tool_call['arguments']

				logging.info(f"Executing tool: {tool_name}")
				logging.info(f"With arguments: {tool_args}")

				params = {"execution": tool_name, "fromHTTPService": True}

				for key, value in tool_args.items():
					if isinstance(value, str):
						params[key] = value
					elif isinstance(value, list):
						params[key] = ",".join(value)
					else:
						params[key] = value

				if tool_name in available_tools:
					try:
						payload = {
							"action": "execution",
							"params": params
						}

						result = requests.post(
							f"{petp_mcp_url}/petp/exec",
							json=payload,
							headers={"Content-Type": "application/json"}
						)
						logging.info(f"call tool request payload: {payload}")
						result.raise_for_status()
						response_content = result.json() if result.content else result.text
						logging.info(f"call tool response: {response_content}")

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
