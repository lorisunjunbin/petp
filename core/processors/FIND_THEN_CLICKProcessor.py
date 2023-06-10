import logging

from core.processor import Processor
from utils.SeleniumUtil import SeleniumUtil


class FIND_THEN_CLICKProcessor(Processor):
    TPL: str = '{"clickby":"id|xpath|link|css", "identity":"","identity_key":"", "wait":5}'
    DESC: str = f'''
        {TPL}
    '''

    def process(self):

        super().process()

        chrome = self.get_data_by_param_default_data('chrome_name', 'chrome')
        clickby = self.get_param('clickby')
        identity = self.get_data(self.get_param('identity_key')) if self.has_param('identity_key') \
            else self.get_param('identity')
        ele = self.get_element_by(chrome, clickby, identity)

        super().extra_wait()

        try:
            SeleniumUtil.move_to_ele_then_click(chrome, ele)
            # ele.click()
            logging.info('click: ' + identity)
        except Exception as ex:
            logging.info('move to click: ' + identity)
