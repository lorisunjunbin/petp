import logging
import os

from core.processor import Processor
from core.processors.sub.llm.BaseLLMClient import BaseLLMClient


class AI_LLM_SETUPProcessor(Processor):
    TPL: str = '{"provider":"deepseek", "api_key_env":"", "api_key":"", "base_url":"", "model":"", "llm_data_key":"llm_client", "top_p":"0.85", "temperature":"0.8"}'

    DESC: str = '''
Set up a unified LLM client instance for any supported provider. The client is stored in the data_chain for use by AI_LLM_QANDA or AI_LLM_QANDA_MCP. Skips setup if the client already exists.

Supported providers: deepseek, zhipu, qianfan, minimax, anthropic, doubao, moonshot, gemini, ollama, openai_compatible

- provider: LLM provider name (default: "deepseek"), available providers: deepseek, zhipu, qianfan, minimax, anthropic, doubao, moonshot, gemini, ollama, openai_compatible
- api_key_env: Environment variable name holding the API key; ignored for ollama (supports expression, default: provider-specific)
- api_key: API key string; if provided, takes precedence over api_key_env (supports expression, default: "")
- base_url: API endpoint base URL; uses provider default if empty (supports expression, default: provider-specific)
- model: Model name; uses provider default if empty (supports expression, default: provider-specific)
- llm_data_key: Key in data_chain to store the initialized client (supports expression, default: "llm_client")
- top_p: Top-p sampling parameter, used by gemini (default: "0.85")
- temperature: Sampling temperature, used by gemini during setup (default: "0.8")
'''

    PROVIDER_DEFAULTS = {
        'deepseek': {
            'api_key_env': 'DEEPSEEK_API_KEY',
            'base_url': 'https://api.deepseek.com',
            'model': 'deepseek-chat',
        },
        'zhipu': {
            'api_key_env': 'ZHIPU_ACCESS_KEY',
            'base_url': 'https://open.bigmodel.cn/api/paas/v4/',
            'model': 'GLM-5',
        },
        'qianfan': {
            'api_key_env': 'QIANFAN_API_KEY',
            'base_url': 'https://qianfan.baidubce.com/v2',
            'model': 'ernie-4.5-8k',
        },
        'minimax': {
            'api_key_env': 'MINIMAX_API_KEY',
            'base_url': 'https://api.minimaxi.com/v1',
            'model': 'MiniMax-Text-01',
        },
        'anthropic': {
            'api_key_env': 'ANTHROPIC_API_KEY',
            'base_url': '',
            'model': 'claude-sonnet-4-20250514',
        },
        'doubao': {
            'api_key_env': 'DOUBAO_API_KEY',
            'base_url': 'https://ark.cn-beijing.volces.com/api/v3',
            'model': 'doubao-1.5-pro-32k',
        },
        'moonshot': {
            'api_key_env': 'MOONSHOT_API_KEY',
            'base_url': 'https://api.moonshot.cn/v1',
            'model': 'moonshot-v1-8k',
        },
        'gemini': {
            'api_key_env': 'GOOGLE_API_KEY',
            'base_url': '',
            'model': 'gemini-1.5-pro',
        },
        'ollama': {
            'api_key_env': '',
            'base_url': '',
            'model': 'deepseek-r1:7b',
        },
        'openai_compatible': {
            'api_key_env': 'OPENAI_API_KEY',
            'base_url': 'https://api.openai.com/v1',
            'model': 'gpt-4o',
        },
    }

    def get_category(self) -> str:
        return super().CATE_AI_LLM

    def process(self):
        llm_data_key = self.expression2str(self.get_param('llm_data_key'))

        if self.get_data(llm_data_key) is not None:
            logging.info(f'LLM client already set up at key "{llm_data_key}", skip.')
            return

        provider = self.expression2str(self.get_param('provider')).strip().lower()
        defaults = self.PROVIDER_DEFAULTS.get(provider, {})

        api_key_env = self.explain_param_or_default('api_key_env', defaults.get('api_key_env', ''))
        base_url = self.explain_param_or_default('base_url', defaults.get('base_url', ''))
        model = self.explain_param_or_default('model', defaults.get('model', ''))
        top_p = self.explain_param_as_float('top_p', 0.85)
        temperature = self.explain_param_as_float('temperature', 0.8)

        api_key = ''
        if self.has_param('api_key'):
            api_key = self.expression2str(self.get_param('api_key'))

        if not api_key and api_key_env:
            api_key = os.environ.get(api_key_env, '')

        if not api_key and provider not in ('ollama',):
            raise ValueError(
                f"No API key found. Set environment variable '{api_key_env}' or provide 'api_key' parameter.")

        client = BaseLLMClient.get_client_by_provider(
            provider=provider,
            api_key=api_key,
            base_url=base_url,
            model=model,
            temperature=temperature,
            top_p=top_p,
        )

        self.populate_data(llm_data_key, client)
        logging.info(f"LLM client set up: provider={provider}, model={model}, key='{llm_data_key}'")
