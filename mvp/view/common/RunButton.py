import wx


class RunButton(wx.Control):
    """Custom-drawn run button with green gradient, rounded corners, and a breathing glow."""

    _BASE_TOP = wx.Colour(76, 175, 80)
    _BASE_BTM = wx.Colour(56, 142, 60)
    _HOVER_TOP = wx.Colour(102, 197, 106)
    _HOVER_BTM = wx.Colour(76, 175, 80)
    _PRESS_TOP = wx.Colour(46, 125, 50)
    _PRESS_BTM = wx.Colour(36, 105, 40)
    _TEXT_COLOUR = wx.Colour(255, 255, 255)
    _GLOW_COLOUR = wx.Colour(76, 175, 80, 60)

    def __init__(self, parent, label="Run", **kwargs):
        super().__init__(parent, wx.ID_ANY, **kwargs)
        self._label = label
        self._hover = False
        self._pressed = False
        self._glow_alpha = 0
        self._glow_dir = 1

        self.SetMinSize((100, 32))
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)

        self._timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._on_tick, self._timer)
        self._timer.Start(50)

        self.Bind(wx.EVT_PAINT, self._on_paint)
        self.Bind(wx.EVT_ENTER_WINDOW, self._on_enter)
        self.Bind(wx.EVT_LEAVE_WINDOW, self._on_leave)
        self.Bind(wx.EVT_LEFT_DOWN, self._on_left_down)
        self.Bind(wx.EVT_LEFT_UP, self._on_left_up)
        self.Bind(wx.EVT_ERASE_BACKGROUND, lambda e: None)
        self.Bind(wx.EVT_WINDOW_DESTROY, self._on_destroy)

    def SetLabel(self, label):
        self._label = label
        self.Refresh()

    def GetLabel(self):
        return self._label

    def SetLabelText(self, label):
        self.SetLabel(label)

    def Enable(self, enable=True):
        super().Enable(enable)
        self.Refresh()
        return True

    def Disable(self):
        self.Enable(False)

    def _on_tick(self, _evt):
        if not self.IsEnabled():
            if self._glow_alpha != 0:
                self._glow_alpha = 0
                self.Refresh()
            return
        self._glow_alpha += self._glow_dir * 4
        if self._glow_alpha >= 50:
            self._glow_alpha = 50
            self._glow_dir = -1
        elif self._glow_alpha <= 0:
            self._glow_alpha = 0
            self._glow_dir = 1
        self.Refresh()

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

        r = 6

        if not self.IsEnabled():
            top = wx.Colour(180, 180, 180)
            btm = wx.Colour(160, 160, 160)
            txt = wx.Colour(220, 220, 220)
        elif self._pressed:
            top, btm, txt = self._PRESS_TOP, self._PRESS_BTM, self._TEXT_COLOUR
        elif self._hover:
            top, btm, txt = self._HOVER_TOP, self._HOVER_BTM, self._TEXT_COLOUR
        else:
            top, btm, txt = self._BASE_TOP, self._BASE_BTM, self._TEXT_COLOUR

        if self.IsEnabled() and self._glow_alpha > 0:
            glow_r = r + 3
            gc.SetBrush(wx.Brush(wx.Colour(76, 175, 80, self._glow_alpha)))
            gc.SetPen(wx.TRANSPARENT_PEN)
            path = gc.CreatePath()
            path.AddRoundedRectangle(0, 0, w, h, glow_r)
            gc.FillPath(path)

        brush = gc.CreateLinearGradientBrush(0, 0, 0, h, top, btm)
        gc.SetBrush(brush)
        gc.SetPen(wx.TRANSPARENT_PEN)
        path = gc.CreatePath()
        path.AddRoundedRectangle(2, 1, w - 4, h - 2, r)
        gc.FillPath(path)

        font = self.GetFont()
        if not font.IsOk():
            font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        gc.SetFont(font, txt)
        tw, th = gc.GetTextExtent(self._label)[:2]
        gc.DrawText(self._label, (w - tw) / 2, (h - th) / 2)

    def _on_destroy(self, evt):
        evt.Skip()
        if evt.GetEventObject() is not self:
            return
        self._timer.Stop()
