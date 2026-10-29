#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""考核表·覆盖核对（台账里每人每月每条「工作日报」是否都进了考核表）

用法：
  python check_kaohe_coverage.py --month 2026-10
  python check_kaohe_coverage.py --month 2026-10 --doc "D:/Documents/我的文档/CTO攻略/2026-10_绩效考核表_v5完整版.md"
  python check_kaohe_coverage.py --month 2026-10 --dump     # 只打印每人的日报清单（拿来当「全月流水」附录）

判据：某人当月「日报条数」== 考核表里出现过的日期条数，才算覆盖完整。
（表里每个分区都标日期，这个检查才有效；没标日期的表先补日期再跑。）
"""
import argparse
import json
import re
import sys

TAIKUAN = r"D:\Hermes\xiaonan-memory\集团\台账数据.json"


def load_rows(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)["任务"]


def month_rows(rows, month):
    return [t for t in rows if str(t.get("work_date", "")).startswith(month)]


def by_person(rows):
    out = {}
    for t in rows:
        out.setdefault(t.get("人", "?"), []).append(t)
    for k in out:
        out[k].sort(key=lambda x: x["work_date"])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--month", required=True, help="如 2026-10")
    ap.add_argument("--doc", default="", help="考核表 md 路径；给了就做覆盖核对")
    ap.add_argument("--taikuan", default=TAIKUAN)
    ap.add_argument("--dump", action="store_true", help="只打印每人日报清单")
    ap.add_argument("--daily-only", action="store_true", default=True,
                    help="只统计来源含「工作日报」的行（默认开）")
    a = ap.parse_args()

    rows = month_rows(load_rows(a.taikuan), a.month)
    if a.daily_only:
        rows = [t for t in rows if "工作日报" in str(t.get("来源", ""))]
    people = by_person(rows)

    doc = ""
    if a.doc:
        with open(a.doc, encoding="utf-8") as f:
            doc = f.read()

    total_missing = 0
    for person, items in sorted(people.items(), key=lambda kv: -len(kv[1])):
        print("\n=== %s · %d 条日报 ===" % (person, len(items)))
        missing = []
        for t in items:
            d = t["work_date"][5:]  # MM-DD
            node = t.get("节点", "")
            proj = t.get("项目", "")
            if a.dump or not a.doc:
                print("  %s | %-14s | %s" % (d, proj[:14], node[:46]))
                continue
            hit = d in doc
            flag = "  " if hit else "!!"
            print("  %s %s | %-14s | %s" % (flag, d, proj[:14], node[:46]))
            if not hit:
                missing.append(d)
        if a.doc and not a.dump:
            print("  → 覆盖 %d/%d" % (len(items) - len(missing), len(items)))
            if missing:
                total_missing += len(missing)
                print("  ✗ 表里找不到的日期：%s" % "、".join(sorted(set(missing))))

    if a.doc and not a.dump:
        print("\n合计缺失 %d 条。" % total_missing)
        if total_missing:
            print("下一步：逐条读台账原文 → 判定归属（哪个分区/是否本职外/是否已作废）→ 补进表 → 文末附「全月流水」。")
            sys.exit(0)


if __name__ == "__main__":
    main()
