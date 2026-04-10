import logging
import os

from openai import OpenAI

from core.processor import Processor

"""
REQUIREMENTS:

pip install openai


"""


class AI_LLM_DEEPSEEK_SETUPProcessor(Processor):
    TPL: str = '{"api_key_name":"DEEPSEEK_API_KEY", "api_key":"", "base_url":"https://api.deepseek.com", "llm_data_key":"llmdeepseek"}'

    DESC: str = f'''
        Set up a DeepSeek LLM client instance (OpenAI-compatible). The API key can be provided
        directly or read from an environment variable. The client is stored in the data_chain
        for use by downstream tasks. Skips setup if the client already exists.

        Requires: pip install openai

        - api_key_name: Name of the environment variable holding the API key (supports expression, default: "DEEPSEEK_API_KEY")
        - api_key: API key string; if provided, takes precedence over the environment variable (supports expression, default: "")
        - base_url: Base URL of the DeepSeek API endpoint (supports expression, default: "https://api.deepseek.com")
        - llm_data_key: Key in data_chain to store the initialized OpenAI/DeepSeek client instance (supports expression, default: "llmdeepseek")

        {TPL}
    '''

    def get_category(self) -> str:
        return super().CATE_AI_LLM

    def process(self):
        llm_data_key = self.get_param('llm_data_key')
        existed_llm = self.get_data(llm_data_key)

        if existed_llm is not None:
            logging.info(f'LLM DeepSeek was already setup, skip.')
            return
        api_key_name = self.get_param('api_key_name')

        api_key = self.get_param('api_key') if self.has_param('api_key') else \
            (os.environ[api_key_name] if api_key_name in os.environ else None)

        if api_key is None:
            raise ValueError(
                f'No API Key found in environment variables with key: {api_key_name} or in parameter: api_key')

        base_url = self.get_param('base_url')

        deepseek: OpenAI = OpenAI(api_key=api_key, base_url=base_url)

        self.populate_data(llm_data_key, deepseek)
