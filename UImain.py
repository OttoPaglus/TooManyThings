from tkinter import *
from tkinter.ttk import *
from tkinter import scrolledtext
import time
import datetime
import sqlite3
from tkinter import messagebox
'''全局变量设置'''
test = []
current_edit_id = None
things_level_dic={0:'重要并且紧急',1:'不重要但紧急',2:'重要但不紧急',3:'不重要不紧急'}
things_level_dic_op={'重要并且紧急':0,'不重要但紧急':1,'重要但不紧急':2,'不重要不紧急':3}

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

            # 填充数据
            title_edit.insert(0, task_data[1])  # title字段
            content_edit.insert(END, task_data[2])  # text字段
            date_edit.insert(0, task_data[4])  # deadline字段
            branch_edit.insert(END, task_data[6])

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
        cursor.close()
        conn.close()


def save():
    # 获取各输入框的值
    title = title_entry.get()
    content = content_entry.get("1.0", "end-1c")  # 获取多行文本框内容
    date = date_entry.get()
    level = things_level_dic_op[level_entry.get()]
    branch = branch_entry.get()
    # 清空输入框
    title_entry.delete(0, 'end')
    content_entry.delete('1.0', 'end')
    date_entry.delete(0, 'end')
    branch_entry.delete(0, 'end')
    level_entry.set('')  # 清空选择框

    # 显示保存成功提示
    print("保存成功！当前数据条数：", len(test))
    # 数据库操作部分
    try:
        conn = sqlite3.connect("Thingsdatabase.db")
        cursor = conn.cursor()
        # 使用参数化查询插入数据
        cursor.execute("INSERT INTO Thingstable(title,deadline,text,level,isfinished,branch) VALUES (?, ?, ? ,? ,?,?)",
                       (title,date, content, level, False, branch))
        conn.commit()
        messagebox.showinfo("成功", "成功保存到数据库！")
        update_treeview(None)
    except sqlite3.Error as e:
        messagebox.showerror("错误", f"加载数据失败:\n{str(e)}")
    finally:
        if conn:
            conn.close()


def update_task():
    # 获取输入数据
    title = title_edit.get()
    content = content_edit.get("1.0", "end-1c")
    deadline = date_edit.get()
    level = things_level_dic_op[level_edit.get()]
    isfinish = 1 if finish_edit.get() == '已完成' else 0
    branch = branch_edit.get()

    try:
        conn = sqlite3.connect("Thingsdatabase.db")
        cursor = conn.cursor()
        cursor.execute("""UPDATE Thingstable 
                        SET title=?, text=?, deadline=?, level=?, isfinished=?,branch=?
                        WHERE id=?""",
                       (title, content, deadline, level, isfinish,branch, current_edit_id))
        conn.commit()

        # 更新显示
        update_treeview(None)
        note.select(data_add)  # 切换回添加选项卡

        # 清除编辑数据
        title_edit.delete(0, END)
        content_edit.delete('1.0', END)
        date_edit.delete(0, END)
        level_edit.set('')
        finish_edit.set('')

        messagebox.showinfo("成功", "任务更新成功！")
        update_treeview(None)
    except Exception as e:
        messagebox.showerror("错误", f"加载数据失败:\n{str(e)}")
    finally:
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

def on_tab_changed(event):
    current_tab = note.select()

    # 方法1：通过选项卡文本判断
    tab_text = note.tab(current_tab, "text")
    if tab_text == "关于":  # 只对指定文本的选项卡生效
        messagebox.showinfo("启动说明",
                        "本程序为待办事项管理系统，\n请在添加待办选项卡中添加待办事项，\n双击待办事项可进行修改和删除操作。\n作者：OttoPaglus\n版本：v1.0\n日期：2025年04月")
def search_branch():
    conn = sqlite3.connect("Thingsdatabase.db")
    cursor = conn.cursor()
    branch = branch_search.get()
    for item in txtree.get_children():
        txtree.delete(item)
    try:
        cursor.execute("SELECT id, title, deadline FROM Thingstable WHERE branch=?", (branch,))
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



'''主窗口设置'''

window = Tk()
window.title("TooManyThings")
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()
x = (screen_width // 2) - (700 // 2)
y = (screen_height // 2) - (500// 2)
window.geometry(f"{700}x{500}+{x}+{y}")
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
about_about= Frame(note)

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

#保存按钮设置
button_save_add=Button(data_add,text='保存',command=save)
button_save_add.grid(row=4, column=2, sticky="ne",padx=5, pady=5)

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

#保存按钮设置
button_save_edit=Button(data_edit,text='保存修改',command=update_task)
button_save_edit.grid(row=4, column=2, padx=5, pady=5, sticky="e")
button_delete = Button(data_edit, text='删除任务', command=delete_task)
button_delete.grid(row=4, column=3, padx=5, pady=5, sticky="w")

'''data_search 选项卡设置'''
Label(data_search,text='按分支查找',font=('等线',15)).grid(row=0, column=0, padx=5, pady=5, sticky="nw")
branch_search = Entry(data_search)
branch_search.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
button_search=Button(data_search,text='搜索',command=search_branch)
button_search.grid(row=0, column=3, padx=5, pady=5, sticky="e")
# 添加选项卡
note.add(data_add, text='添加待办')
note.add(data_edit, text='修改待办')
note.add(data_search,text="搜索待办")
note.add(about_about,text='关于')
note.bind("<<NotebookTabChanged>>", on_tab_changed)
window.mainloop()