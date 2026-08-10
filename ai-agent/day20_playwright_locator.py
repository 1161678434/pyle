"""
Day 20：Playwright 元素定位 —— 找到、点击、输入
===================================================
昨天学会了打开页面。今天学怎么在页面上"找到"想要的东西——
按钮、输入框、文字、链接，然后操作它们。

三种定位方式：
1. CSS 选择器    — page.locator("css=选择器")  最灵活
2. 文本定位      — page.get_by_text("文本")   最直观
3. Role 定位     — page.get_by_role(...)      最语义化

操作：
  .click()      点击
  .fill("内容")  输入文本
  .inner_text() 提取文字内容
"""
from playwright.sync_api import sync_playwright
import json


# ============================================================
# TODO 1：CSS 选择器定位 + 提取文本
# ============================================================
# 打开 example.com，定位页面上的 <h1> 和 <p>，提取文字

print("=" * 50)
print("TODO 1：CSS 选择器定位")
print("=" * 50)

with sync_playwright() as p:
    browser = p.chromium.launch()  # headless=False 可以看到浏览器界面
    page = browser.new_page()
    page.goto("https://example.com")

    # ← 写代码：
    # 1. 用 page.locator("h1") 定位 <h1> 元素，.inner_text() 提取文字
    # 2. 用 page.locator("p") 定位 <p> 元素，.inner_text() 提取文字
    # 3. assert 验证 h1 文字是 "Example Domain"
    # 4. 打印结果
    h1_text = page.locator("h1").inner_text()
    p_text = page.locator("p").first.inner_text()
    assert h1_text == "Example Domain", f"h1 文字不对，实际是 {h1_text}"
    assert p_text == "This domain is for use in documentation examples without needing permission. Avoid use in operations.", f"p 文字不对，实际是 {p_text}"
    print(f"h1 文字: {h1_text}")
    print(f"p 文字: {p_text}")
    page.screenshot(path="example_com.png")
    browser.close()


# ============================================================
# TODO 2：文本定位 + 点击
# ============================================================
# 打开 example.com，页面上有一个 <a> 链接 "More information..."
# 用文本定位找到它，获取它的 href 属性

print("=" * 50)
print("TODO 2：文本定位")
print("=" * 50)

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto("https://example.com")

    # ← 写代码：
    # 1. 用 page.get_by_text("More information...") 定位链接
    # 2. 用 .get_attribute("href") 获取链接地址
    # 3. assert 验证 href 是 "https://www.iana.org/domains/example"
    # 4. 用 .click() 点击这个链接
    # 5. 打印跳转后的页面标题
    print(f"跳转前的页面标题: {page.title()}")
    more_info_link = page.get_by_text("Learn more")
    href = more_info_link.get_attribute("href")
    assert href == "https://iana.org/domains/example", f"URL 不对，实际是 {href}"
    more_info_link.click()
    print(f"跳转后的页面标题: {page.title()}")
    browser.close()


# ============================================================
# TODO 3：输入框操作 —— 搜索框输入 + 提交
# ============================================================
# 打开百度，定位搜索框，输入关键词，点击搜索

print("=" * 50)
print("TODO 3：输入框操作")
print("=" * 50)

with sync_playwright() as p:
    browser = p.chromium.launch()  # 打开浏览器界面，方便调试
    page = browser.new_page()
    page.goto("https://www.baidu.com")

    # ← 写代码：
    # 1. 定位搜索框：page.locator("#kw")  ← 百度搜索框的 id 是 "kw"
    # 2. 用 .fill("Playwright Python") 输入文字
    # 3. 定位搜索按钮：page.locator("#su")  ← 百度搜索按钮的 id 是 "su"
    # 4. 用 .click() 点击搜索
    # 5. 等待搜索结果加载：page.wait_for_load_state("networkidle")
    # 6. 截图保存为 "baidu_search.png"
    # 7. 打印当前页面标题
    kw_input = page.locator("#chat-textarea")
    kw_input.fill("Playwright Python")
    search_button = page.locator("#chat-submit-button")
    search_button.click()
    page.wait_for_load_state("networkidle")
    page.screenshot(path="baidu_search.png")
    print(f"搜索结果页面标题: {page.title()}")

    browser.close()


# ============================================================
# TODO 4：组合练习 —— 打开页面、定位、输入、断言
# ============================================================
# 打开 https://httpbin.org/forms/post ，
# 填写表单，提交，验证返回的 JSON

print("=" * 50)
print("TODO 4：表单填写 + 提交")
print("=" * 50)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)  # 打开浏览器界面，方便调试
    page = browser.new_page()
    page.goto("https://httpbin.org/forms/post")

    # 表单字段：
    #  客户名称：<input name="custname" />
    #  电话：    <input name="custtel" />
    #  邮箱：    <input name="custemail" />
    #  提交按钮：<button type="submit">

    # ← 写代码：
    # 1. 定位并填写 "客户名称" 字段（用 name 属性）
    # 2. 定位并填写 "电话" 字段
    # 3. 定位并填写 "邮箱" 字段
    # 4. 点击提交按钮
    # 5. 等待提交结果页面加载
    # 6. 提取结果页面的 body 文本，assert 里面包含你填写的名字
    custname_input = page.locator("input[name='custname']")
    custname_input.fill("张三")
    custtel_input = page.locator("input[name='custtel']")
    custtel_input.fill("1234567890")
    custemail_input = page.locator("input[name='custemail']")
    custemail_input.fill("zhangsan@example.com")
    submit_button = page.locator("body > form > p:nth-child(8) > button")
    submit_button.click()
    page.wait_for_load_state("networkidle")
    body_text = page.locator("body > pre").inner_text()
    body_json = json.loads(body_text)
    print(f"提交结果 JSON: {body_json['form']['custname']}")
    try:
        assert body_json['form']['custname'] == "张三1", "提交结果中没有找到客户名称！"
        print("表单提交验证通过！")
    except KeyError as e:
        print(f"表单提交验证失败：结果 JSON 中没有找到键 {e}")
    except AssertionError as e:
        print(f"表单提交验证失败：{e}")
    browser.close()


# ============================================================
# TODO 5（思考题）
# ============================================================
# 问题 1：locator() 和 get_by_text() 有什么区别？什么时候用哪个？
# 答: locator() 是基于 CSS 选择器的定位方式，可以非常灵活地定位页面上的元素，适用于各种复杂的场景。get_by_text() 则是基于元素的文本内容进行定位，更加直观和语义化，适合快速定位包含特定文本的元素。一般来说，如果你知道元素的结构和属性，使用 locator() 更合适；如果你只关心元素显示的文本内容，使用 get_by_text() 更方便。
# 问题 2：如果一个页面上有多个相同文本的元素，get_by_text() 会怎样？
#    试试怎么定位"第一个匹配的"和"全部匹配的"
# 答: get_by_text() 默认会返回第一个匹配的元素，如果页面上有多个相同文本的元素，可以使用 .nth(index) 来定位第 n 个匹配的元素，例如 page.get_by_text("文本").nth(1) 定位第二个匹配的元素。要获取全部匹配的元素，可以使用 page.get_by_text("文本").all()，它会返回一个列表包含所有匹配的元素。
# 问题 3：在百度搜索框输入文字后，除了点击搜索按钮，还有什么方式触发搜索？
#    提示：想想键盘操作
#    答：可以使用 page.keyboard.press("Enter") 来模拟按下回车键触发搜索。

# ============================================================
# 运行
# ============================================================
# python day20_playwright_locator.py
