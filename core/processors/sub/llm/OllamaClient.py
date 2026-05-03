import logging

from core.processors.sub.llm.BaseLLMClient import BaseLLMClient, LLMResponse


class OllamaClient(BaseLLMClient):

    def __init__(self):
        import ollama
        self._ollama = ollama

    @property
    def provider_name(self) -> str:
        return 'ollama'

    def chat(self, messages: list, model: str, temperature: float, **kwargs) -> LLMResponse:
        response = self._ollama.chat(model=model, messages=messages, stream=False)
        content = response.message.content
        return LLMResponse(content=content)

    @classmethod
    def create(cls, provider: str, **kwargs) -> 'OllamaClient':
        logging.info("Ollama client initialized (local, no auth required)")
        return cls()
