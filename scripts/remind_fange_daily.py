# -*- coding: utf-8 -*-
"""remind_fange_daily.py —— 凡哥的每日例行提醒（no_agent 脚本版）

每天 11:00 由 cron 投递到 bot-chat（工作日；非工作日默认静默，只当有到期/超期项才提醒）。
凡哥 2026-10-11 令：「只在工作日提醒」（小南 2026-10-12 落地 · 闸门见 workday_cal.py）
数据源：
  · 集团/凡哥例行与待办.json  —— 日/周/月例行清单 + 凡哥待办（小南维护）
  · 集团/台账数据.json        —— 自动带出凡哥名下未完成的任务
测试钩子：REMIND_TODAY=2026-10-04 python remind_fange_daily.py（假装今天是那一天）
"""
import json
import os
import sys
import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from workday_cal import is_workday
except Exception:                                   # 兜底：表读不到就按周一至周五
    def is_workday(d):
        return d.weekday() < 5

BASE = r"D:\Hermes\xiaonan-memory\集团"
_ENV = os.environ.get("REMIND_TODAY")
TODAY = datetime.date.fromisoformat(_ENV) if _ENV else datetime.date.today()
WD = TODAY.weekday()                                    # 0 = 周一
DAY = TODAY.day
WD_CN = ["一", "二", "三", "四", "五", "六", "日"][WD]


def load(name):
    try:
        return json.loads(open(os.path.join(BASE, name), encoding="utf-8").read())
    except Exception:
        return None


def due_of(t):
    try:
        return datetime.date.fromisoformat((t.get("截止") or "").strip())
    except Exception:
        return None


def tname(x):
    """标题字段兼容：待办用「项」，周会新增的几条误写成「事项」，台账用「节点」。
    小南 2026-11-23 修：11-23 周会新增 4 条待办用了「事项」键，
    导致 line 88 KeyError: '项'，当天 11:00 提醒整份没发出去。"""
    return x.get("项") or x.get("事项") or x.get("节点") or ""


def closed(st):
    """状态是否等于「已收口」——按包含判断。

    小南 2026-11-03 修：原来用精确等于 ("已完成","已作废")，
    所以「已完成（模板已交）」「已完成（10-30 更正）」「已结项」这类
    都会被当成没做完，天天重复弹（10-30～11-02 实际发生过）。
    """
    s = (st or "").strip()
    return any(k in s for k in ("已完成", "已作废", "已结项", "已取消", "已撤回", "已挂起"))


plan = load("凡哥例行与待办.json") or {}
ledger = load("台账数据.json") or {}

todo = [t for t in plan.get("待办", []) if not closed(t.get("状态"))]
mine = [t for t in ledger.get("任务", [])
        if (t.get("人") or "") == "谢泽凡" and not closed(t.get("状态"))]

# ── 非工作日静默闸门（凡哥 2026-10-11 令）────────────────────
# 非工作日 + 没有「今天到期 / 已超期」的项 → 输出为空 = 不投递
WORKDAY = is_workday(TODAY)
urgent = [t for t in todo if due_of(t) is not None and due_of(t) <= TODAY]
if not WORKDAY and not urgent:
    sys.exit(0)

print(f"【凡哥 · {TODAY}（周{WD_CN}）· 小南的每日提醒】")
if not WORKDAY:
    print("（今天是非工作日 · 只因为有过期/到期项才提醒）")

# ── 1) 还没做的 ────────────────────────────────
if todo or mine:
    print("\n■ 【还没做的】")
    for t in todo:
        due = t.get("截止") or ""
        flag = ""
        dd = due_of(t)
        if dd is not None:
            if dd < TODAY:
                flag = f"   ⚠️ 已超期 {(TODAY - dd).days} 天"
            elif dd == TODAY:
                flag = "   ⚠️ 今天到期"
            else:
                flag = f"   （{dd} 到期）"
        print(f"  · {tname(t)}" + (f"（截止 {due}）" if due else "") + flag)
        if t.get("备注"):
            print(f"      → {t['备注']}")
    for t in mine:
        print(f"  · [台账] {t.get('节点')}｜{t.get('状态')}")

# ── 2) 每天必做 ────────────────────────────────
print("\n■ 【每天必做】")
for x in plan.get("每日", []):
    print(f"  · {tname(x)}")
    if x.get("提示"):
        print(f"      → {x['提示']}")

# ── 3) 每周（周一提醒）─────────────────────────
if WD == 0:
    print("\n■ 【本周必做】")
    for x in plan.get("每周", []):
        print(f"  · {tname(x)}")
        if x.get("提示"):
            print(f"      → {x['提示']}")

# ── 4) 每月（1–3 号 or 月末）───────────────────
last_day = (TODAY.replace(day=28) + datetime.timedelta(days=4)).replace(day=1) - datetime.timedelta(days=1)
if 1 <= DAY <= 3 or DAY == last_day.day:
    print("\n■ 【本月必做】" + ("（月初 · 收发表+打分）" if DAY <= 3 else "（月底 · 冻结+算分+归档）"))
    for x in plan.get("每月", []):
        print(f"  · {x.get('日', '')} {tname(x)}")
        if x.get("提示"):
            print(f"      → {x['提示']}")

# ── 5) 事件触发项（不是周期，但"到了就必须做"）──
ev = plan.get("事件触发", [])
if ev:
    print("\n■ 【事件触发项】（到了就要做，小南盯着台账替你记）")
    for x in ev:
        print(f"  · {x.get('事件','')} → {tname(x)}")
        if x.get("提示"):
            print(f"      → {x['提示']}")

print("\n（清单在 集团/凡哥例行与待办.json —— 要加要改，跟我说一句就行）")
