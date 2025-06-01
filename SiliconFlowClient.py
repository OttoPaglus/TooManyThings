
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

        prompt = f"""
你是一个智能任务助手。请根据用户输入生成一个新的待办事项建议。

✅ 请严格按如下 JSON 格式输出，**不需要任何解释、描述或前缀后缀文本**。直接输出完整 JSON 即可。

示例格式：

{{
  "title": "任务标题",
  "text": "任务详情描述",
  "level": "重要紧急",  // 可选项：重要紧急、重要不紧急、不重要紧急、不紧急
  "deadline": "自动从用户输入中提取的日期,精确到年月日",
  "isfinished": false,
  "branch": "提取的活动主题或任务范围，只需要一个",
  "file": "无关联文件"
}}

字段信息如下：
{chr(10).join(f"- {col}" for col in columns)}

以下是数据库中的示例任务数据（仅供参考）：
"""
        for row in rows:
            prompt += " | ".join(str(item) for item in row) + "\n"

        prompt += "\n用户输入示例可能是任务内容、指令或命令，请你根据上下文合理输出一条结构化的待办 JSON。"
        return prompt
    except Exception as e:
        return f"[系统提示生成失败：{e}]"


class SiliconFlowClient:
    def __init__(self, api_key=None, model="Qwen/Qwen3-8B", system_prompt=None):
        self.api_key = api_key or "sk-usaxnlhkworwtpgftpvkgedgwpmcujbzvltufnvbqczxbvxw"
        self.model = model
        self.api_url = "https://api.siliconflow.cn/v1/chat/completions"
        self.messages = []
        self.system_prompt = system_prompt

    def stream_chat(self, user_input):
        self._full_reply = ""  # 新增：存一份完整回复，供外部访问

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

            for line in response.iter_lines():
                if line:
                    if line.startswith(b"data: "):
                        line = line[len(b"data: "):]
                    try:
                        chunk = json.loads(line.decode("utf-8"))
                        delta = chunk["choices"][0]["delta"].get("content")
                        if isinstance(delta, str):
                            self._full_reply += delta
                            yield delta
                    except Exception as e:
                        yield f"[解析错误：{e}]"

        self.messages.append({"role": "assistant", "content": self._full_reply})

