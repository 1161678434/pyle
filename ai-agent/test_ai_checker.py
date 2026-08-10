# test_ai_checker.py
import pytest
from ai_checker import ask_deepseek

test_data = [
    ("你好", True, None),
    ("1+1等于几", True, "2"),
    ("", True, None),
]

@pytest.mark.parametrize("prompt, expected_success, keyword", test_data)
def test_ds_reply(prompt, expected_success, keyword):
    result = ask_deepseek(prompt)
    assert result["success"] == expected_success, f"调用失败：{result['error']}"
    assert result["reply"] is not None and len(result["reply"]) > 0, "回复为空"
    if keyword:
        assert keyword in result["reply"], f"未找到关键词'{keyword}'，实际：{result['reply']}"

def test_reply_is_not_blank():
    result = ask_deepseek("介绍一下你支持的功能")
    assert result["success"]
    assert len(result["reply"]) > 10, f"回复过短：{result['reply']}"