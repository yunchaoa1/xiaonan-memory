---
name: skill-library-maintenance
description: 技能库维护与治理操作——停用/归档/合并重复技能、批量补中文触发描述、修复悬空引用、管理 curator 自动归档冲突、构建技能总调度。凡哥说"清理技能""技能太多了""停用XX技能""技能重复""优化技能触发"或需要治理/维护技能库时加载。
---

# 技能库维护 · Skill Library Maintenance

技能库治理的操作篇（评估方法论见 `D:\Hermes\skills_archive\skill-library-governance`，已归档仅作参考）。

## 核心事实（2026-08-06 实测）

### Hermes 技能机制
- **无关键词规则引擎**：技能 name+description 进系统提示，模型语义判断后 skill_view 加载。自动激活是概率性的，不是 100%。
- 中文描述对中文触发至关重要；英文描述 + 高度相似的描述族（如 26 个 seedance 子技能）会互相抢触发。
- 确定性方式：`/skill 名称`、`hermes -s 名称` 预加载。
- 技能索引每会话占 token：120 技能 ≈ 16,346 字符 ≈ 4K tokens；瘦身到 60 技能减半。

### curator（技能管家）自动归档冲突
- 默认 **ENABLED**，每 7 天跑一次；**30 天未用 → stale；90 天未用 → 自动归档**（从列表消失）。
- 判定依据是 .usage.json 使用频率，**不看业务价值**——低频但有用的技能（撩妹聊天、月更工具）会被误归档。
- consolidate（LLM 合并重叠技能为伞形）默认 off，需 opt-in；开启会合并高度相似的技能族（如 Seedance 22 件套）。
- curator 只归档不删除，自动备份可 `hermes curator restore` 恢复。
- **防重复查证**：curator 全部 12 个命令（status/run/pause/resume/pin/unpin/restore/list-archived/archive/prune/backup/rollback）**没有任何创建功能**；`skill_manage` 创建同名技能会被源码拒绝（`A skill named 'X' already exists`）；Hermes 加载同名去重、本地优先。唯一防不住的是"名字不同内容相似"（world-building/worldbuilding）——靠人工查。

### curator 调参（凡哥 2026-08-06 拍板"不限时"模式，已执行）
- config.yaml **没有的段 = 用代码默认值**；调整只需在文件末尾**追加覆盖段**，不用写全量配置。
- 配置键（源码默认值）：`enabled: True`、`interval_hours: 168`、`min_idle_hours: 2`、`stale_after_days: 30`、`archive_after_days: 90`、`consolidate: False`、`prune_builtins: True`（内置技能也会归档！）、`backup.enabled: True, keep: 5`。
- 已执行的"不限时"追加段：
```yaml
curator:
  enabled: true
  stale_after_days: 36500
  archive_after_days: 36500
  consolidate: false
  prune_builtins: false
```
- 36500 ≈ 100年 = 技能永不因时间被归档；`prune_builtins: false` 保内置技能；consolidate **永远保持关闭**（辅助模型不懂凡哥业务，可能合并 Seedance 22件套并改写实测规则）。
- 验证：`hermes curator status` 应显示 `stale after: 36500d` / `archive after: 36500d` / `consolidate: off`。

### Self-improvement review（后台自动生成技能 · 2026-08-06 破案）
- **机制**：`agent/background_review.py` 后台运行，实时读会话 → 自动创建技能（含 references/、scripts/ 固化）→ 自动 patch 现有技能（把会话教训写进相关技能）。
- **日志特征**：`desktop.log` 出现 `💾 Self-improvement review: Skill 'X' created. / Patched SKILL.md in skill 'Y'`；`agent.log`/`errors.log` 里能看到它调 skill_manage 的记录。
- **它是省事的好机制**：自动沉淀的技能质量高（会固化脚本、写执行记录 reference），不用白不用——但会与人工创建**打架**（本次 3 个治理技能并存即它+人工同时生成）。
- **防打架铁律**：创建技能**必须用 `skill_manage(action='create')`**（有 `A skill named 'X' already exists` 重名保护）；**绝不要用 `write_file` 直接写技能目录**——write_file 无重名保护，会绕过系统检查造成重复（本次教训：根级 maintenance 就是这么写出来的）。
- **发现重复后的处置**：对比各版本 SKILL.md → 互补内容合并进一个 → 其余 `mv` 到 `skills_archive/` 保留备份 → 验证 `hermes skills list` 只剩一个。
- 详细证据见 `references/background-review-mechanism.md`。

### 受保护技能的更新边界

- `skill_manage` 拒绝写入 user-owned、bundled、hub-installed、external-dir 或 pinned 技能时，不要通过 `write_file`、复制到新目录或改名来绕过保护。
- 先把新经验留在当前会话，向用户说明目标技能受保护；如确实要纳入自动治理，建议用户在前台执行 `hermes curator adopt <name>`，再由用户明确触发后更新。
- 如果经验属于可迁移的上层类别，优先寻找一个 curator-managed 的 class-level umbrella；确认没有合适的伞形技能后，才考虑创建新的 class-level 技能，禁止创建“一次会话一个修复技能”。
- “已加载”不等于“可写入”；加载技能、用户手写技能和用户要求前台创建的技能都默认保留所有权边界。
- 入口：`D:\Hermes\config.yaml` 的 `skills.disabled` 列表。
- ⚠️ **patch 工具拒绝修改 Hermes 配置文件**（security 保护）——必须用 python 脚本读写，或 `hermes config` 命令。
- 停用 builtin 技能只是不显示，文件还在，随时可恢复（从 disabled 移除即可）。

### 2. 归档技能（彻底移出扫描）
- 移到 skills 目录外：`mkdir -p D:\Hermes\skills_archive && mv skills/<类>/<名> skills_archive/<名>`。
- 移出后不再被发现；如需恢复，移回原路径即可。

### 3. 合并重复技能
- 先对比两个 SKILL.md：互补则合并成完整版（如 world-building 英文工作流并入 worldbuilding 中文设计原则，保留业务核心方），被吸收方移出目录。
- 同名冲突技能（world-building vs worldbuilding）优先保留中文、业务核心的一方。

### 4. 修复悬空引用
- 官方包扁平化安装的常见问题：SKILL.md 在但 references/ 缺失（seedance 系列是 Emily2040/seedance-2.0 官方包，只拷了 SKILL.md）。
- **正文自足原则**：正文有完整表格/规则时，把 `[ref:xxx]` 替换为"以正文为准"提示，不补不存在的文件。
- 批量替换脚本：解析 frontmatter 拿技能名 → 排除 disabled 列表 → 正则替换缺失 `[ref:xxx]` → 只保留指向真实存在文件的引用。
- 顺带修复：脚本/命令引用缺失时换成真实可用的替代（如 `python scripts/extract_last_frame.py` → `ffmpeg -sseof -0.5 -i <file> -frames:v 1 out.png`）。

### 5. 批量补中文触发描述
- 三种 YAML 格式都要处理：
  - 裸文本 `description: text` → 行尾追加 `（中文触发：XXX）`（全角括号+全角冒号，YAML 安全）
  - 双引号 `description: "text"` → 引号内追加
  - ⚠️ **块标量 `description: |` → 中文放块内容首行，绝不能拼在 `|` 后面**（会 YAML 损坏，computer-use 踩过）
- 写每个技能的中文触发说明要准确（"凡哥说XX时加载我"），不瞎编。

### 6. 验证
- `hermes skills list` 确认 enabled/disabled 数量对账（总数不变）。
- 脚本重新 `yaml.safe_load` 全部 SKILL.md，确认无损坏；统计中文描述覆盖 100%。
- `skill_view` 抽查核心技能加载正常。

## 周体检检查项（凡哥要求长期保持高效精简）

每周检查一次（或凡哥说"检查下技能库"时手动执行）：
0. **一键体检**：运行 `python D:\Hermes\skills\software-development\skill-library-maintenance\scripts\health_check.py --verbose`（自动检查 YAML/悬空引用/重复对/curator参数，退出码1=有异常）
1. 技能总数/启用数 vs 上次记录——看有无新增
2. 新增技能是否与现有技能语义重复（两两比对 description+正文，相似度 >0.6 预警）
3. 坏引用：`[ref:xxx]` / references/ / scripts/ 是否悬空
4. YAML 完整性：全部 SKILL.md frontmatter 可解析；**同时查正文脏数据** —— 有没有"字面 `\n` 转义块"（假 frontmatter 被当字符串塞进正文里）。脚本已内置该项（第 2.5 检查）。案例：2026-09-17 `barnum-effect` 的 SKILL.md 正文首行是一整段字面 `\nname:...\nversion:...`，YAML 检查只看第一个 block 所以漏掉 —— 现在会报"正文脏数据"。这类脏块会污染技能索引和加载内容，发现即清理
5. curator 状态：consolidate 还关着、stale/archive 线还是 36500、参数没被改
6. 结果处理：正常静默不打扰；异常给凡哥**大白话**报告（新增了啥、哪个和哪个重复、要不要处理），凡哥说"处理"才动手

## 技能总调度模式（skill-router）
模糊需求精准调取的解法：主入口技能（description 覆盖全部创作触发词）→ 路由表把"凡哥说 X"映射到"加载 Y+Z+W"→ 跨维度任务逐项加载不遗漏 → 输出前自查清单（维度打勾+双线规则+格式检查）。路由表引用技能若停用，用最近似替代并说明。

## 安装外部技能（GitHub 来源）

凡哥说「帮我找个 XX 技能装上」「要公认好评最多的，不要随便找一个瞎试」→ 走这五步，全程留痕。

### 1. 挑：拿证据，不凭感觉
- 先用 GitHub API 核**真实**数据，列候选对比表再决定：
  `curl -s https://api.github.com/repos/<owner>/<repo>` → `stargazers_count / forks_count / pushed_at / created_at`
- 加分项：**专用**（不是大杂烩仓库的副产品）、**近 3 个月有推送**、作者可信、中文友好（凡哥是中文用户）。
- 交叉验证独立目录的安装量（skills.sh / Skillselion / Awesome Skills 搜索页）。星数与安装量不一致时**如实说明**，别只挑好看的数字。
- ⚠️ 必须向凡哥指出的两点：**单提交仓库突然几千星**（可能是作者名气/刷榜，要标注）；**仓库无 LICENSE**（自用无碍，二次分发要留意）。

### 2. 取：GitHub 文件获取优先级
1. `api.github.com/repos/<owner>/<repo>/contents/<path>` → JSON 的 `content` 字段 base64 解码落盘（**最稳**，单文件可取、无需 clone；列全树用 `git/trees/<branch>?recursive=1`）
2. `raw.githubusercontent.com/<owner>/<repo>/<branch>/<path>`（直取原文）
3. `git clone --depth 1 --filter=blob:none`（整仓，最慢）
某些网络环境下 2/3 失败时 1 通常仍可用 —— 遇到就用 1 写个小脚本递归拉全，**不要因此放弃或改用别的技能**。
⚠️ 未认证 API 有速率限制：**连续拉十几个文件会 `HTTP 403 rate limit exceeded`**（本次装 logo 技能时踩到，12 个文件拉到第 9 个开始 403）→ 每个文件之间 `time.sleep(6)`，或分批取；已取到的先落盘，失败的重试下一批，别整批重来。

### 3. 装：落到技能库
- 目录：`D:\Hermes\skills\<类别>\<name>\`（按领域归类，别都丢根级）
- **frontmatter 的 description 必须补中文触发**（"凡哥说 XX 时加载"），否则中文语境下不触发
- SKILL.md 尾部追加 **「本机环境适配」** 章节：原版假设 → 本机执行方式（python 命令名、缺的依赖、可替代的服务、输出路径规范、实测过的坑）
- 装完跑 `python D:\Hermes\skills\software-development\skill-library-maintenance\scripts\health_check.py` 确认 YAML 完好 / 无悬空引用 / 无重复

### 4. 记：总控台留痕
- `DASHBOARD.md` 技能索引表加一行（类别 / 技能名 / 触发词），并在技能体系段落写清**出处 + 星数 + 本机适配要点**

### 5. 权限提醒（重要）
外部技能装进来默认是**用户所有（`created_by=None`）**，后台 curator **不能**自动 patch 它（真实报错：`Refusing background curator write_file for skill 'X': the skill is not curator-managed`）。
→ 首次实战的坑要么在前台会话里当场回流，要么**明确建议凡哥跑 `hermes curator adopt <name>`** 纳入自动治理，别指望后台自己搞定。

## Pitfalls

0. **Self-improvement review 自动创建技能**：Hermes 的 `agent/background_review.py` 会在会话结束后自动从对话中提取经验、生成技能并 patch 现有技能。产生的新技能可能与人工创建的重复（名称不同但内容高度相似）。去重时先查 `desktop.log` 中 `💾 Self-improvement review:` 行确认来源，再把 review 生成的技能合并归档，不要直接删除。
1. **YAML 块标量损坏**是补描述最常见的坑——拼在 `|` 后即坏，必须放块内容首行。
2. **patch 改配置文件/HTML**会被拒或误报——用 python 脚本。
3. **停用 ≠ 删除**；移出目录才是真归档。
4. **curator 归档不看业务价值**——核心技能必须 pin 或调大参数，否则 90 天自动消失。
5. **面向凡哥汇报用大白话**：留什么、清什么、修好什么、保证什么、影响什么；专业术语（相似度/分级）只当内部底稿。
6. 治理后注意系统提示"困难任务后提议保存技能"机制会鼓励技能库重新膨胀——提建议前先问凡哥，不擅自新建。
7. **write_file 写技能目录没有重名保护**——创建技能一律走 `skill_manage(action='create')`（会拒绝重名），只有改已有技能内容才用 write_file/patch。本次用 write_file 直接写技能目录导致与后台 Self-improvement review 自动生成的同功能技能并存。
8. **治理技能的"自动版"可能随时出现**——后台 review 会把当前会话的治理经验自动生成技能；发现与现有维护技能重复时，对比合并进 `skill-library-maintenance`，其余归档，不慌。
