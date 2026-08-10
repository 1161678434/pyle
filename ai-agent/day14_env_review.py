"""
Day 14：环境变量巩固 —— dotenv 到底做了什么？
===============================================
从 Day 5 你就在用 .env 和 os.getenv()，但你真的理解它怎么工作吗？
今天把"能用"变成"理解"。
"""
import os
from dotenv import load_dotenv

# ============================================================
# 第一部分：回顾 —— 你已经知道的部分
# ============================================================
# .env 文件：   存敏感信息（API密钥），不提交到 Git
# dotenv 库：   把 .env 里的内容读到环境变量中
# os.getenv()： 读取环境变量

# 你的 ai_utils.py 里就是这么用的：
#   from dotenv import load_dotenv
#   load_dotenv()
#   API_KEY = os.getenv("DEEPSEEK_API_KEY")


# ============================================================
# TODO 1：探究 load_dotenv() 到底做了什么
# ============================================================
# load_dotenv() 做的事很简单：
#   1. 找到 .env 文件
#   2. 逐行解析 KEY=VALUE
#   3. 把每一对写到 os.environ 字典里
#
# 动手验证：

print("=" * 50)
print("TODO 1：load_dotenv 做了什么")
print("=" * 50)

# 加载前，先看看 os.environ 里有没有 DEEPSEEK_API_KEY
# os.environ 是一个字典，存着所有系统环境变量
os_env = dict(os.environ)
print(f"os.environ 中有什么环境变量？（前5个）{list(os.environ.keys())[:5]} ...")
print(f"os.environ 中的环境变量数量：{len(os_env)}")
print(f"加载前 os.environ 中 DEEPSEEK_API_KEY 是否存在：{'DEEPSEEK_API_KEY' in os.environ}")
# ← 写代码：打印 os.environ 里 DEEPSEEK_API_KEY 是否存在（用 in 判断）
# 注意：因为 load_dotenv() 在 import 时可能已经被 ai_utils 调用过了，
# 所以这里的"加载前"其实已经被加载了。没关系，关键是理解原理。

# 手动调用一次 load_dotenv()
load_dotenv()
app_key = os.getenv("DEEPSEEK_API_KEY")
print(f"os.environ 中的环境变量数量：{len(os.environ)}")
print(f"打印 app_key 的前8个字符：{app_key[:8]}...")  # 打印前8个字符，遮住后面
print(f"加载前 os.environ 中 DEEPSEEK_API_KEY 是否存在：{'DEEPSEEK_API_KEY' in os.environ}")
# ← 写代码：再次检查 DEEPSEEK_API_KEY 是否存在，并打印它的前8个字符（遮住后面的）
# 提示：os.getenv("DEEPSEEK_API_KEY") 或 os.environ["DEEPSEEK_API_KEY"]

print()

# TODO 1 思考：
# 为什么 load_dotenv() 被调用多次也不会出问题？
# 因为 load_dotenv() 只是把 .env 里面的键值写到 os.environ 中，而 os.environ 是一个普通的字典，重复写同一个键不会报错，只会覆盖之前的值（但因为值是一样的，所以没区别）。所以即使 load_dotenv() 被调用多次，也不会有副作用。

# ============================================================
# TODO 2：os.getenv() vs os.environ[] —— 区别在哪？
# ============================================================
# 两种方式都能拿到环境变量，但行为不同：

print("=" * 50)
print("TODO 2：os.getenv() vs os.environ[]")
print("=" * 50)

# ← 写代码：分别用 os.getenv("不存在的变量") 和 os.environ["不存在的变量"]，
#    对比它们的行为有什么不同（一个返回 None，一个抛异常 KeyError）
try:
    print(os.getenv("不存在的变量"))  # 返回 None
except Exception as e:
    print(f"os.getenv 抛出异常：{e}")
try:
    print(os.environ["不存在的变量"])  # 抛出 KeyError
except Exception as e:
    print(f"os.environ[] 抛出异常：{e}")

print()


# ============================================================
# TODO 3：os.getenv() 的第二个参数 —— 默认值
# ============================================================
# 当环境变量不存在时，可以给一个备选值：

print("=" * 50)
print("TODO 3：默认值")
print("=" * 50)

# ← 写代码：
# model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
# 打印 model，理解第二个参数的作用
model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
print(f"使用的模型是：{model}")


# ← 写代码：
# max_tokens = os.getenv("MAX_TOKENS", "500")
# 打印 max_tokens 和它的类型，思考：getenv 返回的永远是字符串，怎么转成整数？
max_tokens = os.getenv("MAX_TOKENS", "500")
print(f"max_tokens 的值：{max_tokens}, 类型：{type(max_tokens)}")
# 提示：可以用 int() 转换，但要注意如果环境变量里不是数字
try:
    max_tokens_int = int(max_tokens)
    print(f"转换后的 max_tokens: {max_tokens_int}, 类型: {type(max_tokens_int)}")
except ValueError:
    print("环境变量 MAX_TOKENS 不是一个有效的整数！")

print()


# ============================================================
# TODO 4（动手）：写一个 mini 版的 load_dotenv
# ============================================================
# 不调用 dotenv 库，自己手动解析 .env 文件

print("=" * 50)
print("TODO 4：手动解析 .env")
print("=" * 50)

def my_load_dotenv(filepath=".env"):
    """手动解析 .env 文件，把内容加载到 os.environ"""
    # ← 写你的代码：
    # 1. 用 open() 打开 .env 文件
    # 2. 逐行读取
    # 3. 跳过空行和注释行（以 # 开头）
    # 4. 按 = 分割每一行，得到 key 和 value
    # 5. 去掉 value 首尾多余的引号和空格
    # 6. os.environ[key] = value
    try:
        with open(filepath, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    os.environ[key] = value
    except FileNotFoundError:
        print(f"文件 {filepath} 不存在!")
    except Exception as e:
        print(f"加载 .env 文件时发生错误: {e}")
    

# 测试自己的实现
my_load_dotenv()
print(f"my_load_dotenv 验证：{os.getenv('DEEPSEEK_API_KEY', '未加载')[:8]}...")
print()


# ============================================================
# TODO 5（思考题）：环境变量的常见坑
# ============================================================
# 问题 1：如果把 .env 文件提交到 Git，会发生什么？怎么防止？
# 答：提交了就暴露了APikey，可能被盗用，恶意使用，导致费用增加甚至账号被封。防止方法是在 .gitignore 文件里添加 .env，这样 Git 就不会跟踪这个文件了。
# 问题 2：.env 里的 KEY = VALUE 中间的等号两边有空格会怎样？
# 答: 可能会被解析成 key="KEY " 和 value=" VALUE"，导致读取环境变量时出问题。正确的做法是确保等号两边没有多余的空格，或者在解析时使用 strip() 去掉空格。
# 问题 3：同一台机器上开发多个项目，每个项目有不同的 API Key，怎么管理？
# 答：可以为每个项目创建不同的 .env 文件，并在项目的根目录下使用 load_dotenv() 加载对应的 .env 文件。或者在系统环境变量里设置不同的变量名，比如 DEEPSEEK_API_KEY_PROJECT1, DEEPSEEK_API_KEY_PROJECT2，然后在代码里根据需要读取对应的环境变量。
# 问题 4：部署到服务器时，.env 文件怎么处理？直接在服务器上创建吗？
# 答：可以直接在服务器上创建 .env 文件，或者在服务器的环境变量配置里设置对应的变量。也可以使用部署工具（如 Docker、Kubernetes）提供的方式来管理环境变量，比如 Docker 的 --env-file 参数或者 Kubernetes 的 ConfigMap 和 Secret。

