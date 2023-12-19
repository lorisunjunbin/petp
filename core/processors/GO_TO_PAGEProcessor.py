import logging

from core.processor import Processor
from utils.SeleniumUtil import SeleniumUtil


class GO_TO_PAGEProcessor(Processor):
    TPL: str = '{"url":"required", "url_key":"", "chrome_name":"chrome","skip_in_pipeline":"no", "download_folder":""}'
    DESC: str = f''' 
        - Call selenium to launch chrome browser and visit specific URL, usually it's the first task of web  relevant execution.   

        {TPL}

    '''

    def get_category(self) -> str:
        return super().CATE_SELENIUM

    def process(self):

        if super().need_skip():
            logging.debug('skipped this task: GO_TO_PAGE')
            return

        download_folder = self.expression2str(self.get_param('download_folder')) \
            if self.has_param('download_folder') else None

        url = self.get_data_by_param_default_param("url_key", "url")
        chrome = SeleniumUtil.get_page_from_url(url, download_folder=download_folder)

        if self.has_param('chrome_name'):
            self.populate_data(self.get_param('chrome_name'), chrome)
        else:
            self.populate_data('chrome', chrome)
