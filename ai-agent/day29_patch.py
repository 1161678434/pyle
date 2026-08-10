"""
Day 29：patch 补丁 — 替换真实对象，不消耗 API 额度跑测试
===========================================================
核心概念：
1. @patch 装饰器 — 把函数内部的依赖临时替换成 Mock
2. 补丁的"目标路径"怎么确定 — patch 的是 import 的位置，不是定义的位置
3. patch.object — 精确替换单个对象
4. 为什么需要 patch — 不改源码就能测试有外部依赖的函数

学完今天你能：
- 测试任何调用外部 API 的函数，不消耗 API 额度
- 理解 patch 的路径规则（最大坑）
- 用 @patch 和 with patch() 两种方式写测试
"""
from unittest.mock import Mock, patch

# ============================================================
# 前置：模拟一个"你不方便改源码"的模块
# ============================================================
# 假设这是公司内部库，你不能改它：

import time

def get_current_timestamp():
    """获取当前时间戳（真调用 time.time()）"""
    return time.time()

def double_number(x):
    """简单运算 — 后面用来对比"""
    return x * 2

def call_external_api(url):
    """模拟调用外部 API — 这里用 time.sleep 模拟耗时"""
    return f"真实响应: {url} 的官方数据"


# ============================================================
# 第一部分：@patch 装饰器 — 最常用的方式
# ============================================================

print("=" * 50)
print("第一部分：@patch 装饰器")
print("=" * 50)

# 回顾：不用 patch 时，只能把 mock 作为参数传入
print("=== 不用 patch（函数参数传入 mock）===")

def process(multiplier):
    """调用 multiplier 函数处理数据"""
    return multiplier(5)

mock_func = Mock(return_value=100)
result = process(mock_func)
print(f"result = {result}，mock 被调用: {mock_func.called}")

# 但如果你不能改 process 的签名呢？它内部直接 import time.time()
# 这时用 @patch

print()
print("=== 用 @patch 替换内置函数 ===")

@patch('builtins.input', return_value='默认用户输入')
def test_with_patch(mock_input):
    """patch 装饰器：把 input() 替换掉"""
    user = input("请输入：")
    print(f"用户输入了: {user}")
    return user

result = test_with_patch()
print(f"测试结果: {result}")


# ============================================================
# 第二部分：patch 路径规则 — 最重要的知识点！
# ============================================================

print()
print("=" * 50)
print("第二部分：patch 路径规则（最大坑！）")
print("=" * 50)

# 规则：patch 的路径 = 目标被 import 的模块.目标名
# 不是目标定义的位置！

# 本模块顶部写了 import time，所以 time 是 day29_patch 模块的一个属性
# 要替换 get_current_timestamp 内部的 time.time，
# 必须 patch 'day29_patch.time'（因为 time 是通过 import time 引入本模块的）

print("=== 验证：patch 路径必须指向被 import 的位置 ===")

# from day29_patch import get_current_timestamp
# 实际上我们就在这个模块里，直接测：

# ⚠️ 用 __name__ 自动适配：python 直接运行就是 '__main__'，被 import 就是模块名
with patch(f'{__name__}.time') as mock_time:
    mock_time.time.return_value = 99999.0
    result = get_current_timestamp()
    print(f"get_current_timestamp() = {result}")  # 99999.0

# 常见错误对比表：
# 本模块中 patch 'time'           → ❌ 无效，time 模块本身不变
# python day29_patch.py 直接跑    → 模块名是 __main__，patch '__main__.time' 才对
# 别人 import day29_patch 再用   → 模块名是 day29_patch，patch 'day29_patch.time' 才对
# 最佳实践：patch(f'{__name__}.xxx') → 不管怎么跑都对


# ============================================================
# 第三部分：同时 patch 多个对象
# ============================================================

print()
print("=" * 50)
print("第三部分：同时 patch 多个对象")
print("=" * 50)


def complex_operation():
    """同时用了 time.time 和 time.sleep（模拟带延迟的操作）"""
    t = time.time()
    time.sleep(2)   # 测试时等 2 秒太慢了！
    return f"在 {t} 完成"


# @patch 装饰器从下往上执行，参数从下往上传递
# ⚠️ python day29_patch.py 运行时，模块名是 __main__，不是 day29_patch
with patch(f'{__name__}.time') as mock_time:   # __name__ 自动适配运行方式
    mock_time.time.return_value = 100.0
    mock_time.sleep.return_value = None  # sleep 不阻塞
    result = complex_operation()
    print(result)  # 在 100.0 完成 — 瞬间返回，不等 2 秒


# ============================================================
# TODO 1：用 patch 测试"调用外部 API"的函数
# ============================================================

print()
print("=" * 50)
print("TODO 1：patch 外部 API 调用")
print("=" * 50)

# 这是一个"调用外部 API"的函数，你不能改它
def fetch_data(url):
    """获取数据 — 真调 call_external_api，我们不想真调"""
    return call_external_api(url)


# ← 写代码：
# 1. 用 with patch(f'{__name__}.call_external_api') as mock_api（提示：用 __name__ 自动适配）
# 2. 设置 mock_api.return_value = "Mock数据"
# 3. 调用 fetch_data("http://example.com")
# 4. 打印结果，断言结果是 "Mock数据"
# 5. 断言 mock_api 被调用了 1 次，参数是 "http://example.com"

# ← 你的代码写在这里
with patch(f'{__name__}.call_external_api') as mock_ai:
    mock_ai.return_value = 'Mock数据'
    result = fetch_data("http://example.com")
    print(result)
    assert result == 'Mock数据'
    print(f"调用次数 {mock_ai.call_count}")
    mock_ai.assert_called_once_with("http://example.com")
    
    


# ============================================================
# TODO 2：patch 耗时操作 — 让慢速测试变快
# ============================================================

print()
print("=" * 50)
print("TODO 2：patch 耗时操作")
print("=" * 50)


def slow_report():
    """生成报告 — 内部有耗时操作"""
    time.sleep(3)  # 模拟耗时计算
    return "报告内容: 销售数据"


def generate_and_send(report_func):
    """生成报告并发送"""
    report = report_func()
    return f"已发送: {report}"


# ← 写代码：
# 1. 用 with patch(f'{__name__}.time') as mock_time
# 2. 设置 mock_time.sleep.return_value = None（让 sleep 瞬间返回）
# 3. 调用 slow_report()，验证它不慢
# 4. 打印结果

# ← 你的代码写在这里
with patch(f'{__name__}.time') as mock_time:
    mock_time.sleep.return_value = None
    result = slow_report()
    print(f"验证速度 {result}")


# ============================================================
# TODO 3（思考题）：@patch 装饰器方式 vs with patch() 方式
# ============================================================

print()
print("=" * 50)
print("TODO 3：@patch vs with patch()")
print("=" * 50)

# 把 TODO 1 的逻辑改写为 @patch 装饰器形式的测试函数
# def test_fetch_data_xxx():
#     ...

@patch(f'{__name__}.call_external_api')

def test_fetch_data_patch(mock_api):
    mock_api.return_value = "Mock 数据"
    result = fetch_data("http://example.com")
    assert result =="Mock 数据"
    mock_api.assert_called_once_with("http://example.com")

test_fetch_data_patch()


# 问题 1：@patch 装饰器和 with patch() 各适用于什么场景？
# 问题 2：同时 patch 多个对象时，@patch 装饰器的参数顺序是什么规则？

"""
# 答案提示：
#
# 1. @patch 装饰器：整个测试函数都需要用到 mock → 干净，省缩进
#    with patch()：只在一小段代码中需要 mock → 灵活，可嵌套
#
# 2. 多个 @patch 从上往下执行，参数从下往上传递：
#
#    @patch('module.A')   # 第 2 个执行
#    @patch('module.B')   # 第 1 个执行
#    def test(mock_B, mock_A):   # mock_B 在第 1 个参数位置
#        ...
"""


# ============================================================
# 运行
# ============================================================
# python day29_patch.py
