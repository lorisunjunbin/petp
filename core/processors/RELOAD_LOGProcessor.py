import wx

from core.processor import Processor
from mvp.presenter.event.PETPEvent import PETPEvent


class RELOAD_LOGProcessor(Processor):
    TPL: str = '{"name":"reload logger"}'

    DESC: str = f''' 
        Reload the log window to show latest logs.
        {TPL}
    '''

    def get_category(self) -> str:
        return super().CATE_GUI

    def process(self):
        wx.PostEvent(self.view, PETPEvent(PETPEvent.LOG))
