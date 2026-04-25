import logging
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
        Perform mouse click at position (x, y). If x and y are both -1, uses position from data_chain (x_from, y_from).

        - x_from: key of data_chain for stored x position when x is -1 (default: "mouse_at_x")
        - y_from: key of data_chain for stored y position when y is -1 (default: "mouse_at_y")
        - x: click x coordinate, set -1 to use position from data_chain (default: -1)
        - y: click y coordinate, set -1 to use position from data_chain (default: -1)
        - wait: seconds to wait after clicking (default: 5)

        {TPL}
    '''

    def get_category(self) -> str:
        return super().CATE_MOUSE

    def process(self):

        x = int(self.expression2str(self.get_param('x')))
        y = int(self.expression2str(self.get_param('y')))

        if (x == -1 and y == -1) or (x is None and y is None):
            x_at = self.get_data(self.get_param('x_from'))
            y_at = self.get_data(self.get_param('y_from'))
            pyautogui.click(x=x_at, y=y_at)
            logging.debug('Mouse clicked at (%s, %s)', x_at, y_at)
        else:
            pyautogui.click(x=x, y=y)
            logging.debug('Mouse clicked at (%s, %s)', x, y)

        wait = int(self.expression2str(self.get_param('wait')))
        time.sleep(wait)
