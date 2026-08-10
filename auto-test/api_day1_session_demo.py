"""
接口自动化：Session & Cookie 管理演示
=====================================
实战演示三种常见模式：
  1. requests.Session() — 自动管理 Cookie（像浏览器一样）
  2. 手动提取 Token — 从登录响应拿到 token，拼到后续请求头
  3. 混合模式 — Cookie + Token 同时存在的情况

对比：不用 Session vs 用 Session
"""

import requests

BASE = "http://127.0.0.1:5000"
V = {"verify": False}  # 公司代理 SSL 问题，生产环境去掉

# ============================================================
# 模式 1：requests.Session() — 自动管理 Cookie
# ============================================================
"""
原理：
  不用 Session：每次 request 都是独立请求，Cookie 不会自动传递
  用 Session：Session 内部维护一个 cookie jar，服务器返回 Set-Cookie 后
             后续请求自动带上 Cookie 头 —— 和浏览器行为一致
"""

def demo_session_cookie():
    print("=== 模式 1：Session 自动管理 Cookie ===")

    s = requests.Session()
    #第一步：请求设置 cookie（模拟登录后服务器下发 session）
    r1 = s.get(f"{BASE}/cookies/set?session_id=abc123")
    print(f"1. 服务器 Set-Cookie: {r1.cookies.get_dict()}")

    # 第二步：请求 /cookies，查看携带了哪些 cookie
    #         因为用了 Session，上一步的 cookie 自动带上了
    r2 = s.get(f"{BASE}/cookies")
    print(f"2. 自动携带的 Cookie: {r2.json()['cookies']}")

    # 第三步：再设一个 cookie，观察累积
    s.get(f"{BASE}/cookies/set?user_role=qa")
    r3 = s.get(f"{BASE}/cookies")
    print(f"3. 累积的 Cookie: {r3.json()['cookies']}")

    # 对比：不用 Session
    print("\n--- 对比：不用 Session ---")
    requests.get(f"{BASE}/cookies/set?session_id=xyz789")
    r4 = requests.get(f"{BASE}/cookies")
    print(f"4. 不用 Session: {r4.json()['cookies']}  ← 空的！Cookie 丢了")

    s.close()


# ============================================================
# 模式 2：手动提取 Token（最常见场景）
# ============================================================
"""
原理：
  登录接口返回 JSON：{"token": "eyJhbG...", "user_id": 42}
  你需要：
    1. 从响应 JSON 提取 token
    2. 拼到后续请求的 Header：Authorization: Bearer <token>
  Session 不会自动帮你做这件事 —— Token 是业务逻辑，Cookie 是传输层
"""

def demo_token_management():
    print("\n=== 模式 2：手动管理 Token ===")

    # 模拟登录（httpbin 没有真实登录接口，用 /post 模拟响应回显）
    login_resp = requests.post(f"{BASE}/post", json={
        "username": "qa_tester",
        "password": "test123"
    })

    # --- 关键步骤 1：从登录响应提取 token ---
    # 真实场景：token = login_resp.json()["token"]
    # 这里用 httpbin 回显来演示模式
    import hashlib
    token = hashlib.md5(b"qa_tester").hexdigest()
    print(f"1. 登录成功，提取 token: {token}")

    # --- 关键步骤 2：token 拼到后续请求头 ---
    headers = {"Authorization": f"Bearer {token}"}

    r2 = requests.get(f"{BASE}/get", headers=headers)
    print(f"2. GET 携带 Authorization: {r2.json()['headers'].get('Authorization')}")

    r3 = requests.post(f"{BASE}/post", headers=headers, json={"action": "create"})
    print(f"3. POST 同样携带: {r3.json()['headers'].get('Authorization')}")

    # --- 关键步骤 3：Token 过期 → 重新登录 ---
    print("\n>> 真实测试用例的典型写法：")
    print("""
    def login():
        '''每个用例调用它获取新鲜 token'''
        resp = requests.post("/api/login", json={"user": "qa", "pwd": "xxx"})
        assert resp.status_code == 200
        token = resp.json()["token"]
        return {"Authorization": f"Bearer {token}"}

    def test_create_order():
        headers = login()       # ← 用例开始前获取 token
        resp = requests.post("/api/orders", headers=headers, json={...})
        assert resp.status_code == 201
    """)


# ============================================================
# 模式 3：Cookie + Token 混合（真实接口最常见的模式）
# ============================================================

def demo_mixed():
    print("\n=== 模式 3：Session（Cookie）+ 手动（Token）混合 ===")

    s = requests.Session()
    s.headers.update({"User-Agent": "QATest/1.0"})  # Session 级固定头

    # 模拟登录：同时获得 cookie 和 token
    s.get(f"{BASE}/cookies/set?PHPSESSID=server_cookie")
    token = "eyJhbGciOiJIUzI1NiJ9.eyJ1c2VyIjoicWEifQ.signature"
    s.headers.update({"Authorization": f"Bearer {token}"})

    # 后续请求：Cookie 自动带 + Token 手动带，两者都有
    r = s.get(f"{BASE}/get")
    result = r.json()
    print(f"Cookie（自动）: {result['cookies']}")
    print(f"Token（手动）: {result['headers'].get('Authorization')}")

    s.close()


# ============================================================
# 总结：映射到 pytest fixture（Day 3 会详细讲）
# ============================================================
"""
@pytest.fixture(scope="function")  # 每个用例独立 session
def api():
    s = requests.Session()
    resp = s.post("https://api.example.com/login", json={
        "username": "qa", "password": "test123"
    }, verify=False)
    token = resp.json()["token"]
    s.headers.update({"Authorization": f"Bearer {token}"})
    yield s   # ← 测试用例拿到的是已登录的 session
    s.close()

def test_profile(api):
    r = api.get("https://api.example.com/user/profile")
    assert r.status_code == 200
    assert r.json()["role"] == "qa"

# 10 个用例？每个都有独立的登录 session，互不干扰
"""


if __name__ == "__main__":
    demo_session_cookie()
    demo_token_management()
    demo_mixed()
