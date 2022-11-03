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
    TPL: str = '{"fileuploadby":"id|xpath", "identity":"", "filepath":"", "filepath_key":""}'

    DESC: str = f'''
        To select the file which will be uploaded.
        {TPL}
    '''

    def process(self):
        chrome = self.get_data_by_param_default_data('chrome_name', 'chrome')
        fileuploadby = self.get_param('fileuploadby')
        identity = self.expression2str(self.get_param('identity'))
        filepath = self.get_data_by_param_default_param('filepath_key', 'filepath')
        ele = self.get_element_by(chrome, fileuploadby, identity)

        try:
            SeleniumUtil.move_to_ele_then_click(chrome, ele)
        except:
            ele.click()

        time.sleep(2)
        pyperclip.copy(filepath)  # copy-paste for unicode file name.
        pyautogui.hotkey("ctrl", "v")
        pyautogui.press('enter')
