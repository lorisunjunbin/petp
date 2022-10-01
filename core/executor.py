import wx

from threading import Thread

from core.execution import Execution
from mvp.presenter.event.PETPEvent import PETPEvent


class Executor(Thread):
    """New thread executor for execution"""
    execution: Execution
    wx_comp: None
    init_data: {}

    def __init__(self, execution, init_data, wx_comp):
        Thread.__init__(self, daemon=True)
        self.execution = execution
        self.wx_comp = wx_comp
        self.init_data = init_data

    def run(self):
        self.execution.run(self.init_data)
        wx.PostEvent(self.wx_comp, PETPEvent(PETPEvent.DONE, f"{self.execution.execution} is DONE via other thread!"))
