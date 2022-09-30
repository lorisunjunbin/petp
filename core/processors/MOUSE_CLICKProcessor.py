import time

import pyautogui

from core.processor import Processor

"""

pip install pyautogui

"""


class MOUSE_CLICKProcessor(Processor):
    TPL: str = '{"x":10, "y":10, "wait":5}'

    DESC: str = f'''
        To support mouse click on position(x,y)
        {TPL}
    '''

    def process(self):
        x = self.get_param('x')
        y = self.get_param('y')
        wait = self.get_param('wait')
        time.sleep(wait)

        pyautogui.click(x=x, y=y)
