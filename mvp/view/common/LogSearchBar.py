import sys

import wx

from mvp.view.theme import get_theme

_IS_WINDOWS = sys.platform == 'win32'
_ICON_SEARCH = "🔍"
_ICON_FILTER = "🔎"
_ICON = _ICON_SEARCH


def _blend(c1, c2, t=0.5):
    return (
        int(c1[0] + (c2[0] - c1[0]) * t),
        int(c1[1] + (c2[1] - c1[1]) * t),
        int(c1[2] + (c2[2] - c1[2]) * t),
    )


# ---------------------------------------------------------------------------
# Event
# ---------------------------------------------------------------------------

_EVT_LOG_BAR_TYPE = wx.NewEventType()
EVT_LOG_BAR = wx.PyEventBinder(_EVT_LOG_BAR_TYPE, 1)


class LogBarEvent(wx.PyCommandEvent):
    """Single event class for all LogSearchBar actions.

    action values:
      "search"     — text changed;          GetString() = current keyword
      "prev"       — navigate to prev match
      "next"       — navigate to next match
      "filter"     — filter toggle;         GetInt() = 1 active / 0 off
      "key_escape" — Escape pressed in search box
    """

    def __init__(self, action: str, source: wx.Window,
                 string: str = "", int_val: int = 0):
        super().__init__(_EVT_LOG_BAR_TYPE, source.GetId())
        self.SetEventObject(source)
        self.action = action
        self._string = string
        self._int = int_val

    def GetAction(self) -> str:
        return self.action

    def GetString(self) -> str:
        return self._string

    def GetInt(self) -> int:
        return self._int


# ---------------------------------------------------------------------------
# Internal button
# ---------------------------------------------------------------------------

class _NavBtn(wx.Control):
    """Compact navigation / toggle button that blends into the search bar."""

    def __init__(self, parent, label, toggle=False, **kwargs):
        super().__init__(parent, wx.ID_ANY, style=wx.BORDER_NONE, **kwargs)
        self._label = label
        self._hover = False
        self._pressed = False
        self._toggle = toggle
        self._active = False
        self.SetMinSize((26, 22))
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.Bind(wx.EVT_PAINT, self._on_paint)
        self.Bind(wx.EVT_ENTER_WINDOW, lambda e: self._set(hover=True))
        self.Bind(wx.EVT_LEAVE_WINDOW, lambda e: self._set(hover=False, pressed=False))
        self.Bind(wx.EVT_LEFT_DOWN, self._on_down)
        self.Bind(wx.EVT_LEFT_UP, self._on_up)
        self.Bind(wx.EVT_ERASE_BACKGROUND, lambda e: None)

    def SetLabel(self, label):
        self._label = label
        self.Refresh()

    def GetLabel(self):
        return self._label

    def IsActive(self):
        return self._active

    def SetActive(self, val: bool):
        self._active = val
        self.Refresh()

    def _set(self, **kw):
        for k, v in kw.items():
            setattr(self, f"_{k}", v)
        self.Refresh()

    def _on_down(self, _e):
        self._pressed = True
        self.CaptureMouse()
        self.Refresh()

    def _on_up(self, evt):
        if self.HasCapture():
            self.ReleaseMouse()
        was = self._pressed
        self._pressed = False
        self.Refresh()
        if was:
            r = self.GetClientRect()
            if r.Contains(evt.GetPosition()):
                if self._toggle:
                    self._active = not self._active
                    self.Refresh()
                ev = wx.CommandEvent(wx.wxEVT_BUTTON, self.GetId())
                ev.SetEventObject(self)
                self.GetEventHandler().ProcessEvent(ev)

    def _on_paint(self, _e):
        dc = wx.AutoBufferedPaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        if gc is None:
            return
        w, h = self.GetClientSize()
        th = get_theme()
        bg = self.GetParent().GetBackgroundColour()
        gc.SetBrush(wx.Brush(bg))
        gc.SetPen(wx.TRANSPARENT_PEN)
        gc.DrawRectangle(0, 0, w, h)

        if self._toggle and self._active:
            fill = wx.Colour(*_blend(th.log_bg, th.accent, 0.45))
            txt_colour = wx.Colour(*th.accent)
        elif self._pressed:
            fill = wx.Colour(*_blend(th.log_bg, th.accent, 0.5))
            txt_colour = wx.Colour(*th.log_search_fg)
        elif self._hover:
            fill = wx.Colour(*_blend(th.log_bg, th.accent, 0.25))
            txt_colour = wx.Colour(*th.log_search_fg)
        else:
            fill = wx.Colour(*th.log_bg)
            txt_colour = wx.Colour(*th.log_fg)

        r = 0 if _IS_WINDOWS else 5
        gc.SetBrush(wx.Brush(fill))
        path = gc.CreatePath()
        path.AddRoundedRectangle(1, 1, w - 2, h - 2, r)
        gc.FillPath(path)

        font = self.GetFont()
        if not font.IsOk():
            font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        gc.SetFont(font, txt_colour)
        tw, th2 = gc.GetTextExtent(self._label)[:2]
        gc.DrawText(self._label, (w - tw) / 2, (h - th2) / 2)


# ---------------------------------------------------------------------------
# LogSearchBar
# ---------------------------------------------------------------------------

class LogSearchBar(wx.Panel):
    """Rounded search bar: search input, match count, prev/next nav, filter toggle.

    All user actions emit a single ``LogBarEvent`` (bind with ``EVT_LOG_BAR``).
    Check ``evt.GetAction()``:

      "search"     — keyword changed (GetString)
      "prev"       — navigate to previous match
      "next"       — navigate to next match
      "filter"     — filter-mode toggled (GetInt: 1=on, 0=off)
      "key_escape" — Escape pressed in search box

    Public aliases kept for backward compat:
      textCtrl, matchCount, prevBtn, nextBtn, filterBtn
    """

    def __init__(self, parent, **kwargs):
        super().__init__(parent, wx.ID_ANY, style=wx.BORDER_NONE, **kwargs)
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)

        th = get_theme()
        self._bar_bg = wx.Colour(*th.log_bg)
        self._icon_fg = wx.Colour(*th.log_search_fg)

        inner = wx.Panel(self, wx.ID_ANY, style=wx.BORDER_NONE)
        inner.SetBackgroundColour(self._bar_bg)
        self._inner = inner

        icon = wx.StaticText(inner, wx.ID_ANY, _ICON)
        icon.SetForegroundColour(self._icon_fg)
        icon.SetBackgroundColour(self._bar_bg)
        self._icon = icon

        self.textCtrl = wx.TextCtrl(inner, wx.ID_ANY, "",
                                    style=wx.BORDER_NONE | wx.TE_PROCESS_ENTER)
        self.textCtrl.SetMinSize((130, -1))
        self.textCtrl.SetBackgroundColour(self._bar_bg)
        self.textCtrl.SetForegroundColour(wx.Colour(*th.log_search_fg))

        self.matchCount = wx.StaticText(inner, wx.ID_ANY, "")
        self.matchCount.SetMinSize((80, -1))
        self.matchCount.SetForegroundColour(self._icon_fg)
        self.matchCount.SetBackgroundColour(self._bar_bg)

        self.prevBtn = _NavBtn(inner, "🔼")
        self.nextBtn = _NavBtn(inner, "🔽")
        self.filterBtn = _NavBtn(inner, "≡", toggle=True)
        self.filterBtn.SetMinSize((28, 22))

        sep1 = wx.StaticLine(inner, style=wx.LI_VERTICAL)
        sep1.SetMinSize((1, 16))
        sep2 = wx.StaticLine(inner, style=wx.LI_VERTICAL)
        sep2.SetMinSize((1, 16))
        sep3 = wx.StaticLine(inner, style=wx.LI_VERTICAL)
        sep3.SetMinSize((1, 16))
        self._seps = (sep1, sep2, sep3)

        row = wx.BoxSizer(wx.HORIZONTAL)
        row.Add(self.matchCount, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 8)
        row.Add(sep1, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.RIGHT, 2)
        row.Add(icon, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 4)
        row.Add(self.textCtrl, 1, wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.RIGHT, 4)
        row.Add(sep2, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.RIGHT, 2)
        row.Add(self.prevBtn, 0, wx.ALIGN_CENTER_VERTICAL)
        row.Add(self.nextBtn, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 2)
        row.Add(sep3, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.RIGHT, 2)
        row.Add(self.filterBtn, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 4)
        inner.SetSizer(row)

        outer = wx.BoxSizer(wx.VERTICAL)
        outer.Add(inner, 0, wx.EXPAND | wx.ALL, 2)
        self.SetSizer(outer)

        # wire internal widgets → LogBarEvent
        self.textCtrl.Bind(wx.EVT_TEXT, self._on_text)
        self.textCtrl.Bind(wx.EVT_KEY_DOWN, self._on_key_down)
        self.prevBtn.Bind(wx.EVT_BUTTON, lambda _e: self._fire("prev"))
        self.nextBtn.Bind(wx.EVT_BUTTON, lambda _e: self._fire("next"))
        self.filterBtn.Bind(wx.EVT_BUTTON, self._on_filter_btn)

        self.Bind(wx.EVT_PAINT, self._on_paint)
        self.Bind(wx.EVT_ERASE_BACKGROUND, lambda e: None)
        self.Bind(wx.EVT_SIZE, lambda e: (e.Skip(), self.Refresh()))

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    def get_search_text(self) -> str:
        return self.textCtrl.GetValue()

    def set_search_text(self, text: str):
        self.textCtrl.SetValue(text)

    def focus_search(self):
        self.textCtrl.SetFocus()
        self.textCtrl.SelectAll()

    def is_filter_active(self) -> bool:
        return self.filterBtn.IsActive()

    # ------------------------------------------------------------------
    # Theme
    # ------------------------------------------------------------------

    def apply_theme(self, th):
        bar_bg = wx.Colour(*th.log_bg)
        icon_fg = wx.Colour(*th.log_search_fg)
        self._bar_bg = bar_bg
        self._icon_fg = icon_fg
        self._inner.SetBackgroundColour(bar_bg)
        self._icon.SetForegroundColour(icon_fg)
        self._icon.SetBackgroundColour(bar_bg)
        self.textCtrl.SetBackgroundColour(bar_bg)
        self.textCtrl.SetForegroundColour(icon_fg)
        self.matchCount.SetForegroundColour(icon_fg)
        self.matchCount.SetBackgroundColour(bar_bg)
        sep_colour = wx.Colour(*_blend(th.log_bg, th.log_fg, 0.2))
        for sep in self._seps:
            sep.SetBackgroundColour(sep_colour)
        self.Refresh()

    # ------------------------------------------------------------------
    # Internal → LogBarEvent
    # ------------------------------------------------------------------

    def _fire(self, action: str, string: str = "", int_val: int = 0):
        self.GetEventHandler().ProcessEvent(
            LogBarEvent(action, self, string=string, int_val=int_val)
        )

    def _on_text(self, evt):
        evt.Skip()
        self._fire("search", string=self.textCtrl.GetValue())

    def _on_key_down(self, evt):
        code = evt.GetKeyCode()
        if code in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER):
            self._fire("prev" if evt.ShiftDown() else "next")
        elif code == wx.WXK_ESCAPE:
            self._fire("key_escape")
        else:
            evt.Skip()

    def _on_filter_btn(self, _evt):
        active = self.filterBtn.IsActive()
        self._icon.SetLabel(_ICON_FILTER if active else _ICON_SEARCH)
        self._fire("filter", int_val=1 if active else 0)

    # ------------------------------------------------------------------
    # Paint
    # ------------------------------------------------------------------

    def _on_paint(self, _e):
        dc = wx.AutoBufferedPaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        if gc is None:
            return
        w, h = self.GetClientSize()
        gc.SetBrush(wx.Brush(self._bar_bg))
        gc.SetPen(wx.TRANSPARENT_PEN)
        gc.DrawRectangle(0, 0, w, h)
