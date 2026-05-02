import sys

import wx

from i18n.translations import t

_IS_MAC = sys.platform == 'darwin'


def _filter(choices, cat_map, needle):
    """Return (name_matches, cat_only_matches) — deduped, name matches first."""
    if not needle:
        return list(choices), []
    nl = needle.lower()
    name_hits = [c for c in choices if nl in c.lower()]
    name_set = set(name_hits)
    cat_hits = [c for c in choices if c not in name_set and nl in cat_map.get(c, '').lower()]
    return name_hits, cat_hits


class ProcessorPalette(wx.Frame):
    """Command-palette style floating window for selecting a processor type.

    Name matches shown first, then category-only matches with a separator.
    Keyboard: Up/Down navigate, Enter confirms, Escape dismisses.
    Loses focus → auto-close.

    tag_map: optional {name: tag_str} to show a right-aligned tag per item.
             When None, falls back to processor category lookup.
    hint:    placeholder text for the search box (overrides i18n default).
    """

    _SEP_SENTINEL = "\x00"    # internal sentinel stored parallel to _names

    def __init__(self, parent, choices, current_value="", on_select=None,
                 tag_map=None, hint=None):
        style = wx.FRAME_NO_TASKBAR | wx.FRAME_FLOAT_ON_PARENT | wx.BORDER_SIMPLE | wx.STAY_ON_TOP
        super().__init__(parent, style=style)
        self._choices = list(choices)
        self._on_select = on_select
        self._total = len(choices)
        self._confirmed = False
        # tag_map overrides category lookup when provided
        if tag_map is not None:
            self._cat_map = tag_map
            self._use_cat_filter = False  # don't split into name/cat groups
        else:
            from core.processor import Processor
            self._cat_map = Processor.get_category_map()
            self._use_cat_filter = True
        self._hint = hint
        # _names[i] is the processor name for listbox row i (or _SEP_SENTINEL for separator rows)
        self._names = []

        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        search_sizer = wx.BoxSizer(wx.HORIZONTAL)
        icon = wx.StaticText(panel, label=" \U0001f50d ")
        self._search = wx.TextCtrl(panel, style=wx.BORDER_NONE | wx.TE_PROCESS_ENTER)
        self._search.SetHint(self._hint if self._hint else t("palette_hint"))
        search_sizer.Add(icon, 0, wx.ALIGN_CENTER_VERTICAL)
        search_sizer.Add(self._search, 1, wx.EXPAND | wx.ALL, 2)
        sizer.Add(search_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 4)

        sizer.Add(wx.StaticLine(panel), 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 4)

        self._listbox = wx.ListBox(panel, style=wx.LB_SINGLE | wx.BORDER_NONE)
        self._listbox.SetFont(wx.Font(
            wx.FontInfo(12).FaceName("Menlo" if _IS_MAC else "Consolas").AntiAliased()
        ))
        self._listbox.SetMinSize((-1, 320))
        sizer.Add(self._listbox, 1, wx.EXPAND | wx.ALL, 4)

        sizer.Add(wx.StaticLine(panel), 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 4)

        self._footer = wx.StaticText(panel, label="")
        sizer.Add(self._footer, 0, wx.ALL, 4)

        panel.SetSizer(sizer)
        outer = wx.BoxSizer(wx.VERTICAL)
        outer.Add(panel, 1, wx.EXPAND)
        self.SetSizer(outer)

        self._apply_theme(panel)
        self._rebuild_list("", init=True, current_value=current_value)

        self._search.Bind(wx.EVT_TEXT, self._on_text)
        self._listbox.Bind(wx.EVT_LISTBOX_DCLICK, self._on_dclick)
        self.Bind(wx.EVT_CHAR_HOOK, self._on_char_hook)
        self.Bind(wx.EVT_ACTIVATE, self._on_activate)

        self.SetSize((380, 440))
        self.Layout()

    def _fmt(self, name):
        cat = self._cat_map.get(name, '')
        tag = f"[{cat}]" if cat else ""
        # left: name fixed 28 chars, right: tag
        return f"{name:<28}{tag}"

    def _rebuild_list(self, needle, init=False, current_value=""):
        if self._use_cat_filter:
            name_hits, cat_hits = _filter(self._choices, self._cat_map, needle)
        else:
            # simple name-only filter, no category split
            if needle:
                nl = needle.lower()
                name_hits = [c for c in self._choices if nl in c.lower()]
            else:
                name_hits = list(self._choices)
            cat_hits = []

        items = []
        names = []
        for n in name_hits:
            items.append(self._fmt(n))
            names.append(n)
        if cat_hits:
            items.append(t("palette_sep_label"))
            names.append(self._SEP_SENTINEL)
            for n in cat_hits:
                items.append(self._fmt(n))
                names.append(n)

        self._names = names
        self._listbox.Set(items)

        total_matches = len(name_hits) + len(cat_hits)
        if needle:
            self._footer.SetLabel(t("palette_footer_filtered").format(
                total=total_matches, n=self._total, nm=len(name_hits), ct=len(cat_hits)
            ))
        else:
            self._footer.SetLabel(t("palette_footer_all").format(n=self._total))

        # initial selection
        if init and current_value and current_value in self._choices:
            try:
                idx = names.index(current_value)
                self._listbox.SetSelection(idx)
                self._listbox.EnsureVisible(idx)
            except ValueError:
                pass
        elif names:
            first = 0
            if names and names[0] == self._SEP_SENTINEL:
                first = 1
            if first < len(names):
                self._listbox.SetSelection(first)

    def _apply_theme(self, panel):
        bg = wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW)
        fg = wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOWTEXT)
        panel.SetBackgroundColour(bg)
        self._search.SetBackgroundColour(bg)
        self._search.SetForegroundColour(fg)
        self._listbox.SetBackgroundColour(bg)
        self._listbox.SetForegroundColour(fg)
        self._footer.SetForegroundColour(wx.Colour(128, 128, 128))

    def ShowAt(self, pos):
        self.SetPosition(pos)
        self.Show()
        self.Raise()
        wx.CallAfter(self._search.SetFocus)

    def _on_activate(self, evt):
        if not evt.GetActive():
            wx.CallAfter(self._dismiss)
        evt.Skip()

    def _dismiss(self):
        if not self._confirmed:
            self.Destroy()

    def _on_text(self, _evt):
        self._rebuild_list(self._search.GetValue())

    def _on_char_hook(self, evt):
        code = evt.GetKeyCode()
        if code == wx.WXK_ESCAPE:
            self.Destroy()
            return
        if code in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER):
            self._confirm_selection()
            return
        if code == wx.WXK_UP:
            self._move_selection(-1)
            return
        if code == wx.WXK_DOWN:
            self._move_selection(1)
            return
        evt.Skip()

    def _move_selection(self, delta):
        count = self._listbox.GetCount()
        if count == 0:
            return
        cur = self._listbox.GetSelection()
        if cur == wx.NOT_FOUND:
            cur = 0 if delta > 0 else count - 1
        nxt = cur + delta
        # skip separator rows
        while 0 <= nxt < len(self._names) and self._names[nxt] == self._SEP_SENTINEL:
            nxt += delta
        nxt = max(0, min(count - 1, nxt))
        if self._names[nxt] != self._SEP_SENTINEL:
            self._listbox.SetSelection(nxt)
            self._listbox.EnsureVisible(nxt)

    def _on_dclick(self, _evt):
        self._confirm_selection()

    def _confirm_selection(self):
        sel = self._listbox.GetSelection()
        if sel == wx.NOT_FOUND or not self._names:
            self.Destroy()
            return
        name = self._names[sel] if sel < len(self._names) else self._SEP_SENTINEL
        if name == self._SEP_SENTINEL:
            return  # separator row — ignore
        self._confirmed = True
        self.Destroy()
        if self._on_select:
            self._on_select(name)
