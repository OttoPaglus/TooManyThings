import sqlite3
from tkinter import Toplevel, Label, Entry, Button, messagebox, END, W, E
from tkinter.ttk import Treeview

class BookEditWindow:
    def __init__(self, parent, on_close_callback=None):
        self.on_close_callback = on_close_callback
        self.window = Toplevel(parent)
        self.window.title("书籍查看、搜索与编辑")
        self.window.geometry("900x650")
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
        self.build_widgets()
        self.load_books()

    def on_close(self):
        if self.on_close_callback:
            self.on_close_callback()
        self.window.destroy()

    def build_widgets(self):
        # 搜索栏
        Label(self.window, text="搜索（书名/作者/出版社）:").grid(row=0, column=0, padx=10, pady=5, sticky=W)
        self.search_entry = Entry(self.window, width=40)
        self.search_entry.grid(row=0, column=1, sticky=W)
        Button(self.window, text="搜索", command=self.search_books).grid(row=0, column=2, sticky=W)
        Button(self.window, text="重置", command=self.load_books).grid(row=0, column=3, padx=5, sticky=W)

        # TreeView 展示书籍列表
        self.tree = Treeview(self.window, columns=("title", "author", "publisher"), show="headings", height=15)
        self.tree.heading("title", text="书名")
        self.tree.heading("author", text="作者")
        self.tree.heading("publisher", text="出版社")
        self.tree.column("title", width=300)
        self.tree.column("author", width=150)
        self.tree.column("publisher", width=150)
        self.tree.grid(row=1, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        # 详细信息输入框标签和输入框，12个字段
        labels = ["书名", "ISBN", "作者", "国别", "出版社", "出版时间",
                  "ReclassCN", "ReclassDV", "馆藏地", "购买时间", "购买地点", "电子书地址","创建时间"]
        self.entries = {}

        for i, label_text in enumerate(labels, start=2):
            Label(self.window, text=label_text + ":").grid(row=i, column=0, sticky=W, padx=10, pady=2)
            entry = Entry(self.window, width=60)
            entry.grid(row=i, column=1, sticky=W, pady=2)
            self.entries[label_text] = entry

        # 按钮
        Button(self.window, text="保存修改", command=self.update_book).grid(row=15, column=1, sticky=E, pady=10, padx=10)
        Button(self.window, text="删除书籍", command=self.delete_book).grid(row=15, column=0, sticky=W, pady=10, padx=10)

        # 网格扩展
        self.window.grid_rowconfigure(1, weight=1)
        self.window.grid_columnconfigure(1, weight=1)

    def load_books(self):
        self.tree.delete(*self.tree.get_children())
        try:
            conn = sqlite3.connect("Thingsdatabase.db")
            cursor = conn.cursor()
            cursor.execute("SELECT rowid, Title, Writer, Publisher FROM book_storlist")
            for row in cursor.fetchall():
                self.tree.insert("", "end", values=(row[1], row[2], row[3]), tags=(row[0],))
        except Exception as e:
            messagebox.showerror("加载失败", str(e))
        finally:
            if conn:
                conn.close()

    def search_books(self):
        keyword = self.search_entry.get().strip()
        if not keyword:
            messagebox.showinfo("提示", "请输入搜索关键词")
            return

        self.tree.delete(*self.tree.get_children())
        try:
            conn = sqlite3.connect("Thingsdatabase.db")
            cursor = conn.cursor()
            cursor.execute("""
                SELECT rowid, Title, Writer, Publisher
                FROM book_storlist
                WHERE Title LIKE ? OR Writer LIKE ? OR Publisher LIKE ?
            """, (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"))
            rows = cursor.fetchall()
            for row in rows:
                self.tree.insert("", "end", values=(row[1], row[2], row[3]), tags=(row[0],))
        except Exception as e:
            messagebox.showerror("搜索失败", str(e))
        finally:
            if conn:
                conn.close()

    def on_select(self, event):
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            self.selected_id = item["tags"][0]

            try:
                conn = sqlite3.connect("Thingsdatabase.db")
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT Title, ISBN, Writer, Nation, Publisher, Publish_time,
                           ReclassCN, ReclassDV, Location, Buy_time, Buy_location, Ebook_address,createtime
                    FROM book_storlist WHERE rowid=?
                """, (self.selected_id,))
                row = cursor.fetchone()
                if row:
                    keys = ["书名", "ISBN", "作者", "国别", "出版社", "出版时间",
                            "ReclassCN", "ReclassDV", "馆藏地", "购买时间", "购买地点", "电子书地址","创建时间"]
                    for key, value in zip(keys, row):
                        entry = self.entries.get(key)
                        if entry:
                            entry.delete(0, END)
                            entry.insert(0, value if value is not None else "")
            except Exception as e:
                messagebox.showerror("读取失败", str(e))
            finally:
                if conn:
                    conn.close()

    def update_book(self):
        if not hasattr(self, 'selected_id'):
            messagebox.showwarning("未选中", "请先选中要修改的书籍")
            return
        try:
            conn = sqlite3.connect("Thingsdatabase.db")
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE book_storlist SET 
                    Title=?, ISBN=?, Writer=?, Nation=?, Publisher=?, Publish_time=?,
                    ReclassCN=?, ReclassDV=?, Location=?, Buy_time=?, Buy_location=?, Ebook_address=?
                WHERE rowid=?
            """, (
                self.entries["书名"].get(),
                self.entries["ISBN"].get(),
                self.entries["作者"].get(),
                self.entries["国别"].get(),
                self.entries["出版社"].get(),
                self.entries["出版时间"].get(),
                self.entries["ReclassCN"].get(),
                self.entries["ReclassDV"].get(),
                self.entries["馆藏地"].get(),
                self.entries["购买时间"].get(),
                self.entries["购买地点"].get(),
                self.entries["电子书地址"].get(),
                self.selected_id
            ))
            conn.commit()
            messagebox.showinfo("修改成功", "书籍信息已更新")
            self.load_books()
        except Exception as e:
            conn.rollback()
            messagebox.showerror("数据库错误", str(e))
        finally:
            if conn:
                conn.close()

    def delete_book(self):
        if not hasattr(self, 'selected_id'):
            messagebox.showwarning("未选中", "请先选中要删除的书籍")
            return
        if not messagebox.askyesno("确认删除", "确定要删除该书籍记录吗？"):
            return
        try:
            conn = sqlite3.connect("Thingsdatabase.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM book_storlist WHERE rowid=?", (self.selected_id,))
            conn.commit()
            messagebox.showinfo("删除成功", "书籍记录已删除")
            for entry in self.entries.values():
                entry.delete(0, END)
            self.load_books()
        except Exception as e:
            conn.rollback()
            messagebox.showerror("删除失败", str(e))
        finally:
            if conn:
                conn.close()
