import wx


class PETPEvent(wx.PyEvent):
    """ available petp events"""
    LOG = 88880001
    DONE = 88880002
    START = 88880003
    OPEN_INPUT_DIALOG = 88880004
    HTTP_REQUEST = 88880005
    MATPLOTLIB = 88880006

    def __init__(self, etype, data=None, handler=None):
        wx.PyEvent.__init__(self)
        self.SetEventType(etype)
        self.data = data
        self.handler = handler

    @staticmethod
    def bind_to(wxComp, etype, func):
        """Define Result Event."""
        wxComp.Connect(-1, -1, etype, func)
