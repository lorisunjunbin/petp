import logging

import wx
import wx.dataview
import wx.lib.colourutils

from mvp.presenter.event.PETPEvent import PETPEvent
from mvp.view.common.LogSearchBar import EVT_LOG_BAR


class PETPInteractor():
    """
    PETPInteractor is in charge of binding events from view to presenter.
    """

    def __init__(self):
        self.v = None
        self.p = None
        logging.info("Init PETPInteractor")

    def install(self, presenter, view):
        self.p = presenter
        self.v = view

        # PETP Event binding
        PETPEvent.bind_to(self.v, PETPEvent.LOG, self.on_load_log)
        PETPEvent.bind_to(self.v, PETPEvent.DONE, self.on_handle_done)
        PETPEvent.bind_to(self.v, PETPEvent.START, self.on_handle_start)
        PETPEvent.bind_to(self.v, PETPEvent.OPEN_INPUT_DIALOG, self.on_handle_open_input_dialog)
        PETPEvent.bind_to(self.v, PETPEvent.HTTP_REQUEST, self.on_handle_http_request)
        PETPEvent.bind_to(self.v, PETPEvent.MATPLOTLIB, self.on_handle_display_in_matplotlib_view)
        PETPEvent.bind_to(self.v, PETPEvent.PIPELINE_STEP, self.on_handle_pipeline_step)
        PETPEvent.bind_to(self.v, PETPEvent.SYNC_TASK_INPUT, self.on_sync_task_input)

        # UI event binding
        self.v.Bind(wx.EVT_CLOSE, self.on_close_window)
        self.v.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.on_notebook_page_changed, self.v.notebook)

        # Execution relevant --------------------------------------------------
        self.bind_view_event_4e_loop_editor()
        self.bind_view_event_4e_task_editor()
        self.bind_view_event_4e_input_editor()
        self.bind_view_event_4e_execution_action_panel()

        # Pipeline relevant ---------------------------------------------------
        self.bind_view_event_4p_pipeline_editor()
        self.bind_view_event_4p_pipeline_action_panel()

        # Log console
        self.bind_view_event_4_log_panel()

        # Keyboard shortcuts
        self._bind_accelerators()

        logging.info('PETPInteractor installed')

    def _bind_accelerators(self):
        undo_id = wx.NewId()
        redo_id = wx.NewId()
        self.v.Bind(wx.EVT_MENU, self.on_undo, id=undo_id)
        self.v.Bind(wx.EVT_MENU, self.on_redo, id=redo_id)
        accel = wx.AcceleratorTable([
            (wx.ACCEL_CTRL, ord('Z'), undo_id),
            (wx.ACCEL_CTRL, ord('Y'), redo_id),
            (wx.ACCEL_CTRL | wx.ACCEL_SHIFT, ord('Z'), redo_id),
        ])
        self.v.SetAcceleratorTable(accel)

    def bind_view_event_4_log_panel(self):
        self.v.Bind(wx.EVT_COMBOBOX, self.on_lang_changed, self.v.langChooser)
        self.v.Bind(wx.EVT_COMBOBOX, self.on_theme_changed, self.v.themeChooser)

        self.v.logContents.Bind(wx.EVT_SET_FOCUS, self.on_logcontents_focused)
        self.v.logContents.Bind(wx.EVT_KILL_FOCUS, self.on_logcontents_unfocused)
        self.v.logContents.Bind(wx.EVT_KEY_DOWN, self.on_log_key_down)

        self.v.logSearchBar.Bind(EVT_LOG_BAR, self.on_log_bar_event)

    def bind_view_event_4p_pipeline_action_panel(self):
        self.v.Bind(wx.EVT_BUTTON, self.on_delete_pipeline, self.v.delPipeline)
        self.v.pipelineChooser.Bind(wx.EVT_LEFT_DOWN, self.on_pipeline_chooser_click)
        self.v.pipelineChooser.Bind(wx.EVT_KEY_DOWN, self.on_pipeline_chooser_key)
        self.v.Bind(wx.EVT_BUTTON, self.on_save_pipeline, self.v.savePipeline)
        self.v.Bind(wx.EVT_BUTTON, self.on_run_pipeline, self.v.runPipeline)
        self.v.Bind(wx.EVT_CHECKBOX, self.on_cron_actived, self.v.asCronChecbox)
        self.v.Bind(wx.EVT_TEXT, self.on_cron_changed, self.v.cronInput)
        self.v.Bind(wx.EVT_BUTTON, self.on_stop_all, self.v.stopAll)
        self.v.Bind(wx.EVT_BUTTON, self.on_stop_current, self.v.stopCurrentCron)
        self.v.Bind(wx.EVT_BUTTON, self.on_open_cron_dashboard, self.v.cronDashboardBtn)

    def bind_view_event_4p_pipeline_editor(self):
        self.v.Bind(wx.EVT_BUTTON, self.on_add_row4p, self.v.addRow4P)
        self.v.Bind(wx.EVT_BUTTON, self.on_delete_rows4p, self.v.delRow4P)
        self.v.executionGrid.Bind(wx.grid.EVT_GRID_CELL_CHANGED, self.on_grid_cell_change4p)

    def bind_view_event_4e_execution_action_panel(self):
        # Execution action panel
        self.v.Bind(wx.EVT_BUTTON, self.on_delete_execution, self.v.delExecution)
        self.v.Bind(wx.EVT_BUTTON, self.on_copy_execution, self.v.copyExecution)
        self.v.Bind(wx.EVT_BUTTON, self.on_add_execution, self.v.addExecution)
        self.v.executionChooser.Bind(wx.EVT_LEFT_DOWN, self.on_execution_chooser_click)
        self.v.executionChooser.Bind(wx.EVT_KEY_DOWN, self.on_execution_chooser_key)

        self.v.Bind(wx.EVT_BUTTON, self.on_save_execution, self.v.saveExection)
        self.v.Bind(wx.EVT_BUTTON, self.on_stop_execution, self.v.stopExection)
        self.v.Bind(wx.EVT_BUTTON, self.on_run_execution, self.v.runExecution)
        self.v.Bind(wx.EVT_BUTTON, self.on_open_snapshots, self.v.snapshots)
        self.v.Bind(wx.EVT_CHECKBOX, self.on_executeonstartup_changed, self.v.checkbox_executeonstartup)
        self.v.Bind(wx.EVT_CHECKBOX, self.on_only_tool_changed, self.v.only_tool)

    def bind_view_event_4e_input_editor(self):
        # input editor
        self.v.taskProperty.Bind(wx.propgrid.EVT_PG_CHANGED, self.on_property_change4e)
        self.v.taskProperty.Bind(wx.propgrid.EVT_PG_RIGHT_CLICK, self.on_property_right_click4e)
        self.v.taskProperty.Bind(wx.propgrid.EVT_PG_SELECTED, self.on_task_property_selected4e)
        self.v.taskProperty.GetGrid().Bind(wx.EVT_KEY_DOWN, self.on_task_property_key_down)

        self.v.Bind(wx.EVT_CHECKBOX, self.on_cb_astool_changed, self.v.cb_astool)

        self.v.datepicker.Bind(wx.adv.EVT_DATE_CHANGED, self.on_datepicker_changed)
        self.v.Bind(wx.EVT_BUTTON, self.on_delete_property, self.v.delProperty)
        self.v.Bind(wx.EVT_BUTTON, self.on_add_property, self.v.addProperty)
        self.v.Bind(wx.EVT_CHECKBOX, self.on_skip_task_changed, self.v.cb_skipped)


    def bind_view_event_4e_task_editor(self):
        # task editor - top action panel
        self.v.Bind(wx.EVT_BUTTON, self.on_add_row4e, self.v.addRow4E)
        self.v.Bind(wx.EVT_BUTTON, self.on_delete_rows4e, self.v.delRow4E)
        self.v.Bind(wx.EVT_BUTTON, self.on_select_recording, self.v.selectRecording)
        self.v.Bind(wx.EVT_BUTTON, self.on_load_from_recording, self.v.loadRecording)
        # task editor - grid mouse selection/click
        self.v.taskGrid.Bind(wx.grid.EVT_GRID_EDITOR_SHOWN, self.on_grid_cell_editor_shown4e)
        self.v.taskGrid.Bind(wx.grid.EVT_GRID_CELL_CHANGED, self.on_grid_cell_change4e)
        self.v.taskGrid.Bind(wx.grid.EVT_GRID_SELECT_CELL, self.on_grid_cell_select4e)
        self.v.taskGrid.Bind(wx.grid.EVT_GRID_CELL_RIGHT_CLICK, self.on_grid_cell_right_click)
        self.v.taskGrid.Bind(wx.grid.EVT_GRID_LABEL_RIGHT_CLICK, self.on_grid_empty_right_click)
        self.v.taskGrid.Bind(wx.grid.EVT_GRID_CELL_LEFT_DCLICK, self.on_task_grid_dclick)
        self.v.taskGrid.GetGridWindow().Bind(wx.EVT_KEY_DOWN, self.on_task_grid_key_down)
        self.v.taskGrid.Bind(wx.EVT_SIZE, self.on_task_grid_size)

    def bind_view_event_4e_loop_editor(self):
        self.v.Bind(wx.EVT_BUTTON, self.on_add_loop, self.v.addLoop)
        self.v.Bind(wx.EVT_BUTTON, self.on_del_loop, self.v.delLoop)
        self.v.Bind(wx.EVT_BUTTON, self.on_edit_loop, self.v.editLoop)
        self.v.loopProperty.Bind(wx.propgrid.EVT_PG_CHANGING, self.on_loop_property_changing4e)
        self.v.loopProperty.Bind(wx.propgrid.EVT_PG_CHANGED, self.on_loop_property_change4e)
        self.v.loopProperty.Bind(wx.propgrid.EVT_PG_RIGHT_CLICK, self.on_loop_property_right_click4e)
        self.v.loopProperty.Bind(wx.propgrid.EVT_PG_SELECTED, self.on_loop_property_selected4e)

    def on_handle_display_in_matplotlib_view(self, evt: PETPEvent):
        self.p.on_handle_display_in_matplotlib_view(evt)

    def on_handle_open_input_dialog(self, evt: PETPEvent):
        self.p.on_handle_open_input_dialog(evt)

    def on_handle_http_request(self, evt: PETPEvent):
        self.p.on_handle_http_request(evt)

    def on_handle_start(self, evt: PETPEvent):
        logging.info(f"{evt.data[0]} is START via new thread")
        self.p.update_highlight_info_start(evt.data[0])

    def on_handle_pipeline_step(self, evt: PETPEvent):
        action = evt.data[0]
        if action == 'start':
            pipeline_name = evt.data[1]
            self.p.update_highlight_info_pipeline_start(pipeline_name)
        elif action == 'step':
            _, pipeline_name, execution_name, row_idx = evt.data
            self.p._welcome_paused = True
            self.p._set_highlight_info(f"[PIPELINE] {pipeline_name} → {execution_name}")
            self.p.select_pipeline_execution_row(row_idx)
        elif action == 'done':
            pipeline_name = evt.data[1]
            self.p.update_highlight_info_pipeline_done(pipeline_name)

    def on_sync_task_input(self, evt: PETPEvent):
        self.p.on_sync_task_input(evt)

    def on_handle_done(self, evt: PETPEvent):
        execution = evt.data[0]
        error = evt.data[2] if len(evt.data) > 2 else None
        logging.info(f"{execution} is DONE.")
        self.p.clear_running_task_highlight()
        self.p.update_highlight_info_done(execution, error)

        data_chain = evt.data[1]
        from httpservice.handlers.HttpRequestHandler import HttpRequestHandler

        request_id_key = HttpRequestHandler.get_request_id_key()
        response_key = HttpRequestHandler.get_response_key()

        if request_id_key not in data_chain:
            return

        current_request_id = data_chain[request_id_key]
        server = HttpRequestHandler.get_server()
        if not current_request_id or not server:
            return

        if response_key in data_chain:
            server.store_result(current_request_id, data_chain[data_chain[response_key]])
        else:
            output_schema = self._get_output_schema_for(execution)
            if output_schema:
                from httpservice.HttpServer import HttpServer
                shaped = HttpServer._build_output_from_schema(data_chain, output_schema)
                server.store_result(current_request_id, shaped)

    def _get_output_schema_for(self, execution_name: str):
        tools = self.p.get_tools()
        raw = tools.get(execution_name)
        if not raw:
            return None
        from httpservice.HttpServer import HttpServer
        parsed = HttpServer._parse_tool_value(raw)
        schema = parsed.get("outputSchema")
        if isinstance(schema, dict) and schema.get("properties"):
            return schema
        return None

    def on_load_log(self, evt):
        """Called by internal PETPEvent.LOG — highlight running task."""
        evt.Skip()
        self.p.highlight_running_task(evt.data)
        self.p.on_logcontents_unfocused()

    def on_grid_cell_right_click(self, evt):
        evt.Skip()
        self.p.on_grid_cell_right_click(evt)

    def on_grid_empty_right_click(self, evt):
        evt.Skip()
        self.p.on_grid_empty_right_click(evt)

    def on_notebook_page_changed(self, evt):
        self.p.on_notebook_page_changed(evt)

    def on_load_from_recording(self, evt):
        evt.Skip()
        self.p.on_load_from_recording()

    def on_add_loop(self, evt):
        evt.Skip()
        self.p.on_add_loop()

    def on_del_loop(self, evt):
        evt.Skip()
        self.p.on_del_loop()

    def on_edit_loop(self, evt):
        evt.Skip()
        self.p.on_edit_loop()

    def on_loop_property_changing4e(self, evt):
        evt.Skip()
        self.p.on_loop_property_changing4e(evt)

    def on_loop_property_change4e(self, evt):
        self.p.on_loop_property_change4e(evt)

    def on_loop_property_right_click4e(self, evt):
        self.p.on_loop_property_right_click4e(evt)

    def on_loop_property_selected4e(self, evt):
        evt.Skip()
        self.p.on_loop_property_selected4e(evt)

    def on_add_row4e(self, evt):
        evt.Skip()
        self.p.on_add_row4e()

    def on_delete_rows4e(self, evt):
        evt.Skip()
        self.p.on_delete_rows4e()

    def on_select_recording(self, evt):
        evt.Skip()
        self.p.on_select_recording()

    def on_add_row4p(self, evt):
        evt.Skip()
        self.p.on_add_row4p()

    def on_delete_rows4p(self, evt):
        evt.Skip()
        self.p.on_delete_rows4p()

    def on_task_execution_changed(self, evt):
        evt.Skip()
        self.p.on_task_execution_changed()

    def on_execution_chooser_click(self, evt):
        wx.CallAfter(self.p._show_execution_palette)

    def on_execution_chooser_key(self, evt):
        code = evt.GetKeyCode()
        if code in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER, wx.WXK_F2, wx.WXK_SPACE):
            wx.CallAfter(self.p._show_execution_palette)
        else:
            evt.Skip()

    def on_execution_pipeline_changed(self, evt):
        evt.Skip()
        self.p.on_execution_pipeline_changed()

    def on_pipeline_chooser_click(self, evt):
        wx.CallAfter(self.p._show_pipeline_palette)

    def on_pipeline_chooser_key(self, evt):
        code = evt.GetKeyCode()
        if code in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER, wx.WXK_F2, wx.WXK_SPACE):
            wx.CallAfter(self.p._show_pipeline_palette)
        else:
            evt.Skip()

    def on_lang_changed(self, evt):
        evt.Skip()
        self.p.on_lang_changed()

    def on_theme_changed(self, evt):
        evt.Skip()
        self.p.on_theme_changed()

    def on_save_execution(self, evt):
        evt.Skip()
        self.p.on_save_execution()

    def on_delete_execution(self, evt):
        evt.Skip()
        self.p.on_delete_execution()

    def on_copy_execution(self, evt):
        evt.Skip()
        self.p.on_copy_execution()

    def on_add_execution(self, evt):
        evt.Skip()
        self.p.on_add_execution()

    def on_run_execution(self, evt):
        evt.Skip()
        self.p.on_run_execution()

    def on_executeonstartup_changed(self, evt):
        evt.Skip()
        self.p.on_executeonstartup_changed(evt)

    def on_only_tool_changed(self, evt):
        evt.Skip()
        self.p.on_only_tool_changed(evt)

    def on_stop_execution(self, evt):
        evt.Skip()
        self.p.on_stop_execution()

    def on_open_snapshots(self, evt):
        evt.Skip()
        self.p._on_open_snapshots(evt)

    def on_save_pipeline(self, evt):
        evt.Skip()
        self.p.on_save_pipeline()

    def on_delete_pipeline(self, evt):
        evt.Skip()
        self.p.on_delete_pipeline()

    def on_run_pipeline(self, evt):
        evt.Skip()
        self.p.on_run_pipeline()

    def on_stop_all(self, evt):
        evt.Skip()
        self.p.on_stop_all()

    def on_stop_current(self, evt):
        evt.Skip()
        self.p.on_stop_current()

    def on_grid_cell_change4e(self, evt):
        self.p.on_grid_cell_change4e(evt)

    def on_grid_cell_editor_shown4e(self, evt):
        self.p.on_grid_cell_editor_shown4e(evt)

    def on_grid_cell_select4e(self, evt):
        self.p.on_grid_cell_select4e(evt)

    def on_grid_cell_change4p(self, evt):
        self.p.on_grid_cell_change4p(evt)

    def on_property_change4e(self, evt):
        self.p.on_property_change4e(evt)

    def on_property_right_click4e(self, evt):
        self.p.on_property_right_click4e(evt)

    def on_task_property_selected4e(self, evt):
        self.p.on_task_property_selected4e(evt)

    def on_task_property_key_down(self, evt):
        if evt.ShiftDown():
            if evt.GetKeyCode() == wx.WXK_UP:
                self.p._move_pgrid_property(-1)
                return
            if evt.GetKeyCode() == wx.WXK_DOWN:
                self.p._move_pgrid_property(1)
                return
        evt.Skip()

    def on_task_grid_dclick(self, evt):
        if evt.GetCol() == 0:
            self.p._show_processor_palette(evt.GetRow())
        elif evt.GetCol() == 1:
            self.p._on_view_processor_usage(evt.GetRow())
        else:
            evt.Skip()

    def on_task_grid_key_down(self, evt):
        if evt.ControlDown():
            if evt.GetKeyCode() == ord('C'):
                self.p.on_task_grid_copy()
                return
            if evt.GetKeyCode() == ord('V'):
                self.p.on_task_grid_paste()
                return
        code = evt.GetKeyCode()
        if code in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER, wx.WXK_F2):
            grid = self.v.taskGrid
            if grid.GetGridCursorCol() == 0:
                self.p._show_processor_palette(grid.GetGridCursorRow())
                return
        evt.Skip()

    def on_task_grid_size(self, evt):
        evt.Skip()
        wx.CallAfter(self.p._autosize_input_col)

    def on_cron_actived(self, evt):
        self.p.on_cron_actived(evt)

    def on_cron_changed(self, evt):
        evt.Skip()
        self.p.on_cron_changed()

    def on_undo(self, evt):
        self.p._undo()

    def on_redo(self, evt):
        self.p._redo()

    def on_cb_astool_changed(self, evt):
        evt.Skip()
        self.p.on_cb_astool_changed(evt)

    def on_datepicker_changed(self, evt):
        self.p.on_datepicker_changed(evt)

    def on_add_property(self, evt):
        evt.Skip()
        self.p.on_add_property()

    def on_skip_task_changed(self, evt):
        evt.Skip()
        self.p.on_skip_task_changed(evt)

    def on_delete_property(self, evt):
        evt.Skip()
        self.p.on_delete_property()

    def on_open_cron_dashboard(self, evt):
        evt.Skip()
        self.p.on_open_cron_dashboard()

    def on_logcontents_focused(self, evt):
        evt.Skip()
        self.p.on_logcontents_focused()

    def on_logcontents_unfocused(self, evt):
        evt.Skip()
        self.p.on_logcontents_unfocused()

    def on_log_bar_event(self, evt):
        action = evt.GetAction()
        if action == "search":
            self.p.on_search_log()
        elif action == "prev":
            self.p.on_prev_log_match()
        elif action == "next":
            self.p.on_next_log_match()
        elif action == "filter":
            self.p.on_filter_toggle(bool(evt.GetInt()))
        elif action == "key_escape":
            self.v.logSearchBar.set_search_text('')
            self.p.on_clear_log_search()
            self.v.logContents.SetFocus()
        elif action == "level_changed":
            self.p.on_log_level_changed()
        elif action == "clean":
            self.p.on_clean_log()

    def on_log_key_down(self, evt):
        if evt.GetKeyCode() == ord('F') and evt.CmdDown():
            self.v.logSearchBar.focus_search()
        else:
            evt.Skip()

    def on_close_window(self, evt):
        if self.p.on_close_window(evt):
            evt.Skip()
        else:
            evt.Veto()
