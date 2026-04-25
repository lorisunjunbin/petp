import json
import logging

try:
    import wx
except ImportError:
    wx = None
import ollama

from core.processor import Processor

"""
Refer: https://github.com/ollama/ollama-python

1, install ollama:
> pip install ollama

2, pull the model you want to use, for example:
> ollama pull llama3.2:latest
> ollama pull deepseek-r1:7b

3, run ollama:
> ollama run deepseek-r1:7b

curl http://localhost:11434/api/generate -d '{
  "model": "llama3.1",
  "prompt": "Why is the sky blue?"
}'

"""


class AI_LLM_OLLAMA_QANDAProcessor(Processor):
    TPL: str = '{"model":"deepseek-r1:7b", "prompt":"How old are you?", "role":"user","show_in_popup":"yes","resp_content_key":"ollama_resp"}'

    DESC: str = f'''
        Ask Ollama LLM a question via a locally running Ollama instance, retrieve the response, parse it to JSON if needed,
        and optionally display the response in a popup dialog. Requires Ollama to be running locally.

        - model: The Ollama model name to use for chat (supports expression, default: "deepseek-r1:7b")
        - prompt: The question or prompt text to send to the LLM (supports expression, default: "How old are you?")
        - role: The chat role for the message, typically "user" or "system" (default: "user")
        - show_in_popup: Whether to display the Q&A result in a popup dialog, "yes" or "no" (default: "yes")
        - resp_content_key: The data chain key under which the raw LLM response will be stored (default: "ollama_resp")

        {TPL}
    '''

    def get_category(self) -> str:
        return super().CATE_AI_LLM

    def process(self):
        model = self.get_param('model')
        role = self.get_param('role')
        prompt = self.expression2str(self.get_param('prompt'))
        resp_content_key = self.explain_param_or_default('resp_content_key', '')
        show_in_popup = True if 'yes' == self.get_param("show_in_popup") else False

        try:
            answer = ollama.chat(model=model, messages=[{
                'role': role,
                'content': prompt,
            }])

            message = "Q:\n" + prompt + "\nA:\n" + self._try_process_resp_json(answer)
            logging.info('Ollama response received (model=%s)', model)
            logging.debug('Q and A:\n%s', message)

            if show_in_popup:
                if wx is not None:
                    wx.MessageDialog(None, message, "AI_LLM_OLLAMA_QAND").ShowModal()
                else:
                    logging.info(f"[Notification] AI_LLM_OLLAMA_QAND: {message}")

            self.populate_data(resp_content_key, answer)
        except ollama.ResponseError as e:
            logging.error(f'Can NOT call ollama, because: {e.error}')

    def _try_process_resp_json(self, given):
        try:
            return json.dumps(given)
        except Exception as e:
            logging.error(f'Can NOT convert to json, because: {e}, will return str directly.')
            return str(given)
