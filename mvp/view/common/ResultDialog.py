import csv
import io
import json
import os

import wx


class ResultDialog(wx.Dialog):
    """Enhanced result dialog with scrollable monospace content,
    automatic JSON pretty-printing, copy-to-clipboard,
    and conditional Save-as-JSON / Save-as-CSV export."""

    def __init__(self, parent=None, title="", message=""):
        style = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
        super().__init__(parent, title="PETP - Message Box", style=style)

        self._raw_msg = message or ""
        self._display_msg = _format_message(message)
        self._parsed_json = _try_parse_json(self._raw_msg)
        # CSV export supports either JSON 2-D data or raw CSV text.
        self._csv_rows = _try_parse_2d_array(self._parsed_json) or _try_parse_csv_text(self._raw_msg)

        self._build_ui(self._display_msg, title)
        self._try_set_icon()

        self.Fit()
        self.CentreOnScreen()

    # ------------------------------------------------------------------ #
    # UI construction
    # ------------------------------------------------------------------ #

    def _build_ui(self, message, title):
        PAD = 15
        sizer = wx.BoxSizer(wx.VERTICAL)

        # -- Header row: icon + title text --
        hdr = wx.BoxSizer(wx.HORIZONTAL)
        bmp = wx.ArtProvider.GetBitmap(wx.ART_INFORMATION,
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

        # -- Scrollable message area --
        txt_style = (wx.TE_MULTILINE | wx.TE_READONLY
                     | wx.TE_RICH2 | wx.HSCROLL)
        self._text = wx.TextCtrl(self, value=message, style=txt_style)
        self._text.SetFont(
            wx.Font(wx.FontInfo(13).Family(wx.FONTFAMILY_MODERN))
        )

        # Auto-size: taller for long content, clamped to sane bounds.
        lines = message.count('\n') + 1 if message else 1
        height = min(max(lines * 24 + 30, 160), 480)
        self._text.SetMinSize((520, height))

        sizer.Add(self._text, 1, wx.LEFT | wx.RIGHT | wx.EXPAND, PAD)

        # -- Button bar --
        btns = wx.BoxSizer(wx.HORIZONTAL)

        # Save as JSON — enabled only when content is valid JSON
        self._json_btn = wx.Button(self, label="Save as JSON")
        self._json_btn.Bind(wx.EVT_BUTTON, self._on_save_json)
        self._json_btn.Enable(self._parsed_json is not None)

        # Save as CSV — enabled when content can be represented as CSV rows
        self._csv_btn = wx.Button(self, label="Save as CSV")
        self._csv_btn.Bind(wx.EVT_BUTTON, self._on_save_csv)
        self._csv_btn.Enable(self._csv_rows is not None)

        self._copy_btn = wx.Button(self, label="Copy")
        self._copy_btn.Bind(wx.EVT_BUTTON, self._on_copy)

        ok_btn = wx.Button(self, wx.ID_OK, "&OK")
        ok_btn.SetDefault()

        btns.AddStretchSpacer()
        btns.Add(self._json_btn, 0, wx.RIGHT, 8)
        btns.Add(self._csv_btn, 0, wx.RIGHT, 8)
        btns.Add(self._copy_btn, 0, wx.RIGHT, 8)
        btns.Add(ok_btn)
        sizer.AddSpacer(PAD)
        sizer.Add(btns, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, PAD)

        self.SetSizer(sizer)
        self.SetMinSize((680, 320))

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

    def _on_copy(self, _evt):
        if wx.TheClipboard.Open():
            try:
                wx.TheClipboard.SetData(wx.TextDataObject(self._display_msg))
            finally:
                wx.TheClipboard.Close()

    def _on_save_json(self, _evt):
        """Save the parsed JSON to a .json file chosen by the user."""
        with wx.FileDialog(self, "Save as JSON",
                           wildcard="JSON files (*.json)|*.json",
                           style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT,
                           defaultFile="result.json") as dlg:
            if dlg.ShowModal() == wx.ID_CANCEL:
                return
            path = dlg.GetPath()
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(self._parsed_json, f, indent=2, ensure_ascii=False)
            wx.MessageBox(f"Saved to:\n{path}", "Save as JSON",
                          wx.OK | wx.ICON_INFORMATION, self)
        except Exception as e:
            wx.MessageBox(f"Failed to save:\n{e}", "Error",
                          wx.OK | wx.ICON_ERROR, self)

    def _on_save_csv(self, _evt):
        """Save CSV-compatible rows as a .csv file chosen by the user."""
        with wx.FileDialog(self, "Save as CSV",
                           wildcard="CSV files (*.csv)|*.csv",
                           style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT,
                           defaultFile="result.csv") as dlg:
            if dlg.ShowModal() == wx.ID_CANCEL:
                return
            path = dlg.GetPath()
        try:
            with open(path, 'w', encoding='utf-8-sig', newline='') as f:
                writer = csv.writer(f)
                for row in self._csv_rows:
                    writer.writerow(row)
            wx.MessageBox(f"Saved to:\n{path}", "Save as CSV",
                          wx.OK | wx.ICON_INFORMATION, self)
        except Exception as e:
            wx.MessageBox(f"Failed to save:\n{e}", "Error",
                          wx.OK | wx.ICON_ERROR, self)


# ------------------------------------------------------------------ #
# Module-level helpers
# ------------------------------------------------------------------ #

def _format_message(msg):
    """Pretty-print JSON strings; return everything else unchanged."""
    if not msg:
        return ""
    try:
        data = json.loads(msg)
        return json.dumps(data, indent=2, ensure_ascii=False)
    except (json.JSONDecodeError, TypeError, ValueError):
        return msg


def _try_parse_json(msg):
    """Return parsed object if *msg* is valid JSON, else None."""
    if not msg:
        return None
    try:
        return json.loads(msg)
    except (json.JSONDecodeError, TypeError, ValueError):
        return None


def _try_parse_2d_array(parsed):
    """Return a list-of-lists if *parsed* is a 2-D array structure, else None.

    Accepted shapes:
      1. [[v, v, ...], [v, v, ...], ...]          — plain 2-D list
      2. [{"k":"v", ...}, {"k":"v", ...}, ...]     — list of flat dicts
         → converted to 2-D with dict keys as the header row.
    """
    if not isinstance(parsed, list) or len(parsed) == 0:
        return None

    # Shape 1: every element is a list/tuple
    if all(isinstance(row, (list, tuple)) for row in parsed):
        return [list(row) for row in parsed]

    # Shape 2: every element is a flat dict
    if all(isinstance(row, dict) for row in parsed):
        # Collect all keys preserving insertion order
        keys = list(dict.fromkeys(k for row in parsed for k in row))
        header = keys
        rows = [header] + [[row.get(k, '') for k in keys] for row in parsed]
        return rows

    return None


def _try_parse_csv_text(msg):
    """Return CSV rows parsed from raw text, else None."""
    if not isinstance(msg, str) or not msg.strip():
        return None

    text = msg.strip('\ufeff\r\n ')
    if not text:
        return None

    sample = text[:2048]
    dialect = csv.excel
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",;\t|")
    except csv.Error:
        pass

    try:
        rows = list(csv.reader(io.StringIO(text), dialect))
    except csv.Error:
        return None

    if not rows:
        return None

    # Avoid enabling CSV save for plain single-value text.
    if max((len(row) for row in rows), default=0) < 2:
        return None

    return rows

