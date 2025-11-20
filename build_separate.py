#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
教师端EXE打包脚本
单独打包教师端功能为exe文件
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def create_teacher_spec():
    """创建教师端PyInstaller spec文件"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['teacher/teacher_gui.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('demo_data.json', '.'),
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
    name='教师端-作业查看器',
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
    icon=None,
)
'''
    
    with open('教师端.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    print("✓ 创建教师端spec文件成功")

def create_student_spec():
    """创建学生端PyInstaller spec文件"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['student/student_gui.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('demo_data.json', '.'),
        ('student', 'student'),
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
        'PIL',
        'PIL.Image',
        'os',
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
    name='学生端-作业查看器',
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
    icon=None,
)
'''
    
    with open('学生端.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    print("✓ 创建学生端spec文件成功")

def clean_build_dirs():
    """清理构建目录"""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            try:
                # 强制删除文件权限
                for root, dirs, files in os.walk(dir_name):
                    for file in files:
                        file_path = os.path.join(root, file)
                        try:
                            os.chmod(file_path, 0o777)  # 强制修改权限
                        except:
                            pass
                
                shutil.rmtree(dir_name)
                print(f"✓ 清理目录: {dir_name}")
            except PermissionError:
                print(f"⚠ 无法清理目录: {dir_name} (可能被占用)")
            except Exception as e:
                print(f"⚠ 清理目录失败: {dir_name} - {e}")

def build_teacher_exe():
    """构建教师端exe文件"""
    print("开始构建教师端exe文件...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "PyInstaller",
            "--clean",
            "教师端.spec"
        ])
        print("✓ 教师端exe文件构建成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ 教师端构建失败: {e}")
        return False

def build_student_exe():
    """构建学生端exe文件"""
    print("开始构建学生端exe文件...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "PyInstaller",
            "--clean",
            "学生端.spec"
        ])
        print("✓ 学生端exe文件构建成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ 学生端构建失败: {e}")
        return False

def create_teacher_portable():
    """创建教师端便携版"""
    print("创建教师端便携版...")
    
    portable_dir = "教师端_便携版"
    if os.path.exists(portable_dir):
        shutil.rmtree(portable_dir)
    
    os.makedirs(portable_dir)
    
    # 复制exe文件
    exe_source = os.path.join("dist", "教师端-作业查看器.exe")
    if os.path.exists(exe_source):
        shutil.copy2(exe_source, portable_dir)
        print(f"✓ 复制教师端exe文件到 {portable_dir}")
    
    # 复制必要文件
    files_to_copy = ["demo_data.json", "README.md"]
    for file in files_to_copy:
        if os.path.exists(file):
            shutil.copy2(file, portable_dir)
            print(f"✓ 复制文件: {file}")
    
    # 创建使用说明
    usage_content = '''教师端-作业查看器 便携版

教师端功能:
1. 启动局域网服务器
2. 选择学科和班级
3. 发送和管理作业
4. 查看学生留言
5. 数据统计功能
6. 全屏作业查看模式（新增）

使用说明:
1. 双击 "教师端-作业查看器.exe" 启动程序
2. 输入教师姓名和端口设置
3. 点击"启动服务器"
4. 按照界面提示操作

全屏查看功能:
- 点击"全屏模式"按钮进入全屏作业查看
- 全屏模式下显示所有作业列表
- 支持数据导出功能
- 按ESC键可快速退出全屏模式
- 全屏模式下窗口关闭时会先退出全屏

注意事项:
- 确保学生端在同一局域网
- 默认端口：8888
- 首次运行可能需要防火墙允许
- 数据自动保存在程序目录下
- 全屏功能提供了更好的作业查看体验

版本: 2.0 - 新增全屏作业查看模式
'''
    
    with open(os.path.join(portable_dir, "教师端使用说明.txt"), 'w', encoding='utf-8') as f:
        f.write(usage_content)
    
    print("✓ 教师端便携版创建完成")

def create_student_portable():
    """创建学生端便携版"""
    print("创建学生端便携版...")
    
    portable_dir = "学生端_便携版"
    if os.path.exists(portable_dir):
        shutil.rmtree(portable_dir)
    
    os.makedirs(portable_dir)
    
    # 复制exe文件
    exe_source = os.path.join("dist", "学生端-作业查看器.exe")
    if os.path.exists(exe_source):
        shutil.copy2(exe_source, portable_dir)
        print(f"✓ 复制学生端exe文件到 {portable_dir}")
    
    # 复制必要文件
    files_to_copy = ["demo_data.json", "README.md"]
    for file in files_to_copy:
        if os.path.exists(file):
            shutil.copy2(file, portable_dir)
            print(f"✓ 复制文件: {file}")
    
    # 创建使用说明
    usage_content = '''学生端-作业查看器 便携版

学生端功能:
1. 连接教师端服务器
2. 选择班级查看作业
3. 按学科筛选作业
4. 发送留言给教师
5. 实时接收新作业
6. 系统托盘后台运行（新增）

使用说明:
1. 双击 "学生端-作业查看器.exe" 启动程序
2. 输入教师端IP地址和学生姓名
3. 点击"连接服务器"
4. 选择对应班级开始使用

系统托盘功能:
- 勾选"后台运行"选项，关闭窗口时将最小化到系统托盘
- 双击托盘图标可快速恢复窗口
- 右键托盘图标显示操作菜单
- 老师连接/断开时会有托盘通知

注意事项:
- 需要知道教师端IP地址
- 确保与教师端在同一局域网
- 首次运行可能需要防火墙允许
- 数据自动保存在程序目录下
- 系统托盘功能需要PIL和pystray库支持

版本: 2.0 - 新增系统托盘后台运行功能
'''
    
    with open(os.path.join(portable_dir, "学生端使用说明.txt"), 'w', encoding='utf-8') as f:
        f.write(usage_content)
    
    print("✓ 学生端便携版创建完成")

def main():
    """主函数"""
    print("=" * 50)
    print("    作业查看器系统 - 分离打包工具")
    print("=" * 50)
    print()
    
    # 检查当前目录
    if not os.path.exists("teacher/teacher_gui.py") or not os.path.exists("student/student_gui.py"):
        print("错误: 未找到必要的GUI文件")
        print("请在 homework_viewer 目录下运行此脚本")
        return
    
    # 清理构建目录
    clean_build_dirs()
    
    # 创建spec文件
    create_teacher_spec()
    create_student_spec()
    
    # 打包教师端
    print("\n" + "="*30)
    print("  打包教师端")
    print("="*30)
    if not build_teacher_exe():
        print("教师端打包失败，跳过后续步骤")
        return
    
    # 创建教师端便携版
    create_teacher_portable()
    
    # 清理中间文件
    clean_build_dirs()
    
    # 打包学生端
    print("\n" + "="*30)
    print("  打包学生端")
    print("="*30)
    if not build_student_exe():
        print("学生端打包失败")
        return
    
    # 创建学生端便携版
    create_student_portable()
    
    print()
    print("=" * 50)
    print("  分离打包完成！")
    print("=" * 50)
    print()
    print("文件位置:")
    print("- 教师端: dist/教师端-作业查看器.exe")
    print("- 学生端: dist/学生端-作业查看器.exe")
    print("- 教师端便携版: 教师端_便携版/")
    print("- 学生端便携版: 学生端_便携版/")
    print()

if __name__ == "__main__":
    main()