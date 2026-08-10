"""
Day 3 练习：异常处理 — try/except 实战
======================================
学会捕获异常、处理错误，让程序不崩溃。
"""

# ============================================================
# 背景：模拟一个"测试执行器"，它会执行测试用例，但可能出错
# ============================================================
import time
import random


# ============================================================
# TODO 1：基础 try/except
# ============================================================
# 需求：下面的函数接收一个字典 data，返回 data["result"]
#   但如果 key 不存在，返回 None（不要崩溃）
#
def safe_get_result(data):
    try:
        return data["result"]
    except (KeyError, TypeError):
        return None
    

# ============================================================
# TODO 2：捕获多种异常
# ============================================================
# 需求：模拟执行测试用例，流程如下：
#   1. 从 test_case 字典中读取 name 和 steps
#   2. 遍历 steps 列表，打印每个步骤
#   3. 如果 steps 不存在或不是列表，返回 False
#   4. 如果步骤下标越界（IndexError），返回 False
#   5. 任何未知异常也返回 False（不要崩溃）
#   6. 全部执行完返回 True
#
def execute_test(test_case):
    try:
        name = test_case["name"]
        steps = test_case["steps"]
        if not isinstance(steps, list):
            raise TypeError("steps 必须是列表")
        for i in range(len(steps)):
            print(f"步骤 {i + 1}: {steps[i]}")
    except KeyError:
        print("错误：列表不存在")
        return False
    except IndexError:
        print("错误：步骤下标越界")
        return False
    except Exception as e:
        print(f"未知错误：{str(e)}")
        return False
    else:
        print("测试执行成功")
        return True
    finally:
        print("--- 测试执行结束 ---")



# ============================================================
# TODO 3：else 和 finally
# ============================================================
# 需求：模拟调用一个 API，返回结果为 dict
#   如果 status_code != 200，就 raise ValueError(f"API 返回 {status_code}")
#   否则返回 response_body
#
# 然后在 execute_with_log() 中调用它：
#   - try 中调用 call_api()
#   - except 中打印错误并返回 None
#   - else 中打印 "API 调用成功" 并返回结果
#   - finally 中打印 "--- 请求结束 ---"（不管成败都会跑）
#
def call_api(status_code, response_body):
    if status_code !=200:
        raise ValueError(f"API 返回 {status_code}")
    return response_body


def execute_with_log(status_code, response_body):
    try:
        result = call_api(status_code, response_body)
    except ValueError as e:
        print(f"API 调用失败：{str(e)}")
        return None
    else:
        print("API 调用成功")
        return result
    finally:
        print("--- 请求结束 ---")


# ============================================================
# TODO 4：raise — 主动抛出异常
# ============================================================
# 需求：创建一个 TestCase 对象需要 validate（验证）参数
#   1. 如果 name 是空字符串，raise ValueError("用例名称不能为空")
#   2. 如果 priority 不在 ["P0", "P1", "P2", "P3"] 中，
#      raise ValueError(f"无效的优先级：{priority}")
#   3. 验证通过才返回 True
#
VALID_PRIORITIES = ["P0", "P1", "P2", "P3"]


class TestCaseV2:
    """带参数验证的测试用例"""

    def __init__(self, name, priority="P2"):
        self.name = name
        self.priority = priority
        self._validate()       # 构造时自动调用验证

    def _validate(self):
        """验证参数合法性，不合法就抛异常"""
        if not self.name:
            raise ValueError("用例名称不能为空")
        if self.priority not in VALID_PRIORITIES:
            raise ValueError(f"无效的优先级：{self.priority}")


# ============================================================
# 下面的测试代码不要修改。完成上面的 TODO 后直接运行此文件。
# ============================================================
if __name__ == "__main__":
    print("=" * 50)
    print("Day 3 验证 — 异常处理")
    print("=" * 50)

    # ---- TODO 1 ----
    print("\n--- TODO 1：基础 try/except ---")
    assert safe_get_result({"result": 42}) == 42
    assert safe_get_result({"status": "ok"}) is None
    assert safe_get_result(None) is None    # 额外考验：None 没有 [] 操作，会抛 AttributeError/TypeError
    print("✅ TODO 1 通过")

    # ---- TODO 2 ----
    print("\n--- TODO 2：捕获多种异常 ---")
    # 正常情况
    normal = {"name": "登录测试", "steps": ["打开页面", "输入账号", "点击登录"]}
    assert execute_test(normal) == True, f"正常用例应该成功"

    # 缺少 steps
    no_steps = {"name": "注册测试"}
    assert execute_test(no_steps) == False, "缺少 steps 应返回 False"

    # steps 不是列表
    bad_steps = {"name": "搜索测试", "steps": "打开页面"}
    assert execute_test(bad_steps) == False, "steps 不是列表应返回 False"

    print("✅ TODO 2 通过")

    # ---- TODO 3 ----
    print("\n--- TODO 3：else 和 finally ---")
    # 成功
    result = execute_with_log(200, {"data": "hello"})
    assert result == {"data": "hello"}, "200 应该返回响应体"
    # 失败
    result = execute_with_log(500, {"error": "server error"})
    assert result is None, "5xx 应该返回 None"
    print("✅ TODO 3 通过")

    # ---- TODO 4 ----
    print("\n--- TODO 4：raise 异常 ---")
    # 正常创建
    tc = TestCaseV2("正常用例", "P1")
    assert tc.name == "正常用例"
    assert tc.priority == "P1"
    print("  正常创建通过")

    # 空名称
    try:
        TestCaseV2("", "P2")
        assert False, "空名称应该抛异常"
    except ValueError as e:
        assert "名称" in str(e)
        print(f"  空名称异常捕获：{e}")

    # 无效优先级
    try:
        TestCaseV2("测试", "P9")
        assert False, "无效优先级应该抛异常"
    except ValueError as e:
        assert "优先级" in str(e)
        print(f"  无效优先级异常捕获：{e}")

    print("✅ TODO 4 通过")

    print("\n" + "=" * 50)
    print("🎉 全部断言通过！你完成了 Day 3 的学习！")
    print("=" * 50)
