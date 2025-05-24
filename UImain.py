import sys
from tkinter import *
from tkinter.ttk import *
from tkinter import scrolledtext
from tkinter import filedialog
import time
import datetime
import sqlite3
from tkinter import messagebox
import os
import subprocess
import openpyxl
from book_single_entry import BookEntryWindow
from book_excel_import import BookImportWindow
from book_epub_reader import BookEpubReader
from book_editor import BookEditWindow



'''全局变量设置'''
versions="2.3"
version_date="2025年5月"
things_level_dic={0:'重要并且紧急',1:'不重要但紧急',2:'重要但不紧急',3:'不重要不紧急'}
things_level_dic_op={'重要并且紧急':0,'不重要但紧急':1,'重要但不紧急':2,'不重要不紧急':3}

def import_books_from_excel():
    file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
    if not file_path:
        return

    try:
        workbook = openpyxl.load_workbook(file_path)
        sheet = workbook.active

        conn = sqlite3.connect("Thingsdatabase.db")
        cursor = conn.cursor()

        inserted_count = 0
        for row in sheet.iter_rows(min_row=2, values_only=True):  # 跳过标题行
            if not any(row):
                continue  # 跳过空行

            cursor.execute("""INSERT INTO book_storlist (
                Title, ISBN, Writer, Nation, Publisher, Publish_time,
                ReclassCN, ReclassDV, Location, Buy_time, Buy_location, Ebook_address
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", row)
            inserted_count += 1

        conn.commit()
        messagebox.showinfo("导入成功", f"共导入 {inserted_count} 本书籍记录。")
    except Exception as e:
        messagebox.showerror("导入失败", f"发生错误：{str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()

def load_data_to_edit(task_id):
    """将数据加载到编辑表单"""
    conn = sqlite3.connect("Thingsdatabase.db")
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM Thingstable WHERE id=?", (task_id,))
        task_data = cursor.fetchone()

        if task_data:
            # 切换到编辑选项卡
            note.select(data_edit)

            # 清除旧数据
            title_edit.delete(0, END)
            content_edit.delete('1.0', END)
            date_edit.delete(0, END)
            branch_edit.delete(0, END)
            #path.set("")

            time.sleep(0.1)
            # 填充数据
            title_edit.insert(0, task_data[1])  # title字段
            content_edit.insert(END, task_data[2])  # text字段
            date_edit.insert(0, task_data[4])  # deadline字段
            branch_edit.insert(END, task_data[6] if task_data[6] else "")

            # 设置优先级
            level_str = things_level_dic.get(task_data[5], '重要并且紧急')
            level_edit.set(level_str)

            # 设置完成状态
            finish_edit.set('未完成')

            # 保存当前编辑的ID到全局变量
            global current_edit_id
            current_edit_id = task_id

    except sqlite3.Error as e:
        messagebox.showerror("错误", f"加载数据失败:\n{str(e)}")
    finally:
        # 设置文件路径输入框
        file_entry_edit.delete(0, END)
        file_entry_edit.insert(0, task_data[7] if task_data[7] else "")
        cursor.close()
        conn.close()
def file_update(entry_widget):
    file_path = filedialog.askopenfilename()
    if file_path:
        entry_widget.delete(0, END)
        entry_widget.insert(0, file_path)
def file_save(file_path):
    if not os.path.isfile(file_path):
        raise FileNotFoundError("文件路径无效，请重新选择有效的文件。")
    return file_path
def save_book(book_title_entry, book_isbn_entry, book_writer_entry, book_writernation_entry, book_publish_entry,book_publishtime_entry,book_reclassDV_entry,book_reclassCN_entry,book_location_entry,book_buytime_entry,book_buylocation_entry,ebook_location_entry):
    book_title = book_title_entry.get()
    book_isbn = book_isbn_entry.get()
    book_writer = book_writer_entry.get()
    book_writernation =  book_writernation_entry.get()
    book_publish = book_publish_entry.get()
    book_publishtime = book_publishtime_entry.get()
    book_reclassDV = book_reclassDV_entry.get()
    book_reclassCN = book_reclassCN_entry.get()
    book_location = book_location_entry.get()
    book_buytime = book_buytime_entry.get() or None
    book_buylocation = book_buylocation_entry.get() or None
    ebook_location = ebook_location_entry.get() or None

    location = None
    if ebook_location:
        try:
            location = file_save(ebook_location)
        except FileNotFoundError as fe:
            messagebox.showerror("文件错误", str(fe))
            return

    # 清空输入框
    book_title_entry.delete(0, 'end')
    book_isbn_entry.delete(0, 'end')
    book_writer_entry.delete(0, 'end')
    book_writernation_entry.delete(0, 'end')
    book_publish_entry.delete(0, 'end')
    book_publishtime_entry.delete(0, 'end')
    book_reclassDV_entry.delete(0, 'end')
    book_reclassCN_entry.delete(0, 'end')
    book_location_entry.delete(0, 'end')
    book_buytime_entry.delete(0, 'end')
    book_buylocation_entry.delete(0, 'end')

    try:
        conn = sqlite3.connect("Thingsdatabase.db")
        cursor = conn.cursor()
        cursor.execute("""INSERT INTO book_storlist(Title,ISBN,Writer,Nation,Publisher,Publish_time,ReclassCN,ReclassDV,Location,Buy_time,Buy_location,Ebook_address)
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                       (book_title,book_isbn,book_writer,book_writernation,book_publish,book_publishtime,book_reclassCN,book_reclassDV,book_location,book_buytime,book_buylocation,location))
        conn.commit()
        messagebox.showinfo("成功", "成功保存到数据库！")
        update_treeview(None)
    except sqlite3.Error as e:
        messagebox.showerror("数据库错误", f"保存失败:\n{str(e)}")
    finally:
        file_entry_add.delete(0, END)  # 在 save() 成功后清空
        if conn:
            conn.close()
def save():
    title = title_entry.get()
    content = content_entry.get("1.0", "end-1c")
    date = date_entry.get()
    level = things_level_dic_op[level_entry.get()]
    branch = branch_entry.get() or None  # 允许为空
    file_path = file_entry_add.get() or None  # 允许为空

    location = None
    if file_path:
        try:
            location = file_save(file_path)
        except FileNotFoundError as fe:
            messagebox.showerror("文件错误", str(fe))
            return

    # 清空输入框
    title_entry.delete(0, 'end')
    content_entry.delete('1.0', 'end')
    date_entry.delete(0, 'end')
    branch_entry.delete(0, 'end')
    level_entry.set('')

    try:
        conn = sqlite3.connect("Thingsdatabase.db")
        cursor = conn.cursor()
        cursor.execute("""INSERT INTO Thingstable(title, deadline, text, level, isfinished, branch, file)
                          VALUES (?, ?, ?, ?, ?, ?, ?)""",
                       (title, date, content, level, False, branch, location))
        conn.commit()
        messagebox.showinfo("成功", "成功保存到数据库！")
        update_treeview(None)
    except sqlite3.Error as e:
        messagebox.showerror("数据库错误", f"保存失败:\n{str(e)}")
    finally:
        file_entry_add.delete(0, END)  # 在 save() 成功后清空
        if conn:
            conn.close()
def update_task():
    title = title_edit.get()
    content = content_edit.get("1.0", "end-1c")
    deadline = date_edit.get()
    level = things_level_dic_op[level_edit.get()]
    isfinish = 1 if finish_edit.get() == '已完成' else 0
    branch = branch_edit.get() or None
    file_path = file_entry_edit.get() or None

    location = None
    if file_path:
        try:
            location = file_save(file_path)
        except FileNotFoundError as fe:
            messagebox.showerror("文件错误", str(fe))
            return

    try:
        conn = sqlite3.connect("Thingsdatabase.db")
        cursor = conn.cursor()
        cursor.execute("""UPDATE Thingstable 
                          SET title=?, text=?, deadline=?, level=?, isfinished=?, branch=?, file=? 
                          WHERE id=?""",
                       (title, content, deadline, level, isfinish, branch, location, current_edit_id))
        conn.commit()

        update_treeview(None)
        note.select(data_add)

        title_edit.delete(0, END)
        content_edit.delete('1.0', END)
        date_edit.delete(0, END)
        level_edit.set('')
        branch_edit.delete(0, END)
        finish_edit.set('')

        messagebox.showinfo("成功", "任务更新成功！")
    except sqlite3.Error as e:
        messagebox.showerror("数据库错误", f"更新失败:\n{str(e)}")
    finally:
        file_entry_edit.delete(0, END)  # 在 update_task() 成功后清空
        if conn:
            conn.close()
def on_treeview_double_click(event):
    """处理Treeview双击事件"""
    selected_item = txtree.selection()
    if selected_item:
        item = selected_item[0]
        task_id = txtree.item(item, "tags")[0]
        load_data_to_edit(task_id)
def delete_task():
    """删除当前编辑的任务"""
    global current_edit_id

    if not current_edit_id:
        messagebox.showwarning("警告", "请先选择要删除的任务")
        return

    # 确认对话框
    if not messagebox.askyesno("确认删除", "确定要删除这个任务吗？"):
        return

    try:
        conn = sqlite3.connect("Thingsdatabase.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Thingstable WHERE id=?", (current_edit_id,))
        conn.commit()

        # 更新显示
        update_treeview(None)

        # 清除编辑数据
        title_edit.delete(0, END)
        content_edit.delete('1.0', END)
        date_edit.delete(0, END)
        level_edit.set('')
        finish_edit.set('')

        # 切换回添加选项卡
        note.select(data_add)

        messagebox.showinfo("成功", "任务已删除")
        update_treeview(None)
    except sqlite3.Error as e:
        conn.rollback()
        messagebox.showerror("错误", f"删除失败: {str(e)}")
    finally:
        if conn:
            conn.close()
        current_edit_id = None
def open_file(entry_widget):
    file_path = entry_widget.get()
    if not os.path.isfile(file_path):
        messagebox.showerror("错误", "文件路径无效或文件不存在，请检查路径")
        return
    try:
        if os.name == 'nt':  # Windows
            os.startfile(file_path)
        elif os.name == 'posix':  # macOS/Linux
            opener = 'open' if sys.platform == 'darwin' else 'xdg-open'
            subprocess.run([opener, file_path])
        else:
            messagebox.showwarning("不支持", "当前系统暂不支持打开文件操作")
    except Exception as e:
        messagebox.showerror("打开失败", f"无法打开文件:\n{str(e)}")
def update_treeview(event):
    # 清空当前表格数据
    for item in txtree.get_children():
        txtree.delete(item)

    # 获取当前选中的分类
    selected_category = combo.get()

    # 连接数据库
    conn = sqlite3.connect("Thingsdatabase.db")
    cursor = conn.cursor()

    try:
        # 修改所有查询语句，包含id字段
        if selected_category == '今日待办事项':
            today = datetime.date.today().strftime("%Y-%m-%d")
            cursor.execute("SELECT id, title, deadline FROM Thingstable WHERE deadline=? AND isfinished=0", (today,))
        elif selected_category == '全部待办事项':
            cursor.execute("SELECT id, title, deadline FROM Thingstable WHERE isfinished=0")
        elif selected_category == '已经完成事项':
            cursor.execute("SELECT id, title, deadline FROM Thingstable WHERE isfinished=1")
        else:
            level = things_level_dic_op[selected_category]
            cursor.execute("SELECT id, title, deadline FROM Thingstable WHERE level=? AND isfinished=0", (level,))

        # 插入数据时保存id到tags
        for row in cursor.fetchall():
            txtree.insert('', 'end',
                          values=(row[1], row[2]),  # 显示标题和截止日期
                          tags=(row[0],))  # 存储ID到tags属性

    except Exception as e:
        messagebox.showerror("错误", f"数据库操作出错:\n{str(e)}")
    finally:
        cursor.close()
        conn.close()
def about():
        txt=f"本程序为待办事项管理系统，\n请在添加待办选项卡中添加待办事项，\n双击待办事项可进行修改和删除操作。\n作者：OttoPaglus\n版本：{versions} \n日期：{version_date}"
        messagebox.showinfo("启动说明",txt)
def search_branch():
    conn = sqlite3.connect("Thingsdatabase.db")
    cursor = conn.cursor()
    branch = branch_search.get()
    for item in txtree.get_children():
        txtree.delete(item)
    try:
        cursor.execute("SELECT id, title, deadline FROM Thingstable WHERE branch LIKE ?", ('%' + branch + '%',))
        for row in cursor.fetchall():
            txtree.insert('', 'end',
                          values=(row[1], row[2]),  # 显示标题和截止日期
                          tags=(row[0],))  # 存储ID到tags属性
    except sqlite3.Error as e:
        messagebox.showerror("错误", f"加载数据失败:\n{str(e)}")
    finally:
        combo.current(7)
        cursor.close()
        conn.close()
def bookwinopen():
    BookEntryWindow(window)
def booklistopen():
    BookImportWindow(window)
def timewinopen():
    timewindow=Tk()
    timewindow.title("时间表子模块")
    book_screen_width = timewindow.winfo_screenwidth()
    book_screen_height = timewindow.winfo_screenheight()
    x = (book_screen_width // 2) - (700 // 2)
    y = (book_screen_height // 2) - (600// 2)
    timewindow.geometry(f"{500}x{300}+{x}+{y}")
    timewindow.grid_columnconfigure(1, weight=1)  # 允许列自动扩展
    timewindow.grid_rowconfigure(3, weight=1)     # 允许行自动扩展


'''主窗口设置'''

window = Tk()
window.title("TooManyThings")
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()
x = (screen_width // 2) - (700 // 2)
y = (screen_height // 2) - (600// 2)
window.geometry(f"{700}x{600}+{x}+{y}")
window.grid_columnconfigure(1, weight=1)  # 允许列自动扩展
window.grid_rowconfigure(3, weight=1)     # 允许行自动扩展


#不同分类设置
combo = Combobox(window)
combo['values'] = ('今日待办事项','全部待办事项','重要并且紧急','不重要但紧急','重要但不紧急','不重要不紧急','已经完成事项','查找结果展示')
combo['state'] = 'readonly'
combo.current(0)
combo.grid(column=0, row=0, rowspan=2, sticky="w")
combo.bind("<<ComboboxSelected>>", update_treeview)

#提醒语句设置
t = time.localtime()
m = f"今天是{t.tm_year}年{t.tm_mon}月{t.tm_mday}日，待办事项如下:"
lbl = Label(window, text=m, font=("等线", 15), relief="groove")
lbl.grid(column=1, row=0, rowspan=2, sticky="ew")

#显示待办设置
txtree=Treeview(window,columns=('标题','截止日期'),show="headings")
txtree.heading('标题',text='标题')
txtree.heading('截止日期',text='截止日期')
txtree.column('标题',width=10,anchor='center')
txtree.column('截止日期',width=10,anchor='center')
txtree.grid(column=0, row=2, columnspan=2, sticky="nsew")
txtree.bind("<Double-1>", on_treeview_double_click)
update_treeview(None)

#选项卡设置
note = Notebook(window)
note.grid(column=0, row=3, columnspan=2, sticky="nsew")
# 添加选项卡的 Frame
data_add = Frame(note)
data_edit = Frame(note)
data_search = Frame(note)
book_list = Frame(note)
more_about= Frame(note)

'''data_add模块设置'''

# 标题输入（占据3列）
Label(data_add, text='  标题:', font=("等线", 15)).grid(row=0, column=0, padx=5, pady=5, sticky="w")
title_entry = Entry(data_add)
title_entry.grid(row=0, column=1, columnspan=3, sticky="ew", padx=5, pady=5)  # 跨3列
# 内容输入（占据3列）
Label(data_add, text='  内容:', font=("等线", 15)).grid(row=1, column=0, padx=5, pady=5, sticky="nw")
content_entry = scrolledtext.ScrolledText(data_add, height=4)
content_entry.grid(row=1, column=1, columnspan=3, sticky="nsew", padx=5, pady=5)  # 跨3列

# 截止日期输入
Label(data_add,text='截止日期:',font=("等线",15)).grid(row=2, column=0, padx=5, pady=5, sticky="nw")
date_entry = Entry(data_add)
date_entry.grid(row=2,column=1, sticky="nsew", padx=5, pady=5)

#待办等级选择
Label(data_add,text='   待办等级:',font=("等线",15)).grid(row=2, column=2, padx=5, pady=5, sticky="nw")
level_entry = Combobox(data_add)
level_entry['values']=('重要并且紧急','不重要但紧急','重要但不紧急','不重要不紧急')
level_entry['state'] = 'readonly'
level_entry.current(0)
level_entry.grid(row=2, column=3, sticky="nw", padx=5, pady=5)

#分支从属设置
Label(data_add,text="分支从属:",font=('等线',15)).grid(row=3, column=0, padx=5, pady=5, sticky="nw")
branch_entry = Entry(data_add)
branch_entry.grid(row=3, column=1, sticky="nsew",padx=5, pady=5)

#附件上传设置
Label(data_add,text="上传文件路径:",font=('等线',15)).grid(row=4, column=0, padx=5, pady=5, sticky="nw")
file_entry_add = Entry(data_add)
file_entry_add.grid(row=4, column=1, padx=5, pady=5, sticky="nw")
Button(data_add, text="选择文件", command=lambda: file_update(file_entry_add)).grid(row=4, column=2, padx=5, pady=5, sticky="nw")

#保存按钮设置
button_save_add=Button(data_add,text='保存',command=save)
button_save_add.grid(row=5, column=2, sticky="ne",padx=5, pady=5)

'''data_edit模块设置'''

# 标题输入（占据3列）
Label(data_edit, text='  标题:', font=("等线", 15)).grid(row=0, column=0, padx=5, pady=5, sticky="w")
title_edit = Entry(data_edit)
title_edit.grid(row=0, column=1, columnspan=3, sticky="ew", padx=5, pady=5)  # 跨3列


# 内容输入（占据3列）
Label(data_edit, text='  内容:', font=("等线", 15)).grid(row=1, column=0, padx=5, pady=5, sticky="nw")
content_edit = scrolledtext.ScrolledText(data_edit, height=4)
content_edit.grid(row=1, column=1, columnspan=3, sticky="nsew", padx=5, pady=5)  # 跨3列

# 截止日期输入
Label(data_edit,text='截止日期:',font=("等线",15)).grid(row=2, column=0, padx=5, pady=5, sticky="nw")
date_edit = Entry(data_edit)
date_edit.grid(row=2,column=1, sticky="nsew", padx=5, pady=5)

#待办等级选择
Label(data_edit,text='   待办等级:',font=("等线",15)).grid(row=2, column=2, padx=5, pady=5, sticky="nw")
level_edit = Combobox(data_edit)
level_edit['values']=('重要并且紧急','不重要但紧急','重要但不紧急','不重要不紧急')
level_edit['state'] = 'readonly'
level_edit.current(0)
level_edit.grid(row=2, column=3, sticky="nw", padx=5, pady=5)

#分支从属设置
Label(data_edit,text="分支从属:",font=('等线',15)).grid(row=3, column=0, padx=5, pady=5, sticky="nw")
branch_edit = Entry(data_edit)
branch_edit.grid(row=3, column=1, padx=5, pady=5,sticky="nsew")

#完成情况输入
Label(data_edit,text='   完成情况:',font=('等线',15)).grid(row=3, column=2, padx=5, pady=5, sticky="nw")
finish_edit = Combobox(data_edit)
finish_edit['values']=('已完成','未完成')
finish_edit['state'] = 'readonly'
finish_edit.current(0)
finish_edit.grid(row=3, column=3, padx=5, pady=5, sticky="w")

#附件上传设置
Label(data_edit,text="上传文件路径:",font=('等线',15)).grid(row=4, column=0, padx=5, pady=5, sticky="nw")
file_entry_edit = Entry(data_edit)
file_entry_edit.grid(row=4, column=1, padx=5, pady=5, sticky="nw")
Button(data_edit, text="选择文件", command=lambda: file_update(file_entry_edit)).grid(row=4, column=2, padx=5, pady=5, sticky="nw")

#保存按钮设置
button_save_edit=Button(data_edit,text='保存修改',command=update_task)
button_save_edit.grid(row=5, column=2, padx=5, pady=5, sticky="e")
Button(data_edit, text='打开文件', command=lambda: open_file(file_entry_edit)).grid(row=5, column=1, padx=5, pady=5, sticky="w")
button_delete = Button(data_edit, text='删除任务', command=delete_task)
button_delete.grid(row=5, column=3, padx=5, pady=5, sticky="w")

'''data_search 选项卡设置'''
Label(data_search,text='按分支查找',font=('等线',15)).grid(row=0, column=0, padx=5, pady=5, sticky="nw")
branch_search = Entry(data_search)
branch_search.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
button_search=Button(data_search,text='搜索',command=search_branch)
button_search.grid(row=0, column=3, padx=5, pady=5, sticky="e")

'''book_list 选项卡设置'''
button_book_list=(Button(book_list,text="书目录入",command=bookwinopen))
button_book_list.grid(row=0,column=0,padx=5,pady=5,sticky="nsew")
button_book_excellist = Button(book_list, text="按表格批量导入书目", command=booklistopen)
button_book_excellist.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
button_book_ebook=(Button(book_list,text="EPUB格式录入",command=lambda: BookEpubReader(window)))
button_book_ebook.grid(row=2, column=0, padx=5, pady=5, sticky="nsew")
button_book_edit = Button(book_list, text="书目搜索/编辑/删除", command=lambda: BookEditWindow(window))
button_book_edit.grid(row=3, column=0, padx=5, pady=5, sticky="nsew")

'''more_about 选项卡设置'''
button_time_list=Button(more_about,text="一日计划安排",command=timewinopen).grid(row=0,column=0,padx=5,pady=5,sticky="nsew")
button_about=Button(more_about,text="关于",command=about).grid(row=1,column=0,padx=5,pady=5,sticky="nsew")

# 添加选项卡
note.add(data_add, text='添加待办')
note.add(data_edit, text='修改待办')
note.add(data_search,text="搜索待办")
note.add(book_list,text="个人图书馆管理")
note.add(more_about,text='奇奇怪怪的试验田')
window.mainloop()