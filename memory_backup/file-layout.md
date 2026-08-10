---
name: file-layout
description: 练习文件存放位置 — 按学习计划分目录
metadata: 
  node_type: memory
  type: project
  originSessionId: eb41955a-bcba-4f4f-bcb3-b73e2c7e8916
---

# 文件存放位置

两个学习计划对应两个目录，后续新增文件按此规则放置。

## D:\pyle 目录结构

```
D:\pyle\
├── ai-agent\          ← AI Agent 学习计划（已完成 Day 1-33，暂停）
├── auto-test\          ← 自动化测试进阶计划（进行中）
├── memory_backup\      ← Claude memory 备份
└── *.ps1, .env ...    ← 共享配置文件
```

## 新增规则

| 学习计划 | 目录 | 文件命名 | 示例 |
|----------|------|----------|------|
| AI Agent | `ai-agent/` | `dayXX_*.py` | `ai-agent/day34_xxx.py` |
| 接口自动化 | `auto-test/` | `api_dayX_*.py` | `auto-test/api_day6_xxx.py` |
| 性能测试 | `auto-test/` | `perf_dayX_*.py` | `auto-test/perf_day4_xxx.py` |
| CI/CD | `auto-test/` | `cicd_dayX_*.py` | `auto-test/cicd_day1_xxx.py` |
| 测试数据 | `auto-test/` | `data_dayX_*.py` | `auto-test/data_day1_xxx.py` |
| 框架/共享 | `auto-test/` | `conftest.py`, `config/`, `utils/` | — |

## 当前进度

- **ai-agent/**：Day 1-33 完成，暂停中
- **auto-test/**：Charles ✅ → 接口自动化 ✅ (5/5) → 性能测试 🔄 (3/5)
