"""Probe: RunButton ("Execute") vs neighbouring native buttons in the
Executions toolbar — diagnose vertical alignment.

Replicates the actionPanelSizer_e run row (RunButton + Stop/Snapshots/Save,
all SetMinSize((.., 28))) and prints best/min/actual size so we can see why
RunButton does not line up with the native buttons next to it.

Usage: PYTHONPATH=. python testcoverage/probe_runbtn.py
"""
import sys
import ctypes

try:
    ctypes.windll.user32.SetProcessDpiAwarenessContext(-4)
except Exception:
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        ctypes.windll.user32.SetProcessDPIAware()

import wx

from mvp.view.common.RunButton import RunButton


def grab(frame, path):
    try:
        bmp = frame.ScreenShot()
    except Exception:
        bmp = None
    if bmp is None or bmp.GetSize() == (0, 0):
        rect = frame.GetScreenRect()
        screen = wx.ScreenDC()
        bmp = wx.Bitmap(rect.width, rect.height)
        mem = wx.MemoryDC(bmp)
        mem.Blit(0, 0, rect.width, rect.height, screen, rect.x, rect.y)
        mem.SelectObject(wx.NullBitmap)
    bmp.SaveFile(path, wx.BITMAP_TYPE_PNG)


app = wx.App(False)
f = wx.Frame(None, title="Execute btn probe", style=wx.CAPTION | wx.CLOSE_BOX | wx.STAY_ON_TOP)
f.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNFACE))

row = wx.BoxSizer(wx.HORIZONTAL)

run = RunButton(f, label="Execute")
run.SetMinSize((100, 30))  # Windows: _apply_ui_polish bumps RunButton to 30

stop = wx.Button(f, label="Stop"); stop.SetMinSize((75, 28))
snap = wx.Button(f, label="Snapshots"); snap.SetMinSize((75, 28))
save = wx.Button(f, label="Save"); save.SetMinSize((75, 28))

for w in [run, stop, snap, save]:
    row.Add(w, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 8)

f.SetSizer(row)
f.Fit()
f.CentreOnScreen()
f.Show()
f.Refresh(); f.Update()

import time
for _ in range(10):
    wx.Yield()
    time.sleep(0.05)

print("DPI scale:", f.GetDPIScaleFactor())
print("%-12s %-14s %-14s %-14s %-14s" % ("control", "best", "min", "size", "client"))
for w in [run, stop, snap, save]:
    cls = w.__class__.__name__
    try:
        b = tuple(w.GetBestSize())
    except Exception:
        b = "?"
    print("%-12s %-14s %-14s %-14s %-14s" % (cls, b, tuple(w.GetMinSize()), tuple(w.GetSize()), tuple(w.GetClientSize())))

grab(f, "testcoverage/v_runbtn.png")
print("saved testcoverage/v_runbtn.png")

try:
    run._timer.Stop()
except Exception:
    pass
f.Close()
app.Destroy()
