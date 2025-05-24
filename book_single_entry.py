# book_single_entry.py
import os
import sqlite3
from tkinter import Toplevel, Label, Entry, Button, messagebox, W, END, filedialog

class BookEntryWindow:
    def __init__(self, parent):
        self.window = Toplevel(parent)
        self.window.title("单本书录入")
        self.window.geometry("500x600")
        self.window.grid_columnconfigure(1, weight=1)
        self.build_widgets()
    def open_book_entry(self):
        if self.book_entry_window is None or not self.book_entry_window.window.winfo_exists():
            self.book_entry_window = BookEntryWindow(self.root)
            self.book_entry_window.window.protocol("WM_DELETE_WINDOW", self.on_book_entry_close)
        else:
            self.book_entry_window.window.lift()  # 如果存在则提升到前端

    def on_book_entry_close(self):
        self.book_entry_window.window.destroy()
        self.book_entry_window = None
    def build_widgets(self):
        row = 0
        Label(self.window, text="书籍信息录入：", font=("等线", 25)).grid(row=row, column=0, sticky=W)
        row += 1
        Label(self.window, text="基本信息", font=("等线", 20)).grid(row=row, column=0, sticky=W)
        row += 1

        self.entry_title = self._entry(row, "书籍标题*"); row += 1
        self.entry_isbn = self._entry(row, "ISBN*"); row += 1
        self.entry_writer = self._entry(row, "书籍作者*"); row += 1
        self.entry_nation = self._entry(row, "作者国籍*"); row += 1
        Label(self.window, text="CIP数据", font=("等线", 20)).grid(row=row, column=0, sticky=W); row += 1
        self.entry_publisher = self._entry(row, "出版社*"); row += 1
        self.entry_pubtime = self._entry(row, "出版时间*"); row += 1
        self.entry_cn = self._entry(row, "中国图书馆分类法*"); row += 1
        self.entry_dv = self._entry(row, "杜威十进制分类法*"); row += 1
        Label(self.window, text="存放购买信息", font=("等线", 20)).grid(row=row, column=0, sticky=W); row += 1
        self.entry_location = self._entry(row, "存放位置"); row += 1
        self.entry_buytime = self._entry(row, "购买时间"); row += 1
        self.entry_buylocation = self._entry(row, "购买地点"); row += 1

        Label(self.window, text="电子书地址", font=("等线", 15)).grid(row=row, column=0, sticky=W)
        self.entry_ebook = Entry(self.window)
        self.entry_ebook.grid(row=row, column=1, sticky=W)
        row += 1
        Button(self.window, text="选择文件", command=self.select_file).grid(row=row, column=0, padx=5, pady=5, sticky="w")


        Button(self.window, text="保存", command=self.save_book).grid(row=row, column=1, sticky="ne", padx=5, pady=5)

    def _entry(self, row, label):
        Label(self.window, text=label, font=("等线", 15)).grid(row=row, column=0, sticky=W)
        entry = Entry(self.window)
        entry.grid(row=row, column=1, sticky=W)
        return entry

    def select_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.entry_ebook.delete(0, END)
            self.entry_ebook.insert(0, file_path)

    def save_book(self):
        fields = [
            self.entry_title.get(),
            self.entry_isbn.get(),
            self.entry_writer.get(),
            self.entry_nation.get(),
            self.entry_publisher.get(),
            self.entry_pubtime.get(),
            self.entry_cn.get(),
            self.entry_dv.get(),
            self.entry_location.get(),
            self.entry_buytime.get() or None,
            self.entry_buylocation.get() or None,
            self.entry_ebook.get() or None
        ]

        if fields[11] and not os.path.isfile(fields[11]):
            messagebox.showerror("错误", "电子书地址无效")
            return

        try:
            conn = sqlite3.connect("Thingsdatabase.db")
            cursor = conn.cursor()
            cursor.execute("""INSERT INTO book_storlist (
                Title, ISBN, Writer, Nation, Publisher, Publish_time,
                ReclassCN, ReclassDV, Location, Buy_time, Buy_location, Ebook_address
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", fields)
            conn.commit()
            messagebox.showinfo("成功", "书籍信息已保存")
        except Exception as e:
            if 'conn' in locals():
                conn.rollback()
            messagebox.showerror("数据库错误", str(e))
        finally:
            if 'conn' in locals():
                conn.close()

