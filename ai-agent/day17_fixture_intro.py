"""
Day 17：fixture 入门 —— 准备测试数据
=======================================
前两天写测试时，每个测试函数里都要自己构造数据。
比如 test_extract_normal 里手动拼一个 response dict。

当 10 个测试都用同一份数据时，重复就出现了。
fixture 就是解决这个问题的——把"准备数据"提取出来复用。

核心概念：
- fixture = 测试的"前置准备"，比如构造数据、创建临时文件
- pytest 自动把 fixture 的返回值注入到测试函数的参数里
"""

import pytest


# ============================================================
# 第一部分：认识 fixture —— 把数据提取出来
# ============================================================
# 没有 fixture 的写法（重复）：
#   def test_a():
#       data = {"name": "张三", "age": 25}
#       ...
#   def test_b():
#       data = {"name": "张三", "age": 25}   ← 和上面一模一样
#       ...
#
# 有 fixture 的写法：
#   @pytest.fixture
#   def user_data():
#       return {"name": "张三", "age": 25}
#
#   def test_a(user_data):    ← pytest 自动把 fixture 返回值传进来
#       ...
#   def test_b(user_data):    ← 每个测试拿到的是独立的副本
#       ...


# ============================================================
# TODO 1：写第一个 fixture + 使用它
# ============================================================

# ← 写代码：创建一个名为 sample_response 的 fixture
# 返回一个模拟的 AI API 响应 dict（和 Day 15 的结构一样）
# {
#     "choices": [{"message": {"content": "你好！"}}]
# }
@pytest.fixture
def sample_response():
    """一个简单的 fixture, 返回一个模拟的 API 响应"""
    return {
        "choices": [
            {"message": {"content": "你好！"}}
        ]
    }

def extract_content(api_response):
    """Day 15 的函数"""
    try:
        return api_response["choices"][0]["message"]["content"]
    except (KeyError, IndexError):
        return None


# ← 写代码：修改下面两个测试，用 fixture 参数代替手写的 response

def test_extract_normal_fixture(sample_response):
    """测试正常提取 content"""
    # ← 断言 extract_content(sample_response) 等于 "你好！"
    assert extract_content(sample_response) == "你好！"


def test_extract_normal_again_fixture(sample_response):
    """另一个测试，也用同样的数据"""
    # ← 断言 extract_content(sample_response) 等于 "你好！"
    assert extract_content(sample_response) == "你好！"




# ============================================================
# TODO 2：fixture 的执行时机 —— 每个测试拿到的是独立数据
# ============================================================
# 用 print 观察 fixture 被调用了多少次

# ← 写代码：创建一个叫 counter_data 的 fixture
# 里面放一个列表 data = []，append 一个数字，然后 print 提示
# 然后 return data
# 这样可以看出每个测试是否拿到了独立的数据

@pytest.fixture
def counter_data():
    """一个用来计数的 fixture，每次调用都会在列表里添加一个数字"""
    data = []
    data.append(1) # 每次调用都往列表里面添加一个数字
    print(f"counter_data fixture 被调用了，当前列表: {data}")
    return data 

# 测试 1 和测试 2 都用 counter_data fixture
def test_fixture_called_once(counter_data):
    """观察 fixture 的执行"""
    # ← 写你的断言：counter_data 应该只有一个元素
    assert len(counter_data) == 1

    


def test_fixture_called_again(counter_data):
    """第二个测试也用到同一个 fixture"""
    # ← 观察：这个测试拿到的 counter_data 是全新的还是同一个？
    assert len(counter_data) == 1
    # 如果每个测试拿到的都是独立的数据，那么这个断言应该通过

# ============================================================
# TODO 3（思考题）：fixture 和普通函数的区别
# ============================================================
# 问题 1：下面两种写法有什么不同？
#
#   A: @pytest.fixture
#      def data():
#          return {"key": "value"}
#
#      def test_a(data):   ← fixture 作为参数
#          ...
#
#   B: def get_data():
#          return {"key": "value"}
#
#      def test_a():
#          data = get_data()   ← 直接调用普通函数
#          ...
# 答：A 是 fixture 写法，pytest 会自动识别并在运行测试时调用它，把返回值注入到 test_a 的参数里。B 是普通函数写法，test_a 需要手动调用 get_data() 来获取数据。使用 fixture 的好处是更符合 pytest 的设计理念，可以更方便地管理测试依赖和共享数据，同时也能利用 pytest 的其他功能，比如 fixture 的作用域、自动清理等。而普通函数则需要自己管理调用时机和数据的生命周期。
#
# 问题 2：为什么 pytest 要根据参数名匹配 fixture，而不是根据类型？
#    提示：想想如果你有两个 fixture 都返回 dict，pytest 怎么区分？
# 答：pytest 根据参数名匹配 fixture 是为了让测试函数能够明确地指定它需要哪个 fixture。如果 pytest 只根据类型来匹配，那么当有多个 fixture 返回相同类型（比如 dict）时，pytest 就无法确定应该使用哪个 fixture，这会导致冲突和不确定性。通过参数名匹配，测试函数可以清晰地表达它需要哪个具体的 fixture，从而避免了这种歧义。
# 问题 3：fixture 里能做的不只是 return 数据，还能做什么？
#    提示：想想测试前需要"准备环境"的场景
# 答：fixture 里除了 return 数据，还可以执行任何需要的前置准备工作，比如创建临时文件、连接数据库、设置环境变量、模拟 API 响应等。fixture 的作用不仅仅是提供数据，更重要的是为测试提供一个干净、可控的环境，让测试能够专注于验证功能，而不需要关心如何准备这些环境。这也是 fixture 的核心价值所在。

# ============================================================
# 运行
# ============================================================
# pytest day17_fixture_intro.py -v -s
# -s 参数让 print 输出显示出来，观察 fixture 的执行顺序
