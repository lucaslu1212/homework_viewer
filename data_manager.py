"""
数据存储模块
负责管理作业、留言等数据的存储和管理
"""

import json
import os
import shutil
import hashlib
from datetime import datetime
from typing import Dict, List, Any
import platform

# 尝试导入win32api用于检测U盘（Windows系统）
try:
    import win32api
    import win32file
    CAN_DETECT_USB = True
except ImportError:
    print("未找到win32api模块，U盘检测功能将不可用。请安装pywin32: pip install pywin32")
    CAN_DETECT_USB = False

class DataManager:
    def __init__(self, data_file="data.json"):
        # 定义数据文件存储路径 - 修复路径构建
        self.base_data_dir = os.path.join("C:", os.sep, "Program Files", "xsd")
        
        # 确保数据目录存在
        self._ensure_data_directory_exists()
        
        # 构建完整的数据文件路径
        self.data_file = os.path.join(self.base_data_dir, data_file)
        
        # 加载数据
        self.data = self._load_data()
    
    def _ensure_data_directory_exists(self):
        """确保数据目录存在，如果不存在则创建
        
        处理可能的权限问题：
        1. 尝试直接创建目录
        2. 如果失败，尝试创建在用户目录下作为备选
        """
        # 首先尝试创建在Program Files下
        if not os.path.exists(self.base_data_dir):
            try:
                # 尝试直接创建目录
                os.makedirs(self.base_data_dir, exist_ok=True)
                print(f"成功创建数据目录: {self.base_data_dir}")
            except PermissionError:
                # 如果没有管理员权限，尝试在用户目录下创建备选路径
                print(f"创建目录时权限不足: {self.base_data_dir}")
                print("尝试在用户目录下创建数据目录...")
                # 使用用户目录作为备选路径
                user_dir = os.path.expanduser("~")
                self.base_data_dir = os.path.join(user_dir, "xsd")
                try:
                    os.makedirs(self.base_data_dir, exist_ok=True)
                    print(f"成功在用户目录创建备选数据目录: {self.base_data_dir}")
                except Exception as e:
                    print(f"创建备选数据目录失败: {e}")
                    # 即使创建失败，程序仍然可以继续运行，但可能会遇到文件操作错误
                    pass
            except Exception as e:
                print(f"创建数据目录时发生未知错误: {e}")
    def _load_data(self):
        """从文件加载数据"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载数据失败: {e}")
        
        return self._get_default_data()
    
    def _get_default_data(self):
        """获取默认数据结构"""
        return {
            "homeworks": [],      # 作业列表
            "messages": [],       # 留言列表
            "classes": [],        # 班级列表
            "subjects": ["语文", "数学", "英语", "物理", "化学", "生物", "历史", "地理", "政治"],  # 学科列表
            "class_assignments": {},  # 班级对应关系
            "password": self._encrypt_password("xiangjiang"),  # 默认密码（已加密）
            "password_version": "encrypted"  # 标识密码已加密
        }
    
    def save_data(self):
        """保存数据到文件"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存数据失败: {e}")
            return False
    
    def add_homework(self, subject: str, content: str, class_name: str, teacher_name: str = "老师", overwrite: bool = True, **kwargs) -> Dict[str, Any]:
        """添加作业
        
        Args:
            subject: 科目名称
            content: 作业内容
            class_name: 班级名称
            teacher_name: 老师姓名
            overwrite: 是否覆盖相同科目的作业（默认True）
            **kwargs: 额外参数，如 timestamp, status 等
        """
        # 获取额外参数
        timestamp = kwargs.get('timestamp', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        status = kwargs.get('status', 'active')
        
        # 如果启用覆盖模式，先检查是否已存在相同科目的作业
        if overwrite:
            existing_homework = None
            for homework in self.data["homeworks"]:
                if homework["subject"] == subject and homework["class"] == class_name:
                    existing_homework = homework
                    break
            
            if existing_homework:
                # 更新现有作业
                existing_homework.update({
                    "content": content,
                    "teacher": teacher_name,
                    "timestamp": timestamp,
                    "status": status
                })
                self.save_data()
                return existing_homework
        
        # 创建新作业
        homework = {
            "id": len(self.data["homeworks"]) + 1,
            "subject": subject,
            "content": content,
            "class": class_name,
            "teacher": teacher_name,
            "timestamp": timestamp,
            "status": status
        }
        self.data["homeworks"].append(homework)
        self.save_data()
        return homework
    
    def get_homeworks(self, class_name: str = None, subject: str = None) -> List[Dict[str, Any]]:
        """获取作业列表"""
        homeworks = self.data["homeworks"]
        
        if class_name:
            homeworks = [h for h in homeworks if h.get("class") == class_name]
        
        if subject:
            homeworks = [h for h in homeworks if h.get("subject") == subject]
        
        # 按时间倒序排列
        homeworks.sort(key=lambda x: x["timestamp"], reverse=True)
        return homeworks
    
    def add_message(self, content: str, student_name: str, class_name: str = "") -> Dict[str, Any]:
        """添加留言"""
        message = {
            "id": len(self.data["messages"]) + 1,
            "content": content,
            "student": student_name,
            "class": class_name,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "active"
        }
        self.data["messages"].append(message)
        self.save_data()
        return message
    
    def get_messages(self, class_name: str = None) -> List[Dict[str, Any]]:
        """获取留言列表"""
        messages = self.data["messages"]
        
        if class_name:
            messages = [m for m in messages if m.get("class") == class_name]
        
        # 按时间倒序排列
        messages.sort(key=lambda x: x["timestamp"], reverse=True)
        return messages
    
    def add_class(self, class_name: str):
        """添加班级"""
        if class_name not in self.data["classes"]:
            self.data["classes"].append(class_name)
            self.save_data()
    
    def get_classes(self) -> List[str]:
        """获取班级列表"""
        return self.data["classes"]
    
    def get_subjects(self) -> List[str]:
        """获取学科列表"""
        return self.data["subjects"]
    
    def delete_homework(self, homework_id: int) -> bool:
        """删除作业"""
        original_count = len(self.data["homeworks"])
        self.data["homeworks"] = [h for h in self.data["homeworks"] if h["id"] != homework_id]
        
        if len(self.data["homeworks"]) < original_count:
            self.save_data()
            return True
        return False
    
    def delete_message(self, message_id: int) -> bool:
        """删除留言"""
        original_count = len(self.data["messages"])
        self.data["messages"] = [m for m in self.data["messages"] if m["id"] != message_id]
        
        if len(self.data["messages"]) < original_count:
            self.save_data()
            return True
        return False
    
    def clear_all_data(self):
        """清空所有数据"""
        # 保留密码设置
        current_password = self.get_password()
        self.data = self._get_default_data()
        self.set_password(current_password)
        self.save_data()
    
    def _encrypt_password(self, password):
        """加密密码
        
        Args:
            password: 明文密码
            
        Returns:
            str: 加密后的密码
        """
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _is_password_encrypted(self):
        """检查密码是否已加密
        
        Returns:
            bool: 密码是否已加密
        """
        return (self.data.get("password_version") == "encrypted" or 
               len(self.data.get("password", "")) == 64)  # SHA-256加密后长度为64
    
    def get_password(self):
        """获取当前密码"""
        return self.data.get("password", "xiangjiang")
    
    def set_password(self, new_password):
        """设置新密码
        
        Args:
            new_password: 新密码字符串
        
        Returns:
            bool: 设置是否成功
        """
        if not new_password or len(new_password.strip()) == 0:
            return False
        
        self.data["password"] = self._encrypt_password(new_password)
        self.data["password_version"] = "encrypted"  # 标记为已加密
        return self.save_data()
    
    def verify_password(self, password_to_check):
        """验证密码是否正确
        
        Args:
            password_to_check: 待验证的密码
        
        Returns:
            bool: 密码是否正确
        """
        stored_password = self.get_password()
        
        # 如果密码已加密，则对输入的密码进行加密后比较
        if self._is_password_encrypted():
            return self._encrypt_password(password_to_check) == stored_password
        else:
            # 兼容旧的明文密码（自动升级为加密格式）
            if password_to_check == stored_password:
                # 自动将明文密码升级为加密格式
                self.set_password(password_to_check)
                return True
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        homework_count = len(self.data["homeworks"])
        message_count = len(self.data["messages"])
        class_count = len(self.data["classes"])
        
        # 按学科统计作业数量
        subject_stats = {}
        for subject in self.data["subjects"]:
            count = len([h for h in self.data["homeworks"] if h["subject"] == subject])
            subject_stats[subject] = count
        
        return {
            "homework_count": homework_count,
            "message_count": message_count,
            "class_count": class_count,
            "subject_stats": subject_stats,
            "total_homeworks": sum(subject_stats.values())
        }
    
    def get_usb_drives(self) -> List[str]:
        """检测所有连接的U盘驱动器
        
        Returns:
            List[str]: U盘驱动器列表（如 ['D:', 'E:']）
        """
        if not CAN_DETECT_USB or platform.system() != 'Windows':
            print("U盘检测功能在当前环境下不可用")
            return []
        
        try:
            drives = []
            # 获取所有驱动器
            for drive in win32api.GetLogicalDriveStrings().split('\\\\')[:-1]:
                # 检查是否为可移动驱动器（U盘）
                try:
                    drive_type = win32file.GetDriveType(drive + '\\')
                    if drive_type == win32file.DRIVE_REMOVABLE:
                        drives.append(drive)
                except:
                    continue
            return drives
        except Exception as e:
            print(f"检测U盘时出错: {e}")
            return []
    
    def backup_from_usb(self) -> Dict[str, Any]:
        """从连接的U盘备份数据到程序的数据目录
        
        Returns:
            Dict[str, Any]: 备份结果信息
        """
        result = {
            "success": False,
            "message": "",
            "backed_up_files": [],
            "usb_drives": []
        }
        
        # 获取所有U盘
        usb_drives = self.get_usb_drives()
        result["usb_drives"] = usb_drives
        
        if not usb_drives:
            result["message"] = "未检测到连接的U盘"
            return result
        
        # 要查找的数据文件名
        data_file_names = ["data.json", "student_data.json", "teacher_data.json", "demo_data.json"]
        
        # 记录成功备份的文件
        backed_up_files = []
        
        # 遍历所有U盘
        for drive in usb_drives:
            try:
                # 遍历可能的数据文件名
                for file_name in data_file_names:
                    usb_file_path = os.path.join(drive, file_name)
                    
                    # 检查文件是否存在
                    if os.path.exists(usb_file_path):
                        # 目标文件路径
                        target_file_path = os.path.join(self.base_data_dir, file_name)
                        
                        try:
                            # 创建备份副本名（带时间戳）
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            backup_file_name = f"{os.path.splitext(file_name)[0]}_{timestamp}.json"
                            backup_file_path = os.path.join(self.base_data_dir, backup_file_name)
                            
                            # 复制文件到目标位置
                            shutil.copy2(usb_file_path, target_file_path)
                            # 同时创建带时间戳的备份
                            shutil.copy2(usb_file_path, backup_file_path)
                            
                            backed_up_files.append({
                                "file": file_name,
                                "from": usb_file_path,
                                "to": target_file_path,
                                "backup": backup_file_path
                            })
                            
                            print(f"成功从U盘 {drive} 备份文件: {file_name} 到 {target_file_path}")
                            print(f"创建备份副本: {backup_file_path}")
                            
                        except Exception as e:
                            print(f"备份文件 {usb_file_path} 时出错: {e}")
            except Exception as e:
                print(f"访问U盘 {drive} 时出错: {e}")
        
        if backed_up_files:
            result["success"] = True
            result["message"] = f"成功备份 {len(backed_up_files)} 个文件"
            result["backed_up_files"] = backed_up_files
        else:
            result["message"] = "在U盘中未找到可备份的数据文件"
        
        return result
    
    def check_and_backup_usb(self) -> Dict[str, Any]:
        """检查U盘并自动备份（可以在程序启动时调用）
        
        Returns:
            Dict[str, Any]: 备份结果信息
        """
        print("正在检查U盘数据备份...")
        return self.backup_from_usb()