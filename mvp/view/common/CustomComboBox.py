import sys

import wx

from mvp.view.PETPTheme import get_theme

_IS_WINDOWS = sys.platform == 'win32'
_TOOL_PREFIX = "\U0001f9be "
_NAV_PREFIX = "▸ "

_ITEM_H = 24
_MAX_VISIBLE = 12
_RADIUS = 0
_ARROW_W = 22
_PAD_X = 6
_PAD_Y = 2
_POPUP_BORDER = wx.Colour(180, 180, 180)


def _is_dark_mode():
    try:
        return wx.SystemSettings.GetAppearance().IsDark()
    except Exception:
        return False


def _input_bg():
    if _is_dark_mode():
        return wx.Colour(44, 44, 46)
    return wx.Colour(255, 255, 255)


def _input_fg():
    if _is_dark_mode():
        return wx.Colour(230, 230, 230)
    return wx.Colour(30, 30, 30)


def _border_normal():
    if _is_dark_mode():
        return wx.Colour(80, 80, 80)
    return wx.Colour(192, 192, 192)


def _border_hover():
    if _is_dark_mode():
        return wx.Colour(110, 110, 110)
    return wx.Colour(150, 150, 150)


def _popup_bg():
    if _is_dark_mode():
        return wx.Colour(50, 50, 52)
    return wx.Colour(255, 255, 255)


def _popup_item_fg():
    if _is_dark_mode():
        return wx.Colour(220, 220, 220)
    return wx.Colour(40, 40, 40)


def _popup_hover_bg():
    if _is_dark_mode():
        return wx.Colour(65, 65, 68)
    return wx.Colour(235, 235, 235)


# ---------------------------------------------------------------------------
# Virtual List Panel (inside popup)
# ---------------------------------------------------------------------------

class _ListPanel(wx.VListBox):

    def __init__(self, parent, owner):
        super().__init__(parent, wx.ID_ANY, style=wx.BORDER_NONE)
        self._owner = owner
        self._items: list = []
        self._tool_names: set = set()
        self._highlight_idx = -1
        self._hover_idx = -1
        self.SetBackgroundColour(_popup_bg())
        self.Bind(wx.EVT_MOTION, self._on_motion)
        self.Bind(wx.EVT_LEFT_UP, self._on_click)
        self.Bind(wx.EVT_KEY_DOWN, self._on_key)
        self.Bind(wx.EVT_LEFT_DOWN, self._on_left_down)

    def set_items(self, items: list, tool_names: set, highlight_idx: int = -1):
        self._items = list(items)
        self._tool_names = tool_names
        self._highlight_idx = highlight_idx
        self._hover_idx = -1
        self.SetItemCount(len(items))
        if 0 <= highlight_idx < len(items):
            self.ScrollToRow(max(0, highlight_idx - 3))
        self.Refresh()

    def set_highlight(self, idx: int):
        self._highlight_idx = idx
        if 0 <= idx < len(self._items):
            first = self.GetVisibleRowsBegin()
            last = self.GetVisibleRowsEnd()
            if idx < first or idx >= last:
                self.ScrollToRow(max(0, idx - 3))
        self.Refresh()

    def get_highlight(self) -> int:
        return self._highlight_idx

    def get_count(self) -> int:
        return len(self._items)

    # --- wx.VListBox overrides ---

    def OnMeasureItem(self, n):
        return _ITEM_H

    def OnDrawItem(self, dc, rect, n):
        if n < 0 or n >= len(self._items):
            return
        name = self._items[n]
        th = get_theme()

        if n == self._highlight_idx:
            accent = th.accent
            dc.SetBrush(wx.Brush(wx.Colour(accent[0], accent[1], accent[2], 40)))
            dc.SetPen(wx.TRANSPARENT_PEN)
            dc.DrawRectangle(rect)
        elif n == self._hover_idx:
            dc.SetBrush(wx.Brush(_popup_hover_bg()))
            dc.SetPen(wx.TRANSPARENT_PEN)
            dc.DrawRectangle(rect)

        prefix = ""
        if n == self._highlight_idx:
            prefix = _NAV_PREFIX
        if name in self._tool_names:
            prefix += _TOOL_PREFIX

        text = prefix + name
        if n == self._highlight_idx:
            dc.SetTextForeground(wx.Colour(*th.accent))
        else:
            dc.SetTextForeground(_popup_item_fg())
        font = self.GetFont()
        if not font.IsOk():
            font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        dc.SetFont(font)
        _tw, th2 = dc.GetTextExtent(text)
        x = rect.x + 10
        y = rect.y + (rect.height - th2) // 2
        dc.DrawText(text, x, y)

    def OnDrawBackground(self, dc, rect, n):
        dc.SetBrush(wx.Brush(self.GetBackgroundColour()))
        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.DrawRectangle(rect)

    # --- Events ---

    def _on_motion(self, evt):
        pos = evt.GetPosition()
        idx = self.VirtualHitTest(pos.y)
        if idx != self._hover_idx:
            self._hover_idx = idx
            self.Refresh()
        evt.Skip()

    def _on_left_down(self, evt):
        pos = evt.GetPosition()
        idx = self.VirtualHitTest(pos.y)
        if 0 <= idx < len(self._items):
            self._owner._on_item_selected(self._items[idx])

    def _on_click(self, evt):
        pass

    def _on_key(self, evt):
        self._owner._on_popup_key(evt)


# ---------------------------------------------------------------------------
# Popup Window
# ---------------------------------------------------------------------------

_POPUP_STYLE = wx.FRAME_NO_TASKBAR | wx.FRAME_FLOAT_ON_PARENT | wx.BORDER_NONE | wx.STAY_ON_TOP


class _PopupList(wx.Frame):

    def __init__(self, parent, owner):
        super().__init__(parent.GetTopLevelParent(), wx.ID_ANY, "",
                         style=_POPUP_STYLE)
        self._owner = owner
        self._list = _ListPanel(self, owner)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self._list, 1, wx.EXPAND | wx.ALL, 1)
        self.SetSizer(sizer)
        border = wx.Colour(60, 60, 60) if _is_dark_mode() else _POPUP_BORDER
        self.SetBackgroundColour(border)
        self.Bind(wx.EVT_ACTIVATE, self._on_activate)

    @property
    def list_ctrl(self) -> _ListPanel:
        return self._list

    def show_at(self, pos: wx.Point, width: int, items: list,
                tool_names: set, highlight_idx: int = -1):
        self._list.set_items(items, tool_names, highlight_idx)
        count = min(len(items), _MAX_VISIBLE)
        h = count * _ITEM_H + 4
        self.SetSize(width, h)
        self.SetPosition(pos)
        self.Layout()
        self.ShowWithoutActivating()

    def update_highlight(self, idx: int):
        self._list.set_highlight(idx)

    def dismiss(self):
        self.Hide()

    def _on_activate(self, evt):
        if not evt.GetActive():
            wx.CallAfter(self._check_dismiss)
        else:
            wx.CallAfter(self._owner._text.SetFocus)
        evt.Skip()

    def _check_dismiss(self):
        focus = wx.Window.FindFocus()
        if focus and (focus == self._list or focus == self._owner._text
                      or focus == self._owner):
            return
        self._owner._on_popup_dismissed()
        self.Hide()


# ---------------------------------------------------------------------------
# CustomComboBox — the public widget
# ---------------------------------------------------------------------------

class CustomComboBox(wx.Control):
    """Fully custom-drawn ComboBox replacement.

    Drop-in compatible with wx.ComboBox API. Supports editable (filter-as-you-type)
    and readonly modes. Renders identically on macOS and Windows.
    """

    def __init__(self, parent, id=wx.ID_ANY, value="", choices=None,
                 style=wx.CB_DROPDOWN, size=wx.DefaultSize, pos=wx.DefaultPosition,
                 **kwargs):
        super().__init__(parent, id, pos=pos, size=size)

        self._readonly = bool(style & wx.CB_READONLY)
        self._all_choices: list = sorted(list(choices or []), key=str.lower)
        self._tool_names: set = set()
        self._confirmed_value: str = value
        self._highlight_idx: int = -1
        self._filtered: list = []
        self._popup: _PopupList | None = None
        self._popup_open = False
        self._hover = False
        self._focused = False
        self._suppress_text_evt = False

        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)

        text_style = wx.BORDER_NONE | wx.TE_PROCESS_ENTER
        if self._readonly:
            text_style |= wx.TE_READONLY

        self._text = wx.TextCtrl(self, wx.ID_ANY, value, style=text_style)
        font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        font.SetPointSize(font.GetPointSize() + 2)
        self._text.SetFont(font)
        self._text.SetBackgroundColour(_input_bg())
        self._text.SetForegroundColour(_input_fg())

        dc = wx.ClientDC(self)
        dc.SetFont(font)
        _tw, text_h = dc.GetTextExtent("Wg")
        self._text_h = text_h
        best_h = text_h + 6
        self.SetMinSize((120, best_h))

        if self._readonly:
            self._text.SetCursor(wx.Cursor(wx.CURSOR_HAND))
            self.SetCursor(wx.Cursor(wx.CURSOR_HAND))

        self.Bind(wx.EVT_PAINT, self._on_paint)
        self.Bind(wx.EVT_SIZE, self._on_size)
        self.Bind(wx.EVT_ERASE_BACKGROUND, lambda e: None)
        self.Bind(wx.EVT_ENTER_WINDOW, self._on_enter)
        self.Bind(wx.EVT_LEAVE_WINDOW, self._on_leave)
        self.Bind(wx.EVT_LEFT_DOWN, self._on_left_down)

        self._text.Bind(wx.EVT_TEXT, self._on_text)
        self._text.Bind(wx.EVT_KEY_DOWN, self._on_key_down)
        self._text.Bind(wx.EVT_SET_FOCUS, self._on_focus)
        self._text.Bind(wx.EVT_KILL_FOCUS, self._on_blur)
        self._text.Bind(wx.EVT_LEFT_DOWN, self._on_text_click)

        self._do_layout()

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------

    def DoGetBestSize(self):
        dc = wx.ClientDC(self)
        font = self._text.GetFont()
        if not font.IsOk():
            font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        dc.SetFont(font)
        _tw, th = dc.GetTextExtent("Wg")
        h = th + 6
        return wx.Size(200, h)

    def _do_layout(self):
        w, h = self.GetClientSize()
        if w < 1 or h < 1:
            return
        text_x = _PAD_X
        text_w = max(10, w - _ARROW_W - _PAD_X - 1)
        border = 1
        text_y = border
        text_h = h - border * 2
        self._text.SetPosition((text_x, text_y))
        self._text.SetSize((text_w, text_h))

    def _on_size(self, evt):
        self._do_layout()
        self.Refresh()
        evt.Skip()

    # ------------------------------------------------------------------
    # Painting
    # ------------------------------------------------------------------

    def _on_paint(self, _evt):
        dc = wx.AutoBufferedPaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        if gc is None:
            return
        w, h = self.GetClientSize()
        if w < 1 or h < 1:
            return

        # Clear with parent background
        bg = self.GetParent().GetBackgroundColour()
        gc.SetBrush(wx.Brush(bg))
        gc.SetPen(wx.TRANSPARENT_PEN)
        gc.DrawRectangle(0, 0, w, h)

        # Border color based on state
        th = get_theme()
        if self._focused:
            border_colour = wx.Colour(*th.accent)
            border_w = 2
        elif self._hover:
            border_colour = _border_hover()
            border_w = 1
        else:
            border_colour = _border_normal()
            border_w = 1

        # Main box (square corners)
        r = _RADIUS
        gc.SetBrush(wx.Brush(_input_bg()))
        gc.SetPen(wx.Pen(border_colour, border_w))
        path = gc.CreatePath()
        path.AddRoundedRectangle(0.5, 0.5, w - 1, h - 1, r)
        gc.DrawPath(path)

        # Arrow separator line
        arrow_x = w - _ARROW_W
        sep_pad = 5
        sep_colour = wx.Colour(60, 60, 60) if _is_dark_mode() else wx.Colour(210, 210, 210)
        gc.SetPen(wx.Pen(sep_colour, 1))
        gc.StrokeLine(arrow_x, sep_pad, arrow_x, h - sep_pad)

        # Draw chevron triangle
        cx = arrow_x + _ARROW_W / 2
        cy = h / 2
        sz = 3.0
        gc.SetPen(wx.TRANSPARENT_PEN)
        arrow_colour = wx.Colour(180, 180, 180) if _is_dark_mode() else wx.Colour(100, 100, 100)
        gc.SetBrush(wx.Brush(arrow_colour))
        tri = gc.CreatePath()
        tri.MoveToPoint(cx - sz, cy - sz * 0.6)
        tri.AddLineToPoint(cx + sz, cy - sz * 0.6)
        tri.AddLineToPoint(cx, cy + sz * 0.6)
        tri.CloseSubpath()
        gc.FillPath(tri)

    # ------------------------------------------------------------------
    # Mouse / Focus
    # ------------------------------------------------------------------

    def _on_enter(self, _evt):
        self._hover = True
        self.Refresh()

    def _on_leave(self, _evt):
        self._hover = False
        self.Refresh()

    def _on_focus(self, evt):
        self._focused = True
        self.Refresh()
        evt.Skip()

    def _on_blur(self, evt):
        self._focused = False
        self.Refresh()
        evt.Skip()

    def _on_left_down(self, evt):
        pos = evt.GetPosition()
        w, _h = self.GetClientSize()
        if pos.x >= w - _ARROW_W or self._readonly:
            self._toggle_popup()
        else:
            self._text.SetFocus()

    def _on_text_click(self, evt):
        if self._readonly:
            self._toggle_popup()
            return
        evt.Skip()

    # ------------------------------------------------------------------
    # Text input / Filter
    # ------------------------------------------------------------------

    def _on_text(self, evt):
        if self._suppress_text_evt:
            evt.Skip()
            return
        if self._readonly:
            evt.Skip()
            return
        keyword = self._text.GetValue()
        wx.CallAfter(self._apply_filter, keyword)
        evt.Skip()

    def _apply_filter(self, keyword):
        if self._suppress_text_evt:
            return
        self._filtered = self._filter_choices(keyword)
        self._highlight_idx = -1
        if self._filtered and keyword:
            self._show_popup(self._filtered)
        elif self._popup_open and not keyword:
            self._show_popup(self._all_choices)
        elif self._popup_open and not self._filtered:
            self._dismiss_popup()

    def _filter_choices(self, keyword):
        if not keyword:
            return list(self._all_choices)
        needle = keyword.lower()
        return [name for name in self._all_choices if needle in name.lower()]

    # ------------------------------------------------------------------
    # Keyboard
    # ------------------------------------------------------------------

    def _on_key_down(self, evt):
        keycode = evt.GetKeyCode()

        if keycode in (wx.WXK_DOWN, wx.WXK_UP):
            if not self._popup_open:
                items = self._filtered if self._filtered else self._all_choices
                self._filtered = items
                self._show_popup(items)
                if self._confirmed_value:
                    for i, name in enumerate(items):
                        if name.lower() == self._confirmed_value.lower():
                            self._highlight_idx = i
                            break
            count = len(self._filtered) if self._filtered else 0
            if count > 0:
                if keycode == wx.WXK_DOWN:
                    if self._highlight_idx < 0:
                        self._highlight_idx = 0
                    elif self._highlight_idx >= count - 1:
                        self._highlight_idx = 0
                    else:
                        self._highlight_idx += 1
                else:
                    if self._highlight_idx < 0:
                        self._highlight_idx = count - 1
                    elif self._highlight_idx <= 0:
                        self._highlight_idx = count - 1
                    else:
                        self._highlight_idx -= 1
                if self._popup:
                    self._popup.update_highlight(self._highlight_idx)
            return

        if keycode in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER):
            items = self._filtered if self._filtered else self._all_choices
            if 0 <= self._highlight_idx < len(items):
                self._confirm_selection(items[self._highlight_idx])
            elif self._popup_open:
                self._dismiss_popup()
            return

        if keycode == wx.WXK_ESCAPE:
            if self._popup_open:
                self._dismiss_popup()
                self._set_text(self._confirmed_value)
            return

        if keycode == wx.WXK_TAB:
            if self._popup_open:
                items = self._filtered if self._filtered else self._all_choices
                if 0 <= self._highlight_idx < len(items):
                    self._confirm_selection(items[self._highlight_idx])
                else:
                    self._dismiss_popup()
            evt.Skip()
            return

        evt.Skip()

    def _on_popup_key(self, evt):
        self._on_key_down(evt)

    # ------------------------------------------------------------------
    # Popup control
    # ------------------------------------------------------------------

    def _toggle_popup(self):
        if self._popup_open:
            self._dismiss_popup()
        else:
            items = self._all_choices
            if not self._readonly:
                keyword = self._text.GetValue()
                if keyword and keyword != self._confirmed_value:
                    items = self._filter_choices(keyword)
                self._filtered = items
            else:
                self._filtered = items
            self._highlight_idx = -1
            if self._confirmed_value:
                for i, name in enumerate(items):
                    if name == self._confirmed_value:
                        self._highlight_idx = i
                        break
            self._show_popup(items)

    def _show_popup(self, items: list):
        if not items:
            if self._popup_open:
                self._dismiss_popup()
            return

        pos = self.ClientToScreen((0, self.GetSize().height + 2))
        width = max(self.GetSize().width, 160)

        if self._popup is None:
            self._popup = _PopupList(self, self)

        self._popup.show_at(pos, width, items, self._tool_names, self._highlight_idx)
        self._popup_open = True

    def _dismiss_popup(self):
        if self._popup and self._popup.IsShown():
            self._popup.dismiss()
        self._popup_open = False
        self._highlight_idx = -1

    def _on_popup_dismissed(self):
        self._popup_open = False
        self._highlight_idx = -1

    # ------------------------------------------------------------------
    # Selection
    # ------------------------------------------------------------------

    def _on_item_selected(self, name: str):
        self._confirm_selection(name)

    def _confirm_selection(self, name: str):
        self._confirmed_value = name
        self._highlight_idx = -1
        self._filtered = []
        self._dismiss_popup()
        self._set_text(name)
        self._text.SetFocus()
        self._post_combobox_event()

    def _set_text(self, value: str):
        self._suppress_text_evt = True
        self._text.SetValue(value)
        self._text.SetInsertionPointEnd()
        self._suppress_text_evt = False

    def _post_combobox_event(self):
        event = wx.CommandEvent(wx.wxEVT_COMBOBOX, self.GetId())
        event.SetEventObject(self)
        event.SetString(self._confirmed_value)
        self.GetEventHandler().ProcessEvent(event)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def GetValue(self) -> str:
        return self._confirmed_value

    def SetValue(self, value: str):
        self._confirmed_value = value
        self._set_text(value)

    def AppendItems(self, items):
        self._all_choices.extend(items)
        self._all_choices.sort(key=str.lower)

    def Clear(self):
        self._all_choices = []
        self._tool_names = set()
        self._confirmed_value = ""
        self._set_text("")

    def SetItems(self, items):
        self._all_choices = sorted(list(items), key=str.lower)

    def Set(self, items):
        self.SetItems(items)

    def Reload(self, items, value):
        self._all_choices = sorted(list(items), key=str.lower)
        self._confirmed_value = value
        self._set_text(value)

    def FindString(self, s, caseSensitive=False):
        if caseSensitive:
            for i, item in enumerate(self._all_choices):
                if item == s:
                    return i
        else:
            s_lower = s.lower()
            for i, item in enumerate(self._all_choices):
                if item.lower() == s_lower:
                    return i
        return wx.NOT_FOUND

    def Insert(self, item, pos):
        self._all_choices.insert(pos, item)

    def Delete(self, n):
        if 0 <= n < len(self._all_choices):
            self._all_choices.pop(n)

    def GetCount(self) -> int:
        return len(self._all_choices)

    def GetString(self, n) -> str:
        if 0 <= n < len(self._all_choices):
            return self._all_choices[n]
        return ""

    def SetSelection(self, n):
        if 0 <= n < len(self._all_choices):
            self._confirmed_value = self._all_choices[n]
            self._set_text(self._confirmed_value)

    def GetSelection(self) -> int:
        return self.FindString(self._confirmed_value)

    def set_tool_names(self, names):
        self._tool_names = set(names)

    def apply_theme(self):
        self._text.SetBackgroundColour(_input_bg())
        self._text.SetForegroundColour(_input_fg())
        self._text.Refresh()
        self.Refresh()

    def SetFont(self, font):
        super().SetFont(font)
        self._text.SetFont(font)
        self.Refresh()
        return True

    def Enable(self, enable=True):
        super().Enable(enable)
        self._text.Enable(enable)
        self.Refresh()
        return True

    def Disable(self):
        self.Enable(False)

    def Popup(self):
        self._toggle_popup()

    def Dismiss(self):
        self._dismiss_popup()

    def SetToolTip(self, tip):
        super().SetToolTip(tip)
        self._text.SetToolTip(tip)
