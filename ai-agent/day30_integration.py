"""
Day 30：组合实战 — fixture + mock + patch 测试 AI 调用函数
=============================================================
前三天的能力整合：
  Day 27：Mock — 创建假对象
  Day 28：side_effect — 模拟多次调用/异常
  Day 29：patch — 替换真实依赖，不烧 API 额度
  Day 30：三合一 — fixture 准备数据，mock 伪造行为，patch 拦截外部调用

学完今天你能：
- 完整测试一个调用 AI 的函数，0 元成本
- 用 fixture 管理 mock 对象的生命周期
- 区分"用 mock 模拟成功"和"用 mock 模拟失败"两种测试场景

真实场景：你公司有个 ai_utils.py，里面有个函数调 OpenAI API。
老板说：每跑一次测试烧一分钱，100 个用例就是 1 块钱，CI 一天跑 50 次就是 50 块。
你的任务：写测试，保证质量，不烧钱。
"""

import pytest
from unittest.mock import Mock, patch

# ============================================================
# 模拟你的公司代码：ai_utils.py（不能改）
# ============================================================

import time

def call_ai_api(prompt: str) -> dict:
    """
    模拟调用 AI API — 每次调用消耗 token（= 烧钱）
    返回：{"status": "success", "content": str, "tokens_used": int}
    """
    time.sleep(0.5)  # 模拟网络延迟
    return {
        "status": "success",
        "content": f"AI 对 '{prompt}' 的回复",
        "tokens_used": len(prompt) * 2,
    }


def smart_reply(user_message: str) -> str:
    """
    智能回复函数 — 内部调用 call_ai_api
    这是你要测试的函数，你不能改它
    """
    response = call_ai_api(user_message)
    if response["status"] == "success":
        return f"🤖 {response['content']}"
    return "抱歉，AI 暂时不可用"


def retry_reply(user_message: str, max_retries: int = 3) -> str:
    """
    带重试的智能回复 — 失败后自动重试
    """
    for attempt in range(max_retries):
        try:
            response = call_ai_api(user_message)
            if response["status"] == "success":
                return f"🤖 {response['content']} (第{attempt+1}次成功)"
        except Exception:
            continue
    return "多次重试后仍失败"


# ============================================================
# TODO 1：fixture + patch 组合 — 测试成功场景
# ============================================================

print("=" * 50)
print("TODO 1：fixture + patch — 不烧钱测 AI 调用")
print("=" * 50)

# 场景：测试 smart_reply，但不真调 call_ai_api

# 要求：
# 1. 写一个 fixture，返回一个配置好的 mock 对象：
#    mock_api.return_value = {"status": "success", "content": "这是Mock回复", "tokens_used": 10}
# 2. 写测试函数 test_smart_reply_success(mock_api)：
#    - 用 with patch(f'{__name__}.call_ai_api', mock_api) 替换真实调用
#    - 调用 smart_reply("你好")
#    - 断言返回值包含 "Mock回复"
#    - 断言返回 "🤖" 打头
#    - 断言 mock_api 只被调用了 1 次

# ← 你的代码写在这里
@pytest.fixture
def mock_api():
    m = Mock()
    m.return_value = {"status": "success", "content": "这是Mock回复", "tokens_used": 10}
    return m

def test_smart_reply_success(mock_api):
    with patch(f'{__name__}.call_ai_api',mock_api) :
        result = smart_reply("你好")
        print(result)
        assert "Mock回复" in result
        assert result.startswith("🤖")
        mock_api.assert_called_once_with("你好")



# ============================================================
# TODO 2：fixture + side_effect — 测试重试逻辑
# ============================================================

print()
print("=" * 50)
print("TODO 2：fixture + side_effect — 测试重试")
print("=" * 50)

# 场景：retry_reply 会在失败后重试，最多 3 次
# 模拟：前 2 次抛异常，第 3 次成功

# 要求：
# 1. 写一个 fixture，返回一个配置好 side_effect 的 mock：
#    第 1 次 → 抛 ConnectionError("超时")
#    第 2 次 → 抛 ConnectionError("超时")
#    第 3 次 → 返回 {"status": "success", "content": "重试成功", "tokens_used": 5}
# 2. 写测试函数 test_retry_reply(mock_api)：
#    - patch call_ai_api
#    - 调用 retry_reply("测试")
#    - 断言返回 "🤖 重试成功 (第3次成功)"
#    - 断言 mock_api 被调用了 3 次

# ← 你的代码写在这里
@pytest.fixture
def unreliable_api():
    unreliable_api = Mock()
    unreliable_api.side_effect = [
    ConnectionError("网络超时，请重试"),  # 第 1 次调用抛出这个异常
    ConnectionError("网络超时，请重试"),  # 第 2 次调用抛出这个异常
    {"status": "success", "content": "重试成功", "tokens_used": 5},                      # 第 3 次调用成功
]
    return unreliable_api

def test_retry_reply(unreliable_api):
    with patch(f'{__name__}.call_ai_api', unreliable_api):
        result = retry_reply("测试")
        print(result)
        assert result == "🤖 重试成功 (第3次成功)"
        assert unreliable_api.call_count == 3
        


# ============================================================
# TODO 3：两个测试场景对比 — 同一个函数，不同 mock 配置
# ============================================================

print()
print("=" * 50)
print("TODO 3：成功 vs 失败 — 同一个 smart_reply")
print("=" * 50)

# smart_reply 有两行分支代码你没测到：
#   if response["status"] == "success":  ← TODO 1 测了
#       return f"🤖 {response['content']}"
#   return "抱歉，AI 暂时不可用"           ← 还没测！

# 要求：再写一个测试 test_smart_reply_failure()：
#   - mock 的 return_value 里 status = "error"
#   - 断言返回 "抱歉，AI 暂时不可用"
#   - 不需要 fixture，直接手写 mock（对比 fixture 的用法）

# ← 你的代码写在这里
def test_smart_reply_failure():
    m = Mock()
    m.return_value = {"status": "error", "content": ""}
    with patch(f"{__name__}.call_ai_api", m):
        result = smart_reply("疯了疯了")
        print(result)
        assert result == "抱歉，AI 暂时不可用"

# ============================================================
# 思考题
# ============================================================
# 问题 1：TODO 2 的 fixture 用了 side_effect 列表，如果重试次数改成 5 会怎样？
# 答：第四次的时候就抛异常
# 问题 2：什么时候把 mock 放 fixture 里，什么时候直接写在测试函数里？
# 答：多个用例公用就放在fixture 局部使用就放在函数里面
# 问题 3：如果 call_ai_api 在另一个文件 ai_utils.py 里，patch 路径怎么写？
# 答：patch('ai_utils.call_ai_api')

"""
# 提示：
# 1. 列表只有 3 个元素，第 4 次调用抛 StopIteration
# 2. 多个测试共用同一个 mock 配置 → fixture；只有这个测试用 → 直接写
# 3. patch('ai_utils.call_ai_api') —— 路径是被测代码 import 的位置
"""


# ============================================================
# 运行
# ============================================================
# pytest day30_integration.py -v
