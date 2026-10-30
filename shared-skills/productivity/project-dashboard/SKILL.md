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
3. **出图**：`python D:\Hermes\scripts\gen_topology_tree.py --layout` → 一条命令出 `D:\Documents\我的文档\06_图表\拓扑图\项目拓扑图_WBS.{drawio,png,svg,pdf}`（含零重叠断言）。画法与坑见技能 `project-topology-diagrams`。
4. **校验+交付**：跑零重叠断言（脚本自带）或 `scripts/drawio_verify.py`；交付 `.drawio`（可编辑源）+ **PNG（发飞书/聊天）** + SVG/PDF（矢量，放大不糊）；同步把变化写进 DASHBOARD 与共享文件 A 区。

**日报口径（凡哥 2026-09-23 定，写通知/收日报都按这个）：** 渠道＝飞书「工作台 → 日报」应用；提交窗口＝**当天 18:00 之后 → 次日 08:00 之前**；**三栏**＝今日工作完成情况 / 遇到的工作卡点 / 解决方法（**没有「明日计划」栏**）。

**字段规则（凡哥 2026-09-20 定，长期有效）：** 每个项目拆功能模块 → 先框架后逐个实现；模块必须写**开始时间 / 预计交付时间 / 状态**；超出预计交付 → 必须写**卡点在哪 / 解决方案 / 再次交付时间**；**图的最下方 = 待办事项**。

**陷阱：**
- WPS 桌面版**没有**本地流程图组件（`office6/addons` 里只有 `kpromeprocesson`＝在线 ProcessOn，需会员）→ **不要去找"流程图板块下载"**；本地做法＝WPS 演示原生形状（python-pptx 生成 .pptx，双击可编辑）。
- 只改脚本的数据段，别动布局函数；每次生成后必做越界自检。
- 旧版 pptx 被 WPS 打开时会锁定 → 删不掉；让凡哥关掉旧标签页再清理（换版即清的惯例）。
- 术语统一：日报里的"智题分"按口径写作**智提分**；日报卡点与之前口径不一致时，**先问凡哥是同一问题还是新问题**，别自己判断。

## 凡哥口述 → 落账流水线（2026-10-13 实测 · 一次会话记了 12 条）

凡哥在聊天里口述项目进展/决定（"X 已经搞定""Y 交给了谁""Z 不急"）时，**每一条当场落账**，别攒到最后。固定四步：

1. **先查重再写**：在 `集团/台账数据.json` ＋ `集团/凡哥例行与待办.json` 里 grep 关键词 —— 本次搜"元气森林|浪浪椰"发现**台账里 0 条**（他以为派下去了、账上却没有）。查重同时避免重复记。
2. **写台账**（字段 `work_date / 人 / 项目 / 节点 / 内容 / 状态 / 承诺 / 实际 / 备注 / 来源`）：
   - `来源` 必须写出处：`凡哥 10-13 口述（群里下达）` / `会议纪要` —— 追责与核对全靠它
   - **人未定就填「待确认」，别按岗位猜**；他后面说了再补（本次 3 条待确认最后都补齐）
   - 状态用 `待办 / 进行中 / 已完成 / 已作废`；**他说"没有这个计划"就置「已作废」＋备注原因，不要静默删行**（删了以后没人知道为什么没有）
   - 每次改完打印 `len(rows)` 对账（本次 62 → 73）

3. **改待办清单**（`集团/凡哥例行与待办.json`）：他说"已经做了/发了"→ `状态:"已完成"` ＋ `实际:"日期"`；正在做的＝`进行中`
   - ⚠️ **`截止` 字段是活的**：填成**今天** → **17:30 下班提醒会自动带上这条**（实测 `REMIND_TODAY=2026-10-13 python D:\Hermes\scripts\remind_fange_eod.py`，输出里确实有）→ 当天"要核实的事"用这招，**不必新建 cron**
   - `备注` 写清"卡在谁 / 什么时候催 / 下一步"（例：服务器那条写"前一步＝李林唐光辉的计划，承诺 10-14，已挂 16:00 催办提醒，cron 714d70b72beb"）
4. **回话带对账 ＋ git 提交**：条数变化（台账 62→73、待办 15→9）＋ commit 号；不要只答"已记录"

**⏰ 提醒时刻分两档**（2026-10-13 实测）：**提醒凡哥本人去核实＝11:00**；**催别人交东西＝对方下班前 2 小时（16:00）**（凡哥原话「好的，下午四点提醒我」，催的是"明天下班前交并发方案"）—— 催办要留给对方处理时间。

**⚠️ 节奏铁律**（凡哥 2026-10-13 原话「**一件一件的过，任何事情都是一件一件的来，一步一步的做**」）：报完清单**停住等他挑一件**，一件走完（记账＋回话）再问下一件；**别一次抛多件、别一口气给多个方案**。细则见 `working-with-fange`。

📎 案例与"跨条推导"模式（12 条口述的落账样本、五类合并读结论、回话模板）：`references/凡哥口述落账-案例.md`

📎 **服务器/算力类口述**（服务器交给谁管、租哪家、当月要租哪几台、买什么设备、多少钱）→ 落账后按技能 **`compute-capacity-procurement`** 处理（审核五要素、硬伤预判清单、报价必须索取完整账单、租 vs 买对比）。

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
- **两台电脑同时写总控台：先查号、再写入、后对账（2026-10-10 实测撞号）**：插入编号章节前先 `grep -n "^### 10\.5" DASHBOARD.md` 看**当前最大号**——另一台机可能已经写了同号条目（本次两边各写了一个「10.53」）→ **自己的条目改到下一个空号**，别去动对方的 ✓。
- **提交顺序（有本地未提交改动时）**：`git pull --rebase` 会直接报 `error: Please commit or stash them.` 并中止 ✗ → 正确顺序＝`git add -A && git commit` → `git pull --rebase` → `git push` → `git status -sb` 确认无 ahead/behind；**不要**先 pull 后 commit。
- 用 patch/写文件工具改 DASHBOARD 前**先拉最新**（`git pull`）；被别处（另一台机/子代理）改过而未读就写，工具会提示 `modified by sibling ... never read it` —— 此时先读最新内容再补自己的块，避免覆盖对方发言。
- **⚠️ 大段中文写盘会被静默截断（2026-10-13 一次会话踩了 5 次）**：`write_file`、`patch` 的 `new_string`、`execute_code` 里的长中文字符串，**常常只落前半段** —— 文件里留下半句 + `...)` / `...[truncated]` 字样（python 文件＝`SyntaxError`，markdown＝结构错乱）。可靠姿势：
  1. **先落小骨架再分段填**：用 `# @@NEXT@@` 哨兵占位 → 每段 **≤约 1.5KB** → 一次 `patch` 把哨兵换成「本段内容 + 哨兵」→ 每段看 `lint: ok`
  2. **哨兵必须停在最后一块之后**：否则每段都插到最前面 → 顺序倒挂（本次 DASHBOARD 出过"旧章节标题被顶掉、正文挂到新标题下"的错位）
  3. **DASHBOARD 插新章节优先用「行式插入」**（比 patch 长中文块安全）：`ls = open(p, encoding='utf-8').read().split('\n')` → `i = next(k for k,l in enumerate(ls) if l.startswith('### 10.7x '))` → `ls[i:i] = blk` → `open(p,'w',encoding='utf-8').write('\n'.join(ls))`
  4. **写后必核三件**：grep 新标题在不在 · 读回该段有没有半句/`[truncated]` 残留 · `git commit` 输出**不能是 `nothing to commit`**
  5. **python 字符串里别嵌双引号**（`"…没有\"演示\"这个计划…"` → `SyntaxError`）→ 中文引号一律用「」
- **DASHBOARD 的 §10.x 编号续号**：插入前先 `search_files(pattern='^### 10\\.', path=DASHBOARD)` 看当前最大号（本次跑到 §10.80）；一次会话可能连插十几条（10.67–10.80），每条保持「标题 + 3–6 条要点」的固定形态，别写成大段散文。
- **⚠️ 改账忘了落盘（2026-10-13 实测踩坑）**：用 `execute_code` 改 JSON 时只在内存里改 dict、然后 `print("已结项")` ＝ **等于没改**。必须 `json.dump(...)` 写回文件，**再从磁盘重读复核**（打印剩余条数/条目）后才向凡哥回话。本次曾口头报"日报时间已结项"，文件里其实还是"待办"，凡哥下一轮问起才发现 → 之后凡哥提到某条"怎么没销账"时，先怀疑这个。
- **凡哥问「你上次说过 X，还记得吗 / 再发我一份」**：**不要凭记忆复述**——先 `read_file` 读原档（方案/审核依据/台账），从文件里重新组织后再发；结构性方案同时落一份可转发文件到 `D:\Documents\我的文档\`，回话带绝对路径 + `MEDIA:`。
