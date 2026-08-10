"""
Day 21：Playwright 等待 + expect 断言
========================================
前两天用 page.wait_for_load_state("networkidle") 是"等全部加载完"，
但太粗糙——有时候你只等一个按钮出现，不需要等整个页面。

今天学精细控制：
1. 自动等待    — Playwright 默认就等，你其实已经用了
2. expect()   — 智能等待 + 断言二合一，比 assert 更强
3. 手动等待    — 精确控制等待条件
"""
from playwright.sync_api import sync_playwright, expect


# ============================================================
# 第一部分：expect() —— 会等待的断言
# ============================================================
# assert 是"立刻判断"——如果元素还没出现，assert 直接失败
# expect() 是"等待然后判断"——会等元素出现再断言，超时才失败
#
# 对比：
#   assert page.locator("h1").inner_text() == "xxx"    # 立刻取文字，没找到就报错
#   expect(page.locator("h1")).to_have_text("xxx")     # 等待 h1 出现，再检查文字


# ============================================================
# TODO 1：expect 的基本用法
# ============================================================

print("=" * 50)
print("TODO 1：expect 断言")
print("=" * 50)

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto("https://example.com")

    # 用 expect 替代 assert：
    #   assert page.locator("h1").inner_text() == "Example Domain"
    #
    # ← 改成 expect 写法：
    #   expect(page.locator("h1")).to_have_text("Example Domain")
    #
    # ← 写代码：用 expect 验证 h1 文字
    # ← 写代码：用 expect(page).to_have_title("Example Domain") 验证页面标题
    # ← 写代码：用 expect(page.locator("a")).to_be_visible() 验证链接可见
    try:
        expect(page.locator("h1")).to_have_text("Example Domain")
        print("h1 文字断言通过了！")
        expect(page).to_have_title("Example Domain")
        print("页面标题断言通过了！")
        expect(page.locator("a")).to_be_visible()
        print("链接可见断言通过了！")
    except AssertionError as e:
        print(f"断言失败：{e}")
    except Exception as e:
        print(f"发生错误：{e}")
    

    browser.close()


# ============================================================
# TODO 2：等待元素状态变化
# ============================================================
# 打开一个包含延迟加载内容的页面

print("=" * 50)
print("TODO 2：等待元素出现")
print("=" * 50)

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto("https://example.com")   # 这个页面 2 秒后才返回

    # ← 写代码：
    # 1. 页面内容是 2 秒后才出现的，用 expect 等待 body 里的文字出现
    # 2. 用 expect(page.locator("body")).to_contain_text("2") 等待并断言
    page.wait_for_timeout(1000)  # 模拟页面内容 2 秒后才出现
    h1_text = page.locator("h1").inner_text()
    print(f"h1 文字是：{h1_text}")
    expect(page.locator("h1")).to_contain_text("Example")
    print("页面内容断言通过了！")

    browser.close()


# ============================================================
# TODO 3：加载指示器消失 —— 等待"不再可见"
# ============================================================
# 很多页面有 loading spinner（加载动画），测试需要等它消失

print("=" * 50)
print("TODO 3：等待加载完成")
print("=" * 50)

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()

    # 这个页面有一个可见的 loading 区域，3 秒后消失
    page.goto("https://example.com")

    # ← 写代码：
    # 页面加载中……用 expect 怎么等？
    # 提示：没有 loading spinner 可观察，直接用 expect 等待结果文字出现即可
    # expect(page.locator("body")).to_contain_text("3")
    expect(page.locator("h1")).to_contain_text("Example")
    print("页面加载完成，内容断言通过了！")

    browser.close()


# ============================================================
# TODO 4：手动等待 —— 精确控制等待条件
# ============================================================
# 有些场景 expect 覆盖不了，需要手动 wait_for

print("=" * 50)
print("TODO 4：手动等待")
print("=" * 50)

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto("https://example.com")

    # ← 写代码：
    # 1. page.wait_for_url("https://example.com/")  等待 URL 变成指定值
    # 2. page.wait_for_timeout(500)                 纯等待 500ms（极少用）
    # 3. locator.wait_for(state="attached")         等待元素挂载到 DOM
    # 4. locator.wait_for(state="visible")          等待元素可见
    # 5. locator.wait_for(state="hidden")           等待元素隐藏
    page.wait_for_url("https://example.com/")
    page.wait_for_timeout(500)
    page.locator("h1").wait_for(state="attached")
    page.locator("h1").wait_for(state="visible")
    page.locator("spinner").wait_for(state="hidden")
    # 练习：定位 h1，先等待它 visible，再用 expect 断言文字
    heading = page.locator("h1")
    # ← 写代码
    expect(heading).to_be_visible()
    print("h1 可见了！")
    expect(heading).to_have_text("Example Domain")
    print("h1 文字断言通过了！")


    browser.close()


# ============================================================
# TODO 5：综合练习 —— 搜索 + 等待结果 + 断言
# ============================================================
# 用 DuckDuckGo（比百度友好，不拦自动化）完成搜索流程

print("=" * 50)
print("TODO 5：综合练习")
print("=" * 50)

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto("https://www.bing.com")

    # ← 写代码：
    # 1. 定位搜索框（id="searchbox_input"），输入 "Python Playwright"
    # 2. 定位搜索按钮或用 keyboard.press("Enter") 触发搜索
    # 3. 等待搜索结果出现（等标题包含关键词或等结果列表可见）
    # 4. 用 expect 断言页面标题包含 "Python Playwright"
    # 5. 截图保存
    search_input = page.locator("#sb_form_q")
    search_input.fill("Python Playwright")
    search_input.press("Enter")
    title = page.title()
    print(f"搜索结果页面标题: {title}")
    expect(page).to_have_title("Python Playwright - 搜索")
    print("搜索结果页面标题断言通过了！")
    page.screenshot(path="bing_search.png")
    browser.close()


# ============================================================
# TODO 6（思考题）
# ============================================================
# 问题 1：assert 和 expect 的底层区别是什么？
#   提示：一个会重试，一个不会
# 答: expect 内部会自动重试，直到断言成功或超时；而 assert 是立刻执行断言，不会重试，如果元素还没出现就直接失败。
# 问题 2：expect 的默认超时是多少？怎么修改？
#   提示：查阅 Playwright 文档或试试 expect(..., timeout=10000)
# 答: expect 的默认超时是 5000 毫秒（5 秒）。可以通过传递 timeout 参数来修改，例如 expect(..., timeout=10000) 将超时设置为 10 秒。
# 问题 3：什么时候用 page.wait_for_xxx，什么时候用 expect？
# 答: 当需要等待一个特定的条件（如 URL 变化、元素状态变化）时，使用 page.wait_for_xxx；当需要等待元素出现并断言其状态或内容时，使用 expect，因为它结合了等待和断言功能，更加方便和智能。

# ============================================================
# 常用 expect 速查
# ============================================================
# expect(locator).to_be_visible()           # 元素可见
# expect(locator).to_be_hidden()            # 元素隐藏
# expect(locator).to_have_text("文字")       # 精确匹配文字
# expect(locator).to_contain_text("文字")    # 包含文字
# expect(locator).to_have_value("值")        # 输入框的值
# expect(locator).to_be_enabled()           # 可交互
# expect(locator).to_be_disabled()          # 禁用状态
# expect(page).to_have_title("标题")         # 页面标题
# expect(page).to_have_url("http://...")    # 页面 URL


# ============================================================
# 运行
# ============================================================
# python day21_playwright_wait_expect.py
