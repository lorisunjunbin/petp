import logging
import os

from core.processor import Processor
from core.processors.sub.llm.BaseLLMClient import BaseLLMClient, LLMResponse
from core.processors.sub.llm.llm_helpers import (
    read_json_from_markdown,
    remove_think_tags,
    show_notification,
)


class AI_LLM_QANDAProcessor(Processor):
    TPL: str = '{"llm_data_key":"llm_client", "prompt":"", "model":"", "temperature":"1.0", "system_prompt":"", "image_path":"", "resp_content_key":"", "convert_resp_2_json":"no", "show_in_popup":"yes", "show_thinking":"no"}'

    DESC: str = '''
Ask a unified LLM a question and get the response. Depends on AI_LLM_SETUP to initialize the client first.

Works with all supported providers: deepseek, zhipu, qianfan, minimax, doubao, moonshot, gemini, ollama, anthropic, openai_compatible.

- llm_data_key: key in data_chain where the LLM client instance is stored (default: "llm_client")
- prompt: question to ask the LLM (supports expression)
- model: model name; if empty, uses the model configured during SETUP (supports expression, default: "")
- temperature: sampling temperature (default: "1.0")
- system_prompt: system message prepended to conversation; if empty, no system message is sent (supports expression, default: "")
- image_path: path to an image file to include with the prompt; supported by ollama vision models (supports expression, default: "")
- resp_content_key: key in data_chain to store the response content (supports expression, default: "")
- convert_resp_2_json: "yes" to parse JSON from markdown code block in response (default: "no")
- show_in_popup: "yes" to display Q&A in popup dialog (default: "yes")
- show_thinking: "yes" to keep <think> tags in displayed output; "no" to strip them (default: "no")
'''

    def get_category(self) -> str:
        return super().CATE_AI_LLM

    def process(self):
        llm_data_key = self.expression2str(self.get_param('llm_data_key'))
        client: BaseLLMClient = self.get_data(llm_data_key)

        if client is None:
            msg = f'LLM client not found at key "{llm_data_key}". Please add AI_LLM_SETUP as a previous task.'
            show_notification("AI_LLM_QANDA", msg)
            return

        prompt = self.expression2str(self.get_param('prompt'))
        model = self.explain_param_or_default('model', '')
        temperature = self.explain_param_as_float('temperature', 1.0)
        system_prompt = self.explain_param_or_default('system_prompt', '')
        image_path = self.explain_param_or_default('image_path', '')
        resp_content_key = self.explain_param_or_default('resp_content_key', '')
        convert_resp_2_json = self.get_param_bool_if_equal('convert_resp_2_json', 'yes')
        show_in_popup = self.get_param_bool_if_equal('show_in_popup', 'yes')
        show_thinking = self.get_param_bool_if_equal('show_thinking', 'yes')

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        if image_path and os.path.isfile(image_path):
            user_content = [
                {"type": "text", "text": prompt},
                {"type": "image", "path": image_path},
            ]
            messages.append({"role": "user", "content": user_content})
            logging.info(f'Image attached: {image_path}')
        else:
            if image_path:
                logging.warning(f'image_path specified but file not found: {image_path}')
            messages.append({"role": "user", "content": prompt})

        logging.debug(f'LLM prompt: {prompt}')

        try:
            response: LLMResponse = client.chat_with_retry(
                messages=messages,
                model=model,
                temperature=temperature,
            )

            answer_text = response.content or response.reasoning_content or ''
            logging.debug(f'Raw answer: {answer_text}')

            content = read_json_from_markdown(answer_text) if convert_resp_2_json else answer_text
            display_text = answer_text if show_thinking else remove_think_tags(answer_text)
            message = f"Q:\n{prompt}\n\nA:\n{display_text}"
            logging.debug('Q and A:\n%s', message)

            if show_in_popup:
                show_notification(f"AI_LLM_QANDA ({client.provider_name})", message)

            if resp_content_key:
                self.populate_data(resp_content_key, content)

        except Exception as e:
            error_msg = f'Error calling LLM ({client.provider_name}): {e}'
            logging.error(error_msg)
            show_notification("AI_LLM_QANDA Error", error_msg)
