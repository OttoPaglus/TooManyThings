import os
import sys
import subprocess
from tkinter import messagebox

class FileHelper:
    @staticmethod
    def validate_path(path):
        if not os.path.isfile(path):
            raise FileNotFoundError("文件路径无效，请重新选择有效的文件。")
        return path

    @staticmethod
    def open_file(path):
        if not os.path.isfile(path):
            messagebox.showerror("错误", "文件路径无效或文件不存在，请检查路径")
            return

        try:
            if os.name == 'nt':
                os.startfile(path)
            elif os.name == 'posix':
                opener = 'open' if sys.platform == 'darwin' else 'xdg-open'
                subprocess.run([opener, path])
            else:
                messagebox.showwarning("不支持", "当前系统暂不支持打开文件操作")
        except Exception as e:
            messagebox.showerror("打开失败", f"无法打开文件:\n{str(e)}")
