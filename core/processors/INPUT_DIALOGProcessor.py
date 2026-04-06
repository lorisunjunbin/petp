import logging

try:
    import wx
except ImportError:
    wx = None

from core.processor import Processor
from mvp.presenter.event.PETPEvent import PETPEvent


class INPUT_DIALOGProcessor(Processor):
    TPL: str = '{"title":" Message Input","msg":"","value_key":"","default_value":"","stop_on_cancel":"yes"}'

    DESC: str = f''' 
        Display a popup text entry dialog to collect user input at runtime, then store the entered value in the data chain.
        Must run on the main UI thread (wx requirement), so this processor should NOT be used in cron mode.
        Supports stopping the execution if the user cancels the dialog.

        - title: The title displayed on the input dialog window (supports expression, default: " Message Input")
        - msg: The message or label shown above the text entry field (supports expression, default: "")
        - value_key: The data chain key under which the user-entered value will be stored (supports expression, default: "")
        - default_value: The pre-filled default text in the input field (supports expression, default: "")
        - stop_on_cancel: If "yes", stop the entire execution when the user cancels the dialog; if "no", continue (default: "yes")

        {TPL}
        
    '''

    def get_category(self) -> str:
        return super().CATE_GUI

    def process(self):
        title = self.expression2str(self.get_param('title'))
        msg = self.expression2str(self.get_param('msg'))
        value_key = self.expression2str(self.get_param('value_key'))
        default_value = self.expression2str(self.get_param('default_value')) if self.has_param('default_value') else ''

        if wx is not None:
            wx.PostEvent(self.get_view(), PETPEvent(PETPEvent.OPEN_INPUT_DIALOG,
                                                {"msg": msg, "title": title, "default_value": default_value},
                                                self.handle_ui_thread_callback))
        else:
            logging.info(f"[Notification] INPUT_DIALOGProcessor: title={title}, msg={msg}, default_value={default_value}")
        # 挂起当前线程，让UI主线程继续执行
        cond = self.get_condition()
        with cond:
            cond.wait()

        logging.debug(f'=========\n{self.get_data(value_key)}\n=============================')

    def handle_ui_thread_callback(self, given):
        stop_on_cancel = True if self.get_param('stop_on_cancel') == 'yes' else False
        if given is None and stop_on_cancel:
            self.execution.set_should_be_stop(True)
        else:
            value_key = self.expression2str(self.get_param('value_key'))
            self.populate_data(value_key, given)
        # 通知当前线程继续执行
        cond = self.get_condition()
        with cond:
            cond.notify()
