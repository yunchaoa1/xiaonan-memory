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

## 仓库内容

同步的核心文件：
- `DASHBOARD.md` — 工作总控台（项目进度、优先级）
- `SOUL.md` — 小南人格定义
- `MEMORY.md` — 长期记忆摘要
- `memory/` — 每日日志（YYYY-MM-DD.md）
- `heart-demons/` — 心魔谱系（57条）
- `director-kb/` — 导演思维知识库
- `characters/` — 角色设定
- 其他知识库目录

不同步的（.gitignore 排除）：
- 媒体文件（*.mp3, *.png, *.jpg 等）
- Python 缓存（__pycache__/）
- node_modules/
- 临时/脚本文件

## 技能同步不能靠目录存在性推断

运行技能目录、Git同步仓库和另一端Agent的技能目录是三个不同层。仓库里“看得见一个SKILL.md”不代表它已被Git追踪，也不代表另一端运行时已经加载。

核验共享技能必须逐层检查：

1. **运行源**：确认当前Agent实际扫描的技能根目录；Hermes通常读取`$HERMES_HOME/skills/`，其他Agent路径必须实查。
2. **Git追踪**：在同步仓库执行`git check-ignore -v <技能文件>`和`git ls-files <技能路径>`；被`.gitignore`排除或未追踪的文件不会同步。
3. **提交任务范围**：确认cron的`workdir`和提交命令覆盖共享技能源目录，而不是只提交总控台。
4. **安装/镜像**：若Git中的共享技能源不等于运行目录，需要明确复制、链接或安装步骤；只`git pull`不会自动激活技能。
5. **加载验证**：在目标端用技能列表或明确加载命令验证技能可见；Hermes新增技能后使用`/reload-skills`或新会话重扫。
6. **单一真相源**：只在Git共享源编辑，运行目录由安装/镜像步骤生成，避免两端各改一份后漂移。

推荐只同步自建技能，不把Bundled、Hub安装和插件技能整体复制进记忆仓库。共享目录可采用`shared-skills/`加Markdown索引；目标端路径确认后再写适配步骤。

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

**任务根本不触发 → 先查网关**：`hermes gateway status`。网关没进程时，所有 cron **静默不执行**（Windows 的登录项只保证"下次登录后"自动起，本次实测启动前新建的任务一直停在等待首次运行）→ `hermes gateway start`，再 `sleep 4 && hermes gateway status` 确认 PID 起来了。

**改模型只能走 CLI**（`cronjob` 工具的 API 不暴露 model/provider）：
`hermes cron edit <job_id> --model <model> --provider <provider>`
**验证必须做**：`hermes cron run <job_id>` → `Ran now: succeeded` → `hermes cron list` 显示 `ok` → 读 `cron/output/<job_id>/<ts>.md` 的 `## Response`（同步类任务无变更时应为 `[SILENT]`）。

⚠️ **`schedule="30m"` 会落库成一次性任务（`once`/`repeat: once`）** —— 周期性必须用 cron 语法（`*/30 * * * *`）并复核 `repeat` 字段。

**定时任务不能替代"节点即时更新"**：已经在节点自动完成的事（如总控台更新）**不要再加定时提醒**（凡哥判定为噪音并删除）；定时任务只留给**兜底**（17:50 未提交变更的自动推送）和**外部变化源**。

完整排障手册（症状/根因/命令/验证/monitor 哨兵坑）：`references/provider-migration-cron-checklist.md`。

## 验证

```bash
cd /d/Hermes/xiaonan-memory && git status && git log --oneline -3
```

## 注意事项

- 两个实例不同时编辑同一文件，避免合并冲突
- 每天 17:50 自动提交，确保下班前记忆已落地
- 如果冲突发生，优先保留内容更完整的版本
