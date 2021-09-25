import asyncio
import logging
import wx
import wx.dataview
import wx.lib.colourutils


class PETPInteractor():

    def __init__(self):
        logging.info("Init PETPInteractor")

    def install(self, presenter, view):
        self.p = presenter
        self.v = view

        self.v.Bind(wx.EVT_CLOSE, self.on_close_window)

        self.v.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.on_notebook_page_changed, self.v.notebook)
        # Execution relevant

        self.v.Bind(wx.EVT_BUTTON, self.on_add_loop, self.v.addLoop)
        self.v.Bind(wx.EVT_BUTTON, self.on_del_loop, self.v.delLoop)
        self.v.Bind(wx.EVT_BUTTON, self.on_convert_get_deep_data_4loop, self.v.convertGetDeepData4Loop)
        self.v.Bind(wx.EVT_BUTTON, self.on_convert_get_data_4loop, self.v.convertGetData4Loop)

        self.v.Bind(wx.EVT_BUTTON, self.on_add_row4e, self.v.addRow4E)
        self.v.Bind(wx.EVT_BUTTON, self.on_delete_rows4e, self.v.delRow4E)

        self.v.Bind(wx.EVT_BUTTON, self.on_select_recording, self.v.selectRecording)
        self.v.Bind(wx.EVT_BUTTON, self.on_load_from_recording, self.v.loadRecording)
        self.v.Bind(wx.EVT_COMBOBOX, self.on_recording_test_changed, self.v.testChooser)

        self.v.taskGrid.Bind(wx.grid.EVT_GRID_EDITOR_SHOWN, self.on_grid_cell_editor_shown4e)
        self.v.taskGrid.Bind(wx.grid.EVT_GRID_CELL_CHANGED, self.on_grid_cell_change4e)
        self.v.taskGrid.Bind(wx.grid.EVT_GRID_SELECT_CELL, self.on_grid_cell_select4e)
        self.v.taskGrid.Bind(wx.grid.EVT_GRID_CELL_RIGHT_CLICK, self.on_grid_cell_right_click)

        self.v.taskProperty.Bind(wx.propgrid.EVT_PG_CHANGED, self.on_property_change4e)
        self.v.Bind(wx.EVT_BUTTON, self.on_convert_ddir, self.v.convertDDir)
        self.v.Bind(wx.EVT_BUTTON, self.on_convert_pwd, self.v.convertPWD)
        self.v.Bind(wx.EVT_BUTTON, self.on_convert_get_data, self.v.convertGetData)
        self.v.Bind(wx.EVT_BUTTON, self.on_convert_get_deep_data, self.v.convertGetDeepData)

        self.v.datepicker.Bind(wx.adv.EVT_DATE_CHANGED, self.on_datepicker_changed)
        self.v.Bind(wx.EVT_BUTTON, self.on_delete_property, self.v.delProperty)
        self.v.Bind(wx.EVT_BUTTON, self.on_add_property, self.v.addProperty)

        self.v.Bind(wx.EVT_BUTTON, self.on_delete_execution, self.v.delExection)
        self.v.Bind(wx.EVT_COMBOBOX, self.on_task_execution_changed, self.v.executionChooser)
        self.v.Bind(wx.EVT_BUTTON, self.on_save_execution, self.v.saveExection)
        self.v.Bind(wx.EVT_BUTTON, self.on_run_execution, self.v.runExection)

        # Pipeline relevant
        self.v.Bind(wx.EVT_BUTTON, self.on_add_row4p, self.v.addRow4P)
        self.v.Bind(wx.EVT_BUTTON, self.on_delete_rows4p, self.v.delRow4P)

        self.v.executionGrid.Bind(wx.grid.EVT_GRID_CELL_CHANGED, self.on_grid_cell_change4p)

        self.v.Bind(wx.EVT_BUTTON, self.on_delete_pipeline, self.v.delPipeline)
        self.v.Bind(wx.EVT_COMBOBOX, self.on_execution_pipeline_changed, self.v.pipelineChooser)
        self.v.Bind(wx.EVT_BUTTON, self.on_save_pipeline, self.v.savePipeline)
        self.v.Bind(wx.EVT_BUTTON, self.on_run_pipeline, self.v.runPipeline)
        self.v.Bind(wx.EVT_CHECKBOX, self.on_cron_actived, self.v.asCronChecbox)
        self.v.Bind(wx.EVT_TEXT, self.on_cron_changed, self.v.cronInput)

        self.v.Bind(wx.EVT_BUTTON, self.on_stop_all, self.v.stopAll)
        self.v.Bind(wx.EVT_BUTTON, self.on_stop_current, self.v.stopCurrentCron)

        # Log
        self.v.Bind(wx.EVT_BUTTON, self.on_load_log, self.v.reloadLog)
        self.v.Bind(wx.EVT_BUTTON, self.on_clean_log, self.v.cleanLog)

        self.v.logContents.Bind(wx.EVT_SET_FOCUS, self.on_logcontents_focused)
        self.v.logContents.Bind(wx.EVT_KILL_FOCUS, self.on_logcontents_unfocused)
        logging.info('PETPInteractor installed')

    def on_grid_cell_right_click(self, evt):
        evt.Skip()
        self.p.on_grid_cell_right_click(evt)

    def on_notebook_page_changed(self, evt):
        self.p.on_notebook_page_changed(evt)

    def on_load_from_recording(self, evt):
        evt.Skip()
        self.p.on_load_from_recording()

    def on_recording_test_changed(self, evt):
        evt.Skip()
        self.p.on_recording_test_changed()

    def on_add_loop(self, evt):
        evt.Skip()
        self.p.on_add_loop()

    def on_del_loop(self, evt):
        evt.Skip()
        self.p.on_del_loop()

    def on_convert_get_data_4loop(self, evt):
        evt.Skip()
        self.p.on_convert_get_data_4loop()

    def on_convert_get_deep_data_4loop(self, evt):
        evt.Skip()
        self.p.on_convert_get_deep_data_4loop()

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

    def on_execution_pipeline_changed(self, evt):
        evt.Skip()
        self.p.on_execution_pipeline_changed()

    def on_save_execution(self, evt):
        evt.Skip()
        self.p.on_save_execution()

    def on_delete_execution(self, evt):
        evt.Skip()
        self.p.on_delete_execution()

    def on_run_execution(self, evt):
        evt.Skip()
        self.p.on_run_execution()

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

    def on_cron_actived(self, evt):
        self.p.on_cron_actived(evt)

    def on_cron_changed(self, evt):
        evt.Skip()
        self.p.on_cron_changed()

    def on_convert_ddir(self, evt):
        evt.Skip()
        self.p.on_convert_ddir()

    def on_convert_pwd(self, evt):
        evt.Skip()
        self.p.on_convert_pwd()

    def on_convert_get_data(self, evt):
        evt.Skip()
        self.p.on_convert_get_data()

    def on_convert_get_deep_data(self, evt):
        evt.Skip()
        self.p.on_convert_get_deep_data()

    def on_datepicker_changed(self, evt):
        self.p.on_datepicker_changed(evt)

    def on_add_property(self, evt):
        evt.Skip()
        self.p.on_add_property()

    def on_delete_property(self, evt):
        evt.Skip()
        self.p.on_delete_property()

    def on_load_log(self, evt):
        evt.Skip()
        self.p.on_logcontents_unfocused()
        asyncio.run(
            self.p.on_load_log_async()
        )

    def on_clean_log(self, evt):
        evt.Skip()
        self.p.on_clean_log()

    def on_logcontents_focused(self, evt):
        evt.Skip()
        self.p.on_logcontents_focused()

    def on_logcontents_unfocused(self, evt):
        evt.Skip()
        self.p.on_logcontents_unfocused()

    def on_close_window(self, evt):
        evt.Skip()
        self.p.on_close_window()
