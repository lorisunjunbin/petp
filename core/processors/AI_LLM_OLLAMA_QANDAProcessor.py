import json
import logging

import wx
import ollama

from core.processor import Processor

"""
llama3.1 8b model running via ollama locally.

Refer: https://github.com/ollama/ollama-python

pip install ollama

curl http://localhost:11434/api/generate -d '{
  "model": "llama3.1",
  "prompt": "Why is the sky blue?"
}'

"""


class AI_LLM_OLLAMA_QANDAProcessor(Processor):
	TPL: str = '{"model":"llama3.1", "prompt":"How old are you?", "role":"user","show_in_popup":"yes","resp_content_key":"ollama_resp"}'

	DESC: str = f'''
        ask llama a question associated with prompt get the response, parse the response to json if needed, and show the response in popup dialog if needed.
        required ollama to be running locally.
        
        {TPL}
    '''

	def get_category(self) -> str:
		return super().CATE_AI_LLM

	def process(self):
		model = self.get_param('model')
		role = self.get_param('role')
		prompt = self.expression2str(self.get_param('prompt'))
		resp_content_key = self.get_data("resp_content_key")
		show_in_popup = True if 'yes' == self.get_param("show_in_popup") else False

		try:
			answer = ollama.chat(model=model, messages=[{
				'role': role,
				'content': prompt,
			}])

			message = "Q:\n" + prompt + "\nA:\n" + json.dumps(answer)
			logging.info(f'Q and A:\n {message}')

			if show_in_popup:
				wx.MessageDialog(None, message, "AI_LLM_OLLAMA_QAND").ShowModal()

			self.populate_data(resp_content_key, answer)
		except ollama.ResponseError as e:
			logging.error(f'Can NOT call ollama, because: {e.error}')
