"""
接口自动化 Day 2：pytest + requests 整合
========================================
目标：把 Day 1 的裸 requests 调用改写成 pytest 测试用例

核心问题：接口测试到底 assert 什么？
  1. 状态码 — 最基本的
  2. 响应体结构 — 字段存在、类型正确
  3. 响应体内容 — 值符合预期
  4. 响应头 — Content-Type、缓存策略等

用法：pytest api_day2_pytest_requests.py -v
"""

import pytest
import requests

BASE = "http://127.0.0.1:5000"


# ============================================================
# Part 1：最基础的接口测试 — assert 三板斧
# ============================================================

# TODO 1.1：写一个测试函数 test_get_200，请求 /get，断言状态码 == 200
def test_get_200():
    """GET /get 应返回 200"""
    resp = requests.get(BASE + "/get")
    assert resp.status_code == 200


# TODO 1.2：请求 /get，断言 Content-Type 包含 application/json
def test_get_content_type():
    """响应的 Content-Type 应该是 JSON"""
    resp = requests.get(BASE + "/get")
    Content_Type = resp.headers.get("Content-Type","")
    assert "application/json" in Content_Type ,f"期望的 Content-Type 包含 'application/json'，实际为 {Content_Type}"


# TODO 1.3：请求 /get，断言响应 JSON 中包含 method 字段，且值为 "GET"
def test_get_method_field():
    """响应 JSON 中 method 字段应为 GET"""
    resp = requests.get(BASE + "/get")
    data = resp.json()
    method = data.get("method","")
    assert "GET" in method, f"期望 method 为  GET, 实际为 {method} "


# ============================================================
# Part 2：参数化 — 一条用例覆盖多种状态码
# ============================================================

# TODO 2.1：用 @pytest.mark.parametrize 测试多个状态码端点
#           输入: 200, 404, 500
#           断言: response.status_code == 输入值
@pytest.mark.parametrize("code", [200, 404, 500])
def test_status_codes(code):
    """请求 /status/{code}，断言返回对应状态码"""
    resp = requests.get(BASE + f"/status/{code}")
    assert resp.status_code == code, f"期望的状态码{code} ， 实际的状态码 {resp.status_code}"


# ============================================================
# Part 3：数据准备 + 断言响应体
# ============================================================

# TODO 3.1：POST /post 创建用户，断言返回 200 且 json 字段包含发送的数据
def test_post_create_user():
    """POST 创建用户，验证数据回显"""
    payload = {"name": "pytest_user", "role": "qa"}
    # 你的代码
    resp = requests.post(BASE + "/post", json=payload)
    data = resp.json()
    data_json = data.get("json",{})
    assert resp.status_code == 200, f"期望状态码 200 , 实际状态码{resp.status_code}"
    assert data_json.get("name") == payload["name"], f"实际{data_json.get("name")}"
    assert data_json.get("role") == payload["role"], f"实际{data_json.get("role")}"


# TODO 3.2：PUT /put 更新数据，断言 status 字段为 "updated"
def test_put_update():
    """PUT 更新，验证字段值"""
    payload = {"id": 1, "status": "updated"}
    resp = requests.put(BASE + "/put", json=payload)
    data = resp.json()
    assert data["json"]["status"] == "updated"


# ============================================================
# Part 4：fixture — 复用 setup 逻辑
# ============================================================

# TODO 4.1：创建一个 fixture，它返回一个 requests.Session()
#           在 conftest.py 里或者本文件直接写都可以
@pytest.fixture
def session():
    """返回一个 requests.Session 实例"""
    s = requests.Session()
    yield s
    s.close()

# TODO 4.2：用 session fixture 写 test_session_reuse_cookies
#           1. session.get(/cookies/set?token=abc)
#           2. session.get(/cookies) 验证 cookie 被自动携带
def test_session_reuse_cookies(session):
    """Session 自动管理 Cookie，第二次请求应携带"""
    session.get(BASE + "/cookies/set?token=abc")
    resp = session.get(BASE + "/cookies")
    data = resp.json()
    assert data["cookies"]["token"] == "abc"

# ============================================================
# Part 5：异常场景 — 验证"该报错时就报错"
# ============================================================

# TODO 5.1：请求一个不存在的端点 /not-found，断言返回 404
def test_404_on_bad_endpoint():
    """请求不存在的路径，应返回 404"""
    resp = requests.get(BASE + "/not - found")
    assert resp.status_code == 404


# TODO 5.2：请求 /delay/3，设 timeout=1，用 pytest.raises 断言超时
def test_timeout():
    """超短 timeout 应触发超时异常"""
    with pytest.raises(requests.exceptions.Timeout):
        resp = requests.get(BASE + "/delay/3", timeout=1)


