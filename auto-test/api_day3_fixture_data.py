"""
接口自动化 Day 3：fixture 管理测试数据
======================================
目标：学会用 fixture 管理 token、base_url、登录态，不再硬编码

conftest.py 已提供了 4 个 fixture，本文件直接使用它们：
  base_url      → session 级别，整个测试会话共享
  login_token   → function 级别，每个用例重新登录
  auth_headers  → function 级别，token 拼好的请求头
  api_session   → function 级别，已登录的 Session 对象

用法：pytest api_day3_fixture_data.py -v
      pytest api_day3_fixture_data.py -v -s   （加 -s 看 fixture 的 print 输出）
"""

import pytest
import requests


# ============================================================
# Part 1：使用 base_url fixture — 告别硬编码
# ============================================================

class TestPart1BaseURL:
    """所有测试方法用同一个 base_url，不再重复写 URL"""

    # TODO 1.1：用 base_url fixture 替换硬编码 URL
    def test_get_with_fixture(self, base_url):
        """用 base_url fixture 请求 /get"""
        # 你的代码（不要写 http://127.0.0.1:5000）
        resp = requests.get(f"{base_url}/get")
        assert resp.status_code == 200 

    # TODO 1.2：用 base_url 请求 /status/200
    def test_status_with_fixture(self, base_url):
        """用 base_url fixture 请求 /status/200"""
        resp = requests.get(f"{base_url}/status/200")
        assert resp.status_code == 200 

# ============================================================
# Part 2：token 管理 — 登录 → 获取 → 使用
# ============================================================

class TestPart2Token:
    """演示 token 的完整生命周期"""

    # TODO 2.1：用 login_token fixture，验证 token 不为空
    def test_token_not_empty(self, login_token):
        """login_token 应该是一个非空字符串"""
        assert login_token is not None, f"token 为 None"
        assert isinstance(login_token,str), f"token 不是字符串"
        assert len(login_token) >0, f"token 为 空字符串"

    # TODO 2.2：用 auth_headers fixture 请求 /api/user/profile，
    #           断言返回 200 且 name 字段存在
    def test_profile_with_token(self, base_url, auth_headers):
        """用带 token 的 headers 请求用户信息接口"""
        resp = requests.get(f"{base_url}/api/user/profile", headers=auth_headers)
        assert resp.status_code == 200, f"状态不是200,实际状态为{resp.status_code}"
        assert "name" in resp.json(), f"实际出参  {resp.json()}"
        assert resp.json()["name"], f"name 字段为空"


    # TODO 2.3：不带 token 请求 /api/user/profile，断言返回 401
    def test_profile_without_token_401(self, base_url):
        """不带 Authorization 头，应该返回 401"""
        resp = requests.get(f"{base_url}/api/user/profile")
        assert resp.status_code == 401 ,f" 实际状态为{resp.status_code}"


# ============================================================
# Part 3：api_session — 一键登录的 Session（最常用）
# ============================================================

class TestPart3Session:
    """api_session 是 token + cookie 的合集，生产环境最常见的 fixture"""

    # TODO 3.1：用 api_session 请求 /api/user/profile，断言 200
    def test_profile_with_session(self, base_url, api_session):
        """api_session 已自带 Authorization 头"""
        resp = api_session.get(f"{base_url}/api/user/profile")
        assert resp.status_code == 200

    # TODO 3.2：用 api_session 先后请求两个接口，
    #           验证 Authorization 头都被携带
    def test_session_persists_headers(self, base_url, api_session):
        """同一个 Session 多次请求都携带 Authorization"""
        resp1 = api_session.get(f"{base_url}/api/user/profile")
        resp2 = api_session.get(f"{base_url}/headers")
        assert resp1.status_code == 200
        assert "Authorization" in resp2.json()["headers"],f"1不存在 Authorization, 返回内容为{resp2.json()["headers"]}"



# ============================================================
# Part 4：fixture 作用域理解
# ============================================================

# 思考题（不需要写代码，运行后观察输出即可回答）：
#
# 4.1 base_url fixture 的 scope 是 "session"，login_token 是 "function"，
#     整个测试跑完，base_url 执行了几次？login_token 执行了几次？
#     （提示：加 -s 参数运行，看 fixture 里的 print 输出次数）
#答 base_url 6次   login_token 4词 
# 4.2 为什么 token 用 scope="function"（每个用例重新登录），
#     而不用 scope="session"（只登录一次）？
#     提示：考虑 token 过期、用例间数据隔离
#答： token 会有过期的时候，会影响后续用力执行

# TODO 4.3：自己写一个 scope="module" 的 fixture，体会作用域区别
#           要求：记录 fixture 被调用的次数，用 print 输出
@pytest.fixture(scope="module")
def module_counter():
    """module 级别 fixture，整个文件只执行一次"""
    # 你的代码
    print("/n [modu fixture] 初始化 - 整个文件只执行这一次")
    return {"count": 0}


def test_module_fixture_1(module_counter):
    """第一次使用 module_counter"""
    module_counter["count"] +=1
    print(f"test1 调用后 count = {module_counter["count"]}")


def test_module_fixture_2(module_counter):
    """第二次使用 module_counter，应看到 print 只输出一次"""
    module_counter["count"] +=1
    print(f"test2 调用后 count = {module_counter["count"]}")