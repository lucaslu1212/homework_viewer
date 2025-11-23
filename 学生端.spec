# -*- mode: python ; coding: utf-8 -*-

# 加密模块，当前未启用
block_cipher = None

# 分析阶段：收集脚本、依赖、数据文件等
a = Analysis(
    ['student/student_gui.py'],   # 主入口脚本
    pathex=[],                    # 额外模块搜索路径
    binaries=[],                  # 需要打包的二进制文件
    datas=[
        ('demo_data.json', '.'),  # 将 demo_data.json 打包到根目录
        ('student', 'student'),   # 将 student 文件夹整体打包到 student 目录
    ],
    hiddenimports=[               # 显式声明的隐式导入模块
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
        'PIL',
        'PIL.Image',
        'os',
    ],
    hookspath=[],        # 自定义 hook 路径
    hooksconfig={},      # hook 配置
    runtime_hooks=[],    # 运行时 hook
    excludes=[],         # 排除的模块
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,     # 不关闭归档，减少体积
)

# 生成 PYZ 归档：将纯 Python 模块压缩
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# 生成最终可执行文件
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],                            # 额外依赖项
    name='学生端-作业查看器',       # 生成的 exe 文件名
    debug=False,                   # 关闭调试模式
    bootloader_ignore_signals=False,
    strip=False,                   # 不剥离符号
    upx=True,                      # 使用 UPX 压缩
    upx_exclude=[],                # 不被 UPX 压缩的文件
    runtime_tmpdir=None,           # 运行时临时目录
    console=False,                 # 不显示控制台窗口（GUI 模式）
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,              # 目标架构，默认当前
    codesign_identity=None,        # 代码签名身份（macOS）
    entitlements_file=None,        # 权限文件（macOS）
    icon='student.png',            # 应用图标
)
