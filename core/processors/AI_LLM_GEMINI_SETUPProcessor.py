import logging
import os

from langchain_google_genai import ChatGoogleGenerativeAI, HarmCategory, HarmBlockThreshold

from core.processor import Processor

"""
REQUIREMENTS:

1. Install necessary packages:
   pip install langchain langchain-core langchain-google-genai google-generativeai pydantic

2. Pydantic Versioning:
   The error "ImportError: cannot import name 'validate_core_schema' from 'pydantic_core'"
   is often due to a mismatch or issue with Pydantic v2 and its interaction with
   langchain components. 
   
   Troubleshooting steps:
   a. Ensure `pydantic` and `pydantic-core` are compatible. Often, `pydantic-core` is a
      dependency of `pydantic`.
   b. Try reinstalling or upgrading `pydantic` and related `langchain` packages:
      pip uninstall pydantic pydantic-core langchain-core langchain-google-genai
      pip install pydantic langchain-core langchain-google-genai --upgrade
   c. If issues persist, check the specific versions of `langchain`, `langchain-core`, 
      `pydantic`, and `pydantic-core` required by `langchain-google-genai` and ensure 
      they are met. You might need to pin versions, e.g.:
      pip install pydantic>=2.0.0,<3.0.0 langchain-core>=0.1.40,<0.2.0

3. Environment Variables:
   Ensure your GOOGLE_API_KEY is correctly set in your environment.

"""


class AI_LLM_GEMINI_SETUPProcessor(Processor):
    TPL: str = '{"key_name_gemini":"GOOGLE_API_KEY", "model":"gemini-1.5-pro", "llm_data_key":"llmgemini","top_p":"0.85", "temperature":"0.8"}'

    DESC: str = f'''
        To setup LLM Gemini, a ChatGoogleGenerativeAI instance configured for the "gemini-1.5-pro" model with specific temperature, top_p, and safety settings,
        then save the llm instance to llm_data_key. 
        It requires the GOOGLE_API_KEY environment variable to be set.
        
        {TPL}
    '''

    def get_category(self) -> str:
        return super().CATE_AI_LLM

    def process(self):
        llm_data_key = self.get_param('llm_data_key')
        existed_llm = self.get_data(llm_data_key)

        if existed_llm is not None:
            logging.info(f'LLM Gemini ({llm_data_key}) already set up, skipping.')
            return

        key_name_gemini = self.get_param('key_name_gemini')

        if key_name_gemini not in os.environ:
            error_msg = f"Environment variable '{key_name_gemini}' not found. Please set your Google API key."
            logging.error(error_msg)
            raise EnvironmentError(error_msg)

        google_api_key = os.environ[key_name_gemini]
        model = self.get_param('model')

        try:
            top_p_str = self.get_param('top_p')
            temperature_str = self.get_param('temperature')

            top_p = float(top_p_str)
            temperature = float(temperature_str)

            llmgemini = ChatGoogleGenerativeAI(
                model=model,
                google_api_key=google_api_key,
                temperature=temperature,
                top_p=top_p,
                safety_settings={
                    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
                    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE
                }
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
