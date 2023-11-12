import logging

import wx

from core.processor import Processor
from mvp.presenter.event.PETPEvent import PETPEvent


class INPUT_DIALOGProcessor(Processor):
    TPL: str = '{"title":" Message Input","msg":"","value_key":"","default_value":""}'

    DESC: str = f''' 
        DOES NOT WORKS, due to run execution in a new thread, try to figure out later.
        To collect user input via popup text entry dialog, save to data_chain. wx must run Dialog in MainThread, so should not use this processor as cron mode. 
        
        {TPL}
        
    '''

    def process(self):
        title = self.expression2str(self.get_param('title'))
        msg = self.expression2str(self.get_param('msg'))
        value_key = self.expression2str(self.get_param('value_key'))
        default_value = self.expression2str(self.get_param('default_value')) if self.has_param('default_value') else ''

        wx.PostEvent(self.get_view(), PETPEvent(PETPEvent.OPEN_INPUT_DIALOG,
                                                {"msg": msg, "title": title, "default_value": default_value},
                                                self.handle_ui_thread_callback))
        # 挂起当前线程，让UI主线程继续执行
        cond = self.get_condition()
        with cond:
            cond.wait()

        logging.debug(f'=========\n{self.get_data(value_key)}\n=============================')

    def handle_ui_thread_callback(self, given):
        value_key = self.expression2str(self.get_param('value_key'))
        self.populate_data(value_key, given)
        # 通知当前线程继续执行
        cond = self.get_condition()
        with cond:
            cond.notify()
