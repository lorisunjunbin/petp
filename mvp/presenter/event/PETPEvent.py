try:
    import wx
    _WX_AVAILABLE = True
except ImportError:
    _WX_AVAILABLE = False


_LOG = 88880001
_DONE = 88880002
_START = 88880003
_OPEN_INPUT_DIALOG = 88880004
_HTTP_REQUEST = 88880005
_MATPLOTLIB = 88880006
_PIPELINE_STEP = 88880007
_SYNC_TASK_INPUT = 88880008


if _WX_AVAILABLE:
    class PETPEvent(wx.PyEvent):
        LOG = _LOG
        DONE = _DONE
        START = _START
        OPEN_INPUT_DIALOG = _OPEN_INPUT_DIALOG
        HTTP_REQUEST = _HTTP_REQUEST
        MATPLOTLIB = _MATPLOTLIB
        PIPELINE_STEP = _PIPELINE_STEP
        SYNC_TASK_INPUT = _SYNC_TASK_INPUT

        def __init__(self, etype, data=None, handler=None):
            wx.PyEvent.__init__(self)
            self.SetEventType(etype)
            self.data = data
            self.handler = handler

        @staticmethod
        def bind_to(wxComp, etype, func):
            wxComp.Connect(-1, -1, etype, func)

else:
    class PETPEvent:
        LOG = _LOG
        DONE = _DONE
        START = _START
        OPEN_INPUT_DIALOG = _OPEN_INPUT_DIALOG
        HTTP_REQUEST = _HTTP_REQUEST
        MATPLOTLIB = _MATPLOTLIB
        PIPELINE_STEP = _PIPELINE_STEP
        SYNC_TASK_INPUT = _SYNC_TASK_INPUT

        def __init__(self, etype, data=None, handler=None):
            self.etype = etype
            self.data = data
            self.handler = handler

        @staticmethod
        def bind_to(wxComp, etype, func):
            pass
