# 🤖 AI Agent 测试开发工程师 — 互动学习计划

**学员背景**：学到 `def` 类定义，有软件测试经验，无自动化测试经验
**目标**：3-4个月独立完成 AI Agent
**学习方式**：每天互动式手把手教学

---

## 📅 第一阶段(第1-14天)：Python强化 + 第一次调用AI

| 天数 | 主题 | 互动任务 | 预计时长 |
|------|------|---------|---------|
| Day 1 | Python类深入 | 写一个类并和我讨论 | 1.5h |
| Day 2 | 类的高级用法 | 继承、魔术方法 | 1.5h |
| Day 3 | 异常处理 | try/except实战 | 1.5h |
| Day 4 | 文件操作 | 读写文件 + 日志 | 1.5h |
| Day 4.5 | **调试实战** | print/log/断点/VS Code调试 | 1.5h |
| Day 5 | **调用AI第一天** | 用你的API key写第一个AI脚本 | 2h |
| Day 6 | **多轮对话** | 消息管理、命令拦截、上下文裁剪 | ✅ 完成 |
| Day 7 | **系统提示词 + 参数** | system prompt、temperature/top_p/stop | ⏳ 进行中 |
| Day 8 | 上下文管理 | max_tokens限制、token计数 | 1.5h |
| Day 9 | 流式响应 | streaming输出的实现 | 1.5h |
| Day 10 | 巩固+小项目 | 做一个AI问答工具 | 2h |
| Day 11-12 | requests库 | 直接HTTP调API | 1.5h |
| Day 13 | JSON处理 | 解析复杂响应 | 1.5h |
| Day 14 | 环境变量巩固 | dotenv管理密钥复习 | 1h |

---

## 📅 第二阶段(第15-30天)：自动化测试 + UI自动化 + 测试AI

### 第一周：pytest 基础能力（Day 15-18）

| 天数 | 主题 | 学习目标 | 预计时长 |
|------|------|---------|---------|
| Day 15 | pytest 入门 | `assert` 断言、测试函数命名规则、`pytest` 命令行运行、测试通过/失败的输出怎么看 | 1.5h |
| Day 16 | 异常测试 + 参数化 | `pytest.raises()` 捕获异常、`@pytest.mark.parametrize` 一组数据跑多个用例 | 1.5h |
| Day 17 | fixture 入门 | `@pytest.fixture` 准备测试数据、测试函数如何使用 fixture、执行顺序 | 1.5h |
| Day 18 | fixture 进阶 | `scope` 控制生命周期、`conftest.py` 共享 fixture、yield 做 teardown 清理 | 1.5h |

### 第二周：Playwright UI 自动化（Day 19-22）

| 天数 | 主题 | 学习目标 | 预计时长 |
|------|------|---------|---------|
| Day 19 | Playwright 入门 | 安装、启动浏览器、打开页面、截图、基本断言 | 1.5h |
| Day 20 | 元素定位 | CSS 选择器、text 定位、role 定位、点击、输入文本 | 1.5h |
| Day 21 | 等待 + 断言 | 自动等待机制、`expect()` 断言页面内容、表单提交 | 1.5h |
| Day 22 | Playwright 实战 | 整合：用 Playwright 测试一个实际页面（多步操作 + 断言） | 2h |

### 第三周：Appium 移动端自动化（Day 23-26）

| 天数 | 主题 | 学习目标 | 预计时长 |
|------|------|---------|---------|
| Day 23 | Appium 环境搭建 + 第一个脚本 | Appium Server、Android SDK、模拟器配置、`appium-python-client`、启动 App 并截图 | 2h |
| Day 24 | 元素定位 | ID、XPath、Accessibility ID、class name、UIAutomator2 定位、点击、输入 | 1.5h |
| Day 25 | 手势操作 + 断言 | 滑动、长按、拖拽、`assert` 验证元素文本/属性 | 1.5h |
| Day 26 | Appium 实战 | 整合：完整的 App 操作流程（登录页 → 首页 → 退出）| 2h |

### 第四周：mock/patch + 测试 AI（Day 27-34）

| 天数 | 主题 | 学习目标 | 预计时长 |
|------|------|---------|---------|
| Day 27 | mock 入门 | 为什么需要 mock？`unittest.mock.Mock` 创建假对象、`return_value` 伪造返回值 | 1.5h |
| Day 28 | mock 实战 | `side_effect` 模拟多次调用、断言 mock 的调用次数和参数 | 1.5h |
| Day 29 | patch 补丁 | `@patch` 装饰器替换真实对象、`patch.object` 精确替换、不消耗 API 额度跑测试 | 1.5h |
| Day 30 | 组合实战 | 综合 fixture + mock + patch 完整测试一个 AI 调用函数 | 1.5h |
| Day 31 | 测试 AI 输出（一）| 关键词断言（响应必须包含 XX）、长度检查、类型检查 | 1.5h |
| Day 32 | 测试 AI 输出（二）| JSON 格式校验、结构完整性检查、敏感信息检查 | 1.5h |
| Day 33 | 小项目 Day1-2 | 搭建完整测试套件，覆盖 `ai_utils.py` + 边界用例 | 2h |
| Day 34 | 小项目 Day3 + 总结 | 测试报告（`pytest --html`）、覆盖率（`pytest-cov`）、第二阶段总结 | 2h |

### 技能树

```
pytest 线           Web UI 自动化线       移动端自动化线         整合线
Day 15 ─→ assert  Day 19 ─→ Playwright  Day 23 ─→ Appium      Day 27-34
Day 16 ─→ raises  Day 20 ─→ 元素定位    Day 24 ─→ 元素定位  ─→ mock/patch
Day 17 ─→ fixture Day 21 ─→ 等待+断言   Day 25 ─→ 手势操作  ─→ 测试 AI
Day 18 ─→ scope   Day 22 ─→ 整合实战    Day 26 ─→ 整合实战  ─→ 完整套件
```

> **Playwright 和 Appium 的关系**：Playwright 测 Web 端，Appium 测移动原生 App。两者的测试思想（元素定位、等待、断言）是通用的，先学 Playwright 打基础，再学 Appium 会快很多。

---

## 📅 第三阶段(第35-55天)：AI Agent入门

| 天数 | 主题 | 互动任务 |
|------|------|---------|
| Day 35-39 | Function Calling | 让AI调用函数 |
| Day 40-45 | ReAct模式 | 思考-行动循环 |
| Day 46-50 | 多工具Agent | 搜索+计算+查询 |
| Day 51-55 | **第一个Agent** | 可用的智能助手 |

---

## 📅 第四阶段(第56-76天)：LangChain框架

| 天数 | 主题 |
|------|------|
| Day 56-61 | LangChain基础 |
| Day 62-68 | LangChain Agent |
| Day 69-76 | Agent测试套件 |

---

## 📅 第五阶段(第77-96天)：评估+独立项目

| 天数 | 主题 |
|------|------|
| Day 77-84 | Agent评估体系 |
| Day 85-96 | **独立完成Agent项目** |

---

## 📝 如何使用这个计划

每天你来找我，告诉我今天是第几天，我会：
1. 📖 讲解今天的概念（5-10分钟）
2. 💻 给出代码示例 + 需要修改的部分
3. ✏️ 给你一个实操任务
4. ✅ 检查你的代码，反馈指导
