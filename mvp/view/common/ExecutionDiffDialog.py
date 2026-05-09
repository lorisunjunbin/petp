import difflib
import os
import shutil

import wx

from i18n.translations import t

_CLR_ADD = wx.Colour(0, 128, 0)
_CLR_DEL = wx.Colour(180, 0, 0)
_CLR_HDR = wx.Colour(80, 80, 160)
_CLR_DEF = wx.Colour(80, 80, 80)


class ExecutionDiffDialog(wx.Dialog):

    def __init__(self, parent, current_file: str, variant_files: list):
        style = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
        super().__init__(parent, title=t("dlg_compare_title"), style=style)

        self._current_file = current_file
        self._variant_files = variant_files
        self._selected_index = None

        self._build_ui()
        self._try_set_icon()
        self.SetSize((900, 560))
        self.CentreOnScreen()

    def _build_ui(self):
        sizer = wx.BoxSizer(wx.VERTICAL)

        splitter = wx.SplitterWindow(self, style=wx.SP_LIVE_UPDATE)

        self._list = wx.ListBox(splitter, style=wx.LB_SINGLE)
        for f in self._variant_files:
            self._list.Append(os.path.splitext(os.path.basename(f))[0])

        self._preview = wx.TextCtrl(
            splitter, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2 | wx.HSCROLL
        )
        self._preview.SetFont(wx.Font(wx.FontInfo(11).Family(wx.FONTFAMILY_MODERN)))

        splitter.SplitVertically(self._list, self._preview, 260)
        splitter.SetMinimumPaneSize(150)
        sizer.Add(splitter, 1, wx.EXPAND | wx.ALL, 10)

        btns = wx.BoxSizer(wx.HORIZONTAL)
        btns.AddStretchSpacer()
        self._apply_btn = wx.Button(self, wx.ID_OK, t("btn_apply_version"))
        self._apply_btn.Enable(False)
        close_btn = wx.Button(self, wx.ID_CANCEL, t("btn_close"))
        btns.Add(self._apply_btn, 0, wx.RIGHT, 8)
        btns.Add(close_btn)
        sizer.Add(btns, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 10)

        self.SetSizer(sizer)

        self._list.Bind(wx.EVT_LISTBOX, self._on_select)
        self._apply_btn.Bind(wx.EVT_BUTTON, self._on_apply)

        if self._variant_files:
            self._list.SetSelection(0)
            self._show_diff(0)
            self._apply_btn.Enable(True)
            self._selected_index = 0

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
        self._show_diff(idx)

    def _on_apply(self, evt):
        if self._selected_index is None:
            return
        variant = self._variant_files[self._selected_index]
        shutil.copy2(variant, self._current_file)
        self.EndModal(wx.ID_OK)

    def _show_diff(self, idx):
        self._preview.SetValue("")
        variant_file = self._variant_files[idx]

        try:
            with open(self._current_file, 'r', encoding='utf-8') as f:
                current_lines = f.readlines()
            with open(variant_file, 'r', encoding='utf-8') as f:
                variant_lines = f.readlines()
        except Exception as e:
            self._append_colored(f"Error reading files: {e}", _CLR_DEL)
            return

        current_name = os.path.basename(self._current_file)
        variant_name = os.path.basename(variant_file)

        diff = list(difflib.unified_diff(
            current_lines, variant_lines,
            fromfile=current_name,
            tofile=variant_name,
            lineterm="",
        ))

        if not diff:
            self._append_colored(t("compare_no_changes"), _CLR_DEF)
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
