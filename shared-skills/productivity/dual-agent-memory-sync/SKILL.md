---
name: dual-agent-memory-sync
description: 双Agent记忆同步 — 家里+公司两个 Hermes/OpenClaw 实例通过 Git 仓库同步记忆、知识库和工作总控台。
version: 1.0.0
platforms: [windows]
metadata:
  hermes:
    tags: [memory, sync, git, cron, dual-agent]
    category: productivity
---

# 双Agent记忆同步

凡哥使用两个 Agent 实例：家里（OpenClaw）+ 公司（Hermes）。通过 GitHub 私有仓库同步记忆，确保两边小南共享工作上下文。

## 架构

```
家里 OpenClaw ←→ github.com:yunchaoa1/xiaonan-memory.git ←→ 公司 Hermes
                       ↑
              D:\Hermes\xiaonan-memory (本地 clone)
```

## 同步机制

| 端 | 拉取 | 推送 |
|------|------|------|
| 公司 Hermes | **SOUL.md 启动规则**：每新会话自动 `git pull` | Cron job `40df234f060d`：每天 17:50 `git commit + push` |
| 家里 Hermes | 启动时 `git pull` | 每天下班前 push |

> ⚠️ 9:00 cron 已废弃——迟到会错过。改为 SOUL.md 规则：每次新会话第一件事就是 git pull。

## 树形总控台

工作总控台现已升级为**交互式树形 UI**，纳入 git 同步。优先使用仓库内共享版本：
- Markdown 总控：`D:\Hermes\xiaonan-memory\DASHBOARD.md`
- 树形 UI：`D:\Hermes\xiaonan-memory\dashboard-tree.html`

操作规则：
- 所有项目以可折叠树展示，点击节点展开/收起
- 颜色状态：绿色✅完成 / 紫色🔜进行中 / 灰色待办
- 两个小南共享同一棵树，通过 git 同步
- 每天只需更新树上对应节点状态，不需要碎片日志
- 如果旧路径 `D:\\SDkechengz\\dashboard-tree.html` 出现在记忆或旧技能里，先验证实际存在性；不要把旧路径当成唯一真相。

## 第三方 AI（豆包 / 飞书）共享记忆文件

凡哥还会用飞书里的**豆包**整理工作进展与拓扑图，它的记忆也要并进来。定案机制（2026-09-15，来回四轮才定，别再发明中间层）：

`D:\Hermes\xiaonan-memory\集团\豆包工作记忆.md` —— **唯一通道，按需读取**：
- **A 区**＝小南维护的现状口径（豆包只读）｜**B 区**＝豆包追加待并入（每条带日期）｜**C 区**＝变更日志
- 小南读的时机：开工读 DASHBOARD 时 / 凡哥提到项目·考核·进展·豆包时 / 要汇报或更新总控台时 / 凡哥说"同步一下"
- 读法：`python D:\Hermes\scripts\doubao_memory_watch.py`（只列 B 区**未并入**条目）
- 并入后在该条行尾标 `→ 已并入 YYYY-MM-DD`，结论补进 A 区

**两条铁律**：① 外部 AI **只能写共享文件，不能写 `MEMORY.md`**（2200 字硬上限，塞爆就什么都存不进）——外部 AI 写、小南压缩；② **总控台只认凡哥确认过的口径**，豆包的推测只进「待确认（外部输入）」。

**已被凡哥否掉的方案**：定时巡检轮询、飞书消息当中间线。他的"全自动"≈**"我不要多做任何动作"**，不是"你必须后台常驻轮询"——设计前先把这两种理解摆出来问一句。

细节（三区协议原文、给豆包的指令、被否方案的复盘、协议文件落点）：`references/外部AI共享记忆文件.md`。

> **豆包原来干的"画拓扑图"已交接给小南**（2026-09-20）：落地流程＝本地 python-pptx 生成 WPS 演示原生形状，模块字段/卡点三件套/图底待办等硬规则见 `project-topology-diagrams`。

## 仓库内容

同步的核心文件：
- `DASHBOARD.md` — 工作总控台（项目进度、优先级）
- `SOUL.md` — 小南人格定义
- `MEMORY.md` — 长期记忆摘要
- `memory/` — 每日日志（YYYY-MM-DD.md）
- `heart-demons/` — 心魔谱系（57条）
- `director-kb/` — 导演思维知识库
- `characters/` — 角色设定
- `集团/` — **业务主数据**：`台账数据.json`（考核原料）· `凡哥例行与待办.json`（日/周/月例行+待办）· `项目拓扑与模块清单.md` · `豆包工作记忆.md`
- 其他知识库目录

**不同步的（.gitignore 排除）：**
- 媒体文件（*.mp3, *.png, *.jpg 等）
- Python 缓存（__pycache__/）
- node_modules/
- 临时/脚本文件

> ⚠️ **通配规则会误伤主数据（2026-10-11 实测）**：`.gitignore` 里的 `*.json` 曾把 `集团/` 下两份主数据**整个挡在仓库外**，另一端因此没有考核原料。**凡是要跨机同步的业务数据，必须显式加 `!` 例外**（放在 `.gitignore` 末尾）并用 `git add -f` 首次入库 —— 完整分析见下方**坑 6**。

## 技能同步不能靠目录存在性推断

运行技能目录、Git同步仓库和另一端Agent的技能目录是三个不同层。仓库里“看得见一个SKILL.md”不代表它已被Git追踪，也不代表另一端运行时已经加载。

核验共享技能必须逐层检查：

1. **运行源**：确认当前Agent实际扫描的技能根目录；Hermes通常读取`$HERMES_HOME/skills/`，其他Agent路径必须实查。
2. **Git追踪**：在同步仓库执行`git check-ignore -v <技能文件>`和`git ls-files <技能路径>`；被`.gitignore`排除或未追踪的文件不会同步。
3. **提交任务范围**：确认cron的`workdir`和提交命令覆盖共享技能源目录，而不是只提交总控台。
4. **安装/镜像**：若Git中的共享技能源不等于运行目录，需要明确复制、链接或安装步骤；只`git pull`不会自动激活技能。
5. **加载验证**：在目标端用技能列表或明确加载命令验证技能可见；Hermes新增技能后使用`/reload-skills`或新会话重扫。
6. **单一真相源**：只在Git共享源编辑，运行目录由安装/镜像步骤生成，避免两端各改一份后漂移。

推荐只同步自建技能，不把Bundled、Hub安装和插件技能整体复制进记忆仓库。共享目录采用`shared-skills/`加Markdown索引。

### ✅ 本环境实际落地（2026-09-17 建成并验证）

```text
D:\Hermes\skills\                  运行副本（Hermes 实际加载，91 个 source=local 技能）
        ↓ sync_skills.py push
xiaonan-memory\shared-skills\      唯一编辑源（Git 同步，含 INDEX.md 索引）
        ↓ git push / pull
家里电脑（WSL Hermes）             待凡哥确认家里技能目录路径
        ↓ sync_skills.py pull
家里的技能目录                     运行副本
```

两个脚本（配套工具，**已随仓库同步到 `xiaonan-memory\scripts\`**）：
- `python scripts\sync_skills.py status|push|pull` —— 技能，只导 source=local
- `python scripts\sync_profile.py status|push|pull` —— 记忆与人格三件套

> ⚠️ **跑哪一份**：优先用 `<HERMES_HOME>\scripts\` 下那份（SOUL.md 里写死的路径）。仓库副本 `xiaonan-memory\scripts\` 自 2026-10-11 起也能直接跑（已改成位置自适应），但**改脚本时要两份一起改**，否则又漂移。

**自动兜底**：cron `40df234f060d` 每天 17:50 跑两条 push + git 提交 + 推送（**需 Gateway 在运行**，`hermes gateway status` 查）。
**开工安装**：SOUL.md 启动规则已写死 —— git pull 后跑两条 pull（profile 的 pull 会先备份到 `memories\.sync-backup\`）。

**踩过的 6 个坑（都能复现，别再踩）**：

1. **`.gitignore` 里的 `skills/`** —— 标着"OpenClaw 系统文件"，按名字匹配**任意层级**的 skills 目录，导致整个技能目录从未进过仓库。`shared-skills` 名字不同所以不受影响。
2. **技能名 ≠ 目录名** —— `creative/writing-opc-entry-test/` 里的技能名是 `writing-opc-entry`（Hermes 以 frontmatter 的 `name` 为准，不是目录名）。**用目录名扫描会漏 5 个技能**（91 变成 85）。扫描器必须读 frontmatter。
3. **找错记忆文件** —— 真正在用、memory 工具在写的是 `D:\Hermes\memories\MEMORY.md`；`D:\Hermes\MEMORY.md` 是 6 月的废弃副本。找错就会以为"记忆在同步"其实两头各写各的。
4. **builtin 混在同一批目录里** —— `creative/`、`software-development/` 等目录同时装着自建技能和 Hermes 自带技能，必须用 `hermes skills list` 的 Source 列筛 `local`，不能整目录复制。
5. **技能同步"静默空跑"（2026-10-11 实测，最阴）** —— 脚本原用 `HERMES_HOME = Path(__file__).resolve().parent.parent`；从仓库副本 `xiaonan-memory\scripts\` 跑时算出来的是**仓库自己**（少一层）→ `SKILLS`/`SHARED` 指向不存在的目录 → 打印 `push: 新增 0 个 []` / `更新 0 个 []`，**看着像成功，实际什么都没同步，也不报错**。我改完技能跑它，直到 `git show --stat HEAD` 只看见 DASHBOARD/SOUL、**没有技能文件**才露馅。
   **三条防身规则**：① 认 `status` 输出——`运行目录 D:\Hermes\skills 里的自建技能: 0` 就是路径算错了；② **刚改完技能，push 报"更新 0 个"是红旗，不是好消息**；③ 用 `git show --stat HEAD` 确认提交里**真有技能文件**，别只看 `git push` 成功。
   **已修**：改为向上找第一个含 `skills/` 的目录当 HERMES_HOME（两份副本都改了），且 scan 结果为 0 时**明确报错退出**（`**什么也没改。**`）。

6. **`.gitignore` 的通配规则静默吞掉主数据 → "假提交"（2026-10-11 实测，凡哥一句"日志这步你没提醒"顺藤摸出来的，最隐蔽）** —— `.gitignore` 里有一条防中间产物的 `*.json`，把 `集团/台账数据.json`（**考核原料**）和 `集团/凡哥例行与待办.json`（**例行清单**）一起误伤。后果：这两个文件**从未进过 git** → **另一台电脑上压根没有这两份主数据**（考核数据两头各一套）；而**提交历史里明明写着"新建 xx.json"** —— commit 成功、push 成功，**文件却不在仓库里**。
   **症状**：`git status --short` 干净（`nothing to commit`）**但你确定刚改过那个文件**；或 `git check-ignore -v <路径>` 有命中。
   **修法**：① `.gitignore` **末尾**加精确例外（`!` 规则**必须排在排除规则之后**才生效）：`!集团/*.json`；② **首次入库必须 `git add -f <路径>`** —— 新例外对**已被忽略的文件不会自动生效**，光 `git add -A` 带不上；③ 提交后用 `git ls-files -- <路径>` 复核。
   **三条防身规则**：① 写完**要跨机同步的业务数据**，先 `git check-ignore -v <路径>` 确认没被挡；② **提交后要 `git ls-files` 复核文件真在库里**，别只看 commit 输出/push 成功（与坑 5 同源：**"脚本说成功" ≠ "事情做成了"**）；③ 主数据宁可显式加例外，**不靠"通用排除规则碰巧放行"**。
   **通用教训**：`.gitignore` 是**按名字匹配、不分层级、静默生效**的 —— 一条防"中间产物"的规则，会连**主数据**一起吃掉，且**不报错**。

7. **改 SOUL / MEMORY / USER 改错了一份 = 白改，且 push 照旧成功（2026-10-11 实测，以为生效其实被覆盖）** —— `sync_profile.py` 的三对文件里，**真相源是"运行时"那一侧**：

   ```text
   D:\Hermes\SOUL.md               <->  xiaonan-memory\SOUL.md
   D:\Hermes\memories\MEMORY.md    <->  xiaonan-memory\MEMORY.md
   D:\Hermes\memories\USER.md      <->  xiaonan-memory\USER.md
    ↑ 真相源（改这份才生效）              ↑ 仓库副本（push 时会被运行时覆盖）
   ```

   **后果**：改**仓库副本** → 随后一次 `sync_profile.py push`（**运行时 → 仓库**）用旧版把你的改动**原样覆盖**，而 **commit / push 照旧报成功**。本次症状：SOUL 的改动在提交 `8043735` 里**压根没出现**（那次 `--stat` 只有 MEMORY.md 和技能文件），文件 mtime 还停在几周前。
   **症状辨识**：`git log --oneline -1 -- SOUL.md` 显示的最后提交**不是你刚做的那次**；或 `grep <你新加的句子> SOUL.md` 没命中；或 `sync_profile.py status` 报 `SOUL.md: 不同 ⚠️ 运行时 N 字 / 仓库 M 字`。
   **正确工序**：① **改运行时那份**（`D:\Hermes\SOUL.md`、`D:\Hermes\memories\MEMORY.md`、`D:\Hermes\memories\USER.md`）；② `sync_profile.py status` 看差异是否符合预期；③ `sync_profile.py push` 导出到仓库；④ **再 `status` 一次，必须三对全"一致 OK"**；⑤ 随记忆一起 commit + push。
   **与坑 6 同源**：**"命令没报错" ≠ "改动生效了"** —— 涉及两份副本的文件，改完必须**回源头确认**（`status` / `git ls-files` / `git show --stat`），别只看命令成功。

8. **在 `terminal` 里敲 Windows 反斜杠路径 = 路径被吃成粘连乱码（2026-10-12 实测，**每次新会话跑启动同步都会撞**）** —— SOUL.md 启动规则里写的是 `python D:\Hermes\scripts\sync_skills.py pull`，但本机 `terminal` 工具走的是 **bash（git-bash/MSYS）且 MSYS 路径转换已禁用**，未加引号的反斜杠被当作转义符吃掉：
   ```
   $ python D:\Hermes\scripts\sync_skills.py pull
   python.exe: can't open file 'D:\\Hermes\\xiaonan-memory\\Hermesscriptssync_skills.py': [Errno 2]
   ```
   注意它**还把当前工作目录前言拼了进去**，看起来像"脚本找不到"，极易误判成脚本缺失或克隆不全。
   **正确写法 = 一律正斜杠**（Windows 原生程序照样认）：
   ```bash
   python D:/Hermes/scripts/sync_skills.py pull
   python D:/Hermes/scripts/sync_profile.py pull
   python D:/Hermes/skills/software-development/skill-library-maintenance/scripts/health_check.py
   ```
   **三条防身**：① 命令里凡有 `D:\…` 一律手改成 `D:/…`；② 报错文本里出现**没有反斜杠的粘连路径**（`Hermesscripts…`、`Hermesskills…`）= 就是这个坑，**别去查文件在不在，先换斜杠**；③ `cd /d/Hermes/xiaonan-memory && python D:/Hermes/scripts/…` 这种混用是对的 —— bash 内置 `cd` 吃 `/d/…`，**原生 python 吃 `D:/…`**，两者不互通（`python /d/Hermes/...` 同样会失败）。

完整审计清单见`references/shared-skill-sync-audit.md`。

## 新实例上线

当在新环境启动时：
1. 确保 SSH key 已配置：`ssh -T git@github.com`
2. Clone 仓库（如果还没有）：`git clone git@github.com:yunchaoa1/xiaonan-memory.git`
3. 读取 `DASHBOARD.md` 了解当前工作状态
4. 读取 `memory/` 下最近几天的日志了解进展
5. 设置 cron job（pull + push）自动同步

## 手动同步

临时需要同步时：
```bash
cd /d/Hermes/xiaonan-memory
git pull origin main          # 拉取家里小南的最新记忆
# ... 做你的工作，产生记忆变更 ...
git add -A && git commit -m "manual: 手动同步" && git push
```

## cron 健康检查（模型迁移 / 任务坏掉都要跑这套）

当 Hermes 主模型/provider 更换后，不要只看当前会话能不能聊；还要检查旧 cron 任务是否保留了创建时的 `provider_snapshot` / `model_snapshot`。

**最快体检**：`hermes cron list` —— 只看 `Last run` 行；出现 `error: … (N failures in a row)` 就是坏任务（2026-09-15 实测：两个任务被钉在已回滚的 `gpt-5.5/openai-codex` 上，连续失败 17 次，用 `RuntimeError: Request timed out.` 表现）。

**任务不触发 → 先看调度器现状，别急着起 gateway（2026-10-10 修正）**：

- **桌面版 App 自带 in-process 调度器**（日志出现 `hermes_cli.web_server: Desktop cron scheduler started (provider=builtin, interval=60s)`），**App 启动时会补跑错过的任务**（实测 10-07 20:48 补跑了当天 17:50 的提交任务）→ 平时**开着 App 就够，不要再多起一个**。
- ⚠ **两个调度器并存会抢任务**：`hermes gateway start` 会**再起一个** in-process 调度器 → 一次性任务可能被"领走但不执行"、**静默消失**（本次实测：12:33 的测试任务无记录消失；与历史 incidents 里 `Fire claim ownership lost; stale result was discarded` 同一病症）。要起 gateway 就**先停掉另一个**（`hermes gateway stop`）。
- 查询统一用 **`hermes cron status`**（显示调度器进程 / `Ticker heartbeat` / active job 数）——`hermes gateway status` 只反映网关，**不代表调度器**。
- **deliver 必须显式写 `bot-chat`**：用 cronjob 工具不写 deliver 时默认落 `local` ＝ **只存不推送**（桌面版唯一可推送的通道就是 Bot Chat）；纯提醒一律用 **`no_agent` 脚本版**（不走大模型，不怕余额/限流）。
- **通道必须实测**：建一个 2 分钟后的一次性测试任务 → `hermes cron run <id>` 立即触发 → `hermes cron runs <id>` 看 `completed` + `grep "delivered to Bot Chat" logs/agent.log` → 验证完删掉测试任务。提醒类需求另见 `fange-reminders`（含 Windows 任务计划兜底）。

**改模型只能走 CLI**（`cronjob` 工具的 API 不暴露 model/provider）：
`hermes cron edit <job_id> --model <model> --provider <provider>`
**验证必须做**：`hermes cron run <job_id>` → `Ran now: succeeded` → `hermes cron list` 显示 `ok` → 读 `cron/output/<job_id>/<ts>.md` 的 `## Response`（同步类任务无变更时应为 `[SILENT]`）。

**⚠️ 填模型名之前先核 provider 的真实模型列表（2026-09-20 实测踩坑）**：我凭记忆写成 `deepseek-v4-flash`（**这个型号根本不存在**，是把 "v4" 和 "flash" 拼在一起了），填进了 cron，也早躺在 `delegation.model` 里。DeepSeek 官方 `/v1/models` 实际只有**两个**：**`deepseek-flash`**（日常/固化执行）、**`deepseek-v4-pro`**（重活：试错/创作/定方法论）。

- 核验：`set -a; . D:/Hermes/.env; set +a; curl -s "${DEEPSEEK_BASE_URL:-https://api.deepseek.com}/v1/models" -H "Authorization: Bearer $DEEPSEEK_API_KEY"`
- 修 cron：`hermes cron edit <job_id> --model deepseek-flash --provider deepseek`
- 修子代理：`hermes config set delegation.model deepseek-flash`（`config.yaml` 的 `delegation:` 段，约 141 行）
- **症状辨识**：错模型名的表现与 provider 挂掉**一模一样**（cron 连续 `RuntimeError: Request timed out.`）→ 遇到"连不上"先核**名字**，再怀疑网络。
- 铁律：**任何模型名一律先查再填，不凭记忆写**（凡哥对"我写的名字根本不存在"这件事很敏感，会直接反问"我之前不是调成 flash 了吗"）。

⚠️ **`schedule="30m"` 会落库成一次性任务（`once`/`repeat: once`）** —— 周期性必须用 cron 语法（`*/30 * * * *`）并复核 `repeat` 字段。

**定时任务不能替代"节点即时更新"**：已经在节点自动完成的事（如总控台更新）**不要再加定时提醒**（凡哥判定为噪音并删除）；定时任务只留给**兜底**（17:50 未提交变更的自动推送）和**外部变化源**。

完整排障手册（症状/根因/命令/验证/monitor 哨兵坑）：`references/provider-migration-cron-checklist.md`。

## 验证

```bash
cd /d/Hermes/xiaonan-memory && git status && git log --oneline -3
```

## 注意事项

- 两个实例不同时编辑同一文件，避免合并冲突
- **同一个工作树可能被并发提交**（另一端 / 另一会话也在跑 17:50 那类自动提交，2026-10-10 实测）：`git pull` 报 `cannot pull with rebase: You have unstaged changes` → 那是**别人的未提交改动**，不是你的 → 此时**只 `git add <你改的具体路径>`**，**别用 `git add -A`**（会把对方半成品裹进你的提交）
- **提交显示 `nothing to commit` 但你确定刚改过文件** → 大概率是对端已把你的改动一起提交了：先 `git log --oneline -3` + `git status` 核实，**别急着重写文件**
- 每次动手前先 `git pull origin main`（能拉就拉）；拉不动时按上面两条处理，改动就绪后再 push
- 每天 17:50 自动提交，确保下班前记忆已落地
- 如果冲突发生，优先保留内容更完整的版本

## ⚠️ 改 SOUL / MEMORY / USER 必须改"运行时真身"（2026-10-11 实测踩坑）

**配对关系（`sync_profile.py` 的 `PAIRS`，第 25-27 行）**：

| 运行时真身 ← **改这个** | 仓库副本 ← 别直接改 |
|---|---|
| `D:\Hermes\SOUL.md` | `xiaonan-memory\SOUL.md` |
| `D:\Hermes\memories\MEMORY.md` | `xiaonan-memory\MEMORY.md` |
| `D:\Hermes\memories\USER.md` | `xiaonan-memory\USER.md` |

**坑的本质**：`sync_profile.py push` 是**运行时 → 仓库**的**单向覆盖**。**改仓库副本 = 白改** —— 下次 push 会用运行时旧版把它盖掉。

**本次事故**：我改的是仓库副本 `xiaonan-memory\SOUL.md`，随后跑 push，**改动被 9-17 的旧版覆盖** → 查 `git show <commit> -- SOUL.md` 时**压根没有 SOUL.md**（只有 MEMORY 和技能），排查很久才发现是"改错文件"。**症状隐蔽**：patch 工具报"成功"，文件却还是旧时间戳。

**正确流程**：
1. 改**运行时真身**（上表左列）
2. `python D:\Hermes\scripts\sync_profile.py push`
3. `python D:\Hermes\scripts\sync_profile.py status` → 必须显示 **`合计: 一致 3 / 不同 0`**
4. 随记忆一起提交

**自查信号**：改完 SOUL/MEMORY 后 `ls -la` 发现**文件修改时间没变** → 就是改错了文件。

## ⚠️ 用 memory 工具批量改记忆：禁止「链式 replace」（2026-10-12 实测踩坑）

`memory(action='operations')` 的 `old_text` 是**在当前记忆里按子串匹配已有条目**。一旦把上一条的 `new_text` 当下一条的 `old_text`（接龙式），条目会**整体错位、并静默吞掉一条**：

```
op1: A 这条 → 新内容       # 正常
op2: B 这条 → A 的内容      # B 被覆盖成 A 的内容（原 B 丢失）
op3: C 这条 → B 的内容      # 连锁错位…
```

**本次实际后果**：`渠总=…` 那条被顶成「集团名」、`总控台` 条被顶成「渠总」，最后 **`模型:deepseek-flash…` 整条消失**。而批次**报成功**（`Applied N operations`）—— 只有 `read_file D:\Hermes\memories\MEMORY.md` 才看得出错位。

**四条纪律**：

1. **每条操作的 `old_text` 必须是记忆里当前真实存在的原文**，只改它自己那一条；**绝不把上一条的产出当下一条的输入**。
2. **改完必须回读核对**：`read_file D:\Hermes\memories\MEMORY.md`，数条目、看有没有错位/缺失。⚠️ 工具返回的 `usage`（字数）和 `entry_count` **只说明写了，不说明写对了**。
3. **`old_text` 太短/太通用 → 整批不落地**：本次想用 `。` 删掉一个空条目，报 `'。' matched multiple distinct entries`，而 operations 是**全有或全无（all-or-nothing）** —— 一条不匹配，**整批一条都不写**。定位要用**足够长且唯一**的片段（长句尾部、带专有名词的句子）。
4. **要腾空间就在同一批里压缩旧条目**：上限按**批次最终结果**校验（不是中间态），所以「删两条 + 改短一条 + 加一条」可以**一次过** —— 比新开一条、分两批省事得多。把冗长条目改短、把同主题并进一条，是扩容首选。

## ⚠️ 凡哥说「今天没做完的明天继续提醒我」→ 改数据，别新建 cron（2026-10-12 实测）

`集团\凡哥例行与待办.json` 是**提醒的唯一数据源**（11:00 例行提醒 + 17:30 下班提醒脚本都读它；详见 `fange-reminders`）。所以「顺延到明天」是一个**改数据**的动作，不是加定时任务：

1. **顺延**：当天到期、状态仍为 `待办` 的项，在 `备注` 前插 `⚠️ <日期> 未完成顺延 | ` —— ⚠️ **`状态` 保持 `待办` 不变**，改成别的值它就不再弹
2. **要明天绷的项**：`截止` 改到明天。筛选规则是「`截止` < 今天 = 已超期 / == 今天 = 今天到期」，**截止不改就永远不弹**
3. **凡哥点名「包括这个问题」** → 那个项也要一起改到明天，**别只顺延、忘了他点名的**
4. **改完用 `execute_code` 跑一遍筛选逻辑打印"明天会弹什么"**，再跑 `python /d/Hermes/scripts/remind_fange_daily.py` 看脚本真实输出 —— **两处对上才算数**（JSON 里"看起来对"不算）
5. 回话分段给他：`今天该做没做` / `明天到期` / `后天到期`，并点明唯一前提是 App 保持运行

⚠️ **顺延会累积**：项本身永不自删，只覆盖日期标记 → 几天后清单会膨胀。**过几天主动问一句"这几条还留着吗"**。
⚠️ **`_前提条件` 段**也在同一份 JSON 里（App 须运行 / 17:50 依赖 API 余额 / App 重启会补跑）—— 动这个文件时别把它删掉。
