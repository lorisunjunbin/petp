import logging
from core.processor import Processor
from utils.SeleniumUtil import SeleniumUtil


class WAIT_FORProcessor(Processor):
    TPL: str = '{"waitfor":"id|xpath|link|css", "identity":"", "identity_key":"", "timeout":200, "wait":1}'
    DESC: str = f'''
        Wait until a specific element appears on the page via selenium.

        - waitfor: locator type to find the element, "id", "xpath", "link" or "css"
        - identity: locator value for the target element
        - identity_key: key of data_chain to get the locator value, takes priority over identity if set
        - timeout: max seconds to wait for the element (default: 200)
        - wait: extra wait in seconds after element is found (default: 1)

        {TPL}
    '''
    def get_category(self) -> str:
        return super().CATE_GENERAL

    def process(self):
        chrome = self.get_data_by_param_default_data('chrome_name', 'chrome')

        waitfor = self.get_param('waitfor')
        timeout = int(self.expression2str(self.get_param('timeout')))
        identity = self.get_data(self.get_param('identity_key')) if self.has_param('identity_key') \
            else self.get_param('identity')

        ele = SeleniumUtil.get_element_by(chrome, waitfor, identity, timeout)
        super().extra_wait()
        logging.debug('wait for ele: ' + str(ele))