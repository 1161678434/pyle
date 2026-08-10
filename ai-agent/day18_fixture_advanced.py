"""
Day 18：fixture 进阶 —— scope、conftest、yield
=================================================
昨天学了 fixture 的基本用法。今天解决三个进阶问题：

1. scope：fixture 每次测试都重新执行太浪费？可控制复用范围
2. conftest.py：多个测试文件都要用同一个 fixture？不用到处复制
3. yield：测试完需要清理（删文件、断连接）？用 yield 做 teardown
"""
import pytest
import os
import tempfile


# ============================================================
# 第一部分：scope —— 控制 fixture 的生命周期
# ============================================================
# 默认 scope="function"：每个测试函数调用一次（昨天看到的）
# scope="module"    ：整个测试文件调用一次，结果被所有测试共享
# scope="session"   ：整个测试运行过程中只调用一次
#
# 用 print 看调用次数，理解 scope 的区别。

# ← 写代码：创建两个 fixture，都返回一个自增的计数器
#
# fixture A：scope="function"（默认）
#   每次被调用时 count += 1，print 当前 count，return count
#
# fixture B：scope="module"
#   同样的逻辑，但声明 scope="module"

call_count = 0  # 模块级变量，用来验证 module scope

@pytest.fixture(scope="module")
def module_counter():
    """模块级 fixture：整个文件只调用一次"""
    global call_count
    call_count += 1
    print(f"  module_counter 被调用，count={call_count}")
    return call_count


# TODO 1：仿照 module_counter，写一个 function 级别的 function_counter
# 提示：不写 scope 参数就是默认 scope="function"
@pytest.fixture(scope="function")
def function_counter():
    """函数级 fixture：每个测试用例都调用一次"""
    global call_count
    call_count += 1
    print(f" function_counter 被调用，count={call_count}")
    return call_count

# 三个测试都用同一个 module_counter
def test_module_scope_a(module_counter):
    print(f"  test_a 拿到: {module_counter}")


def test_module_scope_b(module_counter):
    print(f"  test_b 拿到: {module_counter}")


def test_module_scope_c(module_counter):
    print(f"  test_c 拿到: {module_counter}")
# 观察：这三个测试拿到的 function_counter 是同一个（count 都是 1），说明 module_counter 只被调用了一次
def test_function_scope_a(function_counter):
    print(f"  test_a 拿到: {function_counter}")


def test_function_scope_b(function_counter):
    print(f"  test_b 拿到: {function_counter}")


def test_function_scope_c(function_counter):
    print(f"  test_c 拿到: {function_counter}")


# ============================================================
# 第二部分：yield —— 测试后清理
# ============================================================
# 很多测试场景需要"准备 → 使用 → 清理"：
#   创建临时文件 → 测试读写 → 删除文件
#   连接数据库    → 测试查询 → 断开连接
#   修改环境变量   → 测试功能 → 恢复原值
#
# yield 就是做这个的：
#   @pytest.fixture
#   def my_fixture():
#       # ← yield 之前的代码：准备（setup）
#       resource = 创建资源()
#       yield resource
#       # ← yield 之后的代码：清理（teardown）

# TODO 2：写一个临时文件的 fixture，用 yield 保证测试后自动清理

# ← 写代码：创建 fixture temp_file
#   - 用 tempfile.mkstemp() 创建临时文件，拿到文件路径
#   - 往文件里写一行测试数据
#   - yield 文件路径（测试函数会拿到这个路径）
#   - yield 之后：用 os.remove() 删除文件
#   - 用 print 日志标记 setup 和 teardown 的时刻
@pytest.fixture

def temp_file():
    """一个临时文件 fixture，测试后自动删除"""
    fd, path = tempfile.mkstemp()
    print(f"  temp_file fixture setup：创建临时文件 {path}")
    with os.fdopen(fd, 'w') as tmp:
        tmp.write("这是一些测试数据\n")
    yield path
    os.remove(path)
    print(f"  temp_file fixture teardown：删除临时文件 {path}")


def test_read_temp_file(temp_file):
    """测试能读取临时文件"""
    # ← 改：用 temp_file fixture，读取文件内容并断言
    with open(temp_file, 'r') as f:
        content = f.read()
    assert content == "这是一些测试数据\n"


def test_temp_file_exists(temp_file):
    """测试临时文件存在"""
    # ← 改：用 temp_file fixture，用 os.path.exists 断言文件存在
    assert os.path.exists(temp_file) == True



# ============================================================
# TODO 3：模拟"连接资源"的 setup/teardown 模式
# ============================================================
# 实际项目中常见的模式：连接 → 操作 → 断开

class FakeDB:
    """模拟数据库连接"""
    def __init__(self):
        self.connected = False
        self.data = {}

    def connect(self):
        self.connected = True
        print("    数据库已连接")

    def close(self):
        self.connected = False
        print("    数据库已断开")

    def insert(self, key, value):
        self.data[key] = value

    def get(self, key):
        return self.data.get(key)


# TODO 3：写一个 db fixture，用 yield 实现自动连接和断开
#
# @pytest.fixture
# def db():
#     db = FakeDB()
#     db.connect()
#     yield db
#     db.close()
#
# 然后写两个测试，用 db fixture 做 insert 和 get，验证数据持久性
@pytest.fixture
def db():
    """一个模拟数据库连接的 fixture，自动连接和断开"""
    db = FakeDB()
    db.connect()
    yield db
    db.close()

def test_db_insert_get(db):
    """测试数据库的插入和查询过程"""
    db.insert("key1", "value1")
    assert db.get("key1") == "value1"
def test_db_persistence(db):
    """测试数据库连接的持久性"""
    db.insert("key1", "value1")
    assert db.get("key1") == "value1"
    assert db.get("nonexistent") is None # 测试查询不存在的键返回 None

# ============================================================
# TODO 4（思考题）
# ============================================================
# 问题 1：scope="module" 的 fixture 被文件里所有测试共享，
#   如果 test_a 修改了 fixture 返回的数据，test_b 会看到修改吗？
#   这是个好习惯还是坏习惯？为什么？
# 答：如果 fixture 返回的是可变对象（比如列表、字典），那么 test_a 修改了这个对象后，test_b 也会看到修改，因为它们共享同一个对象。这可能会导致测试之间相互影响，增加测试的耦合度和不确定性，因此通常被认为是一个坏习惯。为了避免这种情况，可以在 fixture 中返回一个新的对象，或者使用 scope="function" 来确保每个测试都拿到独立的数据。
# 问题 2：yield 和 return 有什么区别？fixture 里能同时用两个吗？
# 答：yield 和 return 的区别在于 yield 可以分为两部分：yield 之前的代码是 setup（准备），yield 之后的代码是 teardown（清理）。当测试函数使用这个 fixture 时，pytest 会先执行 yield 之前的代码，然后把 yield 后面的值传递给测试函数，等测试函数执行完后，再执行 yield 之后的代码来进行清理。而 return 则只能返回一个值，没有分隔 setup 和 teardown 的功能。在 fixture 中不能同时使用两个 yield 或 return，因为 fixture 只能有一个返回值，并且只能有一个 setup/teardown 流程。
# 问题 3：假设有一个 fixture 需要打开浏览器，耗时 5 秒，
#   10 个测试都用它，应该用 scope="function" 还是 scope="module"？
#   权衡是什么？
# 答：如果这个 fixture 用 scope="function"，那么每个测试都会单独打开一次浏览器，耗时 5 秒，总共耗时 50 秒；如果用 scope="module"，那么整个测试文件只打开一次浏览器，所有测试共享这个浏览器实例，总共耗时 5 秒。权衡的因素包括：测试之间是否需要独立的浏览器环境（如果需要，应该用 function），以及测试运行时间的要求（如果时间敏感，应该用 module）。如果测试之间没有相互影响的风险，并且希望节省时间，那么使用 scope="module" 是更好的选择。

# ============================================================
# 运行
# ============================================================
# pytest day18_fixture_advanced.py -v -s
# 观察 scope 不同导致的 print 次数差异
#
# 本文件还需要一个 conftest.py（见 TODO 5）：
#   把 sample_response fixture 从 day17 移过来，
#   然后在 day18 里直接用——模拟跨文件共享 fixture
