"""
Day 22：Playwright 实战整合
=============================
把前三天的内容串起来，完成一个真实的测试场景：
打开网站 → 搜索 → 验证结果 → 截图

不做新知识，只练组合。每个 TODO 都是一个独立的小测试。
"""
from asyncio import wait_for
import re
from playwright.sync_api import sync_playwright, expect


# ============================================================
# TODO 1：Bing 搜索完整流程（用 expect）
# ============================================================
# 把 Day 21 的 TODO 5 完善，加上更多断言

print("=" * 50)
print("TODO 1：Bing 搜索完整流程")
print("=" * 50)

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto("https://www.bing.com")

    # ← 写代码：
    # 1. 搜索框输入 "pytest vs unittest"
    # 2. 按 Enter 搜索
    # 3. expect 等待标题包含关键词
    # 4. expect 断言结果列表可见（搜索结果列表的 id 是 "b_results"）
    # 5. 截图保存 bing_pytest.png
    search_input = page.locator("#sb_form_q")
    search_input.fill("pytest vs unittest")
    search_input.press("Enter")
    search_title = page.title()
    print(f"搜索结果页面标题: {search_title}")
    expect(page).to_have_title("pytest vs unittest - 搜索")
    expect(page.locator("#b_results")).to_be_visible()
    page.screenshot(path="bing_pytest.png")
    browser.close()


# ============================================================
# TODO 2：表单填写 + 提交验证（httpbin 挂了，用代码模拟）
# ============================================================
# 有些页面需要手动等待元素状态变化才能操作，写一个处理流程

print("=" * 50)
print("TODO 2：表单操作流程")
print("=" * 50)

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto("https://example.com")

    # example.com 很简单，我们就练习"等待 → 操作 → 断言"的完整套路
    # 目标：验证页面上 h1、p、a 三个元素

    # ← 写代码：
    # 1. 等 h1 可见
    # 2. 断言 h1 文字
    # 3. 等 p 可见
    # 4. 断言 p 包含 "illustrative" 或 "documentation"
    # 5. 等 a 链接可见
    # 6. 断言 a 的 href 属性
    # 7. 打印所有结果
    page.wait_for_selector("h1")
    expect(page.locator("h1")).to_have_text("Example Domain")
    page.wait_for_selector("p")
    print(f"p 元素文本: {page.locator('p').nth(0).inner_text()}")
    expect(page.locator("p").nth(0)).to_contain_text(re.compile(r"illustrative|documentation"))
    page.wait_for_selector("a")
    print(f"a 的 href: {page.locator('a').get_attribute('href')}")
    expect(page.locator("a").nth(0)).to_have_attribute("href", "https://iana.org/domains/example")
    print(f"h1 文字: {page.locator('h1').inner_text()}")
    print(f"p 文字: {page.locator('p').nth(0).inner_text()}")
    print(f"a 的 href: {page.locator('a').get_attribute('href')}")

    browser.close()


# ============================================================
# TODO 3：多页面管理 + 切换
# ============================================================
# 回忆 Day 19 的 context 和页面切换

print("=" * 50)
print("TODO 3：多页面管理")
print("=" * 50)

with sync_playwright() as p:
    browser = p.chromium.launch()
    context = browser.new_context()          # 创建共享 context
    page1 = context.new_page()
    page1.goto("https://example.com")

    # ← 写代码：
    # 1. 再开一个 page2，打开 httpbin 或 Bing
    # 2. 打印当前 context 下所有页面的标题
    # 3. 验证至少有 2 个页面
    # 4. 用 page1.bring_to_front() 切回第一个页面
    page2 = context.new_page()
    page2.goto("https://www.bing.com")
    print("当前 context 下的页面标题：")
    for page in context.pages:
        print(f"- {page.title()}")
    print(f"页面数量: {len(context.pages)}")
    assert len(context.pages) >= 2, f"页面数量不够，实际是 {len(context.pages)}"
    page1.bring_to_front()
    print(f"切回第一个页面，标题是: {page1.title()}")

    browser.close()


# ============================================================
# TODO 4（思考题）：Playwright 四天回顾
# ============================================================
# 问题 1：从 0 写一个 Playwright 测试，你需要哪几样东西？
#   提示：按顺序列出启动、操作、断言、清理的步骤
# 答案：
# 1. 导入 Playwright 库
# 2. 启动浏览器（launch）
# 3. 创建新页面（new_page）
# 4. 打开目标网址（goto）
# 5. 定位元素（locator 或 get_by_text）
# 6. 执行操作（fill、click、press 等）
# 7. 断言结果（expect）
# 8. 截图（可选）
# 9. 关闭浏览器（close）
# 问题 2：这四天学的内容中，你觉得哪个最容易出错？为什么？
#   提示：定位不到元素？等待不足？网络问题？
# 答案：
# 最容易出错的可能是元素定位和等待问题。因为网页结构复杂多变，元素可能有多个相似的，或者动态加载导致元素暂时不可见。如果定位不准确或者等待时间不足，测试就会失败。

# 问题 3：如果要测试你们公司的登录页面，大概流程是怎样的？
#   提示：打开 → 定位用户名/密码 → fill → 点击登录 → expect 跳转到首页
# 答案：
# 1. 打开登录页面
# 2. 定位用户名输入框，输入用户名
# 3. 定位密码输入框，输入密码
# 4. 定位登录按钮，点击登录
# 5. 等待页面跳转
# 6. 断言跳转后的页面标题或 URL 包含 "首页"
# 7. 可选：断言页面上有用户头像或欢迎信息

# ============================================================
# 运行
# ============================================================
# python day22_playwright_practice.py
