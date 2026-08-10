"""
Day 13：JSON 处理 —— 解析复杂响应
=====================================
之前用 API 返回的 JSON 结构比较简单。今天学怎么处理复杂的、嵌套的、
不规则的 JSON 数据——这在真实项目中非常常见。
"""
import json
from ai_utils import chat


# ============================================================
# 第一部分：JSON 复习
# ============================================================
# JSON 和 Python dict 的对应关系：
#   JSON         Python
#   object  {}   dict
#   array   []   list
#   string  ""   str
#   number  123  int/float
#   true/false   True/False
#   null         None

# json.loads()   → JSON 字符串 → Python 对象
# json.dumps()   → Python 对象 → JSON 字符串


# ============================================================
# TODO 1：基础解析 —— 安全取值
# ============================================================
# 从深层嵌套的 JSON 中安全地取到目标值

def safe_get(data, *keys, default="未找到"):
    """
    从深层嵌套的字典中安全取值，任何一层缺失都返回默认值

    用法：safe_get(data, "choices", 0, "message", "content")
    """
    # ← 写你的代码
    # 提示：一层一层往下取，取不到就返回 default
    current = data
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        elif isinstance(current, list) and isinstance(key, int) and 0 <= key < len(current):
            current = current[key]
        else:
            return default
    return current



# 测试
sample = {
    "id": "chat-123",
    "choices": [
        {
            "index": 0,
            "message": {
                "role": "assistant",
                "content": "你好！"
            },
        }
    ],
    "usage": {"total_tokens": 15},
}

print("=" * 50)
print("TODO 1：安全取值")
print("=" * 50)
content = safe_get(sample, "choices", 0, "message", "content")
print(f"choices[0].message.content = {content}")

missing = safe_get(sample, "choices", 0, "message", "reasoning")
print(f"choices[0].message.reasoning = {missing}")

missing2 = safe_get(sample, "data", "result")
print(f"data.result = {missing2}")
print()


# ============================================================
# TODO 2：让 AI 输出 JSON —— 然后解析
# ============================================================
# 用 system prompt 让 AI 返回 JSON 格式，然后解析它

SYSTEM_JSON = """你是一个数据分析助手。用户给出问题后，你必须以JSON格式回答。
格式如下，不要输出任何其他内容：
{
    "topic": "问题所属领域",
    "keywords": ["关键词1", "关键词2"],
    "difficulty": "easy/medium/hard",
    "answer": "简要回答"
}"""

questions = [
    "Python的GIL是什么？",
    "什么是RESTful API？",
]

print("=" * 50)
print("TODO 2：让 AI 返回 JSON")
print("=" * 50)

for q in questions:
    ok, result = chat([
        {"role": "system", "content": SYSTEM_JSON},
        {"role": "user", "content": q},
    ])
    if not ok:
        print(f"❌ {q} → {result}")
        continue

    print(f"问：{q}")
    print(f"原始返回：{result[:100]}...")

    # ← 尝试解析 JSON
    # 提示：AI 可能返回 ```json ... ``` 包裹的内容，需要先剥离
    # json.loads() 只接受纯 JSON 字符串
    json_str = result.strip().strip("```json").strip("```").strip()
    if json_str.startswith("```") and json_str.endswith("```"):
        json_str = json_str[3:-3].strip()
    try:
        data = json.loads(json_str)
        print(f"解析结果：topic={data['topic']}, difficulty={data['difficulty']}")
    except json.JSONDecodeError:
        print("❌ 解析失败：返回的不是合法 JSON")
    print()


# ============================================================
# TODO 3：解析列表 —— 提取特定字段
# ============================================================
# 实际 API 返回可能包含很多信息，只需要提取有用的字段

# 模拟一个复杂的 API 响应（类似搜索引擎返回的结果）
search_result = {
    "query": "Python学习资源",
    "total_results": 3,
    "results": [
        {
            "title": "Python官方文档",
            "url": "https://docs.python.org",
            "score": 0.95,
            "metadata": {"type": "official", "lang": "zh"},
        },
        {
            "title": "Learn Python - Free Interactive Tutorial",
            "url": "https://www.learnpython.org",
            "score": 0.88,
            "metadata": {"type": "tutorial", "lang": "en"},
        },
        {
            "title": "Python教程 - 廖雪峰",
            "url": "https://www.liaoxuefeng.com",
            "score": 0.82,
            "metadata": {"type": "tutorial", "lang": "zh"},
        },
    ],
}

print("=" * 50)
print("TODO 3：提取列表字段")
print("=" * 50)

# 任务：提取所有中文教程的标题和链接
# ← 写你的代码：遍历 results，筛选 metadata.lang == "zh"
for item in search_result["results"]:
    if item.get("metadata", {}).get("lang") == "zh":
        print(f"标题：{item['title']}, 链接：{item['url']}")


print()


# ============================================================
# TODO 4（动手题）：JSON 对比 —— 判断两个响应是否一致
# ============================================================
# 用同一个问题问 AI 两次（不同 temperature），
# 然后用 JSON 提取关键信息，对比两次回答的差异

SYSTEM_COMPARE = """你是一个信息提取助手。回答用户问题时，必须以如下JSON格式输出：
{
    "summary": "一句话总结",
    "key_points": ["要点1", "要点2", "要点3"],
    "sentiment": "positive/neutral/negative"
}"""

question = "Python相比Java有哪些优势和劣势？"

print("=" * 50)
print("TODO 4：对比两次 AI 回答")
print("=" * 50)

# 第一次调用：temperature=0（确定性回答）
ok1, raw1 = chat([
    {"role": "system", "content": SYSTEM_COMPARE},
    {"role": "user", "content": question},
], temperature=0)

# 第二次调用：temperature=1.2（随机回答）
ok2, raw2 = chat([
    {"role": "system", "content": SYSTEM_COMPARE},
    {"role": "user", "content": question},
], temperature=1.2)

if not ok1 or not ok2:
    print("❌ API 调用失败")
else:
    # ← 写你的代码：
    # 1. 从 raw1, raw2 中提取 JSON（注意清除 markdown 代码块标记）
    # 2. 用 json.loads() 解析
    # 3. 对比两个回答的 key_points 有哪些不同
    raw1 = raw1.strip().strip("```json").strip("```").strip()
    raw2 = raw2.strip().strip("```json").strip("```").strip()
    json1 = json.loads(raw1)
    json2 = json.loads(raw2)
    key_points1 = set(json1.get("key_points", []))
    key_points2 = set(json2.get("key_points", []))
    only_in_1 = key_points1 - key_points2
    only_in_2 = key_points2 - key_points1
    print(f"temperature=0 独有的要点：{only_in_1}")
    print(f"temperature=1.2 独有的要点：{only_in_2}")
    print(f"temp=0 回答：{raw1[:80]}...")
    print(f"temp=1.2 回答：{raw2[:80]}...")
    print()

# ============================================================
# TODO 5（思考题）：JSON 处理中的常见坑
# ============================================================
# 问题 1：json.loads("null") 返回什么？为什么这是个坑？
# 答：返回None，这是个坑因为它不是字符串 "null"，而是 Python 的 None 对象，如果代码里直接用 result["field"] 可能会报错。
# 问题 2：AI 返回的 JSON 经常被 ```json ``` 包裹，你打算怎么处理？
# 答：可以先用 str.strip() 去掉两端的 ```json 和 ```，再解析。
# 问题 3：如果 API 返回的 JSON 字段有时存在有时不存在，怎么安全处理？
# 答：可以写一个 safe_get() 函数，逐层检查字段是否存在，取不到就返回默认值。
