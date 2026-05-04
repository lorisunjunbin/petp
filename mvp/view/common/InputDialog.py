import os

import wx
import wx.stc as stc

from i18n.translations import t
from mvp.view.common.ThemedButton import ThemedButton


class InputDialog(wx.Dialog):
    """Input dialog with scrollable multi-line text entry,
    header row with icon, and OK / Cancel buttons."""

    def __init__(self, parent=None, title="", message="", default_value="", show_save_as_default=False):
        style = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
        super().__init__(parent, title=t("dlg_input_title"), style=style)

        self.value = default_value
        self.save_as_default = False
        self.saved_default_value = default_value
        self._build_ui(title, message, default_value, show_save_as_default)
        self._try_set_icon()

        self.Fit()
        self.CentreOnScreen()

    # ------------------------------------------------------------------ #
    # UI construction
    # ------------------------------------------------------------------ #

    def _build_ui(self, title, message, default_value, show_save_as_default):
        PAD = 15
        sizer = wx.BoxSizer(wx.VERTICAL)

        # -- Header row: icon + title text --
        hdr = wx.BoxSizer(wx.HORIZONTAL)
        bmp = wx.ArtProvider.GetBitmap(wx.ART_QUESTION,
                                       wx.ART_MESSAGE_BOX, (36, 36))
        hdr.Add(wx.StaticBitmap(self, bitmap=bmp),
                0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)

        lbl = wx.StaticText(self, label=title)
        lbl.SetFont(lbl.GetFont().Bold().Scaled(1.4))
        hdr.Add(lbl, 1, wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(hdr, 0, wx.LEFT | wx.TOP | wx.RIGHT, PAD)

        sizer.AddSpacer(PAD // 2)
        sizer.Add(wx.StaticLine(self), 0, wx.LEFT | wx.RIGHT | wx.EXPAND, PAD)
        sizer.AddSpacer(PAD // 2)

        # -- Message label --
        if message:
            msg_label = wx.StaticText(self, label=message)
            sizer.Add(msg_label, 0, wx.LEFT | wx.RIGHT | wx.EXPAND, PAD)
            sizer.AddSpacer(PAD // 2)

        # -- Editable text area (Scintilla code editor) --
        self._text = stc.StyledTextCtrl(self, style=wx.BORDER_THEME)
        self._text.SetText(default_value)

        # font
        font = wx.Font(wx.FontInfo(13).Family(wx.FONTFAMILY_MODERN))
        face = font.GetFaceName()
        size = font.GetPointSize()
        self._text.StyleSetSpec(stc.STC_STYLE_DEFAULT,
                                f"face:{face},size:{size}")
        self._text.StyleClearAll()

        # line numbers
        self._text.SetMarginType(0, stc.STC_MARGIN_NUMBER)
        self._text.SetMarginWidth(0, self._text.TextWidth(stc.STC_STYLE_LINENUMBER, "9999"))

        # tabs → spaces
        self._text.SetUseTabs(False)
        self._text.SetTabWidth(4)

        # word wrap off, show horizontal scrollbar
        self._text.SetWrapMode(stc.STC_WRAP_NONE)

        editor_w, editor_h, dialog_w, dialog_h = self._calc_content_aware_size(default_value)
        self._text.SetMinSize(wx.Size(editor_w, editor_h))
        self._text.SetFocus()
        self._text.SelectAll()
        sizer.Add(self._text, 1, wx.LEFT | wx.RIGHT | wx.EXPAND, PAD)

        # -- Button bar --
        btns = wx.BoxSizer(wx.HORIZONTAL)

        cancel_btn = wx.Button(self, wx.ID_CANCEL, t("dlg_cancel"))
        ok_btn = ThemedButton(self, wx.ID_OK, t("dlg_ok"))
        ok_btn.SetDefault()
        ok_btn.Bind(wx.EVT_BUTTON, self._on_ok)

        btns.AddStretchSpacer()
        btns.Add(cancel_btn, 0, wx.RIGHT, 8)
        if show_save_as_default:
            save_default_btn = ThemedButton(self, wx.ID_ANY, t("dlg_save_as_default"))
            save_default_btn.Bind(wx.EVT_BUTTON, self._on_save_as_default)
            btns.Add(save_default_btn, 0, wx.RIGHT, 8)
        btns.Add(ok_btn)
        sizer.AddSpacer(PAD)
        sizer.Add(btns, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, PAD)

        self.SetSizer(sizer)
        self.SetMinSize(wx.Size(560, 320))
        self.SetSize(wx.Size(dialog_w, dialog_h))

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #
    def _try_set_icon(self):
        icon_path = os.path.realpath(os.path.join('.', 'image', 'petp_small.png'))
        if os.path.isfile(icon_path):
            try:
                self.SetIcon(wx.Icon(icon_path))
            except Exception:
                pass

    def _calc_content_aware_size(self, content):
        lines = content.split('\n') if isinstance(content, str) and content else ['']
        line_count = max(1, len(lines))
        longest_line = max((len(line) for line in lines), default=1)

        # Estimate editor dimensions from text density.
        char_px = max(7, self._text.TextWidth(stc.STC_STYLE_DEFAULT, 'M'))
        line_px = max(18, self._text.TextHeight(0))
        line_margin_px = self._text.GetMarginWidth(0)

        editor_w = int(longest_line * char_px + line_margin_px + 40)
        editor_h = int(line_count * line_px + 24)

        # Keep defaults sensible for short text while allowing larger content.
        min_editor_w, min_editor_h = 520, 160
        editor_w = max(min_editor_w, editor_w)
        editor_h = max(min_editor_h, editor_h)

        # Clamp to current display so the dialog remains fully reachable.
        display_idx = wx.Display.GetFromWindow(self)
        display = wx.Display(display_idx if display_idx != wx.NOT_FOUND else 0)
        client = display.GetClientArea()

        # Approximate non-editor chrome (header/message/buttons/padding).
        dialog_w = min(editor_w + 40, int(client.width * 0.96))
        dialog_h = min(editor_h + 210, int(client.height * 0.92))

        # Recompute editor size to fit inside dialog chrome limits.
        editor_w = max(min_editor_w, dialog_w - 40)
        editor_h = max(min_editor_h, dialog_h - 210)

        return editor_w, editor_h, dialog_w, dialog_h

    def _on_ok(self, _evt):
        self.value = self._text.GetText()
        self.EndModal(wx.ID_OK)

    def _on_save_as_default(self, _evt):
        self.save_as_default = True
        self.saved_default_value = self._text.GetText()

    def GetValue(self):
        return self.value

