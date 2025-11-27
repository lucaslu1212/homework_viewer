"""
测试数据目录创建修复功能
验证修复后的路径构建和目录创建逻辑
"""

import os
import sys
from data_manager import DataManager

print("=== 测试数据目录创建修复功能 ===")

# 测试基本的数据管理器初始化
try:
    # 创建数据管理器实例
    data_manager = DataManager("test_data.json")
    
    # 显示使用的数据目录
    print(f"使用的数据目录: {data_manager.base_data_dir}")
    print(f"完整数据文件路径: {data_manager.data_file}")
    
    # 检查目录是否存在
    dir_exists = os.path.exists(data_manager.base_data_dir)
    print(f"数据目录是否成功创建: {dir_exists}")
    
    # 如果目录存在，尝试写入一个测试文件
    if dir_exists:
        try:
            # 尝试保存一些测试数据
            test_data = {"test": "成功写入数据", "timestamp": "测试时间"}
            data_manager.data = test_data
            save_result = data_manager.save_data()
            print(f"测试数据保存结果: {'成功' if save_result else '失败'}")
            
            # 检查文件是否创建成功
            file_exists = os.path.exists(data_manager.data_file)
            print(f"测试数据文件是否创建: {file_exists}")
            
            if file_exists:
                # 尝试读取回数据验证
                new_manager = DataManager("test_data.json")
                print(f"读取的数据内容: {new_manager.data}")
        except Exception as write_error:
            print(f"写入测试数据时出错: {write_error}")
    else:
        print("警告: 数据目录创建失败，请检查权限设置")
        
    print("\n测试完成")
    
except Exception as e:
    print(f"测试过程中发生错误: {e}")
    import traceback
    traceback.print_exc()
