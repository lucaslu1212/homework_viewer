"""
老师端主程序
提供学科选择、作业发送功能
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import json
import socket

# 使用新架构的通信模块
# from communication import StudentServer, TeacherClient
# 消息类型常量
class MessageTypes:
    HOMEWORK_REQUEST = "homework_request"
    HOMEWORK_RESPONSE = "homework_response"
    HOMEWORK_SEND = "homework_send"
    MESSAGE_SEND = "message_send"
    MESSAGE_RESPONSE = "message_response"
    MESSAGE_RECEIVE = "message_receive"
    CLASS_SELECTION = "class_selection"

try:
    from data_manager import DataManager
except ModuleNotFoundError:
    # 最小桩实现，避免程序无法启动
    class DataManager:
        def __init__(self, filename): pass
        def add_class(self, class_name): pass
        def get_classes(self): return ["高一(1)班", "高一(2)班", "高一(3)班"]
        def get_subjects(self): return ["语文", "数学", "英语"]
        def add_homework(self, **kw): return {"id": 1, **kw}
        def get_homeworks(self, class_name=None, subject=None): return []
        def delete_homework(self, hid): pass
        def clear_all_data(self): pass
        def get_statistics(self): return {"total_homeworks": 0, "message_count": 0, "class_count": 0, "subject_stats": {}}

try:
    from communication import TeacherClient
except ModuleNotFoundError:
    # 最小桩实现，避免程序无法启动
    class TeacherClient:
        def __init__(self): pass
        def connect_to_student_server(self, ip, port=8888, teacher_id=None, teacher_name=""): return False
        def disconnect(self): pass
        def register_handler(self, msg_type, handler): pass
        def _send_message(self, msg): pass
        def is_connected(self): return False

class TeacherGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("作业查看器 - 老师端")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # 初始化组件
        self.comm = TeacherClient()
        self.data_manager = DataManager("teacher_data.json")
        
        # 初始化变量
        self.selected_subject = tk.StringVar()
        self.selected_class = tk.StringVar()
        self.teacher_name = tk.StringVar(value="老师")
        self.homework_content = tk.StringVar()
        self.server_ip = tk.StringVar(value="127.0.0.1")
        self.auto_search = tk.BooleanVar(value=True)  # 添加自动搜索选项
        
        # 客户端状态
        self.is_connected = False
        
        # 服务器状态（保留但不再使用）
        self.is_server_running = False
        
        # 设置界面
        self.setup_ui()
        
        # 注册消息处理器
        self.setup_message_handlers()
        
        # 绑定关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_ui(self):
        """设置用户界面"""
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # 客户端连接框架
        connection_frame = ttk.LabelFrame(main_frame, text="服务器连接", padding="10")
        connection_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        connection_frame.columnconfigure(1, weight=1)
        
        ttk.Label(connection_frame, text="老师姓名:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        ttk.Entry(connection_frame, textvariable=self.teacher_name, width=15).grid(row=0, column=1, sticky=tk.W, padx=(0, 20))
        
        # 自动搜索选项
        self.auto_search_check = ttk.Checkbutton(connection_frame, text="自动搜索学生服务器", variable=self.auto_search)
        self.auto_search_check.grid(row=0, column=2, sticky=tk.W, padx=(0, 20))
        
        ttk.Label(connection_frame, text="服务器IP:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5))
        self.server_ip_entry = ttk.Entry(connection_frame, textvariable=self.server_ip, width=15)
        self.server_ip_entry.grid(row=1, column=1, sticky=tk.W, padx=(0, 20))
        
        ttk.Label(connection_frame, text="端口:").grid(row=1, column=2, sticky=tk.W, padx=(0, 5))
        self.port_entry = ttk.Entry(connection_frame, width=10)
        self.port_entry.insert(0, "8888")
        self.port_entry.grid(row=1, column=3, sticky=tk.W, padx=(0, 20))
        
        self.connect_btn = ttk.Button(connection_frame, text="连接服务器", command=self.connect_to_server)
        self.connect_btn.grid(row=1, column=4, padx=(0, 10))
        
        self.disconnect_btn = ttk.Button(connection_frame, text="断开连接", command=self.disconnect_from_server, state="disabled")
        self.disconnect_btn.grid(row=1, column=5, padx=(0, 10))
        
        self.status_label = ttk.Label(connection_frame, text="未连接服务器", foreground="red")
        self.status_label.grid(row=1, column=6, padx=(10, 0))
        
        # 作业发送框架
        homework_frame = ttk.LabelFrame(main_frame, text="发送作业", padding="10")
        homework_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        homework_frame.columnconfigure(1, weight=1)
        
        ttk.Label(homework_frame, text="学科:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.subject_combo = ttk.Combobox(homework_frame, textvariable=self.selected_subject, width=15)
        self.subject_combo.grid(row=0, column=1, sticky=tk.W, padx=(0, 20))
        
        ttk.Label(homework_frame, text="班级:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.class_combo = ttk.Combobox(homework_frame, textvariable=self.selected_class, width=15)
        self.class_combo.grid(row=0, column=3, sticky=tk.W, padx=(0, 20))
        
        ttk.Button(homework_frame, text="发送作业", command=self.send_homework).grid(row=0, column=4, padx=(10, 0))
        
        # 作业内容输入框架
        content_frame = ttk.Frame(homework_frame)
        content_frame.grid(row=1, column=0, columnspan=5, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        content_frame.columnconfigure(0, weight=1)
        content_frame.rowconfigure(0, weight=1)
        
        self.homework_text = scrolledtext.ScrolledText(content_frame, height=5, wrap=tk.WORD)
        self.homework_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 作业管理框架
        management_frame = ttk.LabelFrame(main_frame, text="作业管理", padding="10")
        management_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        management_frame.columnconfigure(0, weight=1)
        management_frame.rowconfigure(1, weight=1)
        
        # 管理按钮框架
        buttons_frame = ttk.Frame(management_frame)
        buttons_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(buttons_frame, text="查看所有作业", command=self.view_all_homeworks).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(buttons_frame, text="删除选中作业", command=self.delete_homework).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(buttons_frame, text="清空所有数据", command=self.clear_data).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(buttons_frame, text="关于", command=self.show_about).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(buttons_frame, text="刷新", command=self.refresh_data).pack(side=tk.LEFT, padx=(10, 0))
        
        # 全屏模式按钮框架
        fullscreen_frame = ttk.Frame(management_frame)
        fullscreen_frame.grid(row=0, column=1, sticky=(tk.E), padx=(10, 0))
        
        self.fullscreen_var = tk.BooleanVar()
        self.fullscreen_var.trace('w', self.on_fullscreen_toggle)
        ttk.Checkbutton(fullscreen_frame, text="全屏模式", variable=self.fullscreen_var).pack(side=tk.RIGHT)
        
        # 全屏模式下的临时框架
        self.fullscreen_window = None
        self.original_parent = None
        
        # 作业列表框架
        list_frame = ttk.Frame(management_frame)
        list_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # 创建作业树形控件
        columns = ("ID", "学科", "内容", "班级", "老师", "时间", "状态")
        self.homework_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=8)
        
        # 设置列标题和宽度
        column_widths = {"ID": 50, "学科": 80, "内容": 300, "班级": 100, "老师": 80, "时间": 150, "状态": 80}
        for col in columns:
            self.homework_tree.heading(col, text=col)
            self.homework_tree.column(col, width=column_widths.get(col, 100))
        
        # 添加滚动条
        list_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.homework_tree.yview)
        self.homework_tree.configure(yscrollcommand=list_scrollbar.set)
        
        self.homework_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        list_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 统计信息框架
        stats_frame = ttk.LabelFrame(main_frame, text="统计信息", padding="10")
        stats_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.stats_label = ttk.Label(stats_frame, text="统计数据加载中...")
        self.stats_label.grid(row=0, column=0, sticky=tk.W)
        
        # 配置主框架行权重
        main_frame.rowconfigure(2, weight=2)
        
        # 初始化数据
        self.init_data()
    
    def init_data(self):
        """初始化数据"""
        # 加载学科列表
        subjects = self.data_manager.get_subjects()
        self.subject_combo['values'] = subjects
        
        # 先清空班级列表，等待从学生端获取
        self.class_combo['values'] = []
        self.class_combo.set("")
        
        # 设置默认学科
        if subjects:
            self.subject_combo.set(subjects[0])
        
        # 加载作业列表
        self.load_homework_list()
        self.update_statistics()
    
    def setup_message_handlers(self):
        """设置消息处理器"""
        def handle_homework_response(data):
            """处理学生回应作业"""
            print("收到学生作业回应")
            homework_data = data.get('homework', {})
            
            if 'student_class' in homework_data:
                # 新的统一格式
                student_class = homework_data.get('student_class', '')
                student_name = homework_data.get('student_name', '')
                homeworks = homework_data.get('homeworks', [])
                teacher_message = homework_data.get('teacher_message', '')
                
                print(f"学生 {student_name} ({student_class}) 回应了 {len(homeworks)} 份作业")
                
                # 在老师端显示收到的作业
                for homework in homeworks:
                    self.root.after(0, self.display_received_homework, {
                        'student': student_name,
                        'class': student_class,
                        'subject': homework.get('subject', ''),
                        'content': homework.get('content', ''),
                        'teacher': homework.get('teacher', ''),
                        'timestamp': homework.get('timestamp', ''),
                        'status': homework.get('status', '已完成')
                    })
            else:
                # 旧格式兼容
                student = homework_data.get('student', 'Unknown')
                class_name = homework_data.get('class', '')
                subject = homework_data.get('subject', '')
                content = homework_data.get('content', '')
                teacher = homework_data.get('teacher', '')
                
                self.root.after(0, self.display_received_homework, {
                    'student': student,
                    'class': class_name,
                    'subject': subject,
                    'content': content,
                    'teacher': teacher,
                    'timestamp': '刚刚',
                    'status': '已完成'
                })
        
        def handle_message_response(data):
            """处理留言回应"""
            print("收到留言回应")
            content = data.get('content', '')
            sender_name = data.get('sender_name', 'Unknown')
            class_name = data.get('class', '')
            
            print(f"收到留言：{sender_name} ({class_name}) - {content}")
            
            # 在老师端显示留言
            self.root.after(0, self.display_received_message, {
                'content': content,
                'sender': sender_name,
                'class': class_name,
                'timestamp': '刚刚'
            })
        
        def handle_class_list_response(data):
            """处理班级列表响应"""
            try:
                classes = data.get('classes', [])
                if classes:
                    print(f"收到班级列表: {classes}")
                    # 更新班级下拉框
                    self.class_combo['values'] = classes
                    # 设置默认选中第一个班级
                    self.class_combo.set(classes[0])
                    # 加载作业列表
                    self.load_homework_list()
            except Exception as e:
                print(f"处理班级列表响应失败: {e}")
        
        # 注册处理器
        self.comm.register_handler(MessageTypes.HOMEWORK_RESPONSE, handle_homework_response)
        self.comm.register_handler(MessageTypes.MESSAGE_RESPONSE, handle_message_response)
        self.comm.register_handler(MessageTypes.CLASS_LIST_RESPONSE, handle_class_list_response)
    
    def connect_to_server(self):
        """连接到学生服务器"""
        teacher_name = self.teacher_name.get().strip()
        if not teacher_name:
            messagebox.showerror("错误", "请输入老师姓名")
            return
        
        # 如果启用了自动搜索
        if self.auto_search.get():
            self.auto_search_servers()
        else:
            # 手动连接
            self.manual_connect()
    
    def auto_search_servers(self):
        """自动搜索局域网内的学生服务器"""
        def search_thread():
            print("开始自动搜索学生服务器...")
            
            # 获取本地IP和网段
            local_ip = self.get_local_ip()
            if not local_ip:
                self.root.after(0, lambda: messagebox.showerror("错误", "无法获取本地IP地址"))
                return
            
            network = '.'.join(local_ip.split('.')[:-1])
            found_servers = []
            
            # 扫描网段内的所有IP
            for i in range(1, 255):
                ip = f"{network}.{i}"
                if self.test_server_connection(ip, 8888):
                    found_servers.append(ip)
            
            if found_servers:
                print(f"找到 {len(found_servers)} 个学生服务器: {found_servers}")
                self.root.after(0, self.show_server_selection, found_servers)
            else:
                print("未找到任何学生服务器")
                self.root.after(0, lambda: messagebox.showwarning("提示", "未找到任何学生服务器，请确认学生端程序已启动并连接在同一网络中"))
    
    def get_local_ip(self):
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
    
    def test_server_connection(self, ip, port, timeout=1):
        """测试服务器连接"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((ip, port))
            sock.close()
            return result == 0
        except:
            return False
    
    def show_server_selection(self, server_list):
        """显示服务器选择对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("选择学生服务器")
        dialog.geometry("400x300")
        dialog.resizable(False, False)
        
        # 居中显示
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 计算居中位置
        dialog.geometry("+%d+%d" % (
            self.root.winfo_rootx() + 50,
            self.root.winfo_rooty() + 50
        ))
        
        # 服务器列表框架
        list_frame = ttk.Frame(dialog, padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(list_frame, text="请选择要连接的学生服务器：", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 10))
        
        # 创建列表框
        listbox_frame = ttk.Frame(list_frame)
        listbox_frame.pack(fill=tk.BOTH, expand=True)
        
        server_listbox = tk.Listbox(listbox_frame, height=8)
        scrollbar = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=server_listbox.yview)
        server_listbox.configure(yscrollcommand=scrollbar.set)
        
        server_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 添加服务器到列表
        for server_ip in server_list:
            server_listbox.insert(tk.END, server_ip)
        
        # 按钮框架
        button_frame = ttk.Frame(list_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        selected_ip = None
        
        def on_connect():
            nonlocal selected_ip
            selection = server_listbox.curselection()
            if not selection:
                messagebox.showwarning("提示", "请先选择一个服务器")
                return
            
            selected_ip = server_listbox.get(selection[0])
            dialog.destroy()
            self.manual_connect(selected_ip)
        
        def on_cancel():
            dialog.destroy()
        
        ttk.Button(button_frame, text="连接", command=on_connect).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="取消", command=on_cancel).pack(side=tk.RIGHT)
        
        # 设置默认选择第一个
        if server_list:
            server_listbox.selection_set(0)
        
        # 等待对话框关闭
        dialog.wait_window()
    
    def manual_connect(self, server_ip=None):
        """手动连接服务器"""
        if server_ip is None:
            server_ip = self.server_ip.get().strip()
            if not server_ip:
                messagebox.showerror("错误", "请输入服务器IP")
                return
        
        teacher_name = self.teacher_name.get().strip()
        port_text = self.port_entry.get().strip()
        
        if not port_text.isdigit():
            messagebox.showerror("错误", "端口号必须是数字")
            return
        
        port = int(port_text)
        if port < 1024 or port > 65535:
            messagebox.showerror("错误", "端口号必须在1024-65535范围内")
            return
        
        def connect_thread():
            if self.comm.connect_to_student_server(
                server_ip=server_ip, 
                port=port, 
                teacher_name=teacher_name
            ):
                self.is_connected = True
                self.root.after(0, self.on_connect_success)
            else:
                self.root.after(0, self.on_connect_failed)
        
        # 在新线程中连接服务器
        threading.Thread(target=connect_thread, daemon=True).start()
    
    def on_connect_success(self):
        """连接成功回调"""
        self.status_label.config(text="已连接服务器", foreground="green")
        self.connect_btn.config(state="disabled")
        self.disconnect_btn.config(state="normal")
        
        # 请求班级列表
        self.request_class_list()
        
        messagebox.showinfo("成功", "连接服务器成功！")
    
    def on_connect_failed(self):
        """连接失败回调"""
        self.status_label.config(text="连接失败", foreground="red")
        messagebox.showerror("错误", "连接服务器失败，请检查IP和端口是否正确")
    
    def disconnect_from_server(self):
        """断开与服务器的连接"""
        self.comm.disconnect()
        self.is_connected = False
        
        self.status_label.config(text="未连接服务器", foreground="red")
        self.connect_btn.config(state="normal")
        self.disconnect_btn.config(state="disabled")
        
        messagebox.showinfo("提示", "已断开与服务器的连接")
    
    def send_homework(self):
        """发送作业"""
        if not self.is_connected:
            messagebox.showerror("错误", "请先连接到服务器")
            return
        
        subject = self.selected_subject.get()
        class_name = self.selected_class.get()
        content = self.homework_text.get(1.0, tk.END).strip()
        
        if not subject:
            messagebox.showerror("错误", "请选择学科")
            return
        
        if not class_name:
            messagebox.showerror("错误", "请选择班级")
            return
        
        if not content:
            messagebox.showerror("错误", "请输入作业内容")
            return
        
        # 添加作业到数据管理器
        homework = self.data_manager.add_homework(
            subject=subject,
            content=content,
            class_name=class_name,
            teacher_name=self.teacher_name.get().strip()
        )
        
        # 使用标准化消息格式发送给服务器（学生端）
        if self.is_connected:
            try:
                # 尝试导入MessageStructure
                from communication import MessageStructure, MessageTypes
                # 使用标准化的作业发送消息格式
                if hasattr(MessageStructure, 'homework_response'):
                    # 如果有homework_response方法，使用它
                    message = MessageStructure.homework_response(
                        student_name="老师发送",  # 这是老师端发送，所以student_name设为老师
                        student_class=class_name,
                        homeworks=[{
                            'subject': subject,
                            'content': content,
                            'teacher': self.teacher_name.get().strip(),
                            'timestamp': homework.get('timestamp', ''),
                            'status': '已发布'
                        }],
                        teacher_message=f"老师 {self.teacher_name.get().strip()} 向 {class_name} 发布了作业"
                    )
                    # 确保消息类型正确
                    message['type'] = MessageTypes.HOMEWORK_RESPONSE
                else:
                    # 如果没有MessageStructure.homework_response，使用teacher_connect方法
                    message = MessageStructure.teacher_connect(
                        teacher_name=self.teacher_name.get().strip(),
                        server_ip=self.server_ip.get().strip()
                    )
                    message.update({
                        "type": MessageTypes.HOMEWORK_RESPONSE,
                        "homework": {
                            "student_name": self.teacher_name.get().strip(),
                            "student_class": class_name,
                            "homeworks": [{
                                'subject': subject,
                                'content': content,
                                'teacher': self.teacher_name.get().strip(),
                                'timestamp': homework.get('timestamp', ''),
                                'status': '已发布'
                            }],
                            "teacher_message": f"老师 {self.teacher_name.get().strip()} 向 {class_name} 发布了作业"
                        }
                    })
            except ImportError:
                # 如果MessageStructure不可用，使用旧格式
                message = {
                    "type": MessageTypes.HOMEWORK_RESPONSE,
                    "homework": {
                        "student": self.teacher_name.get().strip(),
                        "class": class_name,
                        "subject": subject,
                        "content": content,
                        "teacher": self.teacher_name.get().strip(),
                        "timestamp": homework.get('timestamp', '')
                    }
                }
            
            self.comm._send_message(message)
            print(f"发送作业到服务器: {subject} - {class_name}班 - {content[:50]}...")
        
        # 清空输入框
        self.homework_text.delete(1.0, tk.END)
        
        # 刷新列表
        self.load_homework_list()
        self.update_statistics()
        
        messagebox.showinfo("成功", f"作业发送成功！已向 {class_name} 发送 {subject} 作业")
    
    def load_homework_list(self):
        """加载作业列表"""
        # 清空现有项目
        for item in self.homework_tree.get_children():
            self.homework_tree.delete(item)
        
        # 获取所有作业
        homeworks = self.data_manager.get_homeworks()
        
        # 添加到列表
        for homework in homeworks:
            values = (
                homework.get("id", ""),
                homework.get("subject", ""),
                homework.get("content", "")[:50] + "..." if len(homework.get("content", "")) > 50 else homework.get("content", ""),
                homework.get("class", ""),
                homework.get("teacher", ""),
                homework.get("timestamp", ""),
                homework.get("status", "")
            )
            self.homework_tree.insert("", tk.END, values=values)
    
    def view_all_homeworks(self):
        """查看所有作业"""
        self.load_homework_list()
        messagebox.showinfo("提示", "作业列表已刷新")
    
    def delete_homework(self):
        """删除选中的作业"""
        selected_items = self.homework_tree.selection()
        if not selected_items:
            messagebox.showwarning("警告", "请先选中要删除的作业")
            return
        
        if messagebox.askyesno("确认", "确定要删除选中的作业吗？"):
            for item in selected_items:
                values = self.homework_tree.item(item, "values")
                homework_id = int(values[0])
                self.data_manager.delete_homework(homework_id)
            
            self.load_homework_list()
            self.update_statistics()
            messagebox.showinfo("成功", "作业删除成功")
    
    def clear_data(self):
        """清空所有数据"""
        if messagebox.askyesno("确认", "确定要清空所有数据吗？此操作不可恢复！"):
            self.data_manager.clear_all_data()
            self.load_homework_list()
            self.update_statistics()
            messagebox.showinfo("成功", "所有数据已清空")
    
    def refresh_data(self):
        """刷新数据"""
        self.load_homework_list()
        self.update_statistics()
        messagebox.showinfo("提示", "数据已刷新")
    
    def update_statistics(self):
        """更新统计信息"""
        stats = self.data_manager.get_statistics()
        
        subject_stats_text = []
        for subject, count in stats["subject_stats"].items():
            if count > 0:
                subject_stats_text.append(f"{subject}: {count}个")
        
        stats_text = f"总作业数: {stats['total_homeworks']} | 留言数: {stats['message_count']} | 班级数: {stats['class_count']}"
        if subject_stats_text:
            stats_text += f" | 学科分布: {', '.join(subject_stats_text[:3])}"
            if len(subject_stats_text) > 3:
                stats_text += "..."
        
        self.stats_label.config(text=stats_text)
    
    def display_received_message(self, message_data):
        """显示接收到的留言"""
        content = message_data.get("content", "")
        sender_name = message_data.get("sender_name", message_data.get("student", "匿名"))
        class_name = message_data.get("class_name", message_data.get("class", ""))
        timestamp = message_data.get("timestamp", "刚刚")
        
        print(f"[{timestamp}] {sender_name}({class_name}): {content}")
        
        # 添加到数据管理器（如果可用）
        try:
            self.data_manager.add_message(
                content=content,
                student_name=sender_name,
                class_name=class_name
            )
        except:
            pass  # 如果添加失败，不影响显示
        
        # 显示通知
        self.root.after(0, lambda: messagebox.showinfo(
            "收到留言", 
            f"学生 {sender_name} ({class_name}) 发送了留言\n"
            f"内容: {content[:30]}...\n"
            f"时间: {timestamp}"
        ))
        
        # 更新统计信息
        self.root.after(0, self.update_statistics)
    
    def display_received_homework(self, homework_data):
        """显示收到的作业"""
        student = homework_data.get("student", "匿名")
        class_name = homework_data.get("class", "")
        subject = homework_data.get("subject", "")
        content = homework_data.get("content", "")
        teacher = homework_data.get("teacher", "")
        timestamp = homework_data.get("timestamp", "刚刚")
        status = homework_data.get("status", "已完成")
        
        # 添加作业到数据管理器
        try:
            homework = self.data_manager.add_homework(
                subject=subject,
                content=content,
                class_name=class_name,
                teacher_name=teacher,
                timestamp=timestamp,
                status=status
            )
            homework_id = homework.get("id", 0)
        except:
            homework_id = 0  # 如果添加失败，使用临时ID
        
        # 添加到作业列表
        values = (
            homework_id,
            subject,
            content[:50] + "..." if len(content) > 50 else content,
            class_name,
            teacher,
            timestamp,
            status
        )
        
        self.root.after(0, lambda: self.homework_tree.insert("", tk.END, values=values))
        
        # 显示通知
        self.root.after(0, lambda: messagebox.showinfo(
            "收到作业", 
            f"学生 {student} ({class_name}) 提交了作业\n"
            f"科目: {subject}\n"
            f"内容: {content[:30]}...\n"
            f"时间: {timestamp}"
        ))
        
        # 更新统计信息
        self.root.after(0, self.update_statistics)
    
    def on_fullscreen_toggle(self, *args):
        """全屏模式切换"""
        if self.fullscreen_var.get():
            self.enter_fullscreen_mode()
        else:
            self.exit_fullscreen_mode()
    
    def enter_fullscreen_mode(self):
        """进入全屏模式"""
        # 创建新的顶层窗口
        self.fullscreen_window = tk.Toplevel(self.root)
        self.fullscreen_window.title("作业查看 - 全屏模式")
        self.fullscreen_window.attributes('-fullscreen', True)
        self.fullscreen_window.attributes('-topmost', True)
        
        # 设置背景色
        self.fullscreen_window.configure(bg='black')
        
        # 创建全屏内容框架
        fullscreen_frame = ttk.Frame(self.fullscreen_window, padding="20")
        fullscreen_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建标题
        title_label = tk.Label(fullscreen_frame, text="作业列表 - 全屏模式", 
                              font=("Arial", 20, "bold"), bg='black', fg='white')
        title_label.pack(pady=(0, 20))
        
        # 创建全屏下的作业列表框架
        fs_list_frame = ttk.Frame(fullscreen_frame)
        fs_list_frame.pack(fill=tk.BOTH, expand=True)
        
        # 设置全屏模式下列的宽度
        fs_column_widths = {"ID": 60, "学科": 100, "内容": 500, "班级": 120, "老师": 100, "时间": 200, "状态": 100}
        fs_columns = ("ID", "学科", "内容", "班级", "老师", "时间", "状态")
        
        # 创建全屏模式下的作业树形控件
        self.fullscreen_tree = ttk.Treeview(fs_list_frame, columns=fs_columns, show='headings', height=15)
        
        # 设置列标题和宽度（更大）
        for col in fs_columns:
            self.fullscreen_tree.heading(col, text=col, font=("Arial", 12, "bold"))
            self.fullscreen_tree.column(col, width=fs_column_widths.get(col, 120), minwidth=80)
        
        # 添加滚动条
        fs_scrollbar_v = ttk.Scrollbar(fs_list_frame, orient=tk.VERTICAL, command=self.fullscreen_tree.yview)
        fs_scrollbar_h = ttk.Scrollbar(fs_list_frame, orient=tk.HORIZONTAL, command=self.fullscreen_tree.xview)
        self.fullscreen_tree.configure(yscrollcommand=fs_scrollbar_v.set, xscrollcommand=fs_scrollbar_h.set)
        
        self.fullscreen_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        fs_scrollbar_v.pack(side=tk.RIGHT, fill=tk.Y)
        fs_scrollbar_h.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 添加控制按钮框架
        control_frame = ttk.Frame(fullscreen_frame)
        control_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(control_frame, text="退出全屏", command=self.exit_fullscreen_mode).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(control_frame, text="刷新列表", command=self.refresh_fullscreen_list).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(control_frame, text="导出数据", command=self.export_fullscreen_data).pack(side=tk.LEFT)
        
        # 复制当前作业列表数据到全屏列表
        self.refresh_fullscreen_list()
        
        # 绑定ESC键退出全屏
        self.fullscreen_window.bind('<Escape>', lambda e: self.exit_fullscreen_mode())
        
        # 全屏窗口关闭事件
        self.fullscreen_window.protocol("WM_DELETE_WINDOW", self.exit_fullscreen_mode)
        
        print("已切换到全屏模式")
    
    def exit_fullscreen_mode(self):
        """退出全屏模式"""
        if self.fullscreen_window:
            self.fullscreen_window.destroy()
            self.fullscreen_window = None
        
        # 重置全屏变量
        self.fullscreen_var.set(False)
        
        print("已退出全屏模式")
    
    def request_class_list(self):
        """请求班级列表"""
        try:
            from communication import MessageStructure
            message = MessageStructure.class_list_request()
            self.comm._send_message(message)
            print("已发送班级列表请求")
        except Exception as e:
            print(f"发送班级列表请求失败: {e}")
    
    def refresh_fullscreen_list(self):
        """刷新全屏模式下的作业列表"""
        if hasattr(self, 'fullscreen_tree') and self.fullscreen_tree:
            # 清空全屏列表
            for item in self.fullscreen_tree.get_children():
                self.fullscreen_tree.delete(item)
            
            # 获取所有作业数据
            homeworks = self.data_manager.get_homeworks()
            
            # 添加到全屏列表
            for homework in homeworks:
                values = (
                    homework.get("id", ""),
                    homework.get("subject", ""),
                    homework.get("content", ""),  # 全屏模式下显示完整内容
                    homework.get("class", ""),
                    homework.get("teacher", ""),
                    homework.get("timestamp", ""),
                    homework.get("status", "")
                )
                self.fullscreen_tree.insert("", tk.END, values=values)
    
    def export_fullscreen_data(self):
        """导出全屏模式下的数据"""
        try:
            import csv
            import os
            
            # 获取当前目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
            filename = os.path.join(current_dir, f"homework_export_{self.get_current_timestamp()}.csv")
            
            # 获取作业数据
            homeworks = self.data_manager.get_homeworks()
            
            # 写入CSV文件
            with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
                fieldnames = ['ID', '学科', '内容', '班级', '老师', '时间', '状态']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for homework in homeworks:
                    writer.writerow({
                        'ID': homework.get("id", ""),
                        '学科': homework.get("subject", ""),
                        '内容': homework.get("content", ""),
                        '班级': homework.get("class", ""),
                        '老师': homework.get("teacher", ""),
                        '时间': homework.get("timestamp", ""),
                        '状态': homework.get("status", "")
                    })
            
            messagebox.showinfo("导出成功", f"数据已导出到：\n{filename}")
            print(f"数据已导出到：{filename}")
            
        except Exception as e:
            messagebox.showerror("导出失败", f"导出数据时出错：{str(e)}")
    
    def get_current_timestamp(self):
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def show_about(self):
        """显示关于对话框"""
        about_window = tk.Toplevel(self.root)
        about_window.title("关于教师端作业查看器")
        about_window.geometry("400x350")
        about_window.resizable(False, False)
        about_window.transient(self.root)
        about_window.grab_set()
        
        # 设置窗口居中
        about_window.update_idletasks()
        x = (about_window.winfo_screenwidth() // 2) - (about_window.winfo_width() // 2)
        y = (about_window.winfo_screenheight() // 2) - (about_window.winfo_height() // 2)
        about_window.geometry(f"+{x}+{y}")
        
        # 主框架
        main_frame = ttk.Frame(about_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        title_label = tk.Label(main_frame, text="教师端作业查看器", font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 10))
        
        # 版本信息
        version_label = tk.Label(main_frame, text="版本 2.1", font=("Arial", 12), foreground="blue")
        version_label.pack(pady=(0, 20))
        
        # 功能描述
        description = """
作者：卢文睿
开发时间：2025年
        """
        
        desc_label = tk.Label(main_frame, text=description, font=("Arial", 10), justify=tk.LEFT)
        desc_label.pack(pady=(0, 20), anchor=tk.W)
        
        # 关闭按钮
        close_button = ttk.Button(main_frame, text="关闭", command=about_window.destroy)
        close_button.pack(pady=(10, 0))
        
        # 绑定回车键关闭
        about_window.bind('<Return>', lambda e: about_window.destroy())
        about_window.focus_set()

    def on_closing(self):
        """窗口关闭事件"""
        # 如果在全屏模式，先退出全屏
        if self.fullscreen_window:
            self.exit_fullscreen_mode()
        
        if self.is_connected:
            self.disconnect_from_server()
        self.root.destroy()
    
    def run(self):
        """运行程序"""
        self.root.mainloop()

if __name__ == "__main__":
    app = TeacherGUI()
    app.run()