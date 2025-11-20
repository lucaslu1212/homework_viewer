"""
数据存储模块
负责管理作业、留言等数据的存储和管理
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any

class DataManager:
    def __init__(self, data_file="data.json"):
        self.data_file = data_file
        self.data = self._load_data()
    
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
            "class_assignments": {}  # 班级对应关系
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
        self.data = self._get_default_data()
        self.save_data()
    
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