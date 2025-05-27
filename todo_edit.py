import sqlite3
from tkinter import messagebox
from datetime import datetime
from todo_create import TodoTask
from file_helper import FileHelper

class TodoEditor:
    def __init__(self, db_path="Thingsdatabase.db"):
        self.db_path = db_path

    def load_task(self, task_id):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Thingstable WHERE id=?", (task_id,))
            row = cursor.fetchone()
            if row:
                return TodoTask(
                    title=row[1],
                    content=row[2],
                    deadline=row[4],
                    level=row[5],
                    isfinished=bool(row[3]),
                    branch=row[6],
                    file=row[7]
                ), row[0]
            return None, None
        except sqlite3.Error as e:
            messagebox.showerror("加载失败", f"数据库错误:\n{str(e)}")
            return None, None
        finally:
            conn.close()

    def update_task(self, task: TodoTask, task_id: int):
        try:
            datetime.strptime(task.deadline, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("时间格式错误", "截止时间格式应为：YYYY-MM-DD，例如：2025-05-28")
            return False

        if task.file:
            try:
                task.file = FileHelper.validate_path(task.file)
            except FileNotFoundError as e:
                messagebox.showerror("文件错误", str(e))
                return False

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE Thingstable
                SET title=?, text=?, deadline=?, level=?, isfinished=?, branch=?, file=?
                WHERE id=?
            """, (
                task.title, task.content, task.deadline, task.level,
                int(task.isfinished), task.branch, task.file, task_id
            ))
            conn.commit()
            messagebox.showinfo("成功", "任务更新成功！")
            return True
        except sqlite3.Error as e:
            messagebox.showerror("数据库错误", f"更新失败:\n{str(e)}")
            return False
        finally:
            conn.close()

    def delete_task(self, task_id):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Thingstable WHERE id=?", (task_id,))
            conn.commit()
            messagebox.showinfo("成功", "任务已删除")
            return True
        except sqlite3.Error as e:
            messagebox.showerror("删除失败", f"数据库错误:\n{str(e)}")
            return False
        finally:
            conn.close()
