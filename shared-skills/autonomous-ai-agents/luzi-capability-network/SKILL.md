---
name: luzi-capability-network
description: 凡哥提"炉子"/luzi/能力网络/装Skill到Hermes时加载。
version: 1.0.0
author: 小南
license: MIT
metadata:
  hermes:
    tags:
      - luzi
      - 炉子
      - agent-skill
      - 能力网络
      - hermes-integration
    related_skills:
      - hermes-agent
      - dual-agent-memory-sync
      - skill-library-maintenance
---

# 炉子（luzi.top）— Agent Skill 能力网络

## When to Use

凡哥出现以下任一情形时加载本技能：

- 提「**炉子**」「luzi」「能力网络」「能力广场」「我的炉子」
- 要把炉子里的**能力装进 Hermes** / 问「炉子怎么用」「怎么接入」
- 问炉子**装在哪、认哪个目录、技能库通不通**
- 要**从炉子发布技能出去**，或讨论「哪些技能能外发」
- 排查炉子的部署报错（reparse point / 目标目录 / 包不合规）

> 相关但**不**属于本技能：ComfyUI 版本与插件部署 → `comfyui-env-ops`；Hermes 自身配置 → `hermes-agent`。

## 它是什么

**秋芝2046 团队**做的**桌面端 Agent Skill 分发平台**（Windows / macOS）。官网 `luzi.top`（`luzi.ai` 301 跳转过去），Web 版 `app.luzi.top`，**内测需邀请码**。

- 它**自己不跑 AI**：价值 = 从社区发现别人**真实跑通**的能力 →「带走」进自己的炉子 →「交给熟悉的 AI 运行」
- 能力包 = **zip + 入口文件 `SKILL.md`** —— 与 Hermes 技能格式**同源**，双向可搬
- 资产分三类：`skill` / `prompt`（提示词）/ `reference`（参考内容）
- **Hermes 是官方一等公民**：接入定义写死在程序里（`id: "hermes"`，vendor: Nous Research）

---

## ★ 第一纪律：官方教程去哪找

> **凡哥 2026-09-24 原话：「去官网查炉子的使用教程，不要瞎猜」**

**官方教程位置（按权威度排序）：**

| # | 位置 | 内容 |
|---|---|---|
| 1 | **应用内「仪表盘」→「重看新手引导」** | ⭐ **3 步引导，详细教程在这**。会**扫描本机已有的 AI 工具**，可领「官方样例」试跑 |
| 2 | 官网 `luzi.top` 首页「使用流程」区块 | 三步：**发现 → 带走 → 运行** |
| 3 | 社区「教程」板块 | 别人的实战方法（论坛分：求助/讨论/教程/长文/晒一晒/围炉/活动）|
| 4 | 官方视频 | B站 `BV1DLYC6oEKT`（秋芝2046，21分钟）/ YouTube `Tm0w67MZMj4` |

**官网没有 docs 子站**（`/docs` `/help` `/guide` 全是 403，属 SPA 路由）——官网的教程**就是首页那个三步流程**，没有更细的。

### ⚠️ 反面教材（本纪律的由来）

本次我读了它的前端 JS 包 + 程序里的错误码文案，自己拼出一套「**先接 Agent → 再逛广场 → 再部署**」的操作步骤交给凡哥，被当场要求重去官网查。

**边界必须分清：**

- ✅ JS 包 / 程序资源**能**确认**技术事实**（API 端点、路径定义、数据结构、错误码语义）——查这些没问题
- ❌ **不能**代替官方教程回答「**用户该怎么点**」——操作顺序只能以官方引导为准
- ❌ **不要因为官网「没有文档页」就拿自己的推断填空**。正确做法：如实说「官网只有三步流程，详细教程在应用内的新手引导」，指路给他，而不是自己编一套

---

## 官方流程（三步）

1. **发现** — 能力广场浏览能力详情与真实反馈，选出值得用的能力
2. **带走** — 将完整能力包保存进自己的炉子
3. **运行** — **交给熟悉的 AI 运行**：读取能力包 → 熟悉环境 → 生成结果

**能力档案四要素**：社区来源（作者/版本/原始链接）· 使用方法（提示/规则/工作流）· 运行环境（模型/工具/本地依赖）· 真实反馈（测评/结果/适用边界）。

> 注意：**「接入 Agent」不在官网的三步里**，它是「运行」环节的支撑动作，不是起点。别把它讲成第一步。

---

## Hermes 对接的技术事实（已核实）

来源：程序内接入定义 + 本机实测。

| 项 | 值 |
|---|---|
| Agent id / 名 | `hermes` / "Hermes"（tagline: Nous Research 的通用 Agent）|
| primary_entry | `SOUL.md` |
| roots | `~/.hermes`（`home_relative`，**写死**）|
| skill_entries | `~/.hermes/skills` ← **技能往这装** |
| 支持能力 | 识别 / 复制部署 / 内容预览 / **Agent 迁移** |
| 部署模式 | `copy`（复制）或 `link`（链接），两种都支持 |
| 记忆 | 按原生格式读写 `MEMORY.md` / `USER.md`，支持迁出迁入 |

### ⚠️ 本机路径不匹配 + 解法（2026-09-24 已建并实证）

凡哥的 `HERMES_HOME=D:\Hermes`，技能在 **`D:\Hermes\skills`**（178 个 `SKILL.md` / 33 个分类）；
而炉子认的 `C:\Users\bobby\.hermes` 里**只有桌面版附件缓存**（`desktop-attachments`），**没有 skills** → 不处理的话装的能力会落进一个 Hermes 读不到的地方。

**解法：目录联接（junction）**

```bash
cmd /c mklink /J "C:\Users\bobby\.hermes\skills" "D:\Hermes\skills"
```

junction 免管理员、可秒回滚（删联接不动真数据）。**建完四条验证缺一不可**：

1. `cmd /c dir /AL "C:\Users\bobby\.hermes"` → 看到 `<JUNCTION> skills [D:\Hermes\skills]`
2. 从联接点列目录 → 33 个分类
3. **`find -L`** 数 SKILL.md → 178（⚠️ **不加 `-L` 会数出 0**——junction 被当链接不递归，这不是失败）
4. **反向写测试**：从联接点写一个文件 → 确认它真的出现在 `D:\Hermes\skills`（这条才证明"装进去=收到"）

### 🔴 未验证风险：`TARGET_CONTAINS_REPARSE_POINT`

炉子官方错误文案原文：

> 「目标 Skill 目录当前是一个链接（可能来自之前的链接模式部署）。请到「**Agent 管理**」打开对应 Agent，对这个 Skill 执行**同步或接管**；或删除该链接后再重新部署。」

- 我的 junction 在 `skills` **这一层**；警告说的是**"目标 Skill 目录"**（`skills/<技能名>/`）→ 具体技能目录是普通文件夹，**可能不触发**
- **它到底检查哪一层，没有实测** → **第一次真实部署时必须看结果**：报 reparse / 链接错 → **立刻撤 junction**，改走官方「Agent 管理 → 同步/接管」
- ⚠️ **递归风险**：junction 是真通道 —— **在炉子里删技能 = 真删 `D:\Hermes\skills`**。要删之前先跑 `python D:\Hermes\scripts\sync_skills.py push` 兜底

---

## 本机落地事实

| 项 | 值 |
|---|---|
| 安装位置 | `D:\Program Files\Luzi`（v0.1.13，Tauri + Edge WebView2，`luzi-desktop.exe` 62MB）|
| 登录态/设备 | `~/.luzi/desktop/auth-session.json`（refresh_token）、`device.json` |
| WebView 数据 | `%LOCALAPPDATA%\com.luzi.desktop\`（EBWebView）|
| 界面左栏 | 能力网络 / 广场 / 讨论 / 测评 / 关注 / 我的 / 个人主页 / Skill / 参考 / 随手记 / 发布管理 / **Agent**；左下 `内测 v0.1.13` + 火力值 |

---

## 发布边界（先只做「导入」方向）

凡哥 178 个技能里两类性质完全不同：

| ✅ 可流通（=行业话语权） | 🚫 **绝不外发** |
|---|---|
| 提示词框架、镜头语言、ComfyUI 运维、Seedance/LTX 技巧、OPC 流程 | **南溟岛 IP**（世界观/角色/剧本）、齐白兰·顾蓝汐项目、客户项目、团队考核数据 |

- ⚠️ 凡哥已建了一条「自我介绍」提示词，内含**真名 + 公司 + 职位** —— 它现在只是本地资产，但**一旦点「发布」就等于对外公开这些信息**。提醒他改成通用写法，或干脆不发布。
- **装能力「挑精不挑多」**：技能装太多会稀释 `skill-router` 的路由精度。先只做导入方向，发布方向等凡哥定完边界。

---

## 社区机制（附带了解）

- 论坛板块：求助 / 讨论 / 教程 / 长文 / 晒一晒 / 围炉 / 活动（**每天最多发 5 帖**）；标签含 Vibe Coding / Agent 玩法 / 视频 / 编程 / 办公 / 写作 / 设计
- 炉况等级（头像）：原色炉（默认）→ 新芽炉（完成新手引导）→ 创作炉（首次发布）→ 学者炉（发5篇）→ 律动炉
- 「**初代炉子天使**」共建计划：发布内容 + 参与互动，点亮专属标识

## 部署失败错误分类（官方文案，排障用）

- `package` — 这个 Skill 包**本身不符规范**，不是你的环境问题
- `environment` — 本机环境（磁盘空间 / 目录权限 / 路径被占）
- `target` — 目标位置放不下 → **炉子不会覆盖已经在那儿的东西**，先处理目标位置
- `TARGET_CONTENT_MISMATCH` — 目标链接指向的位置不是这个 Skill（缺 SKILL.md）

---

程序内的 API 端点、`deployment_targets` 完整结构、各 Agent 能力矩阵、内置能力清单与取数方式：`references/luzi-internals.md`
