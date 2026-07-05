import json
import threading
import time
from typing import Optional

import wx
import wx.dataview as dv
import wx.lib.scrolledpanel as scrolled

from core.processor import Processor
from i18n.translations import t, get_localized_desc
from mvp.view.PETPTheme import get_theme


class AIGeneratorDialog(wx.Frame):
    # Minimum gap between two successive LLM calls (seconds). Guards against
    # provider RPM caps and user reflex-clicking Send.
    _MIN_SEND_INTERVAL_S: float = 3.0

    def __init__(self, parent, locale: str, on_apply=None):
        super().__init__(
            parent, title=t("ai_gen_title"),
            size=(800, 700),
            style=wx.DEFAULT_FRAME_STYLE | wx.FRAME_FLOAT_ON_PARENT
        )
        self._locale = locale
        self._on_apply = on_apply
        self._generator = None
        self._undo_handler = None
        self._redo_handler = None
        self._input_history = []
        self._history_cursor = -1
        # Monotonic timestamp of the last successful send, for min-interval throttling.
        self._last_send_ts: float = 0.0
        self._theme = get_theme()
        self._category_map = {}
        self._all_items = []
        self._item_type_map = {}
        self._full_desc_map = {}
        # Optional pre-selection: if set, only these processor types are checked
        # on first populate (typically the types referenced by the current
        # Execution). ``None`` keeps the legacy behavior (check all).
        self._initial_selected_processors: Optional[set] = None
        self._first_populate: bool = True
        self._closed: bool = False
        self._build_ui()
        self._bind_events()

    def set_initial_selected_processors(self, processor_types):
        """Pre-select the given processor types on first populate.

        Call BEFORE the tree is populated (i.e. before ``init_generator_async``).
        Pass a set/list of processor type names (e.g. {'GO_TO_PAGE', 'FIND_THEN_CLICK'}).
        """
        if processor_types:
            self._initial_selected_processors = set(processor_types)
            # Reflect the partial selection state on the "select all" checkbox
            # so users see immediately that not everything is checked.
            if hasattr(self, '_cb_select_all'):
                self._cb_select_all.SetValue(False)

    def _build_processor_map(self):
        for ptype in Processor.get_processors():
            try:
                clazz = Processor.get_processor_by_type(ptype)
                cat = clazz.get_category()
                desc = get_localized_desc(clazz, self._locale)
                first_line = next((l.strip() for l in desc.split('\n') if l.strip()), '') if desc else ''
                self._full_desc_map[ptype] = desc
                self._category_map.setdefault(cat, []).append((ptype, first_line))
            except Exception:
                continue

    def _build_ui(self):
        th = self._theme
        panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # --- Vertical splitter: (processor selector area) / (chat area) ---
        self._v_splitter = wx.SplitterWindow(
            panel, style=wx.SP_LIVE_UPDATE | wx.SP_3DSASH
        )
        self._v_splitter.SetMinimumPaneSize(100)

        # Top pane: tree with search
        tree_panel = wx.Panel(self._v_splitter)
        tree_sizer = wx.BoxSizer(wx.VERTICAL)

        # Search row: search + select all checkbox + expand/collapse toggle
        search_row = wx.BoxSizer(wx.HORIZONTAL)
        self._search_text = wx.SearchCtrl(tree_panel, size=(-1, -1))
        self._search_text.SetDescriptiveText(t("ai_gen_search"))
        search_row.Add(self._search_text, 1, wx.EXPAND | wx.RIGHT, 4)

        self._cb_select_all = wx.CheckBox(tree_panel, label=t("ai_gen_select_all"))
        self._cb_select_all.SetValue(True)
        self._cb_select_all.SetToolTip(t("ai_gen_select_all_tip"))
        search_row.Add(self._cb_select_all, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 4)

        self._expanded = True
        self._btn_toggle_expand = wx.Button(tree_panel, label="⊟", size=(28, 24))
        self._btn_toggle_expand.SetToolTip(t("ai_gen_collapse_all_tip"))
        search_row.Add(self._btn_toggle_expand, 0, wx.ALIGN_CENTER_VERTICAL)

        tree_sizer.Add(search_row, 0, wx.EXPAND | wx.BOTTOM, 4)

        self._tree = dv.TreeListCtrl(
            tree_panel, style=dv.TL_CHECKBOX | dv.TL_3STATE
        )
        self._tree.AppendColumn("Processor", width=180)
        self._tree.AppendColumn("Description", width=280)
        # NOTE: intentionally do NOT populate the tree here. The processor map
        # is loaded asynchronously in ``init_generator_async._init``, which
        # then triggers ``_populate_tree`` via ``wx.CallAfter``. Populating
        # here would run against an empty category_map (a no-op that still
        # burns the ``_first_populate`` flag), causing
        # ``set_initial_selected_processors`` to be silently ignored.
        tree_sizer.Add(self._tree, 1, wx.EXPAND)
        tree_panel.SetSizer(tree_sizer)

        # Bottom pane: chat + input splitter
        self._chat_input_splitter = wx.SplitterWindow(
            self._v_splitter, style=wx.SP_LIVE_UPDATE | wx.SP_3DSASH
        )
        self._chat_input_splitter.SetMinimumPaneSize(36)

        # Chat area (top of bottom pane)
        self._chat_panel = scrolled.ScrolledPanel(
            self._chat_input_splitter, style=wx.VSCROLL | wx.ALWAYS_SHOW_SB
        )
        self._chat_panel.SetBackgroundColour(wx.Colour(*th.log_bg))
        self._chat_sizer = wx.BoxSizer(wx.VERTICAL)
        self._chat_panel.SetSizer(self._chat_sizer)
        self._chat_panel.SetupScrolling(scroll_x=False, rate_y=20)

        # Input area (bottom of bottom pane)
        input_panel = wx.Panel(self._chat_input_splitter)
        input_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._input_text = wx.TextCtrl(
            input_panel, style=wx.TE_MULTILINE | wx.TE_PROCESS_ENTER
        )
        self._input_text.SetMinSize((-1, 36))
        self._input_text.SetBackgroundColour(wx.Colour(*th.log_search_bg))
        self._input_text.SetForegroundColour(wx.Colour(*th.log_search_fg))
        self._input_text.Disable()
        input_sizer.Add(self._input_text, 1, wx.EXPAND)
        self._btn_send = wx.Button(input_panel, label=t("ai_gen_send"), size=(50, -1))
        self._btn_send.SetBackgroundColour(wx.Colour(*th.accent))
        self._btn_send.SetForegroundColour(wx.WHITE)
        input_sizer.Add(self._btn_send, 0, wx.LEFT | wx.EXPAND, 4)
        input_panel.SetSizer(input_sizer)

        self._chat_input_splitter.SplitHorizontally(self._chat_panel, input_panel, -80)

        self._v_splitter.SplitHorizontally(tree_panel, self._chat_input_splitter, 280)

        main_sizer.Add(self._v_splitter, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 8)

        # --- Bottom row ---
        bottom_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._token_label = wx.StaticText(panel, label="")
        self._token_label.SetForegroundColour(wx.Colour(120, 120, 120))
        bottom_sizer.Add(self._token_label, 1, wx.ALIGN_CENTER_VERTICAL)
        self._btn_undo = wx.Button(panel, label=t("ai_gen_undo"), size=(50, -1))
        self._btn_redo = wx.Button(panel, label=t("ai_gen_redo"), size=(50, -1))
        self._btn_done = wx.Button(panel, label=t("ai_gen_done"), size=(50, -1))
        bottom_sizer.Add(self._btn_undo, 0, wx.RIGHT, 2)
        bottom_sizer.Add(self._btn_redo, 0, wx.RIGHT, 2)
        bottom_sizer.Add(self._btn_done, 0)
        main_sizer.Add(bottom_sizer, 0, wx.EXPAND | wx.ALL, 8)

        panel.SetSizer(main_sizer)

    def _populate_tree(self, filter_text=''):
        if self._is_dead():
            return
        self._tree.DeleteAllItems()
        self._tree_item_map = {}
        root = self._tree.GetRootItem()
        filter_lower = filter_text.lower()

        # First populate honors ``_initial_selected_processors`` (if set) to
        # pre-check only the processors referenced by the current Execution.
        # Subsequent populates (after a search filter, etc.) preserve whatever
        # the user currently has checked — see ``_on_search`` which snapshots
        # and reapplies ``checked_before`` around the repopulate.
        use_initial_filter = (
            self._first_populate
            and self._initial_selected_processors is not None
        )
        self._first_populate = False

        for cat in sorted(self._category_map.keys()):
            processors = self._category_map[cat]
            matched = [(p, d) for p, d in processors
                       if not filter_lower or filter_lower in p.lower() or filter_lower in d.lower()]
            if not matched:
                continue
            cat_item = self._tree.AppendItem(root, f"{cat} ({len(matched)})")
            self._tree_item_map[cat_item] = ('category', cat)
            for ptype, desc in sorted(matched, key=lambda x: x[0]):
                p_item = self._tree.AppendItem(cat_item, ptype)
                self._tree.SetItemText(p_item, 1, desc)
                self._tree_item_map[p_item] = ('processor', ptype)
                if use_initial_filter:
                    if ptype in self._initial_selected_processors:
                        self._tree.CheckItem(p_item)
                else:
                    self._tree.CheckItem(p_item)
                full_desc = self._full_desc_map.get(ptype, '')
                if full_desc:
                    lines = full_desc.strip().split('\n')
                    first_non_empty_idx = next((i for i, l in enumerate(lines) if l.strip()), 0)
                    for line in lines[first_non_empty_idx + 1:]:
                        stripped = line.strip()
                        if stripped:
                            desc_item = self._tree.AppendItem(p_item, '')
                            self._tree.SetItemText(desc_item, 1, stripped)
                            self._tree_item_map[desc_item] = ('desc', ptype)
            self._tree.Expand(cat_item)

    def _bind_events(self):
        self._btn_send.Bind(wx.EVT_BUTTON, self._on_send)
        self._input_text.Bind(wx.EVT_TEXT_ENTER, self._on_send)
        self._input_text.Bind(wx.EVT_KEY_DOWN, self._on_input_key_down)
        self._btn_done.Bind(wx.EVT_BUTTON, self._on_done)
        self._btn_undo.Bind(wx.EVT_BUTTON, self._on_undo)
        self._btn_redo.Bind(wx.EVT_BUTTON, self._on_redo)
        self._cb_select_all.Bind(wx.EVT_CHECKBOX, self._on_toggle_select_all)
        self._btn_toggle_expand.Bind(wx.EVT_BUTTON, self._on_toggle_expand)
        self._search_text.Bind(wx.EVT_TEXT, self._on_search)
        self._tree.Bind(dv.EVT_TREELIST_ITEM_CHECKED, self._on_tree_check)
        self.Bind(wx.EVT_CLOSE, self._on_close)

    def _on_close(self, evt):
        # Mark the dialog as dead so late ``wx.CallAfter`` callbacks from the
        # background init thread short-circuit instead of touching freed widgets.
        self._closed = True
        self._cleanup_timers()
        evt.Skip()

    def _is_dead(self) -> bool:
        """True once the dialog has been closed/destroyed.

        Late callbacks scheduled via ``wx.CallAfter`` before the user closed
        the dialog can fire after wx has already released the C++ widgets;
        every method that touches ``self._chat_panel`` / ``self._tree`` /
        ``self._input_text`` etc. from a ``CallAfter`` should guard on this.
        """
        return getattr(self, '_closed', False) or not self

    def _on_toggle_select_all(self, evt):
        checked = self._cb_select_all.GetValue()
        state = wx.CHK_CHECKED if checked else wx.CHK_UNCHECKED
        root = self._tree.GetRootItem()
        cat_item = self._tree.GetFirstChild(root)
        while cat_item.IsOk():
            self._check_category_processors(cat_item, state)
            cat_item = self._tree.GetNextSibling(cat_item)

    def _on_toggle_expand(self, evt):
        root = self._tree.GetRootItem()
        cat_item = self._tree.GetFirstChild(root)
        if self._expanded:
            while cat_item.IsOk():
                self._tree.Collapse(cat_item)
                cat_item = self._tree.GetNextSibling(cat_item)
            self._expanded = False
            self._btn_toggle_expand.SetLabel("⊞")
            self._btn_toggle_expand.SetToolTip(t("ai_gen_expand_all_tip"))
        else:
            while cat_item.IsOk():
                self._tree.Expand(cat_item)
                cat_item = self._tree.GetNextSibling(cat_item)
            self._expanded = True
            self._btn_toggle_expand.SetLabel("⊟")
            self._btn_toggle_expand.SetToolTip(t("ai_gen_collapse_all_tip"))

    def _on_search(self, evt):
        checked_before = set(self.get_selected_processors())
        self._populate_tree(self._search_text.GetValue().strip())
        root = self._tree.GetRootItem()
        cat_item = self._tree.GetFirstChild(root)
        while cat_item.IsOk():
            p_item = self._tree.GetFirstChild(cat_item)
            while p_item.IsOk():
                info = self._tree_item_map.get(p_item)
                if info and info[0] == 'processor':
                    if info[1] in checked_before:
                        self._tree.CheckItem(p_item)
                    else:
                        self._tree.UncheckItem(p_item)
                p_item = self._tree.GetNextSibling(p_item)
            self._tree.UpdateItemParentStateRecursively(cat_item)
            cat_item = self._tree.GetNextSibling(cat_item)

    def _on_tree_check(self, evt):
        item = evt.GetItem()
        info = self._tree_item_map.get(item)
        if info and info[0] == 'desc':
            self._tree.UncheckItem(item)
            return
        if info and info[0] == 'category':
            state = self._tree.GetCheckedState(item)
            new_state = wx.CHK_CHECKED if state == wx.CHK_CHECKED else wx.CHK_UNCHECKED
            self._check_category_processors(item, new_state)
        self._sync_select_all_checkbox()

    def _check_category_processors(self, cat_item, state):
        p_item = self._tree.GetFirstChild(cat_item)
        while p_item.IsOk():
            info = self._tree_item_map.get(p_item)
            if info and info[0] == 'processor':
                if state == wx.CHK_CHECKED:
                    self._tree.CheckItem(p_item)
                else:
                    self._tree.UncheckItem(p_item)
            p_item = self._tree.GetNextSibling(p_item)

    def _sync_select_all_checkbox(self):
        all_processors = self.get_selected_processors()
        total = sum(1 for info in self._tree_item_map.values() if info[0] == 'processor')
        self._cb_select_all.SetValue(len(all_processors) == total)

    def set_generator(self, generator):
        self._generator = generator

    def init_generator_async(self, provider, api_key, base_url, model, max_tokens=None, max_request_tokens=None):
        from core.ai.ExecutionGenerator import ExecutionGenerator
        self._init_params = (provider, api_key, base_url, model, max_tokens, max_request_tokens)
        self._start_loading_animation(t("ai_gen_loading_short", provider=provider))
        self._btn_send.Disable()

        def _init():
            try:
                self._build_processor_map()
                wx.CallAfter(self._populate_tree)
                generator = ExecutionGenerator([], self._locale)
                generator.init_client(provider, api_key, base_url, model, max_tokens, max_request_tokens)
                generator.validate_connection()
                actual_model = generator._model
                wx.CallAfter(self._on_init_success, generator, provider, actual_model)
            except Exception as e:
                wx.CallAfter(self._on_init_failure, str(e))

        thread = threading.Thread(target=_init, daemon=True)
        thread.start()

    def _on_init_success(self, generator, provider, model):
        if self._is_dead():
            return
        self._generator = generator
        self._stop_loading_animation()
        self._input_text.Enable()
        self._btn_send.Enable()
        self._input_text.SetFocus()
        self._add_message(t("ai_gen_welcome", provider=provider, model=model), is_user=False)

    def _on_init_failure(self, error_msg):
        if self._is_dead():
            return
        self._stop_loading_animation()
        self._add_message(t("ai_gen_init_fail", error=error_msg), is_user=False)
        self._input_text.Enable()
        self._btn_send.Enable()
        self._input_text.SetHint(t("ai_gen_retry_hint"))

    _CLIMB_FRAMES = [
        "🤔",
        "🧐",
        "💭",
        "🚀",
        "✨",
    ]

    def _start_loading_animation(self, message):
        self._anim_frame = 0
        self._anim_message = message
        self._anim_panel = wx.Panel(self._chat_panel)
        self._anim_panel.SetBackgroundColour(wx.Colour(255, 243, 205))
        self._anim_panel.SetName("thinking_panel")
        sizer = wx.BoxSizer(wx.VERTICAL)
        self._anim_label = wx.StaticText(self._anim_panel, label="")
        self._anim_label.SetForegroundColour(wx.Colour(80, 60, 0))
        font = self._anim_label.GetFont()
        font.SetPointSize(font.GetPointSize() + 6)
        self._anim_label.SetFont(font)
        sizer.Add(self._anim_label, 0, wx.ALL, 8)
        self._anim_panel.SetSizer(sizer)
        self._chat_sizer.Add(self._anim_panel, 0, wx.ALL | wx.EXPAND, 4)
        self._chat_panel.Layout()
        self._chat_panel.FitInside()

        self._anim_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self._on_anim_tick, self._anim_timer)
        self._anim_timer.Start(400)
        self._on_anim_tick(None)

    def _on_anim_tick(self, evt):
        if not hasattr(self, '_anim_label') or not self._anim_label:
            return
        frame = self._CLIMB_FRAMES[self._anim_frame % len(self._CLIMB_FRAMES)]
        text = f"{frame} {self._anim_message}"
        self._anim_label.SetLabel(text)
        self._anim_panel.Layout()
        self._chat_panel.Layout()
        self._chat_panel.FitInside()
        self._anim_frame += 1

    def _stop_loading_animation(self):
        if hasattr(self, '_anim_timer') and self._anim_timer.IsRunning():
            self._anim_timer.Stop()
        self._remove_thinking()

    def set_undo_redo_handlers(self, on_undo, on_redo):
        self._undo_handler = on_undo
        self._redo_handler = on_redo

    def get_selected_processors(self) -> list:
        selected = []
        root = self._tree.GetRootItem()
        cat_item = self._tree.GetFirstChild(root)
        while cat_item.IsOk():
            p_item = self._tree.GetFirstChild(cat_item)
            while p_item.IsOk():
                if self._tree.GetCheckedState(p_item) == wx.CHK_CHECKED:
                    info = self._tree_item_map.get(p_item)
                    if info and info[0] == 'processor':
                        selected.append(info[1])
                p_item = self._tree.GetNextSibling(p_item)
            cat_item = self._tree.GetNextSibling(cat_item)
        return selected

    def get_selected_categories(self) -> list:
        return list(self._category_map.keys())

    def _on_send(self, evt):
        msg = self._input_text.GetValue().strip()
        if not msg:
            return
        if self._generator is None:
            if hasattr(self, '_init_params'):
                self._input_text.Clear()
                p = self._init_params
                self.init_generator_async(*p)
            return

        # Throttle: enforce a minimum gap between two successive LLM calls.
        elapsed = time.monotonic() - self._last_send_ts
        if elapsed < self._MIN_SEND_INTERVAL_S:
            wait_s = self._MIN_SEND_INTERVAL_S - elapsed
            self._add_message(t("ai_gen_throttle_wait").format(sec=f"{wait_s:.1f}"), is_user=False)
            return

        self._generator.update_filter(self.get_selected_processors())
        self._input_history.append(msg)
        if len(self._input_history) > 20:
            self._input_history.pop(0)
        self._history_cursor = -1
        current_tasks = self._on_apply('get_tasks') if self._on_apply else None
        self._input_text.Clear()
        self._input_text.Disable()
        self._btn_send.Disable()
        self._add_message(msg, is_user=True)
        self._add_message(t("ai_gen_thinking"), is_user=False, is_thinking=True)
        self._last_send_ts = time.monotonic()

        thread = threading.Thread(target=self._do_chat, args=(msg, current_tasks), daemon=True)
        thread.start()

    def _on_input_key_down(self, evt):
        key = evt.GetKeyCode()
        if key == wx.WXK_UP and self._input_history:
            if self._history_cursor == -1:
                self._history_cursor = len(self._input_history) - 1
            elif self._history_cursor > 0:
                self._history_cursor -= 1
            self._input_text.SetValue(self._input_history[self._history_cursor])
            self._input_text.SetInsertionPointEnd()
        elif key == wx.WXK_DOWN and self._input_history:
            if self._history_cursor == -1:
                evt.Skip()
                return
            if self._history_cursor < len(self._input_history) - 1:
                self._history_cursor += 1
                self._input_text.SetValue(self._input_history[self._history_cursor])
            else:
                self._history_cursor = -1
                self._input_text.Clear()
            self._input_text.SetInsertionPointEnd()
        else:
            evt.Skip()

    def _do_chat(self, msg, current_tasks):
        result = self._generator.chat(msg, current_tasks)
        wx.CallAfter(self._handle_response, result)

    def _handle_response(self, result):
        if self._is_dead():
            return
        self._remove_thinking()
        self._input_text.Enable()
        self._btn_send.Enable()
        self._input_text.SetFocus()

        action = result.get('action', 'text')

        if action == 'ask':
            questions = result.get('questions', [])
            text = "\n".join(f"• {q}" for q in questions)
            self._add_message(text, is_user=False)

        elif action == 'generate':
            tasks = self._generator.build_tasks(result.get('tasks', []))
            loops = self._generator.build_loops(result.get('loops', []))
            warnings = self._generator.validate_tasks(tasks)
            if self._on_apply:
                self._on_apply('apply', tasks, loops)
            summary = self._format_task_summary(tasks, warnings)
            self._add_message(summary, is_user=False)

        elif action == 'modify':
            current_tasks = self._on_apply('get_tasks') if self._on_apply else []
            new_tasks = self._generator.apply_modifications(
                current_tasks, result.get('operations', [])
            )
            warnings = self._generator.validate_tasks(new_tasks)
            if self._on_apply:
                self._on_apply('apply', new_tasks, None)
            ops = result.get('operations', [])
            summary = self._format_modify_summary(ops, new_tasks, warnings)
            self._add_message(summary, is_user=False)

        else:
            self._add_message(result.get('content', ''), is_user=False)

        prompt_t, comp_t = self._generator.get_token_usage()
        self._token_label.SetLabel(t("ai_gen_tokens", input=prompt_t, output=comp_t))

    def _format_task_summary(self, tasks, warnings):
        lines = [f"✓ {len(tasks)} tasks:"]
        for i, tk in enumerate(tasks, 1):
            desc = self._brief_input(tk.input)
            lines.append(f"  {i}. {tk.type}  {desc}")
        if warnings:
            lines.append("")
            lines.extend(warnings)
        return "\n".join(lines)

    def _format_modify_summary(self, operations, new_tasks, warnings):
        lines = []
        for op_dict in operations:
            op = op_dict.get('op', '')
            if op == 'insert':
                after = op_dict.get('after', 0)
                inserted = op_dict.get('tasks', [])
                for t_dict in inserted:
                    desc = self._brief_input(json.dumps(t_dict.get('input', {}), ensure_ascii=False))
                    lines.append(f"+ insert after #{after}: {t_dict.get('type', '')}  {desc}")
            elif op == 'delete':
                idx = op_dict.get('index', 0)
                lines.append(f"- delete #{idx}")
            elif op == 'replace':
                idx = op_dict.get('index', 0)
                t_dict = op_dict.get('task', {})
                desc = self._brief_input(json.dumps(t_dict.get('input', {}), ensure_ascii=False))
                lines.append(f"~ replace #{idx}: {t_dict.get('type', '')}  {desc}")
        lines.append(f"✓ {len(new_tasks)} tasks total")
        if warnings:
            lines.append("")
            lines.extend(warnings)
        return "\n".join(lines)

    def _brief_input(self, input_str):
        if not input_str or input_str == '{}':
            return ''
        if len(input_str) > 60:
            return input_str[:57] + '...'
        return input_str

    def _add_message(self, text, is_user=False, is_thinking=False):
        th = self._theme
        msg_panel = wx.Panel(self._chat_panel)
        if is_user:
            bg = wx.Colour(
                min(255, th.accent[0] + 120),
                min(255, th.accent[1] + 120),
                min(255, th.accent[2] + 120),
            )
            fg = wx.Colour(20, 20, 20)
        elif is_thinking:
            bg = wx.Colour(255, 243, 205)
            fg = wx.Colour(80, 60, 0)
        else:
            bg = wx.Colour(*th.log_search_bg)
            fg = wx.Colour(*th.log_search_fg)
        msg_panel.SetBackgroundColour(bg)
        if is_thinking:
            msg_panel.SetName("thinking_panel")

        sizer = wx.BoxSizer(wx.VERTICAL)
        text_ctrl = wx.TextCtrl(
            msg_panel, value=text,
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.BORDER_NONE | wx.TE_NO_VSCROLL
        )
        text_ctrl.SetBackgroundColour(bg)
        text_ctrl.SetForegroundColour(fg)
        text_ctrl.Bind(wx.EVT_MOUSEWHEEL, self._on_chat_mousewheel)
        msg_panel.Bind(wx.EVT_MOUSEWHEEL, self._on_chat_mousewheel)
        line_count = text.count('\n') + 1
        char_width = text_ctrl.GetCharWidth()
        panel_width = max(200, self._chat_panel.GetClientSize().width - 56)
        wrap_lines = sum((len(line) * char_width // panel_width + 1) for line in text.split('\n'))
        height = max(wrap_lines, line_count) * (text_ctrl.GetCharHeight() + 2) + 4
        text_ctrl.SetMinSize((panel_width, height))
        sizer.Add(text_ctrl, 0, wx.ALL | wx.EXPAND, 6)
        msg_panel.SetSizer(sizer)

        self._chat_sizer.Add(msg_panel, 0, wx.ALL | wx.EXPAND, 4)
        self._chat_panel.Layout()
        self._chat_panel.FitInside()
        self._chat_panel.SetupScrolling(scroll_x=False, rate_y=20, scrollToTop=False)
        sx, sy = self._chat_panel.GetScrollPixelsPerUnit()
        vs_y = self._chat_panel.GetVirtualSize()[1]
        if sy > 0:
            self._chat_panel.Scroll(-1, vs_y // sy)

    def _remove_thinking(self):
        for child in self._chat_panel.GetChildren():
            if child.GetName() == "thinking_panel":
                child.Destroy()
                break
        self._chat_panel.Layout()
        self._chat_panel.FitInside()

    def _on_chat_mousewheel(self, evt):
        self._chat_panel.GetEventHandler().ProcessEvent(evt)

    def _on_done(self, evt):
        self._cleanup_timers()
        self.Close()

    def _cleanup_timers(self):
        if hasattr(self, '_anim_timer') and self._anim_timer.IsRunning():
            self._anim_timer.Stop()

    def _on_undo(self, evt):
        if self._undo_handler:
            self._undo_handler()

    def _on_redo(self, evt):
        if self._redo_handler:
            self._redo_handler()
