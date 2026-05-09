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


def build_view():
    view = PETPView(None, wx.ID_ANY, "")

    try:
        screen = wx.Display(0).GetGeometry()
        win_w = max(1200, int(screen.width * 0.80))
        win_h = max(700, int(screen.height * 0.80))
        view.SetSize((win_w, win_h))
        view.Centre()
        logging.info(f'Init PETPView - {win_w}x{win_h} (screen: {screen.width}x{screen.height})')
    except Exception as e:
        logging.warning(f'Could not determine screen size, keeping default window size: {e}')

    return view


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


def start_app():
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

    view.Show()

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
