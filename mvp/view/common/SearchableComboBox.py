import wx

_TOOL_PREFIX = "🦾 "


class SearchableComboBox(wx.ComboBox):
    """
    A drop-in replacement for wx.ComboBox that supports tool icon prefixes.

    Tool items (marked via set_tool_names) display with a 🦾 prefix in the
    dropdown while GetValue / SetValue work with plain names transparently.
    """

    def __init__(self, parent, id=wx.ID_ANY, value="", choices=None, **kwargs):
        kwargs.setdefault("style", wx.CB_DROPDOWN)
        super().__init__(parent, id, value=value, choices=choices or [], **kwargs)

        self._all_choices: list = list(choices or [])
        self._tool_names: set = set()

    # ------------------------------------------------------------------
    # Tool icon prefix API
    # ------------------------------------------------------------------

    def set_tool_names(self, names):
        self._tool_names = set(names)
        current_plain = self.GetValue()
        self._sync(self._all_choices, current_plain)

    def _prefix(self, name):
        return _TOOL_PREFIX + name if name in self._tool_names else name

    def _unprefix(self, text):
        return text[len(_TOOL_PREFIX):] if text.startswith(_TOOL_PREFIX) else text

    # ------------------------------------------------------------------
    # Public API overrides – keep _all_choices in sync
    # ------------------------------------------------------------------

    def GetValue(self):
        return self._unprefix(super().GetValue())

    def AppendItems(self, items):
        self._all_choices.extend(items)
        super().AppendItems([self._prefix(i) for i in items])

    def Clear(self):
        self._all_choices = []
        self._tool_names = set()
        super().Clear()

    def SetValue(self, value: str):
        super().SetValue(self._prefix(value))

    def SetItems(self, items):
        self._all_choices = list(items)
        self._sync(items, self.GetValue())

    def Reload(self, items, value):
        self._all_choices = list(items)
        self._sync(items, value)

    def FindString(self, s, caseSensitive=False):
        return super().FindString(self._prefix(s), caseSensitive)

    def Insert(self, item, pos):
        self._all_choices.insert(pos, item)
        super().Insert(self._prefix(item), pos)

    def Delete(self, n):
        if 0 <= n < len(self._all_choices):
            self._all_choices.pop(n)
        super().Delete(n)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _sync(self, items: list, value: str):
        self.Freeze()
        try:
            super().Clear()
            super().AppendItems([self._prefix(i) for i in items])
            display_value = self._prefix(value) if value else value
            super().SetValue(display_value)
        finally:
            self.Thaw()
