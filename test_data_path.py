"""
测试数据文件路径功能
验证数据目录创建和文件路径设置
"""

import os
from data_manager import DataManager

# 测试学生端数据文件路径
print("=== 测试学生端数据文件路径 ===")
try:
    # 创建学生端数据管理器实例
    student_data_manager = DataManager("student_data.json")
    print(f"数据目录路径: {student_data_manager.base_data_dir}")
    print(f"数据文件完整路径: {student_data_manager.data_file}")
    print(f"数据目录是否存在: {os.path.exists(student_data_manager.base_data_dir)}")
    print("测试成功: 数据管理器初始化完成")
except Exception as e:
    print(f"测试失败: {e}")

# 测试教师端数据文件路径
print("\n=== 测试教师端数据文件路径 ===")
try:
    # 创建教师端数据管理器实例
    teacher_data_manager = DataManager("teacher_data.json")
    print(f"数据目录路径: {teacher_data_manager.base_data_dir}")
    print(f"数据文件完整路径: {teacher_data_manager.data_file}")
    print(f"数据目录是否存在: {os.path.exists(teacher_data_manager.base_data_dir)}")
    print("测试成功: 数据管理器初始化完成")
except Exception as e:
    print(f"测试失败: {e}")

print("\n测试完成")