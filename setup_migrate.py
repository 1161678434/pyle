"""
迁移设置脚本 — 在新电脑上运行
用法: python setup_migrate.py
功能: 安装依赖 + 把学习进度记忆文件复制到正确位置
"""
import os
import shutil
import sys
import subprocess

# 1. 安装依赖
print("=" * 50)
print("Step 1: 安装依赖...")
subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
print("依赖安装完成\n")

# 2. 定位记忆目录
# 规则: ~/.claude/projects/<路径中 :和/ 替换为->/memory/
project_dir = os.path.abspath(".")
# Windows: d:\pyle → d--pyle
# Mac/Linux: /home/user/pyle → -home-user-pyle
munged = project_dir.replace(":\\", "--").replace(":", "--").replace("\\", "-").replace("/", "-")
if munged.startswith("-"):
    munged = munged[1:]  # 去掉开头的 -

memory_dest = os.path.expanduser(f"~/.claude/projects/{munged}/memory/")
os.makedirs(memory_dest, exist_ok=True)
print(f"项目路径: {project_dir}")
print(f"记忆目录: {memory_dest}\n")

# 3. 从迁移包复制记忆文件
# 记忆文件应该在当前目录的 memory_backup/ 下
memory_source = os.path.join(project_dir, "memory_backup")
if os.path.isdir(memory_source):
    print("Step 2: 复制学习进度记忆...")
    for f in os.listdir(memory_source):
        src = os.path.join(memory_source, f)
        dst = os.path.join(memory_dest, f)
        shutil.copy2(src, dst)
        print(f"  ✅ {f} → {dst}")
    print("记忆复制完成\n")
else:
    print("⚠️  未找到 memory_backup/ 目录，跳过记忆复制")
    print("   请确保已从旧电脑复制该目录\n")

print("=" * 50)
print("✅ 迁移设置完成！")
print(f"下一次 Claude Code 在 {project_dir} 启动时会读取学习进度")
