import wx
import wx.dataview
from i18n.translations import t


class CronDashboardDialog(wx.Dialog):
    """
    Dialog showing cron execution history from CronHistory.
    """

    def __init__(self, parent, cron_history):
        super().__init__(
            parent, title=t("dlg_cron_dashboard_title"),
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
        )
        self._history = cron_history
        self._build_ui()
        self.SetSize(900, 480)
        self.Centre()
        self._refresh()

    def _build_ui(self):
        sizer = wx.BoxSizer(wx.VERTICAL)

        toolbar = wx.BoxSizer(wx.HORIZONTAL)
        self._filter = wx.TextCtrl(self, size=(200, 28), style=wx.TE_PROCESS_ENTER)
        self._filter.SetHint(t("cron_filter_hint"))
        self._filter.Bind(wx.EVT_TEXT, lambda e: self._refresh())
        toolbar.Add(wx.StaticText(self, label=t("cron_lbl_filter")), 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 6)
        toolbar.Add(self._filter, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 6)
        toolbar.Add((0, 0), 1)
        btn_refresh = wx.Button(self, label=t("btn_refresh"), size=(80, 28))
        btn_refresh.Bind(wx.EVT_BUTTON, lambda e: self._refresh())
        toolbar.Add(btn_refresh, 0, wx.ALL, 4)
        sizer.Add(toolbar, 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 4)

        self._list = wx.dataview.DataViewListCtrl(
            self, style=wx.dataview.DV_ROW_LINES | wx.dataview.DV_VERT_RULES | wx.dataview.DV_SINGLE
        )
        self._list.AppendTextColumn(t("cron_col_start_time"), width=155)
        self._list.AppendTextColumn(t("cron_col_pipeline"),   width=190)
        self._list.AppendTextColumn(t("cron_col_cron_exp"),   width=120)
        self._list.AppendTextColumn(t("cron_col_status"),     width=55)
        self._list.AppendTextColumn(t("cron_col_duration"),   width=75)
        self._list.AppendTextColumn(t("cron_col_error"),      width=280)
        sizer.Add(self._list, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 4)

        self._detail = wx.TextCtrl(
            self, size=(-1, 80),
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.BORDER_SIMPLE
        )
        self._detail.SetFont(wx.Font(10, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        sizer.Add(self._detail, 0, wx.EXPAND | wx.ALL, 4)

        self._list.Bind(wx.dataview.EVT_DATAVIEW_SELECTION_CHANGED, self._on_row_select)

        btn_close = wx.Button(self, wx.ID_CLOSE, t("btn_close"), size=(80, 28))
        btn_close.Bind(wx.EVT_BUTTON, lambda e: self.Destroy())
        self.Bind(wx.EVT_CLOSE, lambda e: self.Destroy())
        sizer.Add(btn_close, 0, wx.ALIGN_RIGHT | wx.ALL, 6)

        self.SetSizer(sizer)
        self._records = []

    def _refresh(self):
        keyword = self._filter.GetValue().strip().lower()
        pipeline_filter = keyword if keyword else None
        records = self._history.get_history(limit=50, pipeline_name=pipeline_filter)
        self._records = records
        self._list.DeleteAllItems()
        self._detail.SetValue("")
        for r in records:
            duration_s = r.get('duration_ms', 0) / 1000.0
            status = "OK" if r.get('ok') else "FAIL"
            self._list.AppendItem([
                r.get('start_time', ''),
                r.get('pipeline_name', ''),
                r.get('cron_exp', ''),
                status,
                f"{duration_s:.1f}s",
                r.get('error', '') or '',
            ])

    def _on_row_select(self, evt):
        row = self._list.GetSelectedRow()
        if row < 0 or row >= len(self._records):
            return
        r = self._records[row]
        record_id = r.get('id', '')
        full = self._history.get_record(record_id) if record_id else r
        if not full:
            return
        lines = [
            f"Pipeline : {full.get('pipeline_name', '')}",
            f"Cron Exp : {full.get('cron_exp', '')}",
            f"Start    : {full.get('start_time', '')}",
            f"Duration : {full.get('duration_ms', 0) / 1000:.1f}s",
            f"Status   : {'OK' if full.get('ok') else 'FAIL'}",
        ]
        if full.get('error'):
            lines.append(f"Error    : {full['error']}")
        executions = full.get('executions') or []
        if executions:
            lines.append("Steps    :")
            for ex in executions:
                ok_str = "✓" if ex.get('ok') else "✗"
                ms = ex.get('result', {}).get('meta', {}).get('duration_ms', 0) if isinstance(ex.get('result'), dict) else 0
                lines.append(f"  {ok_str} {ex.get('execution', '')}  ({ms}ms)")
        self._detail.SetValue("\n".join(lines))
