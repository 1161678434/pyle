"""
Day 10：AI 问答工具（小项目）
================================
整合 Day 5-9 全部技能，做一个命令行 AI 对话工具。

用到的技能：
  Day 5 → API 调用
  Day 6 → messages 多轮对话
  Day 7 → system prompt + temperature
  Day 8 → tiktoken 计数 + 滑动窗口
  Day 9 → stream=True + 打字机效果
"""
import os
import sys
import time
import tiktoken
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)
encoding = tiktoken.get_encoding("cl100k_base")

# ============================================================
# 配置区 —— 你可以修改这些参数
# ============================================================
SYSTEM_PROMPT = "你是一个Python教学助手，用中文回答，回答简洁，鼓励提问"
TEMPERATURE = 0.7
MAX_TOKENS = 500       # 每次回复的最大 token 数
WINDOW_SIZE = 2000     # 上下文窗口阈值（超过就裁剪）(单位：token)
KEEP_ROUNDS = 5        # 裁剪时保留最近 N 轮对话

# ============================================================
# TODO 1：计算 messages 的 token 数（Day 8 复习）
# ============================================================
def count_tokens(messages):
    """计算 messages 列表的总 token 数"""
    # ← 把 Day 8 的逻辑封装成函数
    full_text = ""
    for msg in messages:
        full_text += msg["content"] + "\n"
    tokens = encoding.encode(full_text)
    return len(tokens)


# ============================================================
# TODO 2：滑动窗口裁剪（Day 8 复习）
# ============================================================
def trim_messages(messages, keep_rounds):
    """
    保留 system prompt + 最近 keep_rounds 轮对话
    每轮对话 = 2 条消息（user + assistant）
    """
    # ← 实现裁剪逻辑

    if len(messages) <= 1 + keep_rounds * 2:
        return messages # 不需要裁剪，直接返回原 messages
    else:
        # 保留 system prompt + 最近 keep_rounds 轮对话
        return [messages[0]] + messages[-keep_rounds*2:]
    


# ============================================================
# TODO 3：流式输出（Day 9 复习）
# ============================================================
def stream_print(stream):
    """
    流式输出 API 返回的内容，带打字机效果
    返回：拼接后的完整回答字符串
    """
    # ← 遍历 chunk，逐字输出 + 拼接完整内容
    full_response = ""
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
            full_response += delta.content
    print()  # 最后换行 
    return full_response


# ============================================================
# TODO 4：处理特殊命令
# ============================================================
def handle_command(user_input, messages):
    """
    处理特殊命令：
      /exit  → 退出程序
      /clear → 清空对话历史（保留 system prompt）

    返回：(should_continue, messages)
      should_continue: True=继续对话, False=退出
      messages: 更新后的消息列表
    """
    # ← 实现命令处理
    if user_input.lower() == "/exit":
        print("再见!")
        return False, messages
    elif user_input.lower() == "/clear":
        return True, [messages[0]]  # 保留 system prompt，清空其他消息
    else:
        return True, messages  # 不处理，继续对话
    


# ============================================================
# TODO 5：主循环 —— 拼装所有零件
# ============================================================
def main():
    """主对话循环"""
    # 1. 初始化 messages（只包含 system prompt）
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
    ]

    print("=" * 60)
    print("🤖 AI 问答工具（基于 DeepSeek）")
    print("=" * 60)
    print("命令：/exit 退出 | /clear 清空对话")
    print(f"System Prompt：{SYSTEM_PROMPT}")
    print(f"Temperature：{TEMPERATURE} | 窗口阈值：{WINDOW_SIZE} tokens")
    print()

    # ← 主循环
    while True:
        # 2. 获取用户输入
        try:
            user_input = input("你：").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见！")
            break

        if not user_input:
            continue

        # 3. 检查特殊命令
        should_continue, messages = handle_command(user_input, messages)
        if not should_continue:
            break
        if user_input.startswith("/"):
            continue  # 特殊命令处理后，直接进入下一轮

        # 4. 添加用户消息到 messages
        messages.append({"role": "user", "content": user_input})

        # 5. 检查 token 数，超出阈值则裁剪
        if count_tokens(messages) > WINDOW_SIZE:
            messages = trim_messages(messages, KEEP_ROUNDS)
     

        # 6. 调用 API（stream=True）
        stream = client.chat.completions.create(
            model = "deepseek-chat",
            max_tokens = MAX_TOKENS,
            temperature = TEMPERATURE,
            stream = True,
            messages = messages,
        )

        # 7. 流式输出
        full_response = stream_print(stream)

        # 8. 把 AI 回答加入 messages
        messages.append({"role": "assistant", "content": full_response})


if __name__ == "__main__":
    main()
