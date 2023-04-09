import wx

from threading import Thread
from threading import Condition

from mvp.presenter.event.PETPEvent import PETPEvent


class Executor(Thread):
    """New thread executor for execution"""
    execution: None
    wx_comp: None
    init_data: {}
    condition: Condition

    def __init__(self, execution, init_data, wx_comp):
        self.condition = Condition()
        self.execution = execution
        self.wx_comp = wx_comp
        self.init_data = init_data
        Thread.__init__(self, daemon=True, args=(self.condition,))

    def run(self):
        wx.PostEvent(self.wx_comp, PETPEvent(PETPEvent.START, f"{self.execution.execution} is START via new thread"))
        self.execution.run(self.init_data, self.condition, self.wx_comp)
        wx.PostEvent(self.wx_comp, PETPEvent(PETPEvent.DONE, f"{self.execution.execution} is DONE."))
