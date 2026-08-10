"""
Day 2 练习：类的高级用法 — 继承 + 魔术方法
===========================================
基于 Day 1 的 TestCase 类，学习继承和更多魔术方法。
"""

# ============================================================
# 下面是 Day 1 的 TestCase 类（完整版，不需要修改）
# ============================================================
class TestCase:
    """一个简单的测试用例管理器"""

    total_cases = 0

    def __init__(self, name, description="", priority="P2"):
        self.name = name
        self.description = description
        self.priority = priority
        self.status = "未执行"
        self.execution_time = 0.0
        self.error_msg = ""

        TestCase.total_cases += 1

    def run(self):
        print(f"正在执行用例：{self.name}...")
        self.status = "通过"
        self.execution_time = 0.5
        return True

    def fail(self, reason):
        self.status = "失败"
        self.error_msg = reason
        return False

    def summary(self):
        return f"{self.name} [{self.priority}] — {self.status}"

    def __str__(self):
        result = f"用例：{self.name}\n描述：{self.description}\n优先级：{self.priority}\n状态：{self.status}\n耗时：{self.execution_time}s"
        if self.error_msg:
            result += f"\n错误：{self.error_msg}"
        return result


# ============================================================
# TODO 1：继承 — 创建 ApiTestCase 子类
# ============================================================
# 需求：
#   - 继承 TestCase
#   - 新增属性：endpoint（API 路径），method（HTTP 方法，默认 "GET"），
#     expected_status（期望的 HTTP 状态码，默认 200）
#   - 调用父类 __init__，然后设置自己的新属性
#
# 提示：
#   super().__init__(...) 可以调用父类的构造函数
#
class ApiTestCase(TestCase):
    """API 接口测试用例"""

    def __init__(self, name, endpoint, method="GET", expected_status=200, description="", priority="P2"):
        super().__init__(name, description, priority)
        self.endpoint = endpoint
        self.method = method
        self.expected_status = expected_status

    # ========== TODO 2：重写 summary() 方法 ==========
    # 需求：
    #   返回格式："{name} [{method} {endpoint}] — {status}"
    #   例如："登录接口 [POST /api/login] — 通过"
    #
    def summary(self):
        return f"{self.name} [{self.method} {self.endpoint}] — {self.status}"

    # ========== TODO 3：实现 __repr__ 魔术方法 ==========
    # __repr__ 和 __str__ 的区别：
    #   __str__ 给用户看（友好、可读）
    #   __repr__ 给开发者看（精确、可用于调试）
    #
    # 需求：返回一个 string，看起来像一个构造调用
    #   格式：ApiTestCase(name='登录接口', endpoint='/api/login', method='POST')
    #
    def __repr__(self):
        return f"ApiTestCase(name='{self.name}', endpoint='{self.endpoint}', method='{self.method}')"


# ============================================================
# TODO 4：实现 __eq__ 魔术方法
# ============================================================
# 给 TestCase 类本身添加 __eq__，让两个用例可以比较
# 在类外面用 Monkey Patch 的方式加上去（真实的项目里直接改类就行）
#
# 两个测试用例“相等”的条件：name 相同 且 priority 相同
# 需求：用例名和优先级都一样就返回 True
#
def testcase_eq(self, other):
    """比较两个测试用例是否相等"""
    if not isinstance(other, TestCase):
        return NotImplemented
    return self.name == other.name and self.priority == other.priority


# 这行把 __eq__ 方法"装"到 TestCase 类上
TestCase.__eq__ = testcase_eq


# ============================================================
# 下面的测试代码不要修改。完成上面的 TODO 后直接运行此文件。
# ============================================================
if __name__ == "__main__":
    print("=" * 50)
    print("Day 2 验证 — 类的高级用法")
    print("=" * 50)

    # ---- 测试 ApiTestCase 继承 ----
    print("\n--- 创建 ApiTestCase ---")
    api1 = ApiTestCase("登录接口", "/api/login", "POST", 200, "验证登录")
    api2 = ApiTestCase("用户信息", "/api/user/me", "GET", 200, priority="P1")

    assert isinstance(api1, TestCase), "ApiTestCase 应该继承自 TestCase"
    assert hasattr(api1, "endpoint"), "ApiTestCase 应该有 endpoint 属性"
    assert api1.endpoint == "/api/login"
    assert api1.method == "POST"
    assert api1.expected_status == 200
    print(f"  创建成功: {api1.name}, endpoint={api1.endpoint}")
    print("✅ 继承 + 构造函数 通过")

    # ---- 测试 run() 继承 ----
    print("\n--- 执行 api1 ---")
    result = api1.run()
    assert result == True
    assert api1.status == "通过"
    print("✅ 子类继承 run() 通过")

    # ---- 测试 summary() 重写 ----
    print("\n--- Summary ---")
    assert api1.summary() == "登录接口 [POST /api/login] — 通过", f"预期不同：{api1.summary()}"
    assert api2.summary() == "用户信息 [GET /api/user/me] — 未执行"
    print(f"  {api1.summary()}")
    print(f"  {api2.summary()}")
    print("✅ summary() 重写 通过")

    # ---- 测试 fail() 继承 ----
    api2.fail("404 Not Found")
    assert api2.status == "失败"
    assert api2.error_msg == "404 Not Found"
    print("\n✅ 子类继承 fail() 通过")

    # ---- 测试 __repr__ ----
    print("\n--- repr(api1) ---")
    repr_str = repr(api1)
    print(f"  {repr_str}")
    assert "ApiTestCase" in repr_str
    assert "name=" in repr_str
    assert "endpoint=" in repr_str
    print("✅ __repr__ 通过")

    # ---- 测试 __eq__ ----
    print("\n--- 比较两个用例 ---")
    tc_a = TestCase("登录测试", priority="P1")
    tc_b = TestCase("登录测试", priority="P1")
    tc_c = TestCase("登录测试", priority="P2")
    tc_d = TestCase("注册测试", priority="P1")

    assert tc_a == tc_b, "同名同优先级应该相等"
    assert tc_a != tc_c, "优先级不同不应该相等"
    assert tc_a != tc_d, "用例名不同不应该相等"
    print("✅ __eq__ 通过")

    print("\n" + "=" * 50)
    print("🎉 全部断言通过！你完成了 Day 2 的学习！")
    print("=" * 50)
