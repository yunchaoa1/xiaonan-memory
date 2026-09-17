# Hermes Self-improvement Review 机制 · 破案实录

> 2026-08-06 在 D:\Hermes 技能治理完成后发现磁盘出现 3 个功能高度重合的治理技能。
> 本文件记录完整的发现 + 调查 + 结论过程。

## 症状

完成 120→60 技能治理后，发现 skills 目录出现：

| 文件 | 时间 | 作者标记 |
|------|------|---------|
| `software-development/skill-library-governance/` | 12:23 | ❓中文版，含 references/ + scripts/ |
| `software-development/skill-library-maintenance/` | 12:57 | ❓中文版，"管理 curator 自动归档冲突" |
| 根级 `skill-library-maintenance/` | 12:59 | 人工创建的版本 |

——三个技能都在教"怎么维护技能库"，互相高度重叠。

## 调查过程

### 1. 内容指纹分析
12:23 的 governance 和 12:57 的 maintenance 都引用了本次会话才产生的事实：
- "管理 curator 自动归档冲突"（本次 12:xx 讨论的 curator 调整）
- "构建技能总调度"（本次 12:xx 创建的 skill-router）
- references/2026-08-06-governance-run.md 完整记录了本次治理的执行过程
- scripts/disable_skills.py / fix_dangling_refs.py 是本次治理用到的临时脚本的固化版

→ 写这些技能的实体**完整参与了本次会话**。

### 2. 日志查证
搜索 Hermes 日志目录，关键发现：
```
desktop.log:
💾 Self-improvement review: Skill 'skill-library-governance' created.
💾 Self-improvement review: Skill 'skill-library-maintenance' created.
💾 Self-improvement review: Patched SKILL.md in skill 'working-with-fange' (1 replacement).
```

### 3. 源码定位
`agent/background_review.py:796` 输出 `💾 Self-improvement review`
→ 确认是 Hermes 内置的后台自动审查机制。

## 结论：不是"另一个小南"，是 Hermes 的自动机制

**机制**：`agent/background_review.py` 在会话运行期间/结束后自动启动，读取会话记录并：
1. 自动创建技能（含 SKILL.md + references/ + scripts/ 固化）
2. 自动 patch 现有技能（把会话教训写进相关技能）

**质量评估**：它生成的技能质量很高——准确记录了本次治理的完整流程（curator 参数、块标量坑、patch 拒绝、所有操作命令），比我手动写的还全。

**冲突场景**：如果人工恰好同时在做同一件事（创建同样的技能），就会产生重复。本次是"后台 review 自动创建 software-development/skill-library-maintenance"+"人工 write_file 创建根级 skill-library-maintenance"→ 两个并存。

## 防冲突规则（已写入 skill-library-maintenance 正文）

1. **创建技能必须用 `skill_manage(action='create')`**（有重名保护）
2. **绝不要用 `write_file` 直接写技能目录**（无重名保护）
3. **发现重复后**：对比各版本 → 合并 → 归档其余 → 验证
4. Self-improvement review 是好事（省事沉淀），不是 bug——只需要人工审核和去重

## 处置结果

三个版本合并为一个 `software-development/skill-library-maintenance`：
- 保留了后台 review 的详细版（7235字节）+ 它的 references/ 和 scripts/
- 合并了人工创建的 scripts/health_check.py
- governance 和根级版均归档到 skills_archive/
