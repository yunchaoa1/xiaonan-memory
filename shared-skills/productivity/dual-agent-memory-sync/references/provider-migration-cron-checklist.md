# Hermes provider migration + cron sync checklist

Use this when Hermes' main model/provider changes (for example DeepSeek/custom → OpenAI Codex OAuth) and the user relies on dual-agent memory sync.

## Why this matters

Cron jobs can retain `provider_snapshot` / `model_snapshot` from the provider active when the job was created. Updating `config.yaml` or `/model` does not necessarily update old cron snapshots. A sync job can keep calling an expired provider key while normal chat already works.

把模型状态分成四层核对：①当前会话 runtime ②`config.yaml` 默认主模型 ③`auxiliary.vision` 视觉覆盖 ④cron 的 model/provider override 或 snapshot。手动切换当前会话不代表其他三层同步变化；`auxiliary.vision.provider=auto` 才会优先跟随主模型，显式 provider/model 会继续锁定旧视觉模型。

## Checklist

1. Verify current chat model and auth:
   - `hermes config show`
   - `hermes auth list <provider>`
   - one real smoke test: `hermes chat -q "只回答 ok" --provider <provider> -m <model>`

2. Verify auxiliary vision separately:
   - Check `auxiliary.vision.provider/model/base_url/api_key`.
   - If migrating away from an old aggregator, clear stale `base_url` and `api_key`; a leftover endpoint can override the visible provider/model.
   - Run one real `vision_analyze` smoke test on a known image.

3. Audit cron jobs:
   - `hermes cron list --all`
   - Inspect `cron/jobs.json` for `provider_snapshot` and `model_snapshot`.
   - If a job still points to the old provider, update the job model/provider or recreate it.
   - Check recent `cron/output/<job_id>/*.md` for 401/auth errors.

4. Verify scheduler health:
   - `hermes cron status`
   - If it says gateway/scheduler is not running, the jobs will not fire automatically even if their model config is valid.

5. Verify the memory repo before relying on auto-sync:
   - `git -C D:/Hermes/xiaonan-memory status --short --branch`
   - Ensure `.gitignore` excludes Hermes desktop transient attachments such as `.hermes/` and large/private document formats when appropriate.

6. Verify the scheduler/gateway, not just the job config:
   - `hermes gateway status`
   - `hermes cron status`
   - On Windows, if cron says the gateway is not running, install/start the scheduled gateway task before trusting automatic jobs.
   - 2026-09-15 实测：Windows **登录项已装**（`…\Startup\Hermes_Gateway.vbs`）但**进程没跑** → `hermes gateway start` 后 `✓ Gateway process running (PID …)`，任务才会触发。**"已安装" ≠ "在运行"。**

## Cron 任务排障：被钉死在失效模型上（2026-09-15 实测修复）

**症状**（这两个任务坏了半个多月没人发现）：

```
Last run: 2026-09-14T17:53:20  error: RuntimeError: Request timed out.  (17 failures in a row)
Last run: 2026-09-15T10:30:35  error: RuntimeError: Request timed out.  (16 failures in a row)
```

**根因**：任务创建时钉在 `gpt-5.5 / openai-codex`，该模型已回滚失效 → 每次运行都是超时/连接错误。跟仓库、git、脚本都无关。

**诊断三步**
1. `hermes cron list` → 只看 `Last run` 行，出现 `error: ... (N failures in a row)` 就是坏任务。
2. `hermes cron runs <job_id>` → 逐条历史（本例可回溯到 2026-08-28，全是 `Request timed out` / `Connection error`）。
3. `cron/jobs.json` / `hermes cron list` → 看该任务的 `model` + `provider`，与当前可用模型比对。

**修复**（⚠️ **cronjob 工具的 API 不暴露 model/provider，改模型只能走 CLI**）：

```bash
hermes cron edit <job_id> --model deepseek-v4-flash --provider deepseek --prompt "……"
```

**验证（必须做，别只看命令返回）**
1. `hermes cron run <job_id>` → `Ran now: succeeded.`
2. `hermes cron list` → `Last run: … ok` / `Execution: completed`
3. 读 `cron/output/<job_id>/<时间戳>.md` 末尾的 `## Response`：同步类任务在无变更时应为 `[SILENT]`（= 没东西可提交，且不打扰人）。

**顺手修掉 prompt 里的伪 shell 语法**：`git commit -m "auto: $(date '+%m/%d') …"` 这种写法在**没有 shell** 的执行环境里不会展开，会把 `$(date …)` 原文写进 commit message。改成"用今天真实日期 YYYY-MM-DD"。

## 调度语法陷阱：`30m` 会变成一次性任务

用 cronjob 工具创建时传 `schedule="30m"`，落库是 **`once in 30m` / `repeat: once`** —— **只跑一次**，不是每 30 分钟。

- 要**周期性**：用 cron 语法（`*/30 * * * *`、`* * * * *`、`0 10 * * *`），必要时显式给 `repeat`（`repeat: 100000` 会显示成 `"100000 times"`，等效长期有效）。
- **建完/改完必须 `cronjob action='list'` 复核 `schedule` 与 `repeat` 两个字段**，别有"我以为它在跑"。

## monitor 模式（有变化才唤醒）的实操坑

用哨兵脚本当 `monitor` 时：脚本先跑，输出**字节级哈希**不变 → 直接跳过 agent（不花 LLM 费用）；变了才把 diff 注入 agent。

- 脚本输出**必须确定性**（无时间戳、无随机、顺序稳定），否则每轮都像"有变化"。
- 首次 tick 只做基线；**状态被处理后通常还会多跑一次**（输出由"有 N 条"变成"NO_NEW_ENTRIES"），属正常。
- 匹配规则别写太宽：本次哨兵第一版把 markdown 分隔线 `---` 当成条目 → 只认 `- ` 开头的行并显式排除 `---`。

## 原则：定时任务不能替代"节点即时更新"

「每日总控台更新提醒」被判定**冗余后删除**——逻辑是：既然工作到节点就自动更新总控台，**再定时提醒"记得更新"只是在提醒一件已经自动完成的事，纯噪音**。

- 判定问句：**这件事是不是已经由"节点触发"自动完成？** 是 → 不要再加定时提醒。
- 定时任务只留给两类：**兜底**（如 17:50 未提交变更的自动提交，防漏）与**外部变化源**（别人的改动、外部系统的变化）。
- 兜底型任务要与"平时习惯"区分清楚再讲给凡哥听：他若觉得重复，可以删（本次即说明"我一有变更就推送，这个只是防漏"）。

## Pitfalls

- Do not judge provider health using only `curl` against the public API. OAuth-backed providers may use different endpoints and cookies/tokens than direct API calls.
- Do not record “tool X is broken” as a durable lesson. Record the verification and migration pattern instead.
- In the Hermes TUI, cron jobs with `deliver=origin` are local-only/no live delivery; do not promise they will message the current TUI session.
- Do not remove a backup provider just because the active chain moved away from it. If the user says “保留 DeepSeek，Agnes 不用”, keep DeepSeek/API entries as backup, deprecate Agnes from active/auxiliary config, and make that distinction explicit.
- A cron job can show `last_status: ok` only after a manual run; after editing model/provider, run at least one safe job. For push jobs, make them no-change safe first so a clean tree does not become a fake failure.
- 一个坏了半个多月的定时任务，`hermes cron list` 一眼就能看出来（`(N failures in a row)`）——**凡哥问起"定时任务还好吗"时就直接跑这条命令**，不要靠印象回答。
