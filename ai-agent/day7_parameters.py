"""
Day 7：系统提示词 + API 参数精讲
================================
上半场：系统提示词（System Prompt）—— 控制 AI 角色和行为
下半场：参数调优（temperature/top_p/stop）—— 控制 AI 输出风格
"""
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)


# ============================================================
# 第一部分：系统提示词（System Prompt）
# ============================================================
# system prompt 不是"提问"，而是"设定 AI 的身份和规则"
# AI 对 system 消息的遵从度最高，高于 user 消息
#
# 好的 system prompt 三要素：
#   1. 角色：你是谁？
#   2. 规则：怎么回答？
#   3. 格式：输出什么样？


# ============================================================
# TODO 1：对比不同 system prompt 的效果
# ============================================================
# 用同一个问题，分别用三种 system prompt，观察回答的区别

question = "介绍一下Python"

# 方案 A：太模糊 —— AI 不知道你要什么
system_a = "你是一个助手"

# 方案 B：有角色和规则 —— 回答明显不同
system_b = "你是一个10年经验的Python工程师，用通俗易懂的中文回答，每次回答不超过100字"

# 方案 C：精细控制 —— 适合生产环境
system_c = """你是一个Python教学助手，遵守以下规则：
1. 用中文回答，每次不超过120字
2. 代码用 ```python ``` 包裹
3. 不要用术语，用生活例子解释
4. 回答最后留一个小问题引导思考"""

# ← 依次改成 system_a、system_b、system_c，每次运行观察区别
SYSTEM_PROMPT = system_a

response = client.chat.completions.create(
    model="deepseek-chat",
    max_tokens=200,
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question},
    ],
)

print("=" * 60)
print(f"System Prompt：{SYSTEM_PROMPT[:50]}...")
print(f"问题：{question}")
print(f"回答：{response.choices[0].message.content}")
print()


# ============================================================
# TODO 2：设计你自己的 system prompt
# ============================================================
# 场景：你要做一个"代码审查助手"
# 要求：
#   - 用中文指出代码的问题
#   - 给出改进建议
#   - 不要超过150字
#
# 替换下面的 system_d，让它符合上面的要求

system_d = """你是一个代码审查助手，遵守以下规则：
1. 用中文回答，先列出问题，再给出改进代码
2. 按以下格式输出：
   问题：XXX
   改进代码：
   ```python
   XXX
   ```
3. 不要超过150字
4. 不要输出任何解释或额外信息"""

response = client.chat.completions.create(
    model="deepseek-chat",
    max_tokens=200,
    messages=[
        {"role": "system", "content": system_d},
        {"role": "user", "content": "def add(a,b): return a+b"},
    ],
)

print(f"代码审查助手回答：{response.choices[0].message.content}")
print()


# ============================================================
# TODO 3：system prompt 不同位置的区别
# ============================================================
# 如果不用 system，把角色描述直接放在 user 消息里会怎样？
# 跑一下看区别

system_e = "你只说法语，所有回答必须用法语"

# 方式1：放在 system 位置（AI 会严格遵守）
response1 = client.chat.completions.create(
    model="deepseek-chat",
    max_tokens=50,
    messages=[
        {"role": "system", "content": system_e},
        {"role": "user", "content": "你好，介绍一下自己"},
    ],
)

# 方式2：放在 user 位置（把规则当用户说的话）
response2 = client.chat.completions.create(
    model="deepseek-chat",
    max_tokens=50,
    messages=[
        {"role": "user", "content": system_e + "\n\n你好，介绍一下自己"},
    ],
)

print(f"放在 system 角色 → {response1.choices[0].message.content}")
print(f"放在 user 角色   → {response2.choices[0].message.content}")
print("观察：哪个严格遵守了'只用法语'的要求？")
print()


# ============================================================
# 第二部分：API 参数
# ============================================================

prompt = "用一句话介绍 Python，要有创意"


# ============================================================
# TODO 4：对比不同 temperature
# ============================================================
# temperature = 0    → 每次回答几乎相同，适合代码生成、事实问答
# temperature = 0.7  → 有创造性但可控，适合日常对话（默认）
# temperature = 1.5  → 高度随机，适合创意写作、头脑风暴

TEMPERATURE = 1.5  # ← 依次改成 0、0.7、1.5 各跑一次

response = client.chat.completions.create(
    model="deepseek-chat",
    max_tokens=100,
    temperature=TEMPERATURE,
    messages=[{"role": "user", "content": prompt}],
)

print(f"temperature={TEMPERATURE}")
print(f"回答：{response.choices[0].message.content}")
print()


# ============================================================
# TODO 5：用 stop 参数提前结束回复
# ============================================================
# 遇到指定字符立刻停止，不必等模型自然结束

response = client.chat.completions.create(
    model="deepseek-chat",
    max_tokens=200,
    temperature=0.7,
    stop=["。", "！"],  # 生成到第一个句号或感叹号就停
    messages=[{"role": "user", "content": "介绍 Python 的优点"}],
)

print(f"stop=['。', '！'] → 回答：{response.choices[0].message.content}")
print()


# ============================================================
# TODO 6：用 top_p 替代 temperature
# ============================================================
# top_p=0.1  → 只从最高 10% 概率的词里抽，输出保守
# top_p=1.0  → 考虑所有词，和默认 behavior 一样
# 一般建议 temperature 和 top_p 只调一个

response = client.chat.completions.create(
    model="deepseek-chat",
    max_tokens=100,
    top_p=0.3,
    messages=[{"role": "user", "content": prompt}],
)

print(f"top_p=0.3（保守模式）→ 回答：{response.choices[0].message.content}")
print()


# ============================================================
# TODO 7（思考题）：选参数组合
# ============================================================
# 根据场景选 temperature：
#
#   场景 A：代码自动补全 → temperature=0
#   场景 B：客服机器人   → temperature=0.7
#   场景 C：小说创作     → temperature=1.5
#   场景 D：头脑风暴     → temperature=1.5
#
#   Day 6 的 Python 教学助手适合什么 temperature？为什么？
#0.7~0.9 合适 教学准确的同事富有创造性，能举生活例子引导思考
# 提示：教学需要准确（不能胡说）但又要有趣（不能太死板）
#       你觉得 0.3~0.5 合适，还是 0.7~0.9 合适？
