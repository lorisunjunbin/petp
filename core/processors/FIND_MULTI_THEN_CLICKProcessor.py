import logging

from core.processor import Processor
from utils.CodeExplainerUtil import CodeExplainerUtil
from utils.SeleniumUtil import SeleniumUtil


class FIND_MULTI_THEN_CLICKProcessor(Processor):
    TPL: str = '{"skip_fn":"return ele is None","findby":"xpath|css","identity":"", "wait":3, "timeout":10}'

    DESC = f'''
    Find multiple elements within 'timeout', then click on them one by one, between every click 'wait'.  

    {TPL}

    '''

    def get_category(self) -> str:
        return super().CATE_SELENIUM

    def process(self):
        chrome = self.get_data_by_param_default_data('chrome_name', 'chrome')
        findby = self.get_param('findby')

        skip_fn_body = self.expression2str(self.get_param('skip_fn')) \
            if self.has_param('skip_fn') and len(self.get_param('skip_fn')) > 0 \
            else None

        identity = self.expression2str(self.get_param('identity'))

        time_out = int(self.get_param('timeout')) if self.has_param('timeout') else 10

        super().extra_wait()

        elements = SeleniumUtil.get_elements(chrome, findby, identity, time_out)

        skip_fn = CodeExplainerUtil.create_and_execute_func('FIND_MULTI_THEN_CLICKProcessor_skip_fn', '(ele)',
                                                            skip_fn_body) if skip_fn_body else None
        for ele in elements:
            if skip_fn and skip_fn(ele):
                continue
            try:
                SeleniumUtil.move_to_ele_then_click(chrome, ele)
                logging.debug('click: ' + identity)
            except Exception as ex:
                logging.warning('move to click: ' + identity)
