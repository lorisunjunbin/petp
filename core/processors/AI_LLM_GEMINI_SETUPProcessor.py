import logging
import os

from langchain_google_genai import ChatGoogleGenerativeAI, HarmCategory, HarmBlockThreshold

from core.processor import Processor

"""
REQUIREMENTS:

pip install langchain
pip install langchain-google-genai
pip install generativeai


"""


class AI_LLM_GEMINI_SETUPProcessor(Processor):
    TPL: str = '{"key_name_gemini":"GOOGLE_API_KEY", "model":"gemini-1.5-pro", "llm_data_key":"llmgemini","top_p":"0.85", "temperature":"0.8"}'

    DESC: str = f'''
        To setup LLM Gemini, a ChatGoogleGenerativeAI instance configured for the "gemini-1.5-pro" model with specific temperature, top_p, and safety settings,
        then save the llm instance to llm_data_key.
        
        {TPL}
    '''

    def get_category(self) -> str:
        return super().CATE_AI_LLM

    def process(self):
        llm_data_key = self.get_param('llm_data_key')
        existed_llm = self.get_data(llm_data_key)

        if existed_llm is not None:
            logging.info(f'LLM Gemini already setup, skip.')
            return

        key_name_gemini = self.get_param('key_name_gemini')
        model = self.get_param('model')
        top_p = self.get_param('top_p')
        temperature = self.get_param('temperature')
        llmgemini = ChatGoogleGenerativeAI(
            model=model,
            google_api_key=os.environ[key_name_gemini],
            temperature=float(temperature),
            top_p=float(top_p),
            safety_settings={
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,

                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE
            })

        self.populate_data(llm_data_key, llmgemini)
