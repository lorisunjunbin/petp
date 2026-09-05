import wx
import wx.grid


class ProcessorNameRenderer(wx.grid.GridCellRenderer):
    """Renders taskGrid / executionGrid column 0 (processor / execution name).

    Default grid renderer hard-clips long names at the cell edge with no
    ellipsis (the Description column's TaskInfoRenderer does ellipsize) —
    this renderer gives column 0 the same treatment so both columns truncate
    consistently. Appends " ⊖" for skipped tasks.
    """

    def Draw(self, grid, attr, dc, rect, row, col, isSelected):
        dc.SetClippingRegion(rect)
        try:
            text = grid.GetCellValue(row, col)
            is_skipped = False
            try:
                table = grid.GetTable()
                skipped_val = str(getattr(table, 'GetSkippedValue', lambda r: 'no')(row)).lower()
                is_skipped = skipped_val in {"yes", "y", "true", "t"}
            except Exception:
                pass

            if isSelected:
                bg = grid.GetSelectionBackground()
                fg = grid.GetSelectionForeground()
            else:
                bg = attr.GetBackgroundColour()
                fg = attr.GetTextColour()
                if not fg.IsOk():
                    fg = grid.GetDefaultCellTextColour()

            dc.SetBrush(wx.Brush(bg))
            dc.SetPen(wx.TRANSPARENT_PEN)
            dc.DrawRectangle(rect)

            font = attr.GetFont()
            if not font.IsOk():
                font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
            dc.SetFont(font)
            dc.SetTextForeground(fg)

            text_h = dc.GetTextExtent("A")[1]
            y = rect.y + (rect.height - text_h) // 2
            x = rect.x + 6
            max_w = rect.x + rect.width - 6 - x

            if is_skipped:
                muted = wx.Colour(
                    fg.Red() // 2 + bg.Red() // 2,
                    fg.Green() // 2 + bg.Green() // 2,
                    fg.Blue() // 2 + bg.Blue() // 2,
                )
                mark = "⊖ "
                mw = dc.GetTextExtent(mark)[0]
                dc.SetTextForeground(muted)
                dc.DrawText(mark, x, y)
                x += mw
                max_w -= mw
                dc.SetTextForeground(fg)

            # Ellipsize: drop chars from the end until it fits, then add "…".
            clipped = text
            while clipped and dc.GetTextExtent(clipped)[0] > max_w:
                clipped = clipped[:-1]
            if clipped != text:
                clipped = clipped[:-1] + "…" if clipped else "…"
            dc.DrawText(clipped, x, y)
        finally:
            dc.DestroyClippingRegion()

    def GetBestSize(self, grid, attr, dc, row, col):
        return wx.Size(200, 22)

    def Clone(self):
        return ProcessorNameRenderer()
