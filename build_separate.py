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
import stat
import time  # 添加time模块用于在删除操作后添加延迟

def create_teacher_spec():
    """创建教师端PyInstaller spec文件"""
    # 获取脚本所在目录，确保使用绝对路径
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 使用正斜杠或双反斜杠来避免Unicode转义错误
    script_dir_escaped = script_dir.replace('\\', '\\\\')
    teacher_gui_path = os.path.join('teacher', 'teacher_gui.py').replace('\\', '/')
    demo_data_path = 'demo_data.json'
    teacher_data_path = os.path.join('teacher', 'teacher_data.json').replace('\\', '/')
    
    # 在spec文件中直接配置upx=False，而不是通过命令行参数
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['{teacher_gui_path}'],
    pathex=['{script_dir_escaped}'],  # 添加脚本所在目录到pathex
    binaries=[],
    datas=[
        ('{demo_data_path}', '.'),
        ('{teacher_data_path}', 'teacher'),
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
    hooksconfig={{}},
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
'''
    
    with open('教师端.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    print("✓ 创建教师端spec文件成功")

def create_student_spec():
    """创建学生端PyInstaller spec文件"""
    # 获取脚本所在目录，确保使用绝对路径
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 使用正斜杠或双反斜杠来避免Unicode转义错误
    script_dir_escaped = script_dir.replace('\\', '\\\\')
    student_gui_path = os.path.join('student', 'student_gui.py').replace('\\', '/')
    demo_data_path = 'demo_data.json'
    student_data_path = 'student_data.json'
    student_icon_path = 'student.png'  # 图标文件相对路径
    
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['{student_gui_path}'],
    pathex=['{script_dir_escaped}'],  # 添加脚本所在目录到pathex
    binaries=[],
    datas=[
        ('{demo_data_path}', '.'),
        ('{student_data_path}', '.'),
        ('{student_icon_path}', '.'),
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
        'win32process',
        'wmi'  # 添加wmi模块用于U盘检测
    ],
    hookspath=[],
    hooksconfig={{}},
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
    icon='{student_icon_path}',
)
'''
    
    with open('学生端.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    print("✓ 创建学生端spec文件成功")

def on_rm_error(func, path, exc_info):
    """处理删除文件时的权限错误"""
    # 尝试更改权限并重新执行操作
    try:
        if not os.access(path, os.W_OK):
            os.chmod(path, stat.S_IWUSR)
            time.sleep(0.1)  # 添加小延迟以确保权限更改生效
        func(path)
    except Exception as e:
        print(f"⚠ 删除文件失败: {path} - {e}")
        # 尝试直接使用os.remove作为备选方案
        if os.path.isfile(path):
            try:
                os.remove(path)
                print(f"  备选方法: 成功删除文件 {path}")
            except:
                pass

def clean_build_dirs():
    """清理构建目录"""
    # 获取当前脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    dirs_to_clean = ['build', 'dist', '__pycache__']
    
    for dir_name in dirs_to_clean:
        # 构建绝对路径
        dir_path = os.path.join(script_dir, dir_name)
        if os.path.exists(dir_path):
            try:
                # 使用错误处理函数确保即使有权限问题也能尝试删除
                shutil.rmtree(dir_path, onerror=on_rm_error)
                print(f"✓ 清理目录: {dir_name}")
                time.sleep(0.3)  # 添加延迟确保文件锁释放
            except PermissionError:
                print(f"⚠ 无法清理目录: {dir_name} (可能被占用)")
                # 尝试再次删除
                time.sleep(0.5)
                try:
                    shutil.rmtree(dir_path, onerror=on_rm_error)
                    print(f"✓ 重试后清理目录: {dir_name}")
                except:
                    pass
            except Exception as e:
                print(f"⚠ 清理目录失败: {dir_name} - {e}")
    
    # 最终延迟确保所有目录清理完成
    time.sleep(0.5)

def build_teacher_exe():
    """构建教师端exe文件"""
    print("开始构建教师端exe文件...")
    # 获取当前脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    spec_path = os.path.join(script_dir, "教师端.spec")
    
    try:
        # 确保在正确的目录下执行
        subprocess.check_call([
            sys.executable, "-m", "PyInstaller",
            "--clean",
            spec_path
        ], cwd=script_dir)  # 指定工作目录
        print("✓ 教师端exe文件构建成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ 教师端构建失败: {e}")
        return False
    except FileNotFoundError:
        print("✗ 未找到PyInstaller模块，请确保已安装")
        return False
    except Exception as e:
        print(f"✗ 构建过程中发生未知错误: {e}")
        return False

def build_student_exe():
    """构建学生端exe文件"""
    print("开始构建学生端exe文件...")
    # 获取当前脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 确保先创建或更新spec文件
    create_student_spec()
    
    spec_path = os.path.join(script_dir, "学生端.spec")
    
    try:
        # 确保在正确的目录下执行
        subprocess.check_call([
            sys.executable, "-m", "PyInstaller",
            "--clean",
            spec_path
        ], cwd=script_dir)  # 指定工作目录
        print("✓ 学生端exe文件构建成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ 学生端构建失败: {e}")
        print("尝试重新创建spec文件并再次构建...")
        # 重新创建spec文件
        create_student_spec()
        try:
            # 再次尝试构建
            subprocess.check_call([
                sys.executable, "-m", "PyInstaller",
                "--clean",
                spec_path
            ], cwd=script_dir)
            print("✓ 学生端exe文件构建成功")
            return True
        except subprocess.CalledProcessError as e2:
            print(f"✗ 学生端重新构建也失败: {e2}")
            return False
    except FileNotFoundError:
        print("✗ 未找到PyInstaller模块，请确保已安装")
        return False
    except Exception as e:
        print(f"✗ 构建过程中发生未知错误: {e}")
        return False

def create_teacher_portable():
    """创建教师端便携版"""
    print("创建教师端便携版...")
    
    # 获取当前脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    portable_dir = os.path.join(script_dir, "教师端_便携版")
    
    # 安全删除旧目录
    if os.path.exists(portable_dir):
        try:
            shutil.rmtree(portable_dir, onerror=on_rm_error)
            print(f"✓ 已删除旧便携版目录")
        except Exception as e:
            print(f"⚠ 删除旧便携版目录失败: {e}")
    
    # 确保便携版目录存在，无论之前的删除是否成功
    try:
        os.makedirs(portable_dir, exist_ok=True)
        print(f"✓ 已创建便携版目录: {portable_dir}")
    except Exception as e:
        print(f"✗ 无法创建便携版目录: {e}")
        return
    
    # 复制exe文件
    exe_source = os.path.join(script_dir, "dist", "教师端-作业查看器.exe")
    exe_dest = os.path.join(portable_dir, "教师端-作业查看器.exe")
    if os.path.exists(exe_source):
        try:
            shutil.copy2(exe_source, exe_dest)
            print(f"✓ 复制教师端exe文件到 {portable_dir}")
        except Exception as e:
            print(f"✗ 复制exe文件失败: {e}")
    else:
        print(f"✗ 未找到教师端exe文件: {exe_source}")
    
    # 复制必要文件
    files_to_copy = ["demo_data.json", "README.md"]
    for file in files_to_copy:
        file_source = os.path.join(script_dir, file)
        file_dest = os.path.join(portable_dir, file)
        if os.path.exists(file_source):
            try:
                shutil.copy2(file_source, file_dest)
                print(f"✓ 复制文件: {file}")
            except Exception as e:
                print(f"⚠ 复制文件失败: {file} - {e}")
    
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
    
    try:
        with open(os.path.join(portable_dir, "教师端使用说明.txt"), 'w', encoding='utf-8') as f:
            f.write(usage_content)
        print("✓ 教师端便携版创建完成")
    except Exception as e:
        print(f"✗ 创建使用说明失败: {e}")

def create_student_portable():
    """创建学生端便携版"""
    print("创建学生端便携版...")
    
    # 获取当前脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    portable_dir = os.path.join(script_dir, "学生端_便携版")
    
    # 安全删除旧目录
    if os.path.exists(portable_dir):
        try:
            shutil.rmtree(portable_dir, onerror=on_rm_error)
            print(f"✓ 已删除旧便携版目录")
        except Exception as e:
            print(f"⚠ 删除旧便携版目录失败: {e}")
    
    # 确保便携版目录存在，无论之前的删除是否成功
    try:
        os.makedirs(portable_dir, exist_ok=True)
        print(f"✓ 已创建便携版目录: {portable_dir}")
    except Exception as e:
        print(f"✗ 无法创建便携版目录: {e}")
        return
    
    # 复制exe文件
    exe_source = os.path.join(script_dir, "dist", "学生端-作业查看器.exe")
    exe_dest = os.path.join(portable_dir, "学生端-作业查看器.exe")
    if os.path.exists(exe_source):
        try:
            shutil.copy2(exe_source, exe_dest)
            print(f"✓ 复制学生端exe文件到 {portable_dir}")
        except Exception as e:
            print(f"✗ 复制exe文件失败: {e}")
    else:
        print(f"✗ 未找到学生端exe文件: {exe_source}")
    
    # 复制必要文件
    files_to_copy = ["demo_data.json", "README.md"]
    for file in files_to_copy:
        file_source = os.path.join(script_dir, file)
        file_dest = os.path.join(portable_dir, file)
        if os.path.exists(file_source):
            try:
                shutil.copy2(file_source, file_dest)
                print(f"✓ 复制文件: {file}")
            except Exception as e:
                print(f"⚠ 复制文件失败: {file} - {e}")
    
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
    
    try:
        with open(os.path.join(portable_dir, "学生端使用说明.txt"), 'w', encoding='utf-8') as f:
            f.write(usage_content)
        print("✓ 学生端便携版创建完成")
    except Exception as e:
        print(f"✗ 创建使用说明失败: {e}")

def main():
    """主函数"""
    print("=" * 50)
    print("    作业查看器系统 - 分离打包工具")
    print("=" * 50)
    print()
    
    try:
        # 使用Path对象处理路径，提高跨平台兼容性
        script_path = Path(__file__).resolve()
        script_dir = script_path.parent
        
        # 切换到脚本所在目录，确保相对路径正确
        original_dir = Path.cwd()
        os.chdir(str(script_dir))
        
        # 检查必要的GUI文件
        teacher_gui_path = script_dir / "teacher" / "teacher_gui.py"
        student_gui_path = script_dir / "student" / "student_gui.py"
        
        if not teacher_gui_path.exists() or not student_gui_path.exists():
            print(f"错误: 未找到必要的GUI文件")
            print(f"当前目录: {Path.cwd()}")
            print(f"请在 homework_viewer 目录下运行此脚本")
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
        print(f"- 教师端: {script_dir / 'dist' / '教师端-作业查看器.exe'}")
        print(f"- 学生端: {script_dir / 'dist' / '学生端-作业查看器.exe'}")
        print(f"- 教师端便携版: {script_dir / '教师端_便携版'}/")
        print(f"- 学生端便携版: {script_dir / '学生端_便携版'}/")
        print()
        
    except Exception as e:
        print(f"✗ 打包过程中发生未处理的错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 确保恢复原始工作目录
        try:
            os.chdir(original_dir)
        except:
            pass

if __name__ == "__main__":
    main()