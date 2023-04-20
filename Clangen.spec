# -*- mode: python ; coding: utf-8 -*-

from os import getenv


is_release = getenv('IS_RELEASE', '1') == '1'
block_cipher = None

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
a.datas += [ ('version.ini', './version.ini', 'DATA') ]
a.datas += [ ('changelog.txt', './changelog.txt', 'DATA') ]
a.datas += [ ('OpenDataDirectory.bat', './bin/OpenDataDirectory.bat', 'DATA') ]
a.datas += [ ('.itch.toml', './.itch.toml', 'DATA') ]

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
    console=False if is_release else True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='resources/images/icon.png',
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='Clangen',
)
app = BUNDLE(
    coll,
    name='Clangen.app',
    icon='resources/images/icon.png',
    bundle_identifier='com.sablesteel.clangen',
    version='0.7.5' # imo we should give dev builds .5
)
