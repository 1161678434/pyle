"""
Day 6 Web 版：多轮对话聊天页面
启动方式：python day6_web_server.py
访问地址：http://localhost:5000
"""
import os
from dotenv import load_dotenv
from openai import OpenAI
from flask import Flask, render_template, request, jsonify

load_dotenv()
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)

app = Flask(__name__)

# 存储每个会话的消息历史（简单内存存储）
sessions = {}

MAX_HISTORY = 10  # 保留最近 10 轮对话


def get_or_create_messages(session_id):
    """获取或创建会话的消息历史"""
    if session_id not in sessions:
        sessions[session_id] = [
            {"role": "system", "content": "你是一个Python教学助手，用中文回答，不超过200字"},
        ]
    return sessions[session_id]


def trim_messages(messages):
    """限制上下文长度，保留 system + 最近 N 轮完整配对"""
    if len(messages) > MAX_HISTORY * 2 + 1:
        keep = MAX_HISTORY * 2
        history = messages[-keep:]
        if history[0]["role"] != "user":
            history = messages[-(keep + 1):]
        messages[:] = [messages[0]] + history


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json()
    session_id = data.get("session_id", "default")
    user_input = data.get("message", "").strip()

    if not user_input:
        return jsonify({"error": "消息不能为空"}), 400

    messages = get_or_create_messages(session_id)

    # 处理命令
    if user_input.lower() == "quit":
        return jsonify({"reply": "对话已结束，刷新页面重新开始", "quit": True})

    if user_input.lower() == "/history":
        # 构建历史记录
        history_lines = []
        for msg in messages:
            if msg["role"] == "system":
                continue
            history_lines.append(f"{msg['role']}: {msg['content']}")
        history_lines.append(f"-------共 {len(messages) - 1} 条消息-------")
        return jsonify({"reply": "\n".join(history_lines)})

    if user_input.lower() == "/clear":
        sessions[session_id] = [messages[0]]  # 只保留 system
        return jsonify({"reply": "对话已重置"})

    # 正常对话：加入用户消息
    messages.append({"role": "user", "content": user_input})

    # 裁剪过长历史
    trim_messages(messages)

    # 调用 API
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            max_tokens=500,
            messages=messages,
        )
        ai_text = response.choices[0].message.content
        messages.append({"role": "assistant", "content": ai_text})
        return jsonify({"reply": ai_text})

    except Exception as e:
        messages.pop()  # 移除失败的用户消息
        return jsonify({"error": f"调用失败: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
