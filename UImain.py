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

from todo_create import TodoTask, TodoCreator
from todo_edit import TodoEditor
from todo_search import TodoSearcher
from todo_query import TodoQuery
from utils.file_helper import FileHelper

from book_single_entry import BookEntryWindow
from book_excel_import import BookImportWindow
from book_epub_reader import BookEpubReader
from book_editor import BookEditWindow

from constant import AppConstants

'''全局变量设置'''
book_entry_window_instance = None
book_import_window_instance = None
book_epub_window_instance = None
book_edit_window_instance = None

def save():
    title = title_entry.get()
    content = content_entry.get("1.0", "end-1c")
    date = date_entry.get()
    level = AppConstants.THINGS_LEVEL_DIC_OP[level_entry.get()]
    branch = branch_entry.get() or None
    file_path = file_entry_add.get() or None

    task = TodoTask(title, content, date, level, False, branch, file_path)

    creator = TodoCreator()
    if creator.save_task(task):
        # 清空表单
        title_entry.delete(0, 'end')
        content_entry.delete('1.0', 'end')
        date_entry.delete(0, 'end')
        branch_entry.delete(0, 'end')
        level_entry.set('')
        file_entry_add.delete(0, 'end')
        update_treeview(None)
def update_task():
    if not current_edit_id:
        messagebox.showwarning("警告", "当前没有选中的任务")
        return

    task = TodoTask(
        title=title_edit.get(),
        content=content_edit.get("1.0", "end-1c"),
        deadline=date_edit.get(),
        level=AppConstants.THINGS_LEVEL_DIC_OP[level_edit.get()],
        isfinished=(finish_edit.get() == '已完成'),
        branch=branch_edit.get() or None,
        file=file_entry_edit.get() or None
    )

    editor = TodoEditor()
    if editor.update_task(task, current_edit_id):
        update_treeview(None)
        note.select(data_add)

        title_edit.delete(0, END)
        content_edit.delete('1.0', END)
        date_edit.delete(0, END)
        level_edit.set('')
        branch_edit.delete(0, END)
        finish_edit.set('')
        file_entry_edit.delete(0, END)
def load_data_to_edit(task_id):
    editor = TodoEditor()
    task, _ = editor.load_task(task_id)

    if task:
        global current_edit_id
        current_edit_id = task_id
        note.select(data_edit)

        title_edit.delete(0, END)
        content_edit.delete('1.0', END)
        date_edit.delete(0, END)
        branch_edit.delete(0, END)
        file_entry_edit.delete(0, END)

        title_edit.insert(0, task.title)
        content_edit.insert(END, task.content)
        date_edit.insert(0, task.deadline)
        branch_edit.insert(END, task.branch or "")
        file_entry_edit.insert(0, task.file or "")
        level_edit.set(AppConstants.THINGS_LEVEL_DIC.get(task.level, '重要并且紧急'))
        finish_edit.set('已完成' if task.isfinished else '未完成')
def delete_task():
    global current_edit_id
    if not current_edit_id:
        messagebox.showwarning("警告", "请先选择要删除的任务")
        return
    if not messagebox.askyesno("确认删除", "确定要删除这个任务吗？"):
        return
    editor = TodoEditor()
    if editor.delete_task(current_edit_id):
        update_treeview(None)
        title_edit.delete(0, END)
        content_edit.delete('1.0', END)
        date_edit.delete(0, END)
        level_edit.set('')
        finish_edit.set('')
        file_entry_edit.delete(0, END)
        branch_edit.delete(0, END)
        note.select(data_add)
        current_edit_id = None
def search_branch():
    branch = branch_search.get()
    searcher = TodoSearcher()
    results = searcher.search_by_branch(branch)

    # 清空现有树表
    for item in txtree.get_children():
        txtree.delete(item)

    # 插入结果
    for row in results:
        txtree.insert('', 'end', values=(row[1], row[2]), tags=(row[0],))
    combo.current(7)
def file_update(entry_widget):
    file_path = filedialog.askopenfilename()
    if file_path:
        entry_widget.delete(0, END)
        entry_widget.insert(0, file_path)
def on_treeview_double_click(event):
    """处理Treeview双击事件"""
    selected_item = txtree.selection()
    if selected_item:
        item = selected_item[0]
        task_id = txtree.item(item, "tags")[0]
        load_data_to_edit(task_id)
def open_file(entry_widget):
    FileHelper.open_file(entry_widget.get())
def update_treeview(event):
    selected_category = combo.get()
    query = TodoQuery()
    result = query.fetch_tasks_by_category(selected_category, AppConstants.THINGS_LEVEL_DIC_OP)

    txtree.delete(*txtree.get_children())

    for row in result:
        txtree.insert('', 'end',
                      values=(row[1], row[2]),
                      tags=(row[0],))
def about():
    messagebox.showinfo("启动说明", AppConstants.about_text())

def bookwinopen():
    global book_entry_window_instance
    if book_entry_window_instance is None or not book_entry_window_instance.winfo_exists():
        def on_close():
            global book_entry_window_instance
            book_entry_window_instance = None

        book_entry_window_instance = BookEntryWindow(window, on_close_callback=on_close)
    else:
        book_entry_window_instance.lift()

def booklistopen():
    global book_import_window_instance
    if book_import_window_instance is None or not book_import_window_instance.winfo_exists():
        def on_close():
            global book_import_window_instance
            book_import_window_instance = None
        book_import_window_instance = BookImportWindow(window, on_close_callback=on_close)
    else:
        book_import_window_instance.lift()

def bookepubopen():
    global book_epub_window_instance
    if book_epub_window_instance is None or not book_epub_window_instance.winfo_exists():
        def on_close():
            global book_epub_window_instance
            book_epub_window_instance = None
        book_epub_window_instance = BookEpubReader(window, on_close_callback=on_close)
    else:
        book_epub_window_instance.lift()

def bookeditopen():
    global book_edit_window_instance
    if book_edit_window_instance is None or not book_edit_window_instance.window.winfo_exists():
        book_edit_window_instance = BookEditWindow(window)
    else:
        book_edit_window_instance.window.lift()  # 把窗口置顶

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
    Label(timewindow,text="开发中请等待下一次版本更新",font=("等线",15)).grid(row=0, column=0, sticky=W)



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
combo['values'] = AppConstants.COMBO_VALUES
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
button_book_list = Button(book_list, text="书目录入", command=bookwinopen)
button_book_excellist = Button(book_list, text="按表格批量导入书目", command=booklistopen)
button_book_ebook = Button(book_list, text="电子书录入", command=bookepubopen)
button_book_edit = Button(book_list, text="书目搜索/编辑/删除", command=bookeditopen)

button_book_list.grid(row=0,column=0,padx=5,pady=5,sticky="nsew")
button_book_excellist.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
button_book_ebook.grid(row=2, column=0, padx=5, pady=5, sticky="nsew")
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