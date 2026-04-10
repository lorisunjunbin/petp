import os

import wx


class InputDialog(wx.Dialog):
    """Input dialog with scrollable multi-line text entry,
    header row with icon, and OK / Cancel buttons."""

    def __init__(self, parent=None, title="", message="", default_value=""):
        style = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
        super().__init__(parent, title="PETP - Input", style=style)

        self.value = default_value
        self._build_ui(title, message, default_value)
        self._try_set_icon()

        self.Fit()
        self.CentreOnScreen()

    # ------------------------------------------------------------------ #
    # UI construction
    # ------------------------------------------------------------------ #

    def _build_ui(self, title, message, default_value):
        PAD = 15
        sizer = wx.BoxSizer(wx.VERTICAL)

        # -- Header row: icon + title text --
        hdr = wx.BoxSizer(wx.HORIZONTAL)
        bmp = wx.ArtProvider.GetBitmap(wx.ART_QUESTION,
                                       wx.ART_MESSAGE_BOX, (36, 36))
        hdr.Add(wx.StaticBitmap(self, bitmap=bmp),
                0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)

        lbl = wx.StaticText(self, label=title)
        lbl.SetFont(lbl.GetFont().Bold().Scaled(1.4))
        hdr.Add(lbl, 1, wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(hdr, 0, wx.LEFT | wx.TOP | wx.RIGHT, PAD)

        sizer.AddSpacer(PAD // 2)
        sizer.Add(wx.StaticLine(self), 0, wx.LEFT | wx.RIGHT | wx.EXPAND, PAD)
        sizer.AddSpacer(PAD // 2)

        # -- Message label --
        if message:
            msg_label = wx.StaticText(self, label=message)
            sizer.Add(msg_label, 0, wx.LEFT | wx.RIGHT | wx.EXPAND, PAD)
            sizer.AddSpacer(PAD // 2)

        # -- Editable text area --
        txt_style = wx.TE_MULTILINE | wx.TE_RICH2 | wx.HSCROLL
        self._text = wx.TextCtrl(self, value=default_value, style=txt_style)
        self._text.SetFont(
            wx.Font(wx.FontInfo(13).Family(wx.FONTFAMILY_MODERN))
        )
        self._text.SetMinSize((520, 160))
        self._text.SetFocus()
        self._text.SelectAll()
        sizer.Add(self._text, 1, wx.LEFT | wx.RIGHT | wx.EXPAND, PAD)

        # -- Button bar --
        btns = wx.BoxSizer(wx.HORIZONTAL)

        cancel_btn = wx.Button(self, wx.ID_CANCEL, "&Cancel")
        ok_btn = wx.Button(self, wx.ID_OK, "&OK")
        ok_btn.SetDefault()
        ok_btn.Bind(wx.EVT_BUTTON, self._on_ok)

        btns.AddStretchSpacer()
        btns.Add(cancel_btn, 0, wx.RIGHT, 8)
        btns.Add(ok_btn)
        sizer.AddSpacer(PAD)
        sizer.Add(btns, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, PAD)

        self.SetSizer(sizer)
        self.SetMinSize((560, 380))

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #

    def _try_set_icon(self):
        icon_path = os.path.realpath(os.path.join('.', 'image', 'petp_small.png'))
        if os.path.isfile(icon_path):
            try:
                self.SetIcon(wx.Icon(icon_path))
            except Exception:
                pass

    def _on_ok(self, _evt):
        self.value = self._text.GetValue()
        self.EndModal(wx.ID_OK)

    def GetValue(self):
        return self.value

