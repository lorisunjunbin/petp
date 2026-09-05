"""Visual probe: ThemedButton vs native wx.Button side-by-side.

Replicates the ResultDialog button bar (native wx.Button + ThemedButton OK) so
we can see the height / padding mismatch that makes ThemedButton look "off".
Uses PER_MONITOR_AWARE_V2 (same as the real app entry).

Usage: python testcoverage/probe_themedbtn.py
"""
import sys
import ctypes

# Match the real app: PER_MONITOR_AWARE_V2.
try:
    ctypes.windll.user32.SetProcessDpiAwarenessContext(-4)
except Exception:
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        ctypes.windll.user32.SetProcessDPIAware()

import wx

from mvp.view.common.ThemedButton import ThemedButton
from mvp.view.common.RunButton import RunButton


def grab(frame, path):
    rect = frame.GetScreenRect()
    print("frame screen rect:", (rect.x, rect.y, rect.width, rect.height))
    screen = wx.ScreenDC()
    bmp = wx.Bitmap(rect.width, rect.height)
    mem = wx.MemoryDC(bmp)
    mem.Blit(0, 0, rect.width, rect.height, screen, rect.x, rect.y)
    mem.SelectObject(wx.NullBitmap)
    bmp.SaveFile(path, wx.BITMAP_TYPE_PNG)


app = wx.App(False)
f = wx.Frame(None, title="ThemedButton probe", style=wx.CAPTION | wx.CLOSE_BOX | wx.STAY_ON_TOP)
f.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNFACE))

vbox = wx.BoxSizer(wx.VERTICAL)
PAD = 15
vbox.AddSpacer(PAD)


def add_row(label, widgets):
    vbox.Add(wx.StaticText(f, label=label), 0, wx.LEFT | wx.BOTTOM, 4)
    row = wx.BoxSizer(wx.HORIZONTAL)
    for w, border in widgets:
        row.Add(w, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, border)
    vbox.Add(row, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, PAD)


# Row 1: replicate ResultDialog button bar — native buttons + ThemedButton OK.
r1 = [
    (wx.Button(f, label="Save JSON"), 8),
    (wx.Button(f, label="Save CSV"), 8),
    (wx.Button(f, label="Copy"), 8),
    (ThemedButton(f, wx.ID_ANY, "OK"), 0),
]
add_row("Row1: native wx.Button x3 + ThemedButton(OK)  [ResultDialog layout]", r1)

# Row 2: native OK next to ThemedButton OK — same label, direct compare.
r2 = [
    (wx.Button(f, label="OK"), 12),
    (ThemedButton(f, wx.ID_ANY, "OK"), 0),
]
add_row("Row2: native wx.Button(OK) vs ThemedButton(OK)  [same label]", r2)

f.SetSizer(vbox)
f.Fit()
f.CentreOnScreen()
f.Show()
f.Refresh()
f.Update()

import time
for _ in range(10):
    wx.Yield()
    time.sleep(0.05)

# Report DPI + each button's best/min size so the mismatch is quantified.
print("DPI scale:", f.GetDPIScaleFactor())
for label, widgets in [("row1", r1), ("row2", r2)]:
    for w, _ in widgets:
        cls = w.__class__.__name__
        try:
            best = w.GetBestSize()
        except Exception:
            best = "?"
        try:
            client = tuple(w.GetClientSize())
        except Exception:
            client = "?"
        print(f"  {label:5} {cls:14} best={best} client={client}")

grab(f, "testcoverage/v_themedbtn.png")
print("saved testcoverage/v_themedbtn.png")

f.Close()
app.Destroy()
