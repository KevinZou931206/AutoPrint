block_cipher = None

a = Analysis(
    ['ui.py'],
    pathex=[],
    binaries=[
        ('chromedriver.exe', '.')  # 包含 ChromeDriver
    ],
    datas=[],
    hiddenimports=[
        'PyQt6.QtCore',
        'PyQt6.QtWidgets',
        'selenium.webdriver',
        'loguru',
        'python-dotenv'
    ],
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

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='自动化打单配货程序',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 关闭控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico'  # 添加图标
) 