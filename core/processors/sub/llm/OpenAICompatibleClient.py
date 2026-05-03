import importlib
import logging
import os
from typing import Optional

from core.processors.sub.llm.BaseLLMClient import BaseLLMClient, LLMResponse


class OpenAICompatibleClient(BaseLLMClient):

    def __init__(self, client, provider: str):
        self._client = client
        self._provider = provider

    @property
    def provider_name(self) -> str:
        return self._provider

    def chat(self, messages: list, model: str, temperature: float, **kwargs) -> LLMResponse:
        response = self._client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            stream=False
        )
        answer = response.choices[0].message
        content = getattr(answer, 'content', '') or ''
        reasoning = getattr(answer, 'reasoning_content', None)
        return LLMResponse(content=content, reasoning_content=reasoning)

    @classmethod
    def create(cls, provider: str, api_key: str = '', base_url: str = '', **kwargs) -> 'OpenAICompatibleClient':
        if provider == 'zhipu':
            client, backend = cls._create_zhipu_client(api_key=api_key, base_url=base_url)
            logging.info('LLM client initialized via %s', backend)
        else:
            from openai import OpenAI
            client = OpenAI(api_key=api_key, base_url=base_url)
            logging.info('LLM client initialized via openai.OpenAI (provider=%s)', provider)
        return cls(client=client, provider=provider)

    @staticmethod
    def _create_zhipu_client(api_key: str, base_url: str):
        try:
            zai = importlib.import_module('zai')
            for cls_name in ('ZhipuAiClient', 'ZhipuAI', 'Client'):
                cls_obj = getattr(zai, cls_name, None)
                if cls_obj is None:
                    continue
                try:
                    return cls_obj(base_url=base_url, api_key=api_key), f'zai.{cls_name}'
                except TypeError:
                    return cls_obj(api_key=api_key), f'zai.{cls_name}'
        except Exception:
            pass

        from openai import OpenAI
        return OpenAI(api_key=api_key, base_url=base_url), 'openai.OpenAI (zhipu fallback)'
