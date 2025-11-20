"""
局域网通信模块
负责学生端和老师端之间的数据交换
"""

import socket
import threading
import json
import time
from datetime import datetime

class NetworkCommunication:
    def __init__(self, host='0.0.0.0', port=8888):
        self.host = host
        self.port = port
        self.server_socket = None
        self.client_socket = None
        self.is_server_running = False
        self.message_handlers = {}
        
    def start_server(self):
        """启动服务器（老师端使用）"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.is_server_running = True
            
            print(f"服务器启动成功，监听端口: {self.port}")
            
            # 启动接受连接的线程
            accept_thread = threading.Thread(target=self._accept_connections)
            accept_thread.daemon = True
            accept_thread.start()
            
            return True
        except Exception as e:
            print(f"启动服务器失败: {e}")
            return False
    
    def _accept_connections(self):
        """接受客户端连接"""
        while self.is_server_running:
            try:
                client_socket, address = self.server_socket.accept()
                print(f"新连接来自: {address}")
                
                # 启动处理客户端消息的线程
                client_thread = threading.Thread(
                    target=self._handle_client, 
                    args=(client_socket,)
                )
                client_thread.daemon = True
                client_thread.start()
                
            except Exception as e:
                if self.is_server_running:
                    print(f"接受连接错误: {e}")
    
    def _handle_client(self, client_socket):
        """处理客户端消息"""
        try:
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break
                    
                message = data.decode('utf-8')
                self._process_message(message, client_socket)
                
        except Exception as e:
            print(f"处理客户端消息错误: {e}")
        finally:
            client_socket.close()
    
    def connect_to_server(self, server_ip):
        """连接到服务器（学生端使用）"""
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((server_ip, self.port))
            print(f"成功连接到服务器: {server_ip}:{self.port}")
            
            # 启动接收消息的线程
            receive_thread = threading.Thread(target=self._receive_messages)
            receive_thread.daemon = True
            receive_thread.start()
            
            return True
        except Exception as e:
            print(f"连接服务器失败: {e}")
            return False
    
    def _receive_messages(self):
        """接收消息（学生端使用）"""
        try:
            while True:
                data = self.client_socket.recv(1024)
                if not data:
                    break
                    
                message = data.decode('utf-8')
                self._process_message(message, self.client_socket)
                
        except Exception as e:
            print(f"接收消息错误: {e}")
    
    def _process_message(self, message, client_socket=None):
        """处理接收到的消息"""
        try:
            # 解析JSON消息
            data = json.loads(message)
            msg_type = data.get('type', 'unknown')
            
            # 调用对应的消息处理器
            if msg_type in self.message_handlers:
                self.message_handlers[msg_type](data, client_socket)
            
        except json.JSONDecodeError:
            print(f"消息格式错误: {message}")
        except Exception as e:
            print(f"处理消息错误: {e}")
    
    def send_message(self, message, target_socket=None):
        """发送消息"""
        try:
            message_data = json.dumps(message, ensure_ascii=False)
            
            if self.is_server_running:
                # 服务器端发送消息到特定客户端
                if target_socket:
                    target_socket.send(message_data.encode('utf-8'))
                else:
                    # 广播给所有连接的客户端
                    pass  # 需要维护客户端连接列表
                    
            else:
                # 客户端发送消息到服务器
                if self.client_socket:
                    self.client_socket.send(message_data.encode('utf-8'))
                    
            return True
        except Exception as e:
            print(f"发送消息失败: {e}")
            return False
    
    def register_handler(self, message_type, handler):
        """注册消息处理器"""
        self.message_handlers[message_type] = handler
    
    def stop_server(self):
        """停止服务器"""
        self.is_server_running = False
        if self.server_socket:
            self.server_socket.close()
        if self.client_socket:
            self.client_socket.close()
    
    def discover_server(self):
        """发现局域网内的服务器"""
        # 这里可以实现广播发现机制
        # 简化实现，假设服务器在固定IP
        return True

# 消息类型定义
class MessageTypes:
    HOMEWORK_REQUEST = "homework_request"     # 学生请求作业
    HOMEWORK_SEND = "homework_send"           # 老师发送作业
    MESSAGE_SEND = "message_send"             # 发送留言
    MESSAGE_RECEIVE = "message_receive"       # 接收留言
    CLASS_SELECTION = "class_selection"       # 班级选择
    SUBJECT_SELECTION = "subject_selection"   # 学科选择
    HEARTBEAT = "heartbeat"                   # 心跳包