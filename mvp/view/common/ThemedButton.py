import sys

import wx

from mvp.view.PETPTheme import get_theme

_IS_WINDOWS = sys.platform == 'win32'


def _darken(rgb, amount=20):
    return (max(0, rgb[0] - amount), max(0, rgb[1] - amount), max(0, rgb[2] - amount))


class ThemedButton(wx.Control):
    """Accent-coloured button that follows the active theme.

    Simplified sibling of RunButton — gradient fill with rounded corners,
    hover/pressed states, but no breathing glow animation.
    """

    _TEXT_COLOUR = wx.Colour(255, 255, 255)

    def __init__(self, parent, id=wx.ID_ANY, label="", **kwargs):
        super().__init__(parent, id, **kwargs)
        self._label = label.replace("&", "")
        self._hover = False
        self._pressed = False
        self._is_default = False
        self._sync_theme_colours()

        self.SetMinSize((-1, -1))
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.InvalidateBestSize()

        self.Bind(wx.EVT_PAINT, self._on_paint)
        self.Bind(wx.EVT_ENTER_WINDOW, self._on_enter)
        self.Bind(wx.EVT_LEAVE_WINDOW, self._on_leave)
        self.Bind(wx.EVT_LEFT_DOWN, self._on_left_down)
        self.Bind(wx.EVT_LEFT_UP, self._on_left_up)
        self.Bind(wx.EVT_ERASE_BACKGROUND, lambda e: None)

    def _sync_theme_colours(self):
        th = get_theme()
        self._base_top = wx.Colour(*th.accent)
        self._base_btm = wx.Colour(*_darken(th.accent))
        self._hover_top = wx.Colour(*th.accent_hover)
        self._hover_btm = wx.Colour(*th.accent)
        self._press_top = wx.Colour(*th.accent_pressed)
        self._press_btm = wx.Colour(*_darken(th.accent_pressed))

    def apply_theme(self):
        self._sync_theme_colours()
        self.Refresh()

    def SetDefault(self):
        self._is_default = True
        self.Refresh()
        return self

    def SetLabel(self, label):
        self._label = label.replace("&", "")
        self.InvalidateBestSize()
        self.Refresh()

    def GetLabel(self):
        return self._label

    def SetLabelText(self, label):
        self.SetLabel(label)

    def DoGetBestSize(self):
        dc = wx.ClientDC(self)
        font = self.GetFont()
        if not font.IsOk():
            font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        dc.SetFont(font)
        tw, th = dc.GetTextExtent(self._label)
        return wx.Size(tw + 20, th + 8)

    def Enable(self, enable=True):
        super().Enable(enable)
        self.Refresh()
        return True

    def Disable(self):
        self.Enable(False)

    def _on_enter(self, _evt):
        self._hover = True
        self.Refresh()

    def _on_leave(self, _evt):
        self._hover = False
        self._pressed = False
        self.Refresh()

    def _on_left_down(self, _evt):
        if not self.IsEnabled():
            return
        self._pressed = True
        self.CaptureMouse()
        self.Refresh()

    def _on_left_up(self, evt):
        if self.HasCapture():
            self.ReleaseMouse()
        was_pressed = self._pressed
        self._pressed = False
        self.Refresh()
        if was_pressed and self.IsEnabled():
            r = self.GetClientRect()
            if r.Contains(evt.GetPosition()):
                event = wx.CommandEvent(wx.wxEVT_BUTTON, self.GetId())
                event.SetEventObject(self)
                self.GetEventHandler().ProcessEvent(event)

    def _on_paint(self, _evt):
        dc = wx.AutoBufferedPaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        if gc is None:
            return

        w, h = self.GetClientSize()
        if w < 1 or h < 1:
            return

        gc.SetBrush(wx.Brush(self.GetParent().GetBackgroundColour()))
        gc.DrawRectangle(0, 0, w, h)

        r = 0 if _IS_WINDOWS else 6

        if not self.IsEnabled():
            top = wx.Colour(180, 180, 180)
            btm = wx.Colour(160, 160, 160)
            txt = wx.Colour(220, 220, 220)
        elif self._pressed:
            top, btm, txt = self._press_top, self._press_btm, self._TEXT_COLOUR
        elif self._hover:
            top, btm, txt = self._hover_top, self._hover_btm, self._TEXT_COLOUR
        else:
            top, btm, txt = self._base_top, self._base_btm, self._TEXT_COLOUR

        brush = gc.CreateLinearGradientBrush(0, 0, 0, h, top, btm)
        gc.SetBrush(brush)
        gc.SetPen(wx.TRANSPARENT_PEN)
        path = gc.CreatePath()
        path.AddRoundedRectangle(1, 1, w - 2, h - 2, r)
        gc.FillPath(path)

        font = self.GetFont()
        if not font.IsOk():
            font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        gc.SetFont(font, txt)
        tw, th = gc.GetTextExtent(self._label)[:2]
        gc.DrawText(self._label, (w - tw) / 2, (h - th) / 2)