import json

import wx
import wx.grid


def _first_desc_line(processor_name: str) -> str:
    """Return the first non-empty line of the processor's DESC."""
    try:
        from core.processor import Processor
        p = Processor.get_processor_by_type(processor_name)
        desc = p.get_localized_desc().strip()
        for line in desc.splitlines():
            line = line.strip()
            if line:
                return line
    except Exception:
        pass
    return ""


def _get_category(processor_name: str) -> str:
    try:
        from core.processor import Processor
        return Processor.get_category_map().get(processor_name, '')
    except Exception:
        return ""


def _analyse_input(input_json: str):
    """Return (is_skipped, has_empty, has_expr) from the raw input JSON string."""
    is_skipped = False
    has_empty = False
    has_expr = False
    try:
        data = json.loads(input_json) if input_json and len(input_json) > 2 else {}
        skipped_val = str(data.get("skipped", "no")).lower()
        is_skipped = skipped_val in {"yes", "y", "true", "t"}
        for k, v in data.items():
            if k == "skipped":
                continue
            sv = str(v)
            if sv == "" or sv == '""':
                has_empty = True
            if "{" in sv and "}" in sv:
                has_expr = True
    except Exception:
        pass
    return is_skipped, has_empty, has_expr


class TaskInfoRenderer(wx.grid.GridCellRenderer):
    """Renders taskGrid column 1 as:  description text ...    [Category]   ⊖ ⚠ {…}

    Badges: ⊖ skipped  ⚠ empty param  {…} has expressions
    """

    _desc_cache: dict = {}
    _cat_cache: dict = {}

    def _get_info(self, processor_name):
        if processor_name not in self._desc_cache:
            self._desc_cache[processor_name] = _first_desc_line(processor_name)
            self._cat_cache[processor_name] = _get_category(processor_name)
        return self._cat_cache[processor_name], self._desc_cache[processor_name]

    def Draw(self, grid, attr, dc, rect, row, col, isSelected):
        dc.SetClippingRegion(rect)
        try:
            self._draw(grid, attr, dc, rect, row, col, isSelected)
        finally:
            dc.DestroyClippingRegion()

    def _draw(self, grid, attr, dc, rect, row, col, isSelected):
        processor_name = grid.GetCellValue(row, 0)
        input_json = grid.GetTable().GetValue(row, col)

        is_skipped, has_empty, has_expr = _analyse_input(input_json)
        category, desc = self._get_info(processor_name) if processor_name else ("", "")

        # background
        if isSelected:
            bg = grid.GetSelectionBackground()
            fg = grid.GetSelectionForeground()
        elif is_skipped:
            normal_bg = grid.GetDefaultCellBackgroundColour()
            bg = wx.Colour(
                max(0, normal_bg.Red() - 30),
                max(0, normal_bg.Green() - 30),
                max(0, normal_bg.Blue() - 30),
            )
            fg = grid.GetDefaultCellTextColour()
            fg = wx.Colour(
                fg.Red() + (normal_bg.Red() - fg.Red()) * 2 // 3,
                fg.Green() + (normal_bg.Green() - fg.Green()) * 2 // 3,
                fg.Blue() + (normal_bg.Blue() - fg.Blue()) * 2 // 3,
            )
        else:
            bg = attr.GetBackgroundColour()
            fg = attr.GetTextColour()

        muted = wx.Colour(
            fg.Red() // 2 + bg.Red() // 2,
            fg.Green() // 2 + bg.Green() // 2,
            fg.Blue() // 2 + bg.Blue() // 2,
        )

        dc.SetBrush(wx.Brush(bg))
        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.DrawRectangle(rect)

        font = attr.GetFont()
        if not font.IsOk():
            font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        small_font = font.Scaled(0.85)

        text_h = dc.GetTextExtent("A")[1]
        y = rect.y + (rect.height - text_h) // 2
        right = rect.x + rect.width - 4   # cursor from right edge inward

        # --- badges (rightmost) ---
        badges = []
        if is_skipped:
            badges.append("⊖")
        if has_empty:
            badges.append("⚠")
        if has_expr:
            badges.append("{…}")
        if badges:
            dc.SetFont(font)
            badge_str = "  ".join(badges)
            bw = dc.GetTextExtent(badge_str)[0]
            right -= bw
            dc.SetTextForeground(muted)
            dc.DrawText(badge_str, right, y)
            right -= 8

        # --- [Category] tag (left of badges) ---
        if category:
            tag = f"[{category}]"
            dc.SetFont(small_font)
            tw = dc.GetTextExtent(tag)[0]
            right -= tw
            dc.SetTextForeground(muted)
            dc.DrawText(tag, right, y + 1)
            right -= 8
            dc.SetFont(font)

        # --- description text (fills remaining left space) ---
        x = rect.x + 4
        if desc:
            max_w = right - x - 4
            dc.SetFont(font)
            dc.SetTextForeground(fg)
            clipped = desc
            while clipped and dc.GetTextExtent(clipped)[0] > max_w:
                clipped = clipped[:-1]
            if clipped != desc:
                clipped = clipped[:-1] + "…"
            dc.DrawText(clipped, x, y)

    def GetBestSize(self, grid, attr, dc, row, col):
        return wx.Size(200, 22)

    def Clone(self):
        return TaskInfoRenderer()
