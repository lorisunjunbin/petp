import logging
import time
import pyautogui
pyautogui.PAUSE = 0.5
pyautogui.FAILSAFE = False

from core.processor import Processor

"""

pip install pyautogui

"""


class MOUSE_SCROLLProcessor(Processor):
    TPL: str = '{"x_from":"mouse_at_x","y_from":"mouse_at_y", "x":-1, "y":-1, "vertical":10, "wait":5}'

    DESC: str = '''
        Perform mouse scroll at position (x, y) with given vertical amount. If x and y are both -1, uses position from data_chain (x_from, y_from).

        - x_from: key of data_chain for stored x position when x is -1 (default: "mouse_at_x")
        - y_from: key of data_chain for stored y position when y is -1 (default: "mouse_at_y")
        - x: scroll x coordinate, set -1 to use position from data_chain (default: -1)
        - y: scroll y coordinate, set -1 to use position from data_chain (default: -1)
        - vertical: scroll amount, positive for up, negative for down (default: 10)
        - wait: seconds to wait after scrolling (default: 5)
    '''

    def get_category(self) -> str:
        return super().CATE_MOUSE

    def process(self):
        x = int(self.expression2str(self.get_param('x')))
        y = int(self.expression2str(self.get_param('y')))
        vertical = int(self.expression2str(self.get_param('vertical')))

        if (x == -1 and y == -1) or (x is None and y is None):
            x_at = self.get_data(self.get_param('x_from'))
            y_at = self.get_data(self.get_param('y_from'))
            pyautogui.scroll(vertical, x=x_at, y=y_at)
            logging.debug('Mouse scrolled %s at (%s, %s)', vertical, x_at, y_at)
        else:
            pyautogui.scroll(vertical, x=x, y=y)
            logging.debug('Mouse scrolled %s at (%s, %s)', vertical, x, y)

        wait = int(self.expression2str(self.get_param('wait')))
        time.sleep(wait)
