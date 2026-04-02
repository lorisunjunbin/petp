import logging
import os
from zai import ZhipuAiClient
from core.processor import Processor

"""
Refer: https://docs.bigmodel.cn/cn/guide/develop/python/introduction

# install zhipu zai sdk:
> pip install zai-sdk
> pip install zai-sdk==0.2.0

# API address: https://open.bigmodel.cn/api/paas/v4/

"""


class AI_LLM_ZHIPU_SETUPProcessor(Processor):
    TPL: str = '{"api_key_name":"ZHIPU_ACCESS_KEY", "api_key":"", "base_url":"https://open.bigmodel.cn/api/paas/v4/", "llm_data_key":"llmZHIPU"}'

    DESC: str = f'''
        Initialize and configure a ZhipuAI LLM client instance by reading the API key from an environment variable
        (specified by api_key_name) or directly from the api_key parameter. The client is then stored in the data chain
        for use by downstream processors such as AI_LLM_ZHIPU_QANDAProcessor. Skips setup if an instance already exists.

        - api_key_name: The environment variable name that holds the ZhipuAI API key (default: "ZHIPU_ACCESS_KEY")
        - api_key: The API key string; if empty, the key is read from the environment variable specified by api_key_name (default: "")
        - base_url: The base URL of the ZhipuAI API endpoint (default: "https://open.bigmodel.cn/api/paas/v4/")
        - llm_data_key: The data chain key under which the configured ZhipuAI client instance will be stored (default: "llmZHIPU")

        {TPL}
    '''

    def get_category(self) -> str:
        return super().CATE_AI_LLM

    def process(self):
        llm_data_key = self.get_param('llm_data_key')
        existed_llm = self.get_data(llm_data_key)

        if existed_llm is not None:
            logging.info(f'LLM ZHIPU was already setup, skip.')
            return
        api_key_name = self.get_param('api_key_name')

        api_key = self.get_param('api_key') if self.has_param('api_key') else \
            (os.environ[api_key_name] if api_key_name in os.environ else None)

        if api_key is None:
            raise ValueError(
                f'No API Key found in environment variables with key: {api_key_name} or in parameter: api_key')

        base_url = self.get_param('base_url')

        client = ZhipuAiClient(base_url=base_url, api_key=api_key)

        self.populate_data(llm_data_key, client)
