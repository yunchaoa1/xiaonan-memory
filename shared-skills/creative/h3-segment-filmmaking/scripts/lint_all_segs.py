# -*- coding: utf-8 -*-
"""批量跑 h3_lint.py，按段表汇总 FAIL / WARN。

用法：
    python lint_all_segs.py [seg目录] [--segs 1:14,2:8,3:8,...]

不给 --segs 时按默认的 20 段表跑（《偏心》口径），换项目请改 SEGS 或传 --segs。

h3_lint.py 真身在：
    D:/Hermes/skills/creative/forest-laoli-h3/scripts/h3_lint.py
"""
import os
import re
import subprocess
import sys

LINT_DIR = r"D:/Hermes/skills/creative/forest-laoli-h3"
LINT = os.path.join(LINT_DIR, "scripts", "h3_lint.py")
PY = sys.executable

# 默认段表（段号:时长秒）
SEGS = {1: 14, 2: 8, 3: 8, 4: 14, 5: 7, 6: 10, 7: 8, 8: 12, 9: 7, 10: 8,
        11: 14, 12: 14, 13: 12, 14: 14, 15: 7, 16: 10, 17: 8, 18: 8,
        19: 10, 20: 8}

ASPECT = "9:16"


def parse_segs(arg):
    out = {}
    for part in arg.split(","):
        a, b = part.split(":")
        out[int(a)] = float(b)
    return out


def main():
    seg_dir = r"D:/Hermes/cache/emotion"
    segs = SEGS
    args = sys.argv[1:]
    for i, a in enumerate(args):
        if a == "--segs" and i + 1 < len(args):
            segs = parse_segs(args[i + 1])
        elif not a.startswith("--"):
            seg_dir = a

    if not os.path.exists(LINT):
        print("找不到 h3_lint.py：%s" % LINT)
        return 2

    fails, warns = [], 0
    for n in sorted(segs):
        f = os.path.join(seg_dir, "seg%02d.txt" % n)
        if not os.path.exists(f):
            print("seg%02d  缺文件" % n)
            fails.append((n, "缺文件"))
            continue
        r = subprocess.run([PY, LINT, f, "--duration", str(segs[n]),
                            "--aspect", ASPECT],
                           capture_output=True, text=True, encoding="utf-8",
                           errors="replace", cwd=LINT_DIR)
        out = (r.stdout or "") + (r.stderr or "")
        m = re.search(r"FAIL\s*(\d+)\s*｜\s*WARN\s*(\d+)", out)
        nf, nw = (int(m.group(1)), int(m.group(2))) if m else (-1, -1)
        warns += max(0, nw)
        tag = "OK  " if nf == 0 else "FAIL"
        print("seg%02d %4ss  %s  FAIL %s  WARN %s" % (n, segs[n], tag, nf, nw))
        if nf != 0:
            fails.append((n, nf))
            for line in out.splitlines():
                if line.startswith("[FAIL]"):
                    print("        " + line)

    print()
    print("合计：%d 段，FAIL %d 段，WARN %d 条" % (len(segs), len(fails), warns))
    if fails:
        print("⛔ 必须先清零 FAIL 才能投喂：", [("seg%02d" % n) for n, _ in fails])
        return 1
    print("✅ 全部 FAIL 0，可以投喂")
    return 0


if __name__ == "__main__":
    sys.exit(main())
