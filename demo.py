#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
作业查看器系统演示脚本
展示系统的基本功能和使用方法
"""

from communication import NetworkCommunication, MessageTypes
from data_manager import DataManager
import json
import time

def demo_data_manager():
    """演示数据管理功能"""
    print("=" * 50)
    print("数据管理器功能演示")
    print("=" * 50)
    
    # 创建数据管理器
    dm = DataManager("demo_data.json")
    
    # 添加一些示例作业
    print("1. 添加示例作业...")
    homework1 = dm.add_homework("数学", "完成课后习题1-10题", "高一(1)班", "张老师")
    homework2 = dm.add_homework("语文", "背诵《静夜思》并默写", "高一(1)班", "李老师")
    homework3 = dm.add_homework("英语", "Write an essay about your hometown", "高二(1)班", "王老师")
    
    print(f"添加作业1: {homework1['subject']} - {homework1['content']}")
    print(f"添加作业2: {homework2['subject']} - {homework2['content']}")
    print(f"添加作业3: {homework3['subject']} - {homework3['content']}")
    
    # 添加示例留言
    print("\n2. 添加示例留言...")
    message1 = dm.add_message("老师，这道数学题我不会做", "小明", "高一(1)班")
    message2 = dm.add_message("英语作业已经完成", "小红", "高一(1)班")
    
    print(f"添加留言1: {message1['content']}")
    print(f"添加留言2: {message2['content']}")
    
    # 查询作业
    print("\n3. 查询作业...")
    all_homeworks = dm.get_homeworks()
    print(f"总作业数: {len(all_homeworks)}")
    
    math_homeworks = dm.get_homeworks(subject="数学")
    print(f"数学作业数: {len(math_homeworks)}")
    
    class1_homeworks = dm.get_homeworks(class_name="高一(1)班")
    print(f"高一(1)班作业数: {len(class1_homeworks)}")
    
    # 查询留言
    print("\n4. 查询留言...")
    all_messages = dm.get_messages()
    print(f"总留言数: {len(all_messages)}")
    
    # 显示统计信息
    print("\n5. 统计信息...")
    stats = dm.get_statistics()
    print(f"总作业数: {stats['homework_count']}")
    print(f"总留言数: {stats['message_count']}")
    print(f"班级数: {stats['class_count']}")
    print("学科分布:")
    for subject, count in stats['subject_stats'].items():
        if count > 0:
            print(f"  {subject}: {count}个作业")
    
    return dm

def demo_communication():
    """演示网络通信功能"""
    print("\n" + "=" * 50)
    print("网络通信功能演示")
    print("=" * 50)
    
    # 创建通信管理器
    comm = NetworkCommunication()
    
    # 演示消息格式
    print("1. 消息格式演示...")
    
    # 作业发送消息
    homework_message = {
        "type": MessageTypes.HOMEWORK_SEND,
        "homework": {
            "id": 1,
            "subject": "数学",
            "content": "完成课后习题1-10题",
            "class": "高一(1)班",
            "teacher": "张老师",
            "timestamp": "2024-11-18 10:30:00"
        }
    }
    print(f"作业发送消息: {json.dumps(homework_message, ensure_ascii=False)}")
    
    # 留言消息
    message_send = {
        "type": MessageTypes.MESSAGE_SEND,
        "content": "老师，这道题我不会做",
        "student": "小明",
        "class": "高一(1)班"
    }
    print(f"留言发送消息: {json.dumps(message_send, ensure_ascii=False)}")
    
    # 班级选择消息
    class_selection = {
        "type": MessageTypes.CLASS_SELECTION,
        "class": "高一(1)班",
        "student": "小明"
    }
    print(f"班级选择消息: {json.dumps(class_selection, ensure_ascii=False)}")
    
    # 作业请求消息
    homework_request = {
        "type": MessageTypes.HOMEWORK_REQUEST,
        "class": "高一(1)班",
        "subject": "数学"
    }
    print(f"作业请求消息: {json.dumps(homework_request, ensure_ascii=False)}")
    
    return comm

def demo_system_workflow():
    """演示系统工作流程"""
    print("\n" + "=" * 50)
    print("系统工作流程演示")
    print("=" * 50)
    
    print("老师端操作流程:")
    print("1. 启动服务器，设置端口8888")
    print("2. 选择学科：数学")
    print("3. 选择班级：高一(1)班")
    print("4. 输入作业内容：完成课后习题1-10题")
    print("5. 点击发送作业")
    print("6. 系统将作业保存到数据库")
    print("7. 系统将作业推送给所有连接的学生")
    
    print("\n学生端操作流程:")
    print("1. 输入服务器IP（老师端IP地址）")
    print("2. 输入学生姓名：小明")
    print("3. 点击连接服务器")
    print("4. 选择班级：高一(1)班")
    print("5. 系统自动请求作业列表")
    print("6. 查看接收到的作业")
    print("7. 在留言板发送问题或反馈")
    
    print("\n网络通信流程:")
    print("1. 学生端 -> 服务器: 发送连接请求")
    print("2. 学生端 -> 服务器: 发送班级选择")
    print("3. 学生端 -> 服务器: 发送作业请求")
    print("4. 服务器 -> 学生端: 发送作业列表")
    print("5. 老师端 -> 服务器: 发送新作业")
    print("6. 服务器 -> 学生端: 推送新作业")
    print("7. 学生端 -> 服务器: 发送留言")
    print("8. 服务器 -> 老师端: 转发留言")

def show_network_tips():
    """显示网络使用技巧"""
    print("\n" + "=" * 50)
    print("网络使用技巧")
    print("=" * 50)
    
    print("局域网配置:")
    print("1. 确保老师端和学生端在同一网段")
    print("2. 老师端IP: 使用ipconfig查看 (Windows)")
    print("3. 学生端连接IP: 填入老师端IP地址")
    print("4. 端口: 默认8888，可在老师端修改")
    
    print("\n防火墙设置:")
    print("1. Windows防火墙需要允许Python程序")
    print("2. 允许端口8888的入站连接")
    print("3. 如果仍无法连接，临时关闭防火墙测试")
    
    print("\n故障排除:")
    print("1. 连接失败: 检查IP地址和端口")
    print("2. 作业不显示: 检查班级选择是否匹配")
    print("3. 留言发送失败: 检查连接状态")
    print("4. 程序无响应: 检查网络连接")

def main():
    """主演示函数"""
    print("作业查看器系统功能演示")
    print("基于Python的局域网师生作业管理系统")
    print()
    
    try:
        # 演示数据管理器
        demo_data_manager()
        
        # 演示通信管理器
        demo_communication()
        
        # 演示系统工作流程
        demo_system_workflow()
        
        # 显示网络使用技巧
        show_network_tips()
        
        print("\n" + "=" * 50)
        print("演示完成！")
        print("=" * 50)
        print("使用说明:")
        print("1. 运行 python launcher.py 启动系统")
        print("2. 先启动老师端，再启动学生端")
        print("3. 按照界面提示操作即可")
        print("4. 详细说明请查看 README.md")
        
    except Exception as e:
        print(f"演示过程中出现错误: {e}")

if __name__ == "__main__":
    main()