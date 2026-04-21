import json

import wx
import wx.grid

from i18n.translations import t

from mvp.view.common.ResultDialog import ResultDialog

_TYPE_CHOICES = ["string", "integer", "number", "boolean", "array", "object"]


class McpDescEditor(wx.ScrolledWindow):
    """Structured editor for MCP tool descriptors.

    Drop-in replacement for the old multiline TextCtrl. Exposes the same
    ``GetValue()``/``SetValue(str)``/``Clear()`` interface so the presenter's
    snapshot, undo, dirty-check, and save logic works unchanged.
    """

    def __init__(self, parent, id: int = wx.ID_ANY):
        super().__init__(parent, style=wx.BORDER_NONE | wx.TAB_TRAVERSAL)
        self.SetScrollRate(0, 10)
        self.ShowScrollbars(wx.SHOW_SB_NEVER, wx.SHOW_SB_DEFAULT)
        self._execution_name = ""
        self._on_before_change_callback = None
        self._on_after_change_callback = None
        self._on_undo_callback = None
        self._on_redo_callback = None
        self._suppress_change = False
        self._text_snapshot_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._on_text_snapshot_timer, self._text_snapshot_timer)
        self._build_ui()
        self._bind_events()
        self.Bind(wx.EVT_WINDOW_DESTROY, self._on_destroy)

    # ------------------------------------------------------------------ #
    # Public API (matches wx.TextCtrl interface used by the presenter)
    # ------------------------------------------------------------------ #

    def GetValue(self) -> str:
        desc = self._desc_text.GetValue().strip()
        has_input = any(
            self._input_grid.GetCellValue(r, 0).strip()
            for r in range(self._input_grid.GetNumberRows())
        )
        has_output = any(
            self._output_grid.GetCellValue(r, 0).strip()
            for r in range(self._output_grid.GetNumberRows())
        )
        if not desc and not has_input and not has_output:
            return ""

        result = {"desc": desc}
        exec_name = self._execution_name or "Tool"

        properties = {}
        required = []
        for row in range(self._input_grid.GetNumberRows()):
            name = self._input_grid.GetCellValue(row, 0).strip()
            if not name:
                continue
            ptype = self._input_grid.GetCellValue(row, 1) or "string"
            is_req = self._input_grid.GetCellValue(row, 2) == "1"
            pdesc = self._input_grid.GetCellValue(row, 3)
            properties[name] = {"title": name, "type": ptype, "description": pdesc}
            if is_req:
                required.append(name)
        result["inputSchema"] = {
            "type": "object",
            "title": f"{exec_name}Arguments",
            "properties": properties,
            "required": required,
        }

        out_properties = {}
        out_required = []
        for row in range(self._output_grid.GetNumberRows()):
            name = self._output_grid.GetCellValue(row, 0).strip()
            if not name:
                continue
            ptype = self._output_grid.GetCellValue(row, 1) or "string"
            pdesc = self._output_grid.GetCellValue(row, 2)
            out_properties[name] = {"title": name, "type": ptype, "description": pdesc}
            out_required.append(name)
        if out_properties:
            result["outputSchema"] = {
                "type": "object",
                "title": f"{exec_name}Output",
                "properties": out_properties,
                "required": out_required,
            }

        return json.dumps(result, indent=2, ensure_ascii=False)

    def SetValue(self, value: str):
        self._suppress_change = True
        try:
            self.Clear()
            if not value or not value.strip():
                return

            parsed = self._parse_json(value)
            if parsed is None:
                self._desc_text.SetValue(value)
                return

            self._desc_text.SetValue(parsed.get("desc", ""))

            input_schema = parsed.get("inputSchema")
            if isinstance(input_schema, dict):
                props = input_schema.get("properties", {})
                req_list = input_schema.get("required", [])
                for name, spec in props.items():
                    self._add_input_row(
                        name, spec.get("type", "string"),
                        spec.get("description", ""), name in req_list,
                    )
            elif "params" in parsed:
                params = parsed["params"]
                if isinstance(params, list):
                    for p in params:
                        if isinstance(p, str) and p.strip():
                            self._add_input_row(p, "string", "", True)

            output_schema = parsed.get("outputSchema")
            if isinstance(output_schema, dict):
                props = output_schema.get("properties", {})
                for name, spec in props.items():
                    self._add_output_row(
                        name, spec.get("type", "string"), spec.get("description", ""),
                    )
            elif "outParams" in parsed:
                out_params = parsed["outParams"]
                if isinstance(out_params, list):
                    for p in out_params:
                        if isinstance(p, str) and p.strip():
                            self._add_output_row(p, "string", "")
        finally:
            self._suppress_change = False
        self._fit_grid_height(self._input_grid)
        self._fit_grid_height(self._output_grid)

    def Clear(self):
        prev = self._suppress_change
        self._suppress_change = True
        try:
            self._desc_text.Clear()
            if self._input_grid.GetNumberRows() > 0:
                self._input_grid.DeleteRows(0, self._input_grid.GetNumberRows())
            if self._output_grid.GetNumberRows() > 0:
                self._output_grid.DeleteRows(0, self._output_grid.GetNumberRows())
        finally:
            self._suppress_change = prev
        self._fit_grid_height(self._input_grid)
        self._fit_grid_height(self._output_grid)

    def SetToolTip(self, tip):
        self._desc_text.SetToolTip(tip)

    def set_execution_name(self, name: str):
        self._execution_name = name

    def set_on_change(self, before_callback, after_callback):
        self._on_before_change_callback = before_callback
        self._on_after_change_callback = after_callback

    def set_on_undo(self, callback):
        self._on_undo_callback = callback

    def set_on_redo(self, callback):
        self._on_redo_callback = callback

    def apply_i18n(self):
        self._lbl_desc.SetLabel(t("mcp_lbl_tool_desc"))
        self._lbl_input.SetLabel(t("mcp_lbl_input_params"))
        self._lbl_output.SetLabel(t("mcp_lbl_output_params"))
        self._btn_add_input.SetToolTip(t("mcp_tip_add_input"))
        self._btn_del_input.SetToolTip(t("mcp_tip_del_input"))
        self._btn_add_output.SetToolTip(t("mcp_tip_add_output"))
        self._btn_del_output.SetToolTip(t("mcp_tip_del_output"))
        self._desc_text.SetToolTip(t("mcp_tip_tool_desc"))
        self._btn_preview.SetToolTip(t("mcp_tip_preview_json"))

        for grid, cols in [
            (self._input_grid, [
                t("mcp_col_name"), t("mcp_col_type"),
                t("mcp_col_required"), t("mcp_col_desc"),
            ]),
            (self._output_grid, [
                t("mcp_col_name"), t("mcp_col_type"), t("mcp_col_desc"),
            ]),
        ]:
            for i, label in enumerate(cols):
                grid.SetColLabelValue(i, label)
            grid.ForceRefresh()

    # ------------------------------------------------------------------ #
    # UI construction
    # ------------------------------------------------------------------ #

    def _build_ui(self):
        main = wx.BoxSizer(wx.VERTICAL)

        # --- description row: label + text + { } preview ---
        desc_row = wx.BoxSizer(wx.HORIZONTAL)
        self._lbl_desc = wx.StaticText(self, label=t("mcp_lbl_tool_desc"))
        desc_row.Add(self._lbl_desc, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 4)
        self._desc_text = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER)
        desc_row.Add(self._desc_text, 1, wx.ALIGN_CENTER_VERTICAL)
        self._btn_preview = wx.Button(self, label="{ }", size=(36, 24))
        self._btn_preview.SetToolTip(t("mcp_tip_preview_json"))
        desc_row.Add(self._btn_preview, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 4)
        main.Add(desc_row, 0, wx.EXPAND | wx.ALL, 3)

        # --- input parameters: label ... +/- buttons ---
        inp_hdr = wx.BoxSizer(wx.HORIZONTAL)
        self._lbl_input = wx.StaticText(self, label=t("mcp_lbl_input_params"))
        inp_hdr.Add(self._lbl_input, 0, wx.ALIGN_CENTER_VERTICAL)
        inp_hdr.AddStretchSpacer()
        self._btn_add_input = wx.Button(self, label="+", size=(28, 24))
        self._btn_del_input = wx.Button(self, label="-", size=(28, 24))
        self._btn_add_input.SetToolTip(t("mcp_tip_add_input"))
        self._btn_del_input.SetToolTip(t("mcp_tip_del_input"))
        inp_hdr.Add(self._btn_add_input, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 2)
        inp_hdr.Add(self._btn_del_input, 0, wx.ALIGN_CENTER_VERTICAL)
        main.Add(inp_hdr, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 3)

        self._input_grid = self._create_grid(4, [
            (t("mcp_col_name"), 80),
            (t("mcp_col_type"), 70),
            (t("mcp_col_required"), 60),
            (t("mcp_col_desc"), 80),
        ])
        main.Add(self._input_grid, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 3)

        # --- output parameters: label ... +/- buttons ---
        out_hdr = wx.BoxSizer(wx.HORIZONTAL)
        self._lbl_output = wx.StaticText(self, label=t("mcp_lbl_output_params"))
        out_hdr.Add(self._lbl_output, 0, wx.ALIGN_CENTER_VERTICAL)
        out_hdr.AddStretchSpacer()
        self._btn_add_output = wx.Button(self, label="+", size=(28, 24))
        self._btn_del_output = wx.Button(self, label="-", size=(28, 24))
        self._btn_add_output.SetToolTip(t("mcp_tip_add_output"))
        self._btn_del_output.SetToolTip(t("mcp_tip_del_output"))
        out_hdr.Add(self._btn_add_output, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 2)
        out_hdr.Add(self._btn_del_output, 0, wx.ALIGN_CENTER_VERTICAL)
        main.Add(out_hdr, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 3)

        self._output_grid = self._create_grid(3, [
            (t("mcp_col_name"), 80),
            (t("mcp_col_type"), 70),
            (t("mcp_col_desc"), 80),
        ])
        main.Add(self._output_grid, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 3)

        self.SetSizer(main)

    def _create_grid(self, num_cols, col_defs):
        grid = wx.grid.Grid(self, style=wx.BORDER_NONE)
        grid.CreateGrid(0, num_cols)
        grid.SetRowLabelSize(0)
        grid.DisableDragRowSize()
        grid.SetDefaultRowSize(24)
        grid.SetColLabelSize(22)
        grid.EnableScrolling(False, False)
        grid.ShowScrollbars(wx.SHOW_SB_NEVER, wx.SHOW_SB_NEVER)
        grid.GetGridWindow().Bind(wx.EVT_MOUSEWHEEL, self._on_child_mousewheel)
        for i, (label, width) in enumerate(col_defs):
            grid.SetColLabelValue(i, label)
            grid.SetColSize(i, width)
        return grid

    def _fit_grid_height(self, grid):
        row_count = grid.GetNumberRows()
        height = grid.GetColLabelSize() + row_count * grid.GetDefaultRowSize()
        if row_count == 0:
            height = grid.GetColLabelSize()
        grid.SetMinSize((-1, height))
        grid.SetMaxSize((-1, height))
        self.Layout()
        self.FitInside()

    def _bind_events(self):
        self._btn_add_input.Bind(wx.EVT_BUTTON, self._on_add_input)
        self._btn_del_input.Bind(wx.EVT_BUTTON, self._on_del_input)
        self._btn_add_output.Bind(wx.EVT_BUTTON, self._on_add_output)
        self._btn_del_output.Bind(wx.EVT_BUTTON, self._on_del_output)
        self._btn_preview.Bind(wx.EVT_BUTTON, self._on_preview_json)
        self._desc_text.Bind(wx.EVT_TEXT, self._on_text_change)
        self._desc_text.Bind(wx.EVT_KEY_DOWN, self._on_key_down)
        self._input_grid.Bind(wx.grid.EVT_GRID_CELL_CHANGED, self._on_grid_change)
        self._output_grid.Bind(wx.grid.EVT_GRID_CELL_CHANGED, self._on_grid_change)
        self._input_grid.Bind(wx.EVT_KEY_DOWN, self._on_key_down)
        self._output_grid.Bind(wx.EVT_KEY_DOWN, self._on_key_down)
        self.Bind(wx.EVT_SIZE, self._on_resize)

    # ------------------------------------------------------------------ #
    # Grid row helpers
    # ------------------------------------------------------------------ #

    def _add_input_row(self, name="", ptype="string", desc="", required=True):
        grid = self._input_grid
        row = grid.GetNumberRows()
        grid.AppendRows(1)
        grid.SetCellValue(row, 0, name)
        grid.SetCellEditor(row, 1, wx.grid.GridCellChoiceEditor(_TYPE_CHOICES))
        grid.SetCellValue(row, 1, ptype)
        grid.SetCellRenderer(row, 2, wx.grid.GridCellBoolRenderer())
        grid.SetCellEditor(row, 2, wx.grid.GridCellBoolEditor())
        grid.SetCellAlignment(row, 2, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
        grid.SetCellValue(row, 2, "1" if required else "")
        grid.SetCellValue(row, 3, desc)
        self._fit_grid_height(grid)

    def _add_output_row(self, name="", ptype="string", desc=""):
        grid = self._output_grid
        row = grid.GetNumberRows()
        grid.AppendRows(1)
        grid.SetCellValue(row, 0, name)
        grid.SetCellEditor(row, 1, wx.grid.GridCellChoiceEditor(_TYPE_CHOICES))
        grid.SetCellValue(row, 1, ptype)
        grid.SetCellValue(row, 2, desc)
        self._fit_grid_height(grid)

    def _del_selected_row(self, grid):
        rows = grid.GetSelectedRows()
        if rows:
            grid.DeleteRows(rows[0], 1)
        elif grid.GetGridCursorRow() >= 0:
            grid.DeleteRows(grid.GetGridCursorRow(), 1)
        self._fit_grid_height(grid)

    # ------------------------------------------------------------------ #
    # Event handlers
    # ------------------------------------------------------------------ #

    def _on_add_input(self, _evt):
        self._fire_before_change()
        self._add_input_row()
        self._fire_after_change()

    def _on_del_input(self, _evt):
        if self._input_grid.GetNumberRows() > 0:
            self._fire_before_change()
            self._del_selected_row(self._input_grid)
            self._fire_after_change()

    def _on_add_output(self, _evt):
        self._fire_before_change()
        self._add_output_row()
        self._fire_after_change()

    def _on_del_output(self, _evt):
        if self._output_grid.GetNumberRows() > 0:
            self._fire_before_change()
            self._del_selected_row(self._output_grid)
            self._fire_after_change()

    def _on_key_down(self, evt):
        if evt.GetModifiers() == wx.MOD_CONTROL:
            key = evt.GetKeyCode()
            if key == ord('Z') and self._on_undo_callback:
                self._flush_text_snapshot()
                self._on_undo_callback()
                return
            if key == ord('Y') and self._on_redo_callback:
                self._flush_text_snapshot()
                self._on_redo_callback()
                return
        if evt.GetModifiers() == (wx.MOD_CONTROL | wx.MOD_SHIFT):
            if evt.GetKeyCode() == ord('Z') and self._on_redo_callback:
                self._flush_text_snapshot()
                self._on_redo_callback()
                return
        evt.Skip()

    def _on_text_change(self, _evt):
        if self._suppress_change:
            return
        self._fire_after_change()
        self._text_snapshot_timer.StartOnce(500)

    def _on_text_snapshot_timer(self, _evt):
        self._fire_before_change()

    def _flush_text_snapshot(self):
        if self._text_snapshot_timer.IsRunning():
            self._text_snapshot_timer.Stop()
            self._fire_before_change()

    def _on_grid_change(self, evt):
        evt.Skip()
        self._fire_change()

    def _on_preview_json(self, _evt):
        json_str = self.GetValue() or ""
        title = self._execution_name or "MCP Tool Descriptor"
        dlg = ResultDialog(self, title=title, message=json_str)
        dlg.ShowModal()
        dlg.Destroy()

    def _fire_change(self):
        self._fire_before_change()
        self._fire_after_change()

    def _fire_before_change(self):
        if not self._suppress_change and self._on_before_change_callback:
            self._on_before_change_callback()

    def _fire_after_change(self):
        if not self._suppress_change and self._on_after_change_callback:
            self._on_after_change_callback()

    def _on_resize(self, evt):
        evt.Skip()
        self._resize_desc_column(self._input_grid, 3)
        self._resize_desc_column(self._output_grid, 2)

    def _on_child_mousewheel(self, evt):
        self.GetEventHandler().ProcessEvent(evt)

    def _on_destroy(self, evt):
        evt.Skip()
        if evt.GetEventObject() is not self:
            return
        self._text_snapshot_timer.Stop()

    def _resize_desc_column(self, grid, desc_col_idx):
        available = self.GetClientSize().width - 6
        fixed = sum(grid.GetColSize(c) for c in range(grid.GetNumberCols()) if c != desc_col_idx)
        remaining = available - fixed
        if remaining > 80:
            grid.SetColSize(desc_col_idx, remaining)

    # ------------------------------------------------------------------ #
    # JSON helpers
    # ------------------------------------------------------------------ #

    @staticmethod
    def _parse_json(value: str):
        normalized = (
            value
            .replace("\u201c", '"')
            .replace("\u201d", '"')
            .replace("\n", "")
            .replace("\uff1a", ":")
        )
        try:
            return json.loads(normalized)
        except json.JSONDecodeError:
            return None
