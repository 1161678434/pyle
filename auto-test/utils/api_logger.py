"""
API 请求日志 — 每个请求自动记录 curl 命令 + 响应信息
=====================================================
用途：
  1. 测试失败时快速定位"发了什么、回了什么"
  2. 把 curl 命令甩给开发，"你跑这个就能复现"
  3. 日志文件可归档，出问题时回溯

用法：在 Session 里注册 hooks={'response': log_response}
"""

import json
import logging
import os
from datetime import datetime

# ---- 日志文件配置 ----
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, f"api_{datetime.now().strftime('%Y%m%d')}.log")

# ---- Python logging 基础配置 ----
_logger = logging.getLogger("api")
_logger.setLevel(logging.DEBUG)

_fh = logging.FileHandler(LOG_FILE, encoding="utf-8")
_fh.setLevel(logging.DEBUG)
_fh.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))

_ch = logging.StreamHandler()
_ch.setLevel(logging.WARNING)  # 控制台只打印 WARNING+，不刷屏
_ch.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))

_logger.addHandler(_fh)
_logger.addHandler(_ch)


def to_curl(request) -> str:
    """把 requests.PreparedRequest 对象转成 curl 命令"""
    parts = [f"curl -X {request.method}"]

    # URL
    parts.append(f"'{request.url}'")

    # Headers（跳过无意义的默认头）
    skip_headers = {"User-Agent", "Accept-Encoding", "Accept", "Connection"}
    for key, value in request.headers.items():
        if key not in skip_headers:
            parts.append(f"-H '{key}: {value}'")

    # Body
    if request.body:
        body_str = request.body.decode("utf-8", errors="replace")
        # 截断过长 body
        if len(body_str) > 500:
            body_str = body_str[:500] + "...(truncated)"
        parts.append(f"-d '{body_str}'")

    return " \\\n  ".join(parts)


def log_response(response, *args, **kwargs):
    """
    requests 的 response hook。
    每个请求完成后自动调用，记录请求 + 响应。

    用法：
      s = requests.Session()
      s.hooks['response'].append(log_response)
    """
    req = response.request
    status = response.status_code

    # 日志等级：4xx/5xx 是 ERROR，其他是 INFO
    level = logging.ERROR if status >= 400 else logging.INFO

    # 截断响应体
    try:
        resp_body = json.dumps(response.json(), ensure_ascii=False)
    except Exception:
        resp_body = response.text[:300]
    if len(resp_body) > 800:
        resp_body = resp_body[:800] + "...(truncated)"

    msg = (
        f"\n{'='*60}\n"
        f"▶ {req.method} {req.url}\n"
        f"◀ {status} ({len(response.content)} bytes) in {response.elapsed.total_seconds():.2f}s\n"
        f"{'='*60}\n"
        f"📋 curl 重现命令:\n{to_curl(req)}\n"
        f"{'='*60}\n"
        f"📥 响应:\n{resp_body}\n"
        f"{'='*60}"
    )

    _logger.log(level, msg)


def clear_log():
    """清空日志文件（可选：每次测试会话启动时调用）"""
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)
