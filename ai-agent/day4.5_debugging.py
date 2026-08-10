"""
Day 4.5 练习：调试实战
======================
下面是一个"测试执行器"程序，它负责：
  1. 加载测试用例配置
  2. 逐个执行用例
  3. 生成测试报告

程序里有 4 个 bug，会导致运行失败或结果错误。
你的任务：用调试手段找出并修复它们。

调试工具优先级建议：
  1. 先直接跑一遍，看报错信息（Python 的异常提示已经告诉你很多了）
  2. 在报错行前后加 print() 看变量值
  3. 用 VS Code 断点（F5）一行行走
  4. 修好一个 bug 后重新跑，可能下一个 bug 就暴露了
"""
import time
import random
import os

# ============================================================
# 背景：这是一个"简化版测试框架"
# ============================================================

# 模拟的测试用例数据（从"数据库"加载）
TEST_CASES = [
    {"id": "TC001", "name": "登录测试", "steps": 3, "priority": "P0"},
    {"id": "TC002", "name": "搜索测试", "steps": 2, "priority": "P1"},
    {"id": "TC003", "name": "支付测试", "steps": 5, "priority": "P0"},
    {"id": "TC004", "name": "退出测试", "steps": 1, "priority": "P2"},
]


def load_test_cases():
    """模拟从数据库加载测试用例"""
    print("[加载] 正在从数据库加载用例...")

    cases = []
    for tc in TEST_CASES:
        # 模拟网络延迟
        time.sleep(0.1)
        cases.append(tc)

    print(f"[加载] 加载完成，共 {len(cases)} 条用例")          # BUG 1
    return cases


def execute_single_test(test_case):
    """执行单个测试用例，返回 (name, passed: bool, duration: float)"""
    name = test_case["name"]
    steps = test_case["steps"]                            # BUG 2

    print(f"[执行] {name} — 共 {steps} 步...")

    start = time.time()
    passed = True                                          # BUG 3：初始值错了
    for i in range(steps):
        # 模拟每个步骤有 90% 概率通过
        if random.random() < 0.1:
            passed = False
        time.sleep(0.05)

    duration = time.time() - start
    status = "PASS" if passed else "FAIL"
    print(f"[结果] {name}: {status} (耗时 {duration:.2f}s)")

    return {"name": name, "passed": passed, "duration": duration}


def analyze_results(results):
    """分析测试结果，返回统计信息"""
    total = len(results)

    # 统计通过数
    passed = 0
    for r in results:
        if r["passed"] == True:                                # BUG 4
            passed += 1

    # 计算通过率
    if total > 0:
        pass_rate = passed / total * 100
    else:
        pass_rate = 0.0

    # 计算总耗时
    total_duration = sum(r["duration"] for r in results)

    return {
        "total": total,
        "passed": passed,
        "failed": total - passed,
        "pass_rate": pass_rate,
        "total_duration": total_duration,
    }


def generate_report(stats, report_path):
    """将分析结果写入报告文件"""
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("=" * 40 + "\n")
        f.write("  测 试 报 告\n")
        f.write("=" * 40 + "\n\n")
        f.write(f"总用例数: {stats['total']}\n")
        f.write(f"通过: {stats['passed']} 条\n")
        f.write(f"失败: {stats['failed']} 条\n")
        f.write(f"通过率: {stats['pass_rate']:.1f}%\n")
        f.write(f"总耗时: {stats['total_duration']:.2f}s\n")
    print(f"[报告] 已保存到 {report_path}")


def main():
    """主流程"""
    print("=" * 40)
    print("  自动化测试执行器 v1.0")
    print("=" * 40 + "\n")

    # 1. 加载用例
    cases = load_test_cases()

    # 2. 逐个执行
    results = []
    for case in cases:
        result = execute_single_test(case)
        results.append(result)

    # 3. 分析结果
    stats = analyze_results(results)

    # 4. 生成报告
    report_path = os.path.join(os.path.dirname(__file__), "test_report.txt")
    generate_report(stats, report_path)

    print(f"\n全部完成: {stats['passed']}/{stats['total']} 通过, "
          f"通过率 {stats['pass_rate']:.1f}%")


if __name__ == "__main__":
    main()
