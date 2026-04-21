import wx


class ToggleSwitch(wx.Control):
    """Custom-drawn toggle switch that emits wx.EVT_CHECKBOX.

    Drop-in replacement for wx.CheckBox — supports SetValue/GetValue/
    IsChecked/SetLabel so the presenter code works unchanged.
    """

    _TRACK_W = 36
    _TRACK_H = 18
    _KNOB_PAD = 2
    _GAP = 6

    _ON_TRACK = wx.Colour(76, 175, 80)
    _OFF_TRACK = wx.Colour(189, 189, 189)
    _DISABLED_TRACK = wx.Colour(220, 220, 220)
    _KNOB = wx.Colour(255, 255, 255)
    _KNOB_SHADOW = wx.Colour(0, 0, 0, 30)

    def __init__(self, parent, id=wx.ID_ANY, label="", **kwargs):
        super().__init__(parent, id, **kwargs)
        self._checked = False
        self._label = label
        self._on_label = ""
        self._off_label = ""
        self._hover = False

        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self._update_min_size()

        self.Bind(wx.EVT_PAINT, self._on_paint)
        self.Bind(wx.EVT_LEFT_UP, self._on_click)
        self.Bind(wx.EVT_ENTER_WINDOW, self._on_enter)
        self.Bind(wx.EVT_LEAVE_WINDOW, self._on_leave)
        self.Bind(wx.EVT_ERASE_BACKGROUND, lambda e: None)

    def SetValue(self, val):
        self._checked = bool(val)
        self._sync_label()
        self.Refresh()

    def GetValue(self):
        return self._checked

    def IsChecked(self):
        return self._checked

    def SetLabel(self, label):
        self._label = label
        self._update_min_size()
        self.Refresh()

    def GetLabel(self):
        return self._label

    def set_state_labels(self, on_label, off_label):
        self._on_label = on_label
        self._off_label = off_label
        self._sync_label()
        self.Refresh()

    def _sync_label(self):
        if self._on_label or self._off_label:
            self._label = self._on_label if self._checked else self._off_label
            self._update_min_size()

    def _update_min_size(self):
        dc = wx.ClientDC(self)
        dc.SetFont(self.GetFont() or wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT))
        labels = [self._label, self._on_label, self._off_label]
        tw = max((dc.GetTextExtent(l)[0] for l in labels if l), default=0)
        total_w = self._TRACK_W + (self._GAP + tw if tw else 0)
        self.SetMinSize((total_w + 4, self._TRACK_H + 4))

    def _on_enter(self, _evt):
        self._hover = True
        self.Refresh()

    def _on_leave(self, _evt):
        self._hover = False
        self.Refresh()

    def _on_click(self, evt):
        if not self.IsEnabled():
            return
        r = self.GetClientRect()
        if r.Contains(evt.GetPosition()):
            self._checked = not self._checked
            self._sync_label()
            self.Refresh()
            event = wx.CommandEvent(wx.wxEVT_CHECKBOX, self.GetId())
            event.SetEventObject(self)
            event.SetInt(1 if self._checked else 0)
            self.GetEventHandler().ProcessEvent(event)

    def _on_paint(self, _evt):
        dc = wx.AutoBufferedPaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        if gc is None:
            return

        w, h = self.GetClientSize()
        if w < 1 or h < 1:
            return

        bg = self.GetParent().GetBackgroundColour()
        gc.SetBrush(wx.Brush(bg))
        gc.SetPen(wx.TRANSPARENT_PEN)
        gc.DrawRectangle(0, 0, w, h)

        tw, th = self._TRACK_W, self._TRACK_H
        ty = (h - th) / 2
        radius = th / 2

        if not self.IsEnabled():
            track_colour = self._DISABLED_TRACK
        elif self._checked:
            track_colour = self._ON_TRACK
        else:
            track_colour = self._OFF_TRACK

        if self._hover and self.IsEnabled():
            r, g, b = track_colour.Red(), track_colour.Green(), track_colour.Blue()
            track_colour = wx.Colour(min(255, r + 15), min(255, g + 15), min(255, b + 15))

        gc.SetBrush(wx.Brush(track_colour))
        path = gc.CreatePath()
        path.AddRoundedRectangle(0, ty, tw, th, radius)
        gc.FillPath(path)

        knob_d = th - self._KNOB_PAD * 2
        knob_y = ty + self._KNOB_PAD
        knob_x = (tw - knob_d - self._KNOB_PAD) if self._checked else self._KNOB_PAD

        gc.SetBrush(wx.Brush(self._KNOB_SHADOW))
        gc.DrawEllipse(knob_x + 0.5, knob_y + 1, knob_d, knob_d)

        gc.SetBrush(wx.Brush(self._KNOB))
        gc.DrawEllipse(knob_x, knob_y, knob_d, knob_d)

        if self._label:
            font = self.GetFont()
            if not font.IsOk():
                font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
            fg = self.GetForegroundColour()
            if not self.IsEnabled():
                fg = wx.Colour(160, 160, 160)
            gc.SetFont(font, fg)
            lw, lh = gc.GetTextExtent(self._label)[:2]
            gc.DrawText(self._label, tw + self._GAP, (h - lh) / 2)
