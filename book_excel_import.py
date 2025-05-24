import sqlite3
import openpyxl
from tkinter import Toplevel, Label, Button, filedialog, messagebox, W


class BookImportWindow(Toplevel):
    def __init__(self, parent, on_close_callback=None):
        super().__init__(parent)
        self.title("批量导入书籍")
        self.geometry("500x200")
        self.on_close_callback = on_close_callback
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.build_widgets()

    def on_close(self):
        if self.on_close_callback:
            self.on_close_callback()
        self.destroy()

    def build_widgets(self):
        Label(self, text="批量导入书籍信息（Excel）", font=("等线", 20)).grid(row=0, column=0, columnspan=2, pady=10, sticky=W)
        Label(self, text="请上传包含书籍信息的.xlsx文件\n格式需与数据库字段一致。", font=("等线", 12)).grid(row=1, column=0, columnspan=2, sticky=W, padx=10)
        Button(self, text="选择文件并导入", command=self.import_excel).grid(row=2, column=0, padx=10, pady=20, sticky=W)

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

            conn.commit()
            messagebox.showinfo("导入成功", f"成功导入 {inserted_count} 本书。")
        except Exception as e:
            if 'conn' in locals():
                conn.rollback()
            messagebox.showerror("导入失败", f"出错信息：{str(e)}")
        finally:
            if 'conn' in locals():
                conn.close()
