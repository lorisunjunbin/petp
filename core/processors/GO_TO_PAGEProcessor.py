import logging


from core.processor import Processor
from utils.SeleniumUtil import SeleniumUtil


class GO_TO_PAGEProcessor(Processor):
    TPL: str = '{"url":"required", "url_key":"", "chrome_name":"chrome","skip_in_pipeline":"no"}'
    DESC: str = f''' 
        - Call selenium to launch chrome browser and visit specific URL, usually it's the first task of web  relevant execution.   

        {TPL}

    '''
    def process(self):

        if super().need_skip():
            logging.info('skipped this task: GO_TO_PAGE')
            return

        url = self.get_data_by_param_default_param("url_key", "url")
        chrome = SeleniumUtil.get_page_from_url(url)

        if self.has_param('chrome_name'):
            self.populate_data(self.get_param('chrome_name'), chrome)
        else:
            self.populate_data('chrome', chrome)
