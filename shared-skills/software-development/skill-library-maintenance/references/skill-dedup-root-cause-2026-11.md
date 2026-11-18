# 技能重复的根因取证与「禁止自动建技能」铁律（2026-11-18）

## 1. 凡哥的诊断（比我准）

> 「总是出现重复的 skill，那就是证明我们在需要加载 skill 时，相对应的 skill 没有被调用，导致形成了新的 skill 对吧？」

我先按他说的\"路由没调起来\"去理解，然后用 `.usage.json` 的 `created_at` 验证 —— **结果比他说的更严重，而且不是路由层的问题**。

## 2. 取证方法（可复用）

`.usage.json`（`D:\Hermes\skills\.usage.json`）每个技能条目除 `last_used_at` 外，还有：

- `created_at` —— 创建时间（判断\"什么时候建的\"）
- `created_by` —— `agent` / `None`（判断\"谁建的\"）
- `last_patched_at`、`last_reused_patch_generation`

**做法**：把疑似重复组按 `created_at` 排序，算\"最早到最晚相隔多少天\"，并打印 `created_by`。键名要归一化：`k.split(":")[-1]`（有些键带 `creative:` 前缀）。

## 3. 实测结果

| 重复组 | 创建时间 | 判断 |
|---|---|---|
| 面试 2 个（`technical-hiring-interview` / `hiring-interview-evaluation`） | 同一天 06:06 → 06:17 | **相隔 11 分钟** |
| 品牌/LOGO 3 个（`logo-generator` / `brand-identity-system` / `brand-identity-design`） | 同一天 08:43 → 09:15 → 10:02 | **1 小时 19 分内建 3 个** |
| 穿搭 5 个（`personal-image-advisor` / `personal-style-consulting` / `personal-style-advisor` / `personal-styling-consulting` / `personal-presence-consultant`） | 同一天 08:46 → 12:30 → 12:46 → 13:37，第 5 个在 21 天后 | **4 小时内建 3 个** |
| 总控台 2 个（`project-dashboard` / `dashboard-tree`） | 同一天 06:39 → 13:54 | 相隔 7 小时 |
| 画图 2 个（`project-topology-diagrams` / `project-idea-to-mindmap`） | 相隔 21 天 | **这一类才是\"跨会话没找到\"** |
| 提资产 2→3 个（`screenplay-asset-extraction*` / `subject-assets*`） | 08-30 → 08-31 → 10-08 | 相隔 **38 天** |

**所有条目的 `created_by` 都是 `agent`** —— 全部是我自发建的，不是凡哥要求。

## 4. 结论：病根有两层，我之前只说了一层

| 层 | 病 | 证据 |
|---|---|---|
| **底层（更严重）** | **建之前不查重** —— 想到就建，没人拦 | 11 分钟建 2 个面试技能、4 小时建 3 个穿搭技能 |
| **上层** | **路由/触发词不准** —— 跨会话时该加载的没被加载 | 21 天、38 天两例 |

**只修上层没用**：就算路由 100% 准，底层\"想到就建\"仍会长出新的重复。

## 5. 被否掉的方案（重要，别重犯）

我提的方案：**建技能前跑一个查重脚本**（比对 description 前 14 字、关键词撞车）。

凡哥当场否掉：「**你要确定，你这个办法真的有用**」。

**他是对的：**
- 脚本只是**提醒**，不是关卡。重复产生时的真实心理是\"这次不一样\" —— 我不会去跑，跑了也会找理由绕过。
- \"靠自觉守的规矩，我守不住。\"

**通用教训（可迁移到所有同类问题）：**
> 把\"靠自觉守的规矩\"换成\"结构上做不到的事\" —— 收回权限、要求必填证据、提高动作成本。**别拿提醒当关卡。**

## 6. 最终规则（凡哥定的）

> 「从根上去把这个问题解决，**不要自动产生 skill**，当我遇到什么事的时候，我会养成习惯**问你一嘴有没有相关的 skill**。」

### 流程

```
凡哥说一件事
   ↓
他问（或我主动提一句）：有没有相关的 skill？
   ↓
python D:\Hermes\scripts\find_skill.py <关键词>
   ↓
有 → 直接用/改现成的，告诉他"叫什么、管什么"
没有 → 说"没有现成的"+ 最接近的两个是什么
   ↓
他觉得该建 → 我先说"为什么不能并进那个最接近的" → 他点头才建
```

### 落地三处

1. **MEMORY**（每轮注入）：`不自动建skill;凡哥问'有无相关skill'→先检索再答;确无且点头才建,并说清为何不能并进旧的。`
2. **SOUL.md「Boundaries」**：技能创建铁律 + 病因实证（4 小时 3 个穿搭 / 11 分钟 2 个面试）
3. **DASHBOARD 10.14**：完整记录

## 7. find_skill.py 设计要点

路径：`D:\Hermes\scripts\find_skill.py`（全局脚本，不在技能目录里）

- 扫三个地方：`skills/`（活）、`skills-archive/`（归档），并读 `config.yaml` 的 `skills.disabled` 判禁用状态。
- 打分：命中 `name` +10、`description` +6、正文前 3000 字 +2。
- **输出必带 `[启用]` / `[禁用]` / `[已归档]` 标记** —— 这是设计核心：把历史重复版本摆在眼前，\"这次不一样\"就说不出口了。
- 没命中时明确打印：\"没有找到相关的 skill\" + 提示\"现在可以说没有现成的，要不要建？\" + \"建之前要能说清为什么不能并进现有的\"。
- 兼容 YAML 块标量（`description: |` / `>`）—— 直接取首行会得到 1 个字符。

### 反向测试（拿上面那些重复案例验）

| 查询 | 结果 |
|---|---|
| `穿搭` | 首位 `personal-style-consulting`（启用）✓，另列 4 个已归档历史版本 |
| `面试` | 首位 `technical-hiring-interview`（启用）✓ |
| `出图` | 前三位 `image-prompt` / `storyboard-keyframe-opc-test` / `subject-assets-opc-test` ✓ |

有弱相关噪声（正文匹配导致 `project-dashboard` 出现在\"出图\"结果里），但主技能排序稳定在最前，可接受。

## 8. 诚实边界

**这套机制今天才立，还没经过真正的考验。** 它有没有用，要等下一次我真想建技能的时候才算验证。

汇报时必须说\"还没验证\"，**不要声称已经有效**。如果又犯了，凡哥会说\"查了没\"三个字。
