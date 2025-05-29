import tkinter as tk
from tkinter import scrolledtext
import requests
import json

class OllamaChatClient:
    def __init__(self, model="deepseek-r1:7b", url="http://localhost:11434"):
        self.model = model
        self.api_url = f"{url}/api/chat"
        self.messages = []

    def stream_chat(self, user_input):
        """生成器：逐步返回 AI 回复的片段"""
        self.messages.append({"role": "user", "content": user_input})
        payload = {
            "model": self.model,
            "messages": self.messages,
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
        self.master.title("Ollama DeepSeek Chat (流式回复)")
        self.master.geometry("600x700")

        self.client = OllamaChatClient()

        self.chat_display = scrolledtext.ScrolledText(master, wrap=tk.WORD, state='disabled', font=("Arial", 12))
        self.chat_display.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.user_input = tk.Entry(master, font=("Arial", 12))
        self.user_input.pack(padx=10, pady=5, fill=tk.X)
        self.user_input.bind("<Return>", self.send_message)

        self.send_button = tk.Button(master, text="发送", command=self.send_message)
        self.send_button.pack(pady=(0, 10))

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
