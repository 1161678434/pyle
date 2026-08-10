"""
CI/CD Day 2：GitHub Actions 实战 — 把 YAML 跑起来
==================================================
目标：你的 pytest 第一次在云端自动跑起来

你已经有的：.github/workflows/pytest.yml（上节课的流水线，已写入项目）
今天要做：git init → git push → 看 Actions 标签页 → 理解每一步
"""

# ============================================================
# Part 1：从 0 到第一次 CI 通过（5 步）
# ============================================================
"""
步骤 ①：初始化 git（在项目根目录）
  cd d:\pyle
  git init
  git add .
  git commit -m "init: 接口自动化框架 + 性能测试"

步骤 ②：GitHub 上创建仓库
  浏览器打开 https://github.com/new
  仓库名：pyle
  不要勾选 "Add a README"（会和本地冲突）
  点 Create repository

步骤 ③：关联远程仓库并推送
  git remote add origin https://github.com/你的用户名/pyle.git
  git branch -M main
  git push -u origin main

步骤 ④：看 CI 跑起来
  打开 https://github.com/你的用户名/pyle/actions
  应该看到一条 workflow 正在运行（名字："接口自动化测试"）
  点进去看每一步的实时日志

步骤 ⑤：等结果
  全部绿色 ✓ → CI 通过
  红色 ✗ → 点进去看哪一步挂了
"""

# TODO 1.1：完成上述 5 步，截图 Actions 页面中 "运行测试" 这一步的日志
#           （如果 GitHub 太慢连不上，先把下面 Part 2-4 的 TODO 答完）


# ============================================================
# Part 2：看懂每一步的日志
# ============================================================
"""
CI 跑完后点进去，每个 step 都能展开看日志：

  "检出代码"     → git clone 的日志，能看到 commit hash
  "安装 Python"  → Python 3.12 安装完成
  "安装依赖"     → pip install 的输出
  "启动测试服务器" → Flask 启动，看到 "Running on http://127.0.0.1:5000"
  "运行测试"     → pytest 的输出 —— 你最关心的那一步
  "上传测试报告"  → artifact 打包上传

如果 "运行测试" 是红色的，先看这一步的日志找失败的用例。
不要去翻 "安装 Python" 的日志——那里没有问题。
"""

# TODO 2.1：如果 CI 的 "安装依赖" 步骤挂了，最可能是什么原因？
#           你会怎么修？
# 答：__________________________________

# TODO 2.2：如果 CI 的 "启动测试服务器" 挂了，最可能是什么原因？
# 答：__________________________________


# ============================================================
# Part 3：加一个 job：locust 基准压测
# ============================================================
"""
现在 CI 只跑了 pytest。如果 pytest 全过，还想自动跑一次 locust 基准压测，
确保新代码没有拖慢接口性能。

在 pytest.yml 的 jobs: 下面再加一个 job：

  performance:
    needs: test              ← test job 过了才跑，没过就跳过
    runs-on: ubuntu-latest
    steps:
      - name: 检出代码
        uses: actions/checkout@v4
      - name: 安装 Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: 安装 + 跑压测
        run: |
          pip install locust
          cd auto-test
          python api_test_server.py &
          sleep 2
          locust -f locustfile.py --host=http://127.0.0.1:5000 --headless -u 5 -r 2 -t 15s --only-summary

关键：needs: test 让两个 job 串行——先测功能，功能过了才压性能
"""

# TODO 3.1：needs: test 和不用 needs 直接写两个独立 job，有什么区别？
# 答：__________________________________


# ============================================================
# Part 4：CI 里的环境变量 — 安全存储敏感信息
# ============================================================
"""
不要把 token/密码写在 YAML 里！用 GitHub Secrets：

  ① GitHub 仓库 → Settings → Secrets and variables → Actions
  ② New repository secret
      Name:  API_TOKEN
      Value: eyJhbGci...（你的真实 token）
  ③ YAML 里引用：
      - name: 运行测试
        env:
          TOKEN: ${{ secrets.API_TOKEN }}
        run: pytest --token=$TOKEN

  你的本地 .env 已经做到了代码里不写密码 —— CI 里用 Secrets 是一样的道理
"""

# TODO 4.1：为什么不能把 API token 直接写在 pytest.yml 里？
# 答：__________________________________


# ============================================================
# Part 5：CI 失败排查清单
# ============================================================
"""
你的 CI 挂了，按这个顺序排查，从最常见的开始：

  ① 依赖没装全 → "安装依赖" 那步看看 pip install 有没有报错
  ② 服务器没起来 → "启动测试服务器" 那步有没有看到 Flask 启动日志
  ③ 端口被占 → 上次 CI 的服务器没杀掉，加 if: always() 的 kill 步骤
  ④ 网络不通 → localhost:5000 在 CI 环境里就是那台机器自己，不会有防火墙
  ⑤ 测试用例本身挂了 → 和你本地一样，看 pytest 输出
"""
