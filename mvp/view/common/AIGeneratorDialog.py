import threading
import wx
import wx.lib.scrolledpanel as scrolled

from core.processor import Processor
from i18n.translations import t


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
        self._build_ui()
        self._bind_events()

    def _build_ui(self):
        panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Category selector with splitter
        cat_label = wx.StaticText(panel, label=t("ai_gen_category"))
        main_sizer.Add(cat_label, 0, wx.LEFT | wx.TOP, 8)

        categories = sorted(set(
            Processor.get_processor_by_type(p).get_category()
            for p in Processor.get_processors()
        ))
        self._category_list = wx.CheckListBox(panel, choices=categories)
        for i, cat in enumerate(categories):
            if cat in ('Selenium', 'HTTP', 'General'):
                self._category_list.Check(i, True)
        main_sizer.Add(self._category_list, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)

        # Chat area
        self._chat_panel = scrolled.ScrolledPanel(panel)
        self._chat_panel.SetBackgroundColour(wx.WHITE)
        self._chat_sizer = wx.BoxSizer(wx.VERTICAL)
        self._chat_panel.SetSizer(self._chat_sizer)
        self._chat_panel.SetupScrolling(scroll_x=False)
        main_sizer.Add(self._chat_panel, 3, wx.EXPAND | wx.LEFT | wx.RIGHT, 8)

        # Input area
        input_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._input_text = wx.TextCtrl(
            panel, style=wx.TE_MULTILINE | wx.TE_PROCESS_ENTER, size=(-1, 50)
        )
        self._input_text.SetHint(t("ai_gen_input_hint"))
        input_sizer.Add(self._input_text, 1, wx.EXPAND)
        self._btn_send = wx.Button(panel, label=t("ai_gen_send"), size=(60, 50))
        input_sizer.Add(self._btn_send, 0, wx.LEFT, 4)
        main_sizer.Add(input_sizer, 0, wx.EXPAND | wx.ALL, 8)

        # Token display
        self._token_label = wx.StaticText(panel, label="")
        main_sizer.Add(self._token_label, 0, wx.LEFT | wx.BOTTOM, 8)

        # Bottom buttons
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._btn_done = wx.Button(panel, label=t("ai_gen_done"))
        btn_sizer.Add(self._btn_done, 0)
        btn_sizer.AddStretchSpacer()
        self._btn_undo = wx.Button(panel, label="Undo", size=(60, -1))
        self._btn_redo = wx.Button(panel, label="Redo", size=(60, -1))
        btn_sizer.Add(self._btn_undo, 0, wx.RIGHT, 4)
        btn_sizer.Add(self._btn_redo, 0)
        main_sizer.Add(btn_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)

        panel.SetSizer(main_sizer)

    def _bind_events(self):
        self._btn_send.Bind(wx.EVT_BUTTON, self._on_send)
        self._input_text.Bind(wx.EVT_TEXT_ENTER, self._on_send)
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
        current_tasks = self._on_apply('get_tasks') if self._on_apply else None
        self._input_text.Clear()
        self._input_text.Disable()
        self._btn_send.Disable()
        self._add_message(msg, is_user=True)
        self._add_message(t("ai_gen_thinking"), is_user=False, is_thinking=True)

        thread = threading.Thread(target=self._do_chat, args=(msg, current_tasks), daemon=True)
        thread.start()

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
            summary = f"✓ {len(tasks)} tasks"
            if warnings:
                summary += "\n" + "\n".join(warnings)
            self._add_message(summary, is_user=False)

        elif action == 'modify':
            current_tasks = self._on_apply('get_tasks') if self._on_apply else []
            new_tasks = self._generator.apply_modifications(
                current_tasks, result.get('operations', [])
            )
            warnings = self._generator.validate_tasks(new_tasks)
            if self._on_apply:
                self._on_apply('apply', new_tasks, None)
            summary = f"✓ {len(new_tasks)} tasks (modified)"
            if warnings:
                summary += "\n" + "\n".join(warnings)
            self._add_message(summary, is_user=False)

        else:
            self._add_message(result.get('content', ''), is_user=False)

        prompt_t, comp_t = self._generator.get_token_usage()
        self._token_label.SetLabel(t("ai_gen_tokens", input=prompt_t, output=comp_t))

    def _add_message(self, text, is_user=False, is_thinking=False):
        msg_panel = wx.Panel(self._chat_panel)
        msg_panel.SetBackgroundColour(
            wx.Colour(220, 235, 255) if is_user else wx.Colour(245, 245, 245)
        )
        if is_thinking:
            msg_panel.SetName("thinking_panel")

        sizer = wx.BoxSizer(wx.VERTICAL)
        label = wx.StaticText(msg_panel, label=text)
        label.Wrap(max(200, self._chat_panel.GetClientSize().width - 40))
        sizer.Add(label, 0, wx.ALL, 6)
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
