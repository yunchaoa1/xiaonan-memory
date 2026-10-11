# -*- coding: utf-8 -*-
"""remind_fange_daily.py —— 凡哥的每日例行提醒（no_agent 脚本版）

每天 11:00 由 cron 投递到 bot-chat。
数据源：
  · 集团/凡哥例行与待办.json  —— 日/周/月例行清单 + 凡哥待办（小南维护）
  · 集团/台账数据.json        —— 自动带出凡哥名下未完成的任务
"""
import json
import os
import datetime

BASE = r"D:\Hermes\xiaonan-memory\集团"
TODAY = datetime.date.today()
WD = TODAY.weekday()                                    # 0 = 周一
DAY = TODAY.day
WD_CN = ["一", "二", "三", "四", "五", "六", "日"][WD]


def load(name):
    try:
        return json.loads(open(os.path.join(BASE, name), encoding="utf-8").read())
    except Exception:
        return None


plan = load("凡哥例行与待办.json") or {}
ledger = load("台账数据.json") or {}

print(f"【凡哥 · {TODAY}（周{WD_CN}）· 小南的每日提醒】")

# ── 1) 还没做的 ────────────────────────────────
todo = [t for t in plan.get("待办", []) if t.get("状态") != "已完成"]
mine = [t for t in ledger.get("任务", [])
        if (t.get("人") or "") == "谢泽凡" and (t.get("状态") or "") not in ("已完成",)]

if todo or mine:
    print("\n■ 【还没做的】")
    for t in todo:
        due = t.get("截止") or ""
        flag = ""
        if due:
            try:
                dd = datetime.date.fromisoformat(due)
                if dd < TODAY:
                    flag = f"   ⚠️ 已超期 {(TODAY - dd).days} 天"
                elif dd == TODAY:
                    flag = "   ⚠️ 今天到期"
            except Exception:
                pass
        print(f"  · {t['项']}" + (f"（截止 {due}）" if due else "") + flag)
        if t.get("备注"):
            print(f"      → {t['备注']}")
    for t in mine:
        print(f"  · [台账] {t.get('节点')}｜{t.get('状态')}")

# ── 2) 每天必做 ────────────────────────────────
print("\n■ 【每天必做】")
for x in plan.get("每日", []):
    print(f"  · {x['项']}")
    if x.get("提示"):
        print(f"      → {x['提示']}")

# ── 3) 每周（周一提醒）─────────────────────────
if WD == 0:
    print("\n■ 【本周必做】")
    for x in plan.get("每周", []):
        print(f"  · {x['项']}")
        if x.get("提示"):
            print(f"      → {x['提示']}")

# ── 4) 每月（1–3 号 or 月末）───────────────────
last_day = (TODAY.replace(day=28) + datetime.timedelta(days=4)).replace(day=1) - datetime.timedelta(days=1)
if 1 <= DAY <= 3 or DAY == last_day.day:
    print("\n■ 【本月必做】" + ("（月初 · 收发表+打分）" if DAY <= 3 else "（月底 · 冻结+算分+归档）"))
    for x in plan.get("每月", []):
        print(f"  · {x.get('日', '')} {x['项']}")
        if x.get("提示"):
            print(f"      → {x['提示']}")

# ── 5) 事件触发项（不是周期，但"到了就必须做"）──
ev = plan.get("事件触发", [])
if ev:
    print("\n■ 【事件触发项】（到了就要做，小南盯着台账替你记）")
    for x in ev:
        print(f"  · {x['事件']} → {x['项']}")
        if x.get("提示"):
            print(f"      → {x['提示']}")

print("\n（清单在 集团/凡哥例行与待办.json —— 要加要改，跟我说一句就行）")
