# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['student/student_gui.py'],
    pathex=['C:\\Users\\Lucas\\Desktop\\fan\\homework_viewer'],  # 添加脚本所在目录到pathex
    binaries=[],
    datas=[
        ('demo_data.json', '.'),
        ('student_data.json', '.'),
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
        'student.student_gui',
        'pystray',
        'pystray._win32',  # 添加pystray的Windows实现
        'pystray._win32.lib',  # 添加pystray Windows库
        'pystray._win32.constants',  # 添加pystray Windows常量
        'PIL',
        'PIL.Image',
        'PIL.ImageTk',
        'PIL._imagingtk',  # 添加PIL的Tkinter支持
        'PIL._tkinter_finder',
        'os',
        'sys',
        'time',
        'inspect',  # 确保inspect模块被包含
        # 添加win32相关模块支持单实例检测
        'win32event',
        'win32api',
        'winerror',
        'traceback',
        'ctypes',
        'ctypes.wintypes',
        'win32gui',  # 添加更多win32相关模块
        'win32con',
        'win32process'
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
    name='学生端-作业查看器',
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
    icon='student.png',
)
