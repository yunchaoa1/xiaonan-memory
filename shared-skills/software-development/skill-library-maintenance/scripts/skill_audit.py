#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""技能库质量体检（四维量化）—— 找出"执行不到位"的病根。

四维 = ①时效 ②描述雷同 ③缺验证章节 ④体积失控。另查空壳 / 无 frontmatter / 代码块覆盖。

用法:
    python skill_audit.py                       # 默认扫 D:\\Hermes\\skills
    python skill_audit.py --root D:/别的目录
    python skill_audit.py --top 20              # 每组最多列多少条

设计要点（踩过的坑）:
  * description 可能是 YAML 块标量（`|` / `>`）—— 直接取首行会得到 1 个字符，
    必须往下读缩进块的第一条非空内容。曾把 computer-use / logo-generator
    误报成"描述只有 1 个字"。
  * 归一化只保留中英文，前 14 字相同即视为"菜名撞车"（两块招牌鱼香肉丝）。
  * 不依赖第三方库（yaml 有则用，无则手工解析），保证任何机器能跑。
"""
import argparse
import glob
import os
import re
import sys
import time
from collections import defaultdict

VERIFY_RE = re.compile(
    r"(验证|检查|验收|自检|确认结果|预期输出|成功标准|怎么判断|"
    r"[Vv]erif|[Cc]heck|PASS|FAIL|退出码|exit\s*code)"
)
CMD_RE = re.compile(r"[A-Za-z]:[\\/]|/d/|\.exe|\.py\b|\.sh\b|\bpython\b|\bpip\b|\bnpm\b|\bcurl\b|\bffmpeg\b")


def parse_frontmatter(text):
    """返回 (frontmatter dict, body, 是否找到 frontmatter)。尽力解析，不依赖 yaml。"""
    m = re.match(r"^---\s*\r?\n(.*?)\r?\n---\s*(\r?\n|$)", text, re.S)
    if not m:
        return {}, text, False
    fm_raw = m.group(1)
    body = text[m.end():]
    fm = {}
    lines = fm_raw.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        km = re.match(r"^([A-Za-z_][\w-]*)\s*:\s*(.*)$", line)
        if not km:
            i += 1
            continue
        key, val = km.group(1), km.group(2).strip()
        # YAML 块标量: | 或 > （可能带修饰符 |- >- |+）
        if re.fullmatch(r"[|>][+-]?", val):
            i += 1
            block = []
            while i < len(lines) and (lines[i].strip() == "" or lines[i].startswith((" ", "\t"))):
                block.append(lines[i].strip())
                i += 1
            val = next((b for b in block if b), "")
        fm[key] = val.strip().strip('"').strip("'")
        i += 1
    return fm, body, True


def norm(s):
    return re.sub(r"[^\u4e00-\u9fa5A-Za-z]", "", s or "")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=r"D:\Hermes\skills", help="技能库根目录")
    ap.add_argument("--top", type=int, default=12, help="每组最多列几条")
    args = ap.parse_args()

    if not os.path.isdir(args.root):
        print("目录不存在: %s" % args.root)
        return 2

    rows = []
    for f in glob.glob(os.path.join(args.root, "**", "SKILL.md"), recursive=True):
        try:
            txt = open(f, encoding="utf-8", errors="ignore").read()
        except Exception:
            continue
        fm, body, ok = parse_frontmatter(txt)
        rows.append({
            "file": f,
            "name": fm.get("name") or os.path.basename(os.path.dirname(f)),
            "desc": fm.get("description", ""),
            "body": body,
            "has_fm": ok,
        })

    n = len(rows)
    print("=" * 62)
    print("技能库质量体检  %s" % args.root)
    print("共 %d 个技能" % n)
    print("=" * 62)

    # ---------- ① 时效 ----------
    now = time.time()
    ages = []
    for r in rows:
        try:
            ages.append(((now - os.path.getmtime(r["file"])) / 86400.0, r["name"]))
        except Exception:
            continue
    counts = {"30 天内": 0, "31-90 天": 0, "91-180 天": 0, "180 天以上": 0}
    for age, _ in ages:
        if age <= 30:
            counts["30 天内"] += 1
        elif age <= 90:
            counts["31-90 天"] += 1
        elif age <= 180:
            counts["91-180 天"] += 1
        else:
            counts["180 天以上"] += 1
    print("\n[1] 时效（多久没动过 / 代理指标，atime 不可用）")
    for k in ["30 天内", "31-90 天", "91-180 天", "180 天以上"]:
        pct = 100.0 * counts[k] / n if n else 0
        print("    %-10s %4d   %5.1f%%" % (k, counts[k], pct))
    print("    （>30 天没动的 = 吃灰候选，共 %d 个）" % (n - counts["30 天内"]))
    for age, nm in sorted(ages, reverse=True)[: max(1, args.top // 2)]:
        print("      最久: %4d 天  %s" % (age, nm))

    # ---------- ② 描述雷同 ----------
    groups = defaultdict(list)
    for r in rows:
        key = norm(r["desc"])[:14]
        if len(key) >= 8:  # 太短的描述不参与，避免误报
            groups[key].append((r["name"], r["desc"][:46]))
    dup = {k: v for k, v in groups.items() if len(v) > 1}
    print("\n[2] 描述雷同（description 前 14 字相同 = 两道鱼香肉丝）")
    if not dup:
        print("    没有发现雷同组")
    for k, v in list(dup.items())[: args.top]:
        print("    [%d 个] %s" % (len(v), " | ".join(x[0] for x in v)))

    # ---------- ③ 缺验证章节 ----------
    no_verify, short_desc, no_fm, no_code, tiny = [], [], [], [], []
    for r in rows:
        if not r["has_fm"]:
            no_fm.append(r["name"])
        if not VERIFY_RE.search(r["body"]):
            no_verify.append((r["name"], len(r["body"])))
        if r["has_fm"] and len(r["desc"]) < 20:
            short_desc.append((r["name"], r["desc"]))
        if "```" not in r["body"] and not CMD_RE.search(r["body"]):
            no_code.append((r["name"], len(r["body"])))
        if len(r["body"]) < 400:
            tiny.append((r["name"], len(r["body"])))

    print("\n[3] 缺“怎么做才算做完”（没有验证/检查章节）—— **执行不到位的直接来源**")
    print("    %d / %d 个（%.0f%%）" % (len(no_verify), n, 100.0 * len(no_verify) / n if n else 0))
    for nm, ln in sorted(no_verify, key=lambda x: -x[1])[: args.top]:
        print("      %s  (正文 %d 字)" % (nm, ln))

    # ---------- ③b 触发词 / 边界 ----------（2026-11-18 按马导视频补）
    TRIGGER_RE = re.compile(r"(凡哥说|凡哥要|凡哥提|中文触发|使用场景|什么时候用|触发条件|Use when|use when|WHEN TO USE|When to Use)")
    BOUNDARY_RE = re.compile(r"(边界|不能干|不适用|不要用于|别用于|禁止|Pitfall|pitfall|PITFALL|坑|反例|不要做|Don't use)")
    no_trigger, no_boundary = [], []
    for r in rows:
        if not TRIGGER_RE.search(r["desc"] + "\n" + r["body"][:2500]):
            no_trigger.append(r["name"])
        if not BOUNDARY_RE.search(r["body"]):
            no_boundary.append(r["name"])

    print("\n[3b] 触发词”（description 里有没有“凡哥说XX时加载”）—— 没有就调不准")
    print("    缺触发词: %d / %d 个" % (len(no_trigger), n))
    for nm in no_trigger[: args.top]:
        print("      %s" % nm)

    print("\n[3c] 边界/坑（能不能干什么、有没有 Pitfalls）—— 没有就会被滥用、重复犯错")
    print("    缺边界或坑: %d / %d 个" % (len(no_boundary), n))
    for nm in no_boundary[: args.top]:
        print("      %s" % nm)

    # ---------- ④ 体积 ----------
    lens = sorted(len(r["body"]) for r in rows)
    print("\n[4] 体积分布（正文一个字会整段进上下文）")
    if lens:
        print("    最短 %d / 中位 %d / 最长 %d" % (lens[0], lens[len(lens) // 2], lens[-1]))
    for nm, ln in sorted(((r["name"], len(r["body"])) for r in rows), key=lambda x: -x[1])[: args.top]:
        if ln > 12000:
            print("      ⚠ %s  %d 字（建议拆 references/）" % (nm, ln))

    # ---------- 其他 ----------
    print("\n[5] 其他")
    print("    无 frontmatter: %d 个 %s" % (len(no_fm), no_fm[:5] if no_fm else ""))
    print("    description 过短(<20字): %d 个 %s" % (len(short_desc), [x[0] for x in short_desc[:6]]))
    print("    正文疑似空壳(<400字): %d 个 %s" % (len(tiny), [x[0] for x in tiny[:6]]))
    print("    既无代码块也无具体命令: %d 个（方法论类技能可忽略，工具类技能要补）" % len(no_code))

    print("\n" + "=" * 62)
    print("处理建议：删（没用/被替代）· 并（雷同组）· 改（补验证/补边界/修描述）")
    print("不确定的一律归档不删；先给第一批样本让凡哥确认，再推全量。")
    print("=" * 62)
    return 0


if __name__ == "__main__":
    sys.exit(main())
