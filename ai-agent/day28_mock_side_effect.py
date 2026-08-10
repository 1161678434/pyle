"""
Day 28：mock 实战 — side_effect + 深度断言
=============================================
核心概念：
1. side_effect 作为列表 — 每次调用依次返回不同值
2. side_effect 作为函数 — 根据输入动态返回
3. side_effect 作为异常 — 模拟出错场景
4. 深度断言 — assert_called_once_with、assert_any_call、assert_not_called

学完今天你能：
- 模拟"第1次成功，第2次失败"的重试场景
- 根据输入动态生成 mock 返回值
- 测试异常处理逻辑（不真去断开网线）
"""

import pytest
from unittest.mock import Mock


# ============================================================
# 第一部分：side_effect 作为列表 — 每次调用不同返回值
# ============================================================

print("=" * 50)
print("第一部分：side_effect 列表模式")
print("=" * 50)

# 场景：模拟一个不稳定的 AI API
#   第1次调用 → 成功返回
#   第2次调用 → 超时错误（我们后面学异常模式）
#   第3次调用 → 又成功了

unstable_api = Mock()
unstable_api.chat.side_effect = [
    "你好！我是 AI",          # 第 1 次调用返回这个
    "抱歉，我不明白",          # 第 2 次调用返回这个
    "再见！",                 # 第 3 次调用返回这个
]

print(f"第1次: {unstable_api.chat('hi')}")      # 你好！我是 AI
print(f"第2次: {unstable_api.chat('hi')}")      # 抱歉，我不明白
print(f"第3次: {unstable_api.chat('hi')}")      # 再见！
print(f"统计调用次数: {unstable_api.chat.call_count}")  # 3


# ⚠️ 第4次会怎样？—— 列表用完了，会报 StopIteration
# print(unstable_api.chat('hi'))  # StopIteration


# ============================================================
# 第二部分：side_effect 作为函数 — 根据输入动态返回
# ============================================================

print()
print("=" * 50)
print("第二部分：side_effect 函数模式")
print("=" * 50)

# 场景：模拟翻译 API — 不同语言返回不同结果

def fake_translate(text, target_lang):
    """假的翻译函数 — 根据参数决定返回值"""
    translations = {
        ("你好", "英语"): "Hello",
        ("你好", "日语"): "こんにちは",
        ("你好", "韩语"): "안녕하세요",
    }
    return translations.get((text, target_lang), f"[{target_lang}翻译: {text}]")

translate_api = Mock()
translate_api.translate.side_effect = fake_translate  # 指向真实函数

print(translate_api.translate("你好", "英语"))  # Hello
print(translate_api.translate("你好", "日语"))  # こんにちは
print(translate_api.translate("你好", "韩语"))  # 안녕하세요
print(translate_api.translate("你好", "法语"))  # [法语翻译: 你好]

# 区别 return_value 和 side_effect 函数：
# - return_value：不管传什么参数，永远返回同一个值
# - side_effect 函数：可以根据传入的参数，返回不同的值

# 推荐用 lambda 简化简单逻辑：
simple_mock = Mock()
simple_mock.process.side_effect = lambda x: f"处理了: {x}"
print(simple_mock.process("数据A"))  # 处理了: 数据A
print(simple_mock.process("数据B"))  # 处理了: 数据B


# ============================================================
# 第三部分：side_effect 抛出异常 — 模拟错误场景
# ============================================================

print()
print("=" * 50)
print("第三部分：side_effect 异常模式")
print("=" * 50)

# 场景：模拟网络超时，测试重试逻辑
# 设定 side_effect 为异常类或异常实例

unreliable_service = Mock()
unreliable_service.fetch_data.side_effect = ConnectionError("网络超时，请重试")

# 调用时会抛出异常
try:
    unreliable_service.fetch_data("url")
except ConnectionError as e:
    print(f"捕获到异常: {e}")  # 网络超时，请重试


# ============================================================
# 第四部分：深度断言 — 更多验证方法
# ============================================================

print()
print("=" * 50)
print("第四部分：深度断言方法")
print("=" * 50)

payment_mock = Mock()

# 模拟支付流程
payment_mock.pay(amount=100, currency="CNY")
payment_mock.pay(amount=200, currency="USD")
payment_mock.refund(order_id="ORD-001")

print(f"pay 被调用了 {payment_mock.pay.call_count} 次")  # 2

# assert_called_once_with — 断言只被调用1次，且参数完全匹配
payment_mock.refund.assert_called_once_with(order_id="ORD-001")  # ✅

# assert_any_call — 断言至少有一次以此参数被调用（不管其他调用）
payment_mock.pay.assert_any_call(amount=100, currency="CNY")     # ✅
payment_mock.pay.assert_any_call(amount=200, currency="USD")     # ✅

# assert_not_called — 断言从未被调用
payment_mock.cancel.assert_not_called()  # ✅ cancel 从未被调用


# ============================================================
# TODO 1：模拟重试机制 — 前2次失败，第3次成功
# ============================================================
# 场景：call_with_retry 函数调用 API，失败后重试，最多3次

def call_with_retry(api, data):
    """用重试机制调用 API"""
    for attempt in range(3):
        try:
            result = api.send(data)
            print(f"  第 {attempt+1} 次: 成功 → {result}")
            return result
        except Exception as e:
            print(f"  第 {attempt+1} 次: 失败 → {e}")
    return "全部重试失败"

print()
print("=" * 50)
print("TODO 1：模拟重试机制")
print("=" * 50)

# ← 写代码：
# 1. 创建 Mock 对象 unreliable_api
# 2. 设置 send.side_effect，前2次抛 ConnectionError，第3次返回 "数据已送达"
# 3. 调用 call_with_retry(unreliable_api, "重要数据")
# 4. 打印结果，预期看到前2次失败，第3次成功
# 5. 断言 send 被调用了 3 次

unreliable_api = Mock()
unreliable_api.send.side_effect = [
    ConnectionError("网络超时，请重试"),  # 第 1 次调用抛出这个异常
    ConnectionError("网络超时，请重试"),  # 第 2 次调用抛出这个异常
    "数据已送达",                      # 第 3 次调用返回这个结果
]
result = call_with_retry(unreliable_api, "重要数据")
print(f"最终结果: {result}") # 最终结果: 数据已送达
print(f"send 被调用了 {unreliable_api.send.call_count} 次")  # 3
assert unreliable_api.send.call_count == 3


# ============================================================
# TODO 2：模拟更真实的 AI 聊天 — 根据消息内容返回不同回复
# ============================================================

def ai_qa_bot(ai_client, question):
    """AI 问答机器人：调用 AI，返回答案"""
    answer = ai_client.ask(question)
    return f"回答: {answer}"

print()
print("=" * 50)
print("TODO 2：真实 AI 问答模拟")
print("=" * 50)

# ← 写代码：
# 1. 写一个 fake_answer 函数，接收 question 参数
#    - 如果 question 包含 "天气" → 返回 "今天是晴天"
#    - 如果 question 包含 "时间" → 返回 "现在是下午3点"
#    - 其他 → 返回 "我不知道"
# 2. 创建 Mock 对象，设置 ask.side_effect = fake_answer
# 3. 用 ai_qa_bot 分别问 "今天天气怎么样？"、"现在几点了？"、"你是谁？"
# 4. 打印每个回答
# 5. 断言 ask 被调用了 3 次
# 6. 用 assert_any_call 验证 "今天天气怎么样？" 被调用过

# ← 写代码：
def fake_answer(question):
    """根据问题内容返回不同的答案"""
    if "天气" in question:
        return "今天是晴天"
    elif "时间" in question or "几点" in question:
        return "现在是下午3点"
    else:
        return "我不知道"

mock_ai = Mock()
mock_ai.ask.side_effect = fake_answer

print(ai_qa_bot(mock_ai, "今天天气怎么样？"))
print(ai_qa_bot(mock_ai, "现在几点了？"))
print(ai_qa_bot(mock_ai, "你是谁？"))

print(f"调用次数: {mock_ai.ask.call_count}")
assert mock_ai.ask.call_count == 3

mock_ai.ask.assert_any_call("今天天气怎么样？")
print("✅ TODO 2 全部通过")

# ============================================================
# TODO 3：异常安全函数 — 测试出错时是否有兜底逻辑
# ============================================================

def safe_fetch(fetcher, url):
    """安全的数据获取：出错时返回默认值而不是崩溃"""
    try:
        data = fetcher.get(url)
        return f"数据: {data}"
    except Exception as e:
        return f"获取失败，使用默认数据（原因: {e}）"

print()
print("=" * 50)
print("TODO 3：异常安全函数")
print("=" * 50)

# ← 写代码：
# 1. 创建 Mock 对象 bad_fetcher
# 2. 设置 bad_fetcher.get.side_effect = TimeoutError("请求超时")
# 3. 调用 safe_fetch(bad_fetcher, "http://example.com")
# 4. 打印结果（应该返回默认数据而不是崩溃）
# 5. 断言 get 被调用了 1 次
bad_fetcher = Mock() 
bad_fetcher.get.side_effect = TimeoutError("请求超时")
result = safe_fetch(bad_fetcher, "http://example.com")
print(f"✅返回结果，{result}")
assert bad_fetcher.get.call_count == 1



# ============================================================
# TODO 4（思考题）：side_effect vs return_value
# ============================================================
# 问题 1：return_value 和 side_effect 有什么区别？什么时候用哪个？
# 问题 2：如果同时设置 return_value 和 side_effect，谁会生效？
# 问题 3：side_effect 列表用完了会发生什么？怎么避免？

"""
# 答案提示：

# 1. return_value：每次调用返回相同的值
#    side_effect：可以返回不同值、动态生成、或抛异常
#    用 return_value 当：每次调用返回值一样
#    用 side_effect 当：需要不同返回值、或要模拟异常

# 2. side_effect 优先！如果同时设置，return_value 被忽略。
#    实际上设置 side_effect 会清除 return_value，反之亦然。

# 3. side_effect 列表用完后抛出 StopIteration。
#    避免方法：
#    - 确保列表长度 >= 预期调用次数
#    - 使用 side_effect 函数模式（永不枯竭）
#    - 使用 itertools.cycle(["成功", "失败"]) 循环返回
"""


# ============================================================
# 运行
# ============================================================
# python day28_mock_side_effect.py
