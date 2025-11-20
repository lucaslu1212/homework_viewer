#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
作业查看器系统打包脚本
使用 PyInstaller 将整个系统打包成 exe 文件
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def install_pyinstaller():
    """安装 PyInstaller"""
    print("正在安装 PyInstaller...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✓ PyInstaller 安装成功")
        return True
    except subprocess.CalledProcessError:
        print("✗ PyInstaller 安装失败")
        return False

def clean_build_dirs():
    """清理构建目录"""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"✓ 清理目录: {dir_name}")

def create_spec_file():
    """创建 PyInstaller spec 文件"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['launcher.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('demo_data.json', '.'),
        ('student', 'student'),
        ('teacher', 'teacher'),
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
        'teacher.teacher_gui',
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
    name='作业查看器系统',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 设为 False 隐藏控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # 可以指定图标文件路径
)
'''
    
    with open('作业查看器系统.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    print("✓ 创建 spec 文件成功")

def build_executable():
    """构建可执行文件"""
    print("开始构建 exe 文件...")
    try:
        # 使用 spec 文件构建
        subprocess.check_call([
            sys.executable, "-m", "PyInstaller",
            "--clean",
            "作业查看器系统.spec"
        ])
        print("✓ exe 文件构建成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ 构建失败: {e}")
        return False

def create_portable_package():
    """创建便携版包"""
    print("创建便携版包...")
    
    # 创建便携版目录
    portable_dir = "作业查看器系统_便携版"
    if os.path.exists(portable_dir):
        shutil.rmtree(portable_dir)
    
    os.makedirs(portable_dir)
    
    # 复制 exe 文件
    exe_source = os.path.join("dist", "作业查看器系统.exe")
    if os.path.exists(exe_source):
        shutil.copy2(exe_source, portable_dir)
        print(f"✓ 复制 exe 文件到 {portable_dir}")
    
    # 复制必要的数据文件
    data_files = ["demo_data.json", "README.md"]
    for file in data_files:
        if os.path.exists(file):
            shutil.copy2(file, portable_dir)
            print(f"✓ 复制数据文件: {file}")
    
    # 复制说明文档
    doc_files = ["打包说明.txt"]
    for file in doc_files:
        if os.path.exists(file):
            shutil.copy2(file, portable_dir)
            print(f"✓ 复制文档文件: {file}")
    
    # 创建使用说明
    usage_content = '''作业查看器系统 - 便携版

使用说明:
1. 双击 "作业查看器系统.exe" 启动程序
2. 先启动老师端，再启动学生端
3. 按照界面提示操作即可

注意事项:
- 确保老师端和学生端在同一局域网
- 首次运行可能需要防火墙允许
- 数据会自动保存在程序目录下

技术支持:
- 详细文档请查看 README.md
- 演示数据文件: demo_data.json

版本: 1.0
构建时间: {}
'''.format(subprocess.check_output(['date'], shell=True, text=True).strip())
    
    with open(os.path.join(portable_dir, "使用说明.txt"), 'w', encoding='utf-8') as f:
        f.write(usage_content)
    
    print("✓ 便携版包创建完成")

def main():
    """主函数"""
    print("=" * 50)
    print("    作业查看器系统 - EXE 打包工具")
    print("=" * 50)
    print()
    
    # 检查当前目录
    if not os.path.exists("launcher.py"):
        print("错误: 未找到 launcher.py 文件")
        print("请在 homework_viewer 目录下运行此脚本")
        return
    
    # 安装 PyInstaller
    if not install_pyinstaller():
        return
    
    # 清理构建目录
    clean_build_dirs()
    
    # 创建 spec 文件
    create_spec_file()
    
    # 构建可执行文件
    if not build_executable():
        return
    
    # 创建便携版包
    create_portable_package()
    
    print()
    print("=" * 50)
    print("  打包完成！")
    print("=" * 50)
    print()
    print("文件位置:")
    print("- exe 文件: dist/作业查看器系统.exe")
    print("- 便携版包: 作业查看器系统_便携版/")
    print()
    print("你可以:")
    print("1. 直接使用 dist 目录下的 exe 文件")
    print("2. 使用便携版包，可以复制到其他电脑")
    print()

if __name__ == "__main__":
    main()