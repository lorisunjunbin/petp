"""Hyperspace LLM client.

Hyperspace is a local HTTP proxy that speaks the Anthropic ``/messages``
protocol. The Anthropic SDK internally appends ``/v1/messages`` to its
``base_url``, so the base_url passed here must NOT include ``/v1`` —
we point it at ``http://localhost:6655/anthropic`` and the SDK finalises
the URL as ``http://localhost:6655/anthropic/v1/messages``.

Bearer-token auth, model names must carry the ``anthropic--`` prefix
(e.g. ``anthropic--claude-sonnet-latest``).

Implementation strategy: reuse the ``anthropic`` SDK by pointing it at the
proxy base_url and passing the API key as ``auth_token`` — the same pattern
``AnthropicClient`` already uses for corporate proxy scenarios. This keeps
the request/response shape and streaming logic identical to Anthropic without
maintaining a parallel HTTP path.

See ``hyperspace_llm_guide.md`` for the underlying protocol.
"""

import logging

from core.processors.sub.llm.BaseLLMClient import BaseLLMClient, LLMResponse


class HyperspaceClient(BaseLLMClient):

    # NOTE: no ``/v1`` suffix — the anthropic SDK appends it internally.
    DEFAULT_BASE_URL: str = 'http://localhost:6655/anthropic'
    DEFAULT_MODEL: str = 'anthropic--claude-sonnet-latest'
    DEFAULT_MAX_TOKENS: int = 4096

    def __init__(self, client, model: str):
        self._client = client
        self._model = model

    @property
    def provider_name(self) -> str:
        return 'hyperspace'

    def chat(self, messages: list, model: str, temperature: float, **kwargs) -> LLMResponse:
        use_model = model or self._model
        max_tokens = int(kwargs.get('max_tokens') or self.DEFAULT_MAX_TOKENS)

        system_text = ''
        api_messages = []
        for msg in messages:
            if msg.get('role') == 'system':
                system_text += msg.get('content', '') + '\n'
            else:
                api_messages.append({'role': msg.get('role', 'user'), 'content': msg.get('content', '')})

        params = dict(model=use_model, messages=api_messages, max_tokens=max_tokens, temperature=temperature)
        if system_text.strip():
            params['system'] = system_text.strip()

        response = self._client.messages.create(**params)

        content = ''
        reasoning = ''
        for block in response.content:
            if block.type == 'thinking':
                reasoning += block.thinking
            elif block.type == 'text':
                content += block.text

        return LLMResponse(
            content=content,
            reasoning_content=reasoning or None,
            prompt_tokens=getattr(response.usage, 'input_tokens', 0) if hasattr(response, 'usage') else 0,
            completion_tokens=getattr(response.usage, 'output_tokens', 0) if hasattr(response, 'usage') else 0,
        )

    @classmethod
    def create(cls, provider: str, api_key: str = '', base_url: str = '',
               model: str = '', **kwargs) -> 'HyperspaceClient':
        import anthropic
        effective_base_url = base_url or cls.DEFAULT_BASE_URL
        effective_model = model or cls.DEFAULT_MODEL
        client = anthropic.Anthropic(base_url=effective_base_url, auth_token=api_key)
        logging.info(f"Hyperspace client initialized (model={effective_model}, base_url={effective_base_url})")
        return cls(client=client, model=effective_model)
