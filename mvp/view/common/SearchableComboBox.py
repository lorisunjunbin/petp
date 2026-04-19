import sys
import wx

_IS_WINDOWS = sys.platform == 'win32'
_TOOL_PREFIX = "🦾 "
_NAV_PREFIX = "➡️ "


class SearchableComboBox(wx.ComboBox):
    """Drop-in wx.ComboBox replacement with live filter-as-you-type,
    keyboard navigation (Up/Down/Enter/Escape), and tool icon prefixes.

    Up/Down keys move a visible marker in the dropdown list without
    changing the text input.  Only Enter confirms the marked item.
    """

    def __init__(self, parent, id=wx.ID_ANY, value="", choices=None, **kwargs):
        kwargs.setdefault("style", wx.CB_DROPDOWN)
        super().__init__(parent, id, value=value, choices=choices or [], **kwargs)

        self._all_choices: list = list(choices or [])
        self._tool_names: set = set()

        self._is_syncing = False
        self._is_selecting = False

        self._highlight_idx = -1
        self._typed_keyword = ""
        self._filtered: list = []

        if _IS_WINDOWS:
            self._filter_timer = wx.Timer(self)
            self._pending_keyword = ""
            self.Bind(wx.EVT_TIMER, self._on_filter_timer, self._filter_timer)

        self.Bind(wx.EVT_TEXT, self._on_text)
        self.Bind(wx.EVT_KEY_DOWN, self._on_key_down)
        self.Bind(wx.EVT_COMBOBOX, self._on_combobox_select)
        self.Bind(wx.EVT_KILL_FOCUS, self._on_kill_focus)

    # ------------------------------------------------------------------
    # Tool icon prefix API
    # ------------------------------------------------------------------

    def set_tool_names(self, names):
        self._tool_names = set(names)
        current_plain = self.GetValue()
        self._sync(self._all_choices, current_plain)

    def _display(self, name, highlighted=False):
        tool = _TOOL_PREFIX if name in self._tool_names else ""
        nav = _NAV_PREFIX if highlighted else ""
        return nav + tool + name

    def _unprefix(self, text):
        for pfx in (_NAV_PREFIX, _TOOL_PREFIX):
            if text.startswith(pfx):
                text = text[len(pfx):]
        return text

    # ------------------------------------------------------------------
    # Public API overrides
    # ------------------------------------------------------------------

    def GetValue(self):
        return self._unprefix(super().GetValue())

    def SetValue(self, value: str):
        self._is_syncing = True
        try:
            super().SetValue(self._display(value))
        finally:
            if _IS_WINDOWS:
                wx.CallAfter(self._finish_sync)
            else:
                self._is_syncing = False

    def AppendItems(self, items):
        self._all_choices.extend(items)
        self._all_choices.sort(key=str.lower)
        self._is_syncing = True
        try:
            self.Freeze()
            super().Clear()
            super().AppendItems([self._display(i) for i in self._all_choices])
        finally:
            self.Thaw()
            if _IS_WINDOWS:
                wx.CallAfter(self._finish_sync)
            else:
                self._is_syncing = False

    def Clear(self):
        self._all_choices = []
        self._tool_names = set()
        super().Clear()

    def SetItems(self, items):
        self._all_choices = list(items)
        self._sync(items, self.GetValue())

    def Reload(self, items, value):
        self._all_choices = list(items)
        self._sync(items, value)

    def FindString(self, s, caseSensitive=False):
        return super().FindString(self._display(s), caseSensitive)

    def Insert(self, item, pos):
        self._all_choices.insert(pos, item)
        super().Insert(self._display(item), pos)

    def Delete(self, n):
        if 0 <= n < len(self._all_choices):
            self._all_choices.pop(n)
        super().Delete(n)

    def Destroy(self):
        if _IS_WINDOWS and hasattr(self, '_filter_timer'):
            self._filter_timer.Stop()
        return super().Destroy()

    # ------------------------------------------------------------------
    # Internal event handlers
    # ------------------------------------------------------------------

    def _on_text(self, evt):
        if self._is_syncing or self._is_selecting:
            evt.Skip()
            return

        if _IS_WINDOWS:
            self._pending_keyword = self._unprefix(super().GetValue())
            self._filter_timer.Stop()
            self._filter_timer.StartOnce(200)
            evt.Skip()
            return

        keyword = self._unprefix(super().GetValue())
        self._apply_filter(keyword)
        evt.Skip()

    def _on_filter_timer(self, _evt):
        if self._is_syncing or self._is_selecting:
            return
        self._apply_filter(self._pending_keyword)

    def _on_key_down(self, evt):
        keycode = evt.GetKeyCode()

        if keycode in (wx.WXK_DOWN, wx.WXK_UP):
            if _IS_WINDOWS and hasattr(self, '_filter_timer'):
                self._filter_timer.Stop()
            if not self._filtered:
                self._filtered = list(self._all_choices)
                self._typed_keyword = self.GetValue()
                current = self._typed_keyword
                if current:
                    needle = current.lower()
                    for i, name in enumerate(self._filtered):
                        if needle in name.lower():
                            self._highlight_idx = i
                            break
            count = len(self._filtered)
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
                self._rebuild_dropdown_with_highlight()
                wx.CallAfter(self.Popup)
            return

        if keycode in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER):
            if _IS_WINDOWS and hasattr(self, '_filter_timer'):
                self._filter_timer.Stop()
            items = self._filtered if self._filtered else self._all_choices
            if 0 <= self._highlight_idx < len(items):
                selected = items[self._highlight_idx]
            else:
                selected = self.GetValue()
            self._highlight_idx = -1
            self._filtered = []
            self._is_selecting = True
            self._sync(self._all_choices, selected)
            self._is_selecting = False
            self.Dismiss()
            self._post_combobox_event()
            return

        if keycode == wx.WXK_ESCAPE:
            if _IS_WINDOWS and hasattr(self, '_filter_timer'):
                self._filter_timer.Stop()
            self._highlight_idx = -1
            self._filtered = []
            current = self.GetValue()
            self._is_selecting = True
            self._sync(self._all_choices, current)
            self._is_selecting = False
            self.Dismiss()
            return

        evt.Skip()

    def _on_combobox_select(self, evt):
        self._highlight_idx = -1
        self._filtered = []
        self._is_selecting = True
        if _IS_WINDOWS:
            if hasattr(self, '_filter_timer'):
                self._filter_timer.Stop()
        selected = self.GetValue()
        self._sync(self._all_choices, selected)
        wx.CallAfter(self._finish_selecting)
        evt.Skip()

    def _finish_selecting(self):
        self._is_selecting = False

    def _on_kill_focus(self, evt):
        if _IS_WINDOWS and hasattr(self, '_filter_timer'):
            self._filter_timer.Stop()
        self._highlight_idx = -1
        self._filtered = []
        if self.GetCount() != len(self._all_choices):
            current = self.GetValue()
            self._is_selecting = True
            self._sync(self._all_choices, current)
            self._is_selecting = False
        evt.Skip()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _apply_filter(self, keyword):
        self._typed_keyword = keyword
        self._filtered = self._filter_choices(keyword)
        self._highlight_idx = -1
        self._rebuild_list(self._filtered, keyword)
        if self._filtered and keyword:
            wx.CallAfter(self.Popup)

    def _filter_choices(self, keyword):
        if not keyword:
            return list(self._all_choices)
        needle = keyword.lower()
        return [name for name in self._all_choices if needle in name.lower()]

    def _rebuild_dropdown_with_highlight(self):
        items = self._filtered if self._filtered else self._all_choices
        display_items = []
        for i, name in enumerate(items):
            display_items.append(self._display(name, highlighted=(i == self._highlight_idx)))
        self._is_syncing = True
        try:
            self.Freeze()
            super().Clear()
            super().AppendItems(display_items)
            if _IS_WINDOWS:
                self.ChangeValue(self._typed_keyword)
            else:
                super().SetValue(self._typed_keyword)
            self.SetInsertionPointEnd()
        finally:
            self.Thaw()
            if _IS_WINDOWS:
                wx.CallAfter(self._finish_sync)
            else:
                self._is_syncing = False

    def _rebuild_list(self, items: list, keyword: str):
        self._is_syncing = True
        try:
            self.Freeze()
            super().Clear()
            super().AppendItems([self._display(i) for i in items])
            if _IS_WINDOWS:
                self.ChangeValue(keyword)
            else:
                super().SetValue(keyword)
            self.SetInsertionPointEnd()
        finally:
            self.Thaw()
            if _IS_WINDOWS:
                wx.CallAfter(self._finish_sync)
            else:
                self._is_syncing = False

    def _sync(self, items: list, value: str):
        self._is_syncing = True
        try:
            self.Freeze()
            super().Clear()
            super().AppendItems([self._display(i) for i in items])
            display_value = self._display(value) if value else value
            if _IS_WINDOWS:
                self.ChangeValue(display_value)
            else:
                super().SetValue(display_value)
            self.SetInsertionPointEnd()
        finally:
            self.Thaw()
            if _IS_WINDOWS:
                wx.CallAfter(self._finish_sync)
            else:
                self._is_syncing = False

    def _finish_sync(self):
        self._is_syncing = False

    def _deferred_select_restore(self):
        selected = self.GetValue()
        if self.GetCount() != len(self._all_choices):
            self._sync(self._all_choices, selected)
        self._is_selecting = False

    def _post_combobox_event(self):
        event = wx.CommandEvent(wx.wxEVT_COMBOBOX, self.GetId())
        event.SetEventObject(self)
        event.SetString(super().GetValue())
        self.GetEventHandler().ProcessEvent(event)
