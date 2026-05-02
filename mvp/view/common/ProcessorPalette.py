import sys

import wx

from i18n.translations import t
from mvp.view.PETPTheme import get_theme

_IS_MAC = sys.platform == 'darwin'

_ITEM_H = 24
_SEP_H = 20
_PAD_L = 8
_PAD_R = 8


def _filter(choices, cat_map, needle):
    """Return (name_matches, cat_only_matches) — deduped, name matches first."""
    if not needle:
        return list(choices), []
    nl = needle.lower()
    name_hits = [c for c in choices if nl in c.lower()]
    name_set = set(name_hits)
    cat_hits = [c for c in choices if c not in name_set and nl in cat_map.get(c, '').lower()]
    return name_hits, cat_hits


class _PaletteListBox(wx.VListBox):

    def __init__(self, parent, on_dclick=None):
        super().__init__(parent, style=wx.BORDER_NONE)
        self._items: list[tuple[str, str]] = []
        self._separators: list[bool] = []
        self._selection = -1
        self._on_dclick = on_dclick
        self._fg = wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOWTEXT)
        self._tag_fg = wx.Colour(120, 120, 120)
        self._sep_fg = wx.Colour(140, 140, 140)
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.Bind(wx.EVT_LEFT_DOWN, self._on_left_down)
        self.Bind(wx.EVT_LEFT_DCLICK, self._on_left_dclick)

    def SetItems(self, items, separators):
        self._items = list(items)
        self._separators = list(separators)
        self._selection = -1
        self.SetItemCount(len(items))
        self.Refresh()

    def SetSelection(self, idx):
        if 0 <= idx < len(self._items):
            self._selection = idx
            first = self.GetVisibleRowsBegin()
            last = self.GetVisibleRowsEnd()
            if idx < first or idx >= last:
                self.ScrollToRow(max(0, idx - 3))
            self.Refresh()

    def GetSelection(self):
        return self._selection

    def GetCount(self):
        return len(self._items)

    def EnsureVisible(self, idx):
        if 0 <= idx < len(self._items):
            first = self.GetVisibleRowsBegin()
            last = self.GetVisibleRowsEnd()
            if idx < first or idx >= last:
                self.ScrollToRow(max(0, idx - 3))

    def OnMeasureItem(self, n):
        if 0 <= n < len(self._separators) and self._separators[n]:
            return _SEP_H
        return _ITEM_H

    def OnDrawBackground(self, dc, rect, n):
        if n == self._selection and not (0 <= n < len(self._separators) and self._separators[n]):
            th = get_theme()
            r, g, b = th.accent
            dc.SetBrush(wx.Brush(wx.Colour(r, g, b, 38)))
            dc.SetPen(wx.TRANSPARENT_PEN)
            dc.DrawRectangle(rect)
        else:
            dc.SetBrush(wx.Brush(self.GetBackgroundColour()))
            dc.SetPen(wx.TRANSPARENT_PEN)
            dc.DrawRectangle(rect)

    def OnDrawItem(self, dc, rect, n):
        if n < 0 or n >= len(self._items):
            return

        font = self.GetFont()
        if not font.IsOk():
            font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        dc.SetFont(font)

        name, tag = self._items[n]

        if self._separators[n]:
            dc.SetTextForeground(self._sep_fg)
            tw, th = dc.GetTextExtent(name)
            x = rect.x + (rect.width - tw) // 2
            y = rect.y + (rect.height - th) // 2
            dc.DrawText(name, x, y)
            return

        is_sel = (n == self._selection)
        theme = get_theme()

        if is_sel:
            name_fg = wx.Colour(*theme.accent)
            ar, ag, ab = theme.accent
            tag_fg = wx.Colour(ar, ag, ab, 180)
        else:
            name_fg = self._fg
            tag_fg = self._tag_fg

        _, text_h = dc.GetTextExtent("Ay")
        y = rect.y + (rect.height - text_h) // 2

        if tag:
            tag_w, _ = dc.GetTextExtent(tag)
            tag_x = rect.x + rect.width - _PAD_R - tag_w
            name_budget = rect.width - _PAD_L - _PAD_R - tag_w - 8
        else:
            tag_x = 0
            tag_w = 0
            name_budget = rect.width - _PAD_L - _PAD_R

        name_w, _ = dc.GetTextExtent(name)
        if name_w > name_budget > 0:
            ellipsis = "..."
            ew, _ = dc.GetTextExtent(ellipsis)
            truncated = name
            while truncated and dc.GetTextExtent(truncated)[0] + ew > name_budget:
                truncated = truncated[:-1]
            draw_name = truncated + ellipsis
        else:
            draw_name = name

        dc.SetTextForeground(name_fg)
        dc.DrawText(draw_name, rect.x + _PAD_L, y)

        if tag:
            dc.SetTextForeground(tag_fg)
            dc.DrawText(tag, tag_x, y)

    def _on_left_down(self, evt):
        pos = evt.GetPosition()
        idx = self.VirtualHitTest(pos.y)
        if 0 <= idx < len(self._items) and not self._separators[idx]:
            self.SetSelection(idx)
        evt.Skip()

    def _on_left_dclick(self, evt):
        pos = evt.GetPosition()
        idx = self.VirtualHitTest(pos.y)
        if 0 <= idx < len(self._items) and not self._separators[idx]:
            self._selection = idx
            if self._on_dclick:
                self._on_dclick()


class ProcessorPalette(wx.Frame):
    """Command-palette style floating window for selecting a processor type.

    Name matches shown first, then category-only matches with a separator.
    Keyboard: Up/Down navigate, Enter confirms, Escape dismisses.
    Loses focus → auto-close.

    tag_map: optional {name: tag_str} to show a right-aligned tag per item.
             Values already wrapped like "[tag]" are kept as-is.
             When None, falls back to processor category lookup.
    hint:    placeholder text for the search box (overrides i18n default).
    """

    _SEP_SENTINEL = "\x00"

    def __init__(self, parent, choices, current_value="", on_select=None,
                 tag_map=None, hint=None):
        style = wx.FRAME_NO_TASKBAR | wx.FRAME_FLOAT_ON_PARENT | wx.BORDER_SIMPLE | wx.STAY_ON_TOP
        super().__init__(parent, style=style)
        self._choices = list(choices)
        self._on_select = on_select
        self._total = len(choices)
        self._confirmed = False
        if tag_map is not None:
            self._cat_map = tag_map
            self._use_cat_filter = False
        else:
            from core.processor import Processor
            self._cat_map = Processor.get_category_map()
            self._use_cat_filter = True
        self._hint = hint
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

        self._listbox = _PaletteListBox(panel, on_dclick=self._on_dclick)
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
        self.Bind(wx.EVT_CHAR_HOOK, self._on_char_hook)
        self.Bind(wx.EVT_ACTIVATE, self._on_activate)

        self.SetSize((380, 440))
        self.Layout()

    def _get_tag(self, name):
        cat = str(self._cat_map.get(name, '')).strip()
        if cat.startswith('[') and cat.endswith(']'):
            return cat
        return f"[{cat}]" if cat else ""

    def _rebuild_list(self, needle, init=False, current_value=""):
        selected_name = None
        if not init and self._names:
            cur = self._listbox.GetSelection()
            if 0 <= cur < len(self._names):
                current = self._names[cur]
                if current != self._SEP_SENTINEL:
                    selected_name = current

        if self._use_cat_filter:
            name_hits, cat_hits = _filter(self._choices, self._cat_map, needle)
        else:
            if needle:
                nl = needle.lower()
                name_hits = [c for c in self._choices if nl in c.lower()]
            else:
                name_hits = list(self._choices)
            cat_hits = []

        items = []
        separators = []
        names = []

        for n in name_hits:
            items.append((n, self._get_tag(n)))
            separators.append(False)
            names.append(n)
        if cat_hits:
            items.append((t("palette_sep_label"), ""))
            separators.append(True)
            names.append(self._SEP_SENTINEL)
            for n in cat_hits:
                items.append((n, self._get_tag(n)))
                separators.append(False)
                names.append(n)

        self._names = names
        self._listbox.SetItems(items, separators)

        total_matches = len(name_hits) + len(cat_hits)
        if needle:
            self._footer.SetLabel(t("palette_footer_filtered").format(
                total=total_matches, n=self._total, nm=len(name_hits), ct=len(cat_hits)
            ))
        else:
            self._footer.SetLabel(t("palette_footer_all").format(n=self._total))

        if init and current_value and current_value in self._choices:
            try:
                idx = names.index(current_value)
                self._listbox.SetSelection(idx)
                self._listbox.EnsureVisible(idx)
            except ValueError:
                pass
        elif selected_name and selected_name in names:
            idx = names.index(selected_name)
            self._listbox.SetSelection(idx)
            self._listbox.EnsureVisible(idx)
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
        self._listbox._fg = fg
        is_dark = wx.SystemSettings.GetAppearance().IsDark() if hasattr(wx.SystemSettings, 'GetAppearance') else False
        self._listbox._tag_fg = wx.Colour(150, 150, 150) if is_dark else wx.Colour(120, 120, 120)
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
        if cur < 0:
            cur = 0 if delta > 0 else count - 1
        nxt = cur + delta
        while 0 <= nxt < len(self._names) and self._names[nxt] == self._SEP_SENTINEL:
            nxt += delta
        nxt = max(0, min(count - 1, nxt))
        if self._names[nxt] != self._SEP_SENTINEL:
            self._listbox.SetSelection(nxt)
            self._listbox.EnsureVisible(nxt)

    def _on_dclick(self):
        self._confirm_selection()

    def _confirm_selection(self):
        sel = self._listbox.GetSelection()
        if sel < 0 or not self._names:
            self.Destroy()
            return
        name = self._names[sel] if sel < len(self._names) else self._SEP_SENTINEL
        if name == self._SEP_SENTINEL:
            return
        self._confirmed = True
        self.Destroy()
        if self._on_select:
            self._on_select(name)
