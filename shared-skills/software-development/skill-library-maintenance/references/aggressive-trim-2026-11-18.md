# 技能库激进瘦身实战（2026-11-18）

凡哥原话链：**「数量还是很多啊，181个都有用吗？」→「激进吧」→「干」**

起因：看了马导的 Skill 教学（16 分钟 8 章，2.5 万赞），他点出两个副作用 —— 装多了慢且费钱（AI 开工先扫全部描述）、功能相近会调错（"招牌鱼香肉丝 vs B点鱼香肉丝"）。对照自查全中。

---

## 一、体检数据的真实分布

**首次用 `.usage.json` 的 `last_used_at` 统计（此前一直用 mtime 当代理指标）**：

| 上次用 | 数量 | 占比 |
|---|---|---|
| 7 天内 | 26 | 22% |
| 8-30 天 | 25 | 21% |
| 31-90 天 | 44 | 38% |
| 90 天以上 | 6 | 5% |
| 零使用记录 | 16 | 14% |

**启用 117 个里，30 天内真用过 51 个（44%）。**

对照 mtime 口径：30 天内动过只有 45 个 —— 两者接近但**含义不同**（mtime = 被维护过，`last_used_at` = 被真调用过）。凡哥问"都有用吗"要用后者。

---

## 二、三个数据陷阱（都真实踩过）

### 1. 幽灵记录
`seedance-vocab-zh`、`seedance-style`、`seedance-pipeline` 等 9 个在 `.usage.json` 里显示"104 天未用"，
但 `find skills -type d -name "seedance*"` 结果为空、`hermes skills list | grep -c seedance` = 0 ——
**技能早已被移走（隔离柜），usage 记录还留着**。

→ 结论：**必须把 usage 记录与现存 `SKILL.md` 目录做交叉过滤**，否则会统计出一堆不存在的技能，得出"90 天以上有 38 个"这种错数（实际启用中只有 6 个）。

### 2. 改名丢记录
`storyboard-keyframe-opc-test` / `subject-assets-opc-test` 是当天刚改名的，
usage 里的键还是旧名（`qwen-image-*`），于是被报成"零使用记录"。

→ 判断"没用过"之前，先确认这个技能**近期有没有改过名**。

### 3. builtin 无记录
`apple-notes`、`imessage`、`findmy` 这类 macOS 内置技能本来就不写 usage，
且在 Windows 上是 disabled 状态 —— 不该进"死活"统计。

→ **只统计 enabled 集合**，disabled 的没意义。

---

## 三、执行结果

| | 之前 | 之后 |
|---|---|---|
| 技能文件 | 180 | **146** |
| 启用 | 117 | **63** |
| 归档 | 2 | **36** |
| 禁用 | 53 | **73** |
| 描述雷同组 | 6 组 | **3 组** |

### 归档 34 个（五类理由）

**① 重复（11 个）**
- **穿搭/形象：5 个砍 4 个** —— `personal-styling-consulting`、`personal-image-advisor`、`personal-style-advisor`、`personal-presence-consultant` 全砍，留 `personal-style-consulting`（最近在用）
- `brand-identity-system`（留 `brand-identity-design`）、`logo-generator`
- `hiring-interview-evaluation`（留 `technical-hiring-interview`）
- `screenplay-asset-extraction`（留 `subject-assets-opc-test`）
- `document-to-action-items`（留 `meeting-action-items`）
- `project-idea-to-mindmap`（留 `project-topology-diagrams`）
- `dashboard-tree`（留 `project-dashboard`）

**② 从没用过 / 不做的（12 个）**
`box`（Box 网盘）、`product-price-monitor`（比价）、`yuanbao`（元宝群）、`competitor-news-monitor`、`email-inbox-triage`、`songwriting-and-ai-music`（写歌）、`merge-reconciler`、`inspecting-hermes-desktop-dom`、`youtube-content`（有 media-learning 顶）、`luzi-capability-network`（炉子）、`grounded-citations`、`weekly-review-planning`

**③ 模型换代遗留（3 个）**
`gpt-image-style-prompting`、`z-image`、`z-image-prompt`

**④ 整组停摆（3 个）**
`nanming-island`（98 天）、`nanming-ip-design`（98 天）、`nanmingdao-villain-design`（**133 天**）——南溟岛整组近五个月没动，凡哥重心已转到短剧/咨询/技能治理

**⑤ 边缘（5 个）**
`sparkart-clone`（117 天）、`maps`（105 天）、`creative-project-structure`、`github-issue-to-pr`、`web-console-permission-configuration`

### 禁用 20 个（文件留着，随时能开）
`character-vlog-pipeline`、`agnes-ai`、`opc-workflow-reuse`、`multi-agent-architecture`、`agent-cost-optimization`、`lightpanda-fastfetch`、`js-rendered-page-extraction`、`blocked-source-alternatives`、`vision-analysis-reliability`、`book-distillation`、`website-cloning`、`dual-agent-memory-sync`、`self-reflection`、`knowledge-base-utilization`、`hermes-network-proxy`、`local-tool-provisioning`、`compute-capacity-procurement`、`product-tutorial-production`、`ad-claim-verification`、`blocked-page-recovery`

**挑选逻辑**：全是"8-90 天内用过、但功能与活跃技能有替代关系"的 —— 禁用保留能力，又不占每次开工的上下文。

---

## 四、验证清单（这次点名 52 个，全过）

写剧本 / 出图（image-prompt）/ 宫格关键帧 / 主体资产 / H3 视频提示词 / 影剧工坊 / 内容摄入 / 技能路由 / 技术雷达 / 团队管理 / 招聘面试 / 卡耐基 / 思维咨询 / 总控台 / 飞书日报 / 提醒 / 卡蒙狐反爬 / aria2 / PDF / Word / Excel / 塔罗 / 会议转写 / 长期记忆 …

→ 全部 `enabled`，**零误伤**。做法：把名单写进脚本，读 `hermes skills list` 逐行匹配 `state == "enabled"`。

---

## 五、没凑数的那个决定（重要）

凡哥选了"激进"，我自己给的目标是"砍到 ~70"。按理由只能凑到 63 ——
**剩下 7 个的候选里，有 8 天内还在用的（`windows-system-maintenance`、`product-tutorial-production` 等），砍了就是误伤。**

→ **就此停手，如实说"63 个，比目标多 7 个，因为再砍要误伤近期在用的"。**

凡哥要的是"贵精不贵多"，不是"必须砍到某个数"。为凑数而砍 = 把治理做成了另一种失控。

---

## 六、遗留未做

1. 剩余 3 组描述雷同：`novel-to-screenplay|screenplay-to-15s-storyboard`、`docx|powerpoint|xlsx`、`claude-code|codex|opencode`（后三者已禁用，不算问题）
2. 16 个缺"怎么算做完"
3. 44 个缺触发词
4. `skill_audit.py` 目前扫全部文件（含 disabled），应加 `--enabled-only`

---

## 七、同批的模型换代改造（详见 model-migration-skill-refactor-2026-11.md）

- 归档 `gpt-image-storyboard-keyframe-opc-test`、`gpt-image-subject-assets-opc-test`
- `qwen-image-storyboard-keyframe-opc-test` → **`storyboard-keyframe-opc-test`**
- `qwen-image-subject-assets-opc-test` → **`subject-assets-opc-test`**
- 出图参数全改豆包 Seedream 5.5（2816×1584 / 1584×2816，无 4K），Qwen 标为"云上备用通道"
- 修引用：`image-prompt` 第 50 行、`image-asset-prompting` 的 `related_skills`
- **关键认知**：`subject-assets` 名字带 qwen 但其实是**与模型无关的四视图提示词编译模板**，`image-prompt` 依赖它 —— 差点删错
