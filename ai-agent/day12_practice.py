"""
Day 12 练习：引用 ai_utils 模块
=================================
要求：只用 ai_utils 提供的函数，完成以下 3 道题。
不可直接写 requests.post() 或重复定义已有的函数。
"""
from ai_utils import chat, chat_with_retry, chat_stream, count_tokens


# ============================================================
# 题 1：批量问答
# ============================================================
# 下面有 5 个问题，用 chat() 依次提问，打印每个问题的回答（限前 40 字）。
# 如果某个问题调用失败，打印 "❌ 失败：错误信息" 并继续下一个。
#
# 提示：
#   chat() 返回 (bool, str)，ok 是 True/False

questions = [
    "Python的列表和元组有什么区别？",
    "什么是装饰器？",
    "with语句的作用是什么？",
    "解释GIL是什么",
    "Python如何实现单例模式？",
]

print("=" * 50)
print("题 1：批量问答")
print("=" * 50)

for q in questions:
    ok, answer = chat(q)
    if ok:
        print(f"✅ {answer[:40]}...")
    else:
        print(f"❌ 失败：{answer}")



print()

# ============================================================
# 题 2：带重试的翻译器
# ============================================================
# 用 chat_with_retry() 把下面三句话翻译成英文。
# 翻译失败时打印错误信息。
#
# 提示：
#   构造 messages 时加 system prompt："你是一个翻译助手，只返回翻译结果，不要解释"

texts = [
    "今天天气真好",
    "Python是一门优雅的编程语言",
    "人工智能正在改变世界",
]

SYSTEM_PROMPT = "你是一个翻译助手，把用户输入翻译成英文，只返回翻译结果，不要解释"

print("=" * 50)
print("题 2：带重试的翻译器")
print("=" * 50)

for test in texts:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": test},
    ]
    ok, result = chat_with_retry(messages)
    if ok:
        print(f"✅ {result}")
    else:
        print(f"❌ 失败：{result}")


print()

# ============================================================
# 题 3：统计对话的 token 消耗
# ============================================================
# 用 chat_stream() 依次问下面 3 个问题，收集完整的回答。
# 每次回答后，用 count_tokens() 统计当前对话历史的总 token 数并打印。
# 注意：messages 列表要保留完整对话历史（system + 所有 user + 所有 assistant）

messages = [
    {"role": "system", "content": "你是一个Python教学助手，用中文回答，简洁明了"},
]
questions_3 = [
    "什么是变量？",
    "变量的命名规则是什么？",
    "如何交换两个变量的值？",
]

print("=" * 50)
print("题 3：统计对话的 token 消耗")
print("=" * 50)

for q in questions_3:
    messages.append({"role": "user", "content": q})
    ok, answer = chat_stream(messages)
    if not ok:
        print(f"❌ 失败：{answer}")
        break
    messages.append({"role": "assistant", "content": answer})

    token_count = count_tokens(messages)
    print(f"✅ 回答：{answer[:40]}...  （总 token 数：{token_count}）")



print()
print("练习完成！")
