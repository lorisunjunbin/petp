# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all, collect_submodules

block_cipher = None

# Collect all submodules from problematic packages
submodules = []
for module in $collect_submodules$:
    submodules.extend(collect_submodules(module))

# Get all related data files from problematic modules
datas = []
binaries = []
for module in $collect_submodules$:
    try:
        module_data = collect_all(module)
        datas.extend(module_data[0])
        binaries.extend(module_data[1])
        # We'll add these imports separately
    except:
        pass

# Add application-specific data files
for src, dest in $data_dirs$:
    datas.append((src, dest))

a = Analysis(
    ['PETP.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports= $hidden_imports$ + submodules,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['botocore', 'notebook', 'ipython'],
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
    exclude_binaries=True,  # Changed to True for better file organization
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
    icon='./image/petp.png',
    codesign_identity=None,
    entitlements_file=None,
)

# Using COLLECT creates a folder with all files separate, 
# which helps avoid filename length issues on Windows
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='PETP',
)
