---
name: fange-reminders
description: Use when 凡哥要"到时候提醒我"（承诺到期核实/某日前落地/定时通知）时。可靠提醒三板斧与踩过的坑。
version: 1.0.0
author: 小南
license: MIT
metadata:
  hermes:
    tags: [提醒, cron, 到期核实, 带人]
    related_skills: [project-dashboard, team-management-ops]
---

## When to Use

凡哥说「X 前落地，到时候提醒我去核实」「下周五前完成，记得提醒我」时加载——目标是在**未来某天主动弹给他**，并带上具体核实点；不是现在写个待办就算完。

# 给凡哥挂"到时候提醒我"

## 触发
凡哥说「X 前落地，到时候提醒我去核实」「下周五前完成，记得提醒我」——要在**未来某天主动弹给他**，不是现在写个待办就完事。

## 三板斧（至少做前两条）

### 1. Hermes cron · **no_agent 脚本版**（最可靠：不走大模型）
```python
# D:\Hermes\scripts\remind_<主题>.py —— print() 的内容原样投递
print("⏰ 提醒：…\n① …\n② …")
```
```
cronjob(action='create', name='提醒·…', schedule='2026-10-16T09:30:00',
        no_agent=True, script='remind_<主题>.py', deliver='bot-chat')
```
- ⚠ **deliver 必须显式写 `bot-chat`**：不写默认 `local`＝只存本地、**不推送**（等于没提醒）
- 时刻选**上午 09:30**；承诺期最后一天提醒（能当天就去催），不要等过了期限

### 2. Windows 任务计划（Hermes 没开也能弹）
```vbs
' D:\Hermes\scripts\remind_<主题>.vbs —— 600 秒自动关，不卡电脑
Set sh = CreateObject("WScript.Shell")
sh.Popup "提醒正文…", 600, "小南提醒 · …", 64
```
```
schtasks /Create /TN "Hermes_提醒_<主题>" /TR "wscript.exe \"D:\Hermes\scripts\remind_<主题>.vbs\"" /SC ONCE /ST 09:30 /SD 2026/10/16 /F
```
验证：`schtasks /Query /TN "Hermes_提醒_<主题>" /FO LIST`（看 Next Run Time / Status: Ready）

### 3. 落在台账与总控台（给人看的兜底）
- `D:\Hermes\xiaonan-memory\集团\台账数据.json` 加一条 `状态:"待办"`、`work_date`＝承诺日、写清"到期提醒凡哥核实"
- `DASHBOARD.md` 对应项目分支加节点；脑图 `project_tree_data.py` 加 `block` 节点后跑 `gen_xmind.py`
- 提醒正文里带**3 个具体核实点**（不写"记得核实"这种废话）

## 坑（都实测踩过）
1. **别起 gateway 调度器**：桌面版 App 自带 in-process 调度器（60s tick；App 启动时补跑错过的任务）。再 `hermes gateway start` 会出现**两个调度器互抢** → 任务"被领走但未执行"、**静默消失**（`hermes cron runs` 查不到、任务还从列表没了）。查状态：`hermes cron status`
2. **必须验证通道**：建一个 2 分钟后的测试任务 → `hermes cron run <id>` 立刻触发 → `hermes cron runs <id>` 看 `completed`，再 `grep "delivered to Bot Chat" D:\Hermes\logs\agent.log` 确认投递 → 验证完删掉测试任务。**没验过就等于没挂**
3. **日期先核星期**：`date -d "2026-10-17" "+%A"`——凡哥把 10-17（周六）说成"下周五"过；核完在回复里点出来并给出建议日期
4. **余额风险**：大模型版 cron 遇 402 Insufficient Balance 直接失败 → 纯提醒一律 `no_agent`
5. **别双报**：同一件事只留一个 cron；改需求时先 `cronjob(action='list')` 找旧的删掉
