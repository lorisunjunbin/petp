"""Probe: McpDescEditor grid column layout — are all columns inside the panel?

Replicates the real right-panel width, loads a real execution with mcp_desc
input params, and measures each grid column's x-range vs the grid's visible
width. Ground truth for the "MCP desc table truncated" report.

Usage: PYTHONPATH=. python testcoverage/probe_mcpgrid.py
"""
import ctypes

try:
    ctypes.windll.user32.SetProcessDpiAwarenessContext(-4)
except Exception:
    pass

import wx

from mvp.view.common.McpDescEditor import McpDescEditor
from mvp.view.PETPTheme import set_theme

set_theme("Forest")
app = wx.App(False)
f = wx.Frame(None, size=(520, 700))  # right panel is ~1/4 of a 2048 window
f.Show()
wx.Yield()

ed = McpDescEditor(f, wx.ID_ANY)
f.SetSizer(wx.BoxSizer(wx.VERTICAL))
f.GetSizer().Add(ed, 1, wx.EXPAND)
f.Layout()
wx.Yield()

# Load a representative mcp_desc with several params (like the earthquake tool)
desc = {
    "desc": "information of recent earthquakes",
    "inputSchema": {
        "type": "object",
        "properties": {
            "start_time": {"type": "string", "title": "start_time", "description": "date format: yyyy-mm-dd hh:mm:ss"},
            "sort": {"type": "string", "description": "true means sort asc. otherwise desc"},
            "min_magnitude": {"type": "string", "description": "min of magnitude"},
        },
        "required": ["start_time"],
    },
}
import json
ed.SetValue(json.dumps(desc))
# Simulate the polish pass (fires the initial fit)
base = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
font = wx.Font(base)
font.SetPointSize(10)
ed.apply_ui_polish(font)
wx.Yield()

panel_w = ed.GetClientSize().width
print(f"editor client width: {panel_w}")
for name, grid, ncols in (("input", ed._input_grid, 5), ("output", ed._output_grid, 4)):
    gw = grid.GetClientSize().width
    total = sum(grid.GetColSize(c) for c in range(grid.GetNumberCols()))
    xs = []
    x = 0
    for c in range(grid.GetNumberCols()):
        label = grid.GetColLabelValue(c)
        xs.append(f"  col{c} [{label}] x={x}..{x + grid.GetColSize(c)} w={grid.GetColSize(c)}")
        x += grid.GetColSize(c)
    print(f"\n{name} grid: client_w={gw} sum_cols={total} row_label={grid.GetRowLabelSize()}")
    print("\n".join(xs))
    print(f"  => overflow: {'YES - columns exceed visible width' if total + grid.GetRowLabelSize() > gw else 'no'}")

# Screenshot the editor itself — the whole frame IS the MCP panel, no crop math.
f.Refresh(); f.Update()
import time as _t
for _ in range(10):
    wx.Yield(); _t.sleep(0.05)
screen = wx.ScreenDC()
bmp = wx.Bitmap(f.GetSize().width, f.GetSize().height)
mem = wx.MemoryDC(bmp)
rect = f.GetScreenRect()
mem.Blit(0, 0, rect.width, rect.height, screen, rect.x, rect.y)
mem.SelectObject(wx.NullBitmap)
bmp.SaveFile("testcoverage/v_mcpgrid.png", wx.BITMAP_TYPE_PNG)
print("\nsaved testcoverage/v_mcpgrid.png")

f.Close()
app.Destroy()
