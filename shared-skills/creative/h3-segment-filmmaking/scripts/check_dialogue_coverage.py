# -*- coding: utf-8 -*-
"""台词覆盖核对：原稿每一句是否都进了提示词的 <d>[Chinese] …</d>

用法：
    python check_dialogue_coverage.py <台词原稿.md> <seg目录>

为什么要它：长台词按技能规则要拆成两次开口。拆完忘了补镜，台词就静默丢了
（2026-12-19《偏心》拆完丢了 11 句，人眼查三遍都没看出来）。

退出码：0 = 全覆盖；1 = 有缺句。
"""
import io
import os
import re
import sys
import glob

PUNCT = "，。？！、；：\"'“”‘’…—·　 \t\n「」『』（）().．·・-－"


def norm(s):
    """去掉所有标点和空白，只留字。"""
    return "".join(ch for ch in s if ch not in PUNCT)


def read_source_lines(path):
    """从台词稿里抽出所有引号内的台词。

    跳过两类非台词：① 以 > 开头的引用/规则说明行（常拿「她说」举例，会被误当台词）；
    ② 标题行。2026-11-22 实测：《偏心》台词稿的规则行里写了"我告诉她"，
    被当成台词报缺句，属误报，故加此过滤。
    """
    txt = io.open(path, encoding="utf-8").read()
    text_lines = []
    for ln in txt.splitlines():
        st = ln.strip()
        if st.startswith(">") or st.startswith("#"):
            continue
        text_lines.append(ln)
    lines = re.findall(r"[“\"]([^”\"]{1,200})[”\"]", "\n".join(text_lines))
    out = []
    for ln in lines:
        ln = ln.strip()
        if norm(ln):
            out.append(ln)
    return out


def read_seg_dialogue(seg_dir):
    """收集目录下所有 seg*.txt 的 <d> 块，按文件名排序。"""
    files = sorted(glob.glob(os.path.join(seg_dir, "seg*.txt")))
    per_seg = {}
    for f in files:
        s = io.open(f, encoding="utf-8").read()
        blocks = re.findall(r"<d>\[Chinese\]\s*(.+?)</d>", s, re.S)
        per_seg[os.path.basename(f)] = [b.strip() for b in blocks]
    return per_seg


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 1
    src, seg_dir = sys.argv[1], sys.argv[2]

    orig = read_source_lines(src)
    per_seg = read_seg_dialogue(seg_dir)
    written = [b for blocks in per_seg.values() for b in blocks]
    joined = norm("".join(written))

    print("原稿 %d 句 ｜ 提示词 %d 处 <d> ｜ 目录 %s" % (len(orig), len(written), seg_dir))
    print()

    # 逐句核对：整句能拼出来，或它被拆成的碎片全都在
    missing = []
    for line in orig:
        n = norm(line)
        if not n:
            continue
        if n in joined:
            continue
        # 拆句检测：句子的每个 3 字片段都能在正文里找到 → 视为已覆盖
        chunks = [n[i:i + 3] for i in range(0, max(1, len(n) - 2), 3)]
        if chunks and all(c in joined for c in chunks):
            continue
        missing.append(line)

    if missing:
        print("⚠️  缺 %d 句：" % len(missing))
        for m in missing:
            print("   - " + m)
    else:
        print("✅ 原稿每一句都在提示词里")

    # 每段明细（<d> 数 vs 镜数）
    print()
    print("=== 每段 ===")
    bad = []
    for name in sorted(per_seg):
        s = io.open(os.path.join(seg_dir, name), encoding="utf-8").read()
        shots = len(re.findall(r"\[Shot \d+\]", s))
        nd = len(per_seg[name])
        flag = ""
        if nd == 0:
            flag = "  ← 整段没有台词，确认是留白段？"
            bad.append(name)
        elif nd > shots:
            flag = "  ← <d> 比镜数多，有一镜塞了两句"
            bad.append(name)
        elif shots - nd > 1:
            flag = "  ← 镜比台词多 2 个以上，可能漏写台词"
            bad.append(name)
        print("  %-12s %2d 镜  %2d 句%s" % (name, shots, nd, flag))

    # 字数与填充率速算（段时长需另传，这里只报总字数和句数）
    chars = sum(len(norm(b)) for b in written)
    print()
    print("台词合计 %d 句 / %d 字 → 纯说话约 %.0f 秒（3.3 字/秒）"
          % (len(written), chars, chars / 3.3))
    print("按 85%% 填充率，段总时长应约 %.0f 秒" % (chars / 3.3 / 0.85))
    print("按 20 句/分钟基准，片长不宜超过 %.1f 分钟" % (len(written) / 20.0))

    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
