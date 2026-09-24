# 炉子程序内技术细节（2026-09-24 从官方前端包提取）

> 取数方式：`https://app.luzi.top/app-assets/index-*.js`（约 3.5 MB，含全部 UI 文案 + API 定义 + 各 Agent 接入配置）。
> ⚠️ 这些是**技术事实**，用于确认能力边界与取数位置；**不能当作官方操作教程**（操作流程见 SKILL.md 第一纪律）。

---

## API 端点（baseURL = `/api/v1`）

| 方法 | 端点 | 用途 |
|---|---|---|
| POST | `/assets/` | 上传资产（body 含 `asset:{summary,tag_ids,title,title_zh,type}` + `skill_content:{entry_file:"SKILL.md", package_file_object_id}`）|
| PUT | `/assets/{id}` | 更新资产 |
| PATCH | `/assets/{id}/prompt-use` | 记录提示词使用 |
| GET | `/assets?type={prompt\|skill\|reference}&status=active&asset_id={id}` | 拉资产 |
| GET | `/onboarding` | 新手引导状态 |
| POST | `/onboarding/seeds/{id}` | 保存引导输入（超时 20s，`code:"TIMEOUT"` 表示官方样例取不到）|
| POST | `/onboarding/complete` | 完成引导（`409 STATE_CONFLICT` + `reason:"seed_unavailable"` = 样例不可用）|

资产类型：`skill` / `prompt` / `reference`。

---

## `deployment_targets` —— Agent Skill 部署定义

每个受支持的 Agent 都有一条，字段语义：

```jsonc
{
  "candidate_file": "SKILL.md",          // 入口文件（判定这是不是一个 Skill 包）
  "display_name": "Hermes 用户级 Skill",
  "id": "user-skills",
  "mode": "copy_directory",              // 部署方式：整目录复制
  "relative_path": "skills",             // 相对 root 的路径
  "root_id": "config",
  "scope": "user_agent",
  "supported_deployment_modes": ["copy", "link"]   // 复制 / 链接 两种都支持
}
```

**Hermes 的完整条目：**

```jsonc
{
  "id": "hermes",
  "name": "Hermes",
  "tagline": "Nous Research 的通用 Agent",
  "vendor": "Nous Research",
  "install_source": "https://hermes-agent.nousresearch.com/",
  "management_stage": "deployable",
  "overview_status_labels": ["可管理", "支持部署"],
  "primary_entry": "SOUL.md",
  "roots": [{ "id": "config", "kind": "home_relative", "path": ".hermes" }],
  "skill_entries": ["~/.hermes/skills"],
  "summary": "支持 Hermes 默认与命名 profile 的 SOUL、原生记忆和 Skill 快照；本机迁移可选择 profile，并按原生格式写入 MEMORY.md 或 USER.md。",
  "supported_capabilities": ["识别", "复制部署", "内容预览", "Agent 迁移"],
  "deployment_targets": [{
    "candidate_file": "SKILL.md",
    "display_name": "Hermes 用户级 Skill",
    "id": "user-skills",
    "mode": "copy_directory",
    "relative_path": "skills",
    "root_id": "config",
    "scope": "user_agent",
    "supported_deployment_modes": ["copy", "link"]
  }],
  "capabilities": {
    "import": "可导入此 Agent 中已支持的内容。",
    "memory": "支持迁出和迁入记忆；完整记忆管理暂不支持。",
    "sync": "暂不支持完整双向同步。",
    "handoff": "暂不支持从此 Agent 发现会话并发起接力。"
  },
  "entries": [
    { "id": "config.yaml", "kind": "config_file", "mode": "preview_only" },
    { "id": "cron",        "kind": "config_directory", "mode": "preview_only" }
  ]
}
```

**要点**：
- `roots` 是 `home_relative` + `.hermes` → **写死，不可配置**。这就是为什么本机 `HERMES_HOME=D:\Hermes` 时必须用 junction 把 `~/.hermes/skills` 接过去。
- `cron` 目录被识别为可管理项（但仅预览）。

---

## 支持的 Agent 清单（域名线索）

`code.claude.com`（Claude Code）· `chatgpt.com`（Codex/ChatGPT）· `cursor.com` · `antigravity.google` · `opencode.ai` · `docs.openclaw.ai`（**OpenClaw**）· `www.trae.cn` · `www.codebuddy.cn` · `www.workbuddy.cn` · `agent.minimaxi.com` · `www.kimi.com` · `www.doubao.com` · `qwenwork.cn` · `www.dumate.cn` · **`hermes-agent.nousresearch.com`**（Hermes）

## 官方套餐（Hermes 均在内）

| 套餐 | agentIds |
|---|---|
| 小白包 `beginner` | `doubao-work`, `codex`, `hermes` |
| 高手全套 `pro` | `claude-code`, `codex`, `opencode`, `hermes`, `openclaw` |

## 内置能力（capabilityIds）

`luzi-companion`（炉子伴侣：聊天中一句话调用能力）· `web-access` · `daily-brief` · `lark-cli`（**飞书 CLI**）· `doc-export` · `code-review` · `browser-mcp`（playwright-mcp）

---

## 一键"交给 AI 装"的提示词模板（程序内原文）

两种形态，按目标 Agent 是否在支持列表内不同：

```
请安装 Skill「{名称}」：
1. 按你这个 Agent 的 Skill 目录约定，问我装全局还是装本项目
   （如 Claude Code 全局 ~/.claude/skills/、项目 .claude/skills/）。
2. 从下方链接下载 zip（约 10 分钟内有效），解压到所选 skills 目录的 {名称}/ 文件夹：
   {链接}
3. 装好后读取 SKILL.md，按其中的介绍直接询问我如何使用。
```

```
请安装下面这个 Agent Skill，安装完成后在合适的任务里触发使用。

<Skill 包下载链接> {链接} </Skill 包下载链接>

<安装说明>
1. 下载上面的 zip（链接短期有效，失效时让我重新生成）
2. 解压到你的 skills 目录（例如 ~/.claude/skills/），保留文件夹结构
3. 读入口文件 SKILL.md，按其说明在后续任务中触发使用
</安装说明>
```

**要点**：zip 下载链接**短期有效（约 10 分钟）**——过期就让炉子重新生成，别存旧链接。

---

## 部署失败错误分类（程序内原文）

| 类别 | 原文 |
|---|---|
| `package` | 这个 Skill 包本身不符合规范，不是你的环境问题——换个目标或重试都不会有帮助。 |
| `environment` | 问题出在本机环境（磁盘空间、目录权限或路径被占）。检查一下目标目录和磁盘，然后重试。 |
| `target` | 目标位置放不下这个 Skill。**炉子不会覆盖已经在那儿的东西**，请先处理目标位置，或换一个部署目标。 |
| `TARGET_CONTAINS_REPARSE_POINT` | 目标 Skill 目录当前是一个链接（可能来自之前的链接模式部署）。请到「Agent 管理」打开对应 Agent，对这个 Skill 执行同步或接管；或删除该链接后再重新部署。 |
| `TARGET_CONTENT_MISMATCH` | 目标链接指向的位置不是这个 Skill（缺少 SKILL.md）。 |
| `file_corrupted` | 文件损坏，稍后重试一次；仍然失败说明这个包本身有问题，可以去问作者。 |

⚠️ **`TARGET_CONTAINS_REPARSE_POINT` 与本机 junction 的关系尚未实测**（见 SKILL.md）——第一次部署时以**实际报错**为准，不要预设它会通过、也不要预设它一定失败。

---

## 应用内其它机制（了解用）

- **新手引导**：`/onboarding` 路由，3 步；文案「先看当前家底，再选择适合你的装机方案」/「引导 1 / 3」；可「跳过引导」；有官方样例（取不到时可先下一步）。完成后可随时「**重看新手引导**」（入口在仪表盘）。
- **仪表盘**：显示各 Agent 状态（含 `inaccessible` 状态）。
- **论坛板块**：`求助 help / 讨论 discussion / 教程 tutorial / 长文 longform / 晒一晒 showcase / 围炉 lounge / 活动 activity`；每日发帖上限 5。
- **发帖自动归类**：标题含"求助/怎么/？"→求助；含"教程/心得/踩坑"→教程；含"跑通/做了/做成"→晒一晒。
- **炉况等级**（按 milestone）：`default 原色炉`（冷启动）→ `sprout 新芽炉`（onboarded）→ `beret 创作炉`（first_publication）→ `scholar 学者炉`（posts_5）→ `beat 律动炉`（moved_100）。
- **初代炉子天使**：状态 `candidate`；进度面板 `0/3 · 0/10`；可关闭引导条（`luzi.angel.candidate-guide.dismissed`）。
- **合规文本**：`/community/guidelines` 社区规范 / 隐私政策 / 服务条款（后台可草稿/生效中切换）。
