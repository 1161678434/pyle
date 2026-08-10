"""
Day 15：pytest 入门 —— 写出你的第一个测试
============================================
之前都是写"功能代码"，今天开始写"测试代码"——
用 pytest 验证你的代码行为是否符合预期。

核心概念：
- 测试就是"自动检查"，不需要手动 print 看结果
- assert：如果后面的表达式为 True → 通过，False → 失败
- pytest 自动发现 test_ 开头的函数并执行
"""

# ============================================================
# 第一部分：认识 assert —— 测试的核心
# ============================================================
# assert 就是"我断言这件事是真的"，如果不是，就报错。
#
#   assert 2 + 2 == 4     # True  → 安静通过
#   assert 2 + 2 == 5     # False → AssertionError
#
# 和 if 的区别：
#   if 2 + 2 != 5:        # 你要自己写"报错"逻辑
#       print("错了")      # 手动、零散、不可重复
#
#   assert 2 + 2 == 5     # pytest 自动报错、自动统计


# ============================================================
# TODO 1：写一个简单函数 + 一个测试函数
# ============================================================

def add(a, b):
    """一个简单的加法函数"""
    # ← 写代码：返回 a + b
    add_result = a+b
    return add_result


# 测试函数：必须以 test_ 开头，pytest 才能自动发现
def test_add_basic():
    """测试 add 函数的基本功能"""
    # ← 写代码：用 assert 调用 add(2, 3)，断言结果等于 5
    assert add(2, 3) == 5


def test_add_negative():
    """测试负数加法"""
    # ← 写代码：断言 add(-1, -2) 等于 -3
    assert add(-1, -2) == -3


def test_add_zero():
    """测试加零"""
    # ← 写代码：断言 add(5, 0) 等于 5
    assert add(5, 0) == 5


# ============================================================
# TODO 2：写一个更实用的函数 + 测试
# ============================================================

def extract_content(api_response):
    """
    从 AI API 响应中提取 content 字段。
    这是你 ai_utils.py 里实际做的事情！

    api_response 结构：
    {
        "choices": [
            {"message": {"content": "你好！"}}
        ]
    }
    返回：message 的 content 字段
    如果没有这个字段，返回 None
    """
    # ← 写代码：
    # 提示：用 try/except 安全取值
    try:
        return api_response["choices"][0]["message"]["content"]
    except (KeyError, IndexError):
        return None
    


def test_extract_normal():
    """测试正常提取 content"""
    response = {
        "choices": [
            {"message": {"content": "你好！"}}
        ]
    }
    # ← 断言 extract_content(response) 等于 "你好！"
    assert extract_content(response) == "你好！"

def test_extract_empty():
    """测试空 response 的情况"""
    # ← 断言 extract_content({}) 返回 None
    assert extract_content({}) is None

def test_extract_no_content():
    """测试有 choices 但没有 content 字段的情况"""
    response = {"choices": [{"message": {}}]}
    # ← 断言 extract_content(response) 返回 None
    assert extract_content(response) is None


# ============================================================
# TODO 3（思考题）：为什么测试函数命名必须是 test_ 开头？
# ============================================================
# 答：pytest 是通过反射机制自动发现测试函数的，它默认只会执行以 test_ 开头的函数，这样可以区分测试函数和普通函数。如果不遵守这个命名规则，pytest 就无法识别你的测试函数，也就不会执行它们了。
#


# ============================================================
# 运行说明
# ============================================================
# 在终端运行：
#   pytest day15_pytest_intro.py          # 运行本文件所有测试
#   pytest day15_pytest_intro.py -v       # 详细模式，显示每个测试名
#   pytest day15_pytest_intro.py -v -s    # -s 显示 print 输出

