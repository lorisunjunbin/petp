import json
import logging
import re

try:
    import wx
except ImportError:
    wx = None
import zai

from zai import ZhipuAiClient
from core.processor import Processor

"""
Refer: https://docs.bigmodel.cn/cn/guide/develop/python/introduction

# install zhipu zai sdk:
> pip install zai-sdk
> pip install zai-sdk==0.2.2

# API address: https://open.bigmodel.cn/api/paas/v4/

"""


class AI_LLM_ZHIPU_QANDAProcessor(Processor):
    TPL: str = '{"llm_data_key":"llmZHIPU","prompt":"prompt", "model":"GLM-5","temperature":"1.0", "resp_content_key":"","convert_resp_2_json":"yes","show_in_popup":"yes"}'

    DESC: str = f'''
        Ask ZhipuAI (GLM) big model a question, retrieve the response, optionally parse it as JSON from a markdown block,
        and optionally display the Q&A in a popup dialog. Depends on AI_LLM_ZHIPU_SETUPProcessor to have previously
        initialized the ZhipuAI client instance.

        - llm_data_key: Key to retrieve the pre-configured ZhipuAI client instance from the data chain (default: "llmZHIPU")
        - prompt: The question or prompt text to send to the LLM (supports expression, default: "prompt")
        - model: The ZhipuAI model name to use for the chat completion (default: "GLM-5")
        - temperature: The sampling temperature as a float string, higher values produce more creative output (default: "1.0")
        - resp_content_key: The data chain key under which the final response content will be stored (default: "")
        - convert_resp_2_json: If "yes", attempts to parse the response as JSON from a markdown code block (default: "yes")
        - show_in_popup: Whether to display the Q&A result in a popup dialog, "yes" or "no" (default: "yes")

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
            if wx is not None:
                wx.MessageDialog(None, msg, "AI_LLM_ZHIPU_Q&A").ShowModal()
            else:
                logging.info(f"[Notification] AI_LLM_ZHIPU_Q&A: {msg}")
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

            content = self.read_json_from_markdown(
                answer.reasoning_content) if convert_resp_2_json else answer.reasoning_content
            message = "Q:\n" + prompt + "\nA:\n" + content
            logging.info('Zhipu response received (model=%s)', model)
            logging.debug('Q and A:\n%s', message)

            if show_in_popup:
                if wx is not None:
                    wx.MessageDialog(None, message, "AI_LLM_ZHIPU_QANDA").ShowModal()
                else:
                    logging.info(f"[Notification] AI_LLM_ZHIPU_QANDA: {message}")

            self.populate_data(resp_content_key, content)
        except zai.core.APIStatusError as err:
            error_msg = f"API status Error: {err}"
            logging.error(error_msg)
            if wx is not None:
                wx.MessageDialog(None, error_msg, "AI_LLM_ZHIPU_QANDA").ShowModal()
            else:
                logging.info(f"[Notification] AI_LLM_ZHIPU_QANDA: {error_msg}")
        except zai.core.APITimeoutError as err:
            error_msg = f"request timeout: {err}"
            logging.error(error_msg)
            if wx is not None:
                wx.MessageDialog(None, error_msg, "AI_LLM_ZHIPU_QANDA").ShowModal()
            else:
                logging.info(f"[Notification] AI_LLM_ZHIPU_QANDA: {error_msg}")
        except Exception as err:
            error_msg = f'Unexpected error: {str(err)}'
            logging.error(error_msg)
            if wx is not None:
                wx.MessageDialog(None, error_msg, "AI_LLM_ZHIPU_QANDA").ShowModal()
            else:
                logging.info(f"[Notification] AI_LLM_ZHIPU_QANDA: {error_msg}")
        except Exception as e:
            error_msg = f'Unexpected error: {str(e)}'
            logging.error(error_msg)
            if wx is not None:
                wx.MessageDialog(None, error_msg, "AI_LLM_ZHIPU_QANDA").ShowModal()
            else:
                logging.info(f"[Notification] AI_LLM_ZHIPU_QANDA: {error_msg}")

    def read_json_from_markdown(self, markdown_content: str) -> dict:
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
