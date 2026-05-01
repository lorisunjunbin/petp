import json
import wx
from i18n.translations import t


class DataChainViewerDialog(wx.Dialog):
    """
    Non-modal dialog that shows live data_chain contents during execution.
    Refreshes every second via a wx.Timer while open.
    """

    _REFRESH_MS = 1000

    def __init__(self, parent, get_live_data_fn):
        super().__init__(
            parent, title=t("dlg_dc_viewer_title"),
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER | wx.STAY_ON_TOP,
        )
        self._get_live_data = get_live_data_fn

        self._build_ui()
        self.SetSize(680, 500)
        self.Centre()

        self._timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._on_timer, self._timer)
        self._timer.Start(self._REFRESH_MS)

        self._refresh()

    def _build_ui(self):
        sizer = wx.BoxSizer(wx.VERTICAL)

        toolbar = wx.BoxSizer(wx.HORIZONTAL)
        self._status = wx.StaticText(self, label="")
        self._status.SetForegroundColour(wx.Colour(100, 180, 255))
        toolbar.Add(self._status, 1, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 6)
        btn_copy = wx.Button(self, label=t("btn_dc_copy"), size=(70, 28))
        btn_copy.Bind(wx.EVT_BUTTON, self._on_copy)
        toolbar.Add(btn_copy, 0, wx.ALL, 4)
        sizer.Add(toolbar, 0, wx.EXPAND | wx.TOP, 4)

        self._text = wx.TextCtrl(
            self, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_DONTWRAP | wx.BORDER_NONE
        )
        self._text.SetBackgroundColour(wx.Colour(30, 30, 30))
        self._text.SetForegroundColour(wx.Colour(0, 200, 255))
        self._text.SetFont(wx.Font(11, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        sizer.Add(self._text, 1, wx.EXPAND | wx.ALL, 4)

        btn_close = wx.Button(self, wx.ID_CLOSE, t("btn_close"), size=(80, 28))
        btn_close.Bind(wx.EVT_BUTTON, lambda e: self._close())
        sizer.Add(btn_close, 0, wx.ALIGN_RIGHT | wx.ALL, 6)

        self.Bind(wx.EVT_CLOSE, lambda e: self._close())
        self.SetSizer(sizer)

    def _on_timer(self, evt):
        self._refresh()

    def _refresh(self):
        data = self._get_live_data()
        if data is None:
            self._status.SetLabel(t("dc_no_running"))
            return
        try:
            formatted = json.dumps(data, indent=2, ensure_ascii=False, default=str)
        except Exception:
            formatted = str(data)
        keys = len(data) if isinstance(data, dict) else '?'
        self._status.SetLabel(t("dc_keys_count").format(count=keys))
        pos = self._text.GetInsertionPoint()
        self._text.SetValue(formatted)
        self._text.SetInsertionPoint(pos)

    def _on_copy(self, evt):
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(wx.TextDataObject(self._text.GetValue()))
            wx.TheClipboard.Close()

    def _close(self):
        self._timer.Stop()
        self.Destroy()
