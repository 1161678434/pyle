"""
接口自动化 Day 4：框架搭建 — 目录结构 + 配置分离 + allure 报告
=============================================================
目标：从"散落的测试文件"升级为"可维护的测试框架"

今日三个核心：
  1. 配置分离 — 环境切换不靠改代码
  2. 目录结构 — 文件各司其职
  3. allure 报告 — 测试结果可视化

用法：
  pytest api_day4_framework.py -v                        # 正常跑
  pytest api_day4_framework.py -v --alluredir=reports    # 生成 allure 数据
  allure serve reports                                    # 浏览器打开报告
  pytest api_day4_framework.py -v --junitxml=reports/test_report.xml  # XML 报告
"""

import pytest
import requests
import allure
from config.settings import get_config


# ============================================================
# Part 1：配置分离 — 从硬编码到配置读取
# ============================================================

# TODO 1.1：用 get_config() 获取当前环境的配置，打印 BASE_URL
def test_config_loaded():
    """验证配置加载成功"""
    cfg = get_config()
    print(f"当前环境 BASE_URL: {cfg.BASE_URL}")
    assert "127.0.0.1" in cfg.BASE_URL


# TODO 1.2：手动指定 staging 环境，打印 BASE_URL，确认和 dev 不同
def test_staging_config():
    """手动切换环境"""
    cfg = get_config("staging")
    print(f"当前环境 BASE_URL: {cfg.BASE_URL}")
    assert "127.0.0.1" not in cfg.BASE_URL


# TODO 1.3：用 conftest 的 base_url fixture 请求 /get，验证 200
#           （conftest 已改为从 config 读取 SERVER）
def test_use_config_in_request(base_url):
    """用配置中的 BASE_URL 发请求"""
    resp = requests.get(f"{base_url}/get")
    print(f"状态码{resp.status_code}, url {base_url}")
    assert resp.status_code == 200


# ============================================================
# Part 2：框架目录结构（思考题）
# ============================================================
#
# 2.1 为什么不要把 BASE_URL 写在测试函数里？
# 答：_多次使用，就要写多条，url变动时改动很大，写在配置里面就可以改一个地方映射到全局_________________________________


# ============================================================
# Part 3：allure 报告
# ============================================================

# allure 装饰器：
#   @allure.feature("模块名")     → 给测试分类
#   @allure.story("子功能")       → 子分类
#   @allure.title("用例标题")     → 自定义用例名
#   with allure.step("步骤描述"):  → 标记测试步骤

# TODO 3.1：给下面的测试方法填充代码，并在方法体内用 allure.step 标记步骤
@allure.feature("用户管理")
class TestUserAPI:
    """用户接口测试 — 演示 allure 报告结构"""

    @allure.story("创建用户")
    @allure.title("POST /post 创建新用户")
    def test_create_user(self, base_url):
        """创建用户并验证回显——用 allure.step 标记每一步"""
        with allure.step("发送 POST 请求 携带用户数据"):
            payload = {"name": "allure_user", "role": "qa"}
            resp = requests.post(f"{base_url}/post",json=payload)

        with allure.step("断言状态码 200"):
            assert resp.status_code == 200
        with allure.step("断言name字段回显正确"):
            assert resp.json()["json"]["name"] == "allure_user"

    @allure.story("查询用户")
    @allure.title("GET /get 查询用户信息")
    def test_get_user(self, base_url):
        """查询用户"""
        with allure.step("发送get "):
            resp = requests.get(f"{base_url}/get")
        with allure.step("断言状态码  200"):
            assert resp.status_code == 200 
        with allure.step("返回数据包含用户信息"):
            data = resp.json()
        with allure.step("返回数据包含method字段"):
            assert data["method"] == "GET"



# TODO 3.2：不用 allure，用 pytest 原生方式生成报告
#           运行：pytest api_day4_framework.py -v --junitxml=reports/test_report.xml
#           然后查看 reports/test_report.xml 的内容


# ============================================================
# Part 4：综合 — config + conftest + allure 三合一
# ============================================================

@allure.feature("鉴权测试")
class TestAuthWithFramework:
    """完整框架集成示例"""

    @allure.story("Token 鉴权")
    @allure.title("有效 token 可访问受保护接口")
    def test_valid_token(self, base_url, api_session):
        """
        三层协作：
          配置层 → 提供 base_url（dev/staging/prod 自动切换）
          Fixture层 → api_session 已登录，自带 token
          用例层 → 只写业务断言
        """
        with allure.step("使用登录的 api_session 请求保护接口 /api/user/profile"):
            resp = api_session.get(f"{base_url}/api/user/profile")
        with allure.step("断言状态码  200"):
            assert resp.status_code == 200 ,f"期望 200  实际 {resp.status_code}"

    @allure.story("Token 鉴权")

    @allure.title("无 token 应返回 401")
    def test_no_token_401(self, base_url):
        """验证鉴权生效"""
        with allure.step("不带认证的请求受保护接口"):
            resp = requests.get(f"{base_url}/api/user/profile")
        with allure.step("断言  401  "):
            assert resp.status_code == 401
        with allure.step("验证返回值没有token"):
            data = resp.json()
            assert "error" in data or "message" in data, \
            f"期望错误提示，实际：{data}"
