import sys

import wx

from mvp.view.theme import get_theme

_IS_WINDOWS = sys.platform == 'win32'


def _blend(c1, c2, t=0.5):
    return (
        int(c1[0] + (c2[0] - c1[0]) * t),
        int(c1[1] + (c2[1] - c1[1]) * t),
        int(c1[2] + (c2[2] - c1[2]) * t),
    )


class PopupMenuButton(wx.Control):
    """Compact themed button that shows a popup menu of choices on click.

    Fires wx.wxEVT_COMMAND_COMBOBOX_SELECTED on selection so callers can
    bind with EVT_COMBOBOX. Optionally accepts an on_select callback.
    """

    def __init__(self, parent, choices=None, default="",
                 min_width=62, *, on_select=None, **kwargs):
        super().__init__(parent, wx.ID_ANY, style=wx.BORDER_NONE, **kwargs)
        self._choices = list(choices or [])
        self._value = default
        self._on_select = on_select
        self._hover = False
        self._pressed = False
        self.SetMinSize((min_width, 22))
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)

        self.Bind(wx.EVT_PAINT, self._on_paint)
        self.Bind(wx.EVT_ENTER_WINDOW, lambda e: self._set(hover=True))
        self.Bind(wx.EVT_LEAVE_WINDOW, lambda e: self._set(hover=False, pressed=False))
        self.Bind(wx.EVT_LEFT_DOWN, self._on_down)
        self.Bind(wx.EVT_LEFT_UP, self._on_up)
        self.Bind(wx.EVT_ERASE_BACKGROUND, lambda e: None)

    def SetChoices(self, choices):
        self._choices = list(choices)

    def GetChoices(self):
        return list(self._choices)

    def GetValue(self):
        return self._value

    def SetValue(self, value):
        self._value = value
        self.Refresh()

    def Set(self, choices):
        self.SetChoices(choices)

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
                self._show_menu()

    def _show_menu(self):
        menu = wx.Menu()
        for choice in self._choices:
            menu_id = wx.NewId()
            item = menu.Append(menu_id, choice)
            if choice == self._value:
                item.SetItemLabel("• " + choice)
            self.Bind(
                wx.EVT_MENU,
                lambda e, c=choice: self._on_selected(c),
                id=menu_id
            )
        self.PopupMenu(menu)
        menu.Destroy()

    def _on_selected(self, choice):
        self._value = choice
        self.Refresh()
        if self._on_select:
            self._on_select(choice)
        evt = wx.CommandEvent(wx.wxEVT_COMMAND_COMBOBOX_SELECTED, self.GetId())
        evt.SetEventObject(self)
        evt.SetString(choice)
        wx.PostEvent(self, evt)

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

        if self._pressed:
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
        label = self._value
        tw, th2 = gc.GetTextExtent(label)[:2]
        gc.DrawText(label, (w - tw) / 2, (h - th2) / 2)
