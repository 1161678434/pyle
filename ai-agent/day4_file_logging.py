"""
Day 4 练习：文件操作 + 日志
===========================
学会读写文件、用 logging 记录测试日志。
"""
import os
import logging

# ============================================================
# 背景：模拟一个测试框架的"日志和报告"模块
# ============================================================

# 练习用的临时文件
TMP_DIR = os.path.join(os.path.dirname(__file__), ".day4_tmp")
os.makedirs(TMP_DIR, exist_ok=True)


# ============================================================
# TODO 1：基础写 + 读 — 保存和读取测试报告
# ============================================================
# 需求：
#   1. 把 tests 列表中的每一条写入文件（每条一行）
#   2. 用 with open()，不要裸 open()
#   3. 再写一个函数读取文件，返回文件全部内容（字符串）
#
def save_report(filepath, tests):
    """将测试结果列表逐行写入文件"""
    # TODO: 实现这个函数
    with open(filepath, "w", encoding="utf-8") as f:
        for test in tests:
            f.write(test + "\n")


def read_report(filepath):
    """读取文件全部内容并返回"""
    # TODO: 实现这个函数
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()

# ============================================================
# TODO 2：追加写入 + 逐行读取 — 测试执行日志
# ============================================================
# 需求：
#   1. append_log() — 以追加模式 "a" 写入一行日志
#   2. tail_lines() — 返回文件的最后 n 行（用列表返回，不包含空行）
#
# 提示：读取整个文件后取切片。
#
def append_log(filepath, line):
    """用追加模式写入一行日志"""
    # TODO: 实现这个函数
    with open(filepath, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def tail_lines(filepath, n):
    """返回文件的最后 n 个非空行，不足则全返回"""
    # TODO: 实现这个函数
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()
        # 过滤空行
    not_empty_lines = [lines.strip() for lines in lines if lines.strip()]
    return not_empty_lines[-n:]



# ============================================================
# TODO 3：logging 模块 — 配置和使用
# ============================================================
# 需求：创建函数 setup_logger(log_file)
#   1. 调用 logging.basicConfig() 配置：
#      - level=logging.DEBUG
#      - format="%(asctime)s [%(levelname)s] %(message)s"  (注意：asctime 不是 asctime)
#      - 同时输出到文件（FileHandler）和控制台（StreamHandler）
#   2. 注意：basicConfig 只能调用一次，第二次调用无效。
#      所以本函数用 logger = logging.getLogger("test_runner") 获取一个新的 logger
#      然后手动添加 handler（不要重复调用 basicConfig）
#

def setup_logger(log_file):
    """配置并返回一个 logger，同时输出到文件和控制台"""
    logger = logging.getLogger("test_runner")
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()  # 清空已有 handler，防止重复

    # 文件 handler
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)

    # 控制台 handler
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)

    # 统一的格式
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger


# ============================================================
# TODO 4：实战 — 模拟测试执行并记录日志
# ============================================================
# 需求：实现 run_tests(tests, logger)
#   参数 tests 是一个列表，每个元素是 {"name": str, "passed": bool}
#   1. 开始前记录 info: "测试开始，共 {n} 条用例"
#   2. 遍历 tests：
#      - 通过的用例用 info: "PASS {name}"
#      - 失败的用例用 error: "FAIL {name}"
#   3. 全部结束后记录 info: "测试完成，通过 {passed}/{total}"
#   4. 返回通过数
#
def run_tests(tests, logger):
    """执行测试并记录日志，返回通过数"""
    # TODO: 实现这个函数
    total = len(tests)
    passed_count = sum(1 for test in tests if test["passed"])
    logger.info(f"测试开始，共 {total} 条用例")
    for test in tests:
        if test["passed"]:
            logger.info(f"PASS {test['name']}")
        else:
            logger.error(f"FAIL {test['name']}")
    logger.info(f"测试完成，通过 {passed_count}/{total}")
    return passed_count


# ============================================================
# 下面的测试代码不要修改。完成上面的 TODO 后直接运行此文件。
# ============================================================
if __name__ == "__main__":
    print("=" * 50)
    print("Day 4 验证 — 文件操作 + 日志")
    print("=" * 50)

    # ---- TODO 1 ----
    print("\n--- TODO 1：基础写 + 读 ---")
    report_path = os.path.join(TMP_DIR, "todo1_report.txt")
    test_results = ["登录测试: PASS", "注册测试: FAIL", "搜索测试: PASS"]
    save_report(report_path, test_results)

    # 文件存在且能读回
    content = read_report(report_path)
    assert "登录测试" in content, "应包含第一条用例"
    assert "FAIL" in content, "应包含失败用例"
    assert "搜索测试" in content, "应包含第三条用例"
    print("✅ TODO 1 通过")

    # ---- TODO 2 ----
    print("\n--- TODO 2：追加写入 + 逐行读取 ---")
    log_path = os.path.join(TMP_DIR, "todo2_log.txt")
    # 清空旧文件重新开始
    with open(log_path, "w") as f:
        f.write("")

    append_log(log_path, "2025-01-01 测试系统启动")
    append_log(log_path, "2025-01-01 执行用例A")
    append_log(log_path, "2025-01-01 执行用例B")
    append_log(log_path, "2025-01-01 测试系统关闭")
    append_log(log_path, "")   # 空行应被 tail_lines 过滤掉

    tail = tail_lines(log_path, 3)
    assert len(tail) == 3, f"应返回 3 行，实际返回 {len(tail)} 行"
    assert "测试系统关闭" in tail[-1], f"倒数第一行应包含'测试系统关闭'，实际：{tail[-1]}"
    assert "用例B" in tail[-2], f"倒数第二行应包含'用例B'，实际：{tail[-2]}"
    assert "" not in tail, "空行应被过滤"
    print("✅ TODO 2 通过")

    # ---- TODO 3 ----
    print("\n--- TODO 3：logging 模块 ---")
    log_file = os.path.join(TMP_DIR, "todo3_logger.log")
    # 清理旧文件
    if os.path.exists(log_file):
        os.remove(log_file)

    logger = setup_logger(log_file)
    assert isinstance(logger, logging.Logger), "必须返回 Logger 对象"
    assert len(logger.handlers) == 2, "应该有 2 个 handler（文件 + 控制台）"
    assert isinstance(logger.handlers[0], logging.FileHandler) or \
           isinstance(logger.handlers[1], logging.FileHandler), \
           "其中一个 handler 必须是 FileHandler"

    # 写入一条日志验证文件输出
    logger.info("TODO3 验证消息")
    with open(log_file, "r", encoding="utf-8") as f:
        file_content = f.read()
    assert "TODO3 验证消息" in file_content, f"日志文件应包含写入的消息"
    print("✅ TODO 3 通过")

    # ---- TODO 4 ----
    print("\n--- TODO 4：实战 — 模拟测试执行 ---")
    log_file4 = os.path.join(TMP_DIR, "todo4_run.log")
    if os.path.exists(log_file4):
        os.remove(log_file4)

    logger4 = setup_logger(log_file4)
    test_cases = [
        {"name": "登录成功", "passed": True},
        {"name": "密码错误", "passed": True},
        {"name": "余额不足", "passed": False},
        {"name": "退出登录", "passed": True},
    ]
    passed_count = run_tests(test_cases, logger4)
    assert passed_count == 3, f"通过数应为 3，实际 {passed_count}"

    # 检查日志文件内容
    with open(log_file4, "r", encoding="utf-8") as f:
        run_log = f.read()
    assert "测试开始，共 4 条用例" in run_log, "应包含开始信息"
    assert "PASS 登录成功" in run_log, "应包含通过的用例"
    assert "FAIL 余额不足" in run_log, "应包含失败的用例"
    assert "PASS 密码错误" in run_log, "应包含另一个通过的用例"
    assert "测试完成，通过 3/4" in run_log, "应包含结束统计"
    print("✅ TODO 4 通过")

    print("\n" + "=" * 50)
    print("🎉 全部断言通过！你完成了 Day 4 的学习！")
    print("=" * 50)

    # 清理临时文件（注释掉下面两行可以保留日志文件便于检查）
    import shutil
    shutil.rmtree(TMP_DIR, ignore_errors=True)
