"""
接口自动化 — 本地测试服务器
==========================
替代 httpbin.org，提供 GET/POST/PUT/DELETE/cookies/status/headers 全部端点
启动：python api_test_server.py
"""

from flask import Flask, request, jsonify, make_response, redirect

app = Flask(__name__)

# ============================================================
# HTTP 方法回显
# ============================================================

@app.route('/get')
def echo_get():
    return jsonify({
        "method": "GET",
        "args": dict(request.args),
        "headers": dict(request.headers),
        "cookies": dict(request.cookies),
    })

@app.route('/post', methods=['POST'])
def echo_post():
    data = request.get_json(silent=True) or dict(request.form)
    return jsonify({
        "method": "POST",
        "json": data,
        "form": dict(request.form),
        "headers": dict(request.headers),
        "cookies": dict(request.cookies),
    })

@app.route('/put', methods=['PUT'])
def echo_put():
    data = request.get_json(silent=True) or {}
    return jsonify({
        "method": "PUT",
        "json": data,
        "headers": dict(request.headers),
    })

@app.route('/delete', methods=['DELETE'])
def echo_delete():
    return jsonify({"method": "DELETE", "status": "deleted"})


# ============================================================
# 状态码
# ============================================================

@app.route('/status/<int:code>')
def status_code(code):
    return jsonify({"status": code, "message": "ok" if code < 400 else "error"}), code


@app.route('/redirect/<int:n>')
def do_redirect(n):
    if n <= 1:
        return jsonify({"status": "arrived", "redirects_taken": n})
    return redirect(f"/redirect/{n - 1}")


# ============================================================
# Cookie
# ============================================================

@app.route('/cookies/set')
def set_cookies():
    """通过查询参数设置 cookie：/cookies/set?token=abc&role=qa"""
    resp = make_response(jsonify({"cookies_set": dict(request.args)}))
    for key, value in request.args.items():
        resp.set_cookie(key, value)
    return resp


@app.route('/cookies')
def show_cookies():
    return jsonify({"cookies": dict(request.cookies)})


# ============================================================
# Headers
# ============================================================

@app.route('/headers')
def echo_headers():
    return jsonify({"headers": dict(request.headers)})


@app.route('/response-headers')
def set_response_headers():
    """查询参数变成响应头：/response-headers?X-Custom=hello"""
    resp = make_response(jsonify({"response_headers": dict(request.args)}))
    for key, value in request.args.items():
        resp.headers[key] = value
    return resp


# ============================================================
# 模拟登录（返回 token）
# ============================================================

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json(silent=True) or {}
    username = data.get("username", "")
    password = data.get("password", "")

    if username == "qa_tester" and password == "test123":
        return jsonify({
            "token": "eyJhbGciOiJIUzI1NiJ9.eyJ1c2VyIjoicWFfdGVzdGVyIn0.mock",
            "user_id": 42,
            "role": "qa"
        })
    else:
        return jsonify({"error": "invalid credentials"}), 401


# ============================================================
# 模拟业务接口（需要 token）
# ============================================================

@app.route('/api/user/profile')
def user_profile():
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return jsonify({"error": "unauthorized"}), 401
    return jsonify({"name": "qa_tester", "role": "qa", "email": "qa@example.com"})


@app.route('/delay/<int:seconds>')
def delay(seconds):
    import time
    time.sleep(seconds)
    return jsonify({"delayed": seconds})


# ============================================================
# CRUD — 用户管理（Day 5 实战用，有内存持久化）
# ============================================================
_users = {}      # {1: {"name": "...", "role": "..."}, ...}
_next_id = 1     # 自增 ID


@app.route('/api/users', methods=['GET'])
def list_users():
    """GET /api/users — 返回所有用户"""
    return jsonify({"users": list(_users.values()), "total": len(_users)})


@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """GET /api/users/1 — 返回指定用户，不存在返回 404"""
    user = _users.get(user_id)
    if user is None:
        return jsonify({"error": "user not found"}), 404
    return jsonify(user)


@app.route('/api/users', methods=['POST'])
def create_user():
    """POST /api/users — 创建用户，name 必填，重名返回 409"""
    global _next_id
    data = request.get_json(silent=True) or {}
    name = data.get("name", "").strip()
    if not name:
        return jsonify({"error": "name is required"}), 400

    # 检查重名
    for u in _users.values():
        if u["name"] == name:
            return jsonify({"error": f"user '{name}' already exists"}), 409

    user_id = _next_id
    _next_id += 1
    user = {"id": user_id, "name": name, "role": data.get("role", "member")}
    _users[user_id] = user
    return jsonify(user), 201


@app.route('/api/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """PUT /api/users/1 — 全量更新用户，不存在返回 404"""
    if user_id not in _users:
        return jsonify({"error": "user not found"}), 404
    data = request.get_json(silent=True) or {}
    name = data.get("name", "").strip()
    if not name:
        return jsonify({"error": "name is required"}), 400
    _users[user_id]["name"] = name
    _users[user_id]["role"] = data.get("role", _users[user_id]["role"])
    return jsonify(_users[user_id])


@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """DELETE /api/users/1 — 删除用户，不存在返回 404"""
    if user_id not in _users:
        return jsonify({"error": "user not found"}), 404
    deleted = _users.pop(user_id)
    return jsonify({"deleted": deleted})


@app.route('/api/users/reset', methods=['POST'])
def reset_users():
    """重置数据（测试专用）"""
    global _users, _next_id
    _users = {}
    _next_id = 1
    return jsonify({"status": "reset"})


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
