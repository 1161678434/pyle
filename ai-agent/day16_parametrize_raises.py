"""
Day 16：异常测试 + 参数化
===========================
昨天写的是"正常情况"的测试。但真实代码里有大量异常情况——
函数应该抛异常、抛什么异常、异常信息是什么，这些也要测。

今天两个新武器：
1. pytest.raises() — 断言某段代码"应该抛异常"
2. @parametrize    — 一份测试逻辑，多组数据，自动展开
"""
from operator import add

import pytest


# ============================================================
# 第一部分：pytest.raises() —— 测试异常
# ============================================================
# 之前你写 extract_content({}) 返回 None 来回避异常。
# 但有些场景下，函数就应该抛出异常让调用方知道出错了。
#
# 用法：
#   with pytest.raises(异常类型):
#       会抛异常的代码


# ============================================================
# TODO 1：修正 divide 函数 + 写异常测试
# ============================================================

def divide(a, b):
    """
    除法函数。
    要求：除数为 0 时抛出 ValueError，错误信息为 "除数不能为零"
    """
    # ← 写代码：如果 b == 0，抛出 ValueError
    if b == 0:
        raise ValueError("除数不能为零")
    return a / b


def test_divide_normal():
    """正常除法"""
    assert divide(10, 2) == 5


def test_divide_negative():
    """负数除法"""
    assert divide(-10, 2) == -5


def test_divide_by_zero():
    """测试除数为零时抛出 ValueError"""
    # ← 写代码：用 pytest.raises(ValueError) 包裹 divide(10, 0)
    with pytest.raises(ValueError):
        divide(10, 0)


def test_divide_by_zero_message():
    """测试异常信息是否匹配"""
    # ← 写代码：用 pytest.raises(ValueError, match="除数不能为零")
    # match 参数可以匹配异常信息中的关键词
    with pytest.raises(ValueError, match="除数不能为零"):
        divide(10, 0)


# ============================================================
# TODO 2：测试 AI 相关的异常场景
# ============================================================
# 把 Day 15 的 extract_content 改一下版：
# 对于空响应，不返回 None，而是抛出 ValueError

def extract_content_strict(api_response):
    """
    严格版的 extract_content：
    - 正常返回 content 字符串
    - 如果取不到 content，抛出 ValueError，说明原因
    """
    # ← 写代码：
    # try 取值，如果成功就 return
    # 如果 KeyError 或 IndexError，raise ValueError("响应中没有 content 字段")
    try:
        return api_response["choices"][0]["message"]["content"]
    except (KeyError, IndexError):
        raise ValueError("响应中没有 content 字段")

def test_extract_strict_normal():
    """正常情况"""
    response = {"choices": [{"message": {"content": "你好！"}}]}
    assert extract_content_strict(response) == "你好！"


def test_extract_strict_empty():
    """空响应 → 应抛出 ValueError"""
    # ← 写代码：断言 extract_content_strict({}) 抛出 ValueError
    with pytest.raises(ValueError):
        extract_content_strict({})


def test_extract_strict_wrong_structure():
    """结构不对 → 应抛出 ValueError"""
    response = {"error": "not found"}
    # ← 写代码
    with pytest.raises(ValueError, match="没有 content 字段"):
        extract_content_strict(response)

# ============================================================
# TODO 3：@parametrize —— 一组数据跑多个用例
# ============================================================
# 昨天 test_add_basic、test_add_negative、test_add_zero 三个函数
# 结构完全一样，只是输入输出不同。可以用 parametrize 合并成一个。

# 语法：
# @pytest.mark.parametrize("参数名1,参数名2", [
#     (值1, 值2),
#     (值3, 值4),
# ])
# def test_xxx(参数名1, 参数名2):
#     assert 函数(参数名1) == 参数名2

# ← 写代码：用 parametrize 把下面三个测试合并成一个
# pytest 会自动把每组数据展开为独立的测试用例
@pytest.mark.parametrize("a,b,expected", [
    (2, 3, 5),
    (-1, -2, -3),
    (5, 0, 5)
])

def test_add_parametrize(a, b, expected):
    """测试 add 函数的多组输入输出"""
    assert add(a, b) == expected



# ============================================================
# TODO 4：parametrize 实战 —— extract_content 多场景
# ============================================================
# 用 parametrize 测试 extract_content（返回 None 版本）的多种场景

def extract_content(api_response):
    """Day 15 的版本：出错返回 None"""
    try:
        return api_response["choices"][0]["message"]["content"]
    except (KeyError, IndexError):
        return None


# ← 写代码：用 @parametrize 定义多组 (输入, 期望输出)，
# 覆盖：正常返回、空dict、缺choices、缺content、空列表

# 提示：参数名可以叫 response 和 expected
@pytest.mark.parametrize("response,expected", [
    ({"choices": [{"message": {"content": "你好"}}]}, "你好"),
    ({}, None),
    ({"error": "not found"}, None),
    ({"choices":[{"message": {}}]}, None),
    ({"choices": []}, None)])
def test_extract_content_various(response, expected):
    """测试 extract_content 的多种输入输出场景"""
    assert extract_content(response) == expected


# ============================================================
# TODO 5（思考题）
# ============================================================
# 问题 1：pytest.raises() 里面放一段不抛异常的代码会怎样？
#答：测试会失败，pytest 会报告"Expected ValueError to be raised, but it was not raised"，意思是预期应该抛出 ValueError，但实际上没有抛出任何异常，所以测试不通过了。
# 问题 2：什么时候该返回 None，什么时候该抛异常？
#    提示：想想 extract_content 和 extract_content_strict 的使用场景
#答：如果函数的调用者需要知道出错的具体原因，或者需要区分不同类型的错误，那么抛异常更合适，因为异常可以携带详细的错误信息和类型。而如果函数的调用者只关心结果是否存在，不需要知道具体的错误原因，那么返回 None 可能更方便，因为调用者可以直接检查返回值是否为 None 来判断是否成功了。总之，选择返回 None 还是抛异常，要根据函数的设计目的和使用场景来决定。
# 问题 3：parametrize 生成的测试用例名是什么样的？在终端跑一下看看。
#答：pytest 会根据测试函数的名字和参数值自动生成测试用例名，通常格式是 test_函数名[参数值1-参数值2-...]，比如 test_extract_content_various[{'choices': [{'message': {'content': '你好'}}}-你好]、test_extract_content_various[{}-None] 等等，这样在运行测试时就能清楚地看到每个测试用例对应的输入参数和期望输出了。


# ============================================================
# 运行
# ============================================================
# pytest day16_parametrize_raises.py -v

