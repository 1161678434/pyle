"""
Day 8：上下文管理 —— Token 计数 + 上下文窗口
===============================================
上半场：理解 token（不是字！不是词！）
下半场：理解上下文窗口（context window）—— 模型的"记忆容量"
"""
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)


# ============================================================
# 第一部分：Token 是什么？
# ============================================================
# Token 是模型处理文本的最小单位，不是"字"也不是"词"
#
# 粗略规律（中文）：
#   1 个常用汉字 ≈ 0.5~1.5 token
#   1 个英文单词 ≈ 1~2 token
#   1 个标点符号 ≈ 1 token
#
# 精确规律：不同模型的 tokenizer 不同，需要专门的库来算


# ============================================================
# TODO 1：直观感受 token 数量
# ============================================================
# 安装 tiktoken 库：pip install tiktoken
# tiktoken 是 OpenAI 开源的 token 计算库，兼容 DeepSeek

import tiktoken

# DeepSeek 使用 cl100k_base 编码（和 GPT-4 一样）
encoding = tiktoken.get_encoding("cl100k_base")

texts = [
    "你好世界",
    "Hello World",
    "你好世界 Hello World",
    "Python是一门优雅的编程语言",
    "def add(a, b): return a + b",
]

print("=" * 60)
print("TODO 1：不同文本的 token 数量")
print("=" * 60)
for text in texts:
    tokens = encoding.encode(text)
    print(f"文本：{text!r:40s} → {len(tokens):3d} tokens   (解码验证：{encoding.decode(tokens)!r})")
print()
print("观察：中文和英文的 token 消耗效率，哪个更高？")
print()


# ============================================================
# TODO 2：观察 max_tokens 的截断效果
# ============================================================
# max_tokens 限制的是输出长度，不是输入长度
# 设小了 → 回答一半被截断（让人困惑）
# 设大了 → 浪费钱

for mt in [20, 100, 500]:
    response = client.chat.completions.create(
        model="deepseek-chat",
        max_tokens=mt,  # ← 输出上限，单位是 token 不是字！
        messages=[{"role": "user", "content": "详细介绍 Python 的发展历史"}],
    )
    content = response.choices[0].message.content
    # 用 tiktoken 精确计数
    actual_tokens = len(encoding.encode(content))
    print(f"max_tokens={mt:3d} → 实际输出 {actual_tokens:3d} tokens, {len(content)} 字符")
    print(f"  内容：{content[:80]}...")
    print()

print("观察：为什么 max_tokens=20 时回答很短甚至不完整？")
print()


# ============================================================
# TODO 3：用 finish_reason 判断截断原因
# ============================================================
# "stop"  → 自然结束（正常）
# "length" → 被 max_tokens 硬性截断（危险！用户看到不完整的回答）

response = client.chat.completions.create(
    model="deepseek-chat",
    max_tokens=20,
    messages=[{"role": "user", "content": "解释什么是机器学习"}],
)

print(f"finish_reason = {response.choices[0].finish_reason}")
print(f"回答内容：{response.choices[0].message.content}")
print("解释：finish_reason='length' 说明什么？")
print()


# ============================================================
# 第二部分：上下文窗口（Context Window）
# ============================================================
# 模型的"记忆"不是无限的——有一个上限叫 context_window
# DeepSeek V3 的 context window ≈ 128K tokens（输入 + 输出）
#
# 每次调用 API，messages 列表里的所有内容都会占用这个窗口：
#   system prompt + 所有 user 消息 + 所有 assistant 消息
#
# 当消息总量超过窗口时 → 报错或截断


# ============================================================
# TODO 4：模拟长对话，看上下文增长
# ============================================================
# 用一段长文本反复对话，观察 messages 的 token 消耗

long_text = """Python 是一种广泛使用的高级编程语言，
由吉多·范罗苏姆（Guido van Rossum）于 1991 年首次发布。
Python 的设计哲学强调代码的可读性和简洁性，
使用缩进而不是花括号来定义代码块。
Python 是解释型语言，支持多种编程范式，
包括面向对象、命令式、函数式和过程式编程。
Python 拥有动态类型系统和垃圾回收功能。
""" * 5  # 重复5次，模拟长文本

messages = [
    {"role": "system", "content": "你是一个Python教学助手"},
]

total_tokens = len(encoding.encode(messages[0]["content"]))
print("=" * 60)
print("TODO 4：模拟消息增长，观察 token 消耗")
print("=" * 60)
print(f"初始（只有 system prompt）：{total_tokens} tokens")

# 模拟 5 轮对话
for i in range(5):
    # 每轮：用户发一条长消息 + AI 回复
    user_msg = f"第{i+1}轮：{long_text[:100]}..."
    assistant_msg = f"这是第{i+1}轮的回复。Python 的关键优势包括简洁的语法、丰富的社区库和跨平台的兼容性。"

    messages.append({"role": "user", "content": user_msg})
    messages.append({"role": "assistant", "content": assistant_msg})

    # 重新计算整段对话的 token 总量
    full_text = ""
    for m in messages:
        full_text += m["content"]
    all_tokens = len(encoding.encode(full_text))
    print(f"第{i+1}轮后：{all_tokens:5d} tokens | 消息条数：{len(messages)}")

print()
print("思考：如果不加控制，100轮对话后会发生什么？")
print()


# ============================================================
# TODO 5（动手题）：实现一个简单的上下文管理
# ============================================================
# 把第 44 行的 long_text 改成 100 倍，模拟超长上下文
# 然后在调用 API 之前，加上你的裁剪逻辑：
#   - 如果 messages 超过 500 tokens → 只保留最近 3 轮对话
#   - 提示：用 encoding.encode() 计算每条消息的 token 数
#   - 提示：保留 system prompt + 最近 N 条消息

messages = [
    {"role": "system", "content": "你是一个Python教学助手，用中文回答"},
]

# 模拟 10 轮对话历史（用户问题 + AI 回答）
history = [
    ("什么是变量？", "变量是存储数据的容器，就像贴了标签的盒子。"),
    ("什么是循环？", "循环是重复执行一段代码的结构，Python中有for和while两种。"),
    ("什么是函数？", "函数是一段可重复使用的代码块，用def关键字定义。"),
    ("什么是列表？", "列表是有序的可变容器，用[]表示，可以存储任意类型的数据。"),
    ("什么是字典？", "字典是键值对的无序集合，用{}表示，通过key快速查找value。"),
    ("什么是类？", "类是创建对象的模板，定义了对象的属性和方法。"),
    ("什么是异常？", "异常是程序运行时发生的错误，用try/except捕获和处理。"),
    ("什么是文件操作？", "文件操作包括打开、读取、写入和关闭文件，使用open()函数。"),
    ("什么是模块？", "模块是.py文件，用import导入，可以复用代码。"),
    ("什么是装饰器？", "装饰器是修改函数行为的工具，用@符号在函数上方使用。"),
]

# ← 你的代码从这里开始
# 1. 把 history 全部加入 messages（奇数项是 user，偶数项是 assistant）
# 2. 计算 messages 的总 token 数
# 3. 如果超过 500 tokens，裁剪到只保留 system prompt + 最近 3 轮对话
# 4. 用裁剪后的 messages 调用 API，问："我刚才问的第一个问题是什么？"
#
# 提示：AI 能回答"第一个问题是什么"吗？如果不能，说明什么？
#
# 你的代码：

for q, a in history:
    messages.append({"role": "user", "content": q})
    messages.append({"role": "assistant", "content": a})

# 计算总 tokens
full_text = ""
for m in messages:
    full_text += m["content"]
print(f"裁剪前：{len(encoding.encode(full_text))} tokens, {len(messages)} 条消息")
total = len(encoding.encode(full_text))
THRESHOLD = 500
# ← 在这里写裁剪逻辑
# 保持 system prompt（messages[0]），只保留最后 N 条

# ← 裁剪后，问 AI "我问的第一个问题是什么？"，观察结果
if total > THRESHOLD:
    # 只保留 system + 最近 3 轮 （六条消息）
    keep_count = 6
    messages = messages[:1] + messages[-keep_count:]
    # 重新计算裁剪后的 token 数
    full_text = ""
    for m in messages:
        full_text += m["content"]
    print(f"裁剪后：{len(encoding.encode(full_text))} tokens, {len(messages)} 条消息")
else:
    print("不需要裁剪")

# 调用 API 问："我刚才问的第一个问题是什么？"
response = client.chat.completions.create(
    model="deepseek-chat",
    max_tokens=100,
    messages=messages + [{"role": "user", "content": "我刚才问的第一个问题是什么？"}],
)
print(f"AI 回答：{response.choices[0].message.content}")
# ============================================================
# TODO 6（思考题）：上下文管理的三种策略
# ============================================================
# 当对话太长，超出窗口限制时，有三种策略：
#
# 策略 A：滑动窗口 —— 只保留最近 N 条消息（简单但丢失全局信息）
# 策略 B：摘要压缩 —— 把旧对话总结成一段话，和新对话拼在一起
# 策略 C：分层记忆 —— 重要信息存"长期记忆"，对话只保留"短期记忆"
#
# 问题 1：以下场景分别适合哪种策略？为什么？
#   - 客服机器人：滑动窗口________________________
#   - 编程教学助手：摘要压缩______________________
#   - 小说创作助手：分层记忆______________________
#
# 问题 2：Day 6 的多轮对话 Web 聊天页面，你用什么策略管理上下文？
#         提示：看你 Day 6 的代码

# 答： 策略为  滑动窗口，因为没有设计摘要压缩和分层记忆的功能，所以只能通过限制 messages 的长度来控制上下文窗口的大小。每次用户发送新消息时，检查 messages 的总 token 数，如果超过设定的阈值（比如 500 tokens），就删除最早的对话记录，保留最新的几轮对话和 system prompt。
