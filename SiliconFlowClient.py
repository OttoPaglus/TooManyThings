
import os
import requests
import json
import sqlite3


def generate_system_prompt_from_sqlite(db_path, table_name="Thingstable", sample_limit=5):
    if not os.path.exists(db_path):
        return None

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [col[1] for col in cursor.fetchall()]
        cursor.execute(f"SELECT * FROM {table_name} LIMIT {sample_limit}")
        rows = cursor.fetchall()
        conn.close()

        prompt = "你是一个智能待办助手，请参考以下历史数据，根据用户输入生成新的待办事项建议：\n\n"
        prompt += "字段信息：\n" + "\n".join(f"- {col}" for col in columns)
        prompt += "\n\n样例数据：\n"
        for row in rows:
            prompt += " | ".join(str(item) for item in row) + "\n"
        prompt += "\n请根据这些信息和用户输入，输出结构合理、格式一致的待办建议。"
        return prompt
    except Exception as e:
        return f"[系统提示生成失败：{e}]"


class SiliconFlowClient:
    def __init__(self, api_key=None, model="Qwen/Qwen3-8B", system_prompt=None):
        self.api_key = api_key or ""
        self.model = model
        self.api_url = "https://api.siliconflow.cn/v1/chat/completions"
        self.messages = []
        self.system_prompt = system_prompt

    def stream_chat(self, user_input):
        messages = []
        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})
        messages.extend(self.messages)
        messages.append({"role": "user", "content": user_input})

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": True
        }

        with requests.post(self.api_url, headers=headers, json=payload, stream=True) as response:
            if response.status_code != 200:
                yield f"错误：{response.status_code} - {response.text}"
                return

            full_reply = ""
            for line in response.iter_lines():
                if line:
                    if line.startswith(b"data: "):
                        line = line[len(b"data: "):]
                    try:
                        chunk = json.loads(line.decode("utf-8"))
                        delta = chunk["choices"][0]["delta"].get("content")
                        if isinstance(delta, str):
                            full_reply += delta
                            yield delta
                    except Exception as e:
                        yield f"[解析错误：{e}]"
            self.messages.append({"role": "assistant", "content": full_reply})
