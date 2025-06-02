import sqlite3
import openpyxl
from tkinter import Toplevel, Label, Button, filedialog, messagebox, W
import os
import subprocess
import sys
from book2todo import TodoInserter

class BookImportWindow(Toplevel):
    def __init__(self, parent, on_close_callback=None):
        super().__init__(parent)
        self.title("批量导入书籍")
        self.geometry("500x200")
        self.on_close_callback = on_close_callback
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # 添加 createtime 字段与触发器
        self.ensure_createtime_column()
        self.create_book_insert_trigger()
        self.example_file_path = os.path.abspath("examples\ex.xlsx")  # 示例路径，可修改
        self.build_widgets()

    def on_close(self):
        if self.on_close_callback:
            self.on_close_callback()
        self.destroy()

    def build_widgets(self):
        Label(self, text="批量导入书籍信息（Excel）", font=("等线", 20)).grid(row=0, column=0, columnspan=2, pady=10, sticky=W)
        Label(self, text="请上传包含书籍信息的.xlsx文件\n格式需与数据库字段一致。", font=("等线", 12)).grid(row=1, column=0, columnspan=2, sticky=W, padx=10)
        Button(self, text="选择文件并导入", command=self.import_excel).grid(row=2, column=0, padx=10, pady=20, sticky=W)
        Button(self, text="打开样例文件所在文件夹", command=self.open_example_folder).grid(row=2, column=1, padx=10,pady=10, sticky=W)
    def ensure_createtime_column(self):
        conn = sqlite3.connect("Thingsdatabase.db")
        cursor = conn.cursor()
        try:
            cursor.execute("PRAGMA table_info(book_storlist)")
            columns = [col[1] for col in cursor.fetchall()]
            if "createtime" not in columns:
                cursor.execute("ALTER TABLE book_storlist ADD COLUMN createtime TEXT")
                conn.commit()
        except Exception as e:
            print("添加 createtime 字段失败:", e)
        finally:
            conn.close()
    def open_example_folder(self):
        folder_path = os.path.dirname(self.example_file_path)
        try:
            if sys.platform == "win32":
                os.startfile(folder_path)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", folder_path])
            else:
                subprocess.Popen(["xdg-open", folder_path])
        except Exception as e:
            messagebox.showerror("打开失败", f"无法打开文件夹：{str(e)}")
    def create_book_insert_trigger(self):
        conn = sqlite3.connect("Thingsdatabase.db")
        cursor = conn.cursor()
        try:
            cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS trg_book_insert
            AFTER INSERT ON book_storlist
            BEGIN
                UPDATE book_storlist
                SET createtime = DATETIME('now','+8 hours')
                WHERE rowid = NEW.rowid;
            END;
            """)
            conn.commit()
        except sqlite3.Error as e:
            print("创建触发器失败:", e)
        finally:
            conn.close()

    def import_excel(self):
        file_path = filedialog.askopenfilename(filetypes=[("Excel文件", "*.xlsx")])
        if not file_path:
            return

        try:
            workbook = openpyxl.load_workbook(file_path)
            sheet = workbook.active

            conn = sqlite3.connect("Thingsdatabase.db")
            cursor = conn.cursor()

            inserted_count = 0
            for row in sheet.iter_rows(min_row=2, values_only=True):
                if not any(row):
                    continue
                cursor.execute("""INSERT INTO book_storlist (
                    Title, ISBN, Writer, Nation, Publisher, Publish_time,
                    ReclassCN, ReclassDV, Location, Buy_time, Buy_location, Ebook_address
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", row)
                inserted_count += 1
            todo = TodoInserter()
            todo.insert_todo(row[0],row[11])
            conn.commit()
            messagebox.showinfo("导入成功", f"成功导入 {inserted_count} 本书。")
        except Exception as e:
            if 'conn' in locals():
                conn.rollback()
            messagebox.showerror("导入失败", f"出错信息：{str(e)}")
        finally:
            if 'workbook' in locals():
                workbook.close()
            if 'conn' in locals():
                conn.close()
