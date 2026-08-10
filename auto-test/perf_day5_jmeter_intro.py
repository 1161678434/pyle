"""
性能测试 Day 5：JMeter 入门（选学）
===================================
目标：知道 JMeter 和 locust 的区别，能打开 JMeter 录一个简单脚本

JMeter 是 Apache 开源的老牌压测工具，GUI 操作，拖拽组件搭建测试计划。
和 locust 的区别：一个靠鼠标点，一个靠写 Python 代码。
"""

# ============================================================
# 一、locust vs JMeter — 选哪个？
# ============================================================
"""
┌──────────┬─────────────────────┬──────────────────────┐
│          │ locust              │ JMeter               │
├──────────┼─────────────────────┼──────────────────────┤
│ 脚本方式  │ 写 Python 代码       │ GUI 拖拽 + XML 配置   │
│ 并发模型  │ 协程（轻量，单机万级）│ 线程（重，单机千级）    │
│ 学习曲线  │ 会 Python 就快       │ 需要学 GUI 操作       │
│ 适合谁    │ 开发/自动化测试      │ 专职性能测试/无代码背景 │
│ 分布式    │ master-worker 简单   │ 需要配多台 slave       │
│ 协议支持  │ 主要是 HTTP          │ HTTP/MySQL/TCP/MQTT… │
│ 报告      │ Web UI + HTML        │ 内置超详细图表报告     │
└──────────┴─────────────────────┴──────────────────────┘

一句话总结：
  你会写 Python → 用 locust，灵活、轻量、好集成 CI
  你不写代码 / 要测数据库和 MQ → 用 JMeter，功能全、但重
"""

# TODO 1.1：你已经会 locust 了，什么场景下你会选 JMeter 而不是 locust？
# 答：__http协议首选locust  ，http协议外优先jmeter________________________________


# ============================================================
# 二、JMeter 三组件模型（知道就行）
# ============================================================
"""
JMeter 的任何测试计划都由三类组件搭积木：

  ① Thread Group（线程组）
     = locust 的 "用户数"
     设置：多少个线程、 ramp-up 时间、循环几次

  ② Sampler（取样器）
     = locust 的 self.client.get/post
     发什么请求：HTTP Request、JDBC Request、TCP Request…

  ③ Listener（监听器）
     = locust 的 Statistics 表 + Charts
     看结果：View Results Tree、Aggregate Report、Graph Results

  你的 locust 经验 → JMeter：
    HttpUser.on_start()     → Thread Group 的 setUp
    @task def xxx():        → HTTP Request Sampler
    self.client.get/...     → Sampler 里选 GET/POST + 填 URL
    Statistics / Charts     → Aggregate Report / Graph Results
"""

# TODO 2.1：locust 的 StepLoadShape（阶梯加压），在 JMeter 里怎么实现？
#           提示：看 Thread Group 的参数
# 答：__设置线程组和循环次数________________________________


# ============================================================
# 三、快速上手（安装 + 录一个请求）
# ============================================================
"""
1. 下载 JMeter（需要 Java 8+）：
   https://jmeter.apache.org/download_jmeter.cgi
   解压 → bin/jmeter.bat 双击启动 GUI

2. 创建一个最简单的测试计划：
   右键 Test Plan → Add → Threads → Thread Group
       线程数：10, Ramp-Up：5 秒, 循环次数：10

   右键 Thread Group → Add → Sampler → HTTP Request
       Server: 127.0.0.1  Port: 5000  Path: /api/users

   右键 Thread Group → Add → Listener → View Results Tree
   右键 Thread Group → Add → Listener → Aggregate Report

   点绿色 ▶ 按钮 → 跑 → 切到 Aggregate Report 看结果

3. 和你的 locust 命令行结果对比：
   locust Statistics 表 = JMeter Aggregate Report
   一样的：Avg / Min / Max / Median / Error%
   多了的：JMeter 有 Throughput 图、Response Time Graph（不用额外配）
"""

# TODO 3.1：下载 JMeter，按上面的步骤跑一次 /api/users 接口，
#           Aggregate Report 里的 Average、Median 分别是多少？
#          和你 locust 跑出来的 4ms/4ms 一样吗？
# 答：Average=__4_  Median=_4_  和 locust 一致___（一致/不一致）


# ============================================================
# 四、最终判断 — 你现在的工具箱
# ============================================================
"""
  接口功能测试：pytest + requests + conftest
  接口性能测试：locust（主力）+ JMeter（了解）
  选型原则：优先 locust，除非需求超出它的能力范围
"""
