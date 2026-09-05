"""Probe: PopupMenuButton (theme/lang switcher) — label padding & height.

Replicates themeChooser (longest choice "Cyberpunk") + langChooser ("中文")
next to a native (75,28) button, and prints each choice's text extent vs the
control's client width so we can see how much horizontal padding the label
actually has (and that height 22 != toolbar 28).

Usage: PYTHONPATH=. python testcoverage/probe_popup.py
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

from mvp.view.common.PopupMenuButton import PopupMenuButton


def grab(frame, path):
    rect = frame.GetScreenRect()
    screen = wx.ScreenDC()
    bmp = wx.Bitmap(rect.width, rect.height)
    mem = wx.MemoryDC(bmp)
    mem.Blit(0, 0, rect.width, rect.height, screen, rect.x, rect.y)
    mem.SelectObject(wx.NullBitmap)
    bmp.SaveFile(path, wx.BITMAP_TYPE_PNG)


app = wx.App(False)
f = wx.Frame(None, title="switcher probe", style=wx.CAPTION | wx.CLOSE_BOX | wx.STAY_ON_TOP)
f.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNFACE))

themes = ["Forest", "Ocean", "Monokai", "Solarized", "Nord", "Dracula", "Sakura", "Cyberpunk"]
langs = ["EN", "中文"]

# Show the LONGEST choice so any pinch is visible.
theme_btn = PopupMenuButton(f, choices=themes, default="Cyberpunk", min_width=90, variant="button")
lang_btn = PopupMenuButton(f, choices=langs, default="中文", min_width=50, variant="button")
ref_btn = wx.Button(f, label="Stop"); ref_btn.SetMinSize((75, 28))

row = wx.BoxSizer(wx.HORIZONTAL)
row.Add(ref_btn, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)
row.Add(theme_btn, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 10)
row.Add(lang_btn, 0, wx.ALIGN_CENTER_VERTICAL, 0)
f.SetSizer(row)
f.Fit(); f.CentreOnScreen(); f.Show(); f.Refresh(); f.Update()

import time
for _ in range(10):
    wx.Yield(); time.sleep(0.05)

print("DPI scale:", f.GetDPIScaleFactor())
dc = wx.ClientDC(theme_btn)
font = theme_btn.GetFont() or wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
dc.SetFont(font)
print("\ntheme choice text widths:")
for c in themes:
    print("  %-10s %dpx" % (c, dc.GetTextExtent(c)[0]))
print("lang choice text widths:", {c: dc.GetTextExtent(c)[0] for c in langs})

print("\n%-14s %-10s %-10s %-10s %-12s" % ("control", "best", "min", "size", "client"))
for w in [ref_btn, theme_btn, lang_btn]:
    try:
        b = tuple(w.GetBestSize())
    except Exception:
        b = "?"
    print("%-14s %-10s %-10s %-10s %-12s" % (
        w.__class__.__name__, b, tuple(w.GetMinSize()), tuple(w.GetSize()), tuple(w.GetClientSize())))

# Padding the label actually has on each side at current width.
for btn, choices in [(theme_btn, themes), (lang_btn, langs)]:
    longest = max(choices, key=lambda c: dc.GetTextExtent(c)[0])
    tw = dc.GetTextExtent(longest)[0]
    cw = btn.GetClientSize().width
    print("  %s longest='%s' tw=%d client_w=%d side_pad=%.1f" % (
        btn.__class__.__name__, longest, tw, cw, (cw - tw) / 2))

grab(f, "testcoverage/v_popup.png")
print("\nsaved testcoverage/v_popup.png")
f.Close(); app.Destroy()
