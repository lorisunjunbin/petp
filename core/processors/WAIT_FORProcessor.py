import logging
from core.processor import Processor
from utils.SeleniumUtil import SeleniumUtil


class WAIT_FORProcessor(Processor):
    TPL: str = '{"waitfor":"id|xpath|link|css", "identity":"", "identity_key":"", "timeout":200, "wait":1}'
    DESC: str = f'''
        perform a certain waiting, [timeout] is for selenium wait and [wait] is time.sleep. 

        {TPL}
    '''
    def get_category(self) -> str:
        return super().CATE_GENERAL

    def process(self):
        chrome = self.get_data_by_param_default_data('chrome_name', 'chrome')

        waitfor = self.get_param('waitfor')
        timeout = self.get_param('timeout')
        identity = self.get_data(self.get_param('identity_key')) if self.has_param('identity_key') \
            else self.get_param('identity')

        ele = SeleniumUtil.get_element_by(chrome, waitfor, identity, timeout)
        super().extra_wait()
        logging.debug('wait for ele: ' + str(ele))