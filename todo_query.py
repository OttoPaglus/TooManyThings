import sqlite3
import datetime
from tkinter import messagebox

class TodoQuery:
    def __init__(self, db_path="Thingsdatabase.db"):
        self.db_path = db_path

    def fetch_tasks_by_category(self, category, level_map):
        """
        根据选中的分类查询任务数据
        :param category: 字符串（如 “全部待办事项”）
        :param level_map: 等级文本到数字的映射字典
        :return: [(id, title, deadline), ...]
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            if category == '今日待办事项':
                today = datetime.date.today().strftime("%Y-%m-%d")
                cursor.execute("SELECT id, title, deadline FROM Thingstable WHERE deadline=? AND isfinished=0", (today,))
            elif category == '全部待办事项':
                cursor.execute("SELECT id, title, deadline FROM Thingstable WHERE isfinished=0")
            elif category == '已经完成事项':
                cursor.execute("SELECT id, title, deadline FROM Thingstable WHERE isfinished=1")
            elif category in level_map:
                level = level_map[category]
                cursor.execute("SELECT id, title, deadline FROM Thingstable WHERE level=? AND isfinished=0", (level,))
            else:
                return []
            return cursor.fetchall()
        except sqlite3.Error as e:
            messagebox.showerror("错误", f"数据库操作出错:\n{str(e)}")
            return []
        finally:
            conn.close()
