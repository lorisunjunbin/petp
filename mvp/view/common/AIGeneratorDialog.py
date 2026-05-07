import threading
import wx
import wx.lib.scrolledpanel as scrolled

from core.processor import Processor
from i18n.translations import t
from mvp.view.PETPTheme import get_theme


class AIGeneratorDialog(wx.Frame):

    def __init__(self, parent, locale: str, on_apply=None):
        super().__init__(
            parent, title=t("ai_gen_title"),
            size=(450, 620),
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
        self._build_ui()
        self._bind_events()

    def _build_ui(self):
        th = self._theme
        panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Category selector
        cat_label = wx.StaticText(panel, label=t("ai_gen_category"))
        cat_label.SetFont(cat_label.GetFont().Bold())
        main_sizer.Add(cat_label, 0, wx.LEFT | wx.TOP, 10)

        categories = sorted(set(
            Processor.get_processor_by_type(p).get_category()
            for p in Processor.get_processors()
        ))
        self._category_list = wx.CheckListBox(panel, choices=categories)
        for i, cat in enumerate(categories):
            if cat in ('Selenium', 'HTTP', 'General'):
                self._category_list.Check(i, True)
        main_sizer.Add(self._category_list, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        # Chat area
        self._chat_panel = scrolled.ScrolledPanel(panel)
        chat_bg = wx.Colour(*th.log_bg)
        self._chat_panel.SetBackgroundColour(chat_bg)
        self._chat_sizer = wx.BoxSizer(wx.VERTICAL)
        self._chat_panel.SetSizer(self._chat_sizer)
        self._chat_panel.SetupScrolling(scroll_x=False)
        main_sizer.Add(self._chat_panel, 3, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)

        # Input area
        input_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._input_text = wx.TextCtrl(
            panel, style=wx.TE_MULTILINE | wx.TE_PROCESS_ENTER, size=(-1, 50)
        )
        self._input_text.SetHint(t("ai_gen_input_hint"))
        input_sizer.Add(self._input_text, 1, wx.EXPAND)

        self._btn_send = wx.Button(panel, label=t("ai_gen_send"), size=(60, 50))
        self._btn_send.SetBackgroundColour(wx.Colour(*th.accent))
        self._btn_send.SetForegroundColour(wx.WHITE)
        input_sizer.Add(self._btn_send, 0, wx.LEFT, 4)
        main_sizer.Add(input_sizer, 0, wx.EXPAND | wx.ALL, 10)

        # Token display
        self._token_label = wx.StaticText(panel, label="")
        self._token_label.SetForegroundColour(wx.Colour(120, 120, 120))
        main_sizer.Add(self._token_label, 0, wx.LEFT | wx.BOTTOM, 10)

        # Bottom buttons
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._btn_done = wx.Button(panel, label=t("ai_gen_done"))
        btn_sizer.Add(self._btn_done, 0)
        btn_sizer.AddStretchSpacer()
        self._btn_undo = wx.Button(panel, label=t("ai_gen_undo"), size=(60, -1))
        self._btn_redo = wx.Button(panel, label=t("ai_gen_redo"), size=(60, -1))
        btn_sizer.Add(self._btn_undo, 0, wx.RIGHT, 4)
        btn_sizer.Add(self._btn_redo, 0)
        main_sizer.Add(btn_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

        panel.SetSizer(main_sizer)

    def _bind_events(self):
        self._btn_send.Bind(wx.EVT_BUTTON, self._on_send)
        self._input_text.Bind(wx.EVT_TEXT_ENTER, self._on_send)
        self._input_text.Bind(wx.EVT_KEY_DOWN, self._on_input_key_down)
        self._btn_done.Bind(wx.EVT_BUTTON, self._on_done)
        self._btn_undo.Bind(wx.EVT_BUTTON, self._on_undo)
        self._btn_redo.Bind(wx.EVT_BUTTON, self._on_redo)

    def set_generator(self, generator):
        self._generator = generator

    def set_undo_redo_handlers(self, on_undo, on_redo):
        self._undo_handler = on_undo
        self._redo_handler = on_redo

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
        import json
        lines = [f"✓ {len(tasks)} tasks:"]
        for i, tk in enumerate(tasks, 1):
            desc = self._brief_input(tk.input)
            lines.append(f"  {i}. {tk.type}  {desc}")
        if warnings:
            lines.append("")
            lines.extend(warnings)
        return "\n".join(lines)

    def _format_modify_summary(self, operations, new_tasks, warnings):
        import json
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
            bg = wx.Colour(*th.accent, 60)
            bg = wx.Colour(
                min(255, th.accent[0] + 120),
                min(255, th.accent[1] + 120),
                min(255, th.accent[2] + 120),
            )
        elif is_thinking:
            bg = wx.Colour(255, 243, 205)
        else:
            bg = wx.Colour(*th.log_search_bg)
        msg_panel.SetBackgroundColour(bg)
        if is_thinking:
            msg_panel.SetName("thinking_panel")

        sizer = wx.BoxSizer(wx.VERTICAL)
        text_ctrl = wx.TextCtrl(
            msg_panel, value=text,
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.BORDER_NONE | wx.TE_NO_VSCROLL
        )
        text_ctrl.SetBackgroundColour(bg)
        fg = wx.Colour(*th.log_fg) if not is_thinking else wx.Colour(80, 60, 0)
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

    def get_selected_categories(self) -> list:
        checked = self._category_list.GetCheckedItems()
        return [self._category_list.GetString(i) for i in checked]

    def _on_done(self, evt):
        self.Close()

    def _on_undo(self, evt):
        if self._undo_handler:
            self._undo_handler()

    def _on_redo(self, evt):
        if self._redo_handler:
            self._redo_handler()
