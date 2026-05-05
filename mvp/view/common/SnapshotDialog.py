import difflib
import json
import os

import wx

from i18n.translations import t
from mvp.view.common.ThemedButton import ThemedButton

_CLR_ADD = wx.Colour(0, 128, 0)
_CLR_DEL = wx.Colour(180, 0, 0)
_CLR_HDR = wx.Colour(80, 80, 160)
_CLR_DEF = wx.Colour(80, 80, 80)


class SnapshotDialog(wx.Dialog):

    def __init__(self, parent, snapshots, cursor):
        style = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
        super().__init__(parent, title=t("dlg_snapshot_title"), style=style)

        self._snapshots = snapshots
        self._cursor = cursor
        self._selected_index = None

        self._build_ui()
        self._try_set_icon()
        self.SetSize((860, 520))
        self.CentreOnScreen()

    def _build_ui(self):
        PAD = 10
        sizer = wx.BoxSizer(wx.VERTICAL)

        splitter = wx.SplitterWindow(self, style=wx.SP_LIVE_UPDATE)

        self._list = wx.ListBox(splitter, style=wx.LB_SINGLE)
        for i, snap in enumerate(self._snapshots):
            task_count = len(snap.get("tasks", []))
            marker = " ◀" if i == self._cursor else ""
            self._list.Append(f"#{i + 1}  {snap['timestamp']}  ({task_count} tasks){marker}")

        self._preview = wx.TextCtrl(
            splitter, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2 | wx.HSCROLL
        )
        self._preview.SetFont(wx.Font(wx.FontInfo(11).Family(wx.FONTFAMILY_MODERN)))

        splitter.SplitVertically(self._list, self._preview, 220)
        splitter.SetMinimumPaneSize(150)
        sizer.Add(splitter, 1, wx.EXPAND | wx.ALL, PAD)

        btns = wx.BoxSizer(wx.HORIZONTAL)
        btns.AddStretchSpacer()
        self._apply_btn = ThemedButton(self, wx.ID_OK, t("btn_apply_snapshot"))
        self._apply_btn.Enable(False)
        close_btn = wx.Button(self, wx.ID_CANCEL, t("btn_close"))
        btns.Add(self._apply_btn, 0, wx.RIGHT, 8)
        btns.Add(close_btn)
        sizer.Add(btns, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, PAD)

        self.SetSizer(sizer)

        self._list.Bind(wx.EVT_LISTBOX, self._on_select)
        self._list.Bind(wx.EVT_LISTBOX_DCLICK, self._on_dclick)

        if self._snapshots:
            last = len(self._snapshots) - 1
            self._list.SetSelection(last)
            self._show_preview(last)
            self._apply_btn.Enable(True)
            self._selected_index = last

    def _try_set_icon(self):
        icon_path = os.path.realpath(os.path.join('.', 'image', 'petp_small.png'))
        if os.path.isfile(icon_path):
            try:
                self.SetIcon(wx.Icon(icon_path))
            except Exception:
                pass

    def _on_select(self, evt):
        idx = self._list.GetSelection()
        if idx == wx.NOT_FOUND:
            return
        self._selected_index = idx
        self._apply_btn.Enable(True)
        self._show_preview(idx)

    def _on_dclick(self, evt):
        idx = self._list.GetSelection()
        if idx != wx.NOT_FOUND:
            self._selected_index = idx
            self.EndModal(wx.ID_OK)

    def _show_preview(self, idx):
        self._preview.SetValue("")
        if idx == 0:
            # First snapshot — no previous to diff against, show full content
            snap = self._snapshots[idx]
            self._append_colored(t("snap_first_snapshot") + "\n\n", _CLR_HDR)
            self._append_colored(json.dumps(snap, indent=2, ensure_ascii=False), _CLR_DEF)
            return

        prev = self._snapshots[idx - 1]
        curr = self._snapshots[idx]
        self._render_diff(prev, curr)

    def _render_diff(self, prev, curr):
        prev_lines = json.dumps(prev, indent=2, ensure_ascii=False).splitlines(keepends=True)
        curr_lines = json.dumps(curr, indent=2, ensure_ascii=False).splitlines(keepends=True)

        diff = list(difflib.unified_diff(
            prev_lines, curr_lines,
            fromfile=f"#{self._snapshots.index(prev) + 1} {prev['timestamp']}",
            tofile=f"#{self._snapshots.index(curr) + 1} {curr['timestamp']}",
            lineterm="",
        ))

        if not diff:
            self._append_colored(t("snap_no_changes"), _CLR_DEF)
            return

        for line in diff:
            if line.startswith("+++") or line.startswith("---"):
                self._append_colored(line + "\n", _CLR_HDR)
            elif line.startswith("@@"):
                self._append_colored(line + "\n", _CLR_HDR)
            elif line.startswith("+"):
                self._append_colored(line + "\n", _CLR_ADD)
            elif line.startswith("-"):
                self._append_colored(line + "\n", _CLR_DEL)
            else:
                self._append_colored(line + "\n", _CLR_DEF)

    def _append_colored(self, text: str, color: wx.Colour):
        ctrl = self._preview
        attr = wx.TextAttr(color)
        start = ctrl.GetLastPosition()
        ctrl.AppendText(text)
        ctrl.SetStyle(start, ctrl.GetLastPosition(), attr)

    def get_selected_index(self):
        return self._selected_index
