import importlib
import importlib.util
import logging
import os
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class LLMResponse:
    content: str = ''
    reasoning_content: Optional[str] = None
    prompt_tokens: int = 0
    completion_tokens: int = 0


class RateLimitError(Exception):
    """Raised when an LLM call exhausts retries on HTTP 429 (Too Many Requests)."""


class BaseLLMClient(ABC):

    @abstractmethod
    def chat(self, messages: list, model: str, temperature: float, **kwargs) -> LLMResponse:
        ...

    @property
    @abstractmethod
    def provider_name(self) -> str:
        ...

    def chat_with_retry(self, messages: list, model: str, temperature: float,
                        max_retries: int = 3, base_delay: float = 2.0, **kwargs) -> LLMResponse:
        """Call ``chat`` with exponential backoff on rate-limit errors.

        Retries only on 429 / "rate limit" / "too many requests" style errors.
        Backoff: base_delay * 2**attempt (default 2s, 4s, 8s → 3 retries).
        On the final failure re-raises the underlying exception (or
        ``RateLimitError`` if it was a rate-limit).
        """
        last_err: Optional[Exception] = None
        for attempt in range(max_retries + 1):
            try:
                return self.chat(messages=messages, model=model, temperature=temperature, **kwargs)
            except Exception as e:
                if not _is_rate_limit_error(e):
                    raise
                last_err = e
                if attempt >= max_retries:
                    break
                delay = base_delay * (2 ** attempt)
                logging.warning("LLM rate limit hit (attempt %d/%d), retrying in %.1fs: %s",
                                attempt + 1, max_retries, delay, e)
                time.sleep(delay)
        raise RateLimitError(f"Rate limit exhausted after {max_retries} retries: {last_err}") from last_err

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


def _is_rate_limit_error(err: Exception) -> bool:
    """Heuristic: detect 429 / rate-limit errors across LLM SDKs.

    OpenAI SDK: ``openai.RateLimitError`` (class name check to avoid importing).
    Anthropic:  ``anthropic.RateLimitError``.
    Others:     inspect status_code attribute or error message.
    """
    cls_name = type(err).__name__
    if cls_name in ('RateLimitError', 'TooManyRequestsError'):
        return True
    status = getattr(err, 'status_code', None) or getattr(err, 'code', None)
    if status == 429 or status == '429':
        return True
    msg = str(err).lower()
    return '429' in msg or 'rate limit' in msg or 'too many requests' in msg

