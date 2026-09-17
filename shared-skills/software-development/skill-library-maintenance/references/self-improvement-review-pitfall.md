# Self-Improvement Review 陷阱（2026-08-06 发现）

## 背景

Hermes 有内置后台机制 `agent/background_review.py`，会**自动**读取会话经验、创建/修改技能。
日志标记：`💾 Self-improvement review: ...`

## 它做了什么（实测）

在一个涉及技能治理的会话中，它创建了：
1. `software-development/skill-library-governance`（12:23，含 references/ 和 scripts/）
2. `software-development/skill-library-maintenance`（12:57，7235 字节）
3. 同时 patch 了 `working-with-fange/SKILL.md`（加了"凡哥要求先查证再回答"规则）

这几乎和我手动创建的 `skill-library-maintenance`（12:59，根级 6309 字节）完全相同——造成了三份重复。

## 如何检查

```bash
grep "Self-improvement review" D:\Hermes\logs\desktop.log
```

查看它创建/修改了哪些技能。

## 如何处置

1. **不关停**：它沉淀的内容质量通常很高（会话细节完整），是"白捡的省事"
2. **去重**：对比 review 版本和手动版本 → 合并优势 → 保留最佳 → 归档其余
3. 如果 review 的软件分类和你手动的不一致，以内容质量为准，不必纠结路径

## 防冲突规则

- 创建技能前先检查 `skills_list` → `skill_view` 确认不存在同名/近义技能
- 用 `write_file` 创建技能时（绕过 skill_manage 重名保护），特别注意检查已有技能
- 发现 review 和手动同时生成后，优先合并而不是各留各的
