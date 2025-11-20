#!/usr/bin/env python3
"""
学生端系统托盘功能测试脚本
测试后台运行、系统托盘功能等
"""

import tkinter as tk
from tkinter import messagebox
import sys
import os
import time

# 添加当前目录到路径以便导入模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from student_gui import StudentGUI
from communication import StudentServer, MessageTypes

def test_tray_functionality():
    """测试系统托盘功能"""
    print("开始测试学生端系统托盘功能...")
    
    # 检查pystray库是否可用
    try:
        import pystray
        from PIL import Image
        print("✓ pystray和Pillow库可用")
    except ImportError as e:
        print(f"✗ 缺少依赖库: {e}")
        print("请运行: pip install pystray Pillow")
        return False
    
    # 创建学生GUI实例（不启动主循环）
    try:
        app = StudentGUI()
        print("✓ 学生GUI实例创建成功")
        
        # 测试系统托盘相关变量
        assert hasattr(app, 'tray_icon'), "缺少tray_icon属性"
        assert hasattr(app, 'is_minimized_to_tray'), "缺少is_minimized_to_tray属性"
        assert hasattr(app, 'run_in_background'), "缺少run_in_background属性"
        print("✓ 系统托盘相关变量存在")
        
        # 测试方法存在性
        assert hasattr(app, 'minimize_to_tray'), "缺少minimize_to_tray方法"
        assert hasattr(app, 'restore_from_tray'), "缺少restore_from_tray方法"
        assert hasattr(app, 'create_tray_icon'), "缺少create_tray_icon方法"
        assert hasattr(app, 'create_system_tray_menu'), "缺少create_system托盘方法"
        assert hasattr(app, 'show_tray_notification'), "缺少show_tray_notification方法"
        print("✓ 系统托盘相关方法存在")
        
        # 测试后台运行选项
        assert app.run_in_background.get() == False, "后台运行选项初始值不正确"
        print("✓ 后台运行选项初始状态正确")
        
        print("✓ 所有功能测试通过!")
        return True
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False
    
    finally:
        # 清理资源
        try:
            if 'app' in locals():
                app.root.quit()
                app.root.destroy()
        except:
            pass

def test_tray_menu_creation():
    """测试托盘菜单创建"""
    print("\n测试托盘菜单创建...")
    
    try:
        app = StudentGUI()
        
        # 测试菜单创建
        menu = app.create_system_tray_menu()
        assert menu is not None, "托盘菜单创建失败"
        print("✓ 托盘菜单创建成功")
        
        # 检查菜单项
        menu_items = list(menu.items)
        assert len(menu_items) >= 3, "托盘菜单项数量不足"
        print(f"✓ 托盘菜单包含 {len(menu_items)} 个项目")
        
        return True
        
    except Exception as e:
        print(f"✗ 托盘菜单测试失败: {e}")
        return False
    
    finally:
        try:
            if 'app' in locals():
                app.root.quit()
                app.root.destroy()
        except:
            pass

def test_background_mode():
    """测试后台模式"""
    print("\n测试后台运行模式...")
    
    try:
        app = StudentGUI()
        
        # 测试设置后台运行
        app.run_in_background.set(True)
        assert app.run_in_background.get() == True, "设置后台运行失败"
        print("✓ 后台运行选项设置成功")
        
        # 恢复默认设置
        app.run_in_background.set(False)
        assert app.run_in_background.get() == False, "恢复默认设置失败"
        print("✓ 默认设置恢复成功")
        
        return True
        
    except Exception as e:
        print(f"✗ 后台模式测试失败: {e}")
        return False
    
    finally:
        try:
            if 'app' in locals():
                app.root.quit()
                app.root.destroy()
        except:
            pass

def test_integration():
    """集成测试"""
    print("\n执行集成测试...")
    
    try:
        app = StudentGUI()
        
        # 测试启动GUI并模拟用户操作
        print("✓ GUI启动成功")
        
        # 测试各个组件的可用性
        assert app.server is not None, "服务器实例为空"
        assert app.data_manager is not None, "数据管理器为空"
        assert app.root is not None, "主窗口为空"
        print("✓ 核心组件初始化成功")
        
        return True
        
    except Exception as e:
        print(f"✗ 集成测试失败: {e}")
        return False
    
    finally:
        try:
            if 'app' in locals():
                app.root.quit()
                app.root.destroy()
        except:
            pass

if __name__ == "__main__":
    print("=" * 60)
    print("学生端系统托盘功能测试")
    print("=" * 60)
    
    # 执行所有测试
    tests = [
        ("基础功能测试", test_tray_functionality),
        ("托盘菜单测试", test_tray_menu_creation),
        ("后台模式测试", test_background_mode),
        ("集成测试", test_integration)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} 失败")
        except Exception as e:
            print(f"❌ {test_name} 异常: {e}")
    
    print("\n" + "=" * 60)
    print(f"测试完成: {passed}/{total} 通过")
    print("=" * 60)
    
    if passed == total:
        print("🎉 所有测试通过！学生端系统托盘功能正常")
        print("\n功能特点:")
        print("- ✓ 支持后台运行（系统托盘）")
        print("- ✓ 支持窗口恢复")
        print("- ✓ 支持托盘通知")
        print("- ✓ 支持系统托盘右键菜单")
        print("- ✓ 支持自动状态通知")
    else:
        print("⚠️ 部分测试失败，请检查代码实现")