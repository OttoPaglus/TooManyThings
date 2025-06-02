import tkinter as tk
from tkinter import messagebox
import sqlite3
from datetime import datetime


class DateInputDialog:
    def __init__(self, prompt="请输入日期（YYYY-MM-DD）：", title="输入截止日期"):
        self.result = None
        self.root = tk.Tk()
        self.root.title(title)
        self.root.geometry("300x150")
        self.root.resizable(False, False)

        tk.Label(self.root, text=prompt, font=("Arial", 12)).pack(pady=10)
        self.entry = tk.Entry(self.root, width=30)
        self.entry.pack(pady=5)
        self.entry.focus_set()
        self.entry.bind("<Return>", self.submit)

        tk.Button(self.root, text="提交", command=self.submit).pack(pady=10)
        self.root.mainloop()

    def submit(self, event=None):
        self.result = self.entry.get().strip()
        self.root.destroy()

    def get_result(self):
        return self.result


class TodoInserter:
    def __init__(self, db_path="Thingsdatabase.db"):
        self.db_path = db_path

    def insert_todo(self, title, filepath):
        conn = sqlite3.connect(self.db_path)
        try:
            # 获取用户输入的截止日期
            dialog = DateInputDialog("请输入待办截止日期（YYYY-MM-DD）：", "设置阅读计划")
            deadline = dialog.get_result()

            if not deadline:
                messagebox.showwarning("取消操作", "未输入截止日期，跳过待办事项创建。")
                return

            try:
                datetime.strptime(deadline, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("格式错误", "日期格式不正确，应为 YYYY-MM-DD。")
                return

            # 插入待办事项
            todotitle = f"{title} 阅读计划"
            todotext = f"完成《{title}》的阅读"
            cursor = conn.cursor()
            cursor.execute("""INSERT INTO Thingstable( 
                title, text, level, deadline, isfinished, branch, file
            ) VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (todotitle, todotext, 1, deadline, 0, "reading", filepath))
            conn.commit()
            messagebox.showinfo("导入成功", f"书籍《{title}》的阅读计划已加入待办事项。")
        except Exception as e:
            conn.rollback()
            messagebox.showerror("数据库错误", str(e))
        finally:
            conn.close()