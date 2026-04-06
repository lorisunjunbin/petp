# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for PETP_backgroud.py (no-GUI / background mode)
from PyInstaller.utils.hooks import collect_all, collect_submodules

block_cipher = None

# Collect all submodules from known-problematic packages
submodules = []
for module in ['numpy', 'pandas', 'selenium', 'PIL', 'requests']:
    submodules.extend(collect_submodules(module))

# Collect data files + binaries from those packages
datas = []
binaries = []
for module in ['numpy', 'pandas', 'selenium', 'PIL', 'requests']:
    try:
        module_data = collect_all(module)
        datas.extend(module_data[0])
        binaries.extend(module_data[1])
    except Exception:
        pass

# Application-specific data directories
for src, dest in [('config', 'config'), ('core/executions', 'core/executions'), ('image', 'image'), ('resources', 'resources')]:
    datas.append((src, dest))

a = Analysis(
    ['PETP_backgroud.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=['utils', 'sqlite3', 'requests', 'core.processors.sub.dbprocessors.BaseDBAccess', 'encodings', 'pkg_resources.py2_warn', 'packaging', 'packaging.version', 'numpy.core._methods', 'numpy.lib.format', 'appdirs', 'engineio.async_drivers.threading', 'engineio.async_drivers.eventlet', 'socketio.async_drivers.threading', 'engineio.async_drivers', 'json', 'urllib3', 'xml', 'xmlrpc', 'asyncio.base_subprocess', 'asyncio.subprocess', 'asyncio.proactor_events', 'argparse', 'signal', 'threading', 'core.runtime.BackgroundRuntime', 'core.runtime.UiProcessorPolicy', 'httpservice.BackgroundHttpServer', 'mvp.model.PETPModel', 'yaml', 'wx.lib.colourutils', 'core', 'logging', 'importlib', 'wx.dataview', 'mimetypes', 'datetime', 'jsonpath', 'PIL', 'http', 'pythonmonkey', 'uuid', 'AppKit', 'zipfile', 'time', 'collections', 'langchain_google_genai', 'asyncio', 'wx.adv', 'shutil', 'paramiko', 'matplotlib.figure', 'concurrent.futures', 'importlib.util', 'flask_httpauth', 'smtplib', 'glob', 'functools', 'matplotlib', 'cryptocode', 'ssl', 'psutil', 'zai', 'pyperclip', 'csv', 'ollama', 'pytube', 'selenium', 'utils.Logger', 'flask', 'decorators', 'langchain_core', 'wx', 'platform', 'cron_descriptor', 'mvp', 'subprocess', 'urllib', 'httpservice', 'typing', 'base64', 'pyautogui', 'hashlib', 'wx.grid', 'mcp', 'binascii', 'email', 'traceback', 'concurrent', 'mcp.types', 'openpyxl', 'uvicorn', 'weakref', 'fastapi', 'croniter', 'types', 'openai', 'wx.propgrid', 'bs4', 'config', 'ctypes', 'werkzeug', 'pandas', 'numpy', 'lxml', 'cryptography', 'sqlalchemy', 'utils.ParamikoUtil', 'utils.GlobalStore', 'utils.SeleniumUtil', 'utils.WordUtil', 'utils.SystemConfig', 'utils.ExcelUtil', 'utils.DateUtil', 'utils.CodeExplainerUtil', 'utils.OSUtils'] + submodules,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['botocore', 'notebook', 'ipython', 'wx', 'tkinter', 'PyQt5', 'PySide2'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='PETP_background',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,           # background / headless — keep console visible
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='PETP_background',
)

