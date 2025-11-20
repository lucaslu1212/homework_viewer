#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试教师端GUI功能
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# 测试导入
try:
    from teacher_gui import TeacherGUI
    from communication import MessageTypes
    print("✓ 导入成功")
except Exception as e:
    print(f"✗ 导入失败: {e}")
    sys.exit(1)

# 测试教师端初始化（不显示窗口）
import tkinter as tk
from tkinter import ttk

def test_teacher_gui():
    """测试教师端GUI功能"""
    print("\n测试教师端GUI初始化...")
    
    try:
        # 创建根窗口但不显示
        root = tk.Tk()
        root.withdraw()  # 隐藏窗口
        
        # 初始化TeacherGUI（会创建子窗口）
        teacher_gui = TeacherGUI()
        
        # 检查班级设置
        classes = teacher_gui.class_combo['values']
        print(f"✓ 班级设置: {list(classes)}")
        
        # 检查自动搜索选项
        auto_search = teacher_gui.auto_search.get()
        print(f"✓ 自动搜索选项: {'启用' if auto_search else '禁用'}")
        
        # 检查教师端变量
        print(f"✓ 教师姓名默认值: {teacher_gui.teacher_name.get()}")
        print(f"✓ 服务器IP默认值: {teacher_gui.server_ip.get()}")
        
        # 关闭窗口
        root.destroy()
        
        print("\n✓ 教师端GUI测试完成，所有功能正常！")
        
        # 验证班级设置是否符合要求（1-8班）
        expected_classes = ["1班", "2班", "3班", "4班", "5班", "6班", "7班", "8班"]
        if list(classes) == expected_classes:
            print("✓ 班级设置完全符合要求（1-8班）")
            return True
        else:
            print(f"✗ 班级设置不符合要求，期望: {expected_classes}, 实际: {list(classes)}")
            return False
            
    except Exception as e:
        print(f"✗ 教师端GUI测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_teacher_gui()
    if success:
        print("\n🎉 所有测试通过！教师端功能正常")
    else:
        print("\n❌ 测试失败")
        sys.exit(1)