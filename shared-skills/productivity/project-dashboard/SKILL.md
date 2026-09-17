---
name: project-dashboard
description: Read, navigate, and update the project dashboard (DASHBOARD.md) — the single source of truth for all active projects, priorities, and daily pipelines.（中文触发：读取、更新DASHBOARD.md总控台（项目状态、技能索引、知识库清单）时加载）
---

# Project Dashboard

Use this skill when starting a session, when the user asks about work priorities or project status, or when you need to orient yourself to the current state of all workstreams.

## Core workflow

1. **Session start** — read `DASHBOARD.md` FIRST, before doing anything else. The user expects you to know what's going on without being told.
2. **After major changes** — update the dashboard to reflect new status, completed milestones, or priority shifts.
3. **When asked "what are we working on"** — the dashboard IS the answer; don't search the filesystem or guess.

## Dashboard structure

A well-formed DASHBOARD.md has:
- **Sections by domain** (company, personal, daily pipeline)
- **Status tables** with clear indicators (✅ done, 🔜 next, 🧠 in design)
- **Priority list** — what's being worked on right now
- **Technical references** — environment paths, ports, configs
- **Last-updated timestamp** so you know how fresh the information is

### 树形总控台（新版）

交互式树形 UI，可点击展开/折叠，颜色状态可视化。两个小南共享同一棵树，通过 git 同步。

**路径规则：**优先使用同步仓库里的总控台：
- Markdown：`D:\Hermes\xiaonan-memory\DASHBOARD.md`
- 树形 UI：`D:\Hermes\xiaonan-memory\dashboard-tree.html`

如果旧记忆或旧技能提到 `D:\\SDkechengz\\dashboard-tree.html`，不要直接照搬；先验证当前文件是否存在，优先以 `xiaonan-memory` 仓库里的版本作为共享真相源。

## Execution State Integrity

For delegated or multi-stage work, the dashboard must distinguish at least: planned, dispatched, running, artifact_saved, independently_verified, blocked, and completed. A todo marked `in_progress` is not evidence that a worker is running. A worker's completion message is not evidence that an artifact exists. Promote a stage only after checking its concrete handle: an existing file with size/content, a command result, a URL/ID, or an independent verification result. If a task times out or is truncated, keep it blocked/unfinished until the handle is verified; do not record it as complete.

For high-load creative production, split work into a small validated sample before expanding a whole chapter/season. Preserve failed revisions as comparison evidence, but never replace a verified artifact with an unverified report. After each major change, record the artifact version, verification scope, and remaining boundary in the dashboard.

## Pitfalls

- **NEVER** start working without reading the dashboard first. The user built it precisely so you don't ask "what are we working on."
- Don't search the filesystem for project context when DASHBOARD.md exists — it's the single source of truth.
- After platform migrations, check that the dashboard path hasn't changed and that all referenced paths still resolve.
- When multiple dashboard copies exist (`D:\Hermes\DASHBOARD.md` vs `D:\Hermes\xiaonan-memory\DASHBOARD.md`), treat the git-synced `xiaonan-memory` copy as the durable cross-agent source unless the user explicitly says otherwise.
