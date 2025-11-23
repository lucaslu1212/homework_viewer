"""
新架构通信模块：学生端作为服务器，老师端作为客户端
负责学生服务器和老师客户端之间的数据交换
"""

import socket
import threading
import json
import time
from datetime import datetime
import uuid

class StudentServer:
    def __init__(self, host='0.0.0.0', port=8888):
        self.host = host
        self.port = port
        self.server_socket = None
        self.is_running = False
        self.connected_teachers = {}  # {teacher_id: socket}
        self.message_handlers = {}
        self.teacher_listeners = {}   # 监听器函数列表
        
    def start_server(self):
        """启动学生服务器"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.is_running = True
            
            print(f"学生服务器启动成功，监听端口: {self.port}")
            
            # 启动接受连接的线程
            accept_thread = threading.Thread(target=self._accept_connections)
            accept_thread.daemon = True
            accept_thread.start()
            
            return True
        except Exception as e:
            print(f"启动学生服务器失败: {e}")
            return False
    
    def _accept_connections(self):
        """接受老师客户端连接"""
        while self.is_running:
            try:
                client_socket, address = self.server_socket.accept()
                print(f"老师连接来自: {address}")
                
                # 启动处理老师消息的线程
                teacher_thread = threading.Thread(
                    target=self._handle_teacher, 
                    args=(client_socket,)
                )
                teacher_thread.daemon = True
                teacher_thread.start()
                
            except Exception as e:
                if self.is_running:
                    print(f"接受老师连接错误: {e}")
    
    def _handle_teacher(self, client_socket):
        """处理老师客户端消息"""
        teacher_id = None
        try:
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break
                    
                message = data.decode('utf-8')
                data_json = json.loads(message)
                
                # 处理连接建立消息
                if data_json.get('type') == 'teacher_connect':
                    teacher_id = data_json.get('teacher_id', str(uuid.uuid4()))
                    self.connected_teachers[teacher_id] = client_socket
                    print(f"老师 {data_json.get('teacher_name', 'Unknown')} 已连接 (ID: {teacher_id})")
                    
                    # 通知监听器
                    for listener in self.teacher_listeners.values():
                        listener('teacher_connected', {'teacher_id': teacher_id, 'teacher_data': data_json})
                    continue
                
                # 处理其他消息
                self._process_message(data_json, client_socket, teacher_id)
                
        except Exception as e:
            print(f"处理老师消息错误: {e}")
        finally:
            if teacher_id:
                print(f"老师 {teacher_id} 已断开连接")
                self.connected_teachers.pop(teacher_id, None)
                
                # 通知监听器
                for listener in self.teacher_listeners.values():
                    listener('teacher_disconnected', {'teacher_id': teacher_id})
                    
            client_socket.close()
    
    def _process_message(self, message, client_socket, teacher_id):
        """处理接收到的消息"""
        try:
            msg_type = message.get('type', 'unknown')
            
            # 调用对应的消息处理器
            if msg_type in self.message_handlers:
                self.message_handlers[msg_type](message, client_socket, teacher_id)
            
        except Exception as e:
            print(f"处理消息错误: {e}")
    
    def send_to_teacher(self, teacher_id, message):
        """发送消息给特定老师"""
        try:
            if teacher_id in self.connected_teachers:
                socket = self.connected_teachers[teacher_id]
                message_data = json.dumps(message, ensure_ascii=False)
                socket.send(message_data.encode('utf-8'))
                return True
            else:
                print(f"老师 {teacher_id} 不在线")
                return False
        except Exception as e:
            print(f"发送消息给老师失败: {e}")
            return False
    
    def broadcast_to_teachers(self, message):
        """广播消息给所有老师"""
        message_data = json.dumps(message, ensure_ascii=False)
        success_count = 0
        
        for teacher_id, socket in list(self.connected_teachers.items()):
            try:
                socket.send(message_data.encode('utf-8'))
                success_count += 1
            except Exception as e:
                print(f"发送消息给老师 {teacher_id} 失败: {e}")
                # 移除断开的连接
                self.connected_teachers.pop(teacher_id, None)
        
        return success_count
    
    def register_handler(self, message_type, handler):
        """注册消息处理器"""
        self.message_handlers[message_type] = handler
    
    def add_listener(self, event_type, listener):
        """添加事件监听器"""
        if event_type not in self.teacher_listeners:
            self.teacher_listeners[event_type] = []
        self.teacher_listeners[event_type].append(listener)
    
    def get_connected_teachers(self):
        """获取已连接的老师列表"""
        return list(self.connected_teachers.keys())
    
    def stop_server(self):
        """停止服务器"""
        self.is_running = False
        if self.server_socket:
            self.server_socket.close()
        
        # 关闭所有老师连接
        for socket in self.connected_teachers.values():
            try:
                socket.close()
            except:
                pass
        self.connected_teachers.clear()


class TeacherClient:
    def __init__(self):
        self.client_socket = None
        self.is_connected = False
        self.message_handlers = {}
        self.server_info = None
        
    def connect_to_student_server(self, server_ip, port=8888, teacher_id=None, teacher_name=""):
        """连接到学生服务器"""
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((server_ip, port))
            self.is_connected = True
            
            print(f"成功连接到学生服务器: {server_ip}:{port}")
            
            # 发送连接建立消息
            connect_message = {
                'type': 'teacher_connect',
                'teacher_id': teacher_id or str(uuid.uuid4()),
                'teacher_name': teacher_name,
                'timestamp': datetime.now().isoformat()
            }
            
            self._send_message(connect_message)
            
            # 启动接收消息的线程
            receive_thread = threading.Thread(target=self._receive_messages)
            receive_thread.daemon = True
            receive_thread.start()
            
            return True
        except Exception as e:
            print(f"连接学生服务器失败: {e}")
            return False
    
    def _receive_messages(self):
        """接收消息"""
        try:
            while self.is_connected:
                data = self.client_socket.recv(1024)
                if not data:
                    break
                    
                message = data.decode('utf-8')
                data_json = json.loads(message)
                self._process_message(data_json)
                
        except Exception as e:
            print(f"接收消息错误: {e}")
        finally:
            self.is_connected = False
    
    def _process_message(self, message):
        """处理接收到的消息"""
        try:
            msg_type = message.get('type', 'unknown')
            
            # 调用对应的消息处理器
            if msg_type in self.message_handlers:
                self.message_handlers[msg_type](message)
            
        except Exception as e:
            print(f"处理消息错误: {e}")
    
    def _send_message(self, message):
        """发送消息"""
        try:
            if self.is_connected and self.client_socket:
                message_data = json.dumps(message, ensure_ascii=False)
                self.client_socket.send(message_data.encode('utf-8'))
                return True
            else:
                print("未连接到服务器")
                return False
        except Exception as e:
            print(f"发送消息失败: {e}")
            return False
    
    def register_handler(self, message_type, handler):
        """注册消息处理器"""
        self.message_handlers[message_type] = handler
    
    def disconnect(self):
        """断开连接"""
        self.is_connected = False
        if self.client_socket:
            try:
                self.client_socket.close()
            except:
                pass


# 新消息类型定义
class MessageTypes:
    # 连接相关
    TEACHER_CONNECT = "teacher_connect"       # 老师连接
    TEACHER_DISCONNECT = "teacher_disconnect" # 老师断开
    
    # 作业相关 - 标准的作业流程
    HOMEWORK_REQUEST = "homework_request"     # 老师请求学生作业
    HOMEWORK_RESPONSE = "homework_response"   # 学生回应作业（发送作业内容）
    HOMEWORK_SUBMIT = "homework_submit"       # 学生提交作业
    
    # 留言相关
    MESSAGE_SEND = "message_send"             # 发送留言
    MESSAGE_RESPONSE = "message_response"     # 留言回应
    
    # 状态相关
    CLASS_SELECTION = "class_selection"       # 老师选择班级
    SUBJECT_SELECTION = "subject_selection"   # 老师选择学科
    TEACHER_STATUS = "teacher_status"         # 老师状态更新
    
    # 班级相关
    CLASS_LIST_REQUEST = "class_list_request" # 请求班级列表
    CLASS_LIST_RESPONSE = "class_list_response" # 班级列表响应
    
    # 系统相关
    HEARTBEAT = "heartbeat"                   # 心跳包
    SYSTEM_INFO = "system_info"               # 系统信息

# 消息数据结构定义
class MessageStructure:
    """统一的消息数据结构定义"""
    
    @staticmethod
    def teacher_connect(teacher_id, teacher_name):
        """老师连接消息"""
        return {
            'type': MessageTypes.TEACHER_CONNECT,
            'teacher_id': teacher_id,
            'teacher_name': teacher_name,
            'timestamp': datetime.now().isoformat()
        }
    
    @staticmethod
    def homework_request(class_name, subject, message=""):
        """老师请求作业消息"""
        return {
            'type': MessageTypes.HOMEWORK_REQUEST,
            'class': class_name,
            'subject': subject,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
    
    @staticmethod
    def homework_response(homework_data):
        """学生回应作业消息"""
        return {
            'type': MessageTypes.HOMEWORK_RESPONSE,
            'homework': homework_data,
            'timestamp': datetime.now().isoformat()
        }
    
    @staticmethod
    def message_send(content, sender_name, class_name=""):
        """发送留言消息"""
        return {
            'type': MessageTypes.MESSAGE_SEND,
            'content': content,
            'sender_name': sender_name,
            'class': class_name,
            'timestamp': datetime.now().isoformat()
        }
    
    @staticmethod
    def message_response(content, sender_name, class_name=""):
        """留言回应消息"""
        return {
            'type': MessageTypes.MESSAGE_RESPONSE,
            'content': content,
            'sender_name': sender_name,
            'class': class_name,
            'timestamp': datetime.now().isoformat()
        }
    
    @staticmethod
    def class_list_request():
        """班级列表请求消息"""
        return {
            'type': MessageTypes.CLASS_LIST_REQUEST,
            'timestamp': datetime.now().isoformat()
        }
    
    @staticmethod
    def class_list_response(classes):
        """班级列表响应消息"""
        return {
            'type': MessageTypes.CLASS_LIST_RESPONSE,
            'classes': classes,
            'timestamp': datetime.now().isoformat()
        }