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
        ollama_messages = []
        for msg in messages:
            m = dict(msg)
            if isinstance(m.get('content'), list):
                text_parts = []
                images = []
                for part in m['content']:
                    if isinstance(part, dict):
                        if part.get('type') == 'text':
                            text_parts.append(part.get('text', ''))
                        elif part.get('type') == 'image':
                            images.append(part.get('path', ''))
                m['content'] = '\n'.join(text_parts)
                if images:
                    m['images'] = images
            ollama_messages.append(m)

        response = self._ollama.chat(model=model, messages=ollama_messages, stream=False)
        content = response.message.content
        return LLMResponse(content=content)

    @classmethod
    def create(cls, provider: str, **kwargs) -> 'OllamaClient':
        logging.info("Ollama client initialized (local, no auth required)")
        return cls()
