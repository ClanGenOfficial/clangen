# -*- mode: python ; coding: utf-8 -*-


block_cipher = None

b = Analysis(
    ['winupdate.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyzb = PYZ(b.pure, b.zipped_data, cipher=block_cipher)

exeb = EXE(
    pyzb,
    b.scripts,
    b.binaries,
    b.zipfiles,
    b.datas,
    [],
    name='winupdate',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

a.datas += Tree('./resources', prefix='resources')
a.datas += Tree('./sprites', prefix='sprites')
a.datas += [ ('commit.txt', './commit.txt', 'DATA') ]
a.datas += [ ('OpenDataDirectory.bat', './bin/OpenDataDirectory.bat', 'DATA') ]

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Clangen',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='resources/images/icon.png',
)
coll = COLLECT(
    exe,
    exeb,
    a.binaries + b.binaries,
    a.zipfiles + b.zipfiles,
    a.datas + b.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='Clangen',
)
app = BUNDLE(
    coll,
    name='Clangen.app',
    icon='resources/images/icon.png',
    bundle_identifier=None,
)
