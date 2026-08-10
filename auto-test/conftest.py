"""
conftest.py — pytest 共享 fixture
==================================
pytest 自动加载同目录下的 conftest.py，所有测试文件都能直接使用这里的 fixture。
不用每个文件重复写一遍 setup 逻辑。

fixture 作用域（scope）：
  function  — 每个测试函数调用一次（默认）
  class     — 每个测试类调用一次
  module    — 每个 .py 文件调用一次
  session   — 整个测试会话只调用一次
"""

import pytest
import requests
from config.settings import get_config
from utils.api_logger import log_response

# ---- 从配置读取，不再硬编码 ----
config = get_config()
SERVER = config.BASE_URL


# ============================================================
# fixture 1：base_url — 最简单的 fixture
# ============================================================
@pytest.fixture(scope="session")
def base_url():
    """返回服务器地址。scope=session 表示整个测试只执行一次"""
    return SERVER


# ============================================================
# fixture 2：login_token — 模拟登录获取 token
# ============================================================
@pytest.fixture(scope="function")
def login_token(base_url):
    """
    每个测试用例调用前重新登录，拿到新鲜 token。

    真实场景：
      resp = requests.post(f"{base_url}/api/login", json={
          "username": "qa_user", "password": "test123"
      })
      return resp.json()["token"]
    """
    resp = requests.post(f"{base_url}/api/login", json={
        "username": "qa_tester",
        "password": "test123"
    })
    assert resp.status_code == 200, f"登录失败: {resp.status_code}"
    token = resp.json()["token"]
    print(f"\n  [fixture] 获取到 token: {token[:20]}...")
    return token


# ============================================================
# fixture 3：auth_headers — 把 token 拼成请求头
# ============================================================
@pytest.fixture(scope="function")
def auth_headers(login_token):
    """把 token 拼成 Authorization 头，直接传给需要鉴权的接口"""
    return {"Authorization": f"Bearer {login_token}"}


# ============================================================
# fixture 4：api_session — 已登录的 Session（最常用）
# ============================================================
@pytest.fixture(scope="function")
def api_session(base_url, login_token):
    """
    返回一个已登录的 requests.Session：
      - Cookie 自动管理
      - Authorization 头已写好
      - 测试结束自动关闭

    这是真实项目中最常用的 fixture 形态。
    """
    s = requests.Session()
    s.hooks['response'].append(log_response)  # ← 自动记录每个请求
    s.headers.update({
        "Authorization": f"Bearer {login_token}",
        "User-Agent": "QATest/1.0"
    })
    yield s
    s.close()
    print(f"\n  [fixture] Session 已关闭")
