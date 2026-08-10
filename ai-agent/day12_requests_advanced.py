"""
Day 12：requests 深入 —— 错误处理 + 超时 + 重试
===================================================
Day 11 学会了发 HTTP 请求。今天解决"发了但出问题怎么办"：
  超时处理、错误捕获、自动重试、响应头信息。
"""
import os
import json
import time
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("DEEPSEEK_API_KEY")
API_URL = "https://api.deepseek.com/chat/completions"


# ============================================================
# 第一部分：为什么需要错误处理？
# ============================================================
# Day 11 的 http_chat 假设一切顺利。但真实世界中：
#   1. 网络超时 —— 服务器半天不响应，程序永远卡住
#   2. API 限流 —— 请求太快，服务器返回 429
#   3. 密钥过期 —— 返回 401
#   4. 服务器故障 —— 返回 500/502/503
#   5. DNS 解析失败 —— 连不上服务器
#   6. JSON 解析失败 —— 返回的不是合法的 JSON


# ============================================================
# TODO 1：给 HTTP 请求加上超时
# ============================================================
# requests 默认没有超时限制 —— 如果服务器卡住，程序会永远等下去
# timeout 参数：连接超时 + 读取超时

print("=" * 60)
print("TODO 1：超时处理")
print("=" * 60)

# 正常请求（有超时）
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}

try:
    resp = requests.post(
        API_URL,
        headers=headers,
        json={
            "model": "deepseek-chat",
            "max_tokens": 20,
            "messages": [{"role": "user", "content": "说你好"}],
        },
        timeout=10,  # ← 最多等 10 秒（连接5秒 + 读取5秒）
    )
    print(f"状态码：{resp.status_code}")
    print(f"回答：{resp.json()['choices'][0]['message']['content']}")
except requests.Timeout:
    print("请求超时！服务器可能繁忙")
except requests.ConnectionError:
    print("连接失败！检查网络或 API URL")
except requests.RequestException as e:
    print(f"请求异常：{e}")
print()


# ============================================================
# TODO 2：写一个带错误处理的 http_chat 增强版
# ============================================================
# 在 Day 11 的基础上，增加：
#   - timeout 参数（默认 30 秒）
#   - 捕获各种异常
#   - 检查 HTTP 状态码，给出中文提示

def http_chat_safe(messages, temperature=0.7, max_tokens=200, timeout=30):
    """
    HTTP 调 API，带完整的错误处理
    返回：(success, result)
      success=True  → result = AI 回答字符串
      success=False → result = 错误信息
    """
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    body = {
        "model": "deepseek-chat",
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    # ← 这里写你的代码
    # 1. try/except 捕获 requests.Timeout, ConnectionError, RequestException
    # 2. 检查 resp.status_code：
    #      200 → 成功，解析 JSON 返回
    #      401 → "密钥无效或已过期"
    #      429 → "请求过于频繁，请稍后重试"
    #      500/502/503 → "服务器故障，状态码：xxx"
    #      其他 → "未知错误，状态码：xxx"
    # 3. 解析 JSON 也可能出错，加 try/except
    try:
        resp = requests.post(API_URL, headers=headers, json=body, timeout=timeout)
        if resp.status_code == 200:
            try:
                data = resp.json()
                if "error" in data:
                    return False, data["error"]["message"]
                return True, data["choices"][0]["message"]["content"]
            except json.JSONDecodeError:
                return False, "响应不是合法的JSON格式"
        elif resp.status_code == 401:
            return False, "密钥无效或者过期"
        elif resp.status_code == 429:
            return False, "请求过于频繁，请稍后重试"
        elif 500 <= resp.status_code <= 600:
            return False, f"服务器故障，状态码: {resp.status_code}"
        else:
            return False, f"未知错误，状态码: {resp.status_code}"
    except requests.Timeout:
        return False, "请求超时！服务器可能繁忙"
    except requests.ConnectionError:
        return False, "连接失败！检查网络或 API URL"
    except requests.RequestException as e:
        return False, f"请求异常：{e}"




# 测试
print("=" * 60)
print("TODO 2：安全 HTTP 调用")
print("=" * 60)
ok, result = http_chat_safe([{"role": "user", "content": "1+1=?"}])
if ok:
    print(f"✅ {result}")
else:
    print(f"❌ {result}")
print()


# ============================================================
# TODO 3：自动重试机制
# ============================================================
# 网络抖动、服务器临时故障 → 等几秒再试可能就好了
# 但不是所有错误都适合重试（密钥错误重试也没用）

def http_chat_with_retry(messages, max_retries=3, timeout=30):
    """
    HTTP 调 API，失败时自动重试

    重试策略：
      - 网络超时 → 重试 ✓
      - 服务器 5xx 错误 → 重试 ✓
      - 密钥错误(401) → 不重试 ✗（重试没用）
      - 限流(429) → 等待后重试 ✓
    """
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    body = {
        "model": "deepseek-chat",
        "messages": messages,
        "temperature": 0.7,
    }

    # ← 这里写你的代码
    # 1. for 循环重试 max_retries 次
    # 2. 每次尝试调用 API
    # 3. 成功 → 返回结果
    # 4. 连接超时 → 打印 "重试 N/3：连接超时，等待 X 秒后重试..."
    # 5. 5xx 错误 → 打印 "重试 N/3：服务器错误 503，等待 X 秒后重试..."
    # 6. 401/429 等不重试 → 直接返回错误
    # 7. 每次重试前 time.sleep()，逐次延长等待时间（1秒 → 2秒 → 4秒）
    for attempt in range(1, max_retries + 1):
        try:
            resp = requests.post(API_URL, headers=headers, json=body, timeout=timeout)
            if resp.status_code == 200:
                data = resp.json()
                if "error" in data:
                    return False, data["error"]["message"]
                return True, data["choices"][0]["message"]["content"]
            elif resp.status_code == 401:
                return False, "密钥无效或者过期"
            elif resp.status_code == 429:
                return False, "请求过于频繁，请稍后重试"
            elif 500 <= resp.status_code <= 600:
                if attempt < max_retries:
                    wait_time = 2 ** (attempt - 1)  # 1, 2, 4 秒
                    print(f"重试 {attempt}/{max_retries}: 服务器错误 {resp.status_code}, 等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                else:
                    return False, f"服务器错误 {resp.status_code}，重试次数已达上限"
            else:
                return False, f"未知错误，状态码: {resp.status_code}"
        except requests.Timeout:
            if attempt < max_retries:
                wait_time = 2 ** (attempt - 1) # 1, 2, 4 秒
                print(f"重试 {attempt}/{max_retries}: 请求超时, 等待 {wait_time} 秒后重试...")
                time.sleep(wait_time)
            else:
                return False, "请求超时，重试次数已达上限"
            
        except requests.ConnectionError:
            return False, "连接失败！检查网络或 API URL"
        except requests.RequestException as e:
            return False, f"请求异常：{e}"


# 测试
print("=" * 60)
print("TODO 3：自动重试")
print("=" * 60)
ok, result = http_chat_with_retry([{"role": "user", "content": "说一个词：你好"}])
if ok:
    print(f"✅ {result}")
else:
    print(f"❌ {result}")
print()


# ============================================================
# TODO 4：查看响应头信息
# ============================================================
# API 返回的不只是 JSON body，还有响应头（headers）
# 里面藏着很有用的信息，比如限流状态

resp = requests.post(
    API_URL,
    headers=headers,
    json={
        "model": "deepseek-chat",
        "max_tokens": 10,
        "messages": [{"role": "user", "content": "你好"}],
    },
    timeout=10,
)

print("=" * 60)
print("TODO 4：响应头分析")
print("=" * 60)
print(f"状态码：{resp.status_code}")
print(f"Content-Type：{resp.headers.get('Content-Type')}")
print(f"Date：{resp.headers.get('Date')}")
print(f"Server：{resp.headers.get('Server')}")

# 限流相关头（重点！）
print()
print("--- 限流相关头 ---")
for key in ["x-ratelimit-limit-requests",
            "x-ratelimit-remaining-requests",
            "x-ratelimit-limit-tokens",
            "x-ratelimit-remaining-tokens"]:
    value = resp.headers.get(key, "未提供")
    print(f"{key}：{value}")
print()

# 观察：如果 remaining 接近 0，说明快被限流了，需要放慢速度


# ============================================================
# TODO 5（思考题）：生产环境的错误处理策略
# ============================================================
# 以下场景该如何处理？
#
# 场景 A：用户发了一条请求，3 秒后超时了
#   → 给用户看到什么？请求超时，正在重试______________________________
#   → 后台做什么？___记录日志，通知运维_______________________________
#
# 场景 B：API 返回 429（请求过于频繁）
#   → 程序应该怎么做？___等待一段时间后重试___________________________
#
# 场景 C：连续重试 3 次都失败了
#   → 最终给用户什么反馈？_多次重试失败，请稍后再试_________________________
#   → 需要记录什么信息方便排查？重试失败原因，返回内容_____________________
#
# 场景 D：API 返回了 200，但 JSON 解析失败
#   → 可能是什么原因？_相应内容不是有效JSON_____________________________
#   → 怎么处理？___打印原始响应文本（resp.text），方便排查到底返回了什么。_________________________________
