# -*- coding: utf-8 -*-
"""考核表 xlsx 出表自检（凡哥 2026-10-30 定的三项，缺一不可）

用法：
    python check_kaohe_xlsx.py <xlsx文件或目录> [...]

检查：
  1) 四份合计都 = 100（固定区40 + 变动区40 + 临时区20）
  2) 表内没有内部字眼（凡哥 / 例会 / 周会 / 主责 / 配合小李 / 我认 / 失职 / 过程：）
  3) 页签只有 绩效考核表 + 填表说明（不要「本月工作流水」）
  4) 每个变动区交付点写全三段：交付标准 / 交期 / 判定

退出码：0 = 全过；1 = 有问题
"""
import sys
import os
import glob

import openpyxl
from openpyxl.utils import get_column_letter

BANNED = ["凡哥", "例会", "周会", "我认", "失职", "主责", "配合小李", "配合小何", "过程："]
ALLOWED_SHEETS = {"绩效考核表", "填表说明"}


def check(path):
    """返回 (problems, total, n_items)"""
    wb = openpyxl.load_workbook(path)
    if "绩效考核表" not in wb.sheetnames:
        return [f"缺少「绩效考核表」页签，实际={wb.sheetnames}"], 0, 0
    ws = wb["绩效考核表"]

    total = 0
    items = []
    for r in range(7, ws.max_row + 1):
        v = ws.cell(r, 3).value
        if isinstance(v, (int, float)) and str(ws.cell(r, 1).value or "").isdigit():
            total += int(v)
            items.append((int(v), str(ws.cell(r, 2).value or ""), str(ws.cell(r, 4).value or "")))

    problems = []
    if total != 100:
        problems.append(f"合计 {total} ≠ 100")

    hits = []
    for r in range(1, ws.max_row + 1):
        for c in range(1, 16):
            s = str(ws.cell(r, c).value or "")
            for b in BANNED:
                if b in s:
                    hits.append(f"{get_column_letter(c)}{r}«{b}»")
    if hits:
        problems.append("内部字眼: " + ", ".join(hits[:6]))

    extra = [s for s in wb.sheetnames if s not in ALLOWED_SHEETS]
    if extra:
        problems.append(f"多余页签 {extra}（只应有 绩效考核表 + 填表说明）")

    for w, name, body in items:
        if "交期" not in name:
            continue
        if "交付标准" not in body or "判定" not in body:
            problems.append(f"「{name[:22]}」缺三段（交付标准/交期/判定）")

    return problems, total, len(items)


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    targets = []
    for a in argv:
        if os.path.isdir(a):
            targets += sorted(glob.glob(os.path.join(a, "*.xlsx")))
        else:
            targets.append(a)
    if not targets:
        print("没找到 xlsx")
        return 2

    bad = 0
    for t in targets:
        problems, total, n = check(t)
        tag = "OK " if not problems else "✗  "
        print(f"{tag}{os.path.basename(t)} | 合计 {total} | 指标 {n} 条")
        for p in problems:
            print("      -", p)
            bad += 1

    print("\n全部通过 ✓" if bad == 0 else f"\n有 {bad} 处问题，改完再发")
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
