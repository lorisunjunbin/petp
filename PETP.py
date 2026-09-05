import logging
import os
import platform
import sys

if getattr(sys, 'frozen', False) and sys.platform == 'darwin':
    _bundle_resources = os.path.join(os.path.dirname(sys.executable), '..', 'Resources')
    os.chdir(os.path.abspath(_bundle_resources))
    import shutil
    import filecmp
    from datetime import datetime as _dt
    from utils.AppPaths import get_user_data_dir as _get_data_dir
    _data_dir = _get_data_dir()
    if not os.path.exists(os.path.join(_data_dir, 'config', 'petpconfig.yaml')):
        for _subdir in ['config', 'core/executions', 'core/pipelines', 'log', 'download']:
            _src = os.path.join(os.path.realpath('.'), _subdir)
            _dst = os.path.join(_data_dir, _subdir)
            if os.path.isdir(_src):
                shutil.copytree(_src, _dst, dirs_exist_ok=True)
            else:
                os.makedirs(_dst, exist_ok=True)
    else:
        _ts = _dt.now().strftime('%Y%m%d%H%M%S')
        for _subdir in ['core/executions', 'core/pipelines']:
            _src_dir = os.path.join(os.path.realpath('.'), _subdir)
            _dst_dir = os.path.join(_data_dir, _subdir)
            if not os.path.isdir(_src_dir):
                continue
            os.makedirs(_dst_dir, exist_ok=True)
            for _f in os.listdir(_src_dir):
                if not _f.endswith('.yaml'):
                    continue
                _src_file = os.path.join(_src_dir, _f)
                _dst_file = os.path.join(_dst_dir, _f)
                if not os.path.isfile(_src_file):
                    continue
                if not os.path.exists(_dst_file):
                    shutil.copy2(_src_file, _dst_file)
                elif not filecmp.cmp(_src_file, _dst_file, shallow=False):
                    _name, _ext = os.path.splitext(_f)
                    _prefix = _name + '_'
                    _existing = [
                        _ef for _ef in os.listdir(_dst_dir)
                        if _ef.startswith(_prefix) and _ef.endswith(_ext)
                    ]
                    if _existing:
                        _target = os.path.join(_dst_dir, _existing[0])
                        if not filecmp.cmp(_src_file, _target, shallow=False):
                            shutil.copy2(_src_file, _target)
                    else:
                        shutil.copy2(_src_file, os.path.join(_dst_dir, f'{_name}_{_ts}{_ext}'))

        import yaml as _yaml
        _bundle_cfg = os.path.join(os.path.realpath('.'), 'config', 'petpconfig.yaml')
        _user_cfg = os.path.join(_data_dir, 'config', 'petpconfig.yaml')
        if os.path.isfile(_bundle_cfg) and os.path.isfile(_user_cfg):
            with open(_bundle_cfg, 'r', encoding='utf8') as _bf:
                _bundle_doc = _yaml.safe_load(_bf) or {}
            with open(_user_cfg, 'r', encoding='utf8') as _uf:
                _user_doc = _yaml.safe_load(_uf) or {}
            _merged = False
            for _section, _bundle_vals in _bundle_doc.items():
                if not isinstance(_bundle_vals, dict):
                    continue
                if _section not in _user_doc:
                    _user_doc[_section] = _bundle_vals
                    _merged = True
                else:
                    for _k, _v in _bundle_vals.items():
                        if _k not in _user_doc[_section]:
                            _user_doc[_section][_k] = _v
                            _merged = True
            if _merged:
                with open(_user_cfg, 'w', encoding='utf8') as _uf:
                    _yaml.dump(_user_doc, _uf, default_flow_style=False, sort_keys=False, allow_unicode=True)

import wx

import utils.Logger as Logger

from mvp.model.PETPModel import PETPModel
from mvp.presenter.PETPInteractor import PETPInteractor
from mvp.presenter.PETPPresenter import PETPPresenter
from mvp.view.PETPView import PETPView
from utils.DateUtil import DateUtil
from httpservice.HttpServer import HttpServer
from utils.OSUtils import OSUtils
from i18n.translations import set_locale
from utils.SystemConfig import SystemConfig


def init_log():
    Logger.init('petp')
    logging.info("\n\n")
    logging.info(">>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    logging.info("PETP starting @ " + DateUtil.get_now_in_str("%Y-%m-%d %H:%M:%S"))


def init_display():
    OSUtils.ensure_hdpi()  # only run on windows & use autogui and canvas.


def set_log_level(m: PETPModel) -> None:
    log_level_str = getattr(m, 'log_level')
    logging.getLogger().setLevel(logging.getLevelName(log_level_str))
    getattr(logging, log_level_str.lower())('Default log level is <' + log_level_str + '>')


def setup_windows_display(m: PETPModel):
    enabled = True if getattr(m, 'enable_windows_hdpi') else False
    if enabled:
        OSUtils.ensure_hdpi()


def build_model():
    config = SystemConfig("petpconfig.yaml")
    return PETPModel(config)


def _windows_scale_from_registry():
    """Real system DPI scale from the registry (e.g. 1.5 at 150%).

    On RDP sessions the display DPI arrives asynchronously: every runtime
    API (GetDpiForSystem / GetDpiForMonitor / wx ToDIP) still reports 96
    while a window created in that window of time gets migrated later
    (WM_DPICHANGED) and re-scaled — the visible size jump. The registry
    AppliedDPI value is written at logon and is the reliable truth.
    Returns 1.0 on non-Windows or any failure.
    """
    if platform.system() != "Windows":
        return 1.0
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                            r"Control Panel\Desktop\WindowMetrics") as k:
            applied, _ = winreg.QueryValueEx(k, "AppliedDPI")
        return max(1.0, applied / 96.0)
    except Exception:
        return 1.0


def build_view():
    view = PETPView(None, wx.ID_ANY, "")

    try:
        screen = wx.Display(0).GetGeometry()
        # GetGeometry() returns PHYSICAL pixels; SetSize() expects DIPs on
        # DPI-aware wx 3.3+. Convert with the registry scale — the window is
        # not on screen yet, so view.ToDIP() still assumes 96 DPI and would
        # return the physical value unchanged (oversized window + later
        # re-scale = the visible "shrink" jump).
        scale = _windows_scale_from_registry()
        win_w = max(1200, int(screen.width * 0.80 / scale))
        win_h = max(700, int(screen.height * 0.80 / scale))
        view.SetSize((win_w, win_h))
        view.Centre()
        logging.info(f'Init PETPView - {win_w}x{win_h} DIP (screen: {screen.width}x{screen.height} physical, scale {scale})')
    except Exception as e:
        logging.warning(f'Could not determine screen size, keeping default window size: {e}')

    return view


def _show_when_dpi_stable(view, timeout_ms=4000):
    """Show the frame only after the display DPI has settled (Windows).

    On some setups (typically RDP) the monitor's real DPI arrives a second
    or two after process start; a window that is already visible then gets
    migrated (WM_DPICHANGED) and re-scaled on screen — the visible
    "window jumps to a smaller size" effect. Keep the frame hidden, pump
    events until its DPI matches the logon registry value (or timeout),
    re-apply the intended physical size with the now-correct scale, and
    only then Show() — one clean appearance, no jump. On machines where
    DPI is stable from the start the wait exits immediately.
    """
    if platform.system() != "Windows":
        view.Show()
        return
    import ctypes
    import time as _time
    target = int(round(_windows_scale_from_registry() * 96))
    t0 = _time.time()
    while _time.time() - t0 < timeout_ms / 1000.0:
        wx.Yield()
        try:
            cur = ctypes.windll.user32.GetDpiForWindow(view.GetHandle())
        except Exception:
            cur = 0
        if cur and abs(cur - target) <= 1:
            break
        _time.sleep(0.05)
    try:
        screen = wx.Display(0).GetGeometry()
        want_w, want_h = int(screen.width * 0.80), int(screen.height * 0.80)
        # Set the PHYSICAL size via Win32 directly. wx's DIP bookkeeping for a
        # still-hidden frame can lag the settled Win32 DPI on RDP (scale
        # reports 1.5 but SetSize renders 1:1), so DIP math lands wrong;
        # MoveWindow takes physical pixels and is unambiguous for a
        # per-monitor-aware process.
        import ctypes
        from ctypes import wintypes

        class _MONITORINFO(ctypes.Structure):
            _fields_ = [("cbSize", wintypes.DWORD),
                        ("rcMonitor", wintypes.RECT),
                        ("rcWork", wintypes.RECT),
                        ("dwFlags", wintypes.DWORD)]

        hwnd = view.GetHandle()
        mon = ctypes.windll.user32.MonitorFromWindow(hwnd, 1)
        mi = _MONITORINFO()
        mi.cbSize = ctypes.sizeof(mi)
        ctypes.windll.user32.GetMonitorInfoW(mon, ctypes.byref(mi))
        mx = (mi.rcWork.left + mi.rcWork.right - want_w) // 2
        my = (mi.rcWork.top + mi.rcWork.bottom - want_h) // 2
        ctypes.windll.user32.MoveWindow(hwnd, mx, my, want_w, want_h, True)
        logging.info(f'Show PETPView at {want_w}x{want_h} physical '
                     f'(DPI settled: {cur} target {target})')
    except Exception as e:
        logging.warning(f're-apply size before Show failed: {e}')
    view.Show()


def build_presenter(model, view):
    return PETPPresenter(model, view, PETPInteractor())


def _set_macos_app_name(name: str):
    """Override the macOS bundle display name so the Dock shows 'PETP' instead of 'Python'.
    Uses PyObjC's AppKit which ships with macOS system Python and most virtual environments."""
    try:
        from AppKit import NSBundle
        bundle = NSBundle.mainBundle()
        info = bundle.localizedInfoDictionary() or bundle.infoDictionary()
        info['CFBundleName'] = name
        info['CFBundleDisplayName'] = name
    except Exception as e:
        logging.warning(f'Could not set macOS app name via AppKit: {e}')


def _ensure_windows_dpi_aware():
    """Set PER_MONITOR_AWARE_V2 before any window exists.

    On RDP sessions the display DPI arrives asynchronously: a window created
    while the process is still DPI-unaware starts at 96 DPI, then Windows
    migrates it (WM_DPICHANGED) and re-scales its physical size — the visible
    "big window shrinks" jump. Setting awareness at the very entry (before
    importing/creating any wx window) makes windows initialize at the real
    DPI from the start. Windows-only; no-op elsewhere.
    """
    if platform.system() == "Windows":
        try:
            import ctypes
            try:
                ctypes.windll.user32.SetProcessDpiAwarenessContext(-4)  # PER_MONITOR_AWARE_V2
            except Exception:
                ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except Exception as e:
            logging.warning(f'set DPI awareness failed: {e}')


def start_app():
    _ensure_windows_dpi_aware()
    app = wx.App(False)
    # Set the app name shown in the menu bar and task switcher
    app.SetAppName('PETP')
    app.SetAppDisplayName('PETP')
    # On macOS, also patch the NSBundle info dict so the Dock shows 'PETP' not 'Python'
    if platform.system() == 'Darwin':
        _set_macos_app_name('PETP')

    model: PETPModel = build_model()
    set_locale(getattr(model, 'language', 'zh'))
    view: PETPView = build_view()
    presenter: PETPPresenter = build_presenter(model, view)

    _show_when_dpi_stable(view)

    logging.info(f'PETP is running on {platform.architecture()[0]} platform')

    set_log_level(model)
    setup_windows_display(model)

    # start the http server
    httpServer = HttpServer(presenter)
    httpServer.start()

    presenter.on_load_log()

    app.MainLoop()

    httpServer.stop()
    logging.info('PETP is shutdown @' + DateUtil.get_now_in_str("%Y-%m-%d %H:%M:%S"))
    logging.info("<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
    os._exit(0)


if __name__ == '__main__':
    init_log()
    start_app()
