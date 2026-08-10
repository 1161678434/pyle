"""
Day 9：流式响应（Streaming）
============================
之前所有 API 调用都是"一次性返回"——等 AI 全部想完，然后一次性吐出完整回答。
streaming 则是"边想边吐"——AI 每生成一个 token，立刻返回，用户看到打字机效果。
"""
import os
import time
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)


# ============================================================
# 第一部分：理解流式与非流式的区别
# ============================================================
# 非流式（之前所有调用）：
#   发送请求 → 等待...等待...等待 → 一次性返回完整回答
#   用户体感：卡了3秒，然后突然出现一大段文字
#
# 流式（今天要学的）：
#   发送请求 → 逐字返回 → 逐字返回 → 逐字返回 → 结束
#   用户体感：AI 在"打字"，每个字都是实时出现的


# ============================================================
# TODO 1：体验非流式 vs 流式的速度差异
# ============================================================
# 用同一个问题，分别用非流式和流式调用，对比首字出现时间

question = "用一句话介绍Python，要有创意"

# 非流式
print("=" * 60)
print("非流式调用：")
print("=" * 60)
start = time.time()
response = client.chat.completions.create(
    model="deepseek-chat",
    max_tokens=100,
    messages=[{"role": "user", "content": question}],
)
end = time.time()
print(f"回答：{response.choices[0].message.content}")
print(f"耗时：{end - start:.2f} 秒（一次性返回）")
print()

# 流式
print("=" * 60)
print("流式调用：")
print("=" * 60)
start = time.time()
stream = client.chat.completions.create(
    model="deepseek-chat",
    max_tokens=100,
    stream=True,  # ← 关键参数！打开流式开关
    messages=[{"role": "user", "content": question}],
)
print("回答：", end="", flush=True)
first_token_time = None
for chunk in stream:
    if chunk.choices[0].delta.content:
        if first_token_time is None:
            first_token_time = time.time()
        print(chunk.choices[0].delta.content, end="", flush=True)
end = time.time()
print()
print(f"首个 token 耗时：{first_token_time - start:.2f} 秒")
print(f"总耗时：{end - start:.2f} 秒")
print()
print("观察：哪种方式的'感知速度'更快？为什么？")
print()


# ============================================================
# TODO 2：读懂 stream 的返回结构
# ============================================================
# 非流式返回：response.choices[0].message.content（完整字符串）
# 流式返回：  逐块返回 chunk，每块里有 delta.content（增量字串）
#
# 每个 chunk 长这样：
#   ChatCompletionChunk(
#       choices=[Choice(delta=ChoiceDelta(content="Python"), ...)],
#       ...
#   )
#
# 注意：非流式是 .message.content，流式是 .delta.content
#       message（完整消息） vs delta（增量消息）

stream = client.chat.completions.create(
    model="deepseek-chat",
    max_tokens=50,
    stream=True,
    messages=[{"role": "user", "content": "说一个词：你好"}],
)

print("=" * 60)
print("TODO 2：观察每个 chunk 的结构")
print("=" * 60)
for i, chunk in enumerate(stream):
    delta = chunk.choices[0].delta
    content = delta.content if delta.content else "<空>"
    finish = chunk.choices[0].finish_reason or "null"
    print(f"chunk {i:2d}: finish_reason={finish:6s} | delta.content={content!r}")
    if i >= 10:
        print("...（只展示前 10 个 chunk）")
        break
print()

# 观察点：
#   - 前面的 chunk 有内容，为什么 finish_reason 是 null？ --  一开始没有回答内容？
#   - 最后一个 chunk 内容为空，为什么 finish_reason 是 "stop"？   -- 回答结束
#   - 这说明 finish_reason 是在什么时候出现的？ --- 结束的时候出现


# ============================================================
# TODO 3：流式状态下收集完整回答
# ============================================================
# 流式是增量返回的，如果要拿到完整回答，需要手动拼接

stream = client.chat.completions.create(
    model="deepseek-chat",
    max_tokens=50,
    stream=True,
    messages=[{"role": "user", "content": "什么是Python的列表推导式？"}],
)

# ← 你的代码：收集所有 delta.content，拼成完整回答
full_response = ""
for chunk in stream:
    delta = chunk.choices[0].delta
    if delta.content:
        full_response += delta.content  


print(f"完整回答：{full_response}")
print()


# ============================================================
# TODO 4（动手题）：实现一个简单的流式打字机效果
# ============================================================
# 在 TODO 3 的基础上，加一个"打字机效果"：
#   每个字符之间有 0.03 秒的延迟，模拟 AI 在思考打字
#   每遇到一个"。"（中文句号），额外停顿 0.2 秒
#
# 提示：
#   import sys
#   用 sys.stdout.write(char) + sys.stdout.flush() 逐字输出
#   用 time.sleep(0.03) 控制每个字符的延迟

import sys

stream = client.chat.completions.create(
    model="deepseek-chat",
    max_tokens=100,
    stream=True,
    messages=[{"role": "user", "content": "用三句话介绍 Python，每句话以句号结束。"}],
)

print("=" * 60)
print("TODO 4：打字机效果")
print("=" * 60)

# ← 在这里实现逐字打印效果
# 1. 遍历 chunk，拿到 delta.content
# 2. 对每个字符，sys.stdout.write(char)，然后 time.sleep(0.03)
# 3. 遇到"。"时，额外 time.sleep(0.2)
# 4. 结尾统一 print() 换行
for chunk in stream:
    delta = chunk.choices[0].delta
    if delta.content:
        for char in delta.content:
            sys.stdout.write(char)
            sys.stdout.flush()
            if char == "。":
                time.sleep(0.2)
            else:
                time.sleep(0.03)
print()



# ============================================================
# TODO 5（思考题）：streaming 的优缺点
# ============================================================
# 优点：
#   1. 感知速度更快 —— 用户不用等
#   2. 适合长文本 —— ChatGPT 的逐字输出就是 streaming
#   3. 可以中途停止 —— 用户看到不对的内容可以提前切断
#
# 缺点：
#   1. 无法事后编辑 —— 内容已经输出给用户了，不能撤回
#   2. 更难解析 —— 不能直接取 .content，要手动拼接
#   3. finish_reason 只在最后一个 chunk 才出现
#
# 问题：以下场景该用流式还是非流式？为什么？
#   A. Web 聊天页面（用户实时交互）  → 流式输出_______________
#   B. SQL 生成（需要完整 SQL）     → 非流失输出________________
#   C. 批量处理 1000 条数据          → 非流式输出________________
#   D. 翻译一句话                    → 非流失输出________________
