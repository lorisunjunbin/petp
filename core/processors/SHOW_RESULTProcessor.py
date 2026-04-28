import logging
import threading

try:
    import wx
except ImportError:
    wx = None

from core.processor import Processor


class SHOW_RESULTProcessor(Processor):
    TPL: str = '{"title":"","msg":""}'

    DESC: str = f'''
        Display a message in a rich popup dialog (ResultDialog).
        Also logs the title and message to the console.

        - title: title of the popup dialog window (supports expression, default: "")
        - msg: message content displayed in the popup dialog (supports expression, default: "")

        {TPL}
    '''

    def get_category(self) -> str:
        return super().CATE_GUI

    def process(self):
        title = self.expression2str(self.get_param('title'))
        task_number = getattr(self.task, 'run_sequence', None)
        if task_number is not None:
            title = f"Task {task_number} - {title}" if title else f"Task {task_number}"
        msg = self.expression2str(self.get_param('msg'))

        logging.info('[SHOW_RESULT] %s', title)
        logging.debug('[SHOW_RESULT] %s\n%s', title, msg)
        if self.view is not None and wx is not None:
            # wx.Dialog must be created on the main thread (macOS requirement).
            # Use wx.CallAfter to delegate, and block this worker thread
            # until the user dismisses the dialog.
            done = threading.Event()
            wx.CallAfter(self._show_on_main_thread, title, msg, done)
            done.wait()
        else:
            logging.info(f"[Notification] {title}: {msg}")

    @staticmethod
    def _show_on_main_thread(title, msg, done_event):
        from mvp.view.common.ResultDialog import ResultDialog
        dlg = ResultDialog(None, title=title, message=msg)
        dlg.ShowModal()
        dlg.Destroy()
        done_event.set()
