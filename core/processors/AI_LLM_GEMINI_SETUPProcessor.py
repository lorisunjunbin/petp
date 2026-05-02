import logging
import os
from dataclasses import dataclass
from typing import Any

import google.genai as genai

from core.processor import Processor

"""
REQUIREMENTS:

1. Install necessary packages:
   pip install google-genai

2. Environment Variables:
   Ensure your GOOGLE_API_KEY is correctly set in your environment.

"""


@dataclass
class GeminiInvokeResponse:
    content: str


class GeminiLLMClient:
    """Small adapter to keep existing `invoke(...).content` behavior."""

    def __init__(self, api_key: str, model: str, temperature: float, top_p: float):
        self.model = model
        self.client = genai.Client(api_key=api_key)
        self._config = {
            "temperature": temperature,
            "top_p": top_p,
        }

    def invoke(self, prompt: Any) -> GeminiInvokeResponse:
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=self._config,
        )
        text = getattr(response, "text", None)
        if text is None:
            text = str(response)
        return GeminiInvokeResponse(content=text)


class AI_LLM_GEMINI_SETUPProcessor(Processor):
    TPL: str = '{"api_key_env":"GOOGLE_API_KEY", "model":"gemini-1.5-pro", "llm_data_key":"llmgemini","top_p":"0.85", "temperature":"0.8"}'

    DESC: str = '''
        Initialize and configure a Google Gemini LLM instance with the specified model,
        temperature, and top_p, then store it in the data chain for use by downstream processors
        such as AI_LLM_GEMINI_QANDA_MCPProcessor. Requires the GOOGLE_API_KEY environment variable to be set.
        Skips setup if an LLM instance already exists for the given llm_data_key.

        - api_key_env: The environment variable name that holds the Google API key (default: "GOOGLE_API_KEY")
        - model: The Gemini model name to use (default: "gemini-1.5-pro")
        - llm_data_key: The data chain key under which the configured LLM instance will be stored (default: "llmgemini")
        - top_p: The top-p (nucleus) sampling parameter as a float string, controls diversity (default: "0.85")
        - temperature: The sampling temperature as a float string, higher values produce more creative output (default: "0.8")
    '''

    def get_category(self) -> str:
        return super().CATE_AI_LLM

    def process(self):
        llm_data_key = self.get_param('llm_data_key')
        existed_llm = self.get_data(llm_data_key)

        if existed_llm is not None:
            logging.info(f'LLM Gemini ({llm_data_key}) already set up, skipping.')
            return

        api_key_env = self.get_param('api_key_env')

        if api_key_env not in os.environ:
            error_msg = f"Environment variable '{api_key_env}' not found. Please set your Google API key."
            logging.error(error_msg)
            raise EnvironmentError(error_msg)

        google_api_key = os.environ[api_key_env]
        model = self.get_param('model')
        top_p_str = self.get_param('top_p')
        temperature_str = self.get_param('temperature')

        try:
            top_p = float(top_p_str)
            temperature = float(temperature_str)

            llmgemini = GeminiLLMClient(
                api_key=google_api_key,
                model=model,
                temperature=temperature,
                top_p=top_p,
            )
            self.populate_data(llm_data_key, llmgemini)
            logging.info(f"Successfully set up LLM Gemini (model: {model}) and stored in data key '{llm_data_key}'.")
        except ValueError as ve:
            error_msg = f"Error converting 'top_p' ('{top_p_str}') or 'temperature' ('{temperature_str}') to float: {ve}"
            logging.error(error_msg)
            raise ValueError(error_msg) from ve
        except Exception as e:
            error_msg = f"An error occurred during Gemini LLM (model: {model}) setup for data key '{llm_data_key}': {e}"
            logging.error(error_msg)
            # This could be an API error, invalid model name, etc.
            raise RuntimeError(error_msg) from e
