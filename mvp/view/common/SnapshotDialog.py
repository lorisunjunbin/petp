import json
import os

import wx

from i18n.translations import t
from mvp.view.common.ThemedButton import ThemedButton


class SnapshotDialog(wx.Dialog):

    def __init__(self, parent, snapshots, cursor):
        style = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
        super().__init__(parent, title=t("dlg_snapshot_title"), style=style)

        self._snapshots = snapshots
        self._cursor = cursor
        self._selected_index = None

        self._build_ui()
        self._try_set_icon()
        self.SetSize((720, 480))
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
        self._preview.SetFont(wx.Font(wx.FontInfo(12).Family(wx.FONTFAMILY_MODERN)))

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
        snap = self._snapshots[idx]
        display = json.dumps(snap, indent=2, ensure_ascii=False)
        self._preview.SetValue(display)

    def get_selected_index(self):
        return self._selected_index
