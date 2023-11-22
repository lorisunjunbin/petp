import time

import pyautogui
pyautogui.PAUSE = 0.5
pyautogui.FAILSAFE = False

from core.processor import Processor

"""

pip install pyautogui

"""


class MOUSE_CLICKProcessor(Processor):
    TPL: str = '{"x_from":"mouse_at_x","y_from":"mouse_at_y", "x":-1, "y":-1, "wait":5}'

    DESC: str = f'''
        To support mouse click on position(x,y)
        {TPL}
    '''

    def get_category(self) -> str:
        return super().CATE_MOUSE

    def process(self):

        x = self.get_param('x')
        y = self.get_param('y')

        if (x == -1 and y == -1) or (x is None and y is None):
            x_at = self.get_data(self.get_param('x_from'))
            y_at = self.get_data(self.get_param('y_from'))
            pyautogui.click(x=x_at, y=y_at)
        else:
            pyautogui.click(x=x, y=y)

        wait = self.get_param('wait')
        time.sleep(wait)
