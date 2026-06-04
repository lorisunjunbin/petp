import logging

import wx
import wx.propgrid

from utils.DateUtil import DateUtil

import time


class SnapshotManager:
    """Snapshot / Undo / Redo state machine, extracted from PETPPresenter.

    Holds two independent snapshot stacks:
      - Execution side: taskGrid + loops + mcp_desc + astool
      - Pipeline  side: executionGrid row contents

    All methods delegate back to the Presenter via ``self.p`` to access view
    and internal helpers. The Presenter keeps thin wrappers (``_push_snapshot``
    etc.) to avoid touching ~30 existing call sites.
    """

    _SNAPSHOT_MAX_DEFAULT: int = 20
    _PIPELINE_SNAPSHOT_MAX: int = 20

    def __init__(self, presenter):
        self.p = presenter

        # Execution side
        self.snapshots: list = []
        self.snapshot_cursor: int = -1
        self.SNAPSHOT_MAX: int = int(getattr(presenter.m, 'snapshot_max', self._SNAPSHOT_MAX_DEFAULT))
        self.saved_snapshot = None

        # Pipeline side
        self.pipeline_snapshots: list = []
        self.pipeline_snapshot_cursor: int = -1

    # ------------------------------------------------------------------
    # Execution side
    # ------------------------------------------------------------------

    def reset_execution(self):
        """Clear the stack when switching execution (was lines 1019-1020 / 1062-1063)."""
        self.snapshots.clear()
        self.snapshot_cursor = -1

    def can_undo(self) -> bool:
        return self.snapshot_cursor >= 0

    def can_redo(self) -> bool:
        return self.snapshot_cursor < len(self.snapshots) - 1

    def has_snapshots(self) -> bool:
        return len(self.snapshots) > 0

    def is_dirty(self) -> bool:
        if self.saved_snapshot is None:
            return False
        current = self.capture_snapshot()
        return (
                current["tasks"] != self.saved_snapshot["tasks"]
                or current["loops"] != self.saved_snapshot["loops"]
                or current["mcp_desc"] != self.saved_snapshot["mcp_desc"]
                or current["astool"] != self.saved_snapshot["astool"]
        )

    def mark_clean(self):
        self.saved_snapshot = self.capture_snapshot()
        self.p._update_save_button()

    def capture_snapshot(self) -> dict:
        v = self.p.v
        grid = v.taskGrid
        tasks = []
        for r in range(grid.GetNumberRows()):
            t_type = grid.GetCellValue(r, 0)
            t_input = grid.GetCellValue(r, 1)
            if not t_type and not t_input:
                break
            tasks.append({"type": t_type, "input": t_input})

        loops = []
        page = v.loopProperty.GetPage(self.p.single_page)
        for prop in page.GetPyIterator(wx.propgrid.PG_ITERATE_ALL):
            if isinstance(prop, wx.propgrid.PropertyCategory):
                continue
            loops.append({"loop_code": prop.GetName(), "loop_attributes": prop.GetValue()})

        return {
            "timestamp": DateUtil.get_now_in_str("%H:%M:%S"),
            "tasks": tasks,
            "loops": loops,
            "mcp_desc": v.execution_desc.GetValue(),
            "astool": v.cb_astool.IsChecked(),
        }

    def restore_snapshot(self, snap: dict):
        p = self.p
        v = p.v
        prev_row = p.current_selected_row
        grid = v.taskGrid
        grid.BeginBatch()
        grid.ClearGrid()

        tasks = snap["tasks"]
        while grid.GetNumberRows() < len(tasks):
            p._insert_row(grid, p.available_processors)

        for idx, task in enumerate(tasks):
            grid.SetCellValue(idx, 0, task["type"])
            grid.SetCellValue(idx, 1, task["input"])

        p._apply_all_row_skip_styles()
        grid.EndBatch()

        p._reset_loop_pgrid()
        loop_page = v.loopProperty.GetPage(p.single_page)
        for loop in snap["loops"]:
            p._append_or_update_property_to_page(loop["loop_code"], loop["loop_attributes"], loop_page)

        v.execution_desc.SetValue(snap["mcp_desc"])
        v.cb_astool.SetValue(snap["astool"])

        name = v.executionChooser.GetValue()
        if snap["astool"]:
            p._tool_names.add(name)
        else:
            p._tool_names.discard(name)

        p._pgrid_bound_row = -1
        p._reset_task_pgrid()

        if prev_row >= 0 and prev_row < grid.GetNumberRows():
            grid.SelectRow(prev_row)
            p._load_input_taskproperty(prev_row)

    def push_snapshot(self):
        snap = self.capture_snapshot()
        del self.snapshots[self.snapshot_cursor + 1:]
        self.snapshots.append(snap)
        if len(self.snapshots) > self.SNAPSHOT_MAX:
            self.snapshots.pop(0)
        self.snapshot_cursor = len(self.snapshots) - 1
        self.p._update_save_button()

    def undo(self):
        if self.snapshot_cursor < 0:
            return
        snap = self.snapshots[self.snapshot_cursor]
        current = self.capture_snapshot()
        self.snapshots[self.snapshot_cursor] = current
        self.restore_snapshot(snap)
        self.snapshot_cursor -= 1
        self.p._update_save_button()
        logging.debug(f'Undo → snapshot @{snap["timestamp"]}')

    def redo(self):
        if self.snapshot_cursor >= len(self.snapshots) - 1:
            return
        self.snapshot_cursor += 1
        snap = self.snapshots[self.snapshot_cursor]
        current = self.capture_snapshot()
        self.snapshots[self.snapshot_cursor] = current
        self.restore_snapshot(snap)
        self.p._update_save_button()
        logging.debug(f'Redo → snapshot @{snap["timestamp"]}')

    # ------------------------------------------------------------------
    # Pipeline side
    # ------------------------------------------------------------------

    def reset_pipeline(self):
        self.pipeline_snapshots = []
        self.pipeline_snapshot_cursor = -1

    def push_pipeline_snapshot(self):
        snap = self.capture_pipeline_snapshot()
        self.pipeline_snapshots = self.pipeline_snapshots[:self.pipeline_snapshot_cursor + 1]
        self.pipeline_snapshots.append(snap)
        if len(self.pipeline_snapshots) > self._PIPELINE_SNAPSHOT_MAX:
            self.pipeline_snapshots.pop(0)
        self.pipeline_snapshot_cursor = len(self.pipeline_snapshots) - 1

    def capture_pipeline_snapshot(self) -> dict:
        grid = self.p.v.executionGrid
        rows = []
        for r in range(grid.GetNumberRows()):
            rows.append((grid.GetCellValue(r, 0), grid.GetCellValue(r, 1)))
        return {"rows": rows, "timestamp": time.time()}

    def undo_pipeline(self):
        if self.pipeline_snapshot_cursor < 0:
            return
        current = self.capture_pipeline_snapshot()
        snap = self.pipeline_snapshots[self.pipeline_snapshot_cursor]
        self.pipeline_snapshots[self.pipeline_snapshot_cursor] = current
        self.restore_pipeline_snapshot(snap)
        self.pipeline_snapshot_cursor -= 1

    def redo_pipeline(self):
        if self.pipeline_snapshot_cursor >= len(self.pipeline_snapshots) - 1:
            return
        self.pipeline_snapshot_cursor += 1
        snap = self.pipeline_snapshots[self.pipeline_snapshot_cursor]
        current = self.capture_pipeline_snapshot()
        self.pipeline_snapshots[self.pipeline_snapshot_cursor] = current
        self.restore_pipeline_snapshot(snap)

    def restore_pipeline_snapshot(self, snap: dict):
        grid = self.p.v.executionGrid
        grid.ClearGrid()
        while grid.GetNumberRows() < len(snap["rows"]):
            grid.InsertRows(grid.GetNumberRows(), 1, True)
        while grid.GetNumberRows() > len(snap["rows"]) and grid.GetNumberRows() > 1:
            grid.DeleteRows(grid.GetNumberRows() - 1, 1)
        for r, (exec_val, input_val) in enumerate(snap["rows"]):
            grid.SetCellValue(r, 0, exec_val)
            grid.SetCellValue(r, 1, input_val)
