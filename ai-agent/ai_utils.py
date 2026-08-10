"""
AI 调用工具模块
================
封装了 DeepSeek API 的 HTTP 调用、错误处理、重试机制。
以后任何项目 import 这个文件就能用，不用重复写。

用法：
    from ai_utils import chat, chat_stream, chat_with_retry

    ok, answer = chat("你好")
    ok, answer = chat_stream("你好")
    ok, answer = chat_with_retry("你好")
"""
import os
import sys
import json
import time
import tiktoken
import requests
from dotenv import load_dotenv

load_dotenv()

# ── 配置 ─────────────────────────────────────────────
API_KEY = os.getenv("DEEPSEEK_API_KEY")
API_URL = "https://api.deepseek.com/chat/completions"
DEFAULT_MODEL = "deepseek-chat"

# token 计数器（Day 8）
encoding = tiktoken.get_encoding("cl100k_base")


# ═══════════════════════════════════════════════════════
# 底层：HTTP 请求（不直接对外使用）
# ═══════════════════════════════════════════════════════

def _build_headers():
    """构造请求头"""
    return {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }


def _build_body(messages, temperature=0.7, max_tokens=500, stream=False):
    """构造请求体"""
    return {
        "model": DEFAULT_MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": stream,
    }


def _classify_http_error(status_code):
    """把 HTTP 状态码翻译成中文错误信息"""
    if status_code == 401:
        return "密钥无效或已过期"
    elif status_code == 429:
        return "请求过于频繁，请稍后重试"
    elif 400 <= status_code < 500:
        return f"请求参数错误，状态码: {status_code}"
    elif 500 <= status_code < 600:
        return f"服务器故障，状态码: {status_code}"
    else:
        return f"未知错误，状态码: {status_code}"


def _should_retry(status_code):
    """判断是否应该重试"""
    # 5xx 服务器错误 → 重试
    # 429 限流 → 重试
    # 其余不重试
    return status_code >= 500 or status_code == 429


# ═══════════════════════════════════════════════════════
# 公开 API（直接使用）
# ═══════════════════════════════════════════════════════

def chat(messages, temperature=0.7, max_tokens=500, timeout=30):
    """
    基础 HTTP 调用（带错误处理）

    参数：
        messages：对话消息列表，或直接传字符串（自动包装为 user 消息）
        temperature：创意度 0~2
        max_tokens：最大输出 token 数
        timeout：超时秒数

    返回：(success, result)
        success=True  → result = AI 回答
        success=False → result = 错误信息
    """
    if isinstance(messages, str):
        messages = [{"role": "user", "content": messages}]

    headers = _build_headers()
    body = _build_body(messages, temperature, max_tokens, stream=False)

    try:
        resp = requests.post(API_URL, headers=headers, json=body, timeout=timeout)

        if resp.status_code == 200:
            try:
                data = resp.json()
                if "error" in data:
                    return False, data["error"]["message"]
                return True, data["choices"][0]["message"]["content"]
            except json.JSONDecodeError:
                return False, "响应不是合法的 JSON 格式"

        return False, _classify_http_error(resp.status_code)

    except requests.Timeout:
        return False, "请求超时，服务器可能繁忙"
    except requests.ConnectionError:
        return False, "连接失败，请检查网络或 API 地址"
    except requests.RequestException as e:
        return False, f"请求异常：{e}"


def chat_with_retry(messages, temperature=0.7, max_tokens=500,
                    max_retries=3, timeout=30):
    """
    HTTP 调用 + 自动重试

    参数同上，额外：
        max_retries：最大重试次数
    """
    if isinstance(messages, str):
        messages = [{"role": "user", "content": messages}]

    headers = _build_headers()
    body = _build_body(messages, temperature, max_tokens, stream=False)

    for attempt in range(1, max_retries + 1):
        try:
            resp = requests.post(API_URL, headers=headers, json=body, timeout=timeout)

            if resp.status_code == 200:
                try:
                    data = resp.json()
                    if "error" in data:
                        return False, data["error"]["message"]
                    return True, data["choices"][0]["message"]["content"]
                except json.JSONDecodeError:
                    return False, "响应不是合法的 JSON 格式"

            if _should_retry(resp.status_code):
                if attempt < max_retries:
                    wait = 2 ** (attempt - 1)
                    reason = _classify_http_error(resp.status_code)
                    print(f"重试 {attempt}/{max_retries}: {reason}, 等待 {wait} 秒...")
                    time.sleep(wait)
                    continue
                return False, f"{_classify_http_error(resp.status_code)}，重试次数已达上限"

            return False, _classify_http_error(resp.status_code)

        except requests.Timeout:
            if attempt < max_retries:
                wait = 2 ** (attempt - 1)
                print(f"重试 {attempt}/{max_retries}: 请求超时, 等待 {wait} 秒...")
                time.sleep(wait)
                continue
            return False, "请求超时，重试次数已达上限"

        except requests.ConnectionError:
            return False, "连接失败，请检查网络或 API 地址"

        except requests.RequestException as e:
            return False, f"请求异常：{e}"

    return False, "重试多次后仍失败"


def chat_stream(messages, temperature=0.7, max_tokens=500, timeout=30):
    """
    流式调用 + 打字机效果

    返回：(success, result)
        success=True  → result = 完整回答文本
        success=False → result = 错误信息
    """
    if isinstance(messages, str):
        messages = [{"role": "user", "content": messages}]

    headers = _build_headers()
    body = _build_body(messages, temperature, max_tokens, stream=True)

    try:
        resp = requests.post(API_URL, headers=headers, json=body,
                             stream=True, timeout=timeout)

        if resp.status_code != 200:
            return False, _classify_http_error(resp.status_code)

        full_response = ""
        for line in resp.iter_lines():
            if not line:
                continue
            decoded = line.decode("utf-8")
            if decoded == "data: [DONE]":
                break
            if not decoded.startswith("data: "):
                continue
            try:
                chunk = json.loads(decoded[6:])
                delta = chunk["choices"][0]["delta"]
                if "content" in delta:
                    for char in delta["content"]:
                        sys.stdout.write(char)
                        sys.stdout.flush()
                        if char == "。":
                            time.sleep(0.2)
                        else:
                            time.sleep(0.02)
                    full_response += delta["content"]
            except (json.JSONDecodeError, KeyError):
                continue

        print()
        return True, full_response

    except requests.Timeout:
        return False, "请求超时"
    except requests.ConnectionError:
        return False, "连接失败"
    except requests.RequestException as e:
        return False, f"请求异常：{e}"


def count_tokens(messages):
    """计算消息列表的 token 数"""
    if isinstance(messages, str):
        messages = [{"role": "user", "content": messages}]
    full_text = ""
    for m in messages:
        full_text += m["content"] + "\n"
    return len(encoding.encode(full_text))


# ═══════════════════════════════════════════════════════
# 自测
# ═══════════════════════════════════════════════════════
if __name__ == "__main__":
    print("测试 ai_utils 模块...")
    ok, result = chat("你好，用一句话介绍自己")
    if ok:
        print(f"✅ chat(): {result[:50]}...")
    else:
        print(f"❌ {result}")
