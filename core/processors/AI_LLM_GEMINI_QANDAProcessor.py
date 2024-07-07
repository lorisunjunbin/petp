import json
import logging
import re

import wx
from langchain_google_genai import ChatGoogleGenerativeAI

from core.processor import Processor

"""
REQUIREMENTS:

pip install langchain
pip install langchain-google-genai
pip install generativeai


"""


class AI_LLM_GEMINI_QANDAProcessor(Processor):
    TPL: str = '{"llm_data_key":"llmgemini", "prompt":"prompt", "resp_content_key":"","convert_resp_2_json":"yes","show_in_popup":"yes"}'

    DESC: str = f'''
        this task depends on the task AI_LLM_GEMINI_SETUPProcessor, which is to setup LLM Gemini, then save the llm instance to llm_data_key.
        Ask llm gemini a question associated with prompt get the response, parse the response to json if needed, and show the response in popup dialog if needed.
        
        {TPL}
    '''

    def get_category(self) -> str:
        return super().CATE_AI_LLM

    def process(self):
        llm_data_key = self.get_param('llm_data_key')
        existed_llm: ChatGoogleGenerativeAI = self.get_data(llm_data_key)
        prompt = self.expression2str(self.get_param('prompt'))
        resp_content_key = self.get_data("resp_content_key")
        convert_resp_2_json = True if 'yes' == self.get_param("convert_resp_2_json") else False
        show_in_popup = True if 'yes' == self.get_param("show_in_popup") else False

        if existed_llm is None:
            msg = f'LLM Gemini is not setup yet, please add task AI_LLM_GEMINI_SETUPProcessor as previous Task.'
            wx.MessageDialog(None, msg, "AI_LLM_GEMINI_Q&A").ShowModal()
            return

        logging.debug(f'prompt: {prompt}')
        answer = existed_llm.invoke(prompt)
        logging.debug(f'answer: {answer}')

        content = self.read_json_from_markdown(answer.content) if convert_resp_2_json else answer.content
        message = "Q:\n" + prompt + "\nA:\n" + content
        logging.info(f'Q and A:\n {message}')

        if show_in_popup:
            wx.MessageDialog(None, message, "AI_LLM_GEMINI_QANDA").ShowModal()

        self.populate_data(resp_content_key, content)

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
