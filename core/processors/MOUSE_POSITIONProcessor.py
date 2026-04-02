import time

import logging

import pyautogui
pyautogui.PAUSE = 0.5
pyautogui.FAILSAFE = False

from core.processor import Processor

"""

pip install pyautogui

"""


class MOUSE_POSITIONProcessor(Processor):
    TPL: str = '{"data_key_x":"mouse_at_x", "data_key_y":"mouse_at_y", "wait":5}'

    DESC: str = f'''
        Get current mouse position (x, y), then save to data_chain via data_key_x and data_key_y.

        - data_key_x: key of data_chain to store the x coordinate (default: "mouse_at_x")
        - data_key_y: key of data_chain to store the y coordinate (default: "mouse_at_y")
        - wait: seconds to wait before reading mouse position (default: 5)

        {TPL}
    '''

    def get_category(self) -> str:
        return super().CATE_MOUSE

    def process(self):
        wait = self.get_param('wait')
        if not wait is None and wait > 0:
            time.sleep(wait)

        data_key_x = self.get_param('data_key_x')
        data_key_y = self.get_param('data_key_y')

        position = pyautogui.position()

        self.populate_data(data_key_x, position.x)
        self.populate_data(data_key_y, position.y)
        logging.debug(f'current mouse at [{position.x},{position.y}]')
