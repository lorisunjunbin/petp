import logging
import os

from core.processor import Processor
from utils.OSUtils import OSUtils
from utils.SeleniumUtil import SeleniumUtil


class SCREENSHOTProcessor(Processor):
    TPL: str = '{"xpath":"", "padding":0, "crop":"left|>top|>right|>bottom", "format":"png", "show":"yes|no", "file_path":"", "file_path_key":"", "data_key":"", "wait":3, "chrome_name":"chrome"}'
    DESC: str = '''
        Take a screenshot of the web page via selenium. Supports full page, element by xpath, or cropped region.

        - xpath: xpath to locate a specific element to screenshot using getBoundingClientRect (optional)
        - padding: extra pixels to expand around the xpath element on all sides (default: 0)
        - crop: crop region as "left|>top|>right|>bottom" absolute pixel values (optional); takes priority over xpath
        - format: image format, e.g. "png" (default: "png")
        - show: "yes" to open the screenshot after taking it (default: "no")
        - file_path: file path to save the screenshot (supports expression)
        - file_path_key: key of data_chain to get the file path; takes priority over file_path if set
        - data_key: key of data_chain to store the saved screenshot file path
        - wait: extra wait in seconds before taking screenshot (default: 3)
        - chrome_name: key of data_chain where the chrome driver is stored (default: "chrome")
    '''

    def get_category(self) -> str:
        return super().CATE_SELENIUM

    def process(self):
        chrome = self.get_data_by_param_default_data('chrome_name', 'chrome')
        fmt = self.explain_param_or_default('format', 'png')
        fp = self.get_data(self.get_param('file_path_key')) if self.has_param('file_path_key') \
            else self.expression2str(self.get_param('file_path'))
        show = self.has_param('show') and self.get_param('show') == 'yes'
        super().extra_wait()

        OSUtils.create_folder_if_not_existed(os.path.dirname(fp))

        fp_tmp = os.path.splitext(fp)[0] + '_tmp.' + fmt

        if self.has_param('crop'):
            arr = self.get_param('crop').split(self.SEPARATOR)
            SeleniumUtil.screenshot_with_crop(
                chrome, int(arr[0]), int(arr[1]), int(arr[2]), int(arr[3]),
                fp, fp_tmp, show, fmt
            )
        elif self.has_param('xpath'):
            padding = int(self.get_param('padding')) if self.has_param('padding') else 0
            SeleniumUtil.screenshot_by_x_path(chrome, self.get_param('xpath'), fp, fp_tmp, padding)
            if show:
                from PIL import Image
                Image.open(fp).show()
        else:
            SeleniumUtil.full_screenshot(chrome, fp)

        logging.info('Screenshot saved: %s', fp)
        self.populate_data(self.get_param('data_key'), fp)
