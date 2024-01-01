import json
import logging
from threading import Thread

import wx
import wx.dataview
import wx.lib.colourutils
from cron_descriptor import ExpressionDescriptor

from core.cron.cron import Cron
from core.definition.SeleniumIDERecordingConverter import SeleniumIDERecordingConverter
from core.execution import Execution
from core.executor import Executor
from core.loop import Loop
from core.pipeline import Pipeline
from core.processor import Processor
from core.task import Task
from decorators.decorators import reload_log_after
from mvp.model.PETPModel import PETPModel
from mvp.presenter.PETPInteractor import PETPInteractor
from mvp.presenter.event.PETPEvent import PETPEvent
from mvp.view.PETPView import PETPView
from utils.DateUtil import DateUtil
from utils.OSUtils import OSUtils


class PETPPresenter():
    CRON_INVALID: str = "Invalid CRON"
    cron: Cron
    execution: Execution
    executors: list = []
    pipeline: Pipeline
    converter: SeleniumIDERecordingConverter

    available_processors: list = []
    available_executions: list = []

    cellChoiceEditorInEditting4E = None
    cellChoiceEditorInEditting4P = None

    currentSelectedRow: int = -1
    isLogContentFocused: bool = False
    single_page: str = "petp"
    logger_thread = None
    keep_running = True

    def __init__(self, model: PETPModel, view: PETPView, interactor: PETPInteractor):

        self.m = model
        self.v = view
        self.i = interactor
        self.i.install(self, view)

        logging.info('Init PETPPresenter')

        self._load_available_executions()
        self._load_available_pipelines()

        self._init_taskgrid_choice_editor()
        self._init_executiongrid_choice_editor()
        self._init_cron()
        self._init_property_grid()

        self._load_config()

        self._handle_execute_on_startup()

    def _handle_execute_on_startup(self):
        if self.m.execute_on_startup:
            logging.info(f"execute on startup is enabled, will run execution: {self.m.last_run}")
            self.on_run_execution()

    def _load_config(self):
        # load_executeonstartup
        if self.m.execute_on_startup is not None:
            self.v.checkbox_executeonstartup.SetValue(self.m.execute_on_startup)

        # load_log_level
        if self.m.log_level is not None:
            self.v.logLevelChooser.SetValue(self.m.log_level)

        # load_last_run
        if self.m.last_run is not None:
            logging.info("loading last run: " + self.m.last_run)
            self.v.executionChooser.SetValue(self.m.last_run)
            self.on_task_execution_changed()

    def _init_property_grid(self):
        self.v.taskProperty.AddPage(self.single_page)
        self._append_property_category(self.v.taskProperty, "Input Editor")

        self.v.loopProperty.AddPage(self.single_page)
        self._append_property_category(self.v.loopProperty, "Loop Editor")

    def _append_property_category(self, propgrid_manager, category_name):
        page = propgrid_manager.GetPage(self.single_page)
        page.Append(wx.propgrid.PropertyCategory(category_name))

    def _reset_task_pgrid(self, task_number=0):
        self.v.taskProperty.ClearPage(self.v.taskProperty.GetPageByName(self.single_page))
        self._append_property_category(self.v.taskProperty,
                                       "Input Editor of T" + str(
                                           task_number) if task_number > 0 else "Input Editor")

    def _reset_loop_pgrid(self):
        self.v.loopProperty.ClearPage(self.v.loopProperty.GetPageByName(self.single_page))
        self._append_property_category(self.v.loopProperty, "Loop Editor")

    def on_grid_cell_right_click(self, evt):
        evt.Skip()

        self.selected_row_2_copied_paste = evt.Row

        if not hasattr(self, "popup_id_copy"):
            self.popup_id_copy = wx.NewId()
            self.popup_id_paste = wx.NewId()

        menu = wx.Menu()

        item_copy = wx.MenuItem(menu, self.popup_id_copy, "Copy")
        self.v.Bind(wx.EVT_MENU, self._on_grid_row_copy, item_copy)

        item_paste = wx.MenuItem(menu, self.popup_id_paste, "Paste")
        self.v.Bind(wx.EVT_MENU, self._on_grid_row_paste, item_paste)

        menu.Append(item_copy)
        menu.Append(item_paste)

        self.v.PopupMenu(menu)

        menu.Destroy()

    @reload_log_after
    def _on_grid_row_copy(self, evt):
        self.row_copied = [
            self.v.taskGrid.GetCellValue(self.selected_row_2_copied_paste, 0),
            self.v.taskGrid.GetCellValue(self.selected_row_2_copied_paste, 1)
        ]
        logging.debug("selected_row_copied" + str(self.row_copied))

    def _on_grid_row_paste(self, evt):
        self.v.taskGrid.SetCellValue(self.selected_row_2_copied_paste, 0, self.row_copied[0])
        self.v.taskGrid.SetCellValue(self.selected_row_2_copied_paste, 1, self.row_copied[1])

    def _init_cron(self):
        self.cron = Cron(self.v)

    def _load_available_executions(self):
        self.v.executionChooser.AppendItems(Execution.get_available_executions())

    def _load_available_pipelines(self):
        self.v.pipelineChooser.AppendItems(Pipeline.get_available_pipelines())

    def _init_executiongrid_choice_editor(self):
        self.available_executions = Execution.get_available_executions()
        executionGrid = self.v.executionGrid
        for row in range(executionGrid.GetNumberRows()):
            self._bind_grid_cell_choice_editor(row, executionGrid, self.available_executions)

    def _init_taskgrid_choice_editor(self):
        self.available_processors = Processor.get_processors()
        taskGrid = self.v.taskGrid
        for row in range(taskGrid.GetNumberRows()):
            self._bind_grid_cell_choice_editor(row, taskGrid, self.available_processors)

    def on_add_loop(self):
        loop_code = 'loop-' + DateUtil.get_now_in_str()
        loop_tpl = Loop.tpl()
        page = self.v.loopProperty.GetPage(self.single_page)
        self._append_or_update_property_to_page(loop_code, loop_tpl, page)
        page.FitColumns()

    def on_del_loop(self):
        page = self.v.loopProperty.GetPage(self.single_page)
        self._delete_selected_property_from_page(page)

    def on_convert_get_deep_data_4loop(self):
        """ NOT IMPLEMENTED YET """
        pass

    def on_convert_get_data_4loop(self):
        """ NOT IMPLEMENTED YET """
        pass

    def on_close_window(self):
        self.logger_thread = None
        self.keep_running = False
        self.v.tbicon.Destroy()

    def on_notebook_page_changed(self, evt):
        # switch notebook tab from execution to pipeline
        if evt.Selection == 1:
            self._init_executiongrid_choice_editor()

    @reload_log_after
    def on_log_level_changed(self):
        combo = self.v.logLevelChooser
        logLevel = combo.GetValue()

        # record log_level
        if self.m.log_level != combo.GetValue():
            self.m.log_level = combo.GetValue()
            self.m.set_config('log_level', self.m.log_level)

        logging.getLogger().setLevel(logging.getLevelName(logLevel))
        getattr(logging, logLevel.lower())('Set log level to <' + logLevel + '> successfully.')

    @reload_log_after
    def on_execution_pipeline_changed(self):
        combo = self.v.pipelineChooser
        grid = self.v.executionGrid
        grid.ClearGrid()

        self.pipeline = Pipeline.get_pipeline(combo.GetValue())
        if self.pipeline is None:
            return
        else:
            currentNumberRows = grid.GetNumberRows()
            executionNumber = len(self.pipeline.list)

            self.v.asCronChecbox.SetValue(self.pipeline.cronEnabled)
            self.v.cronInput.SetValue(self.pipeline.cronExp)
            self._update_cron_setting(self.pipeline.cronEnabled)

            if executionNumber > currentNumberRows:
                for _ in range(executionNumber - currentNumberRows):
                    self._insert_row(grid, self.available_executions)

            for idx, itm in enumerate(self.pipeline.list):
                grid.SetCellValue(idx, 0, itm['execution'])
                if 'input' in itm:
                    grid.SetCellValue(idx, 1, itm['input'])

    def _reset_property_grid(self):
        self._reset_task_pgrid()
        self.v.avaibleProperties.Clear()

    @reload_log_after
    def on_task_execution_changed(self):
        self._reset_property_grid()
        combo = self.v.executionChooser
        grid = self.v.taskGrid
        grid.ClearGrid()
        self.execution = Execution.get_execution(combo.GetValue())
        if self.execution is None:
            return
        else:
            currentNumberRows = grid.GetNumberRows()
            taskNumber = len(self.execution.list)

            if taskNumber > currentNumberRows:
                for _ in range(taskNumber - currentNumberRows):
                    self._insert_row(grid, self.available_processors)

            for idx, itm in enumerate(self.execution.list):
                grid.SetCellValue(idx, 0, itm.type)
                if (hasattr(itm, 'input')):
                    grid.SetCellValue(idx, 1, itm.input)

            self._reset_loop_pgrid()
            if not hasattr(self.execution, 'loops'):
                return

            if len(self.execution.loops) > 0:
                for idx, itm in enumerate(self.execution.loops):
                    self._append_or_update_property_to_page(
                        itm.loop_code,
                        itm.loop_attributes,
                        self.v.loopProperty.GetPage(self.single_page)
                    )

    def _save_execcution(self, name):
        grid = self.v.taskGrid
        loopProperty = self.v.loopProperty

        # prepare tasks
        tasks = []
        for row in range(0, grid.GetNumberRows()):
            t_type = grid.GetCellValue(row, 0)
            t_input = grid.GetCellValue(row, 1)
            if len(t_type) == 0 and len(t_input) == 0:
                break
            logging.info(f'{t_type} -> {t_input}')
            tasks.append(Task(t_type, t_input))

        # prepare loops
        loops = []
        itr = loopProperty.GetPage(self.single_page).GetPyIterator(wx.propgrid.PG_ITERATE_ALL)

        for prop in itr:
            if isinstance(prop, wx.propgrid.PropertyCategory):
                continue

            loops.append(Loop(prop.GetName(), prop.GetValue()))

        if len(tasks) > 0:
            Execution(name, tasks, loops).save()

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
            if self.v.asCronChecbox.IsChecked():
                if not self.CRON_INVALID == self.v.lableCronExplain.GetLabel():
                    Pipeline(name, list, self.v.asCronChecbox.IsChecked(), self.v.cronInput.GetValue()).save()
                else:
                    logging.warning('CRON is invalid, cron can not be saved')
            else:
                Pipeline(name, list).save()
        else:
            logging.warning('Execution list should NOT be empty')

    @reload_log_after
    def on_save_pipeline(self):
        combo = self.v.pipelineChooser
        name = combo.GetValue()

        if (len(name) == 0):
            logging.info(f'Pipeline: cron name should not be empty')
            return

        if combo.FindString(name) == -1:
            combo.Insert(name, 0)
        else:
            logging.warning(f'Pipeline: {combo.GetValue()} already existed, overwrite!')

        self._save_pipeline(name)

    @reload_log_after
    def on_save_execution(self):
        combo = self.v.executionChooser
        name = combo.GetValue()

        if combo.FindString(name) == -1:
            combo.Insert(name, 0)
        else:
            logging.warning(f'Execution: {combo.GetValue()} already existed, overrwrite!')

        self._save_execcution(name)

    @reload_log_after
    def on_delete_pipeline(self):
        combo = self.v.pipelineChooser
        found = combo.FindString(combo.GetValue())

        if not found == -1:
            self.pipeline.delete()
            combo.Delete(found)

    @reload_log_after
    def on_delete_execution(self):
        combo = self.v.executionChooser
        found = combo.FindString(combo.GetValue())

        if not found == -1:
            self.execution.delete()
            combo.Delete(found)
            combo.SetValue('')

    @reload_log_after
    def on_stop_all(self):
        self.cron.stop_all()

    @reload_log_after
    def on_stop_current(self):
        if not self.pipeline is None:
            self.cron.stop_one(self.pipeline)

    @reload_log_after
    def on_run_pipeline(self):
        combo = self.v.pipelineChooser
        self.pipeline = Pipeline.get_pipeline(combo.GetValue())
        if self.v.asCronChecbox.IsChecked() and not self.CRON_INVALID == self.v.cronInput.GetValue():
            self.cron.add_one(self.pipeline)
        else:
            Thread(target=self.pipeline.run, args=({"__m": self.m, "__p": self}, self.v), daemon=True).start()

    @reload_log_after
    def on_run_execution(self):
        combo = self.v.executionChooser
        self.execution = Execution.get_execution(combo.GetValue())

        # record last_run
        if self.m.last_run != combo.GetValue():
            self.m.last_run = combo.GetValue()
            self.m.set_config('last_run', self.m.last_run)

        executor = Executor(self.execution, {"__m": self.m, "__p": self}, self.v)
        self.executors.append(executor)
        executor.start()

    @reload_log_after
    def on_executeonstartup_changed(self, evt: wx.EVT_CHECKBOX):
        self.m.execute_on_startup = evt.IsChecked()
        self.m.set_config('execute_on_startup', self.m.execute_on_startup)

    @reload_log_after
    def on_stop_execution(self):
        for executor in self.executors:
            if executor.is_alive():
                executor.execution.should_be_stop = True
                logging.info(f'Execution: [ {executor.execution.execution} ] is manually stopping.')

        self.executors = []

    @reload_log_after
    def on_select_recording(self):
        with wx.FileDialog(self.v, "Open Selenium IDE recording file", wildcard="recording files (*.side)|*.side",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return

            pathname = fileDialog.GetPath()
            self.v.recordingLocation.SetLabel(pathname)
            self.converter = SeleniumIDERecordingConverter(pathname)
            available_tests = self.converter.get_test_names()

            if len(available_tests) > 0:
                self.v.testChooser.Clear()
                self.v.testChooser.AppendItems(available_tests)

    @reload_log_after
    def on_recording_test_changed(self):
        self.converter.set_test_name(self.v.testChooser.GetValue())
        logging.info('load test: ' + self.v.testChooser.GetValue())

    @reload_log_after
    def on_load_from_recording(self):
        if hasattr(self, 'converter') and self.converter.is_initialized():
            tasks = self.converter.convert_from_selenium_ide_recording()

            taskGrid = self.v.taskGrid
            selectedRows = taskGrid.GetSelectedRows()
            tasks = tasks if len(selectedRows) > 0 else reversed(tasks)

            for t in tasks:
                selectedRows = taskGrid.GetSelectedRows()
                insertAt = selectedRows[0] if len(selectedRows) > 0 else 0
                self._insert_row(taskGrid, self.available_processors)
                taskGrid.SetCellValue(insertAt, 0, t.type)
                if (hasattr(t, 'input')):
                    taskGrid.SetCellValue(insertAt, 1, t.input)

            logging.info(
                f'Successfully convert from Selenium IDE recording: {self.converter.file_path}, {self.converter.test_name}')
        else:
            logging.warning(
                'Recording location and test name should not be empty, also able to select the row where start to load.')

    def _bind_grid_cell_choice_editor(self, rowAt, grid, choices):
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
        current_row = evt.GetRow()
        current_column = evt.GetCol()
        evt.Skip()

    @reload_log_after
    def on_grid_cell_change4e(self, evt):
        grid = self.v.taskGrid
        current_value = grid.GetCellValue(evt.GetRow(), evt.GetCol())
        current_row = evt.GetRow()
        current_column = evt.GetCol()
        evt.Skip()

        if current_column == 0:
            if len(current_value) <= 0 or not current_value in self.available_processors:
                return
            p = Processor.get_processor_by_type(current_value)

            grid.SetCellValue(current_row, 1, p.get_tpl())

            logging.info(f'Processor {current_value} : {p.get_desc()}')
            self._load_input_taskproperty(current_row)

    @reload_log_after
    def on_grid_cell_select4e(self, evt):
        current_row = evt.GetRow()
        evt.Skip()
        self._load_input_taskproperty(current_row)

    def _load_input_taskproperty(self, current_row):
        grid = self.v.taskGrid
        self.currentSelectedRow = current_row
        current_input = grid.GetCellValue(current_row, 1)
        if len(current_input) > 5:

            inputDict = json.loads(current_input)
            page = self.v.taskProperty.GetPage(self.single_page)
            self._reset_task_pgrid(current_row + 1)

            for k in inputDict:
                v = inputDict[k]
                self._append_or_update_property_to_page(k, v, page)

            page.FitColumns()

            current_processor = grid.GetCellValue(current_row, 0)
            self._fill_available_properties(current_processor, inputDict)
        else:
            self._reset_task_pgrid()

    def _fill_available_properties(self, processor, inputDict):
        self.v.avaibleProperties.Clear()
        tplDict = json.loads(Processor.get_processor_by_type(processor).get_tpl())
        available_processors = [k for k in tplDict.keys() if not k in inputDict]
        self.v.avaibleProperties.AppendItems(available_processors)

    def _append_or_update_property_to_page(self, k, v, page):
        prop = page.GetPropertyByName(k)

        if prop is not None:
            prop.SetValue(v)
            return False

        if type(v) is str:
            page.Append(wx.propgrid.StringProperty(k, wx.propgrid.PG_LABEL, v))
        elif type(v) is int:
            page.Append(wx.propgrid.IntProperty(k, wx.propgrid.PG_LABEL, v))
        elif type(v) is list:
            page.Append(wx.propgrid.ArrayStringProperty(k, wx.propgrid.PG_LABEL, v))
        else:
            raise AttributeError('Unsupported property type:' + str(type(v)))
        page.FitColumns()
        return True

    def on_cron_actived(self, evt):
        self._update_cron_setting(1 == evt.Selection)

    def on_cron_changed(self):
        self._update_cron_setting(True)

    @reload_log_after
    def on_datepicker_changed(self, evt):
        dateStr = evt.GetDate().Format("%Y-%m-%d")
        evt.Skip()
        tp = self.v.taskProperty
        prop = tp.GetSelection()
        if prop is not None:
            prop.SetValue(prop.GetValue() + dateStr)
            self._modify_property(prop)

    def on_convert_get_data(self):
        self._convert('{self.get_data("")}')

    def on_convert_get_deep_data(self):
        self._convert('{self.get_deep_data(["",""])}')

    def _convert(self, to, put2first=False):
        tp = self.v.taskProperty
        prop = tp.GetSelection()
        if prop is None:
            return
        current_value = prop.GetValue()
        if put2first:
            prop.SetValue(to + current_value)
        else:
            prop.SetValue(current_value + to)
        self._modify_property(prop)

    @reload_log_after
    def on_convert_rdir(self):
        self._convert('{self.get_rdir()}/', True)

    @reload_log_after
    def on_convert_ddir(self):
        self._convert('{self.get_ddir()}/', True)

    @reload_log_after
    def on_convert_pwd(self):
        prefix = '{self.decrypt("'
        suffix = '")}'
        tp = self.v.taskProperty
        prop = tp.GetSelection()
        if prop is None:
            return

        current_value = prop.GetValue()

        if not type(current_value) is str:
            logging.info('please select a string property.')
            return

        if current_value.startswith(prefix) and current_value.endswith(suffix):
            current_value = current_value.replace(prefix, '')
            current_value = current_value.replace(suffix, '')
            prop.SetValue(Processor.decrypt_pwd(current_value))
        else:
            prop.SetValue(prefix + Processor.encrypt_pwd(current_value) + suffix)

        self._modify_property(prop)

    @reload_log_after
    def on_add_property(self):
        k = self.v.avaibleProperties.GetValue()

        if not len(k) > 0:
            return

        grid = self.v.taskGrid
        processor = grid.GetCellValue(self.currentSelectedRow, 0)
        tplDict = json.loads(Processor.get_processor_by_type(processor).get_tpl())

        if not k in tplDict:
            v = ''
        else:
            v = tplDict[k]

        self._append_or_update_property_to_page(k, v, self.v.taskProperty.GetPage(self.single_page))
        self._add_property(k, v)

        inputDict = json.loads(grid.GetCellValue(self.currentSelectedRow, 1))
        self._fill_available_properties(processor, inputDict)

    @reload_log_after
    def on_delete_property(self):
        tp = self.v.taskProperty
        prop = tp.GetSelection()
        if prop is None or isinstance(prop, wx.propgrid.PropertyCategory):
            logging.info('pls select property first.')
            return

        self._delete_property(prop)
        self._delete_selected_property_from_page(tp)

        grid = self.v.taskGrid

        inputDict = json.loads(grid.GetCellValue(self.currentSelectedRow, 1))
        processor = grid.GetCellValue(self.currentSelectedRow, 0)
        self._fill_available_properties(processor, inputDict)

    def _delete_selected_property_from_page(self, pgm):
        prop = pgm.GetSelection()
        if prop is None or isinstance(prop, wx.propgrid.PropertyCategory):
            logging.info('pls select value property first.')
            return
        pgm.DeleteProperty(prop.GetName())

    @reload_log_after
    def _update_cron_setting(self, enabled: bool):
        if enabled:
            self.v.lableCronExplain.SetLabel(self._explain_cron(self.v.cronInput.GetValue()))
            self.v.cronInput.Enable(True)
        else:
            self.v.lableCronExplain.SetLabel("")
            self.v.cronInput.Enable(False)

    def _explain_cron(self, cron):
        try:
            return str(ExpressionDescriptor(cron))
        except Exception as e:
            logging.error(f"{self.CRON_INVALID}: [ " + cron + " ] just try [ 0 * * * * ]")
            return self.CRON_INVALID

    @reload_log_after
    def on_property_change4e(self, evt):
        prop = evt.GetProperty()
        evt.Skip()
        self._modify_property(prop)

    def _add_property(self, propName, propValue):
        self._op_taskgrid_property(propName, propValue, lambda inputDict, key, value: inputDict | {key: value})
        logging.info(f'Input property added @Task{self.currentSelectedRow + 1} - [ {propName} = {propValue} ]')

    def _delete_property(self, prop):
        self._op_taskgrid_property(prop.GetName(), prop.GetValue(),
                                   lambda inputDict, key, value: {k: v for k, v in inputDict.items() if not k == key})
        logging.info(f'Input property deleted @Task{self.currentSelectedRow + 1} - [ {prop.GetName()} ]')

    def _modify_property(self, prop):
        self._op_taskgrid_property(prop.GetName(), prop.GetValue(),
                                   lambda inputDict, key, value: inputDict | {key: value})
        logging.info(
            f'Input property modified @Task{self.currentSelectedRow + 1} - [ {prop.GetName()} = {prop.GetValue()} ]')

    def _op_taskgrid_property(self, key, value, func):
        taskGrid = self.v.taskGrid
        inputCol = 1

        if self.currentSelectedRow is None or key is None or value is None:
            return

        input = taskGrid.GetCellValue(self.currentSelectedRow, inputCol)
        inputDict = json.loads(input)
        inputDict = func(inputDict, key, value)
        input = json.dumps(inputDict)
        taskGrid.SetCellValue(self.currentSelectedRow, inputCol, input)

    def on_grid_cell_change4p(self, evt):
        grid = self.v.executionGrid
        current_row = evt.GetRow()
        current_column = evt.GetCol()
        evt.Skip()

    def _insert_row(self, grid, choices):
        selectedRows = grid.GetSelectedRows()
        totalRows = grid.GetNumberRows()
        insertAtRow = selectedRows[0] if len(selectedRows) > 0 else 0

        # if select on last row, then append.
        if insertAtRow + 1 == totalRows:
            insertAtRow = totalRows

        grid.InsertRows(insertAtRow, 1, True)
        self._bind_grid_cell_choice_editor(insertAtRow, grid, choices)

    def on_add_row4e(self):
        taskGrid = self.v.taskGrid
        self._insert_row(taskGrid, self.available_processors)

    def on_add_row4p(self):
        executionGrid = self.v.executionGrid
        self._insert_row(executionGrid, self.available_executions)

    def on_delete_rows4e(self):
        self._on_delete_rows(self.v.taskGrid)

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

    async def on_load_log_async(self):
        self.on_load_log()

    def on_load_log(self):

        if hasattr(self, 'isLoading') and self.isLoading:
            return

        if self.isLogContentFocused:
            return

        self.isLoading = True
        with open(OSUtils.get_log_file_path(self.m.app_name), 'r', encoding='utf8') as file:
            self.v.logContents.SetValue(file.read())
            self.v.logContents.AppendText('')
            self.v.logContents.ScrollLines(-1)

        self.isLoading = False

    @reload_log_after
    def on_clean_log(self):
        with open(OSUtils.get_log_file_path(self.m.app_name), 'w', encoding='utf8') as file:
            file.write(f'Clean {self.m.app_name} log@' + DateUtil.get_now_in_str() + '\n')
        self.isLogContentFocused = False

    def on_logcontents_focused(self):
        self.isLogContentFocused = True

    def on_logcontents_unfocused(self):
        self.isLogContentFocused = False

    def on_handle_open_input_dialog(self, evt: PETPEvent):
        dlg = wx.TextEntryDialog(None, evt.data['msg'], evt.data['title'])
        dlg.SetValue(evt.data['default_value'])
        if dlg.ShowModal() == wx.ID_OK:
            evt.handler(dlg.GetValue())
        else:
            evt.handler(None)
        dlg.Destroy()
