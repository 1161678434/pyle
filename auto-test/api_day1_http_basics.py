"""
接口自动化 Day 1：HTTP 基础回顾
=================================
目标：用测试工程师的视角重新审视 HTTP — 每个请求/响应都是待测对象

工具：requests + httpbin.org（免费 HTTP 测试服务）
"""

import requests

BASE = "http://127.0.0.1:5000"



# --- GET：获取资源 ---
# TODO 1.1：用 GET 请求 /get，打印状态码和响应 JSON
def todo_1_1_get():
    """发送 GET 请求并检查响应"""
    # 你的代码：
    response = requests.get(BASE + "/get")
    print(f"状态码,{response.status_code}")
    try:
        data = response.json()
        print(f"响应, json",data)
    except Exception as e:
        print(f"响应不是有效的json，或者解析失败", e)



# TODO 1.2：用 GET 请求 /get?page=2&size=10（带查询参数），确认参数回显在响应的 args 字段
def todo_1_2_get_with_params():
    """带查询参数的 GET 请求"""
    # 你的代码：
    response = requests.get(BASE + "/get", params={"page": 2, "size": 10})
    data = response.json()
    print(f"响应, json",data)
    assert "args" in data


# --- POST：创建资源 ---
# TODO 1.3：用 POST 请求 /post，发送 JSON body: {"name": "test_user", "role": "qa"}
#            确认响应中的 json 字段回显了你发送的数据
def todo_1_3_post_json():
    """POST 请求发送 JSON 数据"""
    # 你的代码：
    payload = {"name": "test_user", "role": "qa"}
    response = requests.post(BASE + "/post", json=payload)
    try:
        data = response.json()
        assert data["json"]["name"] == "test_user"
        assert data["json"]["role"] == "qa"
        print(f"数据回显正确")
    except Exception as e:
        print("解析或断言失败:", e)


# TODO 1.4：用 POST 请求 /post，发送 form 数据: username=admin&password=123456
#            对比和 JSON 方式的区别
def todo_1_4_post_form():
    """POST 请求发送表单数据"""
    # 你的代码：
    payload = {"username":"admin","password":"123456"}
    response = requests.post(BASE + "/post", data=payload )
    print(f"状态码,{response.status_code}")
    try:
        data = response.json()
        print(f"响应, json",data)
    except Exception as e:
         print("解析失败:", e)


# --- PUT：更新资源（全量替换）---
# TODO 1.5：用 PUT 请求 /put，发送 JSON body: {"id": 1, "status": "updated"}
#            确认响应中 json 字段包含更新后的数据
def todo_1_5_put():
    """PUT 请求更新资源"""
    # 你的代码：
    payload = {"id": 1, "status": "updated"}
    response = requests.put(BASE + "/put", json=payload)
    print(f"1.5状态码，{response.status_code}")
    try:
        data = response.json()
        assert data["json"]["id"] == 1
        assert data["json"]["status"] == "updated"
        print(f"全部通过")
    except Exception as e:
        print("解析失败:", e)


# --- DELETE：删除资源 ---
# TODO 1.6：用 DELETE 请求 /delete，打印状态码
def todo_1_6_delete():
    """DELETE 请求"""
    # 你的代码：
    response = requests.delete(BASE + "/delete")
    print(f"1.6状态码，{response.status_code}")


# ============================================================
# Part 2：状态码 — 测试的核心断言点
# ============================================================

# TODO 2.1：请求 /status/200，验证返回 200
def todo_2_1_status_200():
    """验证 200 OK"""
    # 你的代码：
    response = requests.get(BASE + "/status/200")
    print(f"2.1状态码{response.status_code}")
    assert response.status_code == 200

# TODO 2.2：请求 /status/404，验证返回 404（requests 默认不抛异常，用 assert 检查）
def todo_2_2_status_404():
    """验证 404 Not Found"""
    # 你的代码：
    response = requests.get(BASE + "/status/404")
    print(f"2.2状态码 {response.status_code}")
    assert response.status_code == 404


# TODO 2.3：请求 /status/500，验证返回 500
def todo_2_3_status_500():
    """验证 500 Server Error"""
    # 你的代码：
    response = requests.get(BASE + "/status/500")
    print(f"2.3状态码 {response.status_code}")
    assert response.status_code == 500


# TODO 2.4：请求 /redirect/3（自动跟随 3 次重定向），打印最终 URL 和状态码
#            提示：用 response.history 查看重定向链
def todo_2_4_redirect():
    """跟踪重定向链"""
    # 你的代码：
    response = requests.get(BASE + "/redirect/3")
    print(f"最终URL {response.url}")
    print(f"最终状态码 {response.status_code}")
    print(f"重定向次数 {len(response.history)}")
    for i,resp in enumerate(response.history,1):
        print(f"{i}.{resp.status_code}-->{resp.url}")


# TODO 2.5：请求 /redirect/3，但禁止跟随重定向（allow_redirects=False），观察状态码
def todo_2_5_no_redirect():
    """禁止重定向"""
    # 你的代码：
    response = requests.get(BASE + "/redirect/3",allow_redirects=False)
    print(f"2.5态码 {response.status_code}")


# ============================================================
# Part 3：Headers — 请求头和响应头
# ============================================================

# TODO 3.1：请求 /headers，发送自定义 Header: X-Test-Id: qa-2026
#            确认响应中的 headers 字段回显了自定义头
def todo_3_1_custom_header():
    """发送自定义请求头"""
    # 你的代码：
    headers = {"X-Test-Id": "qa-2026"}
    response = requests.get(BASE + "/headers", headers=headers)
    print(f"3.1 态码 {response.status_code}")
    print(f"请求头 {response.json()["headers"]}")



# TODO 3.2：请求 /response-headers?X-Custom=hello（让服务器返回自定义响应头）
#            打印响应的所有 headers，找出 X-Custom
def todo_3_2_response_header():
    """读取响应头"""
    # 你的代码：
    response = requests.get(BASE + "/response-headers?X-Custom=hello")
    print(f"3.2 态码 {response.status_code}")
    headers = response.headers
    print(f"请求头 {response.headers}")
    for key,value in headers.items():
        print(f"{key}: {value}")
    custom_value = headers.get("X-Custom")
    if custom_value:
        print(f"X-Custom 的值{custom_value}")
    else:
        print(f"没有找到 X-Custom")


# TODO 3.3：请求 /get，观察默认的 User-Agent 是什么
#            然后修改 User-Agent 为 Mozilla/5.0 Chrome，再次请求，对比变化
def todo_3_3_user_agent():
    """修改 User-Agent"""
    # 你的代码：
    response = requests.get(BASE + "/get")
    headers = response.json()["headers"]["User-Agent"]
    print(f"请求头{headers}")
    User_Agent = headers
    if User_Agent:
        print(f"User_Agent 的值{User_Agent}")
    else:
        print(f"User_Agent 没找到")
    headers = {"User-Agent": "Mozilla/5.0 Chrome"}
    response = requests.get(BASE + "/get",headers=headers)
    User_Agent_M = response.json()["headers"]["User-Agent"]
    print(f"修改后的 User_Agent {User_Agent_M}")


# ============================================================
# Part 4：综合练习
# ============================================================

# TODO 4.1：用 httpbin 模拟完整 CRUD 流程
#   1. POST /post 创建用户（JSON body: name, role）
#   2. GET /get?id=<从步骤1获取>
#   3. PUT /put 更新用户状态
#   4. DELETE /delete 删除用户
#   每步都打印状态码和关键响应字段
def todo_4_1_crud_flow():
    """完整 CRUD 流程"""
    # 你的代码：
    post_resp = requests.post(BASE + "/post", json={"name":"zhangsan", "role": 1})
    name = post_resp.json()["json"]["name"]
    role = post_resp.json()["json"]["role"]
    print(f"post 状态码{post_resp.status_code}")
    print(f"name {name}")
    print(f"id {role}")
    get_resp = requests.get(BASE + "/get",params={"id": role})
    print(f"get状态码{get_resp.status_code}")
    print(f"id{get_resp.json()["args"]["id"]}")
    put_resp = requests.put(BASE + "/put",json={"id": role, "status": "updated"})
    print(f"put 响应状态{put_resp.status_code}")
    print(f"更新状态 {put_resp.json()["json"]["status"]}")
    delete_resp = requests.delete(BASE + "/delete", json={"name":"zhangsan", "role": 1})
    print(f"delete 状态码{delete_resp.status_code}")



# TODO 4.2：模拟接口测试中常见的异常场景
#   a) 超时：请求 /delay/3，设置 timeout=1，捕获异常
#   b) 连接失败：请求 http://localhost:99999（不存在的服务），捕获异常
#   c) 无效 JSON：假设响应不是 JSON，尝试 .json() 并捕获异常
def todo_4_2_error_handling():
    """异常场景处理"""
    # 你的代码：
    #）a
    print("--------a) 超时 ---")
    try:
        resp = requests.get(BASE + "/delay/3", timeout=1)
        print("成功(不应该看到这行):",resp.status_code)
    except requests.exceptions.ConnectionError:
        print(f"捕获异常 ConnectionError : 目标服务不存在")
    except requests.exceptions.ReadTimeout:
        print(f"捕获异常 ReadTimeout : 目标服务不存在")
    print(f"------b) 连接失败")
    try:
        resp = requests.get("http://localhost:999")
        print("成功(不应该看到这行):",resp.status_code)
    except requests.exceptions.ConnectionError:
        print(f"捕获异常 ConnectionError : 目标服务不存在")
    
    print(f"------c) 无效json")
    
    resp = requests.get(BASE + "/this-does-not-exist")
    print(f"状态码 {resp.status_code}")
    print(f"Content-Type: {resp.headers.get('Content-Type')}")
    try:
        data = resp.json()
        print("成功(不应该看到这行):",data)
    except requests.exceptions.JSONDecodeError:
        print("捕获到 JSONDecodeError：响应不是 JSON 格式")
        print(f"实际返回内容前80字符: {resp.text[:80]}")


# ============================================================
# 运行入口
# ============================================================
if __name__ == "__main__":
    print("=" * 50)
    print("Part 1: HTTP 方法")
    print("=" * 50)
    todo_1_1_get()
    todo_1_2_get_with_params()
    todo_1_3_post_json()
    todo_1_4_post_form()
    todo_1_5_put()
    todo_1_6_delete()

    print("\n" + "=" * 50)
    print("Part 2: 状态码")
    print("=" * 50)
    todo_2_1_status_200()
    todo_2_2_status_404()
    todo_2_3_status_500()
    todo_2_4_redirect()
    todo_2_5_no_redirect()

    print("\n" + "=" * 50)
    print("Part 3: Headers")
    print("=" * 50)
    todo_3_1_custom_header()
    todo_3_2_response_header()
    todo_3_3_user_agent()

    print("\n" + "=" * 50)
    print("Part 4: 综合练习")
    print("=" * 50)
    todo_4_1_crud_flow()
    todo_4_2_error_handling()
