"""
学生端主程序
提供作业查看功能，可以作为服务器被老师连接 405 密码 xj123456
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import json
import os
from PIL import Image
import pystray
from communication import StudentServer, TeacherClient, MessageTypes, MessageStructure
from data_manager import DataManager
import socket
import subprocess

# 导入单实例检测相关模块
try:
    import win32event
    import win32api
    from winerror import ERROR_ALREADY_EXISTS
    HAS_WIN32 = True
except ImportError:
    HAS_WIN32 = False

class StudentGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("作业查看器 - 学生端")
        self.root.geometry("900x650")
        self.root.resizable(True, True)
        
        # 设置主窗口图标
        try:
            icon_path = "C:\\Users\\Lucas\\Desktop\\fan\\homework_viewer\\student.png"
            if os.path.exists(icon_path):
                # 先尝试使用iconphoto设置图标（支持PNG）
                from PIL import ImageTk
                icon_image = ImageTk.PhotoImage(Image.open(icon_path))
                self.root.iconphoto(True, icon_image)
                self.window_icon = icon_image  # 保持引用以防止被垃圾回收
                print(f"成功设置主窗口图标: {icon_path}")
            else:
                print(f"警告: 找不到图标文件 {icon_path}")
        except Exception as e:
            print(f"设置主窗口图标失败: {e}")
        
        # 初始化组件
        self.server = StudentServer()  # 学生端服务器
        self.data_manager = DataManager("student_data.json")
        
        # 初始化变量
        self.selected_class = tk.StringVar()
        self.student_name = tk.StringVar(value="学生")  # 设置默认值
        self.port = tk.IntVar(value=8888)
        self.selected_subject = tk.StringVar()
        
        # 连接状态
        self.is_server_running = False
        
        # 系统托盘相关变量
        self.tray_icon = None
        self.is_minimized_to_tray = False
        
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
        
        # 服务器设置框架
        server_frame = ttk.LabelFrame(main_frame, text="服务器设置", padding="10")
        server_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        server_frame.columnconfigure(1, weight=1)
        
        ttk.Label(server_frame, text="监听端口:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        ttk.Entry(server_frame, textvariable=self.port, width=10).grid(row=0, column=1, sticky=tk.W, padx=(0, 10))
        
        # 学生姓名字段已隐藏，设置为默认值
        # ttk.Label(server_frame, text="学生姓名:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        # ttk.Entry(server_frame, textvariable=self.student_name, width=15).grid(row=0, column=3, sticky=tk.W, padx=(0, 10))
        
        self.start_server_btn = ttk.Button(server_frame, text="启动服务器", command=self.start_server)
        self.start_server_btn.grid(row=0, column=2, padx=(10, 0))
        
        self.status_label = ttk.Label(server_frame, text="服务器未启动", foreground="red")
        self.status_label.grid(row=0, column=3, padx=(10, 0))
        
        # 后台运行选项
        self.run_in_background = tk.BooleanVar()
        background_check = ttk.Checkbutton(server_frame, text="后台运行", variable=self.run_in_background)
        background_check.grid(row=1, column=0, columnspan=4, sticky=tk.W, pady=(5, 0))
        self.run_in_background.set(True)
        
        # 已连接老师信息框架
        teachers_frame = ttk.LabelFrame(main_frame, text="已连接的老师", padding="10")
        teachers_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        teachers_frame.columnconfigure(0, weight=1)
        
        # 老师列表
        columns = ("老师ID", "老师姓名", "连接时间")
        self.teachers_tree = ttk.Treeview(teachers_frame, columns=columns, show='headings', height=3)
        for col in columns:
            self.teachers_tree.heading(col, text=col)
            self.teachers_tree.column(col, width=150)
        
        teachers_scrollbar = ttk.Scrollbar(teachers_frame, orient=tk.VERTICAL, command=self.teachers_tree.yview)
        self.teachers_tree.configure(yscrollcommand=teachers_scrollbar.set)
        
        self.teachers_tree.grid(row=0, column=0, sticky=(tk.W, tk.E))
        teachers_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 控制面板框架
        control_frame = ttk.LabelFrame(main_frame, text="控制面板", padding="10")
        control_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        control_frame.columnconfigure(1, weight=1)
        
        ttk.Label(control_frame, text="选择班级:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.class_combo = ttk.Combobox(control_frame, textvariable=self.selected_class, width=15)
        self.class_combo.grid(row=0, column=1, sticky=tk.W, padx=(0, 10))
        self.class_combo.bind('<<ComboboxSelected>>', self.on_class_selected)
        
        ttk.Label(control_frame, text="学科筛选:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.subject_combo = ttk.Combobox(control_frame, textvariable=self.selected_subject, width=15)
        self.subject_combo.grid(row=0, column=3, sticky=tk.W, padx=(0, 10))
        self.subject_combo.bind('<<ComboboxSelected>>', self.on_subject_selected)
        
        ttk.Button(control_frame, text="刷新作业", command=self.refresh_homeworks).grid(row=0, column=4, padx=(10, 0))
        
        # 添加全屏按钮
        ttk.Button(control_frame, text="全屏显示", command=self.toggle_fullscreen).grid(row=0, column=5, padx=(10, 0))
        
        # 添加高级选项按钮
        ttk.Button(control_frame, text="高级选项", command=self.show_advanced_options).grid(row=0, column=6, padx=(10, 0))
        
        # 作业列表框架
        homework_frame = ttk.LabelFrame(main_frame, text="作业列表", padding="10")
        homework_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        homework_frame.columnconfigure(0, weight=1)
        homework_frame.rowconfigure(0, weight=1)
        
        # 创建作业树形控件
        columns = ("ID", "学科", "内容", "老师", "时间")
        self.homework_tree = ttk.Treeview(homework_frame, columns=columns, show='headings', height=8)
        
        # 设置列标题和宽度
        for col in columns:
            self.homework_tree.heading(col, text=col)
            self.homework_tree.column(col, width=120 if col != "内容" else 300)
        
        # 添加滚动条
        homework_scrollbar = ttk.Scrollbar(homework_frame, orient=tk.VERTICAL, command=self.homework_tree.yview)
        self.homework_tree.configure(yscrollcommand=homework_scrollbar.set)
        
        self.homework_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        homework_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 配置主框架行权重
        main_frame.rowconfigure(3, weight=2)
        
        # 绑定窗口大小变化事件，实现自动调整字体
        self.root.bind("<Configure>", self.on_window_resize)
        
        # 初始化数据
        self.init_data()
        
        # 初始化字体大小设置
        self.default_font_size = 10
        self.current_font_size = self.default_font_size
        
        # 初始化全屏状态
        self.fullscreen = False
        
        # 创建全屏模式下的退出按钮
        self.fullscreen_exit_button = ttk.Button(self.root, text="退出全屏", command=self.exit_fullscreen,
                                              style="Accent.TButton")
        # 初始状态下隐藏
        self.fullscreen_exit_button.grid_remove()
        
        # 添加ESC键退出全屏
        self.root.bind("<Escape>", lambda e: self.exit_fullscreen() if self.fullscreen else None)
    
    def init_data(self):
        """初始化数据"""
        # 添加默认班级 - 仅包含701-710班级
        default_classes = [
            "701", "702", "703", "704", "705", "706", "707", "708", "709", "710"
        ]
        for class_name in default_classes:
            self.data_manager.add_class(class_name)
        
        # 加载班级列表
        classes = self.data_manager.get_classes()
        self.class_combo['values'] = classes
        
        # 加载学科列表
        subjects = self.data_manager.get_subjects()
        self.subject_combo['values'] = ["全部"] + subjects
        self.subject_combo.set("全部")
        
        # 设置默认班级
        if classes:
            self.class_combo.set(classes[0])
    
    def setup_message_handlers(self):
        """设置消息处理器"""
        def handle_homework_request(message, client_socket, teacher_id):
            """处理老师请求作业消息"""
            class_name = message.get('class', '')
            subject = message.get('subject', '')
            teacher_message = message.get('message', '')
            
            print(f"收到老师请求作业：班级={class_name}，学科={subject}")
            
            # 获取学生的作业数据
            student_class = self.selected_class.get()
            student_name = self.student_name.get()
            
            # 根据老师请求过滤对应的作业
            matched_homeworks = []
            if class_name == student_class or class_name == "全部":
                # 从本地数据中获取匹配的作业
                homeworks = self.data_manager.get_homeworks(
                    class_name=student_class,
                    subject=subject if subject != "全部" else None
                )
                
                for homework in homeworks:
                    # 构建符合格式的作业回应
                    homework_data = {
                        'id': homework.get('id', ''),
                        'class': homework.get('class', ''),
                        'subject': homework.get('subject', ''),
                        'content': homework.get('content', ''),
                        'teacher': homework.get('teacher', ''),
                        'student': student_name,
                        'timestamp': homework.get('timestamp', ''),
                        'status': homework.get('status', '已完成')
                    }
                    matched_homeworks.append(homework_data)
            
            # 发送作业回应给老师
            if matched_homeworks:
                response_message = MessageStructure.homework_response({
                    'student_class': student_class,
                    'student_name': student_name,
                    'homeworks': matched_homeworks,
                    'teacher_message': teacher_message
                })
                self.server.send_to_teacher(teacher_id, response_message)
                print(f"向老师发送了 {len(matched_homeworks)} 份作业")
            else:
                # 没有找到匹配的作业，发送空回应
                response_message = MessageStructure.homework_response({
                    'student_class': student_class,
                    'student_name': student_name,
                    'homeworks': [],
                    'teacher_message': teacher_message
                })
                self.server.send_to_teacher(teacher_id, response_message)
                print("没有找到匹配的作业，向老师发送空回应")
        
        # 注册处理器
        self.server.register_handler(MessageTypes.HOMEWORK_REQUEST, handle_homework_request)
        self.server.register_handler(MessageTypes.CLASS_LIST_REQUEST, self.handle_class_list_request)
        
        # 添加事件监听器
        self.server.add_listener('teacher_connected', self.on_teacher_connected)
        self.server.add_listener('teacher_disconnected', self.on_teacher_disconnected)
    
    def start_server(self):
        """启动服务器"""
        # 学生姓名已设置为默认值"学生"，无需验证
        def start_thread():
            if self.server.start_server():
                self.is_server_running = True
                self.root.after(0, self.on_server_start_success)
            else:
                self.root.after(0, self.on_server_start_failed)
        
        # 在新线程中启动
        threading.Thread(target=start_thread, daemon=True).start()
    
    def on_server_start_success(self):
        """服务器启动成功"""
        self.status_label.config(text=f"服务器运行中 (端口: {self.port.get()})", foreground="green")
        self.start_server_btn.config(text="停止服务器", command=self.stop_server, state="disabled")
        messagebox.showinfo("成功", "服务器启动成功，等待老师连接！")
    
    def on_server_start_failed(self):
        """服务器启动失败"""
        self.status_label.config(text="服务器启动失败", foreground="red")
        messagebox.showerror("错误", "服务器启动失败，请检查端口是否被占用")
    
    def stop_server(self):
        """停止服务器"""
        # 验证密码
        if not self.verify_exit_password():
            return
        
        self.server.stop_server()
        self.is_server_running = False
        self.status_label.config(text="服务器未启动", foreground="red")
        self.start_server_btn.config(text="启动服务器", command=self.start_server, state="normal")
        
        # 清空老师列表
        for item in self.teachers_tree.get_children():
            self.teachers_tree.delete(item)
    
    def on_teacher_connected(self, event_type, data):
        """老师连接事件"""
        teacher_id = data.get('teacher_id')
        teacher_data = data.get('teacher_data', {})
        teacher_name = teacher_data.get('teacher_name', 'Unknown')
        
        # 在老师列表中显示
        self.root.after(0, self.add_teacher_to_list, teacher_id, teacher_name)
        
        # 发送班级列表给新连接的老师
        self.send_class_list_to_teacher(teacher_id)
    
    def on_teacher_disconnected(self, event_type, data):
        """老师断开连接事件"""
        teacher_id = data.get('teacher_id')
        self.root.after(0, self.remove_teacher_from_list, teacher_id)
    
    def add_teacher_to_list(self, teacher_id, teacher_name):
        """在老师列表中添加老师"""
        # 查找是否已存在
        for item in self.teachers_tree.get_children():
            if self.teachers_tree.item(item)['values'][0] == teacher_id:
                return
        
        timestamp = "刚刚"
        self.teachers_tree.insert("", tk.END, values=(teacher_id, teacher_name, timestamp))
    
    def remove_teacher_from_list(self, teacher_id):
        """从老师列表中移除老师"""
        for item in self.teachers_tree.get_children():
            if self.teachers_tree.item(item)['values'][0] == teacher_id:
                self.teachers_tree.delete(item)
                break
    
    def send_homework_to_teacher(self, teacher_id, homework_data):
        """发送作业给老师（更新为使用MessageStructure）"""
        message = MessageStructure.homework_response(homework_data)
        self.server.send_to_teacher(teacher_id, message)
    
    def handle_class_list_request(self, message, client_socket, teacher_id):
        """处理班级列表请求"""
        self.send_class_list_to_teacher(teacher_id)
    
    def send_class_list_to_teacher(self, teacher_id):
        """发送班级列表给指定老师"""
        # 获取班级列表
        classes = self.data_manager.get_classes()
        # 发送班级列表响应
        message = MessageStructure.class_list_response(classes)
        self.server.send_to_teacher(teacher_id, message)
    

    
    def on_class_selected(self, event=None):
        """班级选择事件"""
        # 更新本地显示
        self.refresh_homeworks()
    
    def on_subject_selected(self, event=None):
        """学科选择事件"""
        # 更新本地显示
        self.refresh_homeworks()
    
    def refresh_homeworks(self):
        """刷新作业列表"""
        # 本地加载
        self.load_local_homeworks()
    
    def calculate_optimal_font_size(self):
        """计算最佳字体大小，确保作业文字占满空间"""
        # 获取作业列表区域的宽度
        if not hasattr(self.homework_tree, 'winfo_width'):
            return self.default_font_size
            
        tree_width = self.homework_tree.winfo_width()
        if tree_width <= 0:
            return self.default_font_size
            
        # 获取内容列的宽度（假设是第2列）
        content_col_width = tree_width * 0.6  # 大约60%的宽度给内容列
        
        # 基于内容列宽度计算字体大小
        # 简单公式：字体大小 = 内容列宽度 / 20
        # 最小10px，最大24px
        font_size = int(content_col_width / 20)
        font_size = max(10, min(24, font_size))
        
        return font_size
    
    def on_window_resize(self, event=None):
        """窗口大小变化时自动调整字体大小"""
        # 避免频繁计算，只在窗口大小真正变化时调整
        if hasattr(event, 'width') and hasattr(self, '_last_width') and event.width == self._last_width:
            return
        
        if hasattr(event, 'width'):
            self._last_width = event.width
            
        # 计算最佳字体大小
        new_font_size = self.calculate_optimal_font_size()
        
        # 如果字体大小发生变化，更新字体并刷新作业列表
        if new_font_size != self.current_font_size:
            self.current_font_size = new_font_size
            self.refresh_homeworks()
    
    def toggle_fullscreen(self):
        """切换全屏/普通模式"""
        if not self.fullscreen:
            self.enter_fullscreen()
        else:
            self.exit_fullscreen()
    
    def enter_fullscreen(self):
        """进入全屏模式"""
        # 保存当前窗口状态
        self.normal_window_state = self.root.state()
        self.normal_window_geometry = self.root.geometry()
        
        # 进入全屏模式
        self.root.attributes('-fullscreen', True)
        self.fullscreen = True
        
        # 显示退出全屏按钮，放置在右上角
        self.fullscreen_exit_button.place(relx=1.0, rely=0.0, anchor="ne", x=-10, y=10)
        
        # 调整UI以适应全屏
        self.on_window_resize()
    
    def exit_fullscreen(self):
        """退出全屏模式"""
        # 恢复普通模式
        self.root.attributes('-fullscreen', False)
        self.fullscreen = False
        
        # 恢复窗口状态
        if hasattr(self, 'normal_window_state') and self.normal_window_state:
            self.root.state(self.normal_window_state)
        if hasattr(self, 'normal_window_geometry') and self.normal_window_geometry:
            self.root.geometry(self.normal_window_geometry)
        
        # 隐藏退出全屏按钮
        self.fullscreen_exit_button.place_forget()
        
        # 调整UI以适应普通窗口
        self.on_window_resize()
    
    def load_local_homeworks(self):
        """从本地加载作业"""
        homeworks = self.data_manager.get_homeworks(
            class_name=self.selected_class.get() if self.selected_class.get() else None,
            subject=self.selected_subject.get() if self.selected_subject.get() != "全部" else None
        )
        
        # 清空现有项目
        for item in self.homework_tree.get_children():
            self.homework_tree.delete(item)
        
        # 确保字体大小已计算
        if not hasattr(self, 'current_font_size'):
            self.current_font_size = self.calculate_optimal_font_size()
        
        # 设置字体
        style = ttk.Style()
        style.configure("Homework.Treeview", font=("微软雅黑", self.current_font_size))
        self.homework_tree.configure(style="Homework.Treeview")
        
        # 添加作业 - 只显示"科目：作业"格式
        for homework in homeworks:
            subject = homework.get("subject", "")
            content = homework.get("content", "")
            # 组合成"科目：作业"格式
            display_text = f"{subject}：{content}"
            values = (
                homework.get("id", ""),
                subject,  # 保留原学科列用于筛选
                display_text,
                homework.get("teacher", ""),
                homework.get("timestamp", "")
            )
            self.homework_tree.insert("", tk.END, values=values)
    

    
    def on_closing(self):
        """窗口关闭事件"""
        if self.run_in_background.get():
            # 后台运行：最小化到系统托盘而不是关闭
            self.minimize_to_tray()
        else:
            # 正常关闭：验证密码后才能退出
            if self.verify_exit_password():
                # 停止服务器并退出
                if self.is_server_running:
                    self.server.stop_server()
                self.root.destroy()

    def verify_exit_password(self):
        """验证退出密码"""
        password_window = tk.Toplevel(self.root)
        password_window.title("密码验证")
        password_window.geometry("350x200")
        password_window.resizable(False, False)
        
        # 居中显示
        password_window.transient(self.root)
        password_window.grab_set()
        password_window.geometry("+%d+%d" % (
            self.root.winfo_rootx() + 50,
            self.root.winfo_rooty() + 50
        ))
        
        # 提示标签
        ttk.Label(password_window, text="退出密码验证", font=("Arial", 12, "bold")).pack(pady=(20, 10))
        ttk.Label(password_window, text="请输入退出密码：", font=("Arial", 10)).pack(pady=(0, 5))
        
        # 密码输入框
        password_var = tk.StringVar()
        password_entry = ttk.Entry(password_window, textvariable=password_var, show="*", width=20, font=("Arial", 10))
        password_entry.pack(pady=(0, 20))
        password_entry.focus()
        
        # 验证结果标签
        result_label = ttk.Label(password_window, text="", foreground="red", font=("Arial", 9))
        result_label.pack()
        
        # 按钮框架
        button_frame = ttk.Frame(password_window)
        button_frame.pack(pady=(0, 20))
        
        # 验证结果变量
        verify_result = {"success": False}
        
        def check_password():
            """检查密码"""
            password = password_var.get()
            if self.data_manager.verify_password(password):
                verify_result["success"] = True
                password_window.destroy()
            else:
                result_label.config(text="密码错误，请重新输入")
                password_var.set("")
                password_entry.focus()
        
        def cancel():
            """取消"""
            verify_result["success"] = False
            password_window.destroy()
        
        # 按钮
        ttk.Button(button_frame, text="确定", command=check_password, width=10).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="取消", command=cancel, width=10).pack(side=tk.LEFT)
        
        # 绑定回车键
        password_entry.bind('<Return>', lambda event: check_password())
        password_entry.bind('<Escape>', lambda event: cancel())
        
        # 等待窗口关闭
        password_window.wait_window()
        
        return verify_result["success"]
    
    def show_advanced_options(self):
        """显示高级选项对话框"""
        # 先验证当前密码
        if not self.verify_current_password():
            return
        
        # 创建高级选项窗口
        options_window = tk.Toplevel(self.root)
        options_window.title("高级选项")
        options_window.geometry("400x300")
        options_window.resizable(False, False)
        
        # 居中显示
        options_window.transient(self.root)
        options_window.grab_set()
        options_window.geometry("+%d+%d" % (
            self.root.winfo_rootx() + 50,
            self.root.winfo_rooty() + 50
        ))
        
        # 设置窗口内边距
        main_frame = ttk.Frame(options_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 修改密码按钮
        ttk.Button(main_frame, text="修改密码", command=self.change_password_dialog, width=20).pack(pady=(20, 20))
        
        # 清空所有数据按钮
        ttk.Button(main_frame, text="清空所有数据（谨慎操作）", command=self.confirm_clear_data, width=25).pack(pady=(10, 10))
        
        # 关闭按钮
        ttk.Button(main_frame, text="关闭", command=options_window.destroy, width=15).pack(pady=(30, 10))
    
    def verify_current_password(self):
        """验证当前密码"""
        password_window = tk.Toplevel(self.root)
        password_window.title("密码验证")
        password_window.geometry("350x200")
        password_window.resizable(False, False)
        
        # 居中显示
        password_window.transient(self.root)
        password_window.grab_set()
        
        # 提示标签
        ttk.Label(password_window, text="高级选项密码验证", font=("Arial", 12, "bold")).pack(pady=(20, 10))
        ttk.Label(password_window, text="请输入当前密码：", font=("Arial", 10)).pack(pady=(0, 5))
        
        # 密码输入框
        password_var = tk.StringVar()
        password_entry = ttk.Entry(password_window, textvariable=password_var, show="*", width=20, font=("Arial", 10))
        password_entry.pack(pady=(0, 20))
        password_entry.focus()
        
        # 验证结果标签
        result_label = ttk.Label(password_window, text="", foreground="red", font=("Arial", 9))
        result_label.pack()
        
        # 按钮框架
        button_frame = ttk.Frame(password_window)
        button_frame.pack(pady=(0, 20))
        
        # 验证结果变量
        verify_result = {"success": False}
        
        def check_password():
            """检查密码"""
            password = password_var.get()
            if self.data_manager.verify_password(password):
                verify_result["success"] = True
                password_window.destroy()
            else:
                result_label.config(text="密码错误，请重新输入")
                password_var.set("")
                password_entry.focus()
        
        def cancel():
            """取消"""
            verify_result["success"] = False
            password_window.destroy()
        
        # 按钮
        ttk.Button(button_frame, text="确定", command=check_password, width=10).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="取消", command=cancel, width=10).pack(side=tk.LEFT)
        
        # 绑定回车键
        password_entry.bind('<Return>', lambda event: check_password())
        password_entry.bind('<Escape>', lambda event: cancel())
        
        # 等待窗口关闭
        password_window.wait_window()
        
        return verify_result["success"]
    
    def change_password_dialog(self):
        """修改密码对话框"""
        # 创建修改密码窗口
        change_window = tk.Toplevel(self.root)
        change_window.title("修改密码")
        change_window.geometry("400x280")
        change_window.resizable(False, False)
        
        # 居中显示
        change_window.transient(self.root)
        change_window.grab_set()
        
        # 设置窗口内边距
        main_frame = ttk.Frame(change_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 当前密码
        ttk.Label(main_frame, text="当前密码：", font=("Arial", 10)).grid(row=0, column=0, sticky=tk.W, pady=(10, 5))
        current_password_var = tk.StringVar()
        current_password_entry = ttk.Entry(main_frame, textvariable=current_password_var, show="*", width=25, font=("Arial", 10))
        current_password_entry.grid(row=0, column=1, pady=(10, 5))
        
        # 新密码
        ttk.Label(main_frame, text="新密码：", font=("Arial", 10)).grid(row=1, column=0, sticky=tk.W, pady=(10, 5))
        new_password_var = tk.StringVar()
        new_password_entry = ttk.Entry(main_frame, textvariable=new_password_var, show="*", width=25, font=("Arial", 10))
        new_password_entry.grid(row=1, column=1, pady=(10, 5))
        
        # 确认新密码
        ttk.Label(main_frame, text="确认新密码：", font=("Arial", 10)).grid(row=2, column=0, sticky=tk.W, pady=(10, 5))
        confirm_password_var = tk.StringVar()
        confirm_password_entry = ttk.Entry(main_frame, textvariable=confirm_password_var, show="*", width=25, font=("Arial", 10))
        confirm_password_entry.grid(row=2, column=1, pady=(10, 5))
        
        # 提示标签
        tip_label = ttk.Label(main_frame, text="密码修改成功后，重启应用生效", foreground="blue", font=("Arial", 9))
        tip_label.grid(row=3, column=0, columnspan=2, pady=(5, 10))
        
        # 错误信息标签
        error_label = ttk.Label(main_frame, text="", foreground="red", font=("Arial", 9))
        error_label.grid(row=4, column=0, columnspan=2, pady=(5, 10))
        
        def validate_and_change_password():
            """验证并修改密码"""
            current_password = current_password_var.get()
            new_password = new_password_var.get()
            confirm_password = confirm_password_var.get()
            
            # 验证当前密码
            if not self.data_manager.verify_password(current_password):
                error_label.config(text="当前密码错误")
                return
            
            # 验证新密码长度
            if len(new_password) < 6:
                error_label.config(text="新密码长度至少为6位")
                return
            
            # 验证两次输入是否一致
            if new_password != confirm_password:
                error_label.config(text="两次输入的新密码不一致")
                return
            
            # 修改密码
            if self.data_manager.set_password(new_password):
                messagebox.showinfo("成功", "密码修改成功，请重启应用以生效")
                change_window.destroy()
            else:
                error_label.config(text="密码修改失败")
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=(10, 0))
        
        # 按钮
        ttk.Button(button_frame, text="确定", command=validate_and_change_password, width=10).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="取消", command=change_window.destroy, width=10).pack(side=tk.LEFT)
        
        # 绑定回车键
        confirm_password_entry.bind('<Return>', lambda event: validate_and_change_password())
        change_window.bind('<Escape>', lambda event: change_window.destroy())
    
    def confirm_clear_data(self):
        """确认清空数据"""
        if messagebox.askyesno("确认", "确定要清空所有数据吗？此操作不可恢复！"):
            # 再次验证密码
            if self.verify_current_password():
                self.data_manager.clear_all_data()
                messagebox.showinfo("成功", "所有数据已清空")
                # 刷新作业列表
                self.refresh_homeworks()
    
    def minimize_to_tray(self):
        """最小化到系统托盘"""
        try:
            self.root.withdraw()  # 隐藏主窗口
            self.create_tray_icon()
            self.is_minimized_to_tray = True
            print("已最小化到系统托盘")
        except Exception as e:
            print(f"最小化到系统托盘失败: {e}")
            # 如果系统托盘创建失败，正常关闭
            if self.is_server_running:
                self.server.stop_server()
            self.root.destroy()
    
    def restore_from_tray(self):
        """从系统托盘恢复窗口"""
        try:
            if self.tray_icon:
                self.tray_icon.stop()
                self.tray_icon = None
            
            self.root.deiconify()  # 显示主窗口
            self.root.lift()  # 将窗口提升到前台
            self.root.focus_force()  # 强制获得焦点
            self.is_minimized_to_tray = False
            print("已从系统托盘恢复窗口")
        except Exception as e:
            print(f"从系统托盘恢复窗口失败: {e}")
    
    def create_tray_icon(self):
        """创建系统托盘图标"""
        try:
            # 使用用户指定的图标文件路径
            image_path = "C:\\Users\\Lucas\\Desktop\\fan\\homework_viewer\\student.png"
            
            # 检查图片文件是否存在
            if os.path.exists(image_path):
                # 使用指定的图标文件作为托盘图标
                image = Image.open(image_path)
            else:
                # 如果图片不存在，创建默认图标
                print(f"未找到图标文件 {image_path}，使用默认图标")
                image = Image.new('RGB', (64, 64), color=(0, 123, 255))
            
            # 创建托盘图标
            self.tray_icon = pystray.Icon(
                "homework_viewer",
                image,
                "作业查看器 - 学生端",
                menu=self.create_system_tray_menu()
            )
            
            # 在新线程中运行托盘图标
            threading.Thread(target=self.tray_icon.run, daemon=True).start()
            
        except Exception as e:
            print(f"创建系统托盘图标失败: {e}")
            # 如果加载图片失败，使用默认图标
            try:
                image = Image.new('RGB', (64, 64), color=(0, 123, 255))
                self.tray_icon = pystray.Icon(
                    "homework_viewer",
                    image,
                    "作业查看器 - 学生端",
                    menu=self.create_system_tray_menu()
                )
                threading.Thread(target=self.tray_icon.run, daemon=True).start()
            except Exception as e2:
                print(f"创建默认托盘图标也失败: {e2}")
                raise e2
    
    def create_system_tray_menu(self):
        """创建系统托盘菜单"""
        def hide_window(icon, item):
            self.tray_icon.visible = False
        
        return pystray.Menu(
            pystray.MenuItem("显示窗口", self.restore_from_tray),
            pystray.MenuItem("隐藏窗口", hide_window),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("关于", self.show_about),
            pystray.MenuItem("退出", self.quit_application)
        )
    
    def show_tray_notification(self, title, message, duration=3000):
        """显示托盘通知"""
        try:
            if self.tray_icon:
                self.tray_icon.show_notification(title, message, duration)
        except Exception as e:
            print(f"显示托盘通知失败: {e}")
    
    def get_local_ip(self):
        """获取本机IP地址"""
        try:
            # 使用 ipconfig 命令获取本机IP
            result = subprocess.run(['ipconfig'], capture_output=True, text=True, encoding='gbk')
            lines = result.stdout.splitlines()
            for line in lines:
                if "IPv4 地址" in line or "IP Address" in line:
                    # 提取IP地址
                    ip = line.split(":")[-1].strip()
                    if ip and not ip.startswith("169.254"):  # 排除自动配置地址
                        return ip
            return "127.0.0.1"
        except Exception:
            return "127.0.0.1"
    
    def show_about(self, icon=None, item=None):
        """显示关于信息"""
        local_ip = self.get_local_ip()
        
        about_text = f"""作业查看器 - 学生端

版本: 2.1
功能: 系统托盘后台运行

网络信息:
默认服务器端口: 8888

系统信息:
操作系统: Windows

作者: 0510卢文睿
开发时间: 2025年"""
        
        messagebox.showinfo("关于", about_text)
    
    def quit_application(self, icon=None, item=None):
        """退出应用程序"""
        try:
            # 在主线程中验证密码，避免线程阻塞
            self.root.after(0, self._verify_and_quit)
        except Exception as e:
            print(f"退出应用程序时出错: {e}")
    
    def _verify_and_quit(self):
        """在主线程中验证密码并退出"""
        try:
            # 确保主窗口是可见的，以便密码验证窗口能正常显示
            self.root.deiconify()
            self.root.lift()
            self.root.focus_force()
            
            # 临时停止托盘图标，避免UI冲突
            tray_was_running = False
            if self.tray_icon:
                tray_was_running = True
                try:
                    self.tray_icon.stop()
                except:
                    pass
                self.tray_icon = None
            
            # 验证退出密码
            if not self.verify_exit_password():
                # 密码错误，恢复托盘图标
                if tray_was_running:
                    self.root.after(500, self.create_tray_icon)
                    self.root.after(600, lambda: self.root.withdraw())
                return
            
            # 停止服务器
            if self.is_server_running:
                self.server.stop_server()
            
            # 退出应用程序
            self.root.quit()
            self.root.destroy()
        except Exception as e:
            print(f"退出应用程序时出错: {e}")
            # 错误时也要恢复托盘图标
            if tray_was_running:
                self.root.after(500, self.create_tray_icon)
                self.root.after(600, lambda: self.root.withdraw())
    
    def on_teacher_connected(self, event_type, data):
        """老师连接事件"""
        teacher_id = data.get('teacher_id')
        teacher_data = data.get('teacher_data', {})
        teacher_name = teacher_data.get('teacher_name', 'Unknown')
        
        # 在老师列表中显示
        self.root.after(0, self.add_teacher_to_list, teacher_id, teacher_name)
        
        # 发送班级列表给新连接的老师
        self.send_class_list_to_teacher(teacher_id)
        
        # 如果在系统托盘运行，显示通知
        if self.is_minimized_to_tray:
            self.root.after(0, self.show_tray_notification, 
                "老师连接", f"老师 {teacher_name} 已连接")
    
    def on_teacher_disconnected(self, event_type, data):
        """老师断开连接事件"""
        teacher_id = data.get('teacher_id')
        self.root.after(0, self.remove_teacher_from_list, teacher_id)
        
        # 如果在系统托盘运行，显示通知
        if self.is_minimized_to_tray:
            self.root.after(0, self.show_tray_notification, 
                "老师断开", f"老师 {teacher_id} 已断开连接")
    
    def run(self):
        """运行程序"""
        self.root.mainloop()

def ensure_single_instance():
    """确保程序只有一个实例在运行
    
    Returns:
        bool: 如果是第一个实例返回True，否则返回False
    """
    if HAS_WIN32:
        # 创建一个命名互斥锁
        mutex_name = "HomeworkViewerStudentMutex"
        try:
            # 尝试创建互斥锁，如果已存在则会抛出ERROR_ALREADY_EXISTS错误
            mutex = win32event.CreateMutex(None, True, mutex_name)
            last_error = win32api.GetLastError()
            
            if last_error == ERROR_ALREADY_EXISTS:
                # 程序已经在运行
                return False
            # 首次运行，返回True
            return True
        except Exception as e:
            print(f"单实例检测失败: {e}")
            # 出错时允许程序继续运行
            return True
    else:
        # 非Windows系统或缺少win32库，尝试使用文件锁方式
        lock_file = os.path.join(os.path.expanduser("~"), ".homework_viewer_student.lock")
        try:
            # 尝试以排他模式打开文件
            with open(lock_file, 'w') as f:
                f.write(str(os.getpid()))
            # 设置程序退出时删除锁文件
            import atexit
            atexit.register(lambda: os.remove(lock_file) if os.path.exists(lock_file) else None)
            return True
        except IOError:
            # 文件已被锁定，程序可能已在运行
            return False

if __name__ == "__main__":
    # 确保只有一个实例在运行
    if not ensure_single_instance():
        root = tk.Tk()
        root.withdraw()  # 隐藏主窗口
        messagebox.showinfo("提示", "程序已经在运行中！")
        root.destroy()
        exit(0)
    
    app = StudentGUI()
    app.run()