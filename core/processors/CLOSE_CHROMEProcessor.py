import logging

from core.processor import Processor
from utils.SeleniumUtil import SeleniumUtil


class CLOSE_CHROMEProcessor(Processor):
    TPL: str = '{"chrome_name":"chrome", "skip_in_pipeline":"no"}'
    DESC: str = '''
        Close existing chrome driver of data_chain according to given chrome_name. Able to skip when running in pipeline.

        - chrome_name: key of data_chain where the chrome driver instance is stored (default: "chrome")
        - skip_in_pipeline: set to "yes" to skip this task when running in pipeline (default: "no")
    '''

    def get_category(self) -> str:
        return super().CATE_SELENIUM

    def process(self):
        if super().need_skip():
            logging.debug('skipped this task: CLOSE_CHROME.')
            return

        if (self.has_data(self.get_param('chrome_name'))):
            chrome = self.get_data(self.get_param('chrome_name'))
            if SeleniumUtil.is_web_driver(chrome):
                chrome.close()
