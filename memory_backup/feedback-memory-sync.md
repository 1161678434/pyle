---
name: feedback-memory-sync
description: 记忆文件双向同步规则 — 本地和备份需保持一致
metadata: 
  node_type: memory
  type: feedback
  originSessionId: c30bfdb0-df68-4d5e-8567-d851c321099d
---

记忆文件有两个位置，需要保持双向同步：
- 本地：`~/.claude/projects/d--pyle/memory/`
- 备份：`d:\pyle\memory_backup\`

**Why:** 用户可能在别处学习时更新备份文件，也可能在此处更新本地文件，两边需要相互同步。

**How to apply:**
1. 每次更新记忆文件时，同时更新两个位置
2. 更新前先比较两边时间戳，以较新为准
3. 同步完成后再进行修改，确保不会丢失另一边的更新
