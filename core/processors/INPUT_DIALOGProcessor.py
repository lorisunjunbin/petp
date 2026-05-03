import json
import logging
import threading

try:
    import wx
except ImportError:
    wx = None

from core.processor import Processor


class INPUT_DIALOGProcessor(Processor):
    TPL: str = '{"title":"Message Input","msg":"","value_key":"","default_value":"","stop_on_cancel":"yes"}'

    DESC: str = '''
        Display a popup text entry dialog to collect user input at runtime, then store the entered value in the data chain.
        Supports stopping the execution if the user cancels the dialog.

        - title: title of the input dialog window (supports expression, default: "Message Input")
        - msg: message shown above the text entry field (supports expression, default: "")
        - value_key: data chain key to store the entered value (supports expression, default: "")
        - default_value: pre-filled default text in the input field (supports expression, default: "")
        - stop_on_cancel: if "yes", stop execution when user cancels; if "no", continue (default: "yes")
    '''

    def get_category(self) -> str:
        return super().CATE_GUI

    def process(self):
        title = self.expression2str(self.get_param('title'))
        msg = self.expression2str(self.get_param('msg'))
        value_key = self.expression2str(self.get_param('value_key'))
        default_value = self.explain_param_or_default('default_value', '')
        stop_on_cancel = self.get_param('stop_on_cancel') == 'yes'

        existing = self.get_data(value_key) if value_key else None
        if existing is not None:
            default_value = existing

        if self.view is not None and wx is not None:
            done = threading.Event()
            result = [None, False]
            wx.CallAfter(self._show_on_main_thread, title, msg, default_value, result, done)
            done.wait()
        else:
            if existing is not None:
                logging.info(f"[INPUT_DIALOG] BG mode: key '{value_key}' already has value '{existing}', skip overwrite")
                result = [existing, False]
            else:
                logging.info(f"[Notification] INPUT_DIALOGProcessor: title={title}, msg={msg}, default_value={default_value}")
                result = [default_value, False]

        if result[0] is None and stop_on_cancel:
            self.execution.set_should_be_stop(True)
        else:
            self.populate_data(value_key, result[0])

        if result[1] is not False and self.view is not None and wx is not None:
            self._save_as_default(result[1])

        logging.debug(f'INPUT_DIALOG result: {result[0]}')

    def _save_as_default(self, new_default_value):
        from mvp.presenter.event.PETPEvent import PETPEvent
        input_dict = json.loads(self.task.input)
        input_dict['default_value'] = new_default_value
        new_input = json.dumps(input_dict, ensure_ascii=False)
        self.task.input = new_input
        row = self.task.run_sequence - 1
        wx.PostEvent(self.view, PETPEvent(PETPEvent.SYNC_TASK_INPUT, {
            "row": row,
            "input": new_input,
        }))

    @staticmethod
    def _show_on_main_thread(title, msg, default_value, result, done_event):
        from mvp.view.common.InputDialog import InputDialog
        dlg = InputDialog(None, title=title, message=msg, default_value=default_value)
        if dlg.ShowModal() == wx.ID_OK:
            result[0] = dlg.GetValue()
        if dlg.save_as_default:
            result[1] = dlg.saved_default_value
        dlg.Destroy()
        done_event.set()
