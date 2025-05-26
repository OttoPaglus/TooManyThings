# ===== 统一导入区 =====
import os
import sqlite3
import zipfile
from io import BytesIO
import re
from tkinter import (
    Toplevel, Text, Scrollbar, Button, filedialog,
    messagebox, RIGHT, Y, LEFT, BOTH, END
)

from ebooklib import epub
from bs4 import BeautifulSoup
from lxml import etree
import mobi
import fitz  # PyMuPDF

# ===== 主类定义 =====
class BookEpubReader(Toplevel):
    def __init__(self, parent, on_close_callback=None):
        super().__init__(parent)
        self.title("电子书阅读器")
        self.geometry("800x700")
        self.on_close_callback = on_close_callback
        self.ensure_createtime_column()
        self.create_book_insert_trigger()
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.build_widgets()

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

    def on_close(self):
        if self.on_close_callback:
            self.on_close_callback()
        self.destroy()

    def build_widgets(self):
        Button(self, text="打开电子书文件（EPUB）", command=self.open_file).pack(pady=10)

        self.text = Text(self, wrap="word", font=("等线", 12))
        self.text.pack(side=LEFT, fill=BOTH, expand=True)

        scrollbar = Scrollbar(self, command=self.text.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.text.config(yscrollcommand=scrollbar.set)

    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[
            ("支持的电子书", "*.epub"),
            ("所有文件", "*.*")
        ])
        if not file_path:
            return

        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".epub":
            self.open_epub(file_path)
        elif ext == ".pdf":
            self.open_pdf(file_path)
        elif ext == ".txt":
            self.open_txt(file_path)
        elif ext == ".mobi":
            self.open_mobi(file_path)
        else:
            messagebox.showerror("不支持的格式", f"不支持的文件类型：{ext}")

    def open_epub(self, file_path):
        try:
            book = epub.read_epub(file_path)
            content = ""
            for item in book.get_items_of_type(epub.EpubHtml):
                soup = BeautifulSoup(item.get_body_content(), 'html.parser')
                content += soup.get_text() + "\n\n"

            metadata = book.metadata.get('DC', {})
            title = metadata.get('title', ['未命名书籍'])[0]
            creator = metadata.get('creator', ['未知作者'])[0]
            publisher = metadata.get('publisher', ['未知出版社'])[0]
        except Exception as e:
            try:
                content, title, creator, publisher = self.read_epub_fallback(file_path)
            except Exception as ex:
                messagebox.showerror("读取错误", f"无法读取 EPUB 文件：\n{str(e)}\n备用解析也失败：{str(ex)}")
                return

        import re

        def split_nation_and_author(creator_raw):
            """
            支持多位作者，每位格式如【国】姓名，提取 Nation 与 Author
            """
            if not creator_raw:
                return None, None

            creator_raw = creator_raw.strip()
            authors = [a.strip() for a in re.split(r'[,/;，；]', creator_raw) if a.strip()]

            nations = []
            names = []

            for item in authors:
                match = re.match(r"[【\[]?([^\]】]{1,6})[】\]]?(.*)", item)
                if match and match.group(2).strip():
                    nations.append(match.group(1).strip())
                    names.append(match.group(2).strip())
                else:
                    nations.append(None)
                    names.append(item.strip())

            # 合并为 / 分隔形式（用于入库）
            nation_str = "/".join([n for n in nations if n])
            author_str = " / ".join(names)

            return nation_str or None, author_str or None

        self.text.delete(1.0, END)
        self.text.insert(END, content.strip())
        nation, author = split_nation_and_author(creator)
        self.insert_into_database(title, author, publisher, file_path, nation)

    def read_epub_fallback(self, file_path):
        def get_rootfile_path(zipf):
            container_xml = zipf.read('META-INF/container.xml')
            tree = etree.fromstring(container_xml)
            ns = {'cn': 'urn:oasis:names:tc:opendocument:xmlns:container'}
            rootfile = tree.find('.//cn:rootfile', namespaces=ns)
            if rootfile is None:
                raise FileNotFoundError("container.xml 中未找到 rootfile")
            return rootfile.get('full-path')

        def parse_content_opf(zipf, opf_path):
            opf_xml = zipf.read(opf_path)
            tree = etree.fromstring(opf_xml)
            ns = {'opf': 'http://www.idpf.org/2007/opf'}
            items = tree.findall('.//opf:item', namespaces=ns)
            manifest = {}
            for item in items:
                href = item.get('href')
                media_type = item.get('media-type')
                manifest[href] = media_type
            return manifest, opf_path.rpartition('/')[0]

        def read_chapter(zipf, base_path, href):
            full_path = base_path + '/' + href if base_path else href
            return zipf.read(full_path)

        def extract_text_from_xhtml(xhtml_bytes):
            parser = etree.XMLParser(recover=True)
            tree = etree.parse(BytesIO(xhtml_bytes), parser)
            texts = tree.xpath('//text()')
            return ''.join(texts).strip()

        with zipfile.ZipFile(file_path, 'r') as zipf:
            opf_path = get_rootfile_path(zipf)
            manifest, base_path = parse_content_opf(zipf, opf_path)

            content = ""
            for href, media_type in manifest.items():
                if media_type == 'application/xhtml+xml':
                    xhtml = read_chapter(zipf, base_path, href)
                    text = extract_text_from_xhtml(xhtml)
                    content += text + "\n\n"

            opf_xml = zipf.read(opf_path)
            tree = etree.fromstring(opf_xml)
            ns_dc = {'dc': 'http://purl.org/dc/elements/1.1/'}
            title_el = tree.find('.//dc:title', namespaces=ns_dc)
            creator_el = tree.find('.//dc:creator', namespaces=ns_dc)
            publisher_el = tree.find('.//dc:publisher', namespaces=ns_dc)
            title = title_el.text if title_el is not None else '未命名书籍'
            creator = creator_el.text if creator_el is not None else '未知作者'
            publisher = publisher_el.text if publisher_el is not None else '未知出版社'

            return content, title, creator, publisher

    def open_pdf(self, file_path):
        try:
            doc = fitz.open(file_path)
            text = "\n\n".join([page.get_text() for page in doc])
            self.text.delete(1.0, END)
            self.text.insert(END, text.strip())
            self.insert_into_database(os.path.basename(file_path), None, None, file_path)
        except Exception as e:
            messagebox.showerror("读取失败", str(e))

    def open_txt(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            self.text.delete(1.0, END)
            self.text.insert(END, text.strip())
            self.insert_into_database(os.path.basename(file_path), None, None, file_path)
        except Exception as e:
            messagebox.showerror("读取失败", str(e))

    def open_mobi(self, file_path):
        try:
            m = mobi.Mobi(file_path)
            m.parse()
            html = m.get_raw_html()
            soup = BeautifulSoup(html, "html.parser")
            text = soup.get_text()
            self.text.delete(1.0, END)
            self.text.insert(END, text.strip())
            self.insert_into_database(os.path.basename(file_path), None, None, file_path)
        except Exception as e:
            messagebox.showerror("读取失败", str(e))

    def insert_into_database(self, title, author, publisher, filepath, nation=None):

        try:
            conn = sqlite3.connect("Thingsdatabase.db")
            cursor = conn.cursor()
            cursor.execute("""INSERT INTO book_storlist (
                Title, ISBN, Writer, Nation, Publisher, Publish_time,
                ReclassCN, ReclassDV, Location, Buy_time, Buy_location, Ebook_address
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                           (title, None, author, nation, publisher, None,
                            None, None, None, None, None, filepath))
            conn.commit()
            messagebox.showinfo("导入成功", f"书籍《{title}》信息已录入数据库。")
        except Exception as e:
            if 'conn' in locals():
                conn.rollback()
            messagebox.showerror("数据库错误", str(e))
        finally:
            if 'conn' in locals():
                conn.close()
