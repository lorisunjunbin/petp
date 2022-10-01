import wx

class PETPEvent(wx.PyEvent):
    """ available petp events"""
    LOG = 88880001
    DONE = 88880002

    def __init__(self,etype, data):

        wx.PyEvent.__init__(self)
        self.SetEventType(etype)
        self.data = data

    @staticmethod
    def bind_to(wxComp, etype, func):
        """Define Result Event."""
        wxComp.Connect(-1, -1, etype, func)

