import logging
import threading

try:
    import wx
except ImportError:
    wx = None

from core.processor import Processor


class INPUT_DIALOGProcessor(Processor):
    TPL: str = '{"title":"Message Input","msg":"","value_key":"","default_value":"","stop_on_cancel":"yes"}'

    DESC: str = f'''
        Display a popup text entry dialog to collect user input at runtime, then store the entered value in the data chain.
        Supports stopping the execution if the user cancels the dialog.

        - title: title of the input dialog window (supports expression, default: "Message Input")
        - msg: message shown above the text entry field (supports expression, default: "")
        - value_key: data chain key to store the entered value (supports expression, default: "")
        - default_value: pre-filled default text in the input field (supports expression, default: "")
        - stop_on_cancel: if "yes", stop execution when user cancels; if "no", continue (default: "yes")

        {TPL}
    '''

    def get_category(self) -> str:
        return super().CATE_GUI

    def process(self):
        title = self.expression2str(self.get_param('title'))
        msg = self.expression2str(self.get_param('msg'))
        value_key = self.expression2str(self.get_param('value_key'))
        default_value = self.explain_param_or_default('default_value', '')
        stop_on_cancel = self.get_param('stop_on_cancel') == 'yes'

        if wx is not None:
            # wx.Dialog must be created on the main thread (macOS requirement).
            # Use wx.CallAfter to delegate, and block this worker thread
            # until the user dismisses the dialog.
            done = threading.Event()
            result = [None]  # mutable container for cross-thread result
            wx.CallAfter(self._show_on_main_thread, title, msg, default_value, result, done)
            done.wait()
        else:
            logging.info(f"[Notification] INPUT_DIALOGProcessor: title={title}, msg={msg}, default_value={default_value}")
            result = [default_value]

        if result[0] is None and stop_on_cancel:
            self.execution.set_should_be_stop(True)
        else:
            self.populate_data(value_key, result[0])

        logging.debug(f'INPUT_DIALOG result: {result[0]}')

    @staticmethod
    def _show_on_main_thread(title, msg, default_value, result, done_event):
        from mvp.view.common.InputDialog import InputDialog
        dlg = InputDialog(None, title=title, message=msg, default_value=default_value)
        if dlg.ShowModal() == wx.ID_OK:
            result[0] = dlg.GetValue()
        dlg.Destroy()
        done_event.set()
