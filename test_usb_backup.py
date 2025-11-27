#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试U盘备份功能
用于验证DataManager中的U盘检测和备份功能是否正常工作
"""

import os
import json
import shutil
from data_manager import DataManager

def test_usb_detection():
    """测试U盘检测功能"""
    print("=" * 50)
    print("开始测试U盘检测功能...")
    
    # 初始化数据管理器
    data_manager = DataManager()
    
    # 测试U盘检测
    print("\n正在检测连接的U盘...")
    usb_drives = data_manager.get_usb_drives()
    
    if usb_drives:
        print(f"成功检测到 {len(usb_drives)} 个U盘:")
        for drive in usb_drives:
            print(f"  - {drive}")
            
            # 检查U盘的基本信息
            try:
                drive_info = os.listdir(drive)
                print(f"    文件列表（最多显示5个）: {drive_info[:5]}")
            except Exception as e:
                print(f"    无法访问U盘内容: {e}")
    else:
        print("未检测到U盘，这可能是因为:")
        print("  1. 没有U盘连接到电脑")
        print("  2. win32api模块未安装（请运行: pip install pywin32）")
        print("  3. 当前操作系统不是Windows")
        print("  4. 没有足够权限访问U盘")
    
    return usb_drives

def test_usb_backup():
    """测试U盘备份功能"""
    print("\n" + "=" * 50)
    print("开始测试U盘备份功能...")
    
    # 初始化数据管理器
    data_manager = DataManager()
    
    # 获取数据目录
    data_dir = data_manager.base_data_dir
    print(f"\n数据存储目录: {data_dir}")
    
    # 检查数据目录是否存在
    if os.path.exists(data_dir):
        print(f"数据目录 {data_dir} 存在")
        # 显示当前数据目录中的文件
        try:
            files = os.listdir(data_dir)
            print(f"数据目录中的文件（最多显示10个）: {files[:10]}")
        except Exception as e:
            print(f"无法访问数据目录内容: {e}")
    else:
        print(f"警告: 数据目录 {data_dir} 不存在")
    
    # 执行备份操作
    print("\n正在执行U盘备份操作...")
    result = data_manager.backup_from_usb()
    
    # 显示备份结果
    print(f"\n备份结果: {'成功' if result['success'] else '失败'}")
    print(f"消息: {result['message']}")
    print(f"检测到的U盘数量: {len(result['usb_drives'])}")
    print(f"成功备份的文件数量: {len(result['backed_up_files'])}")
    
    if result['backed_up_files']:
        print("\n备份文件详情:")
        for file_info in result['backed_up_files']:
            print(f"  - 文件: {file_info['file']}")
            print(f"    来源: {file_info['from']}")
            print(f"    目标: {file_info['to']}")
            print(f"    备份: {file_info['backup']}")
            
            # 验证备份是否成功
            if os.path.exists(file_info['to']):
                print(f"    ✓ 主文件备份成功")
            else:
                print(f"    ✗ 主文件备份失败")
            
            if os.path.exists(file_info['backup']):
                print(f"    ✓ 带时间戳的备份成功")
            else:
                print(f"    ✗ 带时间戳的备份失败")
    
    return result

def test_auto_check_backup():
    """测试自动检查和备份功能"""
    print("\n" + "=" * 50)
    print("开始测试自动检查和备份功能...")
    
    # 初始化数据管理器
    data_manager = DataManager()
    
    # 执行自动检查和备份
    result = data_manager.check_and_backup_usb()
    
    print(f"\n自动检查结果: {'成功' if result['success'] else '失败'}")
    print(f"消息: {result['message']}")
    
    return result

def simulate_usb_backup_test():
    """模拟U盘备份测试（用于在没有实际U盘的情况下测试）"""
    print("\n" + "=" * 50)
    print("模拟U盘备份测试（用于开发和测试）...")
    
    # 创建一个模拟的U盘目录
    mock_usb_dir = os.path.join(os.getcwd(), "mock_usb")
    os.makedirs(mock_usb_dir, exist_ok=True)
    
    # 创建测试数据文件
    test_files = ["demo_data.json", "student_data.json"]
    for file_name in test_files:
        test_file_path = os.path.join(mock_usb_dir, file_name)
        test_data = {
            "test": "这是模拟的测试数据",
            "file": file_name,
            "timestamp": "2024-01-01 12:00:00"
        }
        
        with open(test_file_path, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, ensure_ascii=False, indent=2)
        print(f"创建模拟测试文件: {test_file_path}")
    
    print(f"\n模拟U盘目录已创建: {mock_usb_dir}")
    print("提示: 要测试实际的备份功能，请将这些测试文件复制到真实的U盘中")

def main():
    """主测试函数"""
    print("U盘备份功能测试脚本")
    print("=" * 50)
    
    # 显示当前环境信息
    print(f"当前工作目录: {os.getcwd()}")
    print(f"Python版本: {os.sys.version}")
    
    # 测试U盘检测
    usb_drives = test_usb_detection()
    
    # 测试U盘备份
    backup_result = test_usb_backup()
    
    # 测试自动检查和备份
    auto_check_result = test_auto_check_backup()
    
    # 模拟测试（总是执行）
    simulate_usb_backup_test()
    
    print("\n" + "=" * 50)
    print("测试完成！")
    print("\n总结:")
    print(f"✓ 检测到的U盘数量: {len(usb_drives)}")
    print(f"✓ 成功备份的文件数量: {len(backup_result['backed_up_files'])}")
    print(f"✓ 模拟测试目录已创建: {os.path.join(os.getcwd(), 'mock_usb')}")
    
    if not usb_drives:
        print("\n注意: 未检测到U盘，某些功能测试可能不完整")
        print("建议:")
        print("1. 确保已连接U盘到电脑")
        print("2. 确保已安装pywin32模块: pip install pywin32")
        print("3. 尝试以管理员权限运行此脚本")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
    except Exception as e:
        print(f"\n\n测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n按Enter键退出...")
        input()
