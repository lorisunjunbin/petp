import json
import logging
import re
import wx
import zai

from zai import ZhipuAiClient
from core.processor import Processor

"""
Refer: https://docs.bigmodel.cn/cn/guide/develop/python/introduction

# install zhipu zai sdk:
> pip install zai-sdk
> pip install zai-sdk==0.2.0

# API address: https://open.bigmodel.cn/api/paas/v4/

"""


class AI_LLM_ZHIPU_QANDAProcessor(Processor):
    TPL: str = '{"llm_data_key":"llmZHIPU","prompt":"prompt", "model":"glm-4.7","temperature":"1.0", "resp_content_key":"","convert_resp_2_json":"yes","show_in_popup":"yes"}'

    DESC: str = f'''
        ask zhipu bigmodel a question associated with prompt get the response, parse the response to json if needed, and show the response in popup dialog if needed.
        
        {TPL}
    '''

    def get_category(self) -> str:
        return super().CATE_AI_LLM

    def process(self):
        llm_data_key = self.get_param('llm_data_key')
        existed_llm: ZhipuAiClient = self.get_data(llm_data_key)
        prompt = self.expression2str(self.get_param('prompt'))
        resp_content_key = self.get_data("resp_content_key")
        convert_resp_2_json = True if 'yes' == self.get_param("convert_resp_2_json") else False
        show_in_popup = True if 'yes' == self.get_param("show_in_popup") else False

        if existed_llm is None:
            msg = f'LLM ZHIPU is not setup yet, please add task AI_LLM_ZHIPU_SETUPProcessor as previous Task.'
            wx.MessageDialog(None, msg, "AI_LLM_ZHIPU_Q&A").ShowModal()
            return

        model = self.get_param('model')
        temperature = float(self.get_param('temperature'))

        logging.debug(f'prompt: {prompt}')
        try:
            response = existed_llm.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "你是一个资深的科技助手"},
                    {"role": "user", "content": prompt},
                ],
                temperature=temperature,
                stream=False
            )
            answer = response.choices[0].message
            logging.debug(f'answer: {str(answer)}')

            content = self.read_json_from_markdown(answer.reasoning_content) if convert_resp_2_json else answer.reasoning_content
            message = "Q:\n" + prompt + "\nA:\n" + content
            logging.info(f'Q and A:\n {message}')

            if show_in_popup:
                wx.MessageDialog(None, message, "AI_LLM_ZHIPU_QANDA").ShowModal()

            self.populate_data(resp_content_key, content)
        except zai.core.APIStatusError as err:
            error_msg = f"API status Error: {err}"
            logging.error(error_msg)
            wx.MessageDialog(None, error_msg, "AI_LLM_ZHIPU_QANDA").ShowModal()
        except zai.core.APITimeoutError as err:
            error_msg = f"request timeout: {err}"
            logging.error(error_msg)
            wx.MessageDialog(None, error_msg, "AI_LLM_ZHIPU_QANDA").ShowModal()
        except Exception as err:
            error_msg = f'Unexpected error: {str(err)}'
            logging.error(error_msg)
            wx.MessageDialog(None, error_msg, "AI_LLM_ZHIPU_QANDA").ShowModal()
        except Exception as e:
            error_msg = f'Unexpected error: {str(e)}'
            logging.error(error_msg)
            wx.MessageDialog(None, error_msg, "AI_LLM_ZHIPU_QANDA").ShowModal()

    def read_json_from_markdown(self, markdown_content: str) -> dict[str, any]:
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
