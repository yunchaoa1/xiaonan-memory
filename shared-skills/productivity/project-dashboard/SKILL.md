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

## 每日项目拓扑图（WPS 演示 · 全本地）

凡哥定的项目跟踪方式：**每天发小何/小吴的飞书工作日报截图 → 小南读图 → 更新拓扑图**（豆包已不续费，绘图工作由小南接手）。

**四件套流程：**
1. **读图**：逐字读日报截图（姓名 / 提交时间 / 今日完成项 / 卡点 / 解决方法），人名对应：**小何=何锦波**（框架+后端）、**小吴=吴伟俊**（前端+UI）。
2. **改数据**：更新生成脚本 `D:\Hermes\scripts\gen_topology_pptx.py` 的卡片内容与待办段（第 1 页=拓扑总览，第 2 页=日报明细）。
3. **出图**：`python D:\Hermes\scripts\gen_topology_pptx.py "D:\Documents\我的文档\拓扑图\项目拓扑图_<YYYYMMDD>_v<N>.pptx"`
4. **校验+交付**：用 python-pptx 遍历形状做**越界自检**（两页都要），再用 `wpp.exe` 打开并截图给凡哥；同步把变化写进 DASHBOARD 与共享文件 A 区。

**字段规则（凡哥 2026-09-20 定，长期有效）：** 每个项目拆功能模块 → 先框架后逐个实现；模块必须写**开始时间 / 预计交付时间 / 状态**；超出预计交付 → 必须写**卡点在哪 / 解决方案 / 再次交付时间**；**图的最下方 = 待办事项**。

**陷阱：**
- WPS 桌面版**没有**本地流程图组件（`office6/addons` 里只有 `kpromeprocesson`＝在线 ProcessOn，需会员）→ **不要去找"流程图板块下载"**；本地做法＝WPS 演示原生形状（python-pptx 生成 .pptx，双击可编辑）。
- 只改脚本的数据段，别动布局函数；每次生成后必做越界自检。
- 旧版 pptx 被 WPS 打开时会锁定 → 删不掉；让凡哥关掉旧标签页再清理（换版即清的惯例）。
- 术语统一：日报里的"智题分"按口径写作**智提分**；日报卡点与之前口径不一致时，**先问凡哥是同一问题还是新问题**，别自己判断。

## Execution State Integrity

For delegated or multi-stage work, the dashboard must distinguish at least: planned, dispatched, running, artifact_saved, independently_verified, blocked, and completed. A todo marked `in_progress` is not evidence that a worker is running. A worker's completion message is not evidence that an artifact exists. Promote a stage only after checking its concrete handle: an existing file with size/content, a command result, a URL/ID, or an independent verification result. If a task times out or is truncated, keep it blocked/unfinished until the handle is verified; do not record it as complete.

For high-load creative production, split work into a small validated sample before expanding a whole chapter/season. Preserve failed revisions as comparison evidence, but never replace a verified artifact with an unverified report. After each major change, record the artifact version, verification scope, and remaining boundary in the dashboard.

## Pitfalls

- **NEVER** start working without reading the dashboard first. The user built it precisely so you don't ask "what are we working on."
- Don't search the filesystem for project context when DASHBOARD.md exists — it's the single source of truth.
- After platform migrations, check that the dashboard path hasn't changed and that all referenced paths still resolve.
- When multiple dashboard copies exist (`D:\Hermes\DASHBOARD.md` vs `D:\Hermes\xiaonan-memory\DASHBOARD.md`), treat the git-synced `xiaonan-memory` copy as the durable cross-agent source unless the user explicitly says otherwise.
