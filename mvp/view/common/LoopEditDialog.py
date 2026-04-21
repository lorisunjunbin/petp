import json
import os

import wx
import wx.grid

from i18n.translations import t
from mvp.view.common.HandyToolButton import HandyToolButton


class LoopEditDialog(wx.Dialog):
    """Edit a loop's attributes as a fixed key/value form.

    Keys are read-only (loop schema is fixed); only values are editable.
    The dialog title shows the loop_code so the user always knows which
    loop they are editing.
    """

    def __init__(self, parent, loop_code: str, loop_attributes_json: str):
        style = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
        super().__init__(parent, title=t("loop_dlg_title"), style=style)

        self._loop_code = loop_code
        try:
            self._data: dict = json.loads(loop_attributes_json)
        except (json.JSONDecodeError, TypeError):
            self._data = {}

        self._keys = list(self._data.keys())
        self._build_ui()
        self._try_set_icon()
        self.SetMinSize(wx.Size(640, 300))
        self.SetSize(wx.Size(640, 380))
        self.CentreOnScreen()

    # ------------------------------------------------------------------ #
    # UI
    # ------------------------------------------------------------------ #

    def _build_ui(self):
        PAD = 12
        sizer = wx.BoxSizer(wx.VERTICAL)

        # header
        hdr = wx.BoxSizer(wx.HORIZONTAL)
        bmp = wx.ArtProvider.GetBitmap(wx.ART_INFORMATION, wx.ART_MESSAGE_BOX, (28, 28))
        hdr.Add(wx.StaticBitmap(self, bitmap=bmp), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 8)
        lbl = wx.StaticText(self, label=self._loop_code)
        lbl.SetFont(lbl.GetFont().Bold().Scaled(1.3))
        hdr.Add(lbl, 1, wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(hdr, 0, wx.ALL, PAD)
        sizer.Add(wx.StaticLine(self), 0, wx.LEFT | wx.RIGHT | wx.EXPAND, PAD)
        sizer.AddSpacer(PAD // 2)

        # toolbar above grid
        toolbar = wx.BoxSizer(wx.HORIZONTAL)
        toolbar.AddStretchSpacer()
        self._tools_btn = HandyToolButton(
            self,
            get_value=self._get_selected_cell_value,
            set_value=self._set_selected_cell_value,
        )
        toolbar.Add(self._tools_btn, 0, wx.RIGHT, 0)
        sizer.Add(toolbar, 0, wx.LEFT | wx.RIGHT | wx.EXPAND, PAD)
        sizer.AddSpacer(4)

        # grid
        self._grid = wx.grid.Grid(self)
        self._grid.CreateGrid(len(self._keys), 2)
        self._grid.SetColLabelValue(0, t("loop_dlg_col_key"))
        self._grid.SetColLabelValue(1, t("loop_dlg_col_value"))
        self._grid.SetRowLabelSize(0)
        self._grid.DisableDragRowSize()
        self._grid.SetDefaultRowSize(26)

        for row, key in enumerate(self._keys):
            self._grid.SetCellValue(row, 0, key)
            self._grid.SetReadOnly(row, 0, True)
            self._grid.SetCellBackgroundColour(row, 0, wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNFACE))
            self._grid.SetCellValue(row, 1, str(self._data[key]))

        self._grid.AutoSizeColumn(0)
        self._grid.AutoSizeColumn(1)
        self._grid.SetColMinimalWidth(1, 200)

        sizer.Add(self._grid, 1, wx.LEFT | wx.RIGHT | wx.EXPAND, PAD)
        sizer.AddSpacer(PAD)

        # buttons
        btns = wx.BoxSizer(wx.HORIZONTAL)
        cancel_btn = wx.Button(self, wx.ID_CANCEL, t("dlg_cancel"))
        ok_btn = wx.Button(self, wx.ID_OK, t("dlg_ok"))
        ok_btn.SetDefault()
        ok_btn.Bind(wx.EVT_BUTTON, self._on_ok)
        btns.AddStretchSpacer()
        btns.Add(cancel_btn, 0, wx.RIGHT, 8)
        btns.Add(ok_btn)
        sizer.Add(btns, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, PAD)

        self.SetSizer(sizer)
        self.Bind(wx.EVT_SIZE, self._on_resize)

    # ------------------------------------------------------------------ #
    # Grid cell accessors for HandyToolButton
    # ------------------------------------------------------------------ #

    def _commit_cell_edit(self):
        if self._grid.IsCellEditControlEnabled():
            self._grid.SaveEditControlValue()
            self._grid.HideCellEditControl()

    def _get_selected_cell_value(self):
        self._commit_cell_edit()
        row = self._grid.GetGridCursorRow()
        if row < 0:
            return None
        return self._grid.GetCellValue(row, 1)

    def _set_selected_cell_value(self, value):
        self._commit_cell_edit()
        row = self._grid.GetGridCursorRow()
        if row < 0:
            return
        self._grid.SetCellValue(row, 1, value)

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #

    def _try_set_icon(self):
        icon_path = os.path.realpath(os.path.join('.', 'image', 'petp_small.png'))
        if os.path.isfile(icon_path):
            try:
                self.SetIcon(wx.Icon(icon_path))
            except Exception:
                pass

    def _on_resize(self, evt):
        evt.Skip()
        total = self._grid.GetClientSize().width - self._grid.GetColSize(0)
        if total > 0:
            self._grid.SetColSize(1, total)

    def _on_ok(self, _evt):
        if self._grid.IsCellEditControlEnabled():
            self._grid.SaveEditControlValue()
            self._grid.HideCellEditControl()

        result = {}
        for row, key in enumerate(self._keys):
            raw = self._grid.GetCellValue(row, 1)
            orig = self._data.get(key)
            if isinstance(orig, int):
                try:
                    raw = int(raw)
                except ValueError:
                    pass
            elif isinstance(orig, float):
                try:
                    raw = float(raw)
                except ValueError:
                    pass
            result[key] = raw
        self._result_json = json.dumps(result)
        self.EndModal(wx.ID_OK)

    def get_result_json(self) -> str:
        return self._result_json
