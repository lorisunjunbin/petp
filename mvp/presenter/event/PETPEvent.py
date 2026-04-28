try:
    import wx
    _WX_AVAILABLE = True
except ImportError:
    _WX_AVAILABLE = False


if _WX_AVAILABLE:
    class PETPEvent(wx.PyEvent):
        """ available petp events"""
        LOG = 88880001
        DONE = 88880002
        START = 88880003
        OPEN_INPUT_DIALOG = 88880004
        HTTP_REQUEST = 88880005
        MATPLOTLIB = 88880006
        PIPELINE_STEP = 88880007

        def __init__(self, etype, data=None, handler=None):
            wx.PyEvent.__init__(self)
            self.SetEventType(etype)
            self.data = data
            self.handler = handler

        @staticmethod
        def bind_to(wxComp, etype, func):
            """Define Result Event."""
            wxComp.Connect(-1, -1, etype, func)

else:
    class PETPEvent:
        """Fallback stub used in no-GUI / background mode when wx is unavailable."""
        LOG = 88880001
        DONE = 88880002
        START = 88880003
        OPEN_INPUT_DIALOG = 88880004
        HTTP_REQUEST = 88880005
        MATPLOTLIB = 88880006
        PIPELINE_STEP = 88880007

        def __init__(self, etype, data=None, handler=None):
            self.etype = etype
            self.data = data
            self.handler = handler

        @staticmethod
        def bind_to(wxComp, etype, func):
            pass  # no-op in no-GUI mode

