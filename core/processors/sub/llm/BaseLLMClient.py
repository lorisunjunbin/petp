import importlib
import importlib.util
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class LLMResponse:
    content: str = ''
    reasoning_content: Optional[str] = None


class BaseLLMClient(ABC):

    @abstractmethod
    def chat(self, messages: list, model: str, temperature: float, **kwargs) -> LLMResponse:
        ...

    @property
    @abstractmethod
    def provider_name(self) -> str:
        ...

    @staticmethod
    def get_client_by_provider(provider: str, **kwargs) -> 'BaseLLMClient':
        provider_map = {
            'deepseek': 'OpenAICompatibleClient',
            'zhipu': 'OpenAICompatibleClient',
            'qianfan': 'OpenAICompatibleClient',
            'minimax': 'OpenAICompatibleClient',
            'doubao': 'OpenAICompatibleClient',
            'moonshot': 'OpenAICompatibleClient',
            'anthropic': 'AnthropicClient',
            'gemini': 'GeminiClient',
            'ollama': 'OllamaClient',
            'openai_compatible': 'OpenAICompatibleClient',
        }
        class_name = provider_map.get(provider)
        if class_name is None:
            raise ValueError(f"Unsupported LLM provider: '{provider}'. Supported: {list(provider_map.keys())}")

        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), f'{class_name}.py')
        spec = importlib.util.spec_from_file_location(class_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        clazz = getattr(module, class_name)
        return clazz.create(provider=provider, **kwargs)
