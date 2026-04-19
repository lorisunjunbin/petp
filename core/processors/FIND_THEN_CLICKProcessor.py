import logging

from core.processor import Processor
from utils.SeleniumUtil import SeleniumUtil


class FIND_THEN_CLICKProcessor(Processor):
    TPL: str = '{"clickby":"id|xpath|link|css", "identity":"","identity_key":"", "wait":5, "timeout":5, "skip_timeout_error":"yes|no", "chrome_name":"chrome"}'

    DESC: str = f'''
        Find a web element via Selenium using the specified locator strategy and click it.
        If the element is not found within the timeout, an exception is raised unless skip_timeout_error is set.

        - clickby: locator strategy to find the element, one of "id", "xpath", "link", or "css" (default: "id|xpath|link|css")
        - identity: the locator value used to find the element (supports expression, default: "")
        - identity_key: key in data_chain whose value is used as the locator; takes precedence over identity (supports expression, default: "")
        - wait: seconds to wait before performing the click action (default: 5)
        - timeout: maximum seconds to wait for the element to appear (default: 5)
        - skip_timeout_error: whether to suppress the exception when element is not found; "yes" to skip, "no" to raise (default: "yes|no")

        {TPL}
    '''

    def get_category(self) -> str:
        return super().CATE_SELENIUM

    def process(self):

        super().process()

        chrome = self.get_data_by_param_default_data('chrome_name', 'chrome')
        clickby = self.get_param('clickby')
        identity = self.get_data(self.get_param('identity_key')) if self.has_param('identity_key') \
            else self.expression2str(self.get_param('identity'))

        timeout = int(self.get_param('timeout')) if self.has_param('timeout') else 200
        skip_timeout_error = 'yes' == self.get_param('skip_timeout_error') \
            if self.has_param("skip_timeout_error") else False

        super().extra_wait()

        ele = SeleniumUtil.get_element_by(chrome, clickby, identity, timeout)
        if ele is None:
            if skip_timeout_error:
                logging.warning(f'Find by {clickby} -> {identity} element timeout: {timeout}')
                return
            else:
                raise Exception(f'Find by {clickby} -> {identity} element timeout: {timeout}')

        try:
            ele.click()
            logging.debug('click: ' + identity)
        except Exception as ex:
            logging.warning('move to click: ' + identity)
            SeleniumUtil.move_to_ele_then_click(chrome, ele)
