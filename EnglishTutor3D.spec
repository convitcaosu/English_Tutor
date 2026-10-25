# -*- mode: python ; coding: utf-8 -*-
import os
import panda3d
from PyInstaller.utils.hooks import collect_all

datas = []
binaries = []
hiddenimports = ['ursina', 'speech_recognition', 'pyttsx3', 'pyttsx3.drivers', 'pyttsx3.drivers.sapi5', 'pyaudio', 'panda3d', 'direct']

for pkg in ('ursina', 'speech_recognition', 'pyttsx3', 'panda3d', 'direct'):
    tmp_ret = collect_all(pkg)
    datas += tmp_ret[0]
    binaries += tmp_ret[1]
    hiddenimports += tmp_ret[2]

panda_dir = os.path.dirname(panda3d.__file__)
panda_etc = os.path.join(panda_dir, 'etc')
if os.path.isdir(panda_etc):
    datas.append((panda_etc, 'panda3d/etc'))
    datas.append((panda_etc, 'etc'))

a = Analysis(
    ['avatar3d.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='EnglishTutor3D',
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
    codesign_identity=None,
    entitlements_file=None,
)
