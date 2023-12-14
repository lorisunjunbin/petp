import logging

from core.processor import Processor
from utils.SeleniumUtil import SeleniumUtil


class FIND_MULTI_THEN_CLICKProcessor(Processor):
    TPL: str = '{"findby":"xpath|css","identity":"", "wait":3, "timeout":10}'

    DESC = f'''
    Find multiple elements within 'timeout', then click on them one by one, between every click 'wait'.  

    {TPL}

    '''

    def get_category(self) -> str:
        return super().CATE_SELENIUM

    def process(self):
        chrome = self.get_data_by_param_default_data('chrome_name', 'chrome')
        findby = self.get_param('findby')

        identity = self.expression2str(self.get_param('identity'))

        time_out = int(self.get_param('timeout')) if self.has_param('timeout') else 10

        super().extra_wait()

        elements = SeleniumUtil.get_elements(chrome, findby, identity, time_out)

        for ele in elements:
            try:
                SeleniumUtil.move_to_ele_then_click(chrome, ele)
                logging.debug('click: ' + identity)
            except Exception as ex:
                logging.warning('move to click: ' + identity)
