from core.processor import Processor
from utils.SeleniumUtil import SeleniumUtil


class SCREENSHOTProcessor(Processor):
    TPL: str = '{"xpath":"", "crop":"left;top;right;bottom","format":"png", "show":"yes|no", "filepath":"", "filepath_key":"","data_key":"","wait": 3}'
    DESC: str = f''' 
        - Make a web page screenshot via selenium within chrome, store image location to filepath_key of data_chain.

        {TPL}

    '''

    def get_category(self) -> str:
        return super().CATE_SELENIUM

    def process(self):
        chrome = self.get_data_by_param_default_data('chrome_name', 'chrome')
        format = 'png' if not self.has_param('format') else self.get_param('format')
        fp = self.get_data(self.get_param('filepath_key')) if self.has_param('filepath_key') \
            else self.expression2str(self.get_param('filepath'))
        fp_org = fp.replace('.', '_org.')
        show = False if not self.has_param('show') else 'yes' == self.get_param('show')
        super().extra_wait()

        if self.has_param("crop"):
            arr = self.get_param('crop').split(self.SEPARATOR)
            SeleniumUtil.screenshot_with_crop(chrome, int(arr[0]), int(arr[1]), int(arr[2]), int(arr[3]), fp, fp_org,
                                              show, format)
        # 这个方法crop的不准，少用！
        elif self.has_param('xpath'):
            SeleniumUtil.screenshot_by_x_path(chrome, self.get_param('xpath'), fp, fp_org)
        else:
            SeleniumUtil.full_screenshot(chrome, fp)

        self.populate_data(self.get_param("data_key"), fp)
