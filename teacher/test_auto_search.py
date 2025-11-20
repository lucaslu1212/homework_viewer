#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试自动搜索功能的脚本
"""

import socket
import time

def get_local_ip():
    """获取本地IP地址"""
    try:
        # 连接到一个外部地址来获取本地IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "127.0.0.1"

def test_server_connection(ip, port, timeout=0.5):
    """测试服务器连接"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((ip, port))
        sock.close()
        return result == 0
    except:
        return False

def auto_search_servers():
    """自动搜索局域网内的学生服务器"""
    print("开始自动搜索学生服务器...")
    
    # 获取本地IP和网段
    local_ip = get_local_ip()
    print(f"本地IP地址: {local_ip}")
    
    if not local_ip:
        print("无法获取本地IP地址")
        return []
    
    network = '.'.join(local_ip.split('.')[:-1])
    print(f"扫描网段: {network}.x")
    
    found_servers = []
    
    # 只扫描前20个IP进行测试（避免耗时过长）
    for i in range(1, 21):
        ip = f"{network}.{i}"
        print(f"测试 {ip}:8888... ", end="")
        
        if test_server_connection(ip, 8888):
            found_servers.append(ip)
            print("✓ 找到服务器")
        else:
            print("✗ 无响应")
        
        # 稍微延时，避免网络负载过高
        time.sleep(0.1)
    
    if found_servers:
        print(f"\n总共找到 {len(found_servers)} 个学生服务器: {found_servers}")
    else:
        print("\n未找到任何学生服务器（这是正常的，如果学生端程序未运行）")
    
    return found_servers

if __name__ == "__main__":
    auto_search_servers()