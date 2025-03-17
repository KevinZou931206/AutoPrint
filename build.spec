# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['ui.py'],  # 主入口文件
    pathex=[],
    binaries=[('chromedriver.exe', '.')],  # 包含chromedriver.exe
    datas=[
        ('icon.ico', '.'),  # 图标文件
    ],
    hiddenimports=[
        'PyQt6', 
        'PyQt6.QtCore', 
        'PyQt6.QtWidgets', 
        'PyQt6.QtGui', 
        'PyQt6.sip',
        'PyQt6.QtNetwork',
        'email.mime.text',
        'email.mime.multipart',
        'email.header',
        'email.utils',
        'smtplib',
        'version',  # 添加版本模块
    ],  # 添加所有必要的隐藏依赖
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# 创建空的logs目录
import os
import shutil
if not os.path.exists('logs'):
    os.makedirs('logs')
# 添加空logs目录到数据文件
a.datas += [('logs/.keep', '', 'DATA')]

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='自动化打单配货程序',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # 无控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='自动化打单配货程序',
) 