import sqlite3
from tkinter import messagebox
from datetime import datetime
from utils.file_helper import FileHelper  # 我们稍后也会提供这个工具类代码

# 待办任务数据结构
class TodoTask:
    def __init__(self, title, content, deadline, level, isfinished=False, branch=None, file=None):
        self.title = title
        self.content = content
        self.deadline = deadline  # 应为字符串格式，如 "2025-05-28 18:00"
        self.level = level  # 0-3 整数
        self.isfinished = isfinished  # False/True
        self.branch = branch
        self.file = file

# 创建待办任务的逻辑封装类
class TodoCreator:
    def __init__(self, db_path="Thingsdatabase.db"):
        self.db_path = db_path

    def save_task(self, task: TodoTask):
        # 仅校验时间格式，不限制是否早于当前时间
        try:
            datetime.strptime(task.deadline, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("时间格式错误", "截止时间格式应为：YYYY-MM-DD，例如：2025-05-28")
            return False

        # 校验文件路径
        if task.file:
            try:
                task.file = FileHelper.validate_path(task.file)
            except FileNotFoundError as e:
                messagebox.showerror("文件错误", str(e))
                return False

        # 存入数据库
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO Thingstable(title, deadline, text, level, isfinished, branch, file)
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (task.title, task.deadline, task.content, task.level,
                 int(task.isfinished), task.branch, task.file))
            conn.commit()
            messagebox.showinfo("成功", "成功保存到数据库！")
            return True
        except sqlite3.Error as e:
            messagebox.showerror("数据库错误", f"保存失败:\n{str(e)}")
            return False
        finally:
            conn.close()
