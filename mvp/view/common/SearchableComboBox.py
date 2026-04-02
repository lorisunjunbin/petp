import sys
import wx

_IS_WINDOWS = sys.platform == 'win32'


class SearchableComboBox(wx.ComboBox):
    """
    A drop-in replacement for wx.ComboBox that adds filter-as-you-type behavior.

    - Typing narrows the dropdown list to matching items (case-insensitive contains).
    - Up/Down keys navigate the filtered list; Enter confirms; Escape dismisses.
    - Selecting an item from the list restores the full list for the next interaction.
    - All standard wx.ComboBox API (AppendItems, Clear, SetValue, GetValue …) still works.

    On Windows extra care is taken to prevent flickering caused by asynchronous
    EVT_TEXT events that Clear() / SetValue() post into the event queue.
    """

    def __init__(self, parent, id=wx.ID_ANY, value="", choices=None, **kwargs):
        kwargs.setdefault("style", wx.CB_DROPDOWN)
        super().__init__(parent, id, value=value, choices=choices or [], **kwargs)

        # Master copy of all items; the visible list is a filtered subset.
        self._all_choices: list = list(choices or [])

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
    # Public API overrides – keep _all_choices in sync
    # ------------------------------------------------------------------

    def AppendItems(self, items):
        """Append items to the master list and the visible list."""
        self._all_choices.extend(items)
        super().AppendItems(items)

    def Clear(self):
        """Clear all items from both the master list and the visible list."""
        self._all_choices = []
        super().Clear()

    def SetValue(self, value: str):
        """Programmatically set the displayed value without triggering live
        filtering or opening the dropdown popup.

        Any external caller (e.g. Presenter loading the last-run value on
        startup) should use this method.  User keystrokes fire EVT_TEXT
        directly and bypass SetValue, so they still invoke _on_text and get
        the normal filter-as-you-type behaviour.
        """
        self._is_syncing = True
        try:
            self.Freeze()
            # Restore the full item list in case it was previously narrowed by
            # a filter operation, so the next user interaction sees all choices.
            if self.GetCount() != len(self._all_choices):
                super().Clear()
                super().AppendItems(self._all_choices)
            super().SetValue(value)
            self.SetInsertionPointEnd()
        finally:
            self.Thaw()
            if _IS_WINDOWS:
                # Defer the flag reset so that any async EVT_TEXT events that
                # Clear() queued on Windows are still suppressed.
                wx.CallAfter(self._finish_sync)
            else:
                self._is_syncing = False

    def SetItems(self, items):
        """Replace the full item list (master + visible)."""
        self._all_choices = list(items)
        self._sync(items, self.GetValue())

    def Reload(self, items, value):
        """Replace the full item list and set the display value atomically.

        External callers (e.g. Presenter._reload_executions) should prefer
        this over manual Clear() + AppendItems() + SetValue() sequences to
        avoid triggering unwanted EVT_TEXT cascades on Windows.
        """
        self._all_choices = list(items)
        self._sync(items, value)

    # ------------------------------------------------------------------
    # Internal event handlers
    # ------------------------------------------------------------------

    def _on_text(self, evt):
        """Filter the dropdown list as the user types."""
        if self._is_syncing or self._is_selecting or self._is_navigating:
            evt.Skip()
            return

        if _IS_WINDOWS:
            # Debounce: restart timer so rapid keystrokes don't each rebuild
            # the list (which would trigger more async EVT_TEXT events).
            self._pending_keyword = self.GetValue()
            self._filter_timer.Stop()
            self._filter_timer.StartOnce(200)
            evt.Skip()
            return

        # macOS / Linux: immediate filtering (original behaviour, unchanged).
        keyword = self.GetValue()
        filtered = self._filter(keyword)
        self._sync(filtered, keyword)

        # Open the dropdown so the user can see the filtered results.
        if filtered:
            wx.CallAfter(self.Popup)

        evt.Skip()

    def _on_filter_timer(self, _evt):
        """Windows only – apply the filter after the debounce interval."""
        if self._is_syncing or self._is_selecting or self._is_navigating:
            return
        keyword = self._pending_keyword
        filtered = self._filter(keyword)
        self._sync(filtered, keyword)
        if filtered and keyword:
            wx.CallAfter(self.Popup)

    def _on_combobox_select(self, evt):
        """User clicked an item – restore the full list for the next open."""
        if _IS_WINDOWS:
            self._filter_timer.Stop()
            # On Windows, do NOT call _sync() here.  The Clear() inside
            # _sync would blank the text that the native control just set.
            # Keep the guard flag raised so that the follow-up EVT_TEXT
            # (CBN_EDITCHANGE) is suppressed, and defer the list restore
            # until all native selection events have been processed.
            self._is_selecting = True
            wx.CallAfter(self._deferred_select_restore)
        else:
            self._is_selecting = True
            selected = self.GetValue()
            self._sync(self._all_choices, selected)
            self._is_selecting = False
        evt.Skip()

    def _deferred_select_restore(self):
        """Windows only – restore the full item list after a dropdown selection.

        Called via wx.CallAfter so that all native ComboBox events
        (CBN_SELCHANGE, CBN_EDITCHANGE) have already been processed and the
        displayed text is stable.
        """
        selected = self.GetValue()
        # Restore the full list only if it was previously filtered.
        if self.GetCount() != len(self._all_choices):
            self._sync(self._all_choices, selected)
        # Clear the guard AFTER _sync (which sets its own _is_syncing guard),
        # so that there is no unguarded gap between the two flags.
        self._is_selecting = False

    def _on_key_down(self, evt):
        """Handle keyboard navigation inside the dropdown."""
        keycode = evt.GetKeyCode()

        if keycode in (wx.WXK_UP, wx.WXK_DOWN):
            # Let the ComboBox move the selection; suppress filtering.
            if _IS_WINDOWS:
                self._filter_timer.Stop()
            self._is_navigating = True
            evt.Skip()
            wx.CallAfter(self._reset_navigating)
            return

        if keycode in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER):
            # Confirm the highlighted value and restore the full list.
            if _IS_WINDOWS:
                self._filter_timer.Stop()
            selected = self.GetValue()
            self._is_selecting = True
            self._sync(self._all_choices, selected)
            self._is_selecting = False
            self.Dismiss()
            evt.Skip()
            return

        if keycode == wx.WXK_ESCAPE:
            # Dismiss without changing value; restore full list.
            if _IS_WINDOWS:
                self._filter_timer.Stop()
            self._sync(self._all_choices, self.GetValue())
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

    def _sync(self, items: list, value: str):
        """Atomically update the visible item list and text value."""
        self._is_syncing = True
        try:
            self.Freeze()
            super().Clear()
            super().AppendItems(items)
            if _IS_WINDOWS:
                # ChangeValue() does NOT fire EVT_TEXT – avoids the
                # synchronous re-entrant call that SetValue() causes.
                self.ChangeValue(value)
            else:
                # Use super().SetValue() to bypass our own override so that
                # _is_syncing is not reset prematurely inside this call.
                super().SetValue(value)
            self.SetInsertionPointEnd()
        finally:
            self.Thaw()
            if _IS_WINDOWS:
                # Defer the flag reset: async EVT_TEXT events posted by
                # Clear() are still in the queue; they must see
                # _is_syncing == True so they get suppressed.
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

