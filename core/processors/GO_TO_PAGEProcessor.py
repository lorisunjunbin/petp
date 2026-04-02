import logging

from core.processor import Processor
from utils.SeleniumUtil import SeleniumUtil


class GO_TO_PAGEProcessor(Processor):
    TPL: str = '{"page_load_timeout_seconds":"180","url":"required", "url_key":"", "chrome_name":"chrome","skip_in_pipeline":"no", "download_folder":""}'
    DESC: str = f'''
        Launch chrome browser via selenium and navigate to a specific URL. Usually the first task of web-related execution.

        - page_load_timeout_seconds: max seconds to wait for page load (default: "180")
        - url: target URL to navigate to (required)
        - url_key: key of data_chain to get the URL, takes priority over url if set
        - chrome_name: key of data_chain to store the chrome driver instance (default: "chrome")
        - skip_in_pipeline: "yes" to skip this task when running in pipeline (default: "no")
        - download_folder: folder path for chrome downloads (optional, supports expression)

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
        page_load_timeout_seconds = int(self.get_param('page_load_timeout_seconds')) \
            if self.has_param('page_load_timeout_seconds') else 180

        url = self.get_data_by_param_default_param("url_key", "url")
        chrome = SeleniumUtil.get_page_from_url(url, download_folder=download_folder, page_load_timeout=page_load_timeout_seconds)

        if self.has_param('chrome_name'):
            self.populate_data(self.get_param('chrome_name'), chrome)
        else:
            self.populate_data('chrome', chrome)
