"""
Day 27：mock 入门 — 用假对象替代真实依赖
=============================================
核心概念：
1. Mock() 创建一个万能假对象 — 任何属性/方法都存在
2. return_value — 假对象被调用时返回什么
3. 断言调用 — 验证假对象被如何调用过

学完今天你能：
- 测试 AI 调用函数而不消耗 API 额度
- 伪造网络请求函数的返回值
"""

import pytest
from unittest.mock import Mock


# ============================================================
# 第一部分：Mock 基础 — 什么是 Mock？
# ============================================================

print("=" * 50)
print("第一部分：Mock 基础")
print("=" * 50)

# Mock() 像一个"万能替身"，你可以：
fake = Mock()

# 1. 把它当函数调用
result = fake("hello")
print(f"调用 Mock 返回: {result}")       # <Mock name='mock()' id=...>

# 2. 访问任意属性都不报错
print(f"假属性: {fake.any_property}")    # <Mock name='mock.any_property' id=...>

# 3. 调用任意方法都不报错
print(f"假方法: {fake.any_method()}")    # <Mock name='mock.any_method()' id=...>

# 这就是 Mock 的核心：**永不报错，什么都接受**


# ============================================================
# 第二部分：return_value — 让假对象返回你指定的值
# ============================================================

print()
print("=" * 50)
print("第二部分：return_value")
print("=" * 50)

# 2.1 基本用法
fake_ai = Mock()
fake_ai.return_value = "你好，我是 Mock AI 的回复"

response = fake_ai("什么是 Python？")
print(f"假 AI 回复: {response}")
# → 你好，我是 Mock AI 的回复
# 不管传什么参数，都返回同样的值

# 2.2 模拟真实场景：假 AI 聊天函数
def chat_with_ai(client, message):
    """真正的聊天函数 — 但我们测试时不传真实 client"""
    response = client.chat(message)       # client 是假对象！
    return f"AI 说: {response}"

# 创建假 client
fake_client = Mock()
fake_client.chat.return_value = "Python 是一门很好的语言"

result = chat_with_ai(fake_client, "介绍 Python")
print(f"聊天结果: {result}")
# → AI 说: Python 是一门很好的语言

# 我们没有调用任何真实 API！


# ============================================================
# 第三部分：Mock 的"记忆" — 断言调用历史
# ============================================================

print()
print("=" * 50)
print("第三部分：断言调用历史")
print("=" * 50)

fake_db = Mock()
fake_db.save.return_value = "保存成功"

# 模拟业务逻辑
fake_db.save("user001", name="张三")
fake_db.save("user002", name="李四")

# 断言：被调用了
print(f"save 被调用了 {fake_db.save.call_count} 次")  # 2

# 断言：被调用过
assert fake_db.save.called == True

# 断言：最后一次调用的参数
print(f"最后一次调用参数: {fake_db.save.call_args}")      # args=('user002',), kwargs={'name': '李四'}

# 断言：所有调用的参数列表
print(f"所有调用: {fake_db.save.call_args_list}")

# 断言：是否以特定参数被调用过
fake_db.save.assert_called_with("user002", name="李四")    # ✅ 通过
# fake_db.save.assert_called_with("user999")               # ❌ 会报 AssertionError


# ============================================================
# TODO 1：创建一个假天气 API
# ============================================================
# 要求：
# 1. 创建一个 Mock 对象 fake_weather
# 2. 设置它的 get_weather 方法的 return_value 为 {"temp": 25, "status": "晴"}
# 3. 调用 fake_weather.get_weather("北京") 两次
# 4. 断言 get_weather 被调用了 2 次
# 5. 打印调用次数验证

print()
print("=" * 50)
print("TODO 1：假天气 API")
print("=" * 50)

# ← 写代码：
fake_weather = Mock()
fake_weather.get_weather.return_value = {"temp": 25, "status": "晴"}

fake_weather.get_weather("北京")
fake_weather.get_weather("北京")
print(f"get_weather 被调用了 {fake_weather.get_weather.call_count} 次")  # 2
fake_weather.get_weather.assert_called_with("北京")  # ✅ 通过


# ============================================================
# TODO 2：测试一个发送通知的函数（不真发）
# ============================================================
# 场景：有一个 send_notification 函数，它会调用外部通知服务的 send 方法
# 测试时我们不想真发通知

def send_notification(service, user, message):
    """发送通知 — service 是外部通知服务"""
    result = service.send(user=user, message=message)
    return f"通知结果: {result}"

print()
print("=" * 50)
print("TODO 2：测试通知函数")
print("=" * 50)

# ← 写代码：
# 1. 创建 Mock 对象 fake_service
# 2. 设置 fake_service.send.return_value = "发送成功"
# 3. 调用 send_notification(fake_service, "张三", "你好")
# 4. 断言 service.send 被调用了 1 次
# 5. 断言参数正确：user="张三", message="你好"
fake_service = Mock()
fake_service.send.return_value = "发送成功"
result = send_notification(fake_service, "张三", "你好")
print(result)  # 通知结果: 发送成功
print(f"send 被调用了 {fake_service.send.call_count} 次")  # 1
fake_service.send.assert_called_with(user="张三", message="你好")  # ✅ 通过


# ============================================================
# TODO 3：模拟 AI 对话函数并验证
# ============================================================
# 场景：translate 函数调用 AI 做翻译

def translate(ai_client, text, target_lang):
    """使用 AI 翻译文本"""
    prompt = f"把 '{text}' 翻译成 {target_lang}"
    result = ai_client.chat(prompt)
    return result

print()
print("=" * 50)
print("TODO 3：模拟 AI 翻译")
print("=" * 50)

# ← 写代码：
# 1. 创建 Mock 对象 mock_ai
# 2. 设置 mock_ai.chat.return_value = "Hello, how are you?"
# 3. 调用 translate(mock_ai, "你好，你好吗？", "英语")
# 4. 打印返回结果
# 5. 断言 ai_client.chat 被调用了 1 次
# 6. 断言传递给 chat 的参数中包含 "你好" 和 "英语"
mock_ai = Mock()
mock_ai.chat.return_value = "Hello, how are you?"
translation = translate(mock_ai, "你好，你好吗？", "英语")
print(f"翻译结果: {translation}")  # Hello, how are you?
print(f"chat 被调用了 {mock_ai.chat.call_count} 次")  # 1
mock_ai.chat.assert_called_with("把 '你好，你好吗？' 翻译成 英语")  # ✅ 通过


# ============================================================
# TODO 4（思考题）：mock 到底 mock 什么？
# ============================================================
# 问题 1：为什么要 mock，而不是直接在测试里用真实 API？
#   提示：想想测试的三个特性：快、稳定、便宜
# 答案：使用真实 API 可能慢、可能不稳定（网络问题、API 限额等），还可能产生费用（调用付费 API）。Mock 可以让测试快速、稳定且免费。
# 问题 2：Mock 对象和普通 Python 对象有什么区别？
#   提示：Mock 有 call_count、assert_called_with 等特殊能力
# 答案：Mock 对象是专门为测试设计的，它可以记录调用历史、断言调用参数等，而普通 Python 对象没有这些功能。
# 问题 3：return_value 设置的是什么？没有设置时会返回什么？
# 答案：return_value 设置的是 Mock 对象被调用时返回的值。没有设置时，会返回一个特殊的 Mock 对象。
#


# ============================================================
# 运行
# ============================================================
# python day27_mock_intro.py
