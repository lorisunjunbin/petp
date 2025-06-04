import json
import logging
import re
from typing import Any, Dict, List, Optional

import requests
import wx
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from core.processor import Processor

"""
REQUIREMENTS:

pip install langchain
pip install langchain-google-genai
pip install generativeai
pip install requests

"""


class AI_LLM_GEMINI_QANDA_MCPProcessor(Processor):
	TPL: str = '{"llm_data_key":"llmgemini", "prompt":"prompt", "petp_mcp_url":"http://localhost:8888", "resp_content_key":"gemini_response","convert_resp_2_json":"yes","show_in_popup":"yes"}'

	DESC: str = f'''
        This task depends on the task AI_LLM_GEMINI_SETUPProcessor, which is to setup LLM Gemini, then save the llm instance to llm_data_key.
        
        Run another PETP as mcp server, http endpoint: http://localhost:8888
        
        Ask llm gemini a question associated with available tools, if tool is available, call tool then give the response accordingly.
        
        - llm_data_key: Key to retrieve the pre-configured Gemini LLM instance.
        - prompt: The question/prompt to send to the LLM.
        - petp_mcp_url: The base URL of the PETP MCP server for tool execution (e.g., "http://localhost:8888").
        - model: The Gemini model to use (e.g., "gemini-pro"). Note: The primary model is usually set during SETUP.
        - temperature: The sampling temperature for the LLM. Note: The primary temperature is usually set during SETUP.
        - resp_content_key: The key under which the final response content will be stored in the data chain.
        - convert_resp_2_json: If 'yes', attempts to parse the final response as JSON from a markdown block.
        - show_in_popup: If 'yes', displays the final question and answer in a popup dialog.
        
        {TPL}
    '''

	def get_category(self) -> str:
		return super().CATE_AI_LLM

	def process(self):
		llm_data_key = self.get_param('llm_data_key')
		existed_llm: ChatGoogleGenerativeAI = self.get_data(llm_data_key)

		if existed_llm is None:
			msg = f'LLM Gemini is not setup yet, please add task AI_LLM_GEMINI_SETUPProcessor as a previous Task.'
			wx.MessageDialog(None, msg, "AI_LLM_GEMINI_Q&A Error").ShowModal()
			return

		# Get parameters
		prompt = self.expression2str(self.get_param('prompt'))
		petp_mcp_url = self.get_param('petp_mcp_url')
		resp_content_key = self.get_param("resp_content_key")
		convert_resp_2_json = self.get_param("convert_resp_2_json") == 'yes'
		show_in_popup = self.get_param("show_in_popup") == 'yes'

		# Get available tools from PETP MCP server
		available_tools = self.get_available_tools(petp_mcp_url)
		available_tools_prompt = self.build_tools_message(available_tools)

		messages = [
			SystemMessage(content=available_tools_prompt),
			HumanMessage(content=prompt),
		]

		logging.debug(f'Initial prompt to Gemini: {prompt}')
		logging.debug(f'System message with tools: {available_tools_prompt}')

		try:
			logging.info(f'Calling Gemini LLM with messages: {messages}')
			response_obj = existed_llm.invoke(messages)
			answer = response_obj.content
			logging.debug(f'Initial answer from Gemini: {answer}')

			# Process LLM response for potential tool calls
			tool_call_result = self.process_llm_response(answer, petp_mcp_url, available_tools)

			final_answer = answer

			if tool_call_result != answer:  # Implies a tool was called and result is different
				messages.clear()
				messages.append(HumanMessage(content=prompt))  # User's original question
				# Provide tool result to LLM for final answer generation
				system_message_after_tool = f'Please answer strictly based on the result [ {tool_call_result} ], prefer to use the language of the original prompt.'
				messages.append(SystemMessage(content=system_message_after_tool))

				logging.info(f'Calling Gemini LLM after tool call with messages: {messages}')
				final_response_obj = existed_llm.invoke(messages)
				final_answer = final_response_obj.content
				logging.info(f"Final response from Gemini after tool use: {final_answer}")

			messages.append(AIMessage(content=final_answer))  # Append final assistant message

			content = self.read_json_from_markdown(final_answer) if convert_resp_2_json else final_answer

			alert_message = f"Q:\n{prompt}\n\nA:\n{content}"
			logging.info(f'Final Q and A:\n {alert_message}')

			if show_in_popup:
				dlg = wx.MessageDialog(None, alert_message, "AI LLM GEMINI Q&A (MCP)")
				dlg.ShowModal()
				dlg.Destroy()

			self.populate_data(resp_content_key, content)

		except Exception as e:
			error_msg = f'Unexpected error: {str(e)}'
			logging.error(error_msg)
			wx.MessageDialog(None, error_msg, "AI LLM GEMINI Q&A (MCP) Error").ShowModal()

	def read_json_from_markdown(self, markdown_content: str) -> Optional[Dict[str, Any]]:
		"""Extract JSON from markdown code blocks."""
		try:
			json_match = re.search(r'```json\n([\s\S]*?)\n```', markdown_content)
			if json_match:
				json_str = json_match.group(1)
				return json.loads(json_str)
			else:
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
			else:
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

	def process_llm_response(self, answer: str, petp_mcp_url: str, available_tools: Dict[str, Any]) -> str:
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
