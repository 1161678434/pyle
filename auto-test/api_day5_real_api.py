"""
接口自动化 Day 5：实战 — 测一个真实 CRUD API
============================================
目标：把 Day 1-4 学的内容整合，完整测试一个增删改查接口

被测接口（api_test_server.py 已新增）：
  GET    /api/users         列表
  GET    /api/users/<id>    详情
  POST   /api/users         创建（name 必填、重名返回 409）
  PUT    /api/users/<id>    更新
  DELETE /api/users/<id>    删除
  POST   /api/users/reset   重置数据

用法：
  pytest api_day5_real_api.py -v
  pytest api_day5_real_api.py -v --alluredir=reports
"""

import pytest
import requests
import allure

API = "/api/users"


# ============================================================
# Part 1：基础 CRUD — 增删改查一条龙
# ============================================================

@allure.feature("用户 CRUD")
class TestUserCRUD:

    # TODO 1.1：创建用户 POST /api/users，断言 201 且返回的 name 正确
    def test_create_user(self, base_url):
        requests.post(f"{base_url}{API}/reset")
        """POST 创建用户"""
        payload = {"name": "CRUD"}

        with allure.step("调用post请求创建用户CRUD"):
            resp = requests.post(f"{base_url}{API}",json=payload)
            assert resp.status_code == 201
        with allure.step(f"验证返回用户"):
            data = resp.json()
            assert "name" in data,f"响应中缺少name字段，实际为{data}"
            assert data["name"] == payload["name"],f"期望 name = {payload["name"]},实际name = {data["name"]}"

    # TODO 1.2：查询用户列表 GET /api/users，断言返回的 users 是列表且至少包含 1 条
    def test_list_users(self, base_url):
        with allure.step(f"创建用户"):
            requests.post(f"{base_url}{API}/reset")
            payload =  {"name": "CRUD1"}
            resp = requests.post(f"{base_url}{API}",json=payload)
            assert resp.status_code == 201

        """GET 用户列表"""
        with allure.step(f"请求用户列表"):
            resp = requests.get(f"{base_url}{API}")
            assert resp.status_code == 200
        with allure.step(f"验证users 是列表 且至少包含1条"):
            data = resp.json()
            users = data["users"]
            assert isinstance(users,list),f"期望users 是列表，实际是{type(users)}"
            assert len(users) >= 1 ,f"期望列表至少包含 1条, 实际上{len(users)}"

    # TODO 1.3：查询单个用户 GET /api/users/1，断言返回的 id=1
    def test_get_user_by_id(self, base_url):
        """GET 单个用户"""
        requests.post(f"{base_url}{API}/reset")
        with allure.step(f"创建用户"):
            payload = {"name": "test"}
            resp = requests.post(f"{base_url}{API}",json=payload)
            user_id = resp.json()["id"]
            assert resp.status_code == 201 , f"期望用户创建成功, 实际用户创建失败, 状态码 是{resp.status_code}"
        with allure.step(f"调用户查询接口"):
            resp = requests.get(f"{base_url}{API}/{user_id}")
            assert resp.status_code == 200
        with allure.step(f"断言 id = user_id"):
            data = resp.json()
            assert data["id"] == user_id ,f"期望id= {user_id} , 实际id 为{data["id"]}"

    # TODO 1.4：更新用户 PUT /api/users/1，修改 name，断言返回的 name 已更新
    def test_update_user(self, base_url):
        """PUT 更新用户"""
        requests.post(f"{base_url}{API}/reset")
        with allure.step(f"创建用户"):
            payload = {"name": "test"}
            resp = requests.post(f"{base_url}{API}",json=payload)
            user_id = resp.json()["id"]
            assert resp.status_code == 201 , f"期望用户创建成功, 实际用户创建失败, 状态码 是{resp.status_code}"
        with allure.step(f"调用更新用户接口"):
            payload = {"name": "new_name"}
            resp = requests.put(f"{base_url}{API}/{user_id}", json=payload)
            assert resp.status_code == 200, f"期望请求200 , 实际请求{resp.status_code}"
        with allure.step(f"修改name, 验证name已更新"):
            data = resp.json()
            assert data["name"] == payload["name"], f"实际anme 为{data["name"]}"


    # TODO 1.5：删除用户 DELETE /api/users/1，断言删除后查不到（GET 返回 404）
    def test_delete_user(self, base_url):
        """DELETE 删除用户"""
        requests.post(f"{base_url}{API}/reset")
        with allure.step(f"创建用户"):
            payload = {"name": "test"}
            resp = requests.post(f"{base_url}{API}",json=payload)
            user_id = resp.json()["id"]
            assert resp.status_code == 201 , f"期望用户创建成功, 实际用户创建失败, 状态码 是{resp.status_code}"
        with allure.step(f"调用删除接口, 删除用户"):
            resp = requests.delete(f"{base_url}{API}/{user_id}")
            assert resp.status_code == 200 ,f"期望状态 200 , 实际状态{resp.status_code}"
        with allure.step(f"查新用户是是否不在,不存在返回404"):
            resp = requests.get(f"{base_url}{API}/{user_id}")
            assert resp.status_code == 404 ,f"期望状态404, 实际状态{resp.status_code}"


# ============================================================
# Part 2：异常场景 — 验证接口的错误处理
# ============================================================

@allure.feature("用户 CRUD 异常")
class TestUserErrors:

    # TODO 2.1：创建用户时不传 name，断言返回 400
    def test_create_without_name_400(self, base_url):
        """缺少必填字段应返回 400"""
        requests.post(f"{base_url}{API}/reset")
        with allure.step(f"创建用户不传name,返回400"):
            resp = requests.post(f"{base_url}{API}")
            assert resp.status_code == 400 ,f"期望结果缺少必填参数返回400, 实际结果{resp.status_code}"

    # TODO 2.2：创建同名的用户，断言返回 409 Conflict
    def test_duplicate_name_409(self, base_url):
        """重名应返回 409"""
        requests.post(f"{base_url}{API}/reset")
        with allure.step(f"调用创建用户接口，创建成功返回200"):
            payload = {"name": "CRUD"}
            resp = requests.post(f"{base_url}{API}", json=payload)
            assert resp.status_code == 201, f"期望结果200 ,  实际结果{resp.status_code}"
        with allure.step(f"再次调用相同用户创建，创建失败，返回409"):
            resp = requests.post(f"{base_url}{API}", json=payload)
            assert resp.status_code == 409, f"期望结果409 实际结果{resp.status_code}"

    # TODO 2.3：查询不存在的用户 GET /api/users/999，断言返回 404
    def test_get_nonexistent_404(self, base_url):
        """查不存在的用户应返回 404"""
        with allure.step(f"查询不在在用用户，返回 404"):
            resp = requests.get(f"{base_url}{API}/999")
            assert resp.status_code == 404 ,f"期望结果404 ,  实际结果{resp.status_code}"


    # TODO 2.4：更新不存在的用户 PUT /api/users/999，断言返回 404
    def test_update_nonexistent_404(self, base_url):
        """更新不存在的用户应返回 404"""
        with allure.step(f"更新不存在的用户, 返回404"):
            payload = {"name": "ming"}
            resp = requests.put(f"{base_url}{API}/999", json=payload)
            assert resp.status_code == 404, f"期望结果404, 实际结果 {resp.status_code}"


# ============================================================
# Part 3：数据依赖 — 两个用例的串行流程
# ============================================================

@allure.feature("用户 CRUD 流程")
class TestUserWorkflow:

    # TODO 3.1：完整业务流程
    #   1. 先重置数据（POST /api/users/reset）
    #   2. 创建用户 A
    #   3. 查询列表，确认有 1 条
    #   4. 更新用户 A 的 role
    #   5. 查询用户 A，确认 role 已变
    #   6. 删除用户 A
    #   7. 查询列表，确认 0 条
    def test_full_lifecycle(self, base_url):
        """用户从创建到删除的完整生命周期"""
        with allure.step(f"重置数据"):
            requests.post(f"{base_url}{API}/reset")
        with allure.step(f"创建用户A"):
            payload = {"name": "用户A"}
            resp = requests.post(f"{base_url}{API}", json=payload)
            assert resp.status_code == 201 ,f"创建接口请求成功 201 , 实际请求结果{resp.status_code}"
        with allure.step(f"确认用户创建成功, 且有一个用户A"):
            resp = requests.get(f"{base_url}{API}")
            data = resp.json()
            user_id = data["users"][0]["id"]
            assert isinstance(data["users"], list),f"期望返回是列表,实际返回是{type(data["users"])}"
            assert len(data["users"]) == 1 ,f"期望用户数 1个, 实际用户数{len(data["users"])}"
            assert data["users"][0]["name"] == payload["name"],f"期望用户为用户A, 实际用户为{data["name"]}"
        with allure.step(f"确认用户A, 被更新为用户B"):
            payload = {"name": "用户B"}
            resp = requests.put(f"{base_url}{API}/{user_id}", json=payload)
            assert resp.status_code == 200,f"期望请求 200 , 实际请求{resp.status_code}"
            data = resp.json()
            assert data["name"] == payload["name"],f"期望name 为用户B, 实际用户为{data["name"]}"
            

        with allure.step(f"删除用户, 检查用户列表没有用户"):
            delete_user = requests.delete(f"{base_url}{API}/{user_id}")
            assert delete_user.status_code == 200 ,f"期望删除成功, 实际删除失败状态码为{delete_user.status_code}"
            resp = requests.get(f"{base_url}{API}")
            data = resp.json()
            assert len(data["users"]) == 0, f"期望用户数为0 , 实际用户数{len(data["users"])}"




