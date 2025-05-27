import sqlite3
from tkinter import messagebox

class TodoSearcher:
    def __init__(self, db_path="Thingsdatabase.db"):
        self.db_path = db_path

    def search_by_branch(self, branch_keyword):
        """返回匹配关键词的任务元组列表：(id, title, deadline)"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, title, deadline FROM Thingstable WHERE branch LIKE ?",
                ('%' + branch_keyword + '%',)
            )
            results = cursor.fetchall()
            return results
        except sqlite3.Error as e:
            messagebox.showerror("错误", f"数据库错误:\n{str(e)}")
            return []
        finally:
            conn.close()
