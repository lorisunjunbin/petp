"""Isolated DPI-awareness probe: which mode scales wx windows correctly?

Usage: python testcoverage/probe_mode.py {v2|sys|none}
Creates a wx.Frame + PropertyGridManager, SetSize((2048,1152)), prints the
PHYSICAL window size reported by Win32 (ground truth) vs what wx thinks.
Correct = 2048x1152 or 3072x1728. Inverted/buggy = 1365x768 (=2048/1.5).
Also lets the C++ "Using possibly wrong DPI" warnings surface on stderr.
"""
import sys
import ctypes
from ctypes import wintypes

mode = sys.argv[1] if len(sys.argv) > 1 else "none"
if mode == "v2":           # PER_MONITOR_AWARE_V2 (current setting)
    try:
        ctypes.windll.user32.SetProcessDpiAwarenessContext(-4)
    except Exception:
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except Exception:
            ctypes.windll.user32.SetProcessDPIAware()
elif mode == "sys":        # SYSTEM_DPI_AWARE
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass
# mode == "none": do nothing, let wxPython's own manifest decide

import wx
import wx.propgrid

app = wx.App(False)
f = wx.Frame(None, title="probe")
f.SetSize((2048, 1152))
pg = wx.propgrid.PropertyGridManager(f)
pg.Append(wx.propgrid.StringProperty("Test", value="hello"))
f.Show()
wx.Yield()
import time
time.sleep(0.3)
r = wintypes.RECT()
ctypes.windll.user32.GetWindowRect(f.GetHandle(), ctypes.byref(r))
print("RESULT mode=%s physical_window=%dx%d wx_GetSize=%s dpi_scale=%s"
      % (mode, r.right - r.left, r.bottom - r.top, tuple(f.GetSize()), f.GetDPIScaleFactor()))
app.Destroy()
