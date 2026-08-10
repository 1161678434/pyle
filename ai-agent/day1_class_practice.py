"""
Day 1 练习：Python 类深入
========================
任务：实现一个 TestCase 类，用于管理测试用例的执行和结果。
"""


class TestCase:
    """一个简单的测试用例管理器"""

    total_cases = 0  # 类属性：统计一共创建了多少个测试用例

    def __init__(self, name, description="", priority="P2"):
        """
        构造函数。创建一个测试用例实例。

        参数:
            name: 用例名称（必填）
            description: 用例描述（可选）
            priority: 优先级，默认 P2
        """
        self.name = name
        self.description = description
        self.priority = priority
        self.status = "未执行"       # 状态：未执行 / 通过 / 失败
        self.execution_time = 0.0    # 执行耗时（秒）
        self.error_msg = ""          # 失败时的错误信息

        TestCase.total_cases += 1    # 每创建一个实例，总数 +1

    # ========== TODO 1：实现 run() 方法 ==========
    # 让这个方法模拟执行一个测试用例：
    #   - 打印 "正在执行用例：{name}..."
    #   - 设置 self.status = "通过"
    #   - 设置 self.execution_time = 0.5
    #   - 返回 True 表示执行成功
    #
    def run(self):
        print(f"正在执行用例：{self.name}...")
        self.status = "通过"
        self.execution_time = 0.5
        return True
    

    # ========== TODO 2：实现 fail() 方法 ==========
    # 让这个方法记录一个失败结果：
    #   - 设置 self.status = "失败"
    #   - 用参数 reason 设置 self.error_msg
    #   - 返回 False 表示执行失败
    #
    def fail(self, reason):
        self.status = "失败"
        self.error_msg = reason
        return False

    # ========== TODO 3：实现 summary() 方法 ==========
    # 让这个方法返回用例的摘要信息：
    #   返回格式："{name} [{priority}] — {status}"
    #   例如："登录测试 [P1] — 通过"
    #
    def summary(self):
        return f"{self.name} [{self.priority}] — {self.status}"

    # ========== TODO 4：实现 __str__ 魔术方法 ==========
    # 当用户 print(tc) 时，自动调用此方法
    # 返回一个格式化的多行字符串，包含所有信息：
    #   """
    #   用例：{name}
    #   描述：{description}
    #   优先级：{priority}
    #   状态：{status}
    #   耗时：{execution_time}s
    #   """
    # （如果有错误信息，再加一行 "错误：{error_msg}"）
    #
    def __str__(self):
        result = f"用例：{self.name}\n描述：{self.description}\n优先级：{self.priority}\n状态：{self.status}\n耗时：{self.execution_time}s"
        if self.error_msg:
            result += f"\n错误：{self.error_msg}"

        return result


# ============================================================
# 下面的测试代码不要修改。完成上面的 TODO 后直接运行此文件。
# ============================================================
if __name__ == "__main__":
    print("=" * 50)
    print("Day 1 验证 — Python 类深入")
    print("=" * 50)

    # 创建测试用例
    tc1 = TestCase("登录测试", "验证用户名密码登录", "P1")
    tc2 = TestCase("注册测试", priority="P2")
    tc3 = TestCase("搜索测试", "验证搜索功能", "P1")

    print(f"\n已创建 {TestCase.total_cases} 个测试用例\n")

    # 测试 run()
    print("--- 执行 tc1 ---")
    result = tc1.run()
    assert result == True, "run() 应该返回 True"
    assert tc1.status == "通过", f"状态应为'通过'，实际为'{tc1.status}'"
    assert tc1.execution_time > 0, "execution_time 应大于 0"
    print("✅ run() 通过\n")

    # 测试 fail()
    print("--- 执行 tc2（模拟失败）---")
    tc2.fail("用户名不能为空")
    assert tc2.status == "失败", f"状态应为'失败'，实际为'{tc2.status}'"
    assert tc2.error_msg == "用户名不能为空"
    print("✅ fail() 通过\n")

    # 测试 summary()
    print("--- Summary ---")
    assert tc1.summary() == "登录测试 [P1] — 通过"
    assert tc2.summary() == "注册测试 [P2] — 失败"
    assert tc3.summary() == "搜索测试 [P1] — 未执行"
    print(f"  {tc1.summary()}")
    print(f"  {tc2.summary()}")
    print(f"  {tc3.summary()}")
    print("✅ summary() 通过\n")

    # 测试 __str__
    print("--- print(tc1) ---")
    print(tc1)
    print()
    print("--- print(tc2) ---")
    print(tc2)
    print()

    print("=" * 50)
    print("🎉 全部断言通过！你完成了 Day 1 的学习！")
    print("=" * 50)
