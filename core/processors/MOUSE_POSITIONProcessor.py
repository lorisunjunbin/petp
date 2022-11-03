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
        To get mouse position(x,y), then bind to data_key_x and y
        {TPL}
    '''

    def process(self):
        wait = self.get_param('wait')
        if not wait is None and wait > 0:
            time.sleep(wait)

        data_key_x = self.get_param('data_key_x')
        data_key_y = self.get_param('data_key_y')

        position = pyautogui.position()

        self.populate_data(data_key_x, position.x)
        self.populate_data(data_key_y, position.y)
        logging.info(f'current mouse at [{position.x},{position.y}]')
