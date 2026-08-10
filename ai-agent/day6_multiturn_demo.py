"""
Day 6 精讲：多轮对话的消息管理
=============================
核心问题：AI 无状态，你必须每次把整个对话历史重新发过去。

消息列表结构：
    messages = [
        {"role": "system",   "content": "设定AI行为"},
        {"role": "user",     "content": "用户说的话"},
        {"role": "assistant","content": "AI的回复"},
        {"role": "user",     "content": "用户说的下一句话"},
        {"role": "assistant","content": "AI的回复"},
        ...
    ]

每一轮：
    1. messages.append({"role": "user", ...})     # 把用户新消息加进去
    2. 把整个 messages 发给 API                      # 带历史的完整请求
    3. 拿到 AI 回复
    4. messages.append({"role": "assistant", ...})  # 把AI回复也加进去
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
# TODO 1: 把 Day5 的单次调用改造成 while 循环
# ============================================================
#   - 把 messages 定义在循环外面（初始只有 system prompt）
#   - 用 while True 持续接收 input()
#   - 输入 "quit" 时 break
#   - 每次把最新的 messages 发给 API
#   - 把 AI 回复添加到 messages 中

messages = [
    {"role": "system", "content": "你是一个Python教学助手，用中文回答，不超过100字"},
]

while True:
    # 1. 获取用户输入
    user_input = input("你: ")
    if user_input.strip() == "":
        continue  # 忽略空输入
    if user_input.lower() == "quit":
        print("对话结束")
        break

    # ============================================================
    # TODO 2: 加一个 /history 命令 —— 让用户查看完整对话历史
    # ============================================================
    #   提示：在 if user_input == "quit" 下面加一个 elif 判断
    #   user_input == "/history" 时，遍历 messages 打印每条记录
    #   注意跳过 system 消息（那是内部设定，不必展示）
    #
    #   预期输出效果：
    #   user: 你好
    #   assistant: 你好！有什么可以帮你的？
    #   user: 什么是变量
    #   assistant: 变量是...
    #   -------共 4 条消息-------
    elif user_input.lower() == "/history":
        for msg in messages:
            if msg["role"] == "system":
                continue  # 跳过 system 消息
            print(f"{msg['role']}: {msg['content']}")
        
        continue  # 不调 API，直接下一轮

    # ============================================================
    # TODO 3: 加一个 /clear 命令 —— 清空对话历史，重新开始
    # ============================================================
    #   user_input == "/clear" 时，把 messages 重置为只含 system prompt
    #   system prompt 保持不变
    #   打印 "对话已重置"
    elif user_input.lower() == "/clear":
        messages = [messages[0]]  # 保留 system prompt，丢弃其他消息
        print("对话已重置")
        continue  # 不调 API，直接下一轮

    # 2. 把用户消息加入历史
    messages.append({"role": "user", "content": user_input})
    MAX_HISTORY = 10  # 保留最近10轮对话（即20条消息：10条user + 10条assistant）
    if len(messages) > MAX_HISTORY * 2 + 1:
        # 只保留 system 消息 + 最近的 MAX_HISTORY 轮对话（每轮2条消息）
        keep = MAX_HISTORY * 2  # 最近20条消息（10轮对话）
        history = messages[-keep:]  # 最近20条消息
        if history[0]["role"] != "user":
            history = messages[-(keep + 1):] #  多取一条，从user开始，保证system不被丢弃
        messages = [messages[0]] + history  # system + 最近20条消息

    # 3. 发送完整历史给 API
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            max_tokens=200,
            messages=messages,
        )
        ai_text = response.choices[0].message.content
        print(f"AI: {ai_text}")

        # 4. 把 AI 回复也加入历史（关键！）
        messages.append({"role": "assistant", "content": ai_text})

    except Exception as e:
        print(f"调用失败: {e}")
        # 如果调用失败，把刚才加入的 user 消息移除，避免历史脏数据
        messages.pop()


# ============================================================
# TODO 4: 限制上下文长度 —— 防止 messages 无限增长
# ============================================================
#   当历史太长时，API 调用会变慢、花更多钱、甚至超出模型限制。
#   策略：保留 system prompt + 最近 N 对对话（一对 = user + assistant）
#
#   实现：
#   MAX_HISTORY = 10  # 保留最近10轮对话（即20条消息：10条user + 10条assistant）
#   在每次 API 调用之前，如果 len(messages) > MAX_HISTORY * 2 + 1：
#       messages = [system] + messages[-(MAX_HISTORY * 2):]
#   （+1 是因为 system 消息始终保留在最前面）



# ============================================================
# TODO 5（思考题）: 如果 AI 的回复包含代码块，怎样
#   messages 里有 {"role": "assistant", "content": "```python\n..."}
#   这会在下一轮发给 AI，AI 能正确理解吗？
#   试试让它"把上面的代码改成函数的形式"
# ============================================================
