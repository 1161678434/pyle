import requests
import json

api_key = "sk-5e826e5f14434b299b34636e40b8eb0d"
base_url = "https://api.deepseek.com"
model = "deepseek-v4-flash"

def ask_deepseek(prompt, model="deepseek-v4-flash", temperature=0.7, timeout=15):
    """
    向 DeepSeek 模型发送请求，返回标准化字典结果
    成功：{"success": True, "reply": ..., "error": None}
    失败：{"success": False, "reply": None, "error": 错误信息}
    """
    result = {"success": False, "reply": None, "error": None}
    
    # 1. 构造请求 URL
    url = f"{base_url}/chat/completions"

    # 2. 设置请求 Header
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    # 3. 构造请求 Body
    data = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature
    }

    try:
        # 4. 发送 POST 请求
        response = requests.post(url, headers=headers, json=data, timeout=timeout)

        # 5. 检查 HTTP 状态码，非 200 视为错误
        if response.status_code != 200:
            result["error"] = f"HTTP {response.status_code}: {response.text}"
            return result

        # 6. 解析响应 JSON
        resp_json = response.json()
        reply = resp_json["choices"][0]["message"]["content"]

        result["success"] = True
        result["reply"] = reply
    except requests.exceptions.Timeout:
        result["error"] = f"请求超时（{timeout} 秒）"
    except requests.exceptions.RequestException as e:
        result["error"] = f"网络请求异常: {str(e)}"
    except (KeyError, json.JSONDecodeError) as e:
        result["error"] = f"响应数据解析失败: {str(e)}"
    
    return result
if __name__ == "__main__":
    test_prompt = "用一句话介绍什么是Python"
    res = ask_deepseek(test_prompt)
    if res["success"]:
        print("AI回复:", res["reply"])
    else:
        print("出错了:", res["error"])