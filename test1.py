from tkinter import *
from tkinter.ttk import *
from tkinter import scrolledtext
import time

# 主窗口设置
window = Tk()
window.geometry("680x500")
window.title("TooManyThings")
window.grid_columnconfigure(1, weight=1)  # 允许列自动扩展
window.grid_rowconfigure(3, weight=1)     # 允许行自动扩展

t = time.localtime()
m = f"今天是{t.tm_year}年{t.tm_mon}月{t.tm_mday}日，今日待办事项如下:"
lbl = Label(window, text=m, font=("宋体", 15), relief="groove")
lbl.grid(column=1, row=0, rowspan=2, sticky="ew")

combo = Combobox(window)
combo['values'] = ('今日待办事项','全部待办事项','重要并且紧急','不重要但紧急','重要但不紧急','不重要不紧急','已经完成事项')
combo.current(1)
combo.grid(column=0, row=0, rowspan=2, sticky="w")

txt = scrolledtext.ScrolledText(window, width=80, height=10)
txt.grid(column=0, row=2, columnspan=2, sticky="nsew")

# Notebook 设置
note = Notebook(window)
data_add = Frame(note)
data_edit = Frame(note)

note.add(data_add, text='添加待办')
note.add(data_edit, text='修改待办')
note.grid(column=0, row=3, columnspan=2, sticky="nsew")  # 使用 sticky 填充空间

# 配置 data_add 的内容（关键修改点）
Label(data_add, text='标题:', font=("宋体", 15)).grid(row=0, column=0, padx=5, pady=5)
title_entry = Entry(data_add)
title_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

Label(data_add, text='内容:', font=("宋体", 15)).grid(row=1, column=0, padx=5, pady=5)
content_entry = Entry(data_add)
content_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

# 配置 Frame 的列权重确保内容扩展
data_add.grid_columnconfigure(1, weight=1)

window.mainloop()