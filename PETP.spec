# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['PETP.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports= $hidden_imports$,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [('v', None, 'OPTION')],
    name='PETP',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    icon='./image/favicon-32x32.png',
    codesign_identity=None,
    entitlements_file=None,
)
