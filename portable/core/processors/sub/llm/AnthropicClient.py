import logging

from core.processors.sub.llm.BaseLLMClient import BaseLLMClient, LLMResponse


class AnthropicClient(BaseLLMClient):
    """Anthropic Messages-protocol client.

    Also used by any provider that exposes the Anthropic ``/v1/messages``
    protocol through a compatible base_url — e.g. Hyperspace's local proxy
    and Zhipu's ``https://open.bigmodel.cn/api/anthropic`` endpoint. The
    concrete provider name is captured at ``create()`` time so the token
    log distinguishes them.
    """

    DEFAULT_MAX_TOKENS: int = 4096

    def __init__(self, client, model: str, provider: str = 'anthropic'):
        self._client = client
        self._model = model
        self._provider = provider

    @property
    def provider_name(self) -> str:
        return self._provider

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
    def create(cls, provider: str, api_key: str = '', base_url: str = '', model: str = 'claude-sonnet-4-20250514', **kwargs) -> 'AnthropicClient':
        import anthropic
        params = {}
        if base_url:
            params['base_url'] = base_url
            params['auth_token'] = api_key
        else:
            params['api_key'] = api_key
        client = anthropic.Anthropic(**params)
        logging.info(f"Anthropic client initialized (provider={provider}, model={model}, base_url={base_url or 'default'})")
        return cls(client=client, model=model, provider=provider or 'anthropic')
