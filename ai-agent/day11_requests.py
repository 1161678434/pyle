"""
Day 11：requests 库 —— 直接 HTTP 调 API
==========================================
之前用 OpenAI SDK（client.chat.completions.create）调 DeepSeek。
今天拆掉 SDK 这层壳，直接用 HTTP 请求调 API，理解底层发生了什么。

核心认知：
  SDK 本质上就是帮你发了 HTTP 请求，本质上和你手动发没有区别。
  学会 HTTP 方式后，任何语言的 API 你都会调——本质都一样。
"""
import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("DEEPSEEK_API_KEY")
API_URL = "https://api.deepseek.com/chat/completions"

# ============================================================
# 第一部分：HTTP 请求是什么？
# ============================================================
# SDK 调用（黑盒）：
#   client.chat.completions.create(model=..., messages=...)
#   → 内部发了 HTTP POST 请求 → 返回解析好的对象
#
# HTTP 调用（透明）：
#   你自己构造请求头、请求体 → requests.post() 发出去 → 拿到 JSON 字符串
#   → json.loads() 解析 → 取出想要的数据


# ============================================================
# TODO 1：对比 SDK 和 HTTP 两种调用方式
# ============================================================
# 用同一个问题，分别用两种方式调用，对比返回结果

question = "用一句话介绍Python"

# 方式 A：SDK
from openai import OpenAI
client = OpenAI(api_key=API_KEY, base_url="https://api.deepseek.com")

print("=" * 60)
print("方式 A：SDK 调用")
print("=" * 60)
response = client.chat.completions.create(
    model="deepseek-chat",
    max_tokens=50,
    messages=[{"role": "user", "content": question}],
)
print(f"回答：{response.choices[0].message.content}")
print(f"类型：{type(response)}")
print()

# 方式 B：HTTP
print("=" * 60)
print("方式 B：HTTP 调用")
print("=" * 60)
# HTTP 请求的三个要素：
#   1. URL（往哪发）
#   2. Headers（身份认证 + 格式声明）
#   3. Body（请求内容，JSON 格式）
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}
body = {
    "model": "deepseek-chat",
    "max_tokens": 50,
    "messages": [{"role": "user", "content": question}],
}

resp = requests.post(API_URL, headers=headers, json=body)
data = resp.json()
print(f"HTTP 状态码：{resp.status_code}")
print(f"回答：{data['choices'][0]['message']['content']}")
print(f"类型：{type(data)}")
print()

print("观察：两种方式返回的 answer 一样吗？返回类型有什么区别？")
print()


# ============================================================
# TODO 2：动手写第一个 HTTP 请求
# ============================================================
# 把上面的 headers 和 body 拆开理解：
#
#  headers = {
#      "Authorization": f"Bearer {API_KEY}",  ← 出示你的 API Key
#      "Content-Type": "application/json",     ← 告诉服务器我发的是 JSON
#  }
#
#  body = {
#      "model": "deepseek-chat",               ← 用什么模型
#      "messages": [...],                      ← 对话内容
#      "max_tokens": 100,                      ← 可选参数
#      "temperature": 0.7,                     ← 可选参数
#      "stream": False,                        ← 默认非流式
#  }
#
# 现在写一个函数 http_chat(messages, temperature=0.7, max_tokens=200)：
#   接收 messages 列表，返回 AI 的回答字符串
#   如果 HTTP 状态码不是 200，打印错误信息并返回 None

def http_chat(messages, temperature=0.7, max_tokens=200):
    """用 HTTP 直接调 DeepSeek API，返回 AI 回答字符串"""
    # ← 写你的代码
    header = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    body = {
        "model":"deepseek-chat",
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    response = requests.post(API_URL, headers=header, json=body)
    if response.status_code != 200:
        print(f"请求失败，状态码: {response.status_code}, 错误信息: {response.text}")
        return None
    data = response.json()
    return data["choices"][0]["message"]["content"]

# 测试
response = http_chat([{"role": "user", "content": "1+1等于几？"}])
print(f"http_chat 返回：{response}")
print()


# ============================================================
# TODO 3：用 HTTP 实现流式请求
# ============================================================
# SDK 的 stream=True 在 HTTP 层面做了什么？
#   请求体里加 "stream": true
#   服务器不再一次返回完整 JSON，而是逐行返回，每行格式：
#     data: {"choices":[{"delta":{"content":"你"}}],...}
#     data: {"choices":[{"delta":{"content":"好"}}],...}
#     data: [DONE]          ← 结束标记
#
# 这叫 Server-Sent Events（SSE），是一种流式数据格式

def http_chat_stream(messages, temperature=0.7):
    """用 HTTP 实现流式对话"""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    body = {
        "model": "deepseek-chat",
        "messages": messages,
        "temperature": temperature,
        "stream": True,  # ← HTTP 层面打开流式
    }

    # stream=True 让 requests 不一次性读完响应，而是逐行读取
    resp = requests.post(API_URL, headers=headers, json=body, stream=True)

    full_response = ""
    print("AI：", end="", flush=True)

    for line in resp.iter_lines():
        # ← 在这里处理每一行
        # 提示：
        #   1. 跳过空行和 "[DONE]"
        #   2. 去掉每行开头的 "data: " 前缀（6个字符）
        #   3. json.loads() 解析 JSON
        #   4. 取出 delta.content 并逐字打印
        #   5. 拼接到 full_response
        if not line:
            continue
        decoded_line = line.decode("utf-8")
        if decoded_line == "data: [DONE]":
            break
        if not decoded_line.startswith("data: "):
            continue
        json_str = decoded_line[6:]  # 去掉 "data: " 前6个字符缀
        data = json.loads(json_str)
        delta = data["choices"][0]["delta"]
        if "content" in delta:
            for char in delta["content"]:
                print(char, end="", flush=True)
                full_response += char
    print()
    return full_response


# 测试
print("=" * 60)
print("TODO 3：HTTP 流式请求")
print("=" * 60)
http_chat_stream([{"role": "user", "content": "用一句话介绍Python"}])
print()


# ============================================================
# TODO 4：用 resp.json() 提取更多信息
# ============================================================
# HTTP 返回的是一整坨 JSON，除了回答文本，还包含很多元信息
# 写一个函数 parse_response(resp)，返回一个简洁的字典

def parse_response(data):
    """从 API 返回的 JSON 中提取关键信息"""
    # ← 提取以下字段：
    #   answer：AI 的回答文本
    #   model：使用的模型名
    #   finish_reason：结束原因
    #   usage_tokens：消耗的 token 数（提示：data["usage"]["total_tokens"]）
    #   如果出错，返回 {"error": 错误信息}
    if "error" in data:
        return {"error": data["error"]["message"]}
    return{
        "answer": data["choices"][0]["message"]["content"],
        "model": data["model"],
        "finish_reason": data["choices"][0]["finish_reason"],
        "usage_tokens": data["usage"]["total_tokens"],
    }


# 测试
resp = requests.post(API_URL, headers=headers, json={
    "model": "deepseek-chat",
    "max_tokens": 50,
    "messages": [{"role": "user", "content": "你好"}],
})
info = parse_response(resp.json())
print(f"解析结果：{info}")
print()


# ============================================================
# TODO 5（思考题）：SDK vs HTTP，什么时候用哪个？
# ============================================================
# SDK 的优点：
#   1. 自动处理重试、超时、错误
#   2. 返回结构化对象，IDE 有自动补全
#   3. 代码更短
#
# HTTP 的优点：
#   1. 不依赖特定 SDK，任何语言都能用
#   2. 完全控制请求细节
#   3. 适合调试底层问题
#
# 问题 1：以下场景选 SDK 还是 HTTP？
#   A. 快速原型开发（想尽快看到效果）→SDK ________________
#   B. 用 Go/Java 写后端调 AI      → HTTP________________
#   C. 排查 API 调用失败的原因       → HTTP________________
#   D. 写一个 Python 脚本处理数据    → SDK ________________
#
# 问题 2：SDK 调用的本质是什么？
#         提示：看 TODO 1 的 headers 和 body
#         SDK 已经拼接好http需要调用的内容，直接使用即可