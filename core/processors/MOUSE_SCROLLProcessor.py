import time
import pyautogui

from core.processor import Processor

"""

pip install pyautogui

"""


class MOUSE_SCROLLProcessor(Processor):
    TPL: str = '{"x":10, "y":10, "vertical":-10, "wait":5}'

    DESC: str = f'''
        To support mouse scroll on position(x,y), vertical
        {TPL}
    '''

    def process(self):
        x = self.get_param('x')
        y = self.get_param('y')
        vertical = self.get_param('vertical')
        wait = self.get_param('wait')

        time.sleep(wait)
        pyautogui.scroll(vertical, x=x, y=y)
