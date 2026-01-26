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
        To setup ZHIPU LLM client instance, get api key from environment variable named api_key_name or from parameter api_key,
		then create the llm instance and save to llm_data_key.
        
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
