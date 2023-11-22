from core.processor import Processor


class GO_BACKProcessor(Processor):
    TPL: str = '{"chrome_name":"chrome"}'

    def get_category(self) -> str:
        return super().CATE_SELENIUM

    def process(self):
        chrome = self.get_data_by_param_default_data('chrome_name', 'chrome')
        chrome.back()
