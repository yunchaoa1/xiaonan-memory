# -*- coding: utf-8 -*-
"""把一段时间切成 N 段（塔罗时间轴 / 项目阶段都可用）· 只用标准库

凡哥问"到 12 月 31 日会有什么变化"这类问题，天数与段界一律脚本算，
不许心算（算错一天，段界就错，整盘节奏讲歪）。

用法:
  python date_phases.py 2026-10-19 2026-12-31 3
  python date_phases.py 2026-10-19 2026-12-31 3 --labels 清账期,加速期,收口期
"""
import argparse
import datetime
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

WEEK = ["一", "二", "三", "四", "五", "六", "日"]


def parse_date(s):
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%Y%m%d"):
        try:
            return datetime.datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    raise SystemExit("日期格式看不懂: %s（用 2026-10-19 这种）" % s)


def split(start, end, n):
    """尽量平均地把 [start, end] 切成 n 段，余数从前往后各加 1 天。"""
    total = (end - start).days + 1
    if total < n:
        raise SystemExit("总天数 %d 少于段数 %d，没法切" % (total, n))
    base, extra = divmod(total, n)
    segs, cur = [], start
    for i in range(n):
        days = base + (1 if i < extra else 0)
        segs.append((cur, cur + datetime.timedelta(days=days - 1), days))
        cur = cur + datetime.timedelta(days=days)
    return total, segs


def main():
    ap = argparse.ArgumentParser(description="按天数把区间切成 N 段")
    ap.add_argument("start")
    ap.add_argument("end")
    ap.add_argument("n", type=int, help="切几段（塔罗时间轴通常 2-3 段）")
    ap.add_argument("--labels", default="", help="逗号分隔的段名，例如 清账期,加速期,收口期")
    args = ap.parse_args()

    start, end = parse_date(args.start), parse_date(args.end)
    if end < start:
        raise SystemExit("结束日期早于开始日期")
    total, segs = split(start, end, args.n)
    labels = [x.strip() for x in args.labels.split(",") if x.strip()]

    print("区间: %s ~ %s" % (start, end))
    print("总天数(含首尾): %d 天  |  切成 %d 段" % (total, args.n))
    for i, (s, e, d) in enumerate(segs):
        name = labels[i] if i < len(labels) else "第%d段" % (i + 1)
        print("  %s: %s ~ %s  %d 天  (周%s ~ 周%s)" % (
            name, s, e, d, WEEK[s.weekday()], WEEK[e.weekday()]))
    print("\n每天都要写的两件事：① 该干什么 ② 什么时候收手（给可判断的信号）")


if __name__ == "__main__":
    main()
