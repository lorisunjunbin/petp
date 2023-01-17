#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
#
# generated by wxGlade 1.0.4 on Tue Jan 17 14:38:53 2023
#

import wx

# begin wxGlade: dependencies
import wx.adv
import wx.grid
import wx.propgrid
# end wxGlade

# begin wxGlade: extracode
import os
import wx.adv
from wx._adv import TBI_DOCK
# end wxGlade


class PETPView(wx.Frame):
    def __init__(self, *args, **kwds):
        # begin wxGlade: PETPView.__init__
        kwds["style"] = kwds.get("style", 0) | wx.BORDER_SIMPLE | wx.DEFAULT_FRAME_STYLE | wx.FULL_REPAINT_ON_RESIZE
        wx.Frame.__init__(self, *args, **kwds)
        self.SetSize((1400, 700))
        self.SetTitle("PET-P")

        self.mainSplitterPanel = wx.SplitterWindow(self, wx.ID_ANY, style=wx.CLIP_CHILDREN | wx.SP_BORDER | wx.SP_NOBORDER)
        self.mainSplitterPanel.SetMinimumPaneSize(100)

        self.mainPanel = wx.Panel(self.mainSplitterPanel, wx.ID_ANY)

        mainSizer = wx.BoxSizer(wx.VERTICAL)

        self.notebook = wx.Notebook(self.mainPanel, wx.ID_ANY)
        mainSizer.Add(self.notebook, 1, wx.EXPAND, 0)

        self.nbFirstPage = wx.Panel(self.notebook, wx.ID_ANY, style=wx.BORDER_NONE | wx.TAB_TRAVERSAL)
        self.notebook.AddPage(self.nbFirstPage, "Executions")

        e_main_Sizer = wx.BoxSizer(wx.VERTICAL)

        self.splitterLR4E = wx.SplitterWindow(self.nbFirstPage, wx.ID_ANY, style=wx.SP_BORDER)
        self.splitterLR4E.SetMinimumPaneSize(200)
        e_main_Sizer.Add(self.splitterLR4E, 1, wx.EXPAND, 0)

        self.e_left_panel = wx.SplitterWindow(self.splitterLR4E, wx.ID_ANY, style=wx.SP_BORDER)
        self.e_left_panel.SetMinimumPaneSize(100)

        self.task_editor = wx.Panel(self.e_left_panel, wx.ID_ANY, style=wx.BORDER_THEME)

        task_editor_sizer = wx.BoxSizer(wx.VERTICAL)

        task_editor_action_sizer = wx.BoxSizer(wx.HORIZONTAL)
        task_editor_sizer.Add(task_editor_action_sizer, 0, wx.ALL | wx.EXPAND, 0)

        self.addRow4E = wx.Button(self.task_editor, wx.ID_ANY, "+")
        self.addRow4E.SetMinSize((30, 28))
        self.addRow4E.SetToolTip("Add new row")
        task_editor_action_sizer.Add(self.addRow4E, 0, 0, 0)

        task_editor_action_sizer.Add((5, 30), 0, 0, 0)

        self.delRow4E = wx.Button(self.task_editor, wx.ID_ANY, "-")
        self.delRow4E.SetMinSize((30, 28))
        self.delRow4E.SetToolTip("delete selected row(s)")
        task_editor_action_sizer.Add(self.delRow4E, 0, 0, 0)

        self.recordingLocation = wx.StaticText(self.task_editor, wx.ID_ANY, "")
        task_editor_action_sizer.Add(self.recordingLocation, 0, wx.ALL, 5)

        task_editor_action_sizer.Add((30, 30), 1, wx.ALL, 0)

        self.selectRecording = wx.Button(self.task_editor, wx.ID_ANY, "Select")
        self.selectRecording.SetMinSize((75, 28))
        self.selectRecording.SetToolTip("Select the recording file which generated by Selenium IDE.")
        task_editor_action_sizer.Add(self.selectRecording, 0, 0, 0)

        task_editor_action_sizer.Add((5, 30), 0, 0, 0)

        self.testChooser = wx.ComboBox(self.task_editor, wx.ID_ANY, choices=[], style=wx.CB_DROPDOWN)
        self.testChooser.SetMinSize((120, -1))
        self.testChooser.SetToolTip("Select one test from given recording")
        task_editor_action_sizer.Add(self.testChooser, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 0)

        task_editor_action_sizer.Add((5, 30), 0, 0, 0)

        self.loadRecording = wx.Button(self.task_editor, wx.ID_ANY, "Convert")
        self.loadRecording.SetMinSize((75, 28))
        self.loadRecording.SetToolTip("Convert recording into PETP Task(s)")
        task_editor_action_sizer.Add(self.loadRecording, 0, 0, 0)

        self.taskGrid = wx.grid.Grid(self.task_editor, wx.ID_ANY, size=(1, 1))
        self.taskGrid.CreateGrid(3, 2)
        self.taskGrid.EnableDragGridSize(0)
        self.taskGrid.SetColLabelValue(0, "Task Chooser")
        self.taskGrid.SetColSize(0, 200)
        self.taskGrid.SetColLabelValue(1, "Input")
        self.taskGrid.SetColSize(1, 540)
        task_editor_sizer.Add(self.taskGrid, 1, wx.EXPAND, 0)

        self.loop_editor = wx.Panel(self.e_left_panel, wx.ID_ANY, style=wx.BORDER_THEME)

        loop_editor_sizer = wx.BoxSizer(wx.VERTICAL)

        loop_editor_action_sizer = wx.BoxSizer(wx.HORIZONTAL)
        loop_editor_sizer.Add(loop_editor_action_sizer, 0, wx.ALL | wx.EXPAND, 0)

        self.addLoop = wx.Button(self.loop_editor, wx.ID_ANY, "+")
        self.addLoop.SetMinSize((30, 28))
        self.addLoop.SetToolTip("Add propery")
        loop_editor_action_sizer.Add(self.addLoop, 0, 0, 0)

        loop_editor_action_sizer.Add((5, 30), 0, 0, 0)

        self.delLoop = wx.Button(self.loop_editor, wx.ID_ANY, "-")
        self.delLoop.SetMinSize((30, 28))
        self.delLoop.SetToolTip("delete selected property")
        loop_editor_action_sizer.Add(self.delLoop, 0, 0, 0)

        loop_editor_action_sizer.Add((10, 30), 1, wx.ALL, 0)

        self.convertGetData4Loop = wx.Button(self.loop_editor, wx.ID_ANY, "D")
        self.convertGetData4Loop.SetMinSize((40, 28))
        self.convertGetData4Loop.SetToolTip("{self.get_data(\"\")}")
        loop_editor_action_sizer.Add(self.convertGetData4Loop, 0, 0, 0)

        loop_editor_action_sizer.Add((5, 30), 0, 0, 0)

        self.convertGetDeepData4Loop = wx.Button(self.loop_editor, wx.ID_ANY, "DD")
        self.convertGetDeepData4Loop.SetMinSize((40, 28))
        self.convertGetDeepData4Loop.SetToolTip("{self.get_deep_data([\"\",\"\"])}")
        loop_editor_action_sizer.Add(self.convertGetDeepData4Loop, 0, 0, 0)

        self.loopProperty = wx.propgrid.PropertyGridManager(self.loop_editor, wx.ID_ANY, style=wx.propgrid.PG_BOLD_MODIFIED | wx.propgrid.PG_HIDE_MARGIN | wx.propgrid.PG_NO_INTERNAL_BORDER)
        loop_editor_sizer.Add(self.loopProperty, 0, wx.EXPAND, 0)

        self.e_right_panel = wx.Panel(self.splitterLR4E, wx.ID_ANY, style=wx.BORDER_THEME)

        input_editor_sizer = wx.BoxSizer(wx.VERTICAL)

        input_editor_action_sizer = wx.BoxSizer(wx.HORIZONTAL)
        input_editor_sizer.Add(input_editor_action_sizer, 0, wx.ALL | wx.EXPAND, 0)

        self.avaibleProperties = wx.ComboBox(self.e_right_panel, wx.ID_ANY, choices=[], style=wx.CB_DROPDOWN | wx.TE_PROCESS_ENTER)
        self.avaibleProperties.SetMinSize((100, -1))
        self.avaibleProperties.SetToolTip("Available Properties")
        input_editor_action_sizer.Add(self.avaibleProperties, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 1)

        self.addProperty = wx.Button(self.e_right_panel, wx.ID_ANY, "+")
        self.addProperty.SetMinSize((30, 28))
        self.addProperty.SetToolTip("Add propery")
        input_editor_action_sizer.Add(self.addProperty, 0, 0, 0)

        input_editor_action_sizer.Add((5, 30), 0, 0, 0)

        self.delProperty = wx.Button(self.e_right_panel, wx.ID_ANY, "-")
        self.delProperty.SetMinSize((30, 28))
        self.delProperty.SetToolTip("delete selected property")
        input_editor_action_sizer.Add(self.delProperty, 0, 0, 0)

        input_editor_action_sizer.Add((10, 30), 1, wx.ALL, 0)

        self.datepicker = wx.adv.DatePickerCtrl(self.e_right_panel, wx.ID_ANY, style=wx.adv.DP_DEFAULT | wx.adv.DP_DROPDOWN | wx.adv.DP_SHOWCENTURY)
        self.datepicker.SetToolTip("Fill date to selected property")
        input_editor_action_sizer.Add(self.datepicker, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 1)

        input_editor_action_sizer.Add((5, 30), 0, 0, 0)

        self.convertRDir = wx.Button(self.e_right_panel, wx.ID_ANY, "RDir")
        self.convertRDir.SetMinSize((40, 28))
        self.convertRDir.SetToolTip("get resources dir ")
        input_editor_action_sizer.Add(self.convertRDir, 0, 0, 0)

        input_editor_action_sizer.Add((5, 30), 0, 0, 0)

        self.convertDDir = wx.Button(self.e_right_panel, wx.ID_ANY, "DDir")
        self.convertDDir.SetMinSize((40, 28))
        self.convertDDir.SetToolTip("get download dir ")
        input_editor_action_sizer.Add(self.convertDDir, 0, 0, 0)

        input_editor_action_sizer.Add((5, 30), 0, 0, 0)

        self.convertPWD = wx.Button(self.e_right_panel, wx.ID_ANY, "E/D")
        self.convertPWD.SetMinSize((40, 28))
        self.convertPWD.SetToolTip("Prevent to save password into files")
        input_editor_action_sizer.Add(self.convertPWD, 0, 0, 0)

        input_editor_action_sizer.Add((5, 30), 0, 0, 0)

        self.convertGetData = wx.Button(self.e_right_panel, wx.ID_ANY, "D")
        self.convertGetData.SetMinSize((40, 28))
        self.convertGetData.SetToolTip("{self.get_data(\"\")}")
        input_editor_action_sizer.Add(self.convertGetData, 0, 0, 0)

        input_editor_action_sizer.Add((5, 30), 0, 0, 0)

        self.convertGetDeepData = wx.Button(self.e_right_panel, wx.ID_ANY, "DD")
        self.convertGetDeepData.SetMinSize((40, 28))
        self.convertGetDeepData.SetToolTip("{self.get_deep_data([\"\",\"\"])}")
        input_editor_action_sizer.Add(self.convertGetDeepData, 0, 0, 0)

        self.taskProperty = wx.propgrid.PropertyGridManager(self.e_right_panel, wx.ID_ANY, style=wx.propgrid.PG_BOLD_MODIFIED | wx.propgrid.PG_HIDE_MARGIN | wx.propgrid.PG_NO_INTERNAL_BORDER)
        input_editor_sizer.Add(self.taskProperty, 1, wx.EXPAND, 0)

        e_main_Sizer.Add((0, 5), 0, wx.EXPAND, 0)

        actionPanelSizer_e = wx.BoxSizer(wx.HORIZONTAL)
        e_main_Sizer.Add(actionPanelSizer_e, 0, wx.EXPAND, 0)

        self.delExection = wx.Button(self.nbFirstPage, wx.ID_ANY, "Delete")
        self.delExection.SetMinSize((75, 28))
        self.delExection.SetToolTip("Delete selected Execution")
        actionPanelSizer_e.Add(self.delExection, 0, 0, 0)

        actionPanelSizer_e.Add((5, 30), 0, 0, 0)

        self.executionChooser = wx.ComboBox(self.nbFirstPage, wx.ID_ANY, choices=[], style=wx.CB_DROPDOWN | wx.TE_PROCESS_ENTER)
        self.executionChooser.SetMinSize((300, -1))
        actionPanelSizer_e.Add(self.executionChooser, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 0)

        actionPanelSizer_e.Add((5, 30), 0, 0, 0)

        self.saveExection = wx.Button(self.nbFirstPage, wx.ID_ANY, "Save")
        self.saveExection.SetMinSize((75, 28))
        self.saveExection.SetToolTip("Save or Update selected Execution")
        actionPanelSizer_e.Add(self.saveExection, 0, 0, 0)

        actionPanelSizer_e.Add((5, 30), 0, 0, 0)

        self.stopExection = wx.Button(self.nbFirstPage, wx.ID_ANY, "Stop")
        self.stopExection.SetMinSize((75, 28))
        actionPanelSizer_e.Add(self.stopExection, 0, 0, 0)

        actionPanelSizer_e.Add((5, 30), 0, 0, 0)

        self.runExection = wx.Button(self.nbFirstPage, wx.ID_ANY, "Run Execution")
        self.runExection.SetMinSize((200, 28))
        actionPanelSizer_e.Add(self.runExection, 0, 0, 0)

        actionPanelSizer_e.Add((5, 30), 1, wx.EXPAND, 0)

        self.loadLog = wx.Button(self.nbFirstPage, wx.ID_ANY, "Reload")
        self.loadLog.SetMinSize((80, 28))
        self.loadLog.SetToolTip("reload log ")
        actionPanelSizer_e.Add(self.loadLog, 0, 0, 0)

        actionPanelSizer_e.Add((5, 30), 0, 0, 0)

        self.cleanLog = wx.Button(self.nbFirstPage, wx.ID_ANY, "Clean")
        self.cleanLog.SetMinSize((80, 28))
        self.cleanLog.SetToolTip("Clean log console")
        actionPanelSizer_e.Add(self.cleanLog, 0, 0, 0)

        self.nbSecondPage = wx.Panel(self.notebook, wx.ID_ANY)
        self.notebook.AddPage(self.nbSecondPage, "Pipelines")

        p_main_Sizer = wx.BoxSizer(wx.VERTICAL)

        piplineActionPanelTopSizer = wx.BoxSizer(wx.HORIZONTAL)
        p_main_Sizer.Add(piplineActionPanelTopSizer, 0, wx.ALL, 0)

        piplineActionPanelTopSizer.Add((3, 30), 0, 0, 0)

        self.addRow4P = wx.Button(self.nbSecondPage, wx.ID_ANY, "+")
        self.addRow4P.SetMinSize((30, 28))
        self.addRow4P.SetToolTip("Add row")
        piplineActionPanelTopSizer.Add(self.addRow4P, 0, 0, 0)

        piplineActionPanelTopSizer.Add((10, 30), 0, 0, 0)

        self.delRow4P = wx.Button(self.nbSecondPage, wx.ID_ANY, "-")
        self.delRow4P.SetMinSize((30, 28))
        self.delRow4P.SetToolTip("Delete selected row(s)")
        piplineActionPanelTopSizer.Add(self.delRow4P, 0, 0, 0)

        self.executionGrid = wx.grid.Grid(self.nbSecondPage, wx.ID_ANY, size=(1, 1))
        self.executionGrid.CreateGrid(8, 2)
        self.executionGrid.SetColLabelValue(0, "Execution Chooser")
        self.executionGrid.SetColSize(0, 400)
        self.executionGrid.SetColLabelValue(1, "Input")
        self.executionGrid.SetColSize(1, 800)
        p_main_Sizer.Add(self.executionGrid, 1, wx.EXPAND, 0)

        actionPanelSizer_p = wx.BoxSizer(wx.HORIZONTAL)
        p_main_Sizer.Add(actionPanelSizer_p, 0, wx.EXPAND | wx.FIXED_MINSIZE, 0)

        self.delPipeline = wx.Button(self.nbSecondPage, wx.ID_ANY, "Delete")
        self.delPipeline.SetMinSize((75, 28))
        self.delPipeline.SetToolTip("Delete selected Pipeline")
        actionPanelSizer_p.Add(self.delPipeline, 0, 0, 0)

        actionPanelSizer_p.Add((5, 30), 0, 0, 0)

        self.pipelineChooser = wx.ComboBox(self.nbSecondPage, wx.ID_ANY, choices=[], style=wx.CB_DROPDOWN | wx.TE_PROCESS_ENTER)
        self.pipelineChooser.SetMinSize((300, -1))
        actionPanelSizer_p.Add(self.pipelineChooser, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 0)

        actionPanelSizer_p.Add((5, 30), 0, 0, 0)

        self.savePipeline = wx.Button(self.nbSecondPage, wx.ID_ANY, "Save")
        self.savePipeline.SetMinSize((75, 28))
        self.savePipeline.SetToolTip("Save or Update selected Pipeline")
        actionPanelSizer_p.Add(self.savePipeline, 0, 0, 0)

        actionPanelSizer_p.Add((5, 30), 0, 0, 0)

        self.runPipeline = wx.Button(self.nbSecondPage, wx.ID_ANY, "Run Pipeline")
        self.runPipeline.SetMinSize((200, 28))
        actionPanelSizer_p.Add(self.runPipeline, 0, 0, 0)

        actionPanelSizer_p.Add((5, 30), 0, 0, 0)

        self.asCronChecbox = wx.CheckBox(self.nbSecondPage, wx.ID_ANY, "as cron", style=wx.ALIGN_RIGHT | wx.CHK_2STATE)
        actionPanelSizer_p.Add(self.asCronChecbox, 0, wx.ALL | wx.EXPAND, 0)

        actionPanelSizer_p.Add((5, 30), 0, 0, 0)

        self.cronInput = wx.TextCtrl(self.nbSecondPage, wx.ID_ANY, "0 * * * *", style=wx.TE_CENTRE)
        self.cronInput.SetMinSize((100, -1))
        self.cronInput.Enable(False)
        actionPanelSizer_p.Add(self.cronInput, 0, wx.ALIGN_CENTER_VERTICAL, 0)

        actionPanelSizer_p.Add((5, 30), 0, 0, 0)

        self.lableCronExplain = wx.StaticText(self.nbSecondPage, wx.ID_ANY, "", style=wx.ALIGN_LEFT)
        self.lableCronExplain.SetMinSize((300, -1))
        actionPanelSizer_p.Add(self.lableCronExplain, 0, wx.ALL, 5)

        actionPanelSizer_p.Add((5, 30), 0, 0, 0)

        self.stopCurrentCron = wx.Button(self.nbSecondPage, wx.ID_ANY, "Stop")
        self.stopCurrentCron.SetMinSize((100, 28))
        self.stopCurrentCron.SetToolTip("Stop selected Pipeline which is running as cron")
        actionPanelSizer_p.Add(self.stopCurrentCron, 0, 0, 0)

        actionPanelSizer_p.Add((5, 30), 0, 0, 0)

        self.stopAll = wx.Button(self.nbSecondPage, wx.ID_ANY, "Stop All")
        self.stopAll.SetMinSize((100, 28))
        self.stopAll.SetToolTip("Stop all pipelines running as cron.")
        actionPanelSizer_p.Add(self.stopAll, 0, 0, 0)

        self.logContents = wx.TextCtrl(self.mainSplitterPanel, wx.ID_ANY, "", style=wx.BORDER_NONE | wx.TE_DONTWRAP | wx.TE_LEFT | wx.TE_MULTILINE | wx.TE_READONLY)
        self.logContents.SetBackgroundColour(wx.Colour(78, 78, 78))
        self.logContents.SetForegroundColour(wx.Colour(0, 255, 0))

        self.nbSecondPage.SetSizer(p_main_Sizer)

        self.e_right_panel.SetSizer(input_editor_sizer)

        self.loop_editor.SetSizer(loop_editor_sizer)

        self.task_editor.SetSizer(task_editor_sizer)

        self.e_left_panel.SplitHorizontally(self.task_editor, self.loop_editor, 286)

        self.splitterLR4E.SplitVertically(self.e_left_panel, self.e_right_panel, 855)

        self.nbFirstPage.SetSizer(e_main_Sizer)

        self.mainPanel.SetSizer(mainSizer)

        self.mainSplitterPanel.SplitHorizontally(self.mainPanel, self.logContents, 470)

        self.Layout()
        self.Centre()
        _icon = wx.NullIcon
        _logo_path = os.path.realpath('image') + "/petp.png"
        _icon.CopyFromBitmap(wx.Bitmap(_logo_path , wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)

        _tbiIcon = wx.adv.TaskBarIcon(iconType=TBI_DOCK)
        _tbiIcon.frame=self
        _tbiIcon.SetIcon(_icon, "PETP")

        self.tbicon = _tbiIcon

        # end wxGlade

# end of class PETPView

class PETP(wx.App):
    def OnInit(self):
        self.PETP = PETPView(None, wx.ID_ANY, "")
        self.SetTopWindow(self.PETP)
        self.PETP.Show()
        return True

# end of class PETP

if __name__ == "__main__":
    PETP = PETP(0)
    PETP.MainLoop()
