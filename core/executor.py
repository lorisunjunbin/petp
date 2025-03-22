import wx
from threading import Thread
from threading import Condition
from mvp.presenter.event.PETPEvent import PETPEvent


class Executor(Thread):
    """
    Executor class that extends Thread. This class is responsible for executing execution in a new thread.
    """

    def __init__(self, execution, init_data, wx_comp):
        self.condition = Condition()
        self.execution = execution
        self.wx_comp = wx_comp
        self.init_data = init_data
        super().__init__(daemon=True, args=(self.condition,))

    def run(self):
        wx.PostEvent(self.wx_comp, PETPEvent(PETPEvent.START, [self.execution.execution, self.init_data]))
        data_chain = self.execution.run(self.init_data, self.condition, self.wx_comp)
        wx.PostEvent(self.wx_comp, PETPEvent(PETPEvent.DONE, [self.execution.execution, data_chain]))
