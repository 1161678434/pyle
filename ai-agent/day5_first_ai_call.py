"""
Day 5 练习：第一次调用 AI
=========================
用 DeepSeek API 发送消息，拿到 AI 回复。
"""
import os
from dotenv import load_dotenv
from openai import OpenAI

# ============================================================
# 1. 加载 API Key（从 .env 文件读取，不写死在代码里）
# ============================================================
load_dotenv()
api_key = os.getenv("DEEPSEEK_API_KEY")

# ============================================================
# 2. 创建客户端 —— 指向 DeepSeek 的服务器
# ============================================================
client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com",  # DeepSeek 的地址
)

# ============================================================
# 3. 发送第一条消息 —— 和 AI 对话
# ============================================================
try:
    response = client.chat.completions.create(
        model="deepseek-chat",          # 用哪个模型
        max_tokens=200,                 # 最多回复多长
        messages=[
            {"role": "system", "content": "你是一个python教学助手，用中文回答，不超过50字"},
            {"role": "user", "content": "用AI学Python是否可行"}
    ]
)

# ============================================================
# 4. 取出 AI 的回复并打印
# ============================================================
    ai_text = response.choices[0].message.content
    print("AI 回复：")
    print(ai_text)


# ============================================================
# 5. 看看完整的响应对象长什么样（调试用）
# ============================================================
    print("\n" + "=" * 50)
    print("[完整响应对象 — 方便调试]：")
    print(response)
    
except Exception as e:
    print(f"调用 API 异常: {e}")