from i18n.desc_translations import DESC_TRANSLATIONS

TRANSLATIONS: dict[str, dict[str, str]] = {

    # === Window / Tab ===
    "win_title": {"en": "PET-P", "zh": "PET-P"},
    "tab_executions": {"en": "Executions", "zh": "Executions"},
    "tab_pipelines": {"en": "Pipelines", "zh": "Pipelines"},

    # === Buttons — Execution tab ===
    "btn_delete": {"en": "🗑", "zh": "🗑"},
    "btn_copy": {"en": "📋", "zh": "📋"},
    "btn_save": {"en": "Save", "zh": "保存"},
    "btn_run_execution": {"en": "Execute", "zh": "运 行"},
    "btn_run_pipeline": {"en": "Execute", "zh": "运 行"},
    "btn_stop": {"en": "Stop", "zh": "停 止"},
    "btn_stop_all": {"en": "Stop All", "zh": "全部停止"},
    "btn_reload": {"en": "Reload", "zh": "重载日志"},
    "btn_clean": {"en": "Clean", "zh": "清空日志"},
    "tip_log_search": {"en": "Search log", "zh": "搜索日志"},
    "tip_find_prev": {"en": "Previous match (Shift+Enter)", "zh": "上一个匹配 (Shift+Enter)"},
    "label_find_prev": {"en": "▲", "zh": "▲"},
    "tip_find_next": {"en": "Next match (Enter)", "zh": "下一个匹配 (Enter)"},
    "label_find_next": {"en": "▼", "zh": "▼"},
    "tip_filter_log": {"en": "Filter: show only lines matching keyword", "zh": "过滤：只显示含关键字的行"},
    "log_match_count": {"en": "{count} matches", "zh": "{count}个匹配"},
    "btn_select": {"en": "Select", "zh": "选择"},
    "btn_convert": {"en": "Convert", "zh": "转换"},


    # === Tooltips — task editor ===
    "tip_add_row": {"en": "Add new row", "zh": "添加新行"},
    "tip_delete_row": {"en": "delete selected row(s)", "zh": "删除选中行"},
    "tip_select_recording": {
        "en": "Select the recording file exported from Chrome DevTools Recorder.",
        "zh": "选择由 Chrome DevTools Recorder 导出的录制文件。",
    },
    "tip_convert_recording": {
        "en": "Convert recording into PETP Task(s), insert before selected task, otherwise append to the tail",
        "zh": "将录制内容转换为 PETP 任务, 在选中任务前依次插入，不选追加到任务列表尾部",
    },

    # === Tooltips — loop editor ===
    "tip_add_property": {"en": "Add property", "zh": "添加属性"},
    "tip_delete_property": {"en": "delete selected property", "zh": "删除选中属性"},
    "tip_edit_loop": {"en": "Edit selected loop", "zh": "编辑选中循环"},
    "btn_edit_loop": {"en": "⚙️", "zh": "⚙️"},

    # === Tooltips — input editor ===
    "tip_available_properties": {"en": "Available Properties", "zh": "可用属性"},
    "tip_add_prop": {"en": "Add propery", "zh": "添加属性"},
    "tip_delete_prop": {"en": "delete selected property", "zh": "删除选中属性"},
    "tip_skip_task": {"en": "check to skip current task", "zh": "勾选以跳过当前任务"},
    "tip_fill_date": {"en": "Fill date to selected property", "zh": "将日期填入选中属性"},

    # === Tooltips — handy buttons ===
    "tip_handy_tools": {"en": "Quick insert helpers", "zh": "快捷插入工具"},
    "tip_rdir": {"en": "get resources dir ", "zh": "获取资源目录"},
    "tip_ddir": {"en": "get download dir ", "zh": "获取下载目录"},
    "tip_pwd": {"en": "Prevent to save password into files", "zh": "防止将密码保存到文件中"},

    # === Handy tools menu items ===
    "handy_rdir": {"en": "Resources Dir\t{self.get_rdir()}/", "zh": "资源目录\t{self.get_rdir()}/"},
    "handy_ddir": {"en": "Download Dir\t{self.get_ddir()}/", "zh": "下载目录\t{self.get_ddir()}/"},
    "handy_tdir": {"en": "Test Dir\t{self.get_tdir()}/", "zh": "测试目录\t{self.get_tdir()}/"},
    "handy_encrypt": {"en": "Encrypt / Decrypt Password", "zh": "加密 / 解密密码"},
    "handy_get_data": {"en": "get_data(\"\")", "zh": "get_data(\"\")"},
    "handy_get_data_by_loop": {"en": "get_data_by_loop(\"\")", "zh": "get_data_by_loop(\"\")"},
    "handy_get_deep_data": {"en": "get_deep_data([\"\",\"\"])", "zh": "get_deep_data([\"\",\"\"])"},
    "handy_date_str": {"en": "Date String\t{self.get_now_str()}", "zh": "日期字符串\t{self.get_now_str()}"},
    "handy_os_sep": {"en": "OS Separator\t{os.sep}", "zh": "系统路径分隔符\t{os.sep}"},
    "handy_os_getenv": {"en": "OS Env Var\t{os.getenv(\"\")}", "zh": "系统环境变量\t{os.getenv(\"\")}"},
    "handy_str2dict": {"en": "str2dict(\"k1|>v1\")", "zh": "str2dict(\"k1|>v1\")"},
    "handy_feed_tpl": {"en": "feed_tpl(\"tpl\", {})", "zh": "feed_tpl(\"tpl\", {})"},
    "handy_prop2dict": {"en": "prop2dict(\"k=v\")", "zh": "prop2dict(\"k=v\")"},
    "handy_json2dict": {"en": "json2dict(\"json\")", "zh": "json2dict(\"json\")"},
    "handy_json_dumps": {"en": "json.dumps(obj)", "zh": "json.dumps(obj)"},
    "handy_json_loads": {"en": "json.loads(str)", "zh": "json.loads(str)"},
    "handy_str2list": {"en": "str2list(\"a|>b\")", "zh": "str2list(\"a|>b\")"},
    "handy_get_sdir": {"en": "Shared Dir\t{self.get_sdir()}/", "zh": "共享目录\t{self.get_sdir()}/"},
    "btn_handy_tools": {"en": "🧰", "zh": "🧰"},

    # === Tooltips — execution actions ===
    "tip_delete_execution": {"en": "Delete selected Execution", "zh": "删除选中的Execution"},
    "tip_copy_execution": {"en": "Copy selected Execution", "zh": "复制选中Execution"},
    "tip_create_execution": {"en": "Create new Execution", "zh": "新建Execution"},
    "dlg_create_exec_title": {"en": "Create Execution", "zh": "新建Execution"},
    "dlg_create_exec_name": {"en": "Execution name:", "zh": "Execution名称："},
    "dlg_create_exec_mode": {"en": "Choose creation mode:", "zh": "选择创建方式："},
    "dlg_create_exec_blank": {"en": "Blank (empty)", "zh": "空白新建"},
    "dlg_create_exec_dup": {"en": "Name is empty or already exists.", "zh": "名称为空或已存在。"},
    "dlg_no_exec_selected": {"en": "Please select an Execution first.", "zh": "请先选择一个Execution。"},
    "tip_save_execution": {"en": "Save or Update selected Execution", "zh": "保存或更新选中的Execution"},
    "tip_execute_on_startup": {"en": "Execute on startup", "zh": "启动时运行"},
    "tip_change_log_level": {"en": "Change Log Level", "zh": "更改日志级别"},
    "tip_reload_log": {"en": "reload log ", "zh": "重新加载日志"},
    "tip_clean_log": {"en": "Clean log console", "zh": "清空日志控制台"},
    "tip_change_lang": {"en": "Change Language", "zh": "切换语言"},
    "tip_change_theme": {"en": "Change Theme", "zh": "切换主题"},
    "tip_exec_desc": {"en": "Execution description", "zh": "Execution描述"},
    "tip_as_mcp_tool": {
        "en": "Publish current Execution as PETP MCP tool ",
        "zh": "发布当前Execution PETP MCP Tool",
    },
    "astool_on": {
        "en": "Published as MCP Tool",
        "zh": "已发布为 MCP Tool",
    },
    "astool_off": {
        "en": "Not published as MCP Tool",
        "zh": "尚未发布为 MCP Tool",
    },
    "only_tool_on": {
        "en": "Tool",
        "zh": "工具",
    },
    "only_tool_off": {
        "en": "All",
        "zh": "全部",
    },
    "tip_only_tool": {
        "en": "Show only executions published as MCP tools",
        "zh": "仅显示已发布为 MCP Tool 的 Execution",
    },
    "warn_missing_response_key": {
        "en": "The last Task should be HTTP_RESPONSE_KEY to provide the final result, otherwise please specify Output Parameters instead.",
        "zh": "最后一个 Task 应为 HTTP_RESPONSE_KEY 以提供最终结果，或者请配置输出参数作为替代。",
    },
    "warn_astool_no_output_config": {
        "en": "This execution is marked as MCP tool but has neither HTTP_RESPONSE_KEY as last task nor Output Parameters configured. Please add one of them before saving.",
        "zh": "此执行被标记为 MCP 工具，但既没有 HTTP_RESPONSE_KEY 作为最后一个 Task，也没有配置输出参数。请先添加其中之一再保存。",
    },
    "prompt_sync_initial_params": {
        "en": "The first task is not INITIAL_PARAMS. Convert Input Parameters to an INITIAL_PARAMS task as the first task?",
        "zh": "第一个 Task 不是 INITIAL_PARAMS。是否将输入参数转换为首个 INITIAL_PARAMS Task？",
    },

    # === MCP Description Editor ===
    "mcp_lbl_tool_desc": {"en": "Description:", "zh": "工具描述："},
    "mcp_lbl_input_params": {"en": "Input Parameters:", "zh": "输入参数："},
    "mcp_lbl_output_params": {"en": "Output Parameters:", "zh": "输出参数："},
    "mcp_col_name": {"en": "Name", "zh": "名称"},
    "mcp_col_type": {"en": "Type", "zh": "类型"},
    "mcp_col_desc": {"en": "Description", "zh": "描述"},
    "mcp_col_required": {"en": "Required", "zh": "必填"},
    "mcp_col_default": {"en": "Default", "zh": "默认值"},
    "mcp_col_map_key": {"en": "Map To DataChain Key", "zh": "映射DataChain键"},
    "mcp_tip_add_input": {"en": "Add input parameter", "zh": "添加输入参数"},
    "mcp_tip_del_input": {"en": "Remove selected input parameter", "zh": "删除选中的输入参数"},
    "mcp_tip_add_output": {"en": "Add output parameter", "zh": "添加输出参数"},
    "mcp_tip_del_output": {"en": "Remove selected output parameter", "zh": "删除选中的输出参数"},
    "mcp_tip_tool_desc": {"en": "Brief description of what this tool does", "zh": "简要描述此工具的功能"},
    "mcp_tip_preview_json": {"en": "Preview generated JSON", "zh": "预览生成的JSON"},
    "mcp_tip_sync_input": {"en": "Sync from selected task (default: first)", "zh": "从选中任务同步（默认：首个）"},
    "mcp_dlg_sync_title": {"en": "Sync Input Parameters", "zh": "同步输入参数"},
    "mcp_sync_no_params": {"en": "Selected task has no parseable JSON parameters.", "zh": "选中任务没有可解析的JSON参数。"},
    "mcp_tip_sync_output": {"en": "Sync from selected task (default: last)", "zh": "从选中任务同步（默认：末尾）"},
    "mcp_dlg_sync_output_title": {"en": "Sync Output Parameters", "zh": "同步输出参数"},
    "mcp_sync_output_no_params": {"en": "Selected task has no parseable JSON parameters.", "zh": "选中任务没有可解析的JSON参数。"},
    "mcp_sync_check_all": {"en": "Check All", "zh": "全选"},
    "mcp_sync_uncheck_all": {"en": "Uncheck All", "zh": "全不选"},

    # === Tooltips — pipeline actions ===
    "tip_add_row_p": {"en": "Add row", "zh": "添加行"},
    "tip_delete_row_p": {"en": "Delete selected row(s)", "zh": "删除选中行"},
    "tip_delete_pipeline": {"en": "Delete selected Pipeline", "zh": "删除选中的流水线"},
    "tip_save_pipeline": {"en": "Save or Update selected Pipeline", "zh": "保存或更新选中的流水线"},
    "tip_stop_cron": {
        "en": "Stop selected Pipeline which is running as cron",
        "zh": "停止以定时任务运行的选中流水线",
    },
    "tip_stop_all_cron": {"en": "Stop all pipelines running as cron.", "zh": "停止所有以定时任务运行的流水线。"},
    "btn_cron_history": {"en": "History", "zh": "历史记录"},
    "tip_cron_history": {"en": "View cron execution history", "zh": "查看定时任务执行历史"},

    # === Cron Dashboard dialog ===
    "dlg_cron_dashboard_title": {"en": "Cron Execution History", "zh": "定时任务执行历史"},
    "cron_col_start_time": {"en": "Start Time", "zh": "开始时间"},
    "cron_col_pipeline": {"en": "Pipeline", "zh": "流水线"},
    "cron_col_cron_exp": {"en": "Cron Exp", "zh": "Cron 表达式"},
    "cron_col_status": {"en": "Status", "zh": "状态"},
    "cron_col_duration": {"en": "Duration", "zh": "耗时"},
    "cron_col_error": {"en": "Error", "zh": "错误"},
    "cron_filter_hint": {"en": "Filter by pipeline name…", "zh": "按流水线名称过滤…"},
    "cron_lbl_filter": {"en": "Filter:", "zh": "过滤："},
    "btn_refresh": {"en": "Refresh", "zh": "刷新"},

    # === Tooltips — chooser ===
    "tip_exec_chooser": {
        "en": "Select or search Execution (type to filter)",
        "zh": "选择或搜索Execution（输入以筛选）",
    },
    "tip_pipeline_chooser": {
        "en": "Select or search Pipeline (type to filter)",
        "zh": "选择或搜索Pipeline（输入以筛选）",
    },

    # === Grid column headers ===
    "grid_task_chooser": {"en": "Task Chooser", "zh": "Task选择"},
    "grid_task_desc": {"en": "Description", "zh": "描述"},
    "grid_input": {"en": "Input", "zh": "输入"},
    "grid_exec_chooser": {"en": "Execution Chooser", "zh": "Execution选择"},

    # === Context menu ===
    "menu_copy": {"en": "Copy", "zh": "复制"},
    "menu_paste": {"en": "Paste", "zh": "粘贴"},
    "menu_duplicate_row": {"en": "Duplicate Row", "zh": "复制行"},
    "menu_move_up": {"en": "Move Up", "zh": "上移"},
    "menu_move_down": {"en": "Move Down", "zh": "下移"},
    "menu_delete_row": {"en": "Delete Row", "zh": "删除行"},
    "menu_edit_input": {"en": "Edit Input", "zh": "编辑输入"},
    "menu_fill_skeleton": {"en": "Fill Param Skeleton", "zh": "填充参数骨架"},
    "menu_clear_input": {"en": "Clear Input", "zh": "清除输入"},
    "dlg_delete_pipeline_msg": {"en": "Delete pipeline '{name}'?", "zh": "确定删除流水线 '{name}'？"},
    "dlg_delete_pipeline_title": {"en": "Delete Pipeline", "zh": "删除流水线"},
    "menu_skip_task": {"en": "Skip", "zh": "跳过"},
    "menu_unskip_task": {"en": "Unskip", "zh": "取消跳过"},
    "menu_view_processor_usage": {"en": "View Processor Usage", "zh": "查看Processor用法"},
    "menu_find_referencing_executions": {"en": "Find References of {name}", "zh": "查找{name}的引用"},
    "dlg_processor_usage_title": {"en": "Processor Usage", "zh": "Processor 用法"},
    "dlg_referencing_executions_title": {"en": "References of {name}", "zh": "{name}的引用"},
    "dlg_no_referencing_executions": {"en": "No executions reference {name}.",
                                      "zh": "没有Execution引用{name}。"},
    "menu_copy_name": {"en": "Copy Name", "zh": "复制名"},
    "menu_copy_value": {"en": "Copy Value", "zh": "复制值"},
    "menu_copy_pair": {"en": "Copy Name+Value", "zh": "复制Name+Value"},
    "menu_paste_pair": {"en": "Paste Name+Value", "zh": "粘贴Name+Value"},
    "menu_edit_complex": {"en": "Edit Complex Value", "zh": "编辑复杂值"},
    "menu_rename_key": {"en": "Edit Name", "zh": "修改名"},
    "menu_param_hint": {"en": "Property Description", "zh": "属性介绍"},
    "param_hint_not_found": {"en": "No description found for \"{name}\".", "zh": "未找到\"{name}\"的属性介绍。"},
    "dlg_rename_key_title": {"en": "Edit Property Name", "zh": "修改属性名"},
    "dlg_rename_key_msg": {"en": "New name:", "zh": "新名："},
    "menu_move_up": {"en": "Move Up\tShift+Up", "zh": "上移\tShift+Up"},
    "menu_move_down": {"en": "Move Down\tShift+Down", "zh": "下移\tShift+Down"},
    "menu_edit_loop": {"en": "Edit Loop...", "zh": "编辑循环..."},
    "loop_dlg_title": {"en": "Loop Editor", "zh": "循环编辑器"},
    "loop_dlg_col_key": {"en": "Key", "zh": "键"},
    "loop_dlg_col_value": {"en": "Value", "zh": "值"},
    "loop_tip_task_start":     {"en": "task_start: row number (1-based) in the task grid where the loop body begins", "zh": "task_start: 循环体起始任务行号（从1开始）"},
    "loop_tip_task_end":       {"en": "task_end: row number (1-based) in the task grid where the loop body ends (inclusive)", "zh": "task_end: 循环体结束任务行号（含，从1开始）"},
    "loop_tip_loop_key":       {"en": "loop_key: data_chain key whose value is the collection to iterate over; set loop_times to \"0\" when using this", "zh": "loop_key: data_chain 中作为遍历集合的键；使用此项时 loop_times 须设为 \"0\""},
    "loop_tip_loop_times":     {"en": "loop_times: fixed number of iterations; set to \"0\" to use loop_key instead", "zh": "loop_times: 固定循环次数；设为 \"0\" 则改用 loop_key 遍历集合"},
    "loop_tip_loop_index_key": {"en": "loop_index_key: data_chain key that receives the current 0-based iteration index", "zh": "loop_index_key: 接收当前迭代下标（从0开始）的 data_chain 键"},
    "loop_tip_item_key":       {"en": "item_key: data_chain key that receives the current collection item each iteration", "zh": "item_key: 每次迭代时接收当前集合元素的 data_chain 键"},
    "loop_tip_exception_then":  {"en": "exception_then: what to do when a task inside the loop raises an exception — \"break\" stops the loop, \"continue\" skips to next iteration", "zh": "exception_then: 循环内任务出错时的处理方式 — \"break\" 终止循环，\"continue\" 跳过本次继续"},
    "loop_tip_loop_condition":  {"en": "loop_condition: Python function body (data_chain) → (bool, str); return True,'break' to exit loop; return True,'continue' to skip to next iteration; return False,'' to proceed normally", "zh": "loop_condition: Python方法体 (data_chain)，return True,'break' 终止循环；return True,'continue' 跳到下一次迭代；return False,'' 正常继续"},
    "menu_undo": {"en": "Undo\tCtrl+Z", "zh": "撤销\tCtrl+Z"},
    "menu_redo": {"en": "Redo\tCtrl+Y", "zh": "重做\tCtrl+Y"},
    "menu_snapshots": {"en": "Snapshots", "zh": "快 照"},
    "tip_snapshots": {"en": "View and apply editing snapshots", "zh": "查看并应用编辑快照"},

    # === Snapshot dialog ===
    "dlg_snapshot_title": {"en": "Execution Snapshots", "zh": "Execution 快照"},
    "btn_apply_snapshot": {"en": "Apply", "zh": "应用"},
    "snap_no_changes": {"en": "(no changes from previous snapshot)", "zh": "（与上一快照无变化）"},
    "snap_first_snapshot": {"en": "(first snapshot — full content)", "zh": "（第一个快照 — 完整内容）"},
    "btn_close": {"en": "Close", "zh": "关闭"},

    # === Execution version compare ===
    "menu_compare_versions": {"en": "Compare Versions", "zh": "对比版本"},
    "dlg_compare_title": {"en": "Execution Version Compare", "zh": "Execution 版本对比"},
    "compare_no_changes": {"en": "(no differences)", "zh": "（无差异）"},
    "btn_apply_version": {"en": "Replace Current", "zh": "替换当前版本"},

    # === Unsaved changes dialog ===
    "dlg_unsaved_title": {"en": "Unsaved Changes", "zh": "未保存的更改"},
    "dlg_unsaved_msg": {
        "en": "Current execution has unsaved changes.",
        "zh": "当前Execution有未保存的更改。",
    },
    "btn_dismiss": {"en": "Dismiss", "zh": "知道了"},
    "btn_save_and_run": {"en": "Save and Run", "zh": "保存并继续运行"},
    "dlg_unsaved_on_close_msg": {
        "en": "Current execution has unsaved changes. What would you like to do?",
        "zh": "当前Execution有未保存的更改，是否继续退出？",
    },
    "btn_save_and_exit": {"en": "Save and Exit", "zh": "保存并退出"},
    "btn_exit_without_save": {"en": "Exit Without Saving", "zh": "直接退出"},
    "btn_cancel_exit": {"en": "Cancel", "zh": "取消退出"},

    # === Property grid categories ===
    "pgrid_input_editor": {"en": "Input Editor", "zh": "输入编辑器"},
    "pgrid_input_editor_of": {"en": "Input Editor of T", "zh": "任务 T"},
    "pgrid_loop_editor": {"en": "Loop Editor", "zh": "循环编辑器"},

    # === Dialog titles ===
    "dlg_input_title": {"en": "PETP - Input", "zh": "PETP - 请输入"},
    "dlg_result_title": {"en": "PETP - Message Box", "zh": "PETP - 消息框"},
    "dlg_copy_exec_title": {"en": "Copy Execution", "zh": "复制Execution"},
    "dlg_copy_exec_msg": {"en": "Enter name for the copy:", "zh": "请输入副本名称："},
    "dlg_copy_exec_dup": {"en": "Name already exists, please choose a different name.",
                          "zh": "名称已存在，请选择其他名称。"},
    "dlg_delete_exec_title": {"en": "Delete Execution", "zh": "删除Execution"},
    "dlg_delete_exec_msg": {
        "en": "Delete \"{name}\"?\n\nThe file will be moved to core/executions/trash/ and can be restored manually.",
        "zh": "确定删除 \"{name}\"？\n\n文件将移至 core/executions/trash/，可手动恢复。",
    },

    # === Dialog buttons ===
    "dlg_save_json": {"en": "Save as JSON", "zh": "另存为 JSON"},
    "dlg_save_csv": {"en": "Save as CSV", "zh": "另存为 CSV"},
    "dlg_copy": {"en": "Copy", "zh": "复制"},
    "dlg_view_data_chain": {"en": "View data_chain", "zh": "查看 data_chain"},
    "dlg_ok": {"en": "&OK", "zh": "确定(&O)"},
    "dlg_cancel": {"en": "&Cancel", "zh": "取消(&C)"},
    "dlg_save_as_default": {"en": "Save as &Default", "zh": "保存为默认值(&D)"},

    # === Dialog messages ===
    "dlg_saved_to": {"en": "Saved to:\n{path}", "zh": "已保存至:\n{path}"},
    "dlg_failed_to_save": {"en": "Failed to save:\n{error}", "zh": "保存失败:\n{error}"},
    "dlg_error": {"en": "Error", "zh": "错误"},
    "dlg_data_chain_title": {"en": "data_chain JSON", "zh": "data_chain JSON"},

    # === File dialog ===
    "fdlg_open_recording": {
        "en": "Open Chrome DevTools Recorder file",
        "zh": "打开 Chrome DevTools Recorder 录制文件",
    },

    # === Status / validation messages (presenter) ===
    "msg_cron_invalid": {"en": "Invalid CRON", "zh": "CRON 表达式无效"},
    "msg_cron_cannot_save": {
        "en": "CRON is invalid, cron can not be saved",
        "zh": "CRON 无效，无法保存",
    },
    "msg_exec_list_empty": {
        "en": "Execution list should NOT be empty",
        "zh": "Execution列表不能为空",
    },
    "msg_pipeline_name_empty": {
        "en": "Pipeline: cron name should not be empty",
        "zh": "流水线：名称不能为空",
    },
    "msg_pipeline_overwrite": {
        "en": "Pipeline: {name} already existed, overwrite!",
        "zh": "流水线：{name} 已存在，将覆盖！",
    },
    "msg_execution_overwrite": {
        "en": "Execution: {name} already existed, overwrite!",
        "zh": "Execution：{name} 已存在，将覆盖！",
    },
    "msg_execution_stopping": {
        "en": "Execution: [ {name} ] is manually stopping.",
        "zh": "Execution：[ {name} ] 正在手动停止。",
    },
    "msg_save_aborted": {
        "en": "Save aborted due to unresolved syntax errors.",
        "zh": "因未解决的语法错误，保存已中止。",
    },
    "msg_select_string_prop": {
        "en": "please select a string property.",
        "zh": "请选择一个字符串属性。",
    },
    "msg_no_task_row_bound": {
        "en": "No task row bound to property grid.",
        "zh": "没有任务行绑定到属性网格。",
    },
    "msg_select_task_row_first": {
        "en": "Please select a task row first before toggling skip.",
        "zh": "请先选择一个任务行再切换跳过状态。",
    },
    "msg_select_property_first": {
        "en": "pls select property first.",
        "zh": "请先选择属性。",
    },
    "msg_select_value_property": {
        "en": "pls select value property first.",
        "zh": "请先选择值属性。",
    },
    "msg_cron_invalid_hint": {
        "en": "{cron_invalid}: [ {cron} ] just try [ 0 * * * * ]",
        "zh": "{cron_invalid}: [ {cron} ] 请尝试 [ 0 * * * * ]",
    },
    "msg_convert_success": {
        "en": "Successfully converted from Chrome Recorder: {file_path}, {title}",
        "zh": "成功从 Chrome Recorder 录制转换：{file_path}, {title}",
    },
    "msg_recording_empty": {
        "en": "Recording location and test name should not be empty, also able to select the row where start to load.",
        "zh": "录制位置和测试名称不能为空，也可以选择开始加载的行。",
    },
    "msg_exec_not_tool": {
        "en": "Execution '{name}' is not available as a tool (astool=false)",
        "zh": "Execution '{name}' 不可用作工具（astool=false）",
    },
    "msg_unsupported_chart": {
        "en": "Unsupported chart type: {chart_type}",
        "zh": "不支持的图表类型：{chart_type}",
    },

    # === Checkbox labels ===
    "cb_as_cron": {"en": "as cron", "zh": "定时任务"},

    # === ProcessorPalette ===
    "palette_hint": {"en": "type to filter...", "zh": "输入筛选..."},
    "palette_footer_all": {"en": "{n} items", "zh": "{n} 项"},
    "palette_footer_filtered": {"en": "{total} / {n}  (name: {nm}  cat: {ct})", "zh": "{total} / {n}  (名称: {nm}  分类: {ct})"},
    "palette_sep_label": {"en": "── category matches ──", "zh": "── 分类匹配 ──"},

    "badge_skipped": {"en": "⊖  skipped — this task will be skipped during execution", "zh": "⊖  已跳过 — 执行时此任务将被跳过"},
    "badge_empty":   {"en": "⚠  empty param — one or more parameters are empty", "zh": "⚠  空参数 — 存在一个或多个空参数"},
    "badge_expr":    {"en": "{…}  expression — parameter contains a dynamic expression", "zh": "{…}  表达式 — 参数中包含动态表达式"},

    # === Startup welcome / motivational messages ===
    "welcome_0": {
        "en": "Welcome back! Automation starts here.",
        "zh": "欢迎回来！自动化，从这里启程。",
    },
    "welcome_1": {
        "en": "Every great workflow begins with a single task.",
        "zh": "千里之行，始于一个任务。",
    },
    "welcome_2": {
        "en": "Let the robots work — you focus on what matters.",
        "zh": "让机器人干活，你来专注真正重要的事。",
    },
    "welcome_3": {
        "en": "Build once, run forever. Automate it with PETP.",
        "zh": "一次构建，永久运行。PETP 助你解放双手。",
    },
    "welcome_4": {
        "en": "Less repetition, more creation.",
        "zh": "少一分重复，多一分创造。",
    },
    "welcome_5": {
        "en": "Your pipeline is ready. Make today count.",
        "zh": "流水线已就绪，让今天的每一刻都有价值。",
    },
    "welcome_6": {
        "en": "Automate the boring stuff — dream bigger.",
        "zh": "自动化那些枯燥的事，然后去追更大的梦想。",
    },
    "welcome_7": {
        "en": "Consistency beats perfection. Ship your tasks.",
        "zh": "坚持胜过完美，跑起你的任务吧。",
    },
    "welcome_8": {
        "en": "Small automations, massive gains over time.",
        "zh": "小小的自动化，长期积累的巨大收益。",
    },
    "welcome_9": {
        "en": "You build the tools; the tools build the future.",
        "zh": "你创造工具，工具创造未来。",
    },
    "welcome_10": {
        "en": "The unexamined workflow is not worth running.",
        "zh": "未经审视的流程，不值得运行。",
    },
    "welcome_11": {
        "en": "I automate, therefore I am.",
        "zh": "我自动化，故我在。",
    },
    "welcome_12": {
        "en": "One cannot step into the same pipeline twice.",
        "zh": "人不能两次踏入同一条流水线。",
    },
    "welcome_13": {
        "en": "The only constant is change — so automate adaptively.",
        "zh": "唯一不变的是变化——所以要自适应地自动化。",
    },
    "welcome_14": {
        "en": "To do is to be; to automate is to transcend.",
        "zh": "行动即存在；自动化即超越。",
    },
    "welcome_15": {
        "en": "Simplicity is the ultimate sophistication.",
        "zh": "简约是终极的精妙。",
    },
    "welcome_16": {
        "en": "Between stimulus and response, there is a processor.",
        "zh": "在刺激与响应之间，有一个处理器。",
    },
    "welcome_17": {
        "en": "The task you automate today frees the mind of tomorrow.",
        "zh": "今日自动化的任务，是明日自由的心智。",
    },
    "welcome_18": {
        "en": "Knowing the path is not the same as running the pipeline.",
        "zh": "知道路在哪里，不等于跑通了流水线。",
    },
    "welcome_19": {
        "en": "All tasks are impermanent — but their output persists.",
        "zh": "诸行无常——但输出永存。",
    },


    # === AI Execution Generator ===
    "ai_gen_title": {"en": "AI Execution Generator", "zh": "AI 执行生成器"},
    "ai_gen_btn": {"en": "AI Generate", "zh": "AI 生成"},
    "ai_gen_send": {"en": "Send", "zh": "发送"},
    "ai_gen_done": {"en": "Done", "zh": "完成"},
    "ai_gen_cancel": {"en": "Cancel", "zh": "取消"},
    "ai_gen_thinking": {"en": "Thinking...", "zh": "思考中..."},
    "ai_gen_category": {"en": "Category", "zh": "类别"},
    "ai_gen_input_hint": {"en": "Chat with AI: ask about Processors, generate task flows, or modify existing tasks...", "zh": "与 AI 对话：咨询 Processor 用法、生成任务流程、修改现有任务..."},
    "ai_gen_loading": {"en": "Connecting to {provider} ({model})...", "zh": "正在连接 {provider} ({model})..."},
    "ai_gen_loading_short": {"en": "Connecting to {provider}...", "zh": "正在连接 {provider}..."},
    "ai_gen_unknown_provider": {"en": "Provider '{provider}' is not in built-in defaults. Please configure: {missing}\nSupported providers: {supported}", "zh": "Provider '{provider}' 不在内置默认列表中，请补全配置: {missing}\n支持的 Provider: {supported}"},
    "ai_gen_retry_hint": {"en": "Press Enter or Send to retry...", "zh": "按 Enter 或点击发送重试..."},
    "ai_gen_reuse": {"en": "Using existing connection: {provider} ({model}).\nSelect processors and describe your task.", "zh": "复用已有连接：{provider} ({model})。\n选择 Processor 后描述你的需求。"},
    "ai_gen_welcome": {"en": "Connected to {provider} ({model}).\n\nCategory overview:\n\u2022 Selenium \u2014 Browser automation: navigate, click, input, collect, screenshot, iframe, cookies\n\u2022 HTTP \u2014 HTTP requests (GET/POST) and BeautifulSoup HTML parsing\n\u2022 File \u2014 File read/write/move/delete, OCR text extraction, captcha recognition, file monitoring\n\u2022 Excel/CSV \u2014 Read/write Excel and CSV, format conversion\n\u2022 Database \u2014 SQL database access (query, insert, update)\n\u2022 Email \u2014 Send (SMTP) and receive (IMAP) emails with attachments\n\u2022 Paramiko \u2014 SSH commands, SFTP upload/download\n\u2022 DataProcessing \u2014 Collection merge/filter/map/group, encoding, hashing, data masking\n\u2022 JSON \u2014 JSON file read with path extraction\n\u2022 Mouse/GUI \u2014 Mouse click/scroll/position, input dialogs, result display\n\u2022 AI_LLM \u2014 LLM setup and Q&A, MCP tool calling\n\u2022 General \u2014 Wait, conditions (IF_ELSE), jump, run commands, run sub-executions\n\u2022 Zip \u2014 Compress and decompress ZIP files\n\u2022 Javascript \u2014 Execute external JS files\n\u2022 Youtube \u2014 Download YouTube videos\n\nTip: Select needed processors to save tokens, or select all if unsure.", "zh": "\u5df2\u8fde\u63a5 {provider} ({model})\u3002\n\n\u5206\u7c7b\u6982\u89c8\uff1a\n\u2022 Selenium \u2014 \u6d4f\u89c8\u5668\u81ea\u52a8\u5316\uff1a\u5bfc\u822a\u3001\u70b9\u51fb\u3001\u8f93\u5165\u3001\u91c7\u96c6\u3001\u622a\u56fe\u3001iframe\u3001Cookie\n\u2022 HTTP \u2014 HTTP \u8bf7\u6c42 (GET/POST) \u548c BeautifulSoup HTML \u89e3\u6790\n\u2022 File \u2014 \u6587\u4ef6\u8bfb\u5199/\u79fb\u52a8/\u5220\u9664\u3001OCR \u6587\u5b57\u8bc6\u522b\u3001\u9a8c\u8bc1\u7801\u8bc6\u522b\u3001\u6587\u4ef6\u76d1\u63a7\n\u2022 Excel/CSV \u2014 \u8bfb\u5199 Excel \u548c CSV\u3001\u683c\u5f0f\u8f6c\u6362\n\u2022 Database \u2014 SQL \u6570\u636e\u5e93\u8bbf\u95ee\uff08\u67e5\u8be2\u3001\u63d2\u5165\u3001\u66f4\u65b0\uff09\n\u2022 Email \u2014 \u53d1\u9001 (SMTP) \u548c\u63a5\u6536 (IMAP) \u90ae\u4ef6\uff0c\u652f\u6301\u9644\u4ef6\n\u2022 Paramiko \u2014 SSH \u547d\u4ee4\u6267\u884c\u3001SFTP \u4e0a\u4f20/\u4e0b\u8f7d\n\u2022 DataProcessing \u2014 \u96c6\u5408\u5408\u5e76/\u8fc7\u6ee4/\u6620\u5c04/\u5206\u7ec4\u3001\u7f16\u89e3\u7801\u3001\u54c8\u5e0c\u3001\u6570\u636e\u8131\u654f\n\u2022 JSON \u2014 JSON \u6587\u4ef6\u8bfb\u53d6\uff0c\u652f\u6301\u8def\u5f84\u63d0\u53d6\n\u2022 Mouse/GUI \u2014 \u9f20\u6807\u70b9\u51fb/\u6eda\u52a8/\u5b9a\u4f4d\u3001\u8f93\u5165\u5f39\u7a97\u3001\u7ed3\u679c\u5c55\u793a\n\u2022 AI_LLM \u2014 \u5927\u6a21\u578b\u8bbe\u7f6e\u548c\u95ee\u7b54\u3001MCP \u5de5\u5177\u8c03\u7528\n\u2022 General \u2014 \u7b49\u5f85\u3001\u6761\u4ef6\u5206\u652f (IF_ELSE)\u3001\u8df3\u8f6c\u3001\u6267\u884c\u547d\u4ee4\u3001\u8c03\u7528\u5b50\u6267\u884c\n\u2022 Zip \u2014 \u538b\u7f29\u548c\u89e3\u538b ZIP \u6587\u4ef6\n\u2022 Javascript \u2014 \u6267\u884c\u5916\u90e8 JS \u6587\u4ef6\n\u2022 Youtube \u2014 \u4e0b\u8f7d YouTube \u89c6\u9891\n\n\u63d0\u793a\uff1a\u9009\u4e2d\u9700\u8981\u7684 Processor \u53ef\u8282\u7701 Token\uff1b\u4e0d\u786e\u5b9a\u65f6\u53ef\u5168\u9009\uff0c\u8ba9 AI \u6839\u636e\u4f60\u7684\u63cf\u8ff0\u9009\u62e9\u3002"},
    "ai_gen_init_fail": {"en": "Connection failed: {error}\n\nHow to fix:\n1. Open config/petpconfig.yaml\n2. Set ai_provider (e.g. zhipu, deepseek, anthropic)\n3. Set ai_api_key or ensure the env var is exported\n4. Save and retry (Enter or Send button)", "zh": "连接失败：{error}\n\n解决方法：\n1. 打开 config/petpconfig.yaml\n2. 设置 ai_provider（如 zhipu、deepseek、anthropic）\n3. 设置 ai_api_key 或确保对应环境变量已导出\n4. 保存后点击发送重试"},
    "ai_gen_hello_prompt": {"en": "Introduce yourself briefly. What can you help me with? Reply in plain text, not JSON.", "zh": "请简单介绍你自己，你能帮我做什么？用自然语言回复，不要用JSON格式。"},
    "ai_gen_no_config": {"en": "ai_provider is not configured.\n\nOpen config/petpconfig.yaml and set:\n  ai_provider: zhipu  (or deepseek, anthropic, etc.)\n\nThen retry via right-click → AI Assist.", "zh": "ai_provider 未配置。\n\n请打开 config/petpconfig.yaml 设置：\n  ai_provider: zhipu  （或 deepseek、anthropic 等）\n\n保存后通过右键 → AI 协助重试。"},
    "ai_gen_tokens": {"en": "Tokens: {input} in / {output} out", "zh": "Token: {input} 输入 / {output} 输出"},
    "ai_gen_error": {"en": "Error: {msg}", "zh": "错误: {msg}"},
    "ai_gen_invalid_type": {"en": "Warning: unknown processor type '{ptype}'", "zh": "警告: 未知处理器类型 '{ptype}'"},
    "ai_gen_mcp_btn": {"en": "AI", "zh": "AI"},
    "ai_gen_mcp_tip": {"en": "AI generate MCP description", "zh": "AI 生成 MCP 描述"},
    "ai_gen_mcp_title": {"en": "AI Generate MCP Description", "zh": "AI 生成 MCP 描述"},
    "ai_gen_mcp_info": {"en": "Tasks: {task_count} | Input params: {inputs}", "zh": "任务数: {task_count} | 输入参数: {inputs}"},
    "ai_gen_mcp_generating": {"en": "Analyzing tasks and generating description...", "zh": "正在分析任务并生成描述..."},
    "ai_gen_mcp_done": {"en": "✓ Generation complete. Review and apply:", "zh": "✓ 生成完成，请确认："},
    "ai_gen_mcp_empty": {"en": "⚠ No result generated. The model may not have understood the task structure.", "zh": "⚠ 未生成结果，模型可能无法理解当前任务结构。"},
    "ai_gen_mcp_error_status": {"en": "✗ Connection failed", "zh": "✗ 连接失败"},
    "ai_gen_mcp_error_detail": {"en": "Error: {error}\n\nPossible causes:\n• LLM service unavailable or network issue\n• API key expired or invalid\n• Provider not configured correctly\n\nHow to fix:\n1. Check config/petpconfig.yaml (ai_provider, ai_api_key)\n2. Verify the env variable is exported\n3. Close this dialog and retry after fixing", "zh": "错误：{error}\n\n可能原因：\n• LLM 服务不可用或网络问题\n• API Key 过期或无效\n• Provider 配置不正确\n\n解决方法：\n1. 检查 config/petpconfig.yaml（ai_provider、ai_api_key）\n2. 确认环境变量已导出\n3. 关闭此窗口，修复后重试"},
    "ai_gen_mcp_apply": {"en": "Apply", "zh": "应用"},
    "ai_gen_mcp_overwrite": {"en": "MCP description already exists. How do you want to handle it?", "zh": "MCP 描述已存在，如何处理？"},
    "ai_gen_mcp_merge": {"en": "Merge (keep existing, add new)", "zh": "合并（保留已有，补充新的）"},
    "ai_gen_mcp_replace": {"en": "Replace all", "zh": "全部替换"},
    "ai_gen_assist": {"en": "AI Assist", "zh": "AI 协助"},
    "ai_gen_undo": {"en": "Undo", "zh": "撤销"},
    "ai_gen_redo": {"en": "Redo", "zh": "重做"},
    "ai_gen_search": {"en": "Search processor...", "zh": "搜索 Processor..."},
    "ai_error_analyze_btn": {"en": "AI Analyze", "zh": "AI 分析"},
    "ai_error_title": {"en": "AI Error Analysis", "zh": "AI 错误分析"},
    "ai_error_summary": {"en": "Task #{index} {ptype} failed", "zh": "任务 #{index} {ptype} 失败"},
    "ai_error_analyzing": {"en": "Analyzing error...", "zh": "正在分析错误..."},
    "ai_error_ask_analyze": {"en": "Would you like AI to analyze this error?", "zh": "是否让 AI 分析此错误？"},
    "ai_error_done": {"en": "✓ Analysis complete", "zh": "✓ 分析完成"},
    "ai_error_failed": {"en": "✗ Analysis failed", "zh": "✗ 分析失败"},
    "ai_error_open_assist": {"en": "Open in AI Assist", "zh": "在 AI 助手中打开"},
    "ai_error_inject_msg": {"en": "Task #{index} ({ptype}) failed with: {error}\nPlease help analyze and fix.", "zh": "任务 #{index} ({ptype}) 报错：{error}\n请帮助分析并修复。"},
    "ai_error_analysis_label": {"en": "AI Analysis:", "zh": "AI 分析结果："},
    "ai_gen_select_all": {"en": "All", "zh": "全选"},
    "ai_gen_select_none": {"en": "None", "zh": "全不选"},
    "ai_gen_select_all_tip": {"en": "Select all processors", "zh": "选中所有 Processor"},
    "ai_gen_select_none_tip": {"en": "Deselect all processors", "zh": "取消选中所有 Processor"},
    "ai_gen_expand_all_tip": {"en": "Expand all categories", "zh": "展开所有分类"},
    "ai_gen_collapse_all_tip": {"en": "Collapse all categories", "zh": "收起所有分类"},

    # === Processor descriptions — loaded from desc_translations.py ===
}

TRANSLATIONS.update(DESC_TRANSLATIONS)

_current_locale = "zh"


def set_locale(locale: str):
    global _current_locale
    _current_locale = locale if locale in ("en", "zh") else "zh"


def get_locale() -> str:
    return _current_locale


def t(key: str, **kwargs) -> str:
    entry = TRANSLATIONS.get(key)
    if entry is None:
        return key
    text = entry.get(_current_locale) or entry.get("en") or key
    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, IndexError):
            pass
    return text


def get_localized_desc(cls, locale: str = None) -> str:
    if locale is None:
        locale = _current_locale
    name = cls.__name__ if hasattr(cls, '__name__') else cls.__class__.__name__
    if locale == "zh":
        key = f"desc_{name.replace('Processor', '')}"
        entry = TRANSLATIONS.get(key)
        if entry and "zh" in entry:
            return entry["zh"]
    return getattr(cls, 'DESC', '')
