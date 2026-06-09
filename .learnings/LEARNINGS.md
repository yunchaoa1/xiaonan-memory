# Learnings

Corrections, insights, and knowledge gaps captured during development.

**Categories**: correction | insight | knowledge_gap | best_practice
**Areas**: frontend | backend | infra | tests | docs | config
**Statuses**: pending | in_progress | resolved | wont_fix | promoted | promoted_to_skill

## Status Definitions

| Status | Meaning |
|--------|---------|
| `pending` | Not yet addressed |
| `in_progress` | Actively being worked on |
| `resolved` | Issue fixed or knowledge integrated |
| `wont_fix` | Decided not to address (reason in Resolution) |
| `promoted` | Elevated to CLAUDE.md, AGENTS.md, or copilot-instructions.md |
| `promoted_to_skill` | Extracted as a reusable skill |

## Skill Extraction Fields

When a learning is promoted to a skill, add these fields:

```markdown
**Status**: promoted_to_skill
**Skill-Path**: skills/skill-name
```

Example:
```markdown
## [LRN-20250115-001] best_practice

**Logged**: 2025-01-15T10:00:00Z
**Priority**: high
**Status**: promoted_to_skill
**Skill-Path**: skills/docker-m1-fixes
**Area**: infra

### Summary
Docker build fails on Apple Silicon due to platform mismatch
...
```

---

## [LRN-20260609-001] correction

**Logged**: 2026-06-09T01:22:00Z
**Priority**: critical
**Status**: resolved
**Area**: docs
**Promoted**: MEMORY.md 规则第3条 + 第8条

### Summary
凡哥要求所有文字内容不用代码块、不截断、不带滚动条，让内容一眼看完。
但我多次在发送提示词/技术内容时下意识使用代码块包裹。

### Root Cause
DeepSeek 默认输出习惯倾向用代码块格式化技术内容。
我需要主动对抗这个倾向：凡哥的飞书对话中，任何长文本都直接裸发，不包裹。

### Resolution
- 已在 MEMORY.md 规则第3条和第8条重复强调
- 本次对话中当场修正
- 今后每次发提示词前自我检查：有没有代码块？

---

