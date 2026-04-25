import json
import logging
import re

try:
    import wx
except ImportError:
    wx = None

from core.processor import Processor

"""
REQUIREMENTS:

pip install google-genai


"""


class AI_LLM_GEMINI_QANDAProcessor(Processor):
    TPL: str = '{"llm_data_key":"llmgemini", "prompt":"prompt", "resp_content_key":"","convert_resp_2_json":"yes","show_in_popup":"yes"}'

    DESC: str = f'''
        Ask Google Gemini LLM a question using a previously configured Gemini instance
        (set up by AI_LLM_GEMINI_SETUPProcessor). The prompt is sent to the model, and the
        response can optionally be parsed as JSON and/or displayed in a popup dialog.

        Requires: pip install google-genai

        - llm_data_key: Key in data_chain where the Gemini LLM instance is stored (supports expression, default: "llmgemini")
        - prompt: The question or prompt text to send to the LLM (supports expression, default: "prompt")
        - resp_content_key: Key in data_chain to store the response content; if empty the response is not stored (supports expression, default: "")
        - convert_resp_2_json: If "yes", extracts JSON from the markdown response (supports expression, default: "yes")
        - show_in_popup: If "yes", displays the Q&A result in a popup dialog (supports expression, default: "yes")

        {TPL}
    '''

    def get_category(self) -> str:
        return super().CATE_AI_LLM

    def process(self):
        llm_data_key = self.get_param('llm_data_key')
        existed_llm = self.get_data(llm_data_key)
        prompt = self.expression2str(self.get_param('prompt'))
        resp_content_key = self.get_data("resp_content_key")
        convert_resp_2_json = True if 'yes' == self.get_param("convert_resp_2_json") else False
        show_in_popup = True if 'yes' == self.get_param("show_in_popup") else False

        if existed_llm is None:
            msg = f'LLM Gemini is not setup yet, please add task AI_LLM_GEMINI_SETUPProcessor as previous Task.'
            if wx is not None:
                wx.MessageDialog(None, msg, "AI_LLM_GEMINI_Q&A").ShowModal()
            return

        logging.debug(f'prompt: {prompt}')
        answer = existed_llm.invoke(prompt)
        logging.debug(f'answer: {answer}')

        content = self.read_json_from_markdown(answer.content) if convert_resp_2_json else answer.content
        content_text = content if isinstance(content, str) else json.dumps(content, ensure_ascii=False)
        message = "Q:\n" + prompt + "\nA:\n" + content_text
        logging.info('Gemini response received')
        logging.debug('Q and A:\n%s', message)

        if show_in_popup:
            if wx is not None:
                wx.MessageDialog(None, message, "AI_LLM_GEMINI_QANDA").ShowModal()

        self.populate_data(resp_content_key, content)

    def read_json_from_markdown(self, markdown_content: str):
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
