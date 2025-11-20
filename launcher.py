"""
作业查看器启动器
提供启动学生端和老师端的选项
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys
import os

class HomeworkViewerLauncher:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("作业查看器 - 启动器")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        
        # 居中窗口
        self.center_window()
        
        self.setup_ui()
    
    def center_window(self):
        """将窗口居中显示"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def setup_ui(self):
        """设置用户界面"""
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        title_label = ttk.Label(main_frame, text="作业查看器系统", font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # 描述
        desc_label = ttk.Label(main_frame, text="基于局域网通信的作业管理系统", font=("Arial", 10))
        desc_label.pack(pady=(0, 30))
        
        # 功能按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)
        
        # 老师端按钮
        teacher_btn = ttk.Button(
            button_frame, 
            text="启动老师端", 
            command=self.start_teacher,
            width=20
        )
        teacher_btn.pack(pady=10)
        
        teacher_desc = ttk.Label(button_frame, text="用于发送作业、管理学生留言", font=("Arial", 8))
        teacher_desc.pack()
        
        # 分隔线
        separator = ttk.Separator(main_frame, orient='horizontal')
        separator.pack(fill=tk.X, pady=20)
        
        # 学生端按钮
        student_btn = ttk.Button(
            button_frame, 
            text="启动学生端", 
            command=self.start_student,
            width=20
        )
        student_btn.pack(pady=10)
        
        student_desc = ttk.Label(button_frame, text="用于查看作业、发送留言", font=("Arial", 8))
        student_desc.pack()
        
        # 退出按钮
        exit_btn = ttk.Button(main_frame, text="退出程序", command=self.root.quit, width=15)
        exit_btn.pack(pady=(30, 0))
        
        # 版权信息
        copyright_label = ttk.Label(main_frame, text="v1.0 - 局域网作业管理系统", font=("Arial", 8), foreground="gray")
        copyright_label.pack(side=tk.BOTTOM, pady=(10, 0))
    
    def start_teacher(self):
        """启动老师端"""
        try:
            # 获取当前目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
            teacher_path = os.path.join(current_dir, "teacher", "teacher_gui.py")
            
            if os.path.exists(teacher_path):
                # 启动老师端
                subprocess.Popen([sys.executable, teacher_path])
                messagebox.showinfo("成功", "老师端已启动！")
            else:
                messagebox.showerror("错误", f"找不到老师端程序：{teacher_path}")
        except Exception as e:
            messagebox.showerror("错误", f"启动老师端失败：{e}")
    
    def start_student(self):
        """启动学生端"""
        try:
            # 获取当前目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
            student_path = os.path.join(current_dir, "student", "student_gui.py")
            
            if os.path.exists(student_path):
                # 启动学生端
                subprocess.Popen([sys.executable, student_path])
                messagebox.showinfo("成功", "学生端已启动！")
            else:
                messagebox.showerror("错误", f"找不到学生端程序：{student_path}")
        except Exception as e:
            messagebox.showerror("错误", f"启动学生端失败：{e}")
    
    def run(self):
        """运行启动器"""
        self.root.mainloop()

if __name__ == "__main__":
    app = HomeworkViewerLauncher()
    app.run()