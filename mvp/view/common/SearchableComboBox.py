import sys
import wx

_IS_WINDOWS = sys.platform == 'win32'

_TOOL_PREFIX = "🔧 "


class SearchableComboBox(wx.ComboBox):
    """
    A drop-in replacement for wx.ComboBox that adds filter-as-you-type behavior.

    - Typing narrows the dropdown list to matching items (case-insensitive contains).
    - Up/Down keys navigate the filtered list; Enter confirms; Escape dismisses.
    - Selecting an item from the list restores the full list for the next interaction.
    - All standard wx.ComboBox API (AppendItems, Clear, SetValue, GetValue …) still works.
    - Tool items (marked via set_tool_names) display with a 🔧 prefix in the dropdown.

    On Windows extra care is taken to prevent flickering caused by asynchronous
    EVT_TEXT events that Clear() / SetValue() post into the event queue.
    """

    def __init__(self, parent, id=wx.ID_ANY, value="", choices=None, **kwargs):
        kwargs.setdefault("style", wx.CB_DROPDOWN)
        super().__init__(parent, id, value=value, choices=choices or [], **kwargs)

        # Master copy of all items (plain names, no prefix); the visible list is a filtered subset.
        self._all_choices: list = list(choices or [])

        # Set of item names that should display with the tool icon prefix.
        self._tool_names: set = set()

        # Guard flags that prevent re-entrant filtering during programmatic updates.
        self._is_syncing = False
        self._is_selecting = False
        self._is_navigating = False

        # Windows-only: timer-based debounce to avoid rebuilding the list on
        # every keystroke (async EVT_TEXT from Clear/SetValue causes recursion).
        if _IS_WINDOWS:
            self._filter_timer = wx.Timer(self)
            self._pending_keyword = ""
            self.Bind(wx.EVT_TIMER, self._on_filter_timer)

        self.Bind(wx.EVT_TEXT, self._on_text)
        self.Bind(wx.EVT_COMBOBOX, self._on_combobox_select)
        self.Bind(wx.EVT_KEY_DOWN, self._on_key_down)

    # ------------------------------------------------------------------
    # Tool icon prefix API
    # ------------------------------------------------------------------

    def set_tool_names(self, names):
        """Mark which items should display with a tool icon prefix in the dropdown.

        Call this AFTER items have been added via AppendItems / SetItems / Reload.
        """
        self._tool_names = set(names)
        # Refresh the visible list to show / hide the prefix.
        current_plain = self.GetValue()
        self._sync(self._all_choices, current_plain, display_selected=True)

    def _prefix(self, name):
        """Return the display version of *name* (adds tool icon if applicable)."""
        return _TOOL_PREFIX + name if name in self._tool_names else name

    def _unprefix(self, text):
        """Strip the tool icon prefix from *text* if present."""
        return text[len(_TOOL_PREFIX):] if text.startswith(_TOOL_PREFIX) else text

    # ------------------------------------------------------------------
    # Public API overrides – keep _all_choices in sync
    # ------------------------------------------------------------------

    def GetValue(self):
        """Return the plain item name (tool icon prefix stripped)."""
        return self._unprefix(super().GetValue())

    def AppendItems(self, items):
        """Append items (plain names) to the master list and the visible list."""
        self._all_choices.extend(items)
        super().AppendItems([self._prefix(i) for i in items])

    def Clear(self):
        """Clear all items from both the master list and the visible list."""
        self._all_choices = []
        self._tool_names = set()
        super().Clear()

    def SetValue(self, value: str):
        """Programmatically set the displayed value without triggering live
        filtering or opening the dropdown popup.

        Accepts a plain item name; the tool icon prefix is added automatically
        if the name is marked as a tool.
        """
        self._is_syncing = True
        try:
            self.Freeze()
            if self.GetCount() != len(self._all_choices):
                super().Clear()
                super().AppendItems([self._prefix(i) for i in self._all_choices])
            super().SetValue(self._prefix(value))
            self.SetInsertionPointEnd()
        finally:
            self.Thaw()
            if _IS_WINDOWS:
                wx.CallAfter(self._finish_sync)
            else:
                self._is_syncing = False

    def SetItems(self, items):
        """Replace the full item list (master + visible)."""
        self._all_choices = list(items)
        self._sync(items, self.GetValue(), display_selected=True)

    def Reload(self, items, value):
        """Replace the full item list and set the display value atomically."""
        self._all_choices = list(items)
        self._sync(items, value, display_selected=True)

    def FindString(self, s, caseSensitive=False):
        """Find a plain name in the dropdown (prefix handled internally)."""
        return super().FindString(self._prefix(s), caseSensitive)

    def Insert(self, item, pos):
        """Insert a plain name at the given position."""
        self._all_choices.insert(pos, item)
        super().Insert(self._prefix(item), pos)

    def Delete(self, n):
        """Delete the item at position *n*."""
        if 0 <= n < len(self._all_choices):
            self._all_choices.pop(n)
        super().Delete(n)

    # ------------------------------------------------------------------
    # Internal event handlers
    # ------------------------------------------------------------------

    def _on_text(self, evt):
        """Filter the dropdown list as the user types."""
        if self._is_syncing or self._is_selecting or self._is_navigating:
            evt.Skip()
            return

        if _IS_WINDOWS:
            self._pending_keyword = self.GetValue()
            self._filter_timer.Stop()
            self._filter_timer.StartOnce(200)
            evt.Skip()
            return

        keyword = self.GetValue()
        filtered = self._filter(keyword)
        self._sync(filtered, keyword, display_selected=False)

        if filtered:
            wx.CallAfter(self.Popup)

        evt.Skip()

    def _on_filter_timer(self, _evt):
        """Windows only – apply the filter after the debounce interval."""
        if self._is_syncing or self._is_selecting or self._is_navigating:
            return
        keyword = self._pending_keyword
        filtered = self._filter(keyword)
        self._sync(filtered, keyword, display_selected=False)
        if filtered and keyword:
            wx.CallAfter(self.Popup)

    def _on_combobox_select(self, evt):
        """User clicked an item – restore the full list for the next open."""
        if _IS_WINDOWS:
            self._filter_timer.Stop()
            self._is_selecting = True
            wx.CallAfter(self._deferred_select_restore)
        else:
            self._is_selecting = True
            selected = self.GetValue()
            self._sync(self._all_choices, selected, display_selected=True)
            self._is_selecting = False
        evt.Skip()

    def _deferred_select_restore(self):
        """Windows only – restore the full item list after a dropdown selection."""
        selected = self.GetValue()
        if self.GetCount() != len(self._all_choices):
            self._sync(self._all_choices, selected, display_selected=True)
        self._is_selecting = False

    def _on_key_down(self, evt):
        """Handle keyboard navigation inside the dropdown."""
        keycode = evt.GetKeyCode()

        if keycode in (wx.WXK_UP, wx.WXK_DOWN):
            if _IS_WINDOWS:
                self._filter_timer.Stop()
            self._is_navigating = True
            evt.Skip()
            wx.CallAfter(self._reset_navigating)
            return

        if keycode in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER):
            if _IS_WINDOWS:
                self._filter_timer.Stop()
            selected = self.GetValue()
            self._is_selecting = True
            self._sync(self._all_choices, selected, display_selected=True)
            self._is_selecting = False
            self.Dismiss()
            evt.Skip()
            return

        if keycode == wx.WXK_ESCAPE:
            if _IS_WINDOWS:
                self._filter_timer.Stop()
            self._sync(self._all_choices, self.GetValue(), display_selected=True)
            self.Dismiss()
            evt.Skip()
            return

        evt.Skip()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _reset_navigating(self):
        """Called via CallAfter to clear the navigation guard flag."""
        self._is_navigating = False

    def _sync(self, items: list, value: str, display_selected: bool = True):
        """Atomically update the visible item list and text value.

        Parameters
        ----------
        items : list
            Plain item names (no prefix).
        value : str
            The text to show in the edit field (plain name or partial keyword).
        display_selected : bool
            If True and *value* exactly matches a tool name, the tool icon
            prefix is added to the display text.  Set to False during live
            filtering so the user's typing is not interrupted.
        """
        self._is_syncing = True
        try:
            self.Freeze()
            super().Clear()
            super().AppendItems([self._prefix(i) for i in items])
            display_value = (self._prefix(value)
                             if display_selected and value in self._tool_names
                             else value) if value else value
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
        """Windows only – reset the guard after pending events have drained."""
        self._is_syncing = False

    def _filter(self, keyword: str) -> list:
        """Return items whose text contains *keyword* (case-insensitive)."""
        if not keyword:
            return self._all_choices
        needle = keyword.lower()
        return [item for item in self._all_choices if needle in item.lower()]

    def Destroy(self):
        if _IS_WINDOWS and hasattr(self, '_filter_timer'):
            self._filter_timer.Stop()
        return super().Destroy()