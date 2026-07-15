import logging
from typing import Optional

from core.processors.sub.llm.BaseLLMClient import BaseLLMClient, LLMResponse


class GeminiClient(BaseLLMClient):

    def __init__(self, client, model: str, config: dict):
        self._client = client
        self._model = model
        self._config = config

    @property
    def provider_name(self) -> str:
        return 'gemini'

    def chat(self, messages: list, model: str, temperature: float, **kwargs) -> LLMResponse:
        use_model = model or self._model
        config = dict(self._config)
        if temperature is not None:
            config['temperature'] = temperature

        prompt_parts = []
        for msg in messages:
            role = msg.get('role', '')
            content = msg.get('content', '')
            if role == 'system':
                prompt_parts.append(f"[System instruction]: {content}")
            elif role == 'user':
                prompt_parts.append(content)
            elif role == 'assistant':
                prompt_parts.append(f"[Previous response]: {content}")
        prompt = "\n\n".join(prompt_parts)

        response = self._client.models.generate_content(
            model=use_model,
            contents=prompt,
            config=config,
        )
        text = getattr(response, 'text', None)
        if text is None:
            text = str(response)
        return LLMResponse(content=text)

    @classmethod
    def create(cls, provider: str, api_key: str = '', model: str = 'gemini-1.5-pro',
               temperature: float = 0.8, top_p: float = 0.85, **kwargs) -> 'GeminiClient':
        import google.genai as genai
        client = genai.Client(api_key=api_key)
        config = {
            'temperature': temperature,
            'top_p': top_p,
        }
        logging.info(f"Gemini client initialized (model={model})")
        return cls(client=client, model=model, config=config)
