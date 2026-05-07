import json
import threading
import wx
import wx.lib.scrolledpanel as scrolled

from core.processor import Processor
from i18n.translations import t, get_localized_desc
from mvp.view.PETPTheme import get_theme


class AIGeneratorDialog(wx.Frame):

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
        self._theme = get_theme()
        self._category_map = {}
        self._all_items = []
        self._item_type_map = {}
        self._full_desc_map = {}
        self._build_processor_map()
        self._build_ui()
        self._bind_events()

    def _build_processor_map(self):
        for ptype in Processor.get_processors():
            try:
                clazz = Processor.get_processor_by_type(ptype)
                cat = clazz.get_category()
                desc = get_localized_desc(clazz, self._locale)
                first_line = desc.split('\n')[0].strip() if desc else ''
                self._full_desc_map[ptype] = desc
                self._category_map.setdefault(cat, []).append((ptype, first_line))
            except Exception:
                continue

    def _build_ui(self):
        th = self._theme
        panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # --- Top row: label + search + buttons ---
        top_sizer = wx.BoxSizer(wx.HORIZONTAL)
        cat_label = wx.StaticText(panel, label=t("ai_gen_category"))
        cat_label.SetFont(cat_label.GetFont().Bold())
        top_sizer.Add(cat_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 8)

        self._search_text = wx.SearchCtrl(panel, size=(180, -1))
        self._search_text.SetDescriptiveText(t("ai_gen_search"))
        top_sizer.Add(self._search_text, 1, wx.EXPAND | wx.RIGHT, 4)

        self._btn_select_all = wx.Button(panel, label=t("ai_gen_select_all"), size=(60, -1))
        self._btn_select_none = wx.Button(panel, label=t("ai_gen_select_none"), size=(60, -1))
        top_sizer.Add(self._btn_select_all, 0, wx.RIGHT, 2)
        top_sizer.Add(self._btn_select_none, 0)
        main_sizer.Add(top_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 8)

        # --- Processor list (left) + DESC detail (right) ---
        selector_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self._proc_list = wx.CheckListBox(panel)
        self._populate_list()
        selector_sizer.Add(self._proc_list, 3, wx.EXPAND | wx.RIGHT, 4)

        self._desc_panel = wx.TextCtrl(
            panel, style=wx.TE_MULTILINE | wx.TE_READONLY
        )
        self._desc_panel.SetBackgroundColour(wx.Colour(*th.log_bg))
        self._desc_panel.SetForegroundColour(wx.Colour(*th.log_fg))
        selector_sizer.Add(self._desc_panel, 2, wx.EXPAND)

        main_sizer.Add(selector_sizer, 2, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 8)

        # --- Chat area ---
        self._chat_panel = scrolled.ScrolledPanel(panel)
        self._chat_panel.SetBackgroundColour(wx.Colour(*th.log_bg))
        self._chat_sizer = wx.BoxSizer(wx.VERTICAL)
        self._chat_panel.SetSizer(self._chat_sizer)
        self._chat_panel.SetupScrolling(scroll_x=False)
        main_sizer.Add(self._chat_panel, 3, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 8)

        # --- Input area ---
        input_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._input_text = wx.TextCtrl(
            panel, style=wx.TE_MULTILINE | wx.TE_PROCESS_ENTER, size=(-1, 36)
        )
        self._input_text.SetHint(t("ai_gen_input_hint"))
        input_sizer.Add(self._input_text, 1, wx.EXPAND)
        self._btn_send = wx.Button(panel, label=t("ai_gen_send"), size=(50, 36))
        self._btn_send.SetBackgroundColour(wx.Colour(*th.accent))
        self._btn_send.SetForegroundColour(wx.WHITE)
        input_sizer.Add(self._btn_send, 0, wx.LEFT, 4)
        main_sizer.Add(input_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 8)

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

    def _populate_list(self, filter_text=''):
        self._proc_list.Clear()
        self._all_items = []
        self._item_type_map = {}
        filter_lower = filter_text.lower()

        for cat in sorted(self._category_map.keys()):
            processors = self._category_map[cat]
            matched = [(p, d) for p, d in processors
                       if not filter_lower or filter_lower in p.lower() or filter_lower in d.lower()]
            if not matched:
                continue
            cat_label = f"▸ {cat} ({len(matched)})"
            idx = self._proc_list.Append(cat_label)
            self._all_items.append(('category', cat))
            self._item_type_map[idx] = ('category', cat)

            for ptype, desc in sorted(matched, key=lambda x: x[0]):
                p_label = f"    {ptype} — {desc}" if desc else f"    {ptype}"
                idx = self._proc_list.Append(p_label)
                self._all_items.append(('processor', ptype))
                self._item_type_map[idx] = ('processor', ptype)
                self._proc_list.Check(idx, True)

    def _bind_events(self):
        self._btn_send.Bind(wx.EVT_BUTTON, self._on_send)
        self._input_text.Bind(wx.EVT_TEXT_ENTER, self._on_send)
        self._input_text.Bind(wx.EVT_KEY_DOWN, self._on_input_key_down)
        self._btn_done.Bind(wx.EVT_BUTTON, self._on_done)
        self._btn_undo.Bind(wx.EVT_BUTTON, self._on_undo)
        self._btn_redo.Bind(wx.EVT_BUTTON, self._on_redo)
        self._btn_select_all.Bind(wx.EVT_BUTTON, self._on_select_all)
        self._btn_select_none.Bind(wx.EVT_BUTTON, self._on_select_none)
        self._search_text.Bind(wx.EVT_TEXT, self._on_search)
        self._proc_list.Bind(wx.EVT_CHECKLISTBOX, self._on_check_item)
        self._proc_list.Bind(wx.EVT_LISTBOX, self._on_select_item)

    def _on_select_all(self, evt):
        for i in range(self._proc_list.GetCount()):
            if self._item_type_map.get(i, ('',))[0] == 'processor':
                self._proc_list.Check(i, True)

    def _on_select_none(self, evt):
        for i in range(self._proc_list.GetCount()):
            self._proc_list.Check(i, False)

    def _on_search(self, evt):
        checked_before = set(self.get_selected_processors())
        self._populate_list(self._search_text.GetValue().strip())
        for i in range(self._proc_list.GetCount()):
            item_info = self._item_type_map.get(i)
            if item_info and item_info[0] == 'processor':
                self._proc_list.Check(i, item_info[1] in checked_before)

    def _on_check_item(self, evt):
        idx = evt.GetInt()
        item_info = self._item_type_map.get(idx)
        if not item_info:
            return
        if item_info[0] == 'category':
            checked = self._proc_list.IsChecked(idx)
            for i in range(idx + 1, self._proc_list.GetCount()):
                info = self._item_type_map.get(i)
                if not info or info[0] == 'category':
                    break
                self._proc_list.Check(i, checked)

    def _on_select_item(self, evt):
        idx = evt.GetInt()
        item_info = self._item_type_map.get(idx)
        if item_info and item_info[0] == 'processor':
            ptype = item_info[1]
            full_desc = self._full_desc_map.get(ptype, '')
            self._desc_panel.SetValue(f"{ptype}\n{'─' * 30}\n{full_desc}")
        elif item_info and item_info[0] == 'category':
            cat = item_info[1]
            procs = self._category_map.get(cat, [])
            lines = [f"{cat} ({len(procs)} processors)", '─' * 30]
            for ptype, desc in sorted(procs, key=lambda x: x[0]):
                lines.append(f"• {ptype} — {desc}")
            self._desc_panel.SetValue('\n'.join(lines))

    def set_generator(self, generator):
        self._generator = generator

    def set_undo_redo_handlers(self, on_undo, on_redo):
        self._undo_handler = on_undo
        self._redo_handler = on_redo

    def get_selected_processors(self) -> list:
        selected = []
        for i in range(self._proc_list.GetCount()):
            if self._proc_list.IsChecked(i):
                item_info = self._item_type_map.get(i)
                if item_info and item_info[0] == 'processor':
                    selected.append(item_info[1])
        return selected

    def get_selected_categories(self) -> list:
        return list(self._category_map.keys())

    def _on_send(self, evt):
        msg = self._input_text.GetValue().strip()
        if not msg or self._generator is None:
            return
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
        self._chat_panel.Scroll(-1, self._chat_panel.GetVirtualSize()[1])

    def _remove_thinking(self):
        for child in self._chat_panel.GetChildren():
            if child.GetName() == "thinking_panel":
                child.Destroy()
                break
        self._chat_panel.Layout()
        self._chat_panel.FitInside()

    def _on_done(self, evt):
        self.Close()

    def _on_undo(self, evt):
        if self._undo_handler:
            self._undo_handler()

    def _on_redo(self, evt):
        if self._redo_handler:
            self._redo_handler()
