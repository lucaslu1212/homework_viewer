"""
学生端主程序
提供作业查看功能，可以作为服务器被老师连接
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

class StudentGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("作业查看器 - 学生端")
        self.root.geometry("900x650")
        self.root.resizable(True, True)
        
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
        self.run_in_background.set(False)
        
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
        
        # 初始化数据
        self.init_data()
    
    def init_data(self):
        """初始化数据"""
        # 添加默认班级
        default_classes = ["高一(1)班", "高一(2)班", "高一(3)班", "高二(1)班", "高二(2)班"]
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
    
    def load_local_homeworks(self):
        """从本地加载作业"""
        homeworks = self.data_manager.get_homeworks(
            class_name=self.selected_class.get() if self.selected_class.get() else None,
            subject=self.selected_subject.get() if self.selected_subject.get() != "全部" else None
        )
        
        # 清空现有项目
        for item in self.homework_tree.get_children():
            self.homework_tree.delete(item)
        
        # 添加作业
        for homework in homeworks:
            values = (
                homework.get("id", ""),
                homework.get("subject", ""),
                homework.get("content", ""),
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
            # 正常关闭：询问用户是否确认退出
            if messagebox.askyesno("确认退出", "确定要退出作业查看器吗？"):
                # 停止服务器并退出
                if self.is_server_running:
                    self.server.stop_server()
                self.root.destroy()
    
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
            # 获取当前脚本所在目录的父目录（homework_viewer目录）
            script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            image_path = os.path.join(script_dir, "student.png")
            
            # 检查图片文件是否存在
            if os.path.exists(image_path):
                # 使用 student.png 作为托盘图标
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
本机IP地址: {local_ip}
服务器端口: 8888

系统信息:
操作系统: Windows
Python版本: 3.x

作者: 0510卢文睿
开发时间: 2025年"""
        
        messagebox.showinfo("关于", about_text)
    
    def quit_application(self, icon=None, item=None):
        """退出应用程序"""
        try:
            # 询问用户是否确认退出
            if not messagebox.askyesno("确认退出", "确定要退出作业查看器吗？"):
                return
            
            # 停止系统托盘图标
            if self.tray_icon:
                self.tray_icon.stop()
                self.tray_icon = None
            
            # 停止服务器
            if self.is_server_running:
                self.server.stop_server()
            
            # 退出应用程序
            self.root.quit()
            self.root.destroy()
        except Exception as e:
            print(f"退出应用程序时出错: {e}")
    
    def on_teacher_connected(self, event_type, data):
        """老师连接事件"""
        teacher_id = data.get('teacher_id')
        teacher_data = data.get('teacher_data', {})
        teacher_name = teacher_data.get('teacher_name', 'Unknown')
        
        # 在老师列表中显示
        self.root.after(0, self.add_teacher_to_list, teacher_id, teacher_name)
        
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

if __name__ == "__main__":
    app = StudentGUI()
    app.run()