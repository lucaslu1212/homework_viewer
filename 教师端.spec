# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['teacher/teacher_gui.py'],
    pathex=['C:\\Users\\Lucas\\Desktop\\fan\\homework_viewer'],  # 添加脚本所在目录到pathex
    binaries=[],
    datas=[
        ('demo_data.json', '.'),
        ('teacher/teacher_data.json', 'teacher'),
    ],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'tkinter.filedialog',
        'socket',
        'threading',
        'json',
        'datetime',
        'subprocess',
        'communication',
        'data_manager',
        'teacher.teacher_gui',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['pdb', 'doctest', 'unittest', 'difflib', 'trace', '__pycache__', '*.pyc', '*.pyo'],  # 移除inspect，因为它是必需的
    optimize=2,
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
    name='教师端-作业查看器',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
