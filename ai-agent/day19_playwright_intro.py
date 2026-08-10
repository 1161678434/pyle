"""
Day 19：Playwright 入门 —— 启动浏览器、打开页面、截图
=========================================================
从今天开始，你能用代码操控浏览器了——打开网页、点击按钮、
输入文字、截图留证，全部自动化。

核心概念：
- browser  → 浏览器实例（一个 Playwright 可以开多个）
- page     → 标签页（你的所有操作都在 page 上完成）
- 每个操作都是异步的，但 Playwright 的 sync_api 帮我们屏蔽了复杂性
"""
from playwright.sync_api import Browser, sync_playwright
import os

# ============================================================
# 第一部分：Hello Playwright —— 启动浏览器
# ============================================================
# 三件套：启动 → 打开页面 → 关闭
#
# with sync_playwright() as p:
#     browser = p.chromium.launch()     # 启动 Chromium
#     page = browser.new_page()         # 新建标签页
#     page.goto("https://example.com")  # 打开网址
#     browser.close()                   # 关闭浏览器


# ============================================================
# TODO 1：打开百度首页，截图
# ============================================================
# 打开 https://www.baidu.com，截图保存为 baidu_home.png

print("=" * 50)
print("TODO 1：打开百度首页")
print("=" * 50)

# ← 写代码：
# 1. 用 with sync_playwright() as p:
# 2. browser = p.chromium.launch()
# 3. page = browser.new_page()
# 4. page.goto("https://www.baidu.com")
# 5. page.screenshot(path="baidu_home.png")
# 6. browser.close()
# 7. 用 print 打印页面标题 page.title()
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto("https://www.baidu.com")
    page.screenshot(path="baidu_home.png")
    print(f"页面标题: {page.title()}")
    browser.close()
    

# ============================================================
# TODO 2：获取页面基本信息
# ============================================================
# 打开 example.com，提取标题和 URL，验证内容

print("=" * 50)
print("TODO 2：提取页面信息")
print("=" * 50)

# ← 写代码：打开 https://example.com
# 用 page.title() 获取标题
# 用 page.url 获取当前 URL
# 用 assert 验证标题和 URL 是否符合预期
# （example.com 的标题是 "Example Domain"）
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto("https://example.com")
    title = page.title()
    url = page.url
    assert title == "Example Domain", f"标题不对，实际是 {title}"
    assert url == "https://example.com/", f"URL 不对，实际是 {url}"
    print("标题和 URL 验证通过！")
    browser.close()

# ============================================================
# TODO 3：多页面切换
# ============================================================
# Playwright 可以同时管理多个标签页

print("=" * 50)
print("TODO 3：多标签页")
print("=" * 50)

# ← 写代码：
# 1. 打开 example.com
# 2. page2 = browser.new_page() 再开一个标签页
# 3. page2.goto("https://httpbin.org/get")
# 4. 用 len(browser.pages) 获取当前打开的标签页数量
# 5. assert 验证至少有 2 个页面
with sync_playwright() as p:
    
    browser = p.chromium.launch()
    context = browser.new_context()

    page1 = context.new_page()
    page1.goto("https://example.com")

    page2 = context.new_page()
    page2.goto("https://httpbin.org/get")
    num_pages = len(context.pages)
    assert num_pages >= 2, f"页面数量不对，实际是 {num_pages}"
    print(f"当前打开的标签页数量：{num_pages}")
    browser.close()

# ============================================================
# TODO 4（思考题）
# ============================================================
# 问题 1：page.goto() 和你在浏览器地址栏输入网址有什么区别？
# 答：page.goto() 是 Playwright 提供的一个方法，用于在自动化脚本中导航到指定的 URL。它会等待页面加载完成后才继续执行后续代码。而在浏览器地址栏输入网址是用户手动操作，浏览器会立即开始加载页面，但不会有自动等待的机制。使用 page.goto() 可以确保你的脚本在页面完全加载后再进行下一步操作，避免因为页面未加载完成而导致的错误。
# 问题 2：headless（无头）模式是什么意思？默认是开还是关？
#    试试：p.chromium.launch(headless=False) 看看效果
# 答：headless 模式指的是浏览器在没有图形界面（即无头）的情况下运行，这通常用于自动化测试和服务器环境中。默认情况下，Playwright 启动的浏览器是 headless 模式，也就是说你看不到浏览器窗口。如果你想看到浏览器的操作过程，可以将 headless 参数设置为 False，例如 p.chromium.launch(headless=False)，这样就会以有头模式启动浏览器，显示出浏览器窗口。
# 问题 3：截图能做什么？在自动化测试中截图通常怎么用？
# 答：截图可以用来记录页面的状态，特别是在自动化测试中，当测试失败时，截图可以帮助开发者快速定位问题所在。通过查看截图，可以看到当时页面的内容、布局以及可能出现的错误信息，这对于调试非常有帮助。此外，截图还可以用于生成测试报告，或者在持续集成系统中保存测试结果的视觉证据。

# ============================================================
# 运行
# ============================================================
# python day19_playwright_intro.py
# 代码跑完后，检查目录下有没有 baidu_home.png
