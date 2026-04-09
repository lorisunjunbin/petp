import json
import os

import wx


class ResultDialog(wx.Dialog):
    """Enhanced result dialog with scrollable monospace content,
    automatic JSON pretty-printing, and copy-to-clipboard."""

    def __init__(self, parent=None, title="", message=""):
        style = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
        super().__init__(parent, title="PETP - Message Box", style=style)

        self._display_msg = _format_message(message)
        self._build_ui(self._display_msg, title)
        self._try_set_icon()

        self.Fit()
        self.CentreOnScreen()

    # ------------------------------------------------------------------ #
    # UI construction
    # ------------------------------------------------------------------ #

    def _build_ui(self, message, title):
        PAD = 15
        sizer = wx.BoxSizer(wx.VERTICAL)

        # -- Header row: icon + title text --
        hdr = wx.BoxSizer(wx.HORIZONTAL)
        bmp = wx.ArtProvider.GetBitmap(wx.ART_INFORMATION,
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

        # -- Scrollable message area --
        txt_style = (wx.TE_MULTILINE | wx.TE_READONLY
                     | wx.TE_RICH2 | wx.HSCROLL)
        self._text = wx.TextCtrl(self, value=message, style=txt_style)
        self._text.SetFont(
            wx.Font(wx.FontInfo(13).Family(wx.FONTFAMILY_MODERN))
        )

        # Auto-size: taller for long content, clamped to sane bounds.
        lines = message.count('\n') + 1 if message else 1
        height = min(max(lines * 24 + 30, 160), 480)
        self._text.SetMinSize((520, height))

        sizer.Add(self._text, 1, wx.LEFT | wx.RIGHT | wx.EXPAND, PAD)

        # -- Button bar --
        btns = wx.BoxSizer(wx.HORIZONTAL)

        self._copy_btn = wx.Button(self, label="Copy")
        self._copy_btn.Bind(wx.EVT_BUTTON, self._on_copy)

        ok_btn = wx.Button(self, wx.ID_OK, "&OK")
        ok_btn.SetDefault()

        btns.AddStretchSpacer()
        btns.Add(self._copy_btn, 0, wx.RIGHT, 8)
        btns.Add(ok_btn)
        sizer.AddSpacer(PAD)
        sizer.Add(btns, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, PAD)

        self.SetSizer(sizer)
        self.SetMinSize((560, 320))

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

    def _on_copy(self, _evt):
        if wx.TheClipboard.Open():
            try:
                wx.TheClipboard.SetData(wx.TextDataObject(self._display_msg))
            finally:
                wx.TheClipboard.Close()


def _format_message(msg):
    """Pretty-print JSON strings; return everything else unchanged."""
    if not msg:
        return ""
    try:
        data = json.loads(msg)
        return json.dumps(data, indent=2, ensure_ascii=False)
    except (json.JSONDecodeError, TypeError, ValueError):
        return msg
