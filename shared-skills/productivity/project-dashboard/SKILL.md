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

## 每日项目拓扑图（draw.io 树形 WBS · 全本地 · 2026-09-23 起）

凡哥定的项目跟踪方式：**凡哥发飞书工作日报截图 → 小南读图 → 更新拓扑图 + 台账**（豆包已不续费，绘图工作由小南接手）。**四人报**：小何/小吴/小李/小唐。

**四件套流程：**
1. **读图**：逐字读日报截图（姓名 / 提交时间 / 今日完成项 / 卡点 / 解决方法），人名对应：**小何=何锦波**（框架+后端）、**小吴=吴伟俊**（前端+UI）、**小李=李林**（大模型上下文治理）、**小唐=唐光辉**（多 agent 体系）。
   ⚠️ **按「工作日期」归档，不按提交日期**（2026-09-23 凡哥纠正）：小吴当日 18:00 交（内容＝当日）；**小何次日上午补交前一日**（标题写"09-23 提交"的、内容其实是 09-22）。一次发多份（4 份＝2 天×2 人）时先按工作日期分组；**看着像"重复"的那份先问，别直接丢**。
2. **改数据**：更新 `D:\Hermes\scripts\gen_topology_tree.py` 顶部 `TREE`（**单页树**：根 → 项目 → 模块 → 子节点；**每个节点末尾写 `｜ 负责人`**，无人认领写「待指派」；树最下支＝待办事项）。
3. **出图**：`python D:\Hermes\scripts\gen_topology_tree.py --layout` → 一条命令出 `D:\Documents\我的文档\拓扑图\项目拓扑图_WBS.{drawio,png,svg,pdf}`（含零重叠断言）。画法与坑见技能 `project-topology-diagrams`。
4. **校验+交付**：跑零重叠断言（脚本自带）或 `scripts/drawio_verify.py`；交付 `.drawio`（可编辑源）+ **PNG（发飞书/聊天）** + SVG/PDF（矢量，放大不糊）；同步把变化写进 DASHBOARD 与共享文件 A 区。

**日报口径（凡哥 2026-09-23 定，写通知/收日报都按这个）：** 渠道＝飞书「工作台 → 日报」应用；提交窗口＝**当天 18:00 之后 → 次日 08:00 之前**；**三栏**＝今日工作完成情况 / 遇到的工作卡点 / 解决方法（**没有「明日计划」栏**）。

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
- **写 DASHBOARD 必须验证落地（2026-09-23 实测踩坑）**：用脚本 `s.replace(锚点, 新块)` 更新时，**锚点字符串对不上会静默什么都不做**——脚本照样打印"已更新"，但 git 会告诉你 `nothing to commit`。三步防呆：① 写入前 `assert 锚点 in s` ② 写入后**读回并逐条检查新章节标题是否存在**（`{标题: 标题 in now}`）③ commit 时看输出——**`nothing to commit` ＝ 你的写入没生效**，回去查锚点，别当成功。
- DASHBOARD 的章节锚点会随历史改动漂移（如 `### 10.14` 可能并不存在）；不确定时先 `search_files(pattern='^### ', path=DASHBOARD)` 列表头，再挑一个**当前确实存在**的锚点插入。
