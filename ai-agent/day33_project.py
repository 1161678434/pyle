"""
Day 33：小项目 — 搭建完整 AI 测试套件
======================================
整合 Day 15-32 所有能力：pytest + fixture + mock + patch + AI 输出校验

项目背景：
  你有一个 ai_utils.py（下面模拟），包含 3 个 AI 调用函数。
  你的任务：写一套完整的测试，覆盖成功/失败/边界情况，不烧一分钱。

测试清单：
  ✅ ai_chat      → 关键词 + 长度 + 类型检查
  ✅ ai_classify  → JSON 格式 + 结构完整性
  ✅ ai_summarize → 成功路径 + 失败兜底 + 异常重试

完成后你将拥有一套可直接套用到真实项目的测试模板。
"""
import json
import re
import pytest
from unittest.mock import Mock, patch

# ============================================================
# 模拟 ai_utils.py（不能改 — 这是公司的 AI 调用库）
# ============================================================

import time

def ai_chat(prompt: str) -> str:
    """AI 对话 — 返回文本回复"""
    time.sleep(0.3)  # 模拟网络延迟
    return f"根据您的问题'{prompt[:20]}...'，我建议您从基础开始学习，通过实践巩固知识。"


def ai_classify(text: str, labels: list) -> str:
    """AI 分类 — 返回 JSON 字符串，格式: {"label": str, "confidence": float}"""
    time.sleep(0.2)
    return json.dumps({"label": labels[0], "confidence": 0.92})


def ai_summarize(text: str, max_length: int = 100) -> str:
    """AI 总结 — 返回摘要文本"""
    time.sleep(0.4)
    if len(text) < 10:
        return "文本太短，无法生成摘要"
    return f"摘要({len(text)}字→{max_length}字): {text[:max_length]}..."


# ============================================================
# TODO 1：测试 ai_chat — 关键词 + 长度 + 类型
# ============================================================

print("=" * 50)
print("TODO 1：测试 ai_chat")
print("=" * 50)

# 要求：写 test_ai_chat_returns_valid_response()
#   1. 用 patch 拦截 ai_chat，返回固定文本
#   2. 类型检查：isinstance(result, str)
#   3. 长度检查：len >= 20
#   4. 关键词检查：至少包含 ["建议", "学习", "实践"] 中的一个
#   5. 打印结果 + 3 个 assert

def test_ai_chat_returns_valid_response():
    """测试 AI 对话返回有效回复"""
    # ← 你的代码写在这里
    m = Mock()
    m.return_value = "建议你从基础开始学习 Python，多做实践项目"
    with patch(f"{__name__}.ai_chat", m):
        result = ai_chat("如何学Python")
        print(result)
        assert isinstance(result, str)
        assert len(result) >= 20
        assert any(k in result for k in ["建议", "学习", "实践"])




# ============================================================
# TODO 2：测试 ai_classify — JSON 格式 + 结构完整性
# ============================================================

print()
print("=" * 50)
print("TODO 2：测试 ai_classify")
print("=" * 50)

# 要求：写 test_ai_classify_returns_valid_json()
#   1. 用 patch 拦截 ai_classify，返回合法 JSON 字符串
#   2. json.loads 解析
#   3. 校验结构：必须有 "label"(str) 和 "confidence"(float)
#   4. 校验 confidence 范围：0.0 <= confidence <= 1.0
#   5. assert 各项

def test_ai_classify_returns_valid_json():
    """测试 AI 分类返回合法 JSON"""
    # ← 你的代码写在这里
    m = Mock()
    m.return_value = '{"label": "Python", "confidence": 0.92}'
    with patch(f"{__name__}.ai_classify", m):
        result_str = ai_classify("Python是AI核心语言", ["Python", "Java", "Go"])
        data = json.loads(result_str)
        print(data)
        assert isinstance(data["label"], str)
        assert isinstance(data["confidence"], float)
        assert 0.0 <= data["confidence"] <=1.0


# ============================================================
# TODO 3：测试 ai_summarize — 短文本边界 + 异常重试
# ============================================================

print()
print("=" * 50)
print("TODO 3：测试 ai_summarize")
print("=" * 50)

# 要求 A：写 test_ai_summarize_short_text()
#   1. 用 patch 拦截 ai_summarize
#   2. 模拟"文本太短"场景：ai_summarize 收到短文本时
#   3. 断言返回的摘要里包含"无法生成"或类似提示

def test_ai_summarize_short_text():
    """测试短文本返回提示"""
    # ← 你的代码写在这里
    m = Mock()
    m.return_value = "短小快,无法生成"
    with patch(f"{__name__}.ai_summarize", m):
        result = ai_summarize("短")
        print(result)
        assert "无法生成" in result




# 要求 B：写 test_ai_summarize_with_retry()
#   1. 不用 patch，直接 mock 一个函数模拟"前两次超时，第三次成功"
#   2. 用 side_effect 列表：[ConnectionError, ConnectionError, "摘要: 这是内容..."]
#   3. 写一个 retry_summarize 函数调用这个 mock
#   4. 断言重试 3 次后成功

def retry_summarize(api_func, text: str, max_retries: int = 3) -> str:
    """带重试的总结调用"""
    # ← 你的代码写在这里
    for attempt in range(max_retries):
        try:
            return api_func(text)
        except Exception :
            continue
    return "多次重试后仍然失败"



def test_ai_summarize_with_retry():
    """测试重试机制"""
    # ← 你的代码写在这里
    m = Mock()
    m.side_effect = [
        ConnectionError("超时"),
        ConnectionError("超时"),
        "摘要: Python学习方法总结很难受很长"
    ]
    result = retry_summarize(m, "Python学你方法总结")
    print(result)
    assert "摘要" in result
    assert m.call_count == 3


# ============================================================
# TODO 4（综合）：fixture 管理 mock — 多个测试共享同一个 mock 配置
# ============================================================

print()
print("=" * 50)
print("TODO 4：fixture 共享 mock 配置")
print("=" * 50)

# 场景：ai_chat 会被多个测试用例使用
# 要求：
#   1. 写一个 fixture mock_ai_chat，返回配置好的 mock
#      return_value = "Python 是 AI 测试开发的首选语言，建议从 pytest 开始学习"
#   2. 测试 A：验证包含 "pytest"
#   3. 测试 B：验证包含 "Python"
#   4. 测试 C：验证长度 >= 10

# ← 你的代码写在这里
@pytest.fixture
def mock_ai_chat():
    m = Mock()
    m.return_value = "Python 是 AI 测试开发的首选语言，建议从 pytest 开始学习"
    return m

def test_contains_pytest(mock_ai_chat):
    with patch(f"{__name__}.ai_chat", mock_ai_chat):
        result = ai_chat("测试")
        assert "pytest" in result 
    
def test_contains_python(mock_ai_chat):
    with patch(f"{__name__}.ai_chat", mock_ai_chat):
        result = ai_chat("测试")
        assert "Python" in result

def test_len_enough(mock_ai_chat):
    with patch(f"{__name__}.ai_chat", mock_ai_chat):
        result = ai_chat("测试")
        assert len(result) >= 10



# ============================================================
# 运行
# ============================================================
# pytest day33_project.py -v
