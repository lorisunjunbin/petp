import wx


class SearchableComboBox(wx.ComboBox):
    """
    A drop-in replacement for wx.ComboBox that adds filter-as-you-type behavior.

    - Typing narrows the dropdown list to matching items (case-insensitive contains).
    - Up/Down keys navigate the filtered list; Enter confirms; Escape dismisses.
    - Selecting an item from the list restores the full list for the next interaction.
    - All standard wx.ComboBox API (AppendItems, Clear, SetValue, GetValue …) still works.
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

    def SetItems(self, items):
        """Replace the full item list (master + visible)."""
        self._all_choices = list(items)
        self._sync(items, self.GetValue())

    # ------------------------------------------------------------------
    # Internal event handlers
    # ------------------------------------------------------------------

    def _on_text(self, evt):
        """Filter the dropdown list as the user types."""
        if self._is_syncing or self._is_selecting or self._is_navigating:
            evt.Skip()
            return

        keyword = self.GetValue()
        filtered = self._filter(keyword)
        self._sync(filtered, keyword)

        # Open the dropdown so the user can see the filtered results.
        if filtered:
            wx.CallAfter(self.Popup)

        evt.Skip()

    def _on_combobox_select(self, evt):
        """User clicked an item – restore the full list for the next open."""
        self._is_selecting = True
        selected = self.GetValue()
        self._sync(self._all_choices, selected)
        self._is_selecting = False
        evt.Skip()

    def _on_key_down(self, evt):
        """Handle keyboard navigation inside the dropdown."""
        keycode = evt.GetKeyCode()

        if keycode in (wx.WXK_UP, wx.WXK_DOWN):
            # Let the ComboBox move the selection; suppress filtering.
            self._is_navigating = True
            evt.Skip()
            wx.CallAfter(self._reset_navigating)
            return

        if keycode in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER):
            # Confirm the highlighted value and restore the full list.
            selected = self.GetValue()
            self._is_selecting = True
            self._sync(self._all_choices, selected)
            self._is_selecting = False
            self.Dismiss()
            evt.Skip()
            return

        if keycode == wx.WXK_ESCAPE:
            # Dismiss without changing value; restore full list.
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
            self.SetValue(value)
            self.SetInsertionPointEnd()
        finally:
            self.Thaw()
            self._is_syncing = False

    def _filter(self, keyword: str) -> list:
        """Return items whose text contains *keyword* (case-insensitive)."""
        if not keyword:
            return self._all_choices
        needle = keyword.lower()
        return [item for item in self._all_choices if needle in item.lower()]

