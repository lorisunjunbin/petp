import logging

from core.processor import Processor
from utils.SeleniumUtil import SeleniumUtil


class ENTER_FULLSCREENProcessor(Processor):
    TPL: str = '{"chrome_name":"chrome"}'
    DESC: str = f'''
        Make chrome browser fullscreen associated with chrome_name saved to data_chain.

        - chrome_name: key of data_chain where the chrome driver instance is stored (default: "chrome")

        {TPL}
    '''

    def get_category(self) -> str:
        return super().CATE_SELENIUM

    def process(self):
        if (self.has_data(self.get_param('chrome_name'))):
            chrome = self.get_data(self.get_param('chrome_name'))
            if SeleniumUtil.is_web_driver(chrome):
                SeleniumUtil.full_screen(chrome)
                logging.debug('Browser entered fullscreen')