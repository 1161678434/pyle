"""
Day 31：测试 AI 输出（一）— 关键词、长度、类型检查
=====================================================
核心问题：AI 的输出是不确定的，你不能写 assert result == "精确值"
解决方案：验证输出的"特征"而不是"精确值"

三种基础检查：
1. 关键词断言 — 响应里必须出现 XX（如"推荐"、"步骤"、"代码"）
2. 长度检查 — 响应不能太短（敷衍）也不能太长（超出 token 限制）
3. 类型检查 — 响应必须是 str/list/dict 等预期类型

学完今天你能：
- 对不确定的 AI 输出写出有效的测试断言
- 判断一个 AI 调用是否"基本可用"
"""

import pytest
from unittest.mock import Mock, patch

# ============================================================
# 模拟 AI 服务（就用你熟悉的 mock 拦截，不真调 API）
# ============================================================

def ai_chat(prompt: str) -> str:
    """模拟 AI 聊天 — 真实场景会调 OpenAI API"""
    # 实际上这里会调 API，我们现在用 patch 拦截
    pass


def ai_summarize(text: str) -> str:
    """模拟 AI 总结 — 返回摘要"""
    pass


def ai_extract_keywords(text: str) -> list:
    """模拟 AI 提取关键词 — 返回列表"""
    pass


# ============================================================
# 第一部分：关键词断言 — "响应里必须有这些词"
# ============================================================

print("=" * 50)
print("第一部分：关键词断言")
print("=" * 50)

# 场景：让 AI 推荐一道菜，响应必须提到"食材"或"做法"
# AI 可能说"我推荐宫保鸡丁，食材有..." 也可能说 "试试红烧肉，做法如下..."
# 你不知道确切文字，但知道它应该包含"食材"或"做法"

def recommend_dish(preference: str) -> str:
    """让 AI 推荐一道菜"""
    return ai_chat(f"推荐一道{preference}的菜，说明食材和做法")


# 模拟 AI 的两种可能回答
sample_1 = "我推荐酸辣土豆丝。食材：土豆、辣椒、醋。做法：切丝后快炒。"
sample_2 = "试试这个：西红柿炒鸡蛋，食材有西红柿和鸡蛋，简单美味。"

# 关键词检查的两种写法：
print("=== 方式 1：单个关键词 ===")
assert "食材" in sample_1          # 包含"食材"
assert "食材" in sample_2          # 包含"食材"

print("=== 方式 2：一组关键词中至少命中一个 ===")
keywords = ["食材", "做法", "推荐"]
assert any(k in sample_1 for k in keywords)  # sample_1 命中了"食材"和"做法"
assert any(k in sample_2 for k in keywords)  # sample_2 命中了"食材"

# any() 解释：只要 keywords 列表中有任意一个在 sample 中，返回 True


# ============================================================
# 第二部分：长度检查 — "不能太短，也不能太长"
# ============================================================

print()
print("=" * 50)
print("第二部分：长度检查")
print("=" * 50)

# 场景：让 AI 写一篇简介，要求 50-200 字
#   - 太短（<20字）→ 可能是 AI 敷衍了
#   - 太长（>500字）→ 可能超出 token 预算或输出截断

def write_bio(name: str, role: str) -> str:
    """让 AI 写简介"""
    return ai_chat(f"请为{role}{name}写一段50-200字的简介")


# 模拟四种 AI 输出
good_bio = "张三是一位资深的软件测试工程师，拥有8年从业经验，擅长自动化测试框架搭建，曾主导多个大型项目的质量保障工作，对 AI 驱动的测试工具充满热情。"
short_bio = "张三，测试工程师。"           # ← 太短，敷衍
long_bio = "张三是一个" + "非常" * 600      # ← 太长
empty_bio = ""                              # ← 空响应，AI 出 bug 了

# 长度检查
def check_length(text: str, min_len: int = 10, max_len: int = 500) -> bool:
    """检查响应长度是否在合理范围"""
    length = len(text)
    return min_len <= length <= max_len

print(f"好的简介: {check_length(good_bio)}")    # True — 长度合理
print(f"太短: {check_length(short_bio)}")       # False — 只有 8 个字
print(f"太长: {check_length(long_bio)}")        # False — 超过 500
print(f"空响应: {check_length(empty_bio)}")     # False — 空的


# ============================================================
# 第三部分：类型检查 — "返回的是预期的类型吗？"
# ============================================================

print()
print("=" * 50)
print("第三部分：类型检查")
print("=" * 50)

# 场景：ai_extract_keywords 应该返回 list
# 场景：ai_chat 应该返回 str
# 场景：如果 AI 返回了 JSON 字符串，你能解析出来吗？

def extract_and_validate(user_input: str) -> list:
    """提取关键词 — 应该返回 list"""
    return ai_extract_keywords(user_input)


# 模拟测试
print("=== isinstance 类型检查 ===")
fake_keywords = ["Python", "自动化", "测试"]    # ← 正确的类型
bad_keywords = "Python, 自动化, 测试"          # ← 返回了字符串而不是列表

assert isinstance(fake_keywords, list)           # ✅ 是 list
print(f"类型正确: {isinstance(fake_keywords, list)}")

# ❌ 如果是字符串就过不了
# assert isinstance(bad_keywords, list)          # 会失败

print("=== 检查列表不为空 ===")
assert len(fake_keywords) > 0                    # ✅ 有内容
print(f"列表不为空: {len(fake_keywords)} 个关键词")

print("=== 列表里每个元素都是 str ===")
assert all(isinstance(k, str) for k in fake_keywords)  # ✅ 每一项都是字符串
print("所有元素都是字符串")


# ============================================================
# TODO 1：写一个完整的 AI 输出检查函数
# ============================================================

print()
print("=" * 50)
print("TODO 1：综合检查函数")
print("=" * 50)

# 需求：写一个 validate_ai_response(text: str) -> dict
# 返回 {"valid": True/False, "errors": [...], "length": int}
#
# 检查规则：
#   1. 不能为空
#   2. 长度 >= 10 个字符
#   3. 长度 <= 1000 个字符
#   4. 必须包含至少一个标点符号：。！？.!?
#
# 如果所有检查通过，valid=True，errors=[]
# 哪条不通过，就把那条的说明放进 errors 列表

def validate_ai_response(text: str) -> dict:
    """检查 AI 响应是否合格"""
    # ← 你的代码写在这里
    errors = []
    length = len(text)

    if length == 0:
        errors.append("响应为空")
    if length < 10 :
        errors.append("长度太短，回答敷衍")
    if length >1000 :
        errors.append("长度太长，不够精简")
    if not any(k in text for k  in ["。","！","？",".","!","?"]):
        errors.append("必须含有标点符号")
    return {"valid": len(errors) == 0, "errors": errors, "length": length}


# 测试用例（写完 validate_ai_response 后验证）
def test_validate_ai_response():
    # case 1: 正常响应
    r = validate_ai_response("这是一段正常的AI回复，包含了足够的信息和标点符号。")
    assert r["valid"] == True
    assert r["errors"] == []

    # case 2: 空字符串
    r = validate_ai_response("")
    assert r["valid"] == False
    assert any("空" in e for e in r["errors"])

    # case 3: 太短
    r = validate_ai_response("好")
    assert r["valid"] == False
    assert any("长度" in e for e in r["errors"])

    # case 4: 没有标点
    r = validate_ai_response("这是一段没有标点的文本一直写下去")
    assert r["valid"] == False
    assert any("标点" in e for e in r["errors"])

    # case 5: 太长
    r = validate_ai_response("长" * 1001)
    assert r["valid"] == False

    print("✅ 所有测试通过")


# 测试写完后取消下行注释来验证：
# test_validate_ai_response()


# ============================================================
# TODO 2：mock + AI 输出检查 — 结合 Day 30 的知识
# ============================================================

print()
print("=" * 50)
print("TODO 2：mock 拦截 AI + 检查输出")
print("=" * 50)

# 场景：test_ai_recommend 函数
#   1. 用 mock 拦截 ai_chat，返回 "建议你学习 Python 自动化测试"
#   2. 调用 recommend_dish("家常")
#   3. 用 keywords = ["食材", "做法", "推荐"] 做关键词检查
#   4. 用 check_length() 检查长度

def test_ai_recommend():
    """测试 AI 推荐功能：mock 拦截 + 输出检查"""
    # ← 你的代码写在这里
    m = Mock()
    m.return_value = "我推荐酸辣土豆丝，食材有土豆和辣椒，做法简单"
    with patch (f"{__name__}.ai_chat", m):
        result = recommend_dish("家常")
        keywords = ["食材", "做法", "推荐"]
        assert any(k in result for k in keywords) 
        print(f"长度: {check_length(result)}")



# ============================================================
# TODO 3：边界情况 — AI 可能返回非预期内容
# ============================================================

print()
print("=" * 50)
print("TODO 3：边界情况思考")
print("=" * 50)

# 问题 1：如果 AI 返回了 None 而不是字符串，你的类型检查扛得住吗？
# 问题 2：如果 AI 返回了超长的回复（比如 10 万字），会发生什么？
# 问题 3：关键词检查 "推荐" in response，如果 AI 说的是 "我不推荐" 呢？

"""
# 提示
# 1. isinstance(None, str) → False，会漏过去。应该先判断 if text is None
# 2. len(text) 对 10 万字很快，但你的 token 预算可能爆了
# 3. 关键词匹配是"笨检查"，只能作为第一道防线。
#    后续 Day 32 会学 JSON 格式校验、结构完整性等更精确的检查
"""


# ============================================================
# TODO 4（小实战）：写一个完整的测试用例
# ============================================================

print()
print("=" * 50)
print("TODO 4：完整测试用例")
print("=" * 50)

# 背景：你有一个 ai_answer_question 函数，调用 AI 回答用户问题
# 要求：写一个完整的测试函数，包含：
#   1. 用 patch 拦截 ai_chat
#   2. 对 AI 返回的答案做：类型检查 + 长度检查 + 关键词检查
#   3. 用 assert 验证

def ai_answer_question(question: str) -> str:
    """AI 问答 — 返回答案"""
    return ai_chat(f"请回答：{question}")


def test_ai_answer():
    """测试 AI 问答功能"""
    # ← 你的代码写在这里
    m = Mock()
    m.return_value = "Python 是一种流行的编程语言，广泛用于 Web 开发和数据分析。"
    with patch(f"{__name__}.ai_chat", m):
        result = ai_answer_question("什么是python")
        print(result)
        assert isinstance(result, str)
        assert len(result) >=10
        assert any(k in result for k in ["Python","编程","语言"])


# ============================================================
# 运行
# ============================================================
# python day31_test_ai_output.py      # 看输出
# pytest day31_test_ai_output.py -v   # 跑测试
