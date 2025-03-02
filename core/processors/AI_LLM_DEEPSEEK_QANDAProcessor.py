import json
import logging
import re

import wx
from openai import OpenAI, APIError, APIStatusError

from core.processor import Processor

"""
REQUIREMENTS:

pip install openai

"""


class AI_LLM_DEEPSEEK_QANDAProcessor(Processor):
	TPL: str = '{"llm_data_key":"llmdeepseek", "prompt":"prompt", "model":"deepseek-chat","temperature":"1.0", "resp_content_key":"","convert_resp_2_json":"yes","show_in_popup":"yes"}'

	DESC: str = f'''
        this task depends on the task AI_LLM_DEEPSEEK_SETUPProcessor, which is to setup LLM DeepSeek, then save the llm instance to llm_data_key.
        Ask llm deepseek a question associated with prompt get the response, parse the response to json if needed, and show the response in popup dialog if needed.
        
        USE CASE TEMPERATURE
        
		Coding / Math: 0.0
		Data Cleaning / Data Analysis: 1.0
		General Conversation: 1.3
		Translation: 1.3
		Creative Writing / Poetry: 1.5
        
        {TPL}
    '''

	def get_category(self) -> str:
		return super().CATE_AI_LLM

	def process(self):
		llm_data_key = self.get_param('llm_data_key')
		existed_llm: OpenAI = self.get_data(llm_data_key)
		prompt = self.expression2str(self.get_param('prompt'))
		resp_content_key = self.get_data("resp_content_key")
		convert_resp_2_json = True if 'yes' == self.get_param("convert_resp_2_json") else False
		show_in_popup = True if 'yes' == self.get_param("show_in_popup") else False

		if existed_llm is None:
			msg = f'LLM DeepSeek is not setup yet, please add task AI_LLM_DEEPSEEK_SETUPProcessor as previous Task.'
			wx.MessageDialog(None, msg, "AI_LLM_DEEPSEEK_Q&A").ShowModal()
			return

		model = self.get_param('model')
		temperature = float(self.get_param('temperature'))

		logging.debug(f'prompt: {prompt}')
		try:
			response = existed_llm.chat.completions.create(
				model=model,
				messages=[
					{"role": "system", "content": "你是一个资深的科学助手"},
					{"role": "user", "content": prompt},
				],
				temperature=temperature,
				stream=False
			)
			answer = response.choices[0].message
			logging.debug(f'answer: {answer}')

			content = self.read_json_from_markdown(answer.content) if convert_resp_2_json else answer.content
			message = "Q:\n" + prompt + "\nA:\n" + content
			logging.info(f'Q and A:\n {message}')

			if show_in_popup:
				wx.MessageDialog(None, message, "AI_LLM_DEEPSEEK_QANDA").ShowModal()

			self.populate_data(resp_content_key, content)
		except APIStatusError as e:
			error_msg = f'API Status Error: {e.status_code} - {e.response.json()["error"]["message"]}'
			logging.error(error_msg)
			wx.MessageDialog(None, error_msg, "AI_LLM_DEEPSEEK_QANDA").ShowModal()
		except APIError as e:
			error_msg = f'API Error: {str(e)}'
			logging.error(error_msg)
			wx.MessageDialog(None, error_msg, "AI_LLM_DEEPSEEK_QANDA").ShowModal()
		except Exception as e:
			error_msg = f'Unexpected error: {str(e)}'
			logging.error(error_msg)
			wx.MessageDialog(None, error_msg, "AI_LLM_DEEPSEEK_QANDA").ShowModal()
def read_json_from_markdown(markdown_content: str) -> dict[str, any]:
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
