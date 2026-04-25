import logging

from core.processor import Processor


class GO_BACKProcessor(Processor):
    TPL: str = '{"chrome_name":"chrome"}'

    DESC: str = f'''
        Navigate the chrome browser back to the previous page, equivalent to clicking the browser back button.

        - chrome_name: key of data_chain where the chrome driver instance is stored (default: "chrome")

        {TPL}
    '''

    def get_category(self) -> str:
        return super().CATE_SELENIUM

    def process(self):
        chrome = self.get_data_by_param_default_data('chrome_name', 'chrome')
        chrome.back()
        logging.debug('Browser navigated back')
