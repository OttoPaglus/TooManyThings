import tkinter as tk
from tkinter import scrolledtext
import requests
import json
import sqlite3
import os

from constant import AppConstants

def generate_system_prompt_from_sqlite(db_path, table_name="Thingstable", sample_limit=5):
    if not os.path.exists(db_path):
        return None

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 获取字段
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [col[1] for col in cursor.fetchall()]

        # 获取样例数据
        cursor.execute(f"SELECT * FROM {table_name} LIMIT {sample_limit}")
        rows = cursor.fetchall()

        conn.close()

        # 构建系统提示词
        prompt = "你是一个智能待办助手，请参考以下历史数据，根据用户输入生成新的待办事项建议：\n\n"
        prompt += "字段信息：\n"
        for col in columns:
            prompt += f"- {col}\n"

        prompt += "\n样例数据：\n"
        for row in rows:
            row_text = " | ".join(str(item) for item in row)
            prompt += f"{row_text}\n"

        prompt += "\n请根据这些信息和用户输入，输出结构合理、格式一致的待办建议。"
        return prompt

    except Exception as e:
        return f"提示词生成失败：{e}"

class OllamaChatClient:
    def __init__(self, model="deepseek-r1:7b", url=AppConstants.chathost(), system_prompt=None):
        self.model = model
        self.api_url = f"{url}/api/chat"
        self.messages = []
        self.system_prompt = system_prompt  # 新增字段

    def stream_chat(self, user_input):
        full_messages = []
        if self.system_prompt:
            full_messages.append({"role": "system", "content": self.system_prompt})
        full_messages += self.messages
        full_messages.append({"role": "user", "content": user_input})

        payload = {
            "model": self.model,
            "messages": full_messages,
            "stream": True
        }

        with requests.post(self.api_url, json=payload, stream=True) as response:
            if response.status_code != 200:
                yield f"错误：{response.status_code} - {response.text}"
                return

            full_reply = ""
            for line in response.iter_lines():
                if line:
                    try:
                        chunk = line.decode("utf-8")
                        if chunk.startswith("data: "):
                            chunk = chunk[6:]
                        data = json.loads(chunk)
                        content = data.get("message", {}).get("content", "")
                        full_reply += content
                        yield content
                    except Exception as e:
                        yield f"[解析错误：{e}]"
            self.messages.append({"role": "assistant", "content": full_reply})


# ----------------- Tkinter UI -------------------

class ChatApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Ollama DeepSeek Chat (流式+数据库)")
        self.master.geometry("600x700")

        self.client = OllamaChatClient()

        self.chat_display = scrolledtext.ScrolledText(master, wrap=tk.WORD, state='disabled', font=("Arial", 12))
        self.chat_display.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.user_input = tk.Entry(master, font=("Arial", 12))
        self.user_input.pack(padx=10, pady=5, fill=tk.X)
        self.user_input.bind("<Return>", self.send_message)

        self.send_button = tk.Button(master, text="发送", command=self.send_message)
        self.send_button.pack(pady=(0, 10))

        prompt = generate_system_prompt_from_sqlite("Thingsdatabase.db")
        self.client = OllamaChatClient(system_prompt=prompt)

    def send_message(self, event=None):
        user_text = self.user_input.get().strip()
        if not user_text:
            return

        self.append_chat("你", user_text)
        self.user_input.delete(0, tk.END)

        self.chat_display.config(state='normal')
        self.chat_display.insert(tk.END, "AI：")
        self.chat_display.config(state='disabled')

        # 启动流式回复
        self.reply_generator = self.client.stream_chat(user_text)
        self.master.after(10, self.update_streamed_response)

    def update_streamed_response(self):
        try:
            content = next(self.reply_generator)
            self.chat_display.config(state='normal')
            self.chat_display.insert(tk.END, content)
            self.chat_display.config(state='disabled')
            self.chat_display.see(tk.END)
            self.master.after(10, self.update_streamed_response)
        except StopIteration:
            pass  # 结束流式响应
        except Exception as e:
            self.append_chat("系统", f"[错误]: {e}")

    def append_chat(self, sender, message):
        self.chat_display.config(state='normal')
        self.chat_display.insert(tk.END, f"{sender}：{message}\n\n")
        self.chat_display.config(state='disabled')
        self.chat_display.see(tk.END)


# ----------------- 启动 -------------------

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatApp(root)
    root.mainloop()
