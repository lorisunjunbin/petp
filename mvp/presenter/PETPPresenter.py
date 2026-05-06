import json
import logging
import random
import concurrent.futures
import time
from threading import Thread

import wx
import os
from cron_descriptor import ExpressionDescriptor

from core.cron.cron import Cron
from core.cron.cron_history import CronHistory
from core.definition.ChromeRecorderConverter import ChromeRecorderConverter
from core.execution import Execution
from core.executor import Executor
from core.loop import Loop
from core.pipeline import Pipeline
from core.processor import Processor
from core.task import Task
from mvp.model.PETPModel import PETPModel
from mvp.presenter.PETPInteractor import PETPInteractor
from mvp.presenter.event.PETPEvent import PETPEvent
from mvp.view.common.InputDialog import InputDialog
from mvp.view.common.SearchableGridChoiceEditor import SearchableGridChoiceEditor
from mvp.view.common.ProcessorPalette import ProcessorPalette
from mvp.view.common.TaskInfoRenderer import TaskInfoRenderer
from mvp.view.sub.PETP_LINE_CHARTView import PETP_LINE_CHARTView
from mvp.view.sub.PETP_PIE_CHARTView import PETP_PIE_CHARTView
from mvp.view.sub.PETP_BAR_CHARTView import PETP_BAR_CHARTView
from mvp.view.PETPView import PETPView
from utils.DateUtil import DateUtil
from utils.OSUtils import OSUtils
from utils.CodeExplainerUtil import CodeExplainerUtil
from i18n.translations import t, set_locale
from mvp.view.PETPTheme import get_theme, set_theme, get_theme_names, is_system_theme, SYSTEM_THEME_NAME


class PETPPresenter():
    CRON_INVALID: str = "msg_cron_invalid"

    cron: Cron
    execution: Execution
    executors: list = []
    pipeline: Pipeline
    converter: ChromeRecorderConverter

    available_processors: list = []
    available_executions: list = []

    current_selected_row: int = -1
    _pgrid_bound_row: int = -1  # row the property grid is currently showing
    is_log_content_focused: bool = False
    single_page: str = "petp"
    logger_thread = None
    keep_running = True

    def __init__(self, model: PETPModel, view: PETPView, interactor: PETPInteractor):

        self.m = model
        self.v = view
        self.i = interactor

        # Incremental log loading state
        self._log_last_pos = 0
        self._log_fd = None
        self._log_ino = None

        self._snapshots = []
        self._snapshot_cursor = -1
        self._SNAPSHOT_MAX = int(getattr(model, 'snapshot_max', 20))
        self._saved_snapshot = None
        self._param_hint_dlg = None
        self._log_search_keyword = ''
        self._log_match_positions = []
        self._log_match_cursor = -1
        self._log_filter_active = False
        self._log_full_content = ''  # raw content kept for filter re-apply
        self._exec_start_time = 0.0
        self._cron_history = CronHistory()

        self._log_timer = wx.Timer(view)
        view.Bind(wx.EVT_TIMER, self._on_log_timer, self._log_timer)
        self._log_timer.Start(1000)

        self.i.install(self, view)

        view.execution_desc.set_on_change(self._push_snapshot, self._update_save_button)
        view.execution_desc.set_on_undo(self._undo)
        view.execution_desc.set_on_redo(self._redo)
        view.execution_desc.set_on_sync_input(self._on_sync_input_from_task)
        view.execution_desc.set_on_sync_output(self._on_sync_output_from_task)
        view.execution_desc.set_on_ai_generate(self._on_ai_generate_mcp_desc)

        logging.info('Init PETPPresenter')

        self._load_available_executions()
        self._load_available_pipelines()

        self._init_taskgrid_choice_editor()
        self._init_executiongrid_choice_editor()
        self._init_cron()
        self._init_property_grid()
        self._init_handy_tools()
        self._init_theme_chooser()

        self._apply_i18n()
        self._apply_theme()
        self._load_config()

        wx.CallAfter(self._sync_mcp_panel_visibility)

        view.Bind(wx.EVT_SYS_COLOUR_CHANGED, self._on_sys_appearance_changed)

        self._welcome_index = random.randrange(20)
        self._welcome_total = 20
        self._welcome_paused = False
        wx.CallLater(800, self._rotate_welcome)

    def _rotate_welcome(self):
        if self.v is None:
            return
        if not self._welcome_paused:
            key = f"welcome_{self._welcome_index % self._welcome_total}"
            self._set_highlight_info(t(key))
            self._welcome_index += 1
        wx.CallLater(60000, self._rotate_welcome)

    def _resume_welcome(self):
        self._welcome_paused = False

    def _handle_execute_on_startup(self):
        if self.m.execute_on_startup:
            logging.info(f"execute on startup is enabled, will run execution: {self.m.last_run}")
            self.on_run_execution()

    def _apply_i18n(self):
        v = self.v

        # Window title
        v.SetTitle(t("win_title"))

        # Notebook tabs
        v.notebook.SetPageText(0, t("tab_executions"))
        v.notebook.SetPageText(1, t("tab_pipelines"))

        # --- Execution tab: task editor ---
        v.addRow4E.SetToolTip(t("tip_add_row"))
        v.delRow4E.SetToolTip(t("tip_delete_row"))
        v.selectRecording.SetLabel(t("btn_select"))
        v.selectRecording.SetToolTip(t("tip_select_recording"))
        v.loadRecording.SetLabel(t("btn_convert"))
        v.loadRecording.SetToolTip(t("tip_convert_recording"))

        # Task grid headers
        v.taskGrid.SetColLabelValue(0, t("grid_task_chooser"))
        v.taskGrid.SetColLabelValue(1, t("grid_task_desc"))

        # Loop editor
        v.addLoop.SetToolTip(t("tip_add_property"))
        v.delLoop.SetToolTip(t("tip_delete_property"))
        v.editLoop.SetLabel(t("btn_edit_loop"))
        v.editLoop.SetToolTip(t("tip_edit_loop"))
        v.editLoop.Enable(False)

        # Input editor
        v.availableProperties.SetToolTip(t("tip_available_properties"))
        v.addProperty.SetToolTip(t("tip_add_prop"))
        v.delProperty.SetToolTip(t("tip_delete_prop"))
        v.cb_skipped.SetToolTip(t("tip_skip_task"))
        v.datepicker.SetToolTip(t("tip_fill_date"))

        # Execution description & MCP tool
        v.execution_desc.apply_i18n()
        v.cb_astool.set_state_labels(t("astool_on"), t("astool_off"))
        v.cb_astool.SetToolTip(t("tip_as_mcp_tool"))
        v.only_tool.set_state_labels(t("only_tool_on"), t("only_tool_off"))
        v.only_tool.SetToolTip(t("tip_only_tool"))

        # Execution action buttons
        v.delExecution.SetLabel(t("btn_delete"))
        v.delExecution.SetToolTip(t("tip_delete_execution"))
        v.copyExecution.SetLabel(t("btn_copy"))
        v.copyExecution.SetToolTip(t("tip_copy_execution"))
        v.addExecution.SetToolTip(t("tip_create_execution"))
        v.saveExection.SetLabel(t("btn_save"))
        v.saveExection.SetToolTip(t("tip_save_execution"))
        v.stopExection.SetLabel(t("btn_stop"))
        v.runExecution.SetLabel(t("btn_run_execution"))
        v.snapshots.SetLabel(t("menu_snapshots"))
        v.snapshots.SetToolTip(t("tip_snapshots"))
        v.checkbox_executeonstartup.SetToolTip(t("tip_execute_on_startup"))
        v.langChooser.SetToolTip(t("tip_change_lang"))
        v.themeChooser.SetToolTip(t("tip_change_theme"))

        sb = v.logSearchBar
        sb.logLevelBtn.SetToolTip(t("tip_change_log_level"))
        sb.cleanBtn.SetToolTip(t("tip_clean_log"))
        sb.textCtrl.SetHint(t("tip_log_search"))
        sb.prevBtn.SetLabel(t("label_find_prev"))
        sb.prevBtn.SetToolTip(t("tip_find_prev"))
        sb.nextBtn.SetLabel(t("label_find_next"))
        sb.nextBtn.SetToolTip(t("tip_find_next"))
        sb.filterBtn.SetToolTip(t("tip_filter_log"))

        # --- Pipeline tab ---
        v.addRow4P.SetToolTip(t("tip_add_row_p"))
        v.delRow4P.SetToolTip(t("tip_delete_row_p"))
        v.executionGrid.SetColLabelValue(0, t("grid_exec_chooser"))
        v.executionGrid.SetColLabelValue(1, t("grid_input"))
        v.delPipeline.SetLabel(t("btn_delete"))
        v.delPipeline.SetToolTip(t("tip_delete_pipeline"))
        v.savePipeline.SetLabel(t("btn_save"))
        v.savePipeline.SetToolTip(t("tip_save_pipeline"))
        v.runPipeline.SetLabel(t("btn_run_pipeline"))
        v.asCronChecbox.SetLabel(t("cb_as_cron"))
        v.stopCurrentCron.SetLabel(t("btn_stop"))
        v.stopCurrentCron.SetToolTip(t("tip_stop_cron"))
        v.stopAll.SetLabel(t("btn_stop_all"))
        v.stopAll.SetToolTip(t("tip_stop_all_cron"))
        v.cronDashboardBtn.SetLabel(t("btn_cron_history"))
        v.cronDashboardBtn.SetToolTip(t("tip_cron_history"))

        # Property grid category labels
        self._update_pgrid_category(
            v.taskProperty,
            t("pgrid_input_editor_of") + str(self._pgrid_bound_row + 1)
            if self._pgrid_bound_row >= 0 else t("pgrid_input_editor")
        )
        self._update_pgrid_category(v.loopProperty, t("pgrid_loop_editor"))

    def _apply_theme(self):
        v = self.v
        th = get_theme()

        sel_bg = wx.Colour(*th.grid_sel_bg)
        sel_fg = wx.Colour(*th.grid_sel_fg)
        for grid in (v.taskGrid, v.executionGrid):
            grid.SetSelectionBackground(sel_bg)
            grid.SetSelectionForeground(sel_fg)
            grid.ForceRefresh()

        pg_bg = wx.Colour(*th.pgrid_sel_bg)
        pg_fg = wx.Colour(*th.pgrid_sel_fg)
        for pgm in (v.taskProperty, v.loopProperty):
            pg = pgm.GetGrid()
            pg.SetSelectionBackgroundColour(pg_bg)
            pg.SetSelectionTextColour(pg_fg)
            pg.Refresh()

        log_bg = wx.Colour(*th.log_bg)
        log_fg = wx.Colour(*th.log_fg)
        search_bg = wx.Colour(*th.log_search_bg)
        search_fg = wx.Colour(*th.log_search_fg)

        v.logPanel.SetBackgroundColour(log_bg)
        v.logContents.SetBackgroundColour(log_bg)
        v.logContents.SetForegroundColour(log_fg)
        v.logSearchBar.apply_theme(th)
        v.highlightInfo.SetForegroundColour(wx.Colour(*th.accent))

        v.logPanel.Refresh()
        lc = v.logContents
        if lc.GetLastPosition() > 0:
            lc.Freeze()
            try:
                lc.SetStyle(0, lc.GetLastPosition(), wx.TextAttr(log_fg, log_bg))
            finally:
                lc.Thaw()
        lc.Refresh()

        v.execution_desc.apply_theme(th)

        v.runExecution.apply_theme()
        v.runPipeline.apply_theme()
        v.cb_astool.apply_theme()

    @staticmethod
    def _update_pgrid_category(pgm, label):
        page = pgm.GetPage(0)
        if page is None:
            return
        for prop in page.GetPyIterator(wx.propgrid.PG_ITERATE_ALL):
            if isinstance(prop, wx.propgrid.PropertyCategory):
                prop.SetLabel(label)
                break
        pgm.Refresh()

    def _init_theme_chooser(self):
        v = self.v
        theme_names = get_theme_names()
        v.themeChooser.Set(theme_names)
        saved = getattr(self.m, 'theme', 'Forest')
        if saved in theme_names:
            v.themeChooser.SetValue(saved)
            set_theme(saved)
        else:
            v.themeChooser.SetValue('Forest')

    def _load_config(self):
        # load_executeonstartup
        if self.m.execute_on_startup is not None:
            self.v.checkbox_executeonstartup.SetValue(self.m.execute_on_startup)

        # load_log_level
        if self.m.log_level is not None:
            self.v.logSearchBar.set_log_level(self.m.log_level)

        # load_language
        lang = getattr(self.m, 'language', 'zh')
        self.v.langChooser.SetValue("中文" if lang == "zh" else "EN")

        # load http_port, as part of title
        self.v.SetTitle(self.v.GetTitle() + " [ " + str(self.m.http_port) + " ]")

        # load_last_run
        if self.m.last_run is not None:
            logging.info("loading last run: " + self.m.last_run)
            self.v.executionChooser.SetValue(self.m.last_run)
            self.on_task_execution_changed()

    def _init_property_grid(self):
        self.v.taskProperty.AddPage(self.single_page)
        self._append_property_category(self.v.taskProperty, t("pgrid_input_editor"))

        self.v.loopProperty.AddPage(self.single_page)
        self._append_property_category(self.v.loopProperty, t("pgrid_loop_editor"))

    def _append_property_category(self, propgrid_manager, category_name):
        page = propgrid_manager.GetPage(self.single_page)
        page.Append(wx.propgrid.PropertyCategory(category_name))

    def _reset_task_pgrid(self, task_number=0):
        self.v.taskProperty.ClearPage(self.v.taskProperty.GetPageByName(self.single_page))
        self._append_property_category(self.v.taskProperty,
                                       t("pgrid_input_editor_of") + str(
                                           task_number) if task_number > 0 else t("pgrid_input_editor"))

    def _reset_loop_pgrid(self):
        self.v.loopProperty.ClearPage(self.v.loopProperty.GetPageByName(self.single_page))
        self._append_property_category(self.v.loopProperty, t("pgrid_loop_editor"))

    def on_grid_cell_right_click(self, evt):
        evt.Skip()

        self.selected_row_2_copied_paste = evt.Row

        if not hasattr(self, "popup_id_copy"):
            self.popup_id_copy = wx.NewId()
            self.popup_id_paste = wx.NewId()
            self.popup_id_skip_toggle = wx.NewId()
            self.popup_id_view_processor_usage = wx.NewId()
            self.popup_id_find_referencing_executions = wx.NewId()
            self.popup_id_ai_assist = wx.NewId()

        menu = wx.Menu()

        item_copy = wx.MenuItem(menu, self.popup_id_copy, t("menu_copy"))
        self.v.Bind(wx.EVT_MENU, self._on_grid_row_copy, item_copy)

        item_paste = wx.MenuItem(menu, self.popup_id_paste, t("menu_paste"))
        self.v.Bind(wx.EVT_MENU, self._on_grid_row_paste, item_paste)

        menu.Append(item_copy)
        menu.Append(item_paste)

        menu.AppendSeparator()

        row = evt.Row
        input_json = self.v.taskGrid.GetCellValue(row, 1)
        is_skipped = self._check_task_skipped(input_json)

        label = t("menu_unskip_task") if is_skipped else t("menu_skip_task")
        item_toggle = wx.MenuItem(menu, self.popup_id_skip_toggle, label)
        self.v.Bind(wx.EVT_MENU, self._on_grid_row_toggle_skip, item_toggle)
        menu.Append(item_toggle)

        processor_name = self.v.taskGrid.GetCellValue(row, 0).strip()
        if processor_name and processor_name in self.available_processors:
            menu.AppendSeparator()

            item_usage = wx.MenuItem(menu, self.popup_id_view_processor_usage, t("menu_view_processor_usage"))
            self.v.Bind(wx.EVT_MENU, self._on_view_processor_usage, item_usage)
            menu.Append(item_usage)

            item_refs = wx.MenuItem(menu, self.popup_id_find_referencing_executions,
                                    t("menu_find_referencing_executions").format(name=processor_name))
            self.v.Bind(wx.EVT_MENU, self._on_find_referencing_executions, item_refs)
            menu.Append(item_refs)

        menu.AppendSeparator()
        item_ai = wx.MenuItem(menu, self.popup_id_ai_assist, t("ai_gen_assist"))
        self.v.Bind(wx.EVT_MENU, self._on_ai_assist_execution, item_ai)
        menu.Append(item_ai)

        self.v.PopupMenu(menu)

        menu.Destroy()

    def on_grid_empty_right_click(self, evt):
        if not hasattr(self, "popup_id_ai_assist"):
            self.popup_id_ai_assist = wx.NewId()
        menu = wx.Menu()
        item_ai = wx.MenuItem(menu, self.popup_id_ai_assist, t("ai_gen_assist"))
        self.v.Bind(wx.EVT_MENU, self._on_ai_assist_execution, item_ai)
        menu.Append(item_ai)
        self.v.PopupMenu(menu)
        menu.Destroy()

    def _on_view_processor_usage(self, row_or_evt):
        if isinstance(row_or_evt, int):
            row = row_or_evt
        else:
            row = self.selected_row_2_copied_paste
        processor_name = self.v.taskGrid.GetCellValue(row, 0).strip()
        if not processor_name:
            return
        try:
            p = Processor.get_processor_by_type(processor_name)
            category = p.get_category() if hasattr(p, 'get_category') else 'N/A'
            tpl = p.get_tpl()
            desc = p.get_localized_desc() if hasattr(p, 'get_localized_desc') else p.get_desc()
            content = f"[{category}]  {processor_name}\n{'=' * 60}\n\n"
            content += f"TPL:\n{self._format_tpl(tpl)}\n\n"
            content += f"Description:\n{desc.strip()}"

            from mvp.view.common.TaskInfoRenderer import _analyse_input
            input_json = self.v.taskGrid.GetTable().GetValue(row, 1)
            is_skipped, has_empty, has_expr = _analyse_input(input_json)
            badge_lines = []
            if is_skipped:
                badge_lines.append(t("badge_skipped"))
            if has_empty:
                badge_lines.append(t("badge_empty"))
            if has_expr:
                badge_lines.append(t("badge_expr"))
            if badge_lines:
                content += f"\n\n{'─' * 60}\n" + "\n".join(badge_lines)
        except Exception as e:
            content = f"Failed to load processor info: {e}"

        from mvp.view.common.ResultDialog import ResultDialog
        dlg = ResultDialog(self.v, title=processor_name, message=content)
        dlg.ShowModal()
        dlg.Destroy()

    @staticmethod
    def _format_tpl(tpl_str):
        try:
            tpl_dict = json.loads(tpl_str)
            lines = []
            for k, v in tpl_dict.items():
                lines.append(f"  {k}: {v}")
            return "\n".join(lines)
        except Exception:
            return tpl_str

    def _on_find_referencing_executions(self, evt):
        row = self.selected_row_2_copied_paste
        processor_name = self.v.taskGrid.GetCellValue(row, 0).strip()
        if not processor_name:
            return

        refs = []
        for exec_name in Execution.get_available_executions():
            try:
                execution = Execution.get_execution(exec_name)
                if execution and hasattr(execution, 'list') and execution.list:
                    for i, task in enumerate(execution.list):
                        if hasattr(task, 'type') and task.type == processor_name:
                            refs.append(f"{exec_name}  (Task #{i + 1})")
            except Exception:
                continue

        if refs:
            content = f"Executions referencing [{processor_name}]:\n{'=' * 60}\n\n"
            content += "\n".join(f"  {r}" for r in refs)
        else:
            content = t("dlg_no_referencing_executions").format(name=processor_name)

        from mvp.view.common.ResultDialog import ResultDialog
        dlg = ResultDialog(self.v, title=t("dlg_referencing_executions_title").format(name=processor_name),
                           message=content)
        dlg.ShowModal()
        dlg.Destroy()

    def _on_grid_row_copy(self, evt):
        self.row_copied = [
            self.v.taskGrid.GetCellValue(self.selected_row_2_copied_paste, 0),
            self.v.taskGrid.GetCellValue(self.selected_row_2_copied_paste, 1)
        ]
        logging.debug("selected_row_copied" + str(self.row_copied))

    def on_task_grid_copy(self):
        if self.current_selected_row < 0:
            return
        self.row_copied = [
            self.v.taskGrid.GetCellValue(self.current_selected_row, 0),
            self.v.taskGrid.GetCellValue(self.current_selected_row, 1)
        ]
        logging.debug("row copied via shortcut: " + str(self.row_copied))

    def on_task_grid_paste(self):
        if self.current_selected_row < 0 or not hasattr(self, 'row_copied') or not self.row_copied:
            return
        self.selected_row_2_copied_paste = self.current_selected_row
        self._on_grid_row_paste(None)

    def _on_grid_row_paste(self, evt):
        if not hasattr(self, 'row_copied') or not self.row_copied:
            return
        self._push_snapshot()
        self.v.taskGrid.SetCellValue(self.selected_row_2_copied_paste, 0, self.row_copied[0])
        self.v.taskGrid.SetCellValue(self.selected_row_2_copied_paste, 1, self.row_copied[1])
        self._apply_row_skip_style(
            self.selected_row_2_copied_paste,
            self._check_task_skipped(self.row_copied[1])
        )
        self._update_save_button()

    def _on_grid_row_toggle_skip(self, evt):
        row = self.selected_row_2_copied_paste
        input_json = self.v.taskGrid.GetCellValue(row, 1)
        self._set_task_skipped(row, not self._check_task_skipped(input_json))

    def _set_task_skipped(self, row, skipped):
        grid = self.v.taskGrid
        input_json = grid.GetCellValue(row, 1)
        if not input_json or len(input_json) < 2:
            return
        self._push_snapshot()
        try:
            input_dict = json.loads(input_json)
        except (json.JSONDecodeError, TypeError):
            return
        input_dict["skipped"] = "yes" if skipped else "no"
        grid.SetCellValue(row, 1, json.dumps(input_dict))
        self._apply_row_skip_style(row, skipped)
        self._update_save_button()

        if self._pgrid_bound_row == row:
            page = self.v.taskProperty.GetPage(self.single_page)
            self._append_or_update_property_to_page("skipped", input_dict["skipped"], page)
            self.v.cb_skipped.SetValue(skipped)

    def _init_cron(self):
        self.cron = Cron(self.v)

    def _load_available_executions(self):
        self.available_executions = Execution.get_available_executions()
        self._tool_names = set(Execution.get_tool_execution_names())

    def _refresh_execution_chooser(self, selected_name=''):
        self.available_executions = Execution.get_available_executions()
        self._tool_names = set(Execution.get_tool_execution_names())
        self.v.executionChooser.SetValue(selected_name)

    def _load_available_pipelines(self):
        self.available_pipelines = Pipeline.get_available_pipelines()

    def _init_executiongrid_choice_editor(self):
        self.available_executions = Execution.get_available_executions()
        execution_grid = self.v.executionGrid
        for row in range(execution_grid.GetNumberRows()):
            self._bind_grid_cell_choice_editor(row, execution_grid, self.available_executions)

    def _init_taskgrid_choice_editor(self):
        self.available_processors = Processor.get_processors()
        task_grid = self.v.taskGrid
        col0_attr = wx.grid.GridCellAttr()
        col0_attr.SetReadOnly(True)
        task_grid.SetColAttr(0, col0_attr)
        col1_attr = wx.grid.GridCellAttr()
        col1_attr.SetReadOnly(True)
        col1_attr.SetRenderer(TaskInfoRenderer())
        task_grid.SetColAttr(1, col1_attr)
        for row in range(task_grid.GetNumberRows()):
            self._bind_grid_cell_choice_editor(row, task_grid, self.available_processors)

    def on_add_loop(self):
        self._push_snapshot()
        loop_code = 'loop-' + DateUtil.get_now_in_str()
        loop_tpl = Loop.tpl()
        page = self.v.loopProperty.GetPage(self.single_page)
        self._append_or_update_property_to_page(loop_code, loop_tpl, page)
        page.FitColumns()
        self._update_save_button()

    def on_del_loop(self):
        self._push_snapshot()
        page = self.v.loopProperty.GetPage(self.single_page)
        self._delete_selected_property_from_page(page)
        self._update_save_button()

    def on_edit_loop(self):
        prop = self.v.loopProperty.GetSelection()
        if prop is None or isinstance(prop, wx.propgrid.PropertyCategory):
            logging.info(t("msg_select_property_first"))
            return
        self._right_clicked_loop_property = prop
        self._on_edit_loop_value(None)

    def on_loop_property_selected4e(self, evt):
        evt.Skip()
        prop = evt.GetProperty()
        is_real_prop = prop is not None and not isinstance(prop, wx.propgrid.PropertyCategory)
        self.v.editLoop.Enable(is_real_prop)

    def on_loop_property_changing4e(self, evt):
        evt.Skip()
        self._push_snapshot()

    def on_loop_property_change4e(self, evt):
        evt.Skip()
        self._update_save_button()

    def on_loop_property_right_click4e(self, evt):
        prop = evt.GetProperty()
        evt.Skip()
        if prop is None or isinstance(prop, wx.propgrid.PropertyCategory):
            return

        self._right_clicked_loop_property = prop

        menu = wx.Menu()
        id_edit = wx.NewId()
        menu.Append(id_edit, t("menu_edit_loop"))
        self.v.Bind(wx.EVT_MENU, self._on_edit_loop_value, id=id_edit)
        self.v.PopupMenu(menu)
        menu.Destroy()

    def _on_edit_loop_value(self, evt):
        from mvp.view.common.LoopEditDialog import LoopEditDialog
        prop = getattr(self, '_right_clicked_loop_property', None)
        if prop is None:
            return
        loop_code = prop.GetName()
        loop_attributes_json = prop.GetValue()
        dlg = LoopEditDialog(self.v, loop_code, loop_attributes_json)
        if dlg.ShowModal() == wx.ID_OK:
            new_json = dlg.get_result_json()
            self._push_snapshot()
            prop.SetValue(new_json)
            self._update_save_button()
        dlg.Destroy()

    def on_close_window(self, evt=None):
        if self._is_dirty():
            dlg = wx.Dialog(self.v, title=t("dlg_unsaved_title"))
            sizer = wx.BoxSizer(wx.VERTICAL)
            sizer.Add(wx.StaticText(dlg, label=t("dlg_unsaved_on_close_msg")), 0, wx.ALL, 12)
            btn_sizer = wx.StdDialogButtonSizer()
            btn_save = wx.Button(dlg, wx.ID_ANY, t("btn_save_and_exit"))
            btn_exit = wx.Button(dlg, wx.ID_ANY, t("btn_exit_without_save"))
            btn_cancel = wx.Button(dlg, wx.ID_CANCEL, t("btn_cancel_exit"))
            btn_sizer.Add(btn_save, 0, wx.ALL, 4)
            btn_sizer.Add(btn_exit, 0, wx.ALL, 4)
            btn_sizer.Add(btn_cancel, 0, wx.ALL, 4)
            sizer.Add(btn_sizer, 0, wx.ALIGN_CENTER | wx.BOTTOM, 8)
            dlg.SetSizerAndFit(sizer)

            result = [None]
            btn_save.Bind(wx.EVT_BUTTON, lambda e: result.__setitem__(0, "save") or dlg.EndModal(wx.ID_OK))
            btn_exit.Bind(wx.EVT_BUTTON, lambda e: result.__setitem__(0, "exit") or dlg.EndModal(wx.ID_OK))

            dlg.ShowModal()
            dlg.Destroy()

            if result[0] == "save":
                self.on_save_execution()
            elif result[0] != "exit":
                return False

        self.logger_thread = None
        self.keep_running = False
        self._log_timer.Stop()
        if self._log_fd is not None:
            self._log_fd.close()
            self._log_fd = None
        if hasattr(self.v, 'tbicon') and self.v.tbicon:
            try:
                self.v.tbicon.Destroy()
            except RuntimeError:
                pass
            self.v.tbicon = None
        return True

    def on_notebook_page_changed(self, evt):
        # switch notebook tab from execution to pipeline
        if evt.Selection == 1:
            self._init_executiongrid_choice_editor()

    def on_log_level_changed(self):
        log_level = self.v.logSearchBar.logLevelBtn.GetValue()

        if self.m.log_level != log_level:
            self.m.log_level = log_level
            self.m.set_config('log_level', self.m.log_level)

        logging.getLogger().setLevel(logging.getLevelName(log_level))
        getattr(logging, log_level.lower())('Set log level to <' + log_level + '> successfully.')

    def on_lang_changed(self):
        combo = self.v.langChooser
        locale = "zh" if combo.GetValue() == "中文" else "en"

        if getattr(self.m, 'language', 'zh') != locale:
            self.m.language = locale
            self.m.set_config('language', locale)

        set_locale(locale)
        from mvp.view.common.TaskInfoRenderer import TaskInfoRenderer
        TaskInfoRenderer._desc_cache.clear()
        TaskInfoRenderer._cat_cache.clear()
        self._apply_i18n()
        self._apply_theme()

    def on_theme_changed(self):
        name = self.v.themeChooser.GetValue()
        set_theme(name)
        if getattr(self.m, 'theme', 'Forest') != name:
            self.m.theme = name
            self.m.set_config('theme', name)
        self._apply_theme()

    def _on_sys_appearance_changed(self, evt):
        evt.Skip()
        if is_system_theme():
            set_theme(SYSTEM_THEME_NAME)
            self._apply_theme()

    def _set_highlight_info(self, text: str):
        self.v.highlightInfo.SetLabel(text)
        self.v.highlightInfo.GetParent().Layout()

    def update_highlight_info_start(self, name: str):
        self._exec_start_time = time.time()
        self._welcome_paused = True
        self._set_highlight_info(f"[START] {name}")

    def update_highlight_info_pipeline_start(self, name: str):
        self._pipeline_start_time = time.time()
        self._welcome_paused = True
        self._set_highlight_info(f"[PIPELINE START] {name}")

    def update_highlight_info_pipeline_done(self, name: str):
        elapsed = time.time() - self._pipeline_start_time if hasattr(self,
                                                                     '_pipeline_start_time') and self._pipeline_start_time else 0
        self._set_highlight_info(f"[PIPELINE DONE] {name}  {elapsed:.1f}s")
        wx.CallLater(8000, self._resume_welcome)

    def select_pipeline_execution_row(self, row_idx: int):
        grid = self.v.executionGrid
        if row_idx < grid.GetNumberRows():
            grid.SelectRow(row_idx)
            grid.MakeCellVisible(row_idx, 0)

    def update_highlight_info_done(self, name: str, error: str = None):
        if error:
            msg = f"{name}: {error}"
            if len(msg) > 80:
                msg = msg[:77] + "..."
            self._set_highlight_info(f"[ERROR] {msg}")
        else:
            elapsed = time.time() - self._exec_start_time if self._exec_start_time else 0
            self._set_highlight_info(f"[DONE] {name}  {elapsed:.1f}s")
        wx.CallLater(8000, self._resume_welcome)

    def on_execution_pipeline_changed(self):
        combo = self.v.pipelineChooser
        grid = self.v.executionGrid
        grid.ClearGrid()

        self.pipeline = Pipeline.get_pipeline(combo.GetValue())
        if self.pipeline is None:
            return
        else:
            current_number_rows = grid.GetNumberRows()
            execution_number = len(self.pipeline.list)

            self.v.asCronChecbox.SetValue(self.pipeline.cronEnabled)
            self.v.cronInput.SetValue(self.pipeline.cronExp)
            self._update_cron_setting(self.pipeline.cronEnabled)

            if execution_number > current_number_rows:
                for _ in range(execution_number - current_number_rows):
                    self._insert_row(grid, self.available_executions)

            for idx, itm in enumerate(self.pipeline.list):
                grid.SetCellValue(idx, 0, itm['execution'])
                if 'input' in itm:
                    grid.SetCellValue(idx, 1, itm['input'])

    def _reset_grids(self):
        self._reset_task_pgrid()
        self._reset_loop_pgrid()
        self.v.availableProperties.Clear()

    def on_task_execution_changed(self):
        import time as _t; _t0 = _t.time()
        self._reset_grids()
        combo = self.v.executionChooser
        grid = self.v.taskGrid
        grid.ClearGrid()
        execution_desc = self.v.execution_desc
        cb_astool = self.v.cb_astool
        execution_desc.Clear()

        self.execution = Execution.get_execution(combo.GetValue())
        if self.execution is None:
            self._snapshots.clear()
            self._snapshot_cursor = -1
            self._mark_clean()
            return
        else:
            logging.debug(f'[PERF] get_execution: {(_t.time()-_t0)*1000:.0f}ms')
            current_number_rows = grid.GetNumberRows()
            task_number = len(self.execution.list)

            grid.BeginBatch()
            if task_number > current_number_rows:
                for _ in range(task_number - current_number_rows):
                    self._insert_row(grid, self.available_processors)

            for idx, itm in enumerate(self.execution.list):
                grid.SetCellValue(idx, 0, itm.type)
                if (hasattr(itm, 'input')):
                    grid.SetCellValue(idx, 1, itm.input)

            self._apply_all_row_skip_styles()
            self._autosize_input_col()
            grid.EndBatch()
            logging.debug(f'[PERF] grid populate: {(_t.time()-_t0)*1000:.0f}ms')

            if hasattr(self.execution, 'loops') and len(self.execution.loops) > 0:
                for idx, itm in enumerate(self.execution.loops):
                    self._append_or_update_property_to_page(
                        itm.loop_code,
                        itm.loop_attributes,
                        self.v.loopProperty.GetPage(self.single_page)
                    )

            if hasattr(self.execution, 'mcp_desc') and self.execution.mcp_desc is not None:
                execution_desc.set_execution_name(combo.GetValue())
                execution_desc.SetValue(self.execution.mcp_desc)
            logging.debug(f'[PERF] mcp_desc: {(_t.time()-_t0)*1000:.0f}ms')

            if hasattr(self.execution, 'astool') and self.execution.astool is not None:
                cb_astool.SetValue(self.execution.astool)
            else:
                cb_astool.SetValue(False)

            self._snapshots.clear()
            self._snapshot_cursor = -1
            self._mark_clean()

            if self.v.taskGrid.GetNumberRows() > 0:
                self.v.taskGrid.SelectRow(0)
                if self.current_selected_row != 0:
                    self._load_input_taskproperty(0)
            logging.debug(f'[PERF] load_property: {(_t.time()-_t0)*1000:.0f}ms')

            self._sync_mcp_panel_visibility()
            logging.debug(f'[PERF] total: {(_t.time()-_t0)*1000:.0f}ms')

    def _save_execcution(self, name):
        grid = self.v.taskGrid
        loop_property = self.v.loopProperty

        as_tool = self.v.cb_astool.IsChecked()
        if as_tool and not self._check_last_task_is_response_key() and not self._has_output_schema_properties():
            wx.MessageBox(
                t("warn_astool_no_output_config"),
                "Warning",
                wx.OK | wx.ICON_WARNING,
                self.v,
            )
            logging.warning(t("warn_astool_no_output_config"))
            return False

        # prepare tasks
        tasks = []
        for row in range(0, grid.GetNumberRows()):
            t_type = grid.GetCellValue(row, 0)
            t_input = grid.GetCellValue(row, 1)
            if len(t_type) == 0 and len(t_input) == 0:
                break
            logging.info(f'{t_type} -> {t_input}')

            tasks.append(Task(t_type, t_input, self._check_task_skipped(t_input)))

        # validate dynamic func bodies before saving
        if not self._validate_dynamic_func_bodies(tasks, grid):
            logging.info(t("msg_save_aborted"))
            return False

        # prepare loops
        loops = []
        itr = loop_property.GetPage(self.single_page).GetPyIterator(wx.propgrid.PG_ITERATE_ALL)

        for prop in itr:
            if isinstance(prop, wx.propgrid.PropertyCategory):
                continue

            loops.append(Loop(prop.GetName(), prop.GetValue()))

        execution_desc = self.v.execution_desc.GetValue() or ''
        as_tool = self.v.cb_astool.IsChecked()
        if len(tasks) > 0:
            Execution(name, tasks, execution_desc, as_tool, loops).save()

    def _check_task_skipped(self, input_json):
        try:
            if "skipped" not in input_json:
                return False

            data = json.loads(input_json)

            if "skipped" not in data:
                return False

            skipped_value = str(data["skipped"]).lower()

            return skipped_value in {"yes", "y", "true", "t"}

        except Exception as e:
            return False

    def _apply_row_skip_style(self, row, skipped):
        grid = self.v.taskGrid
        if skipped:
            normal_bg = grid.GetDefaultCellBackgroundColour()
            normal_fg = grid.GetDefaultCellTextColour()
            bg = wx.Colour(
                max(0, normal_bg.Red() - 30),
                max(0, normal_bg.Green() - 30),
                max(0, normal_bg.Blue() - 30),
            )
            fg = wx.Colour(
                normal_fg.Red() + (normal_bg.Red() - normal_fg.Red()) * 2 // 3,
                normal_fg.Green() + (normal_bg.Green() - normal_fg.Green()) * 2 // 3,
                normal_fg.Blue() + (normal_bg.Blue() - normal_fg.Blue()) * 2 // 3,
            )
        else:
            bg = grid.GetDefaultCellBackgroundColour()
            fg = grid.GetDefaultCellTextColour()
        for col in range(grid.GetNumberCols()):
            grid.SetCellBackgroundColour(row, col, bg)
            grid.SetCellTextColour(row, col, fg)
        grid.ForceRefresh()

    def _apply_all_row_skip_styles(self):
        grid = self.v.taskGrid
        grid.BeginBatch()
        for row in range(grid.GetNumberRows()):
            input_json = grid.GetCellValue(row, 1)
            self._apply_row_skip_style(row, self._check_task_skipped(input_json))
        grid.EndBatch()

    def _autosize_input_col(self):
        grid = self.v.taskGrid
        grid.AutoSizeColumn(0, setAsMin=False)
        total = grid.GetClientSize().width
        col0 = grid.GetColSize(0)
        label_w = grid.GetRowLabelSize()
        col1 = total - col0 - label_w - 2
        if col1 > 100:
            grid.SetColSize(1, col1)

    def _validate_dynamic_func_bodies(self, tasks, grid):
        """
        Validate syntax of dynamic function bodies in tasks before saving.
        If a syntax error is found, show an InputDialog for the user to edit and fix.
        Returns True if all valid (or user fixed all), False if user cancelled.
        """
        for task_idx, task in enumerate(tasks):
            task_number = task_idx + 1
            if not task.type or not hasattr(task, 'input') or not task.input:
                continue

            try:
                input_dict = json.loads(task.input)
            except (json.JSONDecodeError, TypeError):
                continue

            params_to_check = CodeExplainerUtil.get_dynamic_param_specs_with_source(task.type, input_dict)
            if not params_to_check:
                continue

            for param_name, func_args, body_prefix, spec_source in params_to_check:
                if param_name not in input_dict or not input_dict[param_name]:
                    continue

                if spec_source == 'fallback':
                    logging.warning(
                        f'Dynamic param inferred by naming convention @Task{task_number} '
                        f'[{task.type}] param="{param_name}". '
                        f'Consider adding explicit mapping in CodeExplainerUtil.DYNAMIC_FUNC_PARAMS.'
                    )

                raw_value = input_dict[param_name]
                if not isinstance(raw_value, str):
                    continue

                # Convert stored escape sequences to real characters for compilation
                func_body = raw_value.replace('\\n', '\n').replace('\\t', '\t')
                error = CodeExplainerUtil.validate_func_syntax(func_args, func_body, body_prefix)

                if error is None:
                    continue

                # Syntax error found — show InputDialog for editing
                while error is not None:
                    dlg = InputDialog(
                        self.v,
                        title=f"Syntax Error — Task {task_number} [{task.type}]",
                        message=f"Parameter: {param_name}\nError: {error}",
                        default_value=func_body
                    )

                    if dlg.ShowModal() == wx.ID_OK:
                        new_value = dlg.GetValue()
                        dlg.Destroy()

                        # Re-validate the edited code
                        error = CodeExplainerUtil.validate_func_syntax(func_args, new_value, body_prefix)
                        if error is None:
                            # User fixed it — store back with escape sequences
                            stored_value = new_value.replace('\n', '\\n').replace('\t', '\\t')
                            input_dict[param_name] = stored_value
                            task.input = json.dumps(input_dict)
                            grid.SetCellValue(task_idx, 1, task.input)
                            logging.info(
                                f'Task {task_number} [{task.type}] param "{param_name}" syntax fixed and updated.')
                        else:
                            # Still has error — loop to let user try again
                            func_body = new_value
                    else:
                        dlg.Destroy()
                        return False  # User cancelled — abort save

        return True

    def _save_pipeline(self, name):
        grid = self.v.executionGrid
        list = []

        for row in range(0, grid.GetNumberRows()):
            executionName = grid.GetCellValue(row, 0)
            executionInput = grid.GetCellValue(row, 1)
            if (len(executionName) == 0 and len(executionInput) == 0):
                break

            list.append({
                'execution': executionName,
                'input': executionInput
            })

        if (len(list) > 0):
            cron_exp = self.v.cronInput.GetValue()
            cron_desc = self._explain_cron(cron_exp) if cron_exp.strip() else ''
            cron_enabled = self.v.asCronChecbox.IsChecked()

            if cron_enabled and t(self.CRON_INVALID) == cron_desc:
                logging.warning(t("msg_cron_cannot_save"))
                return

            Pipeline(name, list, cron_enabled, cron_exp, cron_desc).save()
        else:
            logging.warning(t("msg_exec_list_empty"))

    def on_save_pipeline(self):
        combo = self.v.pipelineChooser
        name = combo.GetValue()

        if (len(name) == 0):
            logging.info(t("msg_pipeline_name_empty"))
            return

        if name not in self.available_pipelines:
            self.available_pipelines.insert(0, name)
        else:
            logging.warning(t("msg_pipeline_overwrite", name=name))

        self._save_pipeline(name)

    def on_save_execution(self):
        combo = self.v.executionChooser
        name = combo.GetValue()

        if self._save_execcution(name) is False:
            return

        is_new = name not in self.available_executions
        if not is_new:
            logging.warning(t("msg_execution_overwrite", name=name))

        self._mark_clean()
        self._refresh_execution_chooser(name)
        self.invalidate_tools_cache()

    def on_delete_pipeline(self):
        combo = self.v.pipelineChooser
        name = combo.GetValue()

        if name in self.available_pipelines:
            self.pipeline.delete()
            self.available_pipelines.remove(name)
            combo.SetValue("")

    def on_delete_execution(self):
        combo = self.v.executionChooser
        name = combo.GetValue()

        if name not in self.available_executions:
            return

        dlg = wx.MessageDialog(
            self.v,
            t("dlg_delete_exec_msg", name=name),
            t("dlg_delete_exec_title"),
            wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING,
        )
        result = dlg.ShowModal()
        dlg.Destroy()

        if result != wx.ID_YES:
            return

        target = self.execution or Execution.get_execution(name)
        if target is None:
            return
        target.delete()
        self.execution = None
        self._refresh_execution_chooser('')
        self.invalidate_tools_cache()
        self.on_task_execution_changed()

    def on_copy_execution(self):
        combo = self.v.executionChooser
        name = combo.GetValue()
        if not name:
            return
        source = Execution.get_execution(name)
        if source is None:
            return

        existing = set(Execution.get_available_executions())
        new_name = name + '_copy'

        while True:
            dlg = wx.TextEntryDialog(self.v, t("dlg_copy_exec_msg"),
                                     t("dlg_copy_exec_title"), new_name)
            if dlg.ShowModal() != wx.ID_OK:
                dlg.Destroy()
                return
            new_name = dlg.GetValue().strip()
            dlg.Destroy()

            if not new_name or new_name in existing:
                wx.MessageBox(t("dlg_copy_exec_dup"), t("dlg_copy_exec_title"),
                              wx.OK | wx.ICON_WARNING, self.v)
                continue
            break

        clean_tasks = [Task(t.type, t.input, t.skipped) for t in source.list]
        copy = Execution(new_name, clean_tasks,
                         source.mcp_desc if hasattr(source, 'mcp_desc') else '',
                         source.astool if hasattr(source, 'astool') else False,
                         list(source.loops) if hasattr(source, 'loops') else [])
        copy.save()
        self._refresh_execution_chooser(new_name)
        self.invalidate_tools_cache()
        self.on_task_execution_changed()

    def on_add_execution(self, _evt=None):
        existing = set(Execution.get_available_executions())

        dlg = wx.TextEntryDialog(self.v, t("dlg_create_exec_name"),
                                 t("dlg_create_exec_title"), "NEW_EXECUTION")
        while True:
            if dlg.ShowModal() != wx.ID_OK:
                dlg.Destroy()
                return
            new_name = dlg.GetValue().strip()
            if not new_name or new_name in existing:
                wx.MessageBox(t("dlg_create_exec_dup"), t("dlg_create_exec_title"),
                              wx.OK | wx.ICON_WARNING, self.v)
                continue
            break
        dlg.Destroy()

        tpl_choices = [t("dlg_create_exec_blank"), t("ai_gen_btn")] + sorted(existing)
        choice_dlg = wx.SingleChoiceDialog(
            self.v, t("dlg_create_exec_mode"),
            t("dlg_create_exec_title"), tpl_choices)
        choice_dlg.SetSelection(0)
        if choice_dlg.ShowModal() != wx.ID_OK:
            choice_dlg.Destroy()
            return
        sel = choice_dlg.GetStringSelection()
        choice_dlg.Destroy()

        if sel == t("ai_gen_btn"):
            self._start_ai_generator(new_name)
        elif sel != t("dlg_create_exec_blank") and sel in existing:
            source = Execution.get_execution(sel)
            clean_tasks = [Task(tk.type, tk.input, tk.skipped) for tk in source.list]
            loops = list(source.loops) if hasattr(source, 'loops') else []
            new_exec = Execution(new_name, clean_tasks, '', False, loops)
            new_exec.save()
            self._refresh_execution_chooser(new_name)
            self.invalidate_tools_cache()
            self.on_task_execution_changed()
        else:
            clean_tasks = [Task('INITIAL_PARAMS', '{}', False)]
            loops = []
            new_exec = Execution(new_name, clean_tasks, '', False, loops)
            new_exec.save()
            self._refresh_execution_chooser(new_name)
            self.invalidate_tools_cache()
            self.on_task_execution_changed()

    def _start_ai_generator(self, execution_name):
        from core.ai.ExecutionGenerator import ExecutionGenerator
        from mvp.view.common.AIGeneratorDialog import AIGeneratorDialog

        provider = getattr(self.m, 'ai_provider', '')
        api_key = getattr(self.m, 'ai_api_key', '')
        model = getattr(self.m, 'ai_model', '')
        base_url = getattr(self.m, 'ai_base_url', '')

        if not provider or not api_key:
            wx.MessageBox(t("ai_gen_no_config"), "Warning", wx.OK | wx.ICON_WARNING, self.v)
            return

        clean_tasks = [Task('INITIAL_PARAMS', '{}', False)]
        new_exec = Execution(execution_name, clean_tasks, '', False, [])
        new_exec.save()
        self._refresh_execution_chooser(execution_name)
        self.invalidate_tools_cache()
        self.on_task_execution_changed()

        locale = getattr(self.m, 'language', 'en')
        dialog = AIGeneratorDialog(self.v, locale=locale, on_apply=self._ai_apply_callback)
        dialog.set_undo_redo_handlers(self._undo, self._redo)

        generator = ExecutionGenerator(dialog.get_selected_categories(), locale)
        generator.init_client(provider, api_key, base_url, model)
        dialog.set_generator(generator)

        self._ai_dialog = dialog
        self._ai_execution_name = execution_name
        dialog.Show()

    def _ai_apply_callback(self, action, tasks=None, loops=None):
        if action == 'get_tasks':
            if self.execution:
                return list(self.execution.list)
            return []

        if action == 'apply' and tasks is not None:
            name = self._ai_execution_name
            execution_loops = loops if loops is not None else (
                list(self.execution.loops) if self.execution and hasattr(self.execution, 'loops') else []
            )
            new_exec = Execution(name, tasks, '', False, execution_loops)
            new_exec.save()
            self.on_task_execution_changed()
            self._push_snapshot()

    def _on_ai_generate_mcp_desc(self):
        from core.ai.ExecutionGenerator import ExecutionGenerator, resolve_api_key

        provider = getattr(self.m, 'ai_provider', '')
        api_key = getattr(self.m, 'ai_api_key', '')
        model_name = getattr(self.m, 'ai_model', '')
        base_url = getattr(self.m, 'ai_base_url', '')
        locale = getattr(self.m, 'language', 'en')

        if not provider or not api_key:
            wx.MessageBox(t("ai_gen_no_config"), "Warning", wx.OK | wx.ICON_WARNING, self.v)
            return

        if not self.execution or not self.execution.list:
            return

        tasks = list(self.execution.list)
        wx.BeginBusyCursor()
        try:
            generator = ExecutionGenerator([], locale)
            generator.init_client(provider, resolve_api_key(api_key), base_url, model_name)
            result = generator.generate_mcp_desc(tasks)
            if result:
                self._push_snapshot()
                self.v.execution_desc.SetValue(result)
        finally:
            wx.EndBusyCursor()

    def _on_ai_assist_execution(self, _evt=None):
        if not self.execution:
            return
        execution_name = self.execution.execution
        from core.ai.ExecutionGenerator import ExecutionGenerator
        from mvp.view.common.AIGeneratorDialog import AIGeneratorDialog

        provider = getattr(self.m, 'ai_provider', '')
        api_key = getattr(self.m, 'ai_api_key', '')
        model = getattr(self.m, 'ai_model', '')
        base_url = getattr(self.m, 'ai_base_url', '')

        if not provider or not api_key:
            wx.MessageBox(t("ai_gen_no_config"), "Warning", wx.OK | wx.ICON_WARNING, self.v)
            return

        locale = getattr(self.m, 'language', 'en')
        dialog = AIGeneratorDialog(self.v, locale=locale, on_apply=self._ai_apply_callback)
        dialog.set_undo_redo_handlers(self._undo, self._redo)

        generator = ExecutionGenerator(dialog.get_selected_categories(), locale)
        generator.init_client(provider, api_key, base_url, model)
        dialog.set_generator(generator)

        self._ai_dialog = dialog
        self._ai_execution_name = execution_name
        dialog.Show()

    def on_stop_all(self):
        self.cron.stop_all()

    def on_stop_current(self):
        if not self.pipeline is None:
            self.cron.stop_one(self.pipeline)

    def on_run_pipeline(self):
        combo = self.v.pipelineChooser
        self.pipeline = Pipeline.get_pipeline(combo.GetValue())
        if self.v.asCronChecbox.IsChecked() and not t(self.CRON_INVALID) == self.v.cronInput.GetValue():
            self.cron.add_one(self.pipeline)
        else:
            Thread(target=self.pipeline.run, args=({"__m": self.m, "__p": self}, self.v), daemon=True).start()

    def on_run_execution(self, init_param: dict = None):
        if self.execution is None:
            wx.MessageBox(t("dlg_no_exec_selected"), t("dlg_create_exec_title"),
                          wx.OK | wx.ICON_INFORMATION, self.v)
            return
        if self._is_dirty():
            dlg = wx.MessageDialog(
                self.v,
                t("dlg_unsaved_msg"),
                t("dlg_unsaved_title"),
                wx.YES_NO | wx.ICON_WARNING,
            )
            dlg.SetYesNoLabels(t("btn_save_and_run"), t("btn_dismiss"))
            result = dlg.ShowModal()
            dlg.Destroy()
            if result == wx.ID_NO:
                return
            self.on_save_execution()

        combo = self.v.executionChooser
        self.execution = Execution.get_execution(combo.GetValue())

        # record last_run
        if self.m.last_run != combo.GetValue():
            self.m.last_run = combo.GetValue()
            self.m.set_config('last_run', self.m.last_run)

        fresh_init = dict(init_param) if init_param else {}
        if not init_param and self._should_inject_mcp_defaults(self.execution):
            mcp_defaults = self._extract_mcp_input_defaults(self.execution, fresh_init)
            if mcp_defaults:
                fresh_init.update(mcp_defaults)
        fresh_init.update({"__m": self.m, "__p": self})
        executor = Executor(self.execution, fresh_init, self.v)
        self.executors.append(executor)
        executor.start()

    def on_executeonstartup_changed(self, evt: wx.EVT_CHECKBOX):
        self.m.execute_on_startup = evt.IsChecked()
        self.m.set_config('execute_on_startup', self.m.execute_on_startup)

    def on_only_tool_changed(self, evt):
        pass  # palette uses _tool_names + only_tool state dynamically

    def on_stop_execution(self):
        for executor in self.executors:
            if executor.is_alive():
                executor.execution.set_should_be_stop(True)
                logging.info(t("msg_execution_stopping", name=executor.execution.execution))
                self._set_highlight_info(f"[STOP] {executor.execution.execution}")

        self.executors = []

    def on_select_recording(self):
        with wx.FileDialog(self.v, t("fdlg_open_recording"), wildcard="recording files (*.json)|*.json",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return

            path_name = fileDialog.GetPath()
            self.converter = ChromeRecorderConverter(path_name)
            title = self.converter.get_title()
            self.v.recordingLocation.SetLabel(f'{title}  ({path_name})')

    def on_load_from_recording(self):
        if hasattr(self, 'converter') and self.converter.is_initialized():
            self._push_snapshot()
            tasks = self.converter.convert()

            task_grid = self.v.taskGrid
            selected_rows = task_grid.GetSelectedRows()
            insert_at = selected_rows[0] if len(selected_rows) > 0 else task_grid.GetNumberRows()

            for i, task in enumerate(tasks):
                row = insert_at + i
                task_grid.InsertRows(row, 1, True)
                self._bind_grid_cell_choice_editor(row, task_grid, self.available_processors)
                task_grid.SetCellValue(row, 0, task.type)
                if hasattr(task, 'input'):
                    task_grid.SetCellValue(row, 1, task.input)

            logging.info(
                t("msg_convert_success", file_path=self.converter.file_path, title=self.converter.get_title()))
            self._update_save_button()
        else:
            logging.warning(t("msg_recording_empty"))

    def _bind_grid_cell_choice_editor(self, rowAt, grid, choices):
        # Prefer searchable choice editor to improve UX when choice lists are long.
        try:
            grid.SetCellEditor(
                rowAt, 0,
                SearchableGridChoiceEditor(choices, allow_others=False, match_mode="contains")
            )
        except Exception:
            grid.SetCellEditor(
                rowAt, 0,
                wx.grid.GridCellChoiceEditor(choices, allowOthers=False)
            )
        # this cell editor is not working for mac so,
        if not OSUtils.get_system() == "darwin":
            grid.SetCellEditor(
                rowAt, 1,
                wx.grid.GridCellAutoWrapStringEditor()
            )

    def on_grid_cell_editor_shown4e(self, evt):
        evt.Skip()

    def _show_processor_palette(self, row):
        grid = self.v.taskGrid
        current_value = grid.GetCellValue(row, 0)
        rect = grid.CellToRect(row, 0)
        pos = grid.GetGridWindow().ClientToScreen(rect.GetBottomLeft())
        palette = ProcessorPalette(
            self.v, self.available_processors, current_value,
            on_select=lambda val: self._on_processor_palette_selected(row, val)
        )
        palette.ShowAt(pos)

    def _on_processor_palette_selected(self, row, value):
        grid = self.v.taskGrid
        if value not in self.available_processors:
            return
        self._push_snapshot()
        grid.SetCellValue(row, 0, value)
        p = Processor.get_processor_by_type(value)
        grid.SetCellValue(row, 1, p.get_tpl())
        logging.info(f'Processor {value} : {p.get_desc()}')
        self._load_input_taskproperty(row)

    def _show_execution_palette(self):
        combo = self.v.executionChooser
        current_value = combo.GetValue()
        if self.v.only_tool.IsChecked():
            choices = [n for n in self.available_executions if n in self._tool_names]
        else:
            choices = self.available_executions
        tag_map = {n: "🦾" for n in self._tool_names}
        pos = combo.ClientToScreen(wx.Point(0, combo.GetSize().height))
        palette = ProcessorPalette(
            self.v, choices, current_value,
            on_select=self._on_execution_palette_selected,
            tag_map=tag_map,
            hint=t("palette_hint"),
        )
        palette.SetSize((max(combo.GetSize().width, 380), 440))
        palette.ShowAt(pos)

    def _on_execution_palette_selected(self, value):
        self.v.executionChooser.SetValue(value)
        self.on_task_execution_changed()

    def _show_pipeline_palette(self):
        combo = self.v.pipelineChooser
        current_value = combo.GetValue()
        choices = self.available_pipelines
        tag_map = {}
        for name in choices:
            p = Pipeline.get_pipeline(name)
            if p and getattr(p, 'cronEnabled', False):
                tag_map[name] = "[cron]"
        pos = combo.ClientToScreen(wx.Point(0, combo.GetSize().height))
        palette = ProcessorPalette(
            self.v, choices, current_value,
            on_select=self._on_pipeline_palette_selected,
            tag_map=tag_map,
            hint=t("palette_hint"),
        )
        palette.SetSize((max(combo.GetSize().width, 380), 440))
        palette.ShowAt(pos)

    def _on_pipeline_palette_selected(self, value):
        self.v.pipelineChooser.SetValue(value)
        self.on_execution_pipeline_changed()

    def on_grid_cell_change4e(self, evt):
        grid = self.v.taskGrid
        current_value = grid.GetCellValue(evt.GetRow(), evt.GetCol())
        current_row = evt.GetRow()
        current_column = evt.GetCol()
        evt.Skip()

        if current_column == 0:
            if len(current_value) <= 0 or not current_value in self.available_processors:
                return
            self._push_snapshot()
            p = Processor.get_processor_by_type(current_value)

            grid.SetCellValue(current_row, 1, p.get_tpl())

            logging.info(f'Processor {current_value} : {p.get_desc()}')
            self._load_input_taskproperty(current_row)
            self._update_save_button()
        else:
            self._push_snapshot()

    def on_grid_cell_select4e(self, evt):
        current_row = evt.GetRow()
        evt.Skip()
        self._load_input_taskproperty(current_row)

    def _load_input_taskproperty(self, current_row):
        grid = self.v.taskGrid
        self.current_selected_row = current_row
        self._pgrid_bound_row = current_row  # lock property grid to this row
        current_input = grid.GetCellValue(current_row, 1)
        current_processor = grid.GetCellValue(current_row, 0)

        try:
            input_dict = json.loads(current_input) if current_input.strip() else {}
        except (json.JSONDecodeError, TypeError):
            input_dict = None

        if isinstance(input_dict, dict):
            page = self.v.taskProperty.GetPage(self.single_page)
            self._reset_task_pgrid(current_row + 1)

            for k in input_dict.keys():
                v = input_dict[k]
                self._append_or_update_property_to_page(k, v, page)

            page.FitColumns()

            if current_processor in self.available_processors:
                self._fill_available_properties(current_processor, input_dict)
        else:
            self._reset_task_pgrid()
            self._pgrid_bound_row = -1  # no valid property binding

    def _fill_available_properties(self, processor, input_dict):
        self.v.availableProperties.Clear()
        tpl_dict = json.loads(Processor.get_processor_by_type(processor).get_tpl())
        available_processors = [k for k in tpl_dict.keys() if not k in input_dict]
        self.v.availableProperties.AppendItems(available_processors)

        combo = self.v.availableProperties
        if available_processors:
            max_w = max(combo.GetTextExtent(s)[0] for s in available_processors)
            combo.SetMinSize((max(max_w + 30, 100), -1))
            combo.GetParent().Layout()

        # Sync the "skipped" checkbox to reflect the current task's skipped state.
        skipped_value = str(input_dict.get("skipped", "")).lower()
        is_skipped = skipped_value in {"yes", "y", "true", "t"}
        self.v.cb_skipped.SetValue(is_skipped)

    def _append_or_update_property_to_page(self, k, v, page):
        prop = page.GetPropertyByName(k)

        if prop is not None:
            prop.SetValue(str(v) if type(v) is int else v)
            return False

        if type(v) is list:
            page.Append(wx.propgrid.ArrayStringProperty(label=k, name=k, value=v))
        elif type(v) in (str, int):
            page.Append(wx.propgrid.StringProperty(label=k, name=k, value=str(v) if type(v) is int else v))
        else:
            raise AttributeError('Unsupported property type:' + str(type(v)))
        page.FitColumns()
        return True

    def on_cron_actived(self, evt):
        self._update_cron_setting(1 == evt.Selection)

    def on_cron_changed(self):
        self._update_cron_setting(True)

    def on_open_cron_dashboard(self):
        from mvp.view.common.CronDashboardDialog import CronDashboardDialog
        dlg = CronDashboardDialog(self.v, self._cron_history)
        dlg.Show()

    def on_datepicker_changed(self, evt):
        date_str = evt.GetDate().Format("%Y-%m-%d")
        evt.Skip()
        tp = self.v.taskProperty
        prop = tp.GetSelection()
        if prop is not None:
            prop.SetValue(prop.GetValue() + date_str)
            self._modify_property(prop)

    def on_cb_astool_changed(self, evt):
        # Snapshot for undo
        self._push_snapshot()

        combo = self.v.executionChooser
        name = combo.GetValue()
        self.v.execution_desc.set_execution_name(name)
        if evt.IsChecked():
            if not self._check_last_task_is_response_key() and not self._has_output_schema_properties():
                wx.MessageBox(
                    t("warn_missing_response_key"),
                    "Info",
                    wx.OK | wx.ICON_INFORMATION,
                    self.v,
                )

            current_desc = self.v.execution_desc.GetValue().strip()
            if not current_desc:
                tpl = self._build_mcp_tool_template(name)
                initial_params = self._extract_initial_params()
                if initial_params:
                    props = {}
                    for key, value in initial_params.items():
                        prop = {"title": key, "type": "string", "description": ""}
                        if value:
                            prop["default"] = str(value)
                        props[key] = prop
                    tpl["inputSchema"]["properties"] = props
                    tpl["inputSchema"]["required"] = list(initial_params.keys())
                default_desc = json.dumps(tpl, indent=2, ensure_ascii=False)
                self.v.execution_desc.SetValue(default_desc)
        else:
            input_params = self._extract_input_params_from_desc()
            if input_params and not self._check_first_task_is_initial_params():
                dlg = wx.MessageDialog(
                    self.v,
                    t("prompt_sync_initial_params"),
                    "Info",
                    wx.YES_NO | wx.ICON_INFORMATION,
                )
                result = dlg.ShowModal()
                dlg.Destroy()
                if result == wx.ID_YES:
                    self._insert_initial_params_task(input_params)
        # Update tool names set for palette display
        if evt.IsChecked():
            self._tool_names.add(name)
        else:
            self._tool_names.discard(name)
        self._sync_mcp_panel_visibility()

    def _sync_mcp_panel_visibility(self):
        splitter = self.v.e_right_panel
        is_tool = self.v.cb_astool.IsChecked()
        h = splitter.GetSize()[1]
        if is_tool:
            pgrid = self.v.taskProperty
            row_h = pgrid.GetGrid().GetRowHeight()
            page = pgrid.GetPage(self.single_page)
            prop_count = sum(1 for _ in page.GetPyIterator(wx.propgrid.PG_ITERATE_ALL))
            display_rows = min(prop_count, 5)
            pgrid_needed = (display_rows + 1) * row_h + 40
            sash = max(pgrid_needed, 50)
            splitter.SetSashPosition(sash)
        else:
            splitter.SetSashPosition(h - 28)

    def _check_last_task_is_response_key(self) -> bool:
        grid = self.v.taskGrid
        for row in range(grid.GetNumberRows() - 1, -1, -1):
            task_type = grid.GetCellValue(row, 0).strip()
            if task_type:
                return task_type == "HTTP_RESPONSE_KEY"
        return False

    def _has_output_schema_properties(self) -> bool:
        desc_str = self.v.execution_desc.GetValue().strip()
        if not desc_str:
            return False
        try:
            parsed = json.loads(desc_str)
        except (json.JSONDecodeError, TypeError):
            return False
        output_schema = parsed.get("outputSchema")
        return isinstance(output_schema, dict) and bool(output_schema.get("properties"))

    def _check_first_task_is_initial_params(self) -> bool:
        grid = self.v.taskGrid
        for row in range(grid.GetNumberRows()):
            task_type = grid.GetCellValue(row, 0).strip()
            if task_type:
                return task_type == "INITIAL_PARAMS"
        return False

    def _extract_input_params_from_desc(self):
        desc_str = self.v.execution_desc.GetValue().strip()
        if not desc_str:
            return None
        try:
            parsed = json.loads(desc_str)
        except (json.JSONDecodeError, TypeError):
            return None
        input_schema = parsed.get("inputSchema")
        if not isinstance(input_schema, dict):
            return None
        props = input_schema.get("properties", {})
        if not props:
            return None
        return {name: spec.get("default", "") for name, spec in props.items()}

    def _insert_initial_params_task(self, params: dict):
        grid = self.v.taskGrid
        grid.InsertRows(0, 1)
        grid.SetCellValue(0, 0, "INITIAL_PARAMS")
        grid.SetCellValue(0, 1, json.dumps(params, ensure_ascii=False))
        self._offset_loop_indices(1)

    def _offset_loop_indices(self, offset: int):
        page = self.v.loopProperty.GetPage(self.single_page)
        for prop in page.GetPyIterator(wx.propgrid.PG_ITERATE_ALL):
            if isinstance(prop, wx.propgrid.PropertyCategory):
                continue
            try:
                attrs = json.loads(prop.GetValue())
            except (json.JSONDecodeError, TypeError):
                continue
            changed = False
            for key in ("task_start", "task_end"):
                if key in attrs:
                    attrs[key] = int(attrs[key]) + offset
                    changed = True
            if changed:
                prop.SetValue(json.dumps(attrs, ensure_ascii=False))

    def _on_sync_input_from_task(self):
        params = self._extract_selected_task_params(fallback_row=0)
        if not params:
            wx.MessageBox(t("mcp_sync_no_params"), "Info", wx.OK | wx.ICON_INFORMATION, self.v)
            return
        existing = {self.v.execution_desc._input_grid.GetCellValue(r, 0).strip()
                    for r in range(self.v.execution_desc._input_grid.GetNumberRows())}
        selected = self._show_sync_param_dialog(
            t("mcp_dlg_sync_title"), params, existing)
        if selected is None:
            return
        self._push_snapshot()
        self.v.execution_desc.sync_input_params(selected)
        self._update_save_button()

    def _on_sync_output_from_task(self):
        params = self._extract_selected_task_params(fallback_row=-1)
        if not params:
            wx.MessageBox(t("mcp_sync_output_no_params"), "Info", wx.OK | wx.ICON_INFORMATION, self.v)
            return
        existing = {self.v.execution_desc._output_grid.GetCellValue(r, 0).strip()
                    for r in range(self.v.execution_desc._output_grid.GetNumberRows())}
        selected = self._show_sync_param_dialog(
            t("mcp_dlg_sync_output_title"), params, existing)
        if selected is None:
            return
        self._push_snapshot()
        self.v.execution_desc.sync_output_params(selected)
        self._update_save_button()

    def _show_sync_param_dialog(self, title: str, params: dict, existing: set):
        """Show a checkbox dialog for selecting params to sync.

        Returns a dict of selected {key: value}, or None if cancelled.
        """
        dlg = wx.Dialog(self.v, title=title, size=(350, 430))
        sizer = wx.BoxSizer(wx.VERTICAL)

        # check/uncheck all row
        toggle_row = wx.BoxSizer(wx.HORIZONTAL)
        btn_all = wx.Button(dlg, label=t("mcp_sync_check_all"), size=(-1, 24))
        btn_none = wx.Button(dlg, label=t("mcp_sync_uncheck_all"), size=(-1, 24))
        toggle_row.Add(btn_all, 0, wx.RIGHT, 4)
        toggle_row.Add(btn_none, 0)
        sizer.Add(toggle_row, 0, wx.LEFT | wx.RIGHT | wx.TOP, 8)

        scrolled = wx.ScrolledWindow(dlg)
        scrolled.SetScrollRate(0, 10)
        cb_sizer = wx.BoxSizer(wx.VERTICAL)
        checkboxes = []
        for key in params:
            cb = wx.CheckBox(scrolled, label=key)
            cb.SetValue(key not in existing)
            checkboxes.append((key, cb))
            cb_sizer.Add(cb, 0, wx.ALL, 4)
        scrolled.SetSizer(cb_sizer)
        sizer.Add(scrolled, 1, wx.EXPAND | wx.ALL, 8)
        btn_sizer = dlg.CreateStdDialogButtonSizer(wx.OK | wx.CANCEL)
        sizer.Add(btn_sizer, 0, wx.EXPAND | wx.ALL, 8)
        dlg.SetSizer(sizer)

        def _check_all(_evt):
            for _, cb in checkboxes:
                cb.SetValue(True)

        def _uncheck_all(_evt):
            for _, cb in checkboxes:
                cb.SetValue(False)

        btn_all.Bind(wx.EVT_BUTTON, _check_all)
        btn_none.Bind(wx.EVT_BUTTON, _uncheck_all)

        if dlg.ShowModal() != wx.ID_OK:
            dlg.Destroy()
            return None
        selected = {key: params[key] for key, cb in checkboxes if cb.GetValue()}
        dlg.Destroy()
        return selected if selected else {}

    def _extract_initial_params(self):
        grid = self.v.taskGrid
        if grid.GetNumberRows() == 0:
            return None
        first_type = grid.GetCellValue(0, 0).strip()
        if first_type != "INITIAL_PARAMS":
            return None
        first_input = grid.GetCellValue(0, 1).strip()
        if not first_input:
            return None
        try:
            params = json.loads(first_input)
            if isinstance(params, dict) and params:
                skipped = params.pop("skipped", None)
                return params if params else None
            return None
        except (json.JSONDecodeError, TypeError):
            return None

    def _extract_selected_task_params(self, fallback_row=0):
        grid = self.v.taskGrid
        row_count = grid.GetNumberRows()
        if row_count == 0:
            return None
        row = self.current_selected_row if self.current_selected_row >= 0 else (
            row_count - 1 if fallback_row == -1 else fallback_row
        )
        if row >= row_count:
            return None
        task_input = grid.GetCellValue(row, 1).strip()
        if not task_input:
            return None
        try:
            params = json.loads(task_input)
            if isinstance(params, dict) and params:
                params.pop("skipped", None)
                return params if params else None
            return None
        except (json.JSONDecodeError, TypeError):
            return None

    def _should_inject_mcp_defaults(self, execution) -> bool:
        return bool(execution.get_mcp_input_defaults())

    @staticmethod
    def _extract_mcp_input_defaults(execution, data_chain: dict = None) -> dict:
        return execution.expand_mcp_defaults(data_chain or {})

    @staticmethod
    def _build_mcp_tool_template(execution_name: str) -> dict:
        return {
            "desc": f"<Brief description of what {execution_name} does>",
            "inputSchema": {
                "type": "object",
                "title": f"{execution_name}Arguments",
                "properties": {},
                "required": []
            },
            "outputSchema": {
                "type": "object",
                "title": f"{execution_name}Output",
                "properties": {},
                "required": []
            }
        }

    def _init_handy_tools(self):
        def get_value():
            prop = self.v.taskProperty.GetSelection()
            return prop.GetValue() if prop else None

        def set_value(value):
            prop = self.v.taskProperty.GetSelection()
            if prop is None:
                return
            prop.SetValue(value)
            self._modify_property(prop)

        self.v.handy_tools.bind_accessors(get_value, set_value)

    def on_add_property(self):
        k = self.v.availableProperties.GetValue()

        if not len(k) > 0:
            return

        if self._pgrid_bound_row < 0:
            logging.info(t("msg_no_task_row_bound"))
            return

        grid = self.v.taskGrid
        processor = grid.GetCellValue(self._pgrid_bound_row, 0)
        tpl_dict = json.loads(Processor.get_processor_by_type(processor).get_tpl())

        if not k in tpl_dict:
            v = ''
        else:
            v = tpl_dict[k]

        page = self.v.taskProperty.GetPage(self.single_page)
        self._append_or_update_property_to_page(k, v, page)
        self._add_property(k, v)

        raw = grid.GetCellValue(self._pgrid_bound_row, 1)
        try:
            input_dict = json.loads(raw) if raw.strip() else {}
        except (json.JSONDecodeError, TypeError):
            input_dict = {}
        self._fill_available_properties(processor, input_dict)

    def on_skip_task_changed(self, evt):
        # Guard: a task row must be selected before toggling skip state
        if self.current_selected_row < 0:
            logging.info(t("msg_select_task_row_first"))
            return

        page = self.v.taskProperty.GetPage(self.single_page)

        if evt.IsChecked():
            # Mark task as skipped: add/update 'skipped = yes' in both
            # the property grid panel and the backing task JSON in the grid cell
            self._append_or_update_property_to_page("skipped", "yes", page)
            self._add_property("skipped", "yes")
        else:
            # Un-skip: update 'skipped' to 'no' so the key stays visible
            # but is no longer treated as a skip signal by _check_task_skipped
            self._append_or_update_property_to_page("skipped", "no", page)
            self._add_property("skipped", "no")

        self._apply_row_skip_style(self.current_selected_row, evt.IsChecked())

    def on_delete_property(self):
        tp = self.v.taskProperty
        prop = tp.GetSelection()
        if prop is None or isinstance(prop, wx.propgrid.PropertyCategory):
            logging.info(t("msg_select_property_first"))
            return

        if self._pgrid_bound_row < 0:
            logging.info(t("msg_no_task_row_bound"))
            return

        self._delete_property(prop)
        self._delete_selected_property_from_page(tp)

        grid = self.v.taskGrid

        input_dict = json.loads(grid.GetCellValue(self._pgrid_bound_row, 1))
        processor = grid.GetCellValue(self._pgrid_bound_row, 0)
        self._fill_available_properties(processor, input_dict)

    def _move_pgrid_property(self, direction):
        tp = self.v.taskProperty
        page = tp.GetPage(self.single_page)
        prop = tp.GetSelection()
        if prop is None or isinstance(prop, wx.propgrid.PropertyCategory):
            return
        selected_name = prop.GetName()
        props = [
            (p.GetName(), p.GetValue())
            for p in page.GetPyVIterator(wx.propgrid.PG_ITERATE_PROPERTIES)
            if not isinstance(p, wx.propgrid.PropertyCategory)
        ]
        idx = next((i for i, (n, _) in enumerate(props) if n == selected_name), None)
        if idx is None:
            return
        new_idx = idx + direction
        if new_idx < 0 or new_idx >= len(props):
            return
        props[idx], props[new_idx] = props[new_idx], props[idx]
        for name, _ in props:
            page.DeleteProperty(name)
        for name, value in props:
            self._append_or_update_property_to_page(name, value, page)
        page.FitColumns()
        tp.SelectProperty(page.GetPropertyByName(selected_name))

        grid = self.v.taskGrid
        if self._pgrid_bound_row >= 0:
            input_dict = json.loads(grid.GetCellValue(self._pgrid_bound_row, 1))
            ordered = {name: input_dict[name] for name, _ in props if name in input_dict}
            rest = {k: v for k, v in input_dict.items() if k not in ordered}
            grid.SetCellValue(self._pgrid_bound_row, 1, json.dumps(ordered | rest))
            self._push_snapshot()

    def _delete_selected_property_from_page(self, pgm):
        prop = pgm.GetSelection()
        if prop is None or isinstance(prop, wx.propgrid.PropertyCategory):
            logging.info(t("msg_select_value_property"))
            return
        pgm.DeleteProperty(prop.GetName())

    def _update_cron_setting(self, enabled: bool):
        if enabled:
            self.v.cronInput.Enable(True)
        else:
            self.v.cronInput.Enable(False)
        cronExp = self.v.cronInput.GetValue()
        cronDesc = self._explain_cron(cronExp)
        self.v.cronInput.SetToolTip(cronDesc)
        logging.info("CORN [ %s ] -> %s", cronExp, cronDesc)

    def _explain_cron(self, cron):
        try:
            return str(ExpressionDescriptor(cron))
        except Exception as e:
            logging.error(t("msg_cron_invalid_hint", cron_invalid=t(self.CRON_INVALID), cron=cron))
            return t(self.CRON_INVALID)

    def on_property_change4e(self, evt):
        prop = evt.GetProperty()
        evt.Skip()
        self._modify_property(prop)

    def on_property_right_click4e(self, evt):
        prop = evt.GetProperty()
        evt.Skip()
        if prop is None or isinstance(prop, wx.propgrid.PropertyCategory):
            return

        self._right_clicked_property = prop

        menu = wx.Menu()
        id_copy_name = wx.NewId()
        id_copy_value = wx.NewId()
        id_copy_pair = wx.NewId()
        id_paste_pair = wx.NewId()
        id_edit_complex = wx.NewId()
        id_rename_key = wx.NewId()
        id_move_up = wx.NewId()
        id_move_down = wx.NewId()
        id_param_hint = wx.NewId()

        menu.Append(id_copy_name, t("menu_copy_name"))
        menu.Append(id_copy_value, t("menu_copy_value"))
        menu.Append(id_copy_pair, t("menu_copy_pair"))
        menu.Append(id_paste_pair, t("menu_paste_pair"))
        menu.Enable(id_paste_pair, self._clipboard_has_property_pair())
        menu.AppendSeparator()
        menu.Append(id_rename_key, t("menu_rename_key"))
        menu.Append(id_edit_complex, t("menu_edit_complex"))
        menu.Append(id_param_hint, t("menu_param_hint"))
        processor_name = self.v.taskGrid.GetCellValue(self.current_selected_row, 0).strip()
        hint_available = False
        if processor_name and processor_name != 'INITIAL_PARAMS' and self._right_clicked_property:
            try:
                p = Processor.get_processor_by_type(processor_name)
                desc = p.get_localized_desc() if hasattr(p, 'get_localized_desc') else p.DESC
                hint_available = bool(self._extract_param_hint(desc, self._right_clicked_property.GetName()))
            except Exception:
                pass
        hint_enabled = bool(hint_available or (self._param_hint_dlg and self._param_hint_dlg.IsShown()))
        menu.Enable(id_param_hint, hint_enabled)
        menu.AppendSeparator()
        menu.Append(id_move_up, t("menu_move_up"))
        menu.Append(id_move_down, t("menu_move_down"))

        can_undo = self._snapshot_cursor >= 0
        can_redo = self._snapshot_cursor < len(self._snapshots) - 1
        if can_undo or can_redo:
            menu.AppendSeparator()
            if can_undo:
                id_undo = wx.NewId()
                menu.Append(id_undo, t("menu_undo"))
                self.v.Bind(wx.EVT_MENU, self._on_undo, id=id_undo)
            if can_redo:
                id_redo = wx.NewId()
                menu.Append(id_redo, t("menu_redo"))
                self.v.Bind(wx.EVT_MENU, self._on_redo, id=id_redo)

        self.v.Bind(wx.EVT_MENU, self._on_copy_property_name, id=id_copy_name)
        self.v.Bind(wx.EVT_MENU, self._on_copy_property_value, id=id_copy_value)
        self.v.Bind(wx.EVT_MENU, self._on_copy_property_pair, id=id_copy_pair)
        self.v.Bind(wx.EVT_MENU, self._on_paste_property_pair, id=id_paste_pair)
        self.v.Bind(wx.EVT_MENU, self._on_edit_complex_value, id=id_edit_complex)
        self.v.Bind(wx.EVT_MENU, self._on_rename_property_key, id=id_rename_key)
        self.v.Bind(wx.EVT_MENU, self._on_show_param_hint, id=id_param_hint)
        self.v.Bind(wx.EVT_MENU, lambda e: self._move_pgrid_property(-1), id=id_move_up)
        self.v.Bind(wx.EVT_MENU, lambda e: self._move_pgrid_property(1), id=id_move_down)

        self.v.PopupMenu(menu)
        menu.Destroy()

    def on_task_property_selected4e(self, evt):
        evt.Skip()
        prop = evt.GetProperty()
        if prop is None or isinstance(prop, wx.propgrid.PropertyCategory):
            return
        if self._param_hint_dlg and self._param_hint_dlg.IsShown():
            self._show_param_hint_for_prop(prop)

    def _on_show_param_hint(self, evt):
        self._show_param_hint_for_prop(self._right_clicked_property)

    def _show_param_hint_for_prop(self, prop):
        if prop is None:
            return
        param_name = prop.GetName()
        processor_name = self.v.taskGrid.GetCellValue(self.current_selected_row, 0).strip()
        if not processor_name or processor_name == 'INITIAL_PARAMS':
            return
        try:
            p = Processor.get_processor_by_type(processor_name)
            desc = p.get_localized_desc() if hasattr(p, 'get_localized_desc') else p.DESC
        except Exception:
            return
        hint = self._extract_param_hint(desc, param_name)
        if self._param_hint_dlg and self._param_hint_dlg.IsShown():
            self._param_hint_dlg.SetTitle(param_name)
            self._param_hint_dlg._txt.SetValue(hint if hint else t('param_hint_not_found', name=param_name))
            self._param_hint_dlg.Raise()
        else:
            if not hint:
                return
            dlg = wx.Dialog(self.v, title=param_name, style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
            txt = wx.TextCtrl(dlg, value=hint,
                              style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2 | wx.TE_AUTO_URL)
            txt.SetMinSize(wx.Size(480, 120))
            btn_close = wx.Button(dlg, wx.ID_CLOSE, t("btn_close"))
            btn_close.Bind(wx.EVT_BUTTON, lambda e: dlg.Hide())
            sizer = wx.BoxSizer(wx.VERTICAL)
            sizer.Add(txt, 1, wx.EXPAND | wx.ALL, 8)
            sizer.Add(btn_close, 0, wx.ALIGN_RIGHT | wx.RIGHT | wx.BOTTOM, 8)
            dlg.SetSizerAndFit(sizer)
            dlg._txt = txt
            self._param_hint_dlg = dlg
            dlg.Show()

    @staticmethod
    def _extract_param_hint(desc: str, param_name: str) -> str:
        lines = desc.splitlines()
        collecting = False
        parts = []
        for line in lines:
            stripped = line.strip()
            if not collecting:
                if stripped.startswith(f'- {param_name}:') or stripped.startswith(f'- {param_name} '):
                    parts.append(stripped[2:].strip())
                    collecting = True
            else:
                if stripped.startswith('- '):
                    break
                if stripped:
                    parts.append(stripped)
        return '\n'.join(parts)

    def _on_undo(self, evt):
        self._undo()

    def _on_redo(self, evt):
        self._redo()

    def _on_open_snapshots(self, evt):
        from mvp.view.common.SnapshotDialog import SnapshotDialog
        dlg = SnapshotDialog(self.v, self._snapshots, self._snapshot_cursor)
        if dlg.ShowModal() == wx.ID_OK:
            idx = dlg.get_selected_index()
            if idx is not None and 0 <= idx < len(self._snapshots):
                self._push_snapshot()
                self._restore_snapshot(self._snapshots[idx])
        dlg.Destroy()

    def _on_copy_property_name(self, evt):
        if self._right_clicked_property is not None:
            name = self._right_clicked_property.GetName()
            if wx.TheClipboard.Open():
                wx.TheClipboard.SetData(wx.TextDataObject(str(name)))
                wx.TheClipboard.Close()
                logging.info(f'Copied property name to clipboard: {name}')

    def _on_copy_property_pair(self, evt):
        prop = self._right_clicked_property
        if prop is None:
            return
        pair = json.dumps({prop.GetName(): prop.GetValue()})
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(wx.TextDataObject(pair))
            wx.TheClipboard.Close()
            logging.info(f'Copied property pair to clipboard: {pair}')

    def _clipboard_has_property_pair(self):
        if not wx.TheClipboard.Open():
            return False
        data = wx.TextDataObject()
        success = wx.TheClipboard.GetData(data)
        wx.TheClipboard.Close()
        if not success:
            return False
        try:
            parsed = json.loads(data.GetText())
            return isinstance(parsed, dict) and len(parsed) > 0
        except (json.JSONDecodeError, ValueError):
            return False

    def _on_paste_property_pair(self, evt):
        if self._pgrid_bound_row < 0:
            return
        if not wx.TheClipboard.Open():
            return
        data = wx.TextDataObject()
        success = wx.TheClipboard.GetData(data)
        wx.TheClipboard.Close()
        if not success:
            return
        try:
            pair = json.loads(data.GetText())
            if not isinstance(pair, dict):
                return
        except (json.JSONDecodeError, ValueError):
            return
        page = self.v.taskProperty.GetPage(self.single_page)
        for k, v in pair.items():
            self._append_or_update_property_to_page(k, v, page)
            self._add_property(k, v)
        logging.info(f'Pasted property pair: {pair}')

    def _on_rename_property_key(self, evt):
        prop = self._right_clicked_property
        if prop is None or self._pgrid_bound_row < 0:
            return
        old_name = prop.GetName()
        dlg = InputDialog(self.v, title=t("dlg_rename_key_title"),
                          message=t("dlg_rename_key_msg"), default_value=old_name)
        if dlg.ShowModal() != wx.ID_OK:
            dlg.Destroy()
            return
        new_name = dlg.GetValue().strip()
        dlg.Destroy()
        if not new_name or new_name == old_name:
            return

        tp = self.v.taskProperty
        page = tp.GetPage(self.single_page)
        props = [
            (p.GetName(), p.GetValue())
            for p in page.GetPyVIterator(wx.propgrid.PG_ITERATE_PROPERTIES)
            if not isinstance(p, wx.propgrid.PropertyCategory)
        ]
        for name, _ in props:
            page.DeleteProperty(name)
        for name, value in props:
            self._append_or_update_property_to_page(new_name if name == old_name else name, value, page)
        page.FitColumns()
        tp.SelectProperty(page.GetPropertyByName(new_name))

        grid = self.v.taskGrid
        input_dict = json.loads(grid.GetCellValue(self._pgrid_bound_row, 1))
        renamed = {(new_name if k == old_name else k): v for k, v in input_dict.items()}
        grid.SetCellValue(self._pgrid_bound_row, 1, json.dumps(renamed))
        self._push_snapshot()
        logging.info(f'Renamed property key: {old_name} → {new_name}')

    def _on_copy_property_value(self, evt):
        if self._right_clicked_property is not None:
            value = self._right_clicked_property.GetValue()
            if wx.TheClipboard.Open():
                wx.TheClipboard.SetData(wx.TextDataObject(str(value)))
                wx.TheClipboard.Close()
                logging.info(f'Copied property value to clipboard: {value}')

    def _on_edit_complex_value(self, evt):
        prop = self._right_clicked_property
        if prop is None:
            return

        prop_name = prop.GetName()
        raw_value = prop.GetValue()

        if isinstance(raw_value, str):
            display_value = raw_value.replace('\\n', '\n').replace('\\t', '\t')
        else:
            display_value = str(raw_value)

        task_number = (self._pgrid_bound_row or 0) + 1
        dlg = InputDialog(self.v, title=f"Edit Complex Value - Task {task_number}",
                          message=f"Property: {prop_name}",
                          default_value=display_value)

        if dlg.ShowModal() == wx.ID_OK:
            new_value = dlg.GetValue()
            stored_value = new_value.replace('\n', '\\n').replace('\t', '\\t')
            prop.SetValue(stored_value)
            self._modify_property(prop)

        dlg.Destroy()

    def _add_property(self, propName, propValue):
        self._op_taskgrid_property(propName, propValue, lambda inputDict, key, value: inputDict | {key: value})
        logging.debug(f'Input property added @Task{self._pgrid_bound_row + 1} - [ {propName} = {propValue} ]')

    def _delete_property(self, prop):
        self._op_taskgrid_property(prop.GetName(), prop.GetValue(),
                                   lambda inputDict, key, value: {k: v for k, v in inputDict.items() if not k == key})
        logging.debug(f'Input property deleted @Task{self._pgrid_bound_row + 1} - [ {prop.GetName()} ]')

    def _modify_property(self, prop):
        value = prop.GetValue()
        if isinstance(value, str):
            try:
                value = int(value)
            except (ValueError, TypeError):
                pass
        self._op_taskgrid_property(prop.GetName(), value,
                                   lambda inputDict, key, value: inputDict | {key: value})
        logging.debug(
            f'Input property modified @Task{self._pgrid_bound_row + 1} - [ {prop.GetName()} = {prop.GetValue()} ]')

    def _op_taskgrid_property(self, key, value, func):
        task_grid = self.v.taskGrid
        input_col = 1

        # Use the row the property grid was populated for, NOT the
        # currently selected grid row — they can differ when the user
        # clicks a new row while a property editor is still open.
        target_row = self._pgrid_bound_row

        if target_row is None or target_row < 0 or key is None or value is None:
            return

        if target_row != self.current_selected_row:
            logging.warning(
                f'Property grid bound to row {target_row} but grid selection is at row '
                f'{self.current_selected_row} — writing to row {target_row} (property grid source).')

        raw = task_grid.GetCellValue(target_row, input_col)
        self._push_snapshot()
        try:
            input_dict = json.loads(raw) if raw.strip() else {}
        except (json.JSONDecodeError, TypeError):
            input_dict = {}
        input_dict = func(input_dict, key, value)
        task_grid.SetCellValue(target_row, input_col, json.dumps(input_dict))
        self._update_save_button()

    def _is_dirty(self):
        if self._saved_snapshot is None:
            return False
        current = self._capture_snapshot()
        return (
                current["tasks"] != self._saved_snapshot["tasks"]
                or current["loops"] != self._saved_snapshot["loops"]
                or current["mcp_desc"] != self._saved_snapshot["mcp_desc"]
                or current["astool"] != self._saved_snapshot["astool"]
        )

    def _update_save_button(self):
        dirty = self._is_dirty()
        has_snapshots = len(self._snapshots) > 0
        self.v.saveExection.Enable(dirty or has_snapshots)
        self.v.snapshots.Enable(has_snapshots)

    def _mark_clean(self):
        self._saved_snapshot = self._capture_snapshot()
        self._update_save_button()

    def _capture_snapshot(self):
        grid = self.v.taskGrid
        tasks = []
        for r in range(grid.GetNumberRows()):
            t_type = grid.GetCellValue(r, 0)
            t_input = grid.GetCellValue(r, 1)
            if not t_type and not t_input:
                break
            tasks.append({"type": t_type, "input": t_input})

        loops = []
        page = self.v.loopProperty.GetPage(self.single_page)
        for prop in page.GetPyIterator(wx.propgrid.PG_ITERATE_ALL):
            if isinstance(prop, wx.propgrid.PropertyCategory):
                continue
            loops.append({"loop_code": prop.GetName(), "loop_attributes": prop.GetValue()})

        return {
            "timestamp": DateUtil.get_now_in_str("%H:%M:%S"),
            "tasks": tasks,
            "loops": loops,
            "mcp_desc": self.v.execution_desc.GetValue(),
            "astool": self.v.cb_astool.IsChecked(),
        }

    def _restore_snapshot(self, snap):
        prev_row = self.current_selected_row
        grid = self.v.taskGrid
        grid.BeginBatch()
        grid.ClearGrid()

        tasks = snap["tasks"]
        while grid.GetNumberRows() < len(tasks):
            self._insert_row(grid, self.available_processors)

        for idx, task in enumerate(tasks):
            grid.SetCellValue(idx, 0, task["type"])
            grid.SetCellValue(idx, 1, task["input"])

        self._apply_all_row_skip_styles()
        grid.EndBatch()

        self._reset_loop_pgrid()
        loop_page = self.v.loopProperty.GetPage(self.single_page)
        for loop in snap["loops"]:
            self._append_or_update_property_to_page(loop["loop_code"], loop["loop_attributes"], loop_page)

        self.v.execution_desc.SetValue(snap["mcp_desc"])
        self.v.cb_astool.SetValue(snap["astool"])

        name = self.v.executionChooser.GetValue()
        if snap["astool"]:
            self._tool_names.add(name)
        else:
            self._tool_names.discard(name)

        self._pgrid_bound_row = -1
        self._reset_task_pgrid()

        if prev_row >= 0 and prev_row < grid.GetNumberRows():
            grid.SelectRow(prev_row)
            self._load_input_taskproperty(prev_row)

    def _push_snapshot(self):
        snap = self._capture_snapshot()
        del self._snapshots[self._snapshot_cursor + 1:]
        self._snapshots.append(snap)
        if len(self._snapshots) > self._SNAPSHOT_MAX:
            self._snapshots.pop(0)
        self._snapshot_cursor = len(self._snapshots) - 1
        self._update_save_button()

    def _undo(self):
        if self._snapshot_cursor < 0:
            return
        snap = self._snapshots[self._snapshot_cursor]
        current = self._capture_snapshot()
        self._snapshots[self._snapshot_cursor] = current
        self._restore_snapshot(snap)
        self._snapshot_cursor -= 1
        self._update_save_button()
        logging.debug(f'Undo → snapshot @{snap["timestamp"]}')

    def _redo(self):
        if self._snapshot_cursor >= len(self._snapshots) - 1:
            return
        self._snapshot_cursor += 1
        snap = self._snapshots[self._snapshot_cursor]
        current = self._capture_snapshot()
        self._snapshots[self._snapshot_cursor] = current
        self._restore_snapshot(snap)
        self._update_save_button()
        logging.debug(f'Redo → snapshot @{snap["timestamp"]}')

    def on_grid_cell_change4p(self, evt):
        grid = self.v.executionGrid
        current_row = evt.GetRow()
        current_column = evt.GetCol()
        evt.Skip()

    def _insert_row(self, grid, choices):
        selected_rows = grid.GetSelectedRows()
        total_rows = grid.GetNumberRows()
        insert_at_row = selected_rows[0] if len(selected_rows) > 0 else 0

        # if select on last row, then append.
        if insert_at_row + 1 == total_rows:
            insert_at_row = total_rows

        grid.InsertRows(insert_at_row, 1, True)
        self._bind_grid_cell_choice_editor(insert_at_row, grid, choices)

    def on_add_row4e(self):
        self._push_snapshot()
        task_grid = self.v.taskGrid
        self._insert_row(task_grid, self.available_processors)
        self._update_save_button()

    def on_add_row4p(self):
        execution_grid = self.v.executionGrid
        self._insert_row(execution_grid, self.available_executions)

    def on_delete_rows4e(self):
        self._push_snapshot()
        self._on_delete_rows(self.v.taskGrid)
        self._update_save_button()

    def on_delete_rows4p(self):
        self._on_delete_rows(self.v.executionGrid)

    def _on_delete_rows(self, grid):
        total_row = grid.GetNumberRows()
        if total_row > 0:
            rows_be_deleted = grid.GetSelectedRows()
            last_row_at = total_row - 1
            deleteStartRow = rows_be_deleted[0] if len(rows_be_deleted) > 0 else last_row_at
            deleteNumber = len(rows_be_deleted) if len(rows_be_deleted) > 0 else 1
            grid.DeleteRows(pos=deleteStartRow, numRows=deleteNumber, updateLabels=True)

    def highlight_running_task(self, data):
        if not isinstance(data, dict):
            return
        exec_name = data.get("execution")
        task_index = data.get("task_index")
        task_total = data.get("task_total")
        proc_name = data.get("proc_name", "")
        if exec_name is None or task_index is None:
            return
        if exec_name != self.v.executionChooser.GetValue():
            return
        grid = self.v.taskGrid
        if 0 <= task_index < grid.GetNumberRows():
            grid.SelectRow(task_index)
            grid.MakeCellVisible(task_index, 0)
        if task_total:
            elapsed = time.time() - self._exec_start_time if self._exec_start_time else 0
            self._set_highlight_info(
                f"[{task_index + 1}/{task_total}] {proc_name}  ({elapsed:.1f}s)")

    def clear_running_task_highlight(self):
        self.v.taskGrid.ClearSelection()

    def _on_log_timer(self, evt):
        if not self.keep_running:
            return
        self.on_load_log_async()

    def on_load_log_async(self):
        """Async log reload triggered by timer."""
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.submit(self.on_load_log)

    def on_load_log(self):
        if hasattr(self, 'isLoading') and self.isLoading:
            return

        if self.is_log_content_focused:
            return

        log_path = OSUtils.get_log_file_path(self.m.app_name)

        try:
            self.isLoading = True
            max_size = 5 * 1024 * 1024  # 5MB

            try:
                st = os.stat(log_path)
            except OSError:
                return
            file_size = st.st_size
            file_ino = st.st_ino

            # Reopen if: no fd, inode changed (rotation), or file truncated
            if (self._log_fd is None
                    or self._log_ino != file_ino
                    or file_size < self._log_last_pos):
                if self._log_fd is not None:
                    self._log_fd.close()
                self._log_fd = open(log_path, 'r', encoding='utf8', errors='replace')
                self._log_ino = file_ino
                self._log_last_pos = 0

            if self._log_last_pos == 0:
                # --- Full load (initial or after clean/rotation) ---
                if file_size > max_size:
                    self._log_fd.seek(file_size - max_size)
                    self._log_fd.readline()  # skip partial line
                    content = f"[log is too big, only showing last {max_size / 1024 / 1024:.1f}MB.]\n\n" + self._log_fd.read()
                else:
                    self._log_fd.seek(0)
                    content = self._log_fd.read()
                self._log_last_pos = self._log_fd.tell()
                wx.CallAfter(self._full_update_log, content)
            else:
                # No new content — skip
                if file_size == self._log_last_pos:
                    return
                # --- Incremental append (the fast path) ---
                self._log_fd.seek(self._log_last_pos)
                new_content = self._log_fd.read()
                self._log_last_pos = self._log_fd.tell()

                if new_content:
                    wx.CallAfter(self._append_log, new_content, max_size)

        except Exception as e:
            logging.error(f"Fail to load log: {str(e)}")
            if self._log_fd is not None:
                self._log_fd.close()
                self._log_fd = None
        finally:
            self.isLoading = False

    def _apply_filter(self, content: str) -> str:
        """Return only lines containing the search keyword (case-insensitive)."""
        kw = self._log_search_keyword.lower()
        if not kw:
            return content
        return '\n'.join(line for line in content.splitlines() if kw in line.lower())

    def _full_update_log(self, content):
        """Full replacement — used only on first load or after clean."""
        self._log_full_content = content
        display = self._apply_filter(content) if self._log_filter_active else content
        try:
            self.v.logContents.Freeze()
            self.v.logContents.SetValue(display)
            self.v.logContents.ShowPosition(self.v.logContents.GetLastPosition())
        except Exception as e:
            logging.error(f"Update log error from UI: {str(e)}")
        finally:
            self.v.logContents.Thaw()
        if self._log_search_keyword and not self._log_filter_active:
            self._highlight_log_matches()

    def _append_log(self, new_content, max_size):
        """Incremental append — much faster than full SetValue."""
        self._log_full_content += new_content
        if len(self._log_full_content) > max_size:
            self._log_full_content = self._log_full_content[-max_size:]

        if self._log_filter_active:
            filtered = self._apply_filter(new_content)
            if not filtered:
                return
            display = filtered
        else:
            display = new_content

        try:
            self.v.logContents.Freeze()
            current_len = self.v.logContents.GetLastPosition()
            if current_len + len(display) > max_size:
                trim_amount = (current_len + len(display)) - max_size
                self.v.logContents.Remove(0, trim_amount)
            self.v.logContents.AppendText(display)
        except Exception as e:
            logging.error(f"Append log error from UI: {str(e)}")
        finally:
            self.v.logContents.Thaw()
        if self._log_search_keyword and not self._log_filter_active:
            self._highlight_log_matches()

    def on_clean_log(self):
        if self._log_fd is not None:
            self._log_fd.close()
            self._log_fd = None
        with open(OSUtils.get_log_file_path(self.m.app_name), 'w', encoding='utf8') as file:
            file.write(f'Clean {self.m.app_name} log@' + DateUtil.get_now_in_str() + '\n')
        self.is_log_content_focused = False
        self._log_last_pos = 0
        self._log_full_content = ''

    def on_logcontents_focused(self):
        self.is_log_content_focused = True

    def on_logcontents_unfocused(self):
        self.is_log_content_focused = False

    def on_search_log(self):
        keyword = self.v.logSearchBar.get_search_text().strip()
        min_search_chars = getattr(self.v.logSearchBar, 'MIN_SEARCH_CHARS', 3)
        if 0 < len(keyword) < min_search_chars:
            keyword = ''
        self._log_search_keyword = keyword
        if self._log_filter_active:
            self._reapply_filter()
        elif keyword:
            self._highlight_log_matches()
        else:
            self._clear_log_highlights()

    def on_filter_toggle(self, active: bool):
        self._log_filter_active = active
        if active:
            self._reapply_filter()
        else:
            self._clear_log_highlights()
            content = self._log_full_content
            if content:
                lc = self.v.logContents
                try:
                    lc.Freeze()
                    lc.SetValue(content)
                    lc.ShowPosition(lc.GetLastPosition())
                finally:
                    lc.Thaw()
            if self._log_search_keyword:
                self._highlight_log_matches()

    def _reapply_filter(self):
        content = self._log_full_content
        filtered = self._apply_filter(content)
        lc = self.v.logContents
        try:
            lc.Freeze()
            lc.SetValue(filtered)
            lc.ShowPosition(lc.GetLastPosition())
        finally:
            lc.Thaw()
        kw = self._log_search_keyword
        count = filtered.lower().count(kw.lower()) if kw else 0
        self.v.logSearchBar.matchCount.SetLabel(f'{count}' if count else '')

    def on_clear_log_search(self):
        self._log_search_keyword = ''
        self.v.logSearchBar.set_search_text('')
        self._clear_log_highlights()

    def _highlight_log_matches(self):
        keyword = self._log_search_keyword
        if not keyword:
            return
        lc = self.v.logContents
        text = lc.GetValue()
        text_lower = text.lower()
        keyword_lower = keyword.lower()
        kw_len = len(keyword_lower)

        th = get_theme()
        positions = []
        lc.Freeze()
        try:
            default_attr = wx.TextAttr(wx.Colour(*th.log_fg), wx.Colour(*th.log_bg))
            lc.SetStyle(0, lc.GetLastPosition(), default_attr)

            highlight_attr = wx.TextAttr(wx.Colour(*th.log_match_fg), wx.Colour(*th.log_match_bg))
            start = 0
            while True:
                pos = text_lower.find(keyword_lower, start)
                if pos < 0:
                    break
                lc.SetStyle(pos, pos + kw_len, highlight_attr)
                positions.append(pos)
                start = pos + kw_len

            self._log_match_positions = positions
            self._log_match_cursor = -1
            count = len(positions)
            self.v.logSearchBar.matchCount.SetLabel(t('log_match_count', count=count) if count > 0 else '')
        finally:
            lc.Thaw()

    def _focus_current_match(self):
        if not self._log_match_positions:
            return
        pos = self._log_match_positions[self._log_match_cursor]
        kw_len = len(self._log_search_keyword)
        lc = self.v.logContents

        th = get_theme()
        lc.Freeze()
        try:
            highlight_attr = wx.TextAttr(wx.Colour(*th.log_match_fg), wx.Colour(*th.log_match_bg))
            for p in self._log_match_positions:
                lc.SetStyle(p, p + kw_len, highlight_attr)
            current_attr = wx.TextAttr(wx.Colour(*th.log_current_match_fg), wx.Colour(*th.log_current_match_bg))
            lc.SetStyle(pos, pos + kw_len, current_attr)
        finally:
            lc.Thaw()

        lc.ShowPosition(pos)
        count = len(self._log_match_positions)
        idx = self._log_match_cursor + 1
        self.v.logSearchBar.matchCount.SetLabel(f'{idx}/{count}')

    def on_prev_log_match(self):
        if not self._log_match_positions:
            return
        self._log_match_cursor = (self._log_match_cursor - 1) % len(self._log_match_positions)
        self._focus_current_match()

    def on_next_log_match(self):
        if not self._log_match_positions:
            return
        self._log_match_cursor = (self._log_match_cursor + 1) % len(self._log_match_positions)
        self._focus_current_match()

    def _clear_log_highlights(self):
        lc = self.v.logContents
        th = get_theme()
        lc.Freeze()
        try:
            default_attr = wx.TextAttr(wx.Colour(*th.log_fg), wx.Colour(*th.log_bg))
            lc.SetStyle(0, lc.GetLastPosition(), default_attr)
            self.v.logSearchBar.matchCount.SetLabel('')
            self._log_match_positions = []
            self._log_match_cursor = -1
        finally:
            lc.Thaw()

    def on_handle_display_in_matplotlib_view(self, evt: PETPEvent):
        data = evt.data

        if data['chart_type'] == 'PIE':
            PETP_PIE_CHARTView(self.v, wx.ID_ANY, data=data).Show()
        elif data['chart_type'] == 'BAR':
            PETP_BAR_CHARTView(self.v, wx.ID_ANY, data=data).Show()
        elif data['chart_type'] == 'LINE':
            PETP_LINE_CHARTView(self.v, wx.ID_ANY, data=data).Show()
        else:
            logging.warning(t("msg_unsupported_chart", chart_type=data["chart_type"]))

    def on_handle_open_input_dialog(self, evt: PETPEvent):
        advance_dialog = InputDialog(self.v, evt.data['title'], evt.data['msg'], evt.data['default_value'])
        result_value = None

        if advance_dialog.ShowModal() == wx.ID_OK:
            result_value = advance_dialog.GetValue()

        advance_dialog.Destroy()

        if evt.handler:
            evt.handler(result_value)

    def on_sync_task_input(self, evt: PETPEvent):
        row = evt.data['row']
        new_input = evt.data['input']
        task_grid = self.v.taskGrid
        if row < 0 or row >= task_grid.GetNumberRows():
            return
        task_grid.SetCellValue(row, 1, new_input)
        self._push_snapshot()
        if self._pgrid_bound_row == row:
            self._load_input_taskproperty(row)
        self._update_save_button()

    def on_handle_http_request(self, evt: PETPEvent):
        action = evt.data['action']
        is_internal = evt.data.get('source') == 'internal'

        if action == 'execution':
            params = evt.data['params']
            exection_name = params['execution']
            execution: Execution = Execution.get_execution(params['execution'])

            if is_internal or (hasattr(execution, 'astool') and execution.astool):
                self.v.executionChooser.SetValue(exection_name)
                self.on_task_execution_changed()
                self.on_run_execution(params)
            else:
                from httpservice.handlers.HttpRequestHandler import HttpRequestHandler
                request_id_key = HttpRequestHandler.get_request_id_key()
                request_id = params.get(request_id_key)
                server = HttpRequestHandler.get_server()
                if request_id and server:
                    server.store_result(request_id, {"error": t("msg_exec_not_tool", name=exection_name)})
        logging.info(f'\nHTTP request be handled - action: {action}, params: {params}\n')

    def get_tools(self):
        cached = getattr(self, '_tools_cache', None)
        if cached is not None:
            return cached
        tools = {}
        for execution_name in self.available_executions:
            execution = Execution.get_execution(execution_name)
            if (hasattr(execution, 'astool') and execution.astool
                    and hasattr(execution, 'mcp_desc') and execution.mcp_desc):
                tools[execution_name] = execution.mcp_desc
        self._tools_cache = tools
        return tools

    def invalidate_tools_cache(self):
        self._tools_cache = None
