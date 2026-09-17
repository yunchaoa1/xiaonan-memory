---
name: dashboard-tree
description: Interactive HTML project dashboard tree — visual status tracking, clickable file links, git-synced between two agents.（中文触发：制作/更新交互式HTML总控台树（DATA对象、状态、链接）时加载）
platforms: [windows]
---

# Dashboard Tree · 工作总控树

A single-file HTML tree for tracking complex projects. Designed for a dual-agent setup (company + home) sharing state via git.

## When to use

- Tracking a multi-module creative/engineering project with 30+ nodes
- Two agents need shared visibility of project status
- The user wants a clickable visual overview they can open in a browser

## Architecture（当前权威路径）

同步仓库中的两份总控台是共享真相源：

| 文件 | 路径 | 作用 |
|------|------|------|
| Markdown | `D:\Hermes\xiaonan-memory\DASHBOARD.md` | 项目状态、规则与技术摘要 |
| 树形UI | `D:\Hermes\xiaonan-memory\dashboard-tree.html` | 可点击的分支视图，`const DATA` 为树数据 |

旧路径 `D:\SDkechengz\dashboard-tree.html` 可能不存在或已废弃。不得把它当默认工作副本；先验证，除非凡哥明确要求，否则直接维护Git同步仓库中的版本。

## How to update

1. 用户确认项目决策后，立即更新 `DASHBOARD.md` 和树形HTML中对应节点。
2. 修改HTML中的 `const DATA`，保持 `done | progress | blocked | pending` 状态合法。
3. 用JavaScript语法检查验证脚本，例如抽取 `<script>` 后运行 `node --check`。
4. 修改只停留在本地工作树；除非凡哥明确要求或到既定同步时间，不因每次编辑自动提交或推送Git。
5. 新生产线采用“类别→题材→具体项目→资产/状态”的层级，不把独立参演剧塞进角色本传节点。

### 参演剧本分类示例

```text
57角色参演剧本
└─ 现代都市剧
   └─ 豪门寻亲·家庭情感·爱情爽剧
      ├─ 主演阵容
      ├─ 故事范围
      ├─ 年龄与时间线
      ├─ 寻亲证据链
      └─ 整季体量
```

**Principle:** confirmed decisions update immediately; Git push follows the user’s sync policy, not every edit.

## Tree data structure

Embedded in a `const DATA` object inside the HTML. Each node:

```javascript
{
  label: "节点名",
  icon: "🎯",
  status: "done",       // done | progress | blocked | pending
  count: "57/57",       // optional
  info: "补充说明",      // optional, grey small text
  file: "world/六界.md", // optional, clickable link (relative to git repo root)
  children: [...]       // sub-nodes
}
```

## Content file structure

Split content into small, topic-specific files. No monolithic documents. Structure:

```
repo/
├── dashboard-tree.html
├── world/       ← 世界观, one file per concept
├── tech/        ← 技术管线
├── heart-demons/ ← 心魔 (one file per volume)
├── characters/   ← 角色 (one file per character)
└── personal/     ← 个人发展
```

Each file should be small enough to open instantly when clicked from the tree.

## 安全更新纪律（2026-09-15 凡哥：「可以把这些做进我们的总控台，**切记不要把我们的总控台搞乱了**」）

凡哥允许把新内容（如集团项目拓扑）并进总控台，但**明确要求不能把树搞乱**。硬约束：

1. **只改 `const DATA`，渲染逻辑一个字不动**（`buildTree` / `STATUS` / 样式 / `countNodes` 都不碰）。
2. **新增＝在 `children` 里插一个分支，绝不重排、不改标签、不动任何既有节点**。当前头号工作插在 `children[0]`（最上面，一眼可见），插完**主动告诉凡哥"我加在哪、原有节点一字未动"，并问要不要挪位置**。
3. **两道校验，缺一不可**（本次实测流程）：
   - 语法：抽出 `<script>` 跑 `node --check`（exit 0 才算过）。
   - 结构：写个约 10 行的 `probe.js`——读 HTML → 截取 `const DATA =` 到 `const STATUS` 之间 → `eval('('+seg+')')` → 打印**顶层 label 列表**与**递归节点总数**。比对：顶层分支数 +1、既有顶层标签全在、节点总数 = 原数 + 新增数。
4. **改动范围报清楚**：本次只改了 ① `const DATA` 里新增分支 ② 文件底部 `lastUpdate` 那行文字（日期＋一句新增说明）。凡一处改动都算"改了总控台"，交付时要逐条列出。
5. 文字口径跟着走：分支标题里的称呼按 `team-management-ops` §称呼与低调口径写「**项目主管**」（不要写 CTO）；新增叶子若指向文件，`file:` 路径相对 repo 根，且**该文件必须真的已建好**（否则点开是空链）。
6. Git 同步按既定策略（白天本地、下班同步）；但**凡哥明确说"做进总控台"时，等同授权写入并在当次同步**。
7. **一个结构变化要"四处同改"**（本次实例：`制剧工作流` 现在内置于 OPC 平台、**测试完成后单独建站**）：① 树 `const DATA`（旧节点加 `info` 说明 ＋ 新增一个 `pending` 待办节点）② 仓库内的清单 md（`集团/项目拓扑与模块清单.md`）③ `DASHBOARD.md` 对应章节 ④ **给外部 AI（豆包）的稿子**。只改一处 → 两边口径立刻分叉，之后每个下游产出都会错。

## Pitfalls

- **Don't push after every edit.** The user corrected this: tree lives locally during the day, only syncs at end-of-day.
- **Don't let files grow large.** If a tree leaf opens a 4000-line file, split it. The user explicitly complained about this.
- **Don't delay tree updates.** The user said: "树的更新是实事的，当我们确认了一些事情的时候，就要及时更新"

## TTS voice fix (Hermes-specific)

If朗读 (read-aloud) speaks English despite Chinese text, the TTS voice config path is `tts.edge.voice`, NOT `tts.voice`:

```
hermes config set tts.edge.voice zh-CN-XiaoxiaoNeural
```

Wrong paths that won't work: `tts.voice`, `voice.voice`, `voice.language`.
Restart Hermes after changing.
