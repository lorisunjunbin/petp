"""DPI helper for custom-drawn controls.

Windows: wx.GraphicsContext draws in physical pixels with NO auto-scaling, so
custom controls (ToggleSwitch, RunButton, ...) that hardcode design pixel values
must scale them by the DPI factor — otherwise they render too small at 125% /
150% / 200%. macOS/Linux: the GraphicsContext already auto-scales, so design
values are returned unchanged.

Centralising this here keeps the "Windows-only" rule in one place (see memory:
UI changes are Windows-only).
"""
import sys


def dip(window, value):
    """Scale a design (96-DPI / DIP) pixel value for custom drawing.

    On Windows returns ``window.FromDIP(value)`` (scales with the user's display
    setting: 36 -> 54 at 150%, -> 72 at 200%). On macOS/Linux returns ``value``
    unchanged. Accepts an int or a (w, h) tuple.
    """
    if sys.platform != "win32":
        return value
    try:
        return window.FromDIP(value)
    except Exception:
        return value
