import wx

from core.processor import Processor
from mvp.presenter.event.PETPEvent import PETPEvent


class RELOAD_LOGProcessor(Processor):
    TPL: str = '{"name":"reload logger"}'

    DESC: str = f''' 
        Trigger a refresh of the log window in the PETP UI to display the latest log entries.
        Useful after a series of tasks to ensure the log view is up to date.

        - name: A descriptive label for this task step (supports expression, default: "reload logger")

        {TPL}
    '''

    def get_category(self) -> str:
        return super().CATE_GUI

    def process(self):
        wx.PostEvent(self.view, PETPEvent(PETPEvent.LOG))
