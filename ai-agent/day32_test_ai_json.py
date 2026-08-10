"""
Day 32：测试 AI 输出（二）— JSON 校验、结构完整性、敏感信息检查
=================================================================
回顾 Day 31：关键词、长度、类型 — 对"自由文本"做模糊检查
Day 32 升级：AI 返回结构化数据（JSON），你要做精确的结构校验

三种进阶检查：
1. JSON 格式校验 — AI 返回的是合法 JSON 吗？（经常丢括号、多逗号）
2. 结构完整性 — JSON 里有没有必填字段？字段类型对不对？
3. 敏感信息检查 — AI 有没有泄露手机号、身份证、邮箱？

学完今天你能：
- 用 try/except + json.loads 验证 JSON 合法性
- 写 schema 校验函数，检查 AI 输出的结构
- 用正则表达式扫描敏感信息泄露
"""

import json
import re
import pytest
from unittest.mock import Mock, patch

# ============================================================
# 模拟 AI 服务
# ============================================================

def ai_extract_info(text: str) -> str:
    """模拟 AI 提取信息 — 应该返回 JSON 字符串"""
    pass


# ============================================================
# 第一部分：JSON 格式校验 — "能解析出来吗？"
# ============================================================

print("=" * 50)
print("第一部分：JSON 格式校验")
print("=" * 50)

# AI 返回 JSON 经常出的问题：
#   1. 多一个逗号 → {"name": "张三",}    ← 最后一个逗号
#   2. 少一个引号 → {"name": 张三}       ← 值没加引号
#   3. 用了单引号 → {'name': '张三'}      ← JSON 必须双引号
#   4. 回复里夹了废话 → "好的，结果如下：{"name": "张三"}"

# 正确做法：用 try/except 包裹 json.loads()
def is_valid_json(text: str) -> bool:
    """检查字符串是不是合法 JSON"""
    try:
        json.loads(text)
        return True
    except json.JSONDecodeError as e:
        print(f"  JSON 解析失败: {e}")
        return False


good_json = '{"name": "张三", "age": 30, "city": "北京"}'
bad_json_1 = '{"name": "张三", "age": 30, "city": "北京",}'   # 多余逗号
bad_json_2 = '{"name": 张三, "age": 30}'                      # 值缺引号
bad_json_3 = "返回结果：{'name': '张三'}"                       # 单引号 + 废话

print(f"合法 JSON: {is_valid_json(good_json)}")     # True
print(f"多余逗号: {is_valid_json(bad_json_1)}")     # False
print(f"缺引号:   {is_valid_json(bad_json_2)}")     # False
print(f"单引号+废话: {is_valid_json(bad_json_3)}")  # False


# ============================================================
# 第二部分：结构完整性 — "该有的字段都有吗？类型对吗？"
# ============================================================

print()
print("=" * 50)
print("第二部分：结构完整性检查")
print("=" * 50)

# 场景：AI 应该返回一个用户信息 JSON
# 要求：name(str)、age(int)、skills(list)
# 这叫"schema 校验"——不看具体值，看结构和类型

EXPECTED_SCHEMA = {
    "name": str,
    "age": int,
    "skills": list,
}

def validate_schema(data: dict, schema: dict) -> dict:
    """校验 JSON 数据的结构是否完整，类型是否正确"""
    errors = []
    for field, expected_type in schema.items():
        # 检查字段是否存在
        if field not in data:
            errors.append(f"缺少字段: {field}")
            continue
        # 检查字段类型
        if not isinstance(data[field], expected_type):
            actual = type(data[field]).__name__
            expected = expected_type.__name__
            errors.append(f"字段 {field} 类型错误: 期望 {expected}，实际 {actual}")
    return {"valid": len(errors) == 0, "errors": errors}


# 测试数据
valid_data = {"name": "李四", "age": 25, "skills": ["Python", "测试"]}
missing_field = {"name": "李四", "age": 25}                     # 缺 skills
wrong_type = {"name": 74, "age": "二十五", "skills": []}    # age 是 str 不是 int

print(f"正常数据: {validate_schema(valid_data, EXPECTED_SCHEMA)}")
print(f"缺少字段: {validate_schema(missing_field, EXPECTED_SCHEMA)}")
print(f"类型错误: {validate_schema(wrong_type, EXPECTED_SCHEMA)}")


# ============================================================
# 第三部分：敏感信息检查 — "AI 有没有泄露隐私？"
# ============================================================

print()
print("=" * 50)
print("第三部分：敏感信息检查")
print("=" * 50)

# AI 有时候会"编造"数据，如果编出了真实的手机号、身份证——这就是隐私泄露
# 用正则表达式扫描常见敏感信息

def check_sensitive_info(text: str) -> list:
    """扫描文本中的敏感信息，返回发现的问题列表"""
    patterns = {
        "手机号": r"1[3-9]\d{9}",
        "身份证": r"\d{17}[\dXx]",
        "邮箱": r"\w+@\w+\.\w+",
    }
    findings = []
    for name, pattern in patterns.items():
        matches = re.findall(pattern, text)
        if matches:
            findings.append(f"发现疑似{name}: {matches}")
    return findings


safe_text = "用户张三: ，联系电话：已加密，地址：北京朝阳区, "
leak_text = "用户李四，手机：13812345678，身份证：110101199001011234，邮箱：lisi@test.com"

print(f"安全文本: {check_sensitive_info(safe_text)}")   # []
print(f"泄露文本: {check_sensitive_info(leak_text)}")   # [手机号, 身份证, 邮箱]


# ============================================================
# TODO 1：把三段检查串起来 — 一个完整的 AI 输出验证器
# ============================================================

print()
print("=" * 50)
print("TODO 1：综合 AI 输出验证器")
print("=" * 50)

# 需求：写 validate_ai_json_response(text, required_fields)
# 流程：
#   1. JSON 格式校验 — 能用 json.loads 解析吗？
#   2. 结构完整性 — 必填字段都在吗？类型对吗？
#   3. 敏感信息 — 有没有泄露身份证/手机号/邮箱？
#
# 返回：
# {
#   "valid_json": True/False,
#   "json_error": str or None,
#   "schema_errors": [...],
#   "sensitive_findings": [...],
#   "all_passed": True/False    ← 三项全过才为 True
# }

def validate_ai_json_response(text: str, required_fields: dict) -> dict:
    """完整验证 AI 返回的 JSON"""
    # ← 你的代码写在这里
    result = {
        "valid_json": True,
        "json_error": None,
        "schema_errors": [],
        "sensitive_findings":[],
    }

    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        result["valid_json"] = False
        result["json_error"] = str(e)
        result["all_passed"] = False
        return result
    # json解析成功，校验结构
    schema_result = validate_schema(data, required_fields)
    result["schema_errors"] = schema_result["errors"]
    # 扫描敏感信息
    result["sensitive_findings"] = check_sensitive_info(text)
    #判断 all——passed ， return
    result["all_passed"] = (
        result["valid_json"] 
        and len(result["schema_errors"]) == 0
        and len(result["sensitive_findings"]) == 0
    )
    return result



# 写完用下面的测试验证
def test_complete_validator():
    # case 1: 完美数据
    r = validate_ai_json_response(
        '{"name": "王五", "age": 30, "skills": ["Go", "运维"]}',
        {"name": str, "age": int, "skills": list}
    )
    assert r["all_passed"] == True
    assert r["valid_json"] == True
    assert r["schema_errors"] == []
    assert r["sensitive_findings"] == []

    # case 2: JSON 格式错误
    r = validate_ai_json_response(
        '{name: "王五", age: 30,}',
        {"name": str, "age": int}
    )
    assert r["all_passed"] == False
    assert r["valid_json"] == False
    assert r["json_error"] is not None

    # case 3: 缺少字段 + 泄露敏感信息
    r = validate_ai_json_response(
        '{"name": "赵六", "phone": "13800001111"}',
        {"name": str, "age": int, "email": str}
    )
    assert r["all_passed"] == False
    assert len(r["schema_errors"]) > 0           # 缺 age 和 email
    assert len(r["sensitive_findings"]) > 0      # 手机号

    print("✅ 全部通过")





# ============================================================
# TODO 2：mock + 结构化输出验证
# ============================================================

print()
print("=" * 50)
print("TODO 2：mock 拦截 + JSON 校验")
print("=" * 50)

# 场景：ai_extract_info 应该返回一个 JSON 字符串
#   你测试时 mock 它返回各种情况进行验证

def parse_user_info(user_text: str) -> dict:
    """解析用户信息 — 调用 AI 提取并返回 dict"""
    json_str = ai_extract_info(user_text)
    return json.loads(json_str)


def test_parse_user_info():
    """测试用户信息解析"""
    # ← 你的代码写在这里
    # 1. mock ai_extract_info，返回合法 JSON
    # 2. 调用 parse_user_info
    # 3. 验证返回的 dict 包含 name 和 age
    # 4. 再 mock 一次返回非法 JSON，验证 throw 了 json.JSONDecodeError
    m = Mock()
    m.return_value = '{"name": "张三", "age": 25}'
    with patch(f"{__name__}.ai_extract_info",m):
        result = parse_user_info("用户张三，25岁")
        assert result == {"name": "张三", "age": 25}

    m2 = Mock()
    m2.return_value = '{"这不是合法json'
    with patch(f"{__name__}.ai_extract_info", m2):
        with pytest.raises(json.JSONDecodeError):
            parse_user_info(f"任意输入")


# ============================================================
# TODO 3（思考题）：真实场景的安全检查
# ============================================================

print()
print("=" * 50)
print("TODO 3：安全检查思考")
print("=" * 50)

# 问题 1：敏感信息检查用正则就够了，还是有更好的方案？
# 
# 问题 2：如果 AI 把手机号分段写，比如 "138 1234 5678"，你的正则会漏掉吗？
# 问题 3：JSON schema 校验除了手写 if 判断，有什么现成的库？

"""
# 提示
# 1. 正则适合快速扫描。更严谨的可以用 pydantic 做 schema 校验。
#    生产环境常用：pydantic + 自定义 validator
# 2. 会漏。实际生产中敏感信息检测是"底线防护"，
#    不能替代"不要让 LLM 处理原始 PII"
# 3. pydantic、marshmallow、cerberus 都是 schema 校验库。
#    Day 33 小项目会用到。
"""


# ============================================================
# 运行
# ============================================================
# python day32_test_ai_json.py        # 看教学示例
# pytest day32_test_ai_json.py -v     # 还没测试函数，先看 TODO 1 的 test_complete_validator
