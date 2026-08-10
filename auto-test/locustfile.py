"""
Locust 压测脚本 — 针对本地测试服务器的用户 CRUD 接口
=====================================================
启动：locust -f locustfile.py --host=http://127.0.0.1:5000
然后浏览器打开 http://localhost:8089
"""

from locust import HttpUser, task, between, LoadTestShape


# ============================================================
# 三种负载策略（用哪个就把哪个类的名字改成 ActiveShape，
#          或者删掉另两个，locust 只认一个 LoadTestShape 子类）
# ============================================================

class StepLoadShape(LoadTestShape):          # ← 策略 A：阶梯加压
    '''阶梯式压测：每 30 秒翻倍用户数 — 找系统瓶颈'''
    stages = [
        (30, 5), (60, 10), (90, 20), (120, 40)
    ]
    def tick(self):
        run_time = self.get_run_time()
        for stage_duration, stage_users in self.stages:
            if run_time < stage_duration:
                return (stage_users, 1)
        return None
"""

class SpikeLoadShape(LoadTestShape):         # ← 策略 B：尖峰测试
    '''模拟瞬时流量洪峰 — 突然涌入大量用户，几十秒后退去'''
    def tick(self):
        run_time = self.get_run_time()
        if run_time < 20:
            return (10, 5)                   # 0-20s：10 用户正常
        elif run_time < 30:
            return (100, 50)                 # 20-30s：10 秒内跳到 100 用户！
        elif run_time < 50:
            return (10, 10)                  # 30-50s：退回到 10 用户
        elif run_time < 60:
            return (100, 50)                 # 50-60s：又一次尖峰
        return None
"""
"""
class SoakLoadShape(LoadTestShape):          # ← 策略 C：稳定性负载
    '''长时间稳定压测 — 检测内存泄漏、连接池泄漏'''
    def tick(self):
        run_time = self.get_run_time()
        if run_time < 30:
            return (20, 5)                   # 前 30s 爬坡到 20 用户
        elif run_time < 300:
            return (20, 20)                  # 保持 20 用户 4.5 分钟
        return None                          # 生产环境这个时间设为 2~24 小时
"""

class ApiUser(HttpUser):
   
    """模拟一个 API 用户的行为"""
    wait_time = between(1, 2)  # 每个请求之间等 1-2 秒

    def on_start(self):
        import random
        vuser_id = random.randint(1, 99999)
        """用户登录（和 conftest.py 的 login_token 思路一样）"""
        resp = self.client.post("/api/login", json={
            "username": "qa_tester",
            "password": "test123"
        })
        self.token = resp.json()["token"]

        """创建多个用户ID"""
        self.user_ids = []
        for i in range(5):
            name = f"load_{vuser_id}_{i}"
            resp = self.client.post("/api/users", json={"name": name})
            self.user_ids.append(resp.json()["id"])    # ← 存真实 ID


    @task(3)  # 权重 3 — 读操作最常见
    def get_profile(self):
        self.client.get(
            "/api/user/profile",
            headers={"Authorization": f"Bearer {self.token}"}
        )

    @task(2)  # 权重 2 — 查列表
    def list_users(self):
        self.client.get("/api/users")

    @task(1)  # 权重 1 — 创建用户（写操作相对少）
    def create_user(self):
        import random
        name = f"perf_user_{random.randint(1, 10000)}"
        self.client.post("/api/users", json={"name": name})

    @task(1)
    def delete_user(self):
        import random
        if not self.user_ids:
            name = f"refill_{random.randint(1, 99999)}"
            resp = self.client.post("/api/users", json={"name": name})
            self.user_ids.append(resp.json()["id"])
        uid = self.user_ids.pop()
        self.client.delete(f"/api/users/{uid}")
