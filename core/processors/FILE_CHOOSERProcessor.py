import time

import pyautogui
pyautogui.PAUSE = 0.5
pyautogui.FAILSAFE = False

import pyperclip

from core.processor import Processor
from utils.SeleniumUtil import SeleniumUtil

"""

pip install pyautogui

"""


class FILE_CHOOSERProcessor(Processor):
    TPL: str = '{"fileuploadby":"id|xpath", "identity":"", "file_path":"", "file_path_key":""}'

    DESC: str = '''
        Find the file upload element via selenium, then select the file to upload using system file chooser dialog.
        Supports unicode file names via copy-paste mechanism.

        - fileuploadby: locator type to find the upload element, "id" or "xpath"
        - identity: locator value for the upload element (supports expression)
        - file_path: the file path to upload (supports expression), used when file_path_key is not set
        - file_path_key: key of data_chain to get the file path, falls back to file_path param if not set
    '''
    def get_category(self) -> str:
        return super().CATE_FILE

    def process(self):
        chrome = self.get_data_by_param_default_data('chrome_name', 'chrome')
        fileuploadby = self.get_param('fileuploadby')
        identity = self.expression2str(self.get_param('identity'))
        filepath = self.get_data_by_param_default_param('file_path_key', 'file_path')
        ele = SeleniumUtil.get_element_by(chrome, fileuploadby, identity)

        try:
            SeleniumUtil.move_to_ele_then_click(chrome, ele)
        except:
            ele.click()

        time.sleep(2)
        pyperclip.copy(filepath)  # copy-paste for unicode file name.
        pyautogui.hotkey("ctrl", "v")
        pyautogui.press('enter')
