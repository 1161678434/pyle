"""
性能测试 Day 2：locust 入门 — 写脚本 + 看 Web UI
===============================================
目标：能独立写出压测脚本，能看懂 Web UI 的实时图表

你已经有的：locustfile.py（Day 1 用来跑概念演示的那个）
今天要做：自己改写它，跑起来，看懂 4 个核心图表
"""

# ============================================================
# Part 1：locustfile 结构拆解
# ============================================================
"""
打开你现有的 locustfile.py，结构如下：

┌─ ① from locust import HttpUser, task, between
│
├─ ② class ApiUser(HttpUser):        ← 一个类 = 一种用户类型
│       wait_time = between(1, 2)     ← 每个请求之间的等待间隔
│
│       def on_start(self):           ← 用户开始压测前执行一次（类似 conftest 的 setup）
│           ... 登录，拿 token ...
│
│       @task(3)                      ← 权重 3 — 这个操作最常见
│       def get_profile(self):
│           self.client.get(...)      ← self.client 是 locust 给的 HTTP 客户端
│
│       @task(1)                      ← 权重 1 — 这个操作比较少
│       def create_user(self):
│           self.client.post(...)
│
└─ ③ 运行：
      locust -f locustfile.py --host=http://127.0.0.1:5000
"""

# TODO 1.1：locustfile.py 里 @task(3) 和 @task(1) 的权重是什么意思？
#           如果把 get_profile 改成 @task(6)，整个脚本跑 100 个请求，
#           大概有多少个是 get_profile？多少个是 list_users？
# 答: @task(3) 占比所有请求的30% 
#     @task(1)  占比所有请求的10%
#     改成@@task(6) get_profile是60个 ,list_users 是 20个 __________________________________


# TODO 1.2：self.client 是什么？和 requests.get/post 有什么区别？
# 答：自动记录性能数据的requests会话工具。 
# 在 Locust 脚本中，千万别用 requests.get，所有请求必须用 self.client，否则压测报告就是一张白纸__________________________________


# ============================================================
# Part 2：动手改脚本 — 加一个新的压测场景
# ============================================================
"""
当前 locustfile.py 测了 3 个接口：
  - GET  /api/user/profile
  - GET  /api/users
  - POST /api/users

TODO 2.1：加一个 DELETE 接口的压测——随机删除一个用户
          提示：先在 on_start 里创建一批用户存到列表里，
          delete 时随机从列表选一个 id。

改完后的结构：
  class ApiUser(HttpUser):
      def on_start(self):
          ... 登录 + 创建 5 个测试用户 ...
          self.user_ids = [1, 2, 3, 4, 5]

      @task(3)  def get_profile(self): ...
      @task(2)  def list_users(self): ...
      @task(1)  def create_user(self): ...
      @task(1)  def delete_user(self):        ← 新增
          import random
          uid = random.choice(self.user_ids)
          self.client.delete(f"/api/users/{uid}")
"""


# ============================================================
# Part 3：Web UI 四个核心图表
# ============================================================
"""
启动 Web UI：
  locust -f locustfile.py --host=http://127.0.0.1:5000
  浏览器打开 http://localhost:8089

填入用户数 10、每秒启动 2 个、点击 Start

四个标签页逐个看：

  ① Statistics（统计表）— 和 headless 模式输出的那张表一样
     每个接口的 请求数/失败率/平均/P50/P95/P99/RPS
     这是最常用的一张表

  ② Charts（图表）— 三条曲线实时变化
     - Total Requests Per Second（RPS 曲线）
     - Response Times（响应时间，ms）
     - Number of Users（用户数曲线）

     TODO 3.1：观察 RPS 曲线，用户数从 0 慢慢涨到 10 的过程中
               RPS 是跟着一起线性涨，还是提前到顶？
               这说明了什么？
     答：跟着一起增长，随着用户量增多，单位内请求数量变多，处理数据便便，导致rps增长__________________________________

  ③ Failures（失败）— 出问题了看这里

  ④ Download Data（下载数据）— 导出 CSV，写报告用
"""


# ============================================================
# Part 4：自定义负载策略 — 不只是"慢慢加人"
# ============================================================
"""
默认模式是"固定用户数"，locust 还支持更复杂的策略。

TODO 4.1：把下面这段代码加到 locustfile.py 最上面，
          然后跑：locust -f locustfile.py --host=http://127.0.0.1:5000

  class StepLoadShape(LoadTestShape):
      '''阶梯式压测：每 30 秒翻倍用户数'''
      stages = [
          (30, 5),    # 前 30s → 5 用户
          (60, 10),   # 30-60s → 10 用户
          (90, 20),   # 60-90s → 20 用户
          (120, 40),  # 90-120s → 40 用户
      ]

      def tick(self):
          run_time = self.get_run_time()
          for stage_duration, stage_users in self.stages:
              if run_time < stage_duration:
                  return (stage_users, 1)  # (用户数, 每秒启动数)
          return None  # 结束

观察：和默认模式相比，图表上用户数是"阶梯状"增长的
"""


# ============================================================
# Part 5：性能测试的执行流程（今天学完你应该能回答）
# ============================================================
"""
TODO 5.1：一个完整的性能测试从开始到结束，应该有哪些步骤？
# 答：① 需求分析     ← "这次压测的目标是什么？"
    把业务需求翻译成技术指标
    例："双 11 要扛 10 万 QPS" → 目标：单接口 P95 < 200ms，TPS > 1000

② 脚本开发     ← 写 locustfile.py（你今天学的）
    不是测所有接口，是测"核心链路"
    例：电商 → 搜索商品 → 加购物车 → 下单（3 个接口）

③ 环境确认     ← 在什么环境跑？
    绝对不要在线上跑！用 staging / 专属压测环境
    确认数据库有足够测试数据（不然后面白跑）

④ 基准测试     ← 先用 1 个用户跑一次
    确认脚本正确、数据正常、指标有基准线
    基准线 = "单用户时这个接口多快"

⑤ 阶梯加压     ← 逐步加用户找瓶颈（你刚写的 StepLoadShape）
    10→20→50→100→200→... 每档停 5 分钟
    观察：RPS 什么时候不涨了？响应时间什么时候开始恶化？

⑥ 瓶颈定位     ← 找到限制因素
    是 CPU 满了？数据库慢了？线程池不够？
    这一般要和服务端日志/监控一起看

⑦ 调优 + 复测  ← 开发改完再跑一次验证
    循环 ⑤→⑥→⑦ 直到达标
    出报告：把每轮压测的 RPS/P95/失败率画成趋势图
__________________________________
"""
