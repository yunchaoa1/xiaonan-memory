#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
语义完整度检查：查的不是句子长短，是每一句话语义碎不碎。

为什么要这个：
  "表压在箱底，一叠，橡皮筋松了，勒不住，纸边发黄" —— 这句不算长，也谈不上短，
  毛病是五个无主语的短语堆在一起，缺"谁、为什么"，语义残缺。
  对照人写的："她要找的打分表在箱子最底层，有整整一叠纸。绑纸的橡皮筋松了，
  应该是放久了没了弹性，纸边也微微泛黄。"
  —— 每段都是一个完整语义块，还带一句"为什么"。

三条可算的指标（都指向同一件事：这句话能不能回答"谁、做了什么、为什么这样"）：

  1. 碎段率   —— 按逗号顿号切段，长度≤4字的段占多少。碎段堆叠＝只报状态不报因果。
  2. 无主语段 —— 每个分句里有没有出现人名/代词。没有＝不知道在说谁。
  3. 推断词   —— "应该/怕是/看样子/原来/看来/估摸/多半/像是"这类词。
                 人看见东西会琢磨为什么，机器只报"是什么样"。

基准（《茶馆》第一幕 + 手写对照句实测）：
  碎段率 ≈ 25% 以下 ｜ 推断词出现在 ≥15% 的句子里

用法：
  python check_semantic_completeness.py 剧本.md
  python check_semantic_completeness.py 剧本.md --verbose
"""
import re
import sys
from pathlib import Path

# 人物指示词（判断有没有主语）
SUBJ = re.compile(r'(我|你|您|他|她|它|咱|自己|[一-龥]{2,3}?(?:说|道))')
# 推断词：人在现场"琢磨"的痕迹
INFER = re.compile(r'(应该|怕是|看样子|原来|看来|估摸|多半|像是|八成|想必|横竖|总归|说不定|敢情|难怪)')
# 动作行前缀
ACTION = re.compile(r'^\s*(△|〔|\[)')

FLOOR = {
    "frag_ratio_max": 0.40,   # 碎段率上限
    "infer_ratio_min": 0.10,  # 带推断词的句子占比下限
}

# 只查动作/场景描述行（△ 开头），台词不算——台词该短就短
def extract_action_lines(path: Path):
    text = path.read_text(encoding="utf-8")
    out = []
    for l in text.split("\n"):
        s = l.strip()
        if s.startswith(">"):
            continue
        if ACTION.match(s):
            s = ACTION.sub("", s).strip()
            if len(s) >= 4:
                out.append(s)
    return out


def analyze(lines):
    """返回 (碎段率, 无主语段率, 带推断词的句子比例, 明细)"""
    frag_total = 0
    frag_count = 0
    subj_missing = 0
    subj_total = 0
    infer_sent = 0
    details = []

    for line in lines:
        # 按句子切
        sents = [s.strip() for s in re.split(r'[。！？；…]', line) if s.strip()]
        line_has_infer = bool(INFER.search(line))
        if line_has_infer:
            infer_sent += 1
        for s in sents:
            segs = [g.strip() for g in re.split(r'[，、,]', s) if g.strip()]
            for g in segs:
                frag_total += 1
                if len(g) <= 4:
                    frag_count += 1
            subj_total += 1
            if not SUBJ.search(s):
                subj_missing += 1
        if len(line) > 4:
            details.append((line, len(sents), sum(len(g) for g in re.split(r'[，、,]', line) if g.strip()) / max(1, len([g for g in re.split(r'[，、,]', line) if g.strip()])), line_has_infer))

    frag_ratio = frag_count / frag_total if frag_total else 0
    subj_ratio = subj_missing / subj_total if subj_total else 0
    infer_ratio = infer_sent / len(lines) if lines else 0
    return frag_ratio, subj_ratio, infer_ratio, details


def check(path: Path, verbose=False) -> int:
    lines = extract_action_lines(path)
    if len(lines) < 8:
        print(f"⚠  {path.name}：只抽到 {len(lines)} 行动作描述，样本太小，判断不可靠")
        return 0

    frag, subj, infer, details = analyze(lines)
    fails = []
    if frag > FLOOR["frag_ratio_max"]:
        fails.append(f"碎段率 {frag*100:.0f}%（每 4 字一段的碎片占比），超过 {FLOOR['frag_ratio_max']*100:.0f}%。"
                     f"动作描述在报状态，不在讲因果。")
    if infer < FLOOR["infer_ratio_min"]:
        fails.append(f"带推断词的描写只占 {infer*100:.0f}%，低于 {FLOOR['infer_ratio_min']*100:.0f}%。"
                     f"人看见东西会琢磨为什么，这里全是'是什么样'。")

    head = "✅" if not fails else "❌"
    print(f"{head} {path.name}：{len(lines)} 行动作 · 碎段 {frag*100:.0f}% · "
          f"缺主语分句 {subj*100:.0f}% · 带推断 {infer*100:.0f}%")

    if verbose:
        print("   最碎的五句（碎段率最高，最像 AI）：")
        worst = sorted(details, key=lambda d: d[2])[:5]
        for line, n, avg, has_infer in worst:
            print(f"     均段 {avg:.1f} 字 {'[有推断]' if has_infer else '[无推断]'}｜{line[:60]}")

    for f in fails:
        print(f"   → {f}")

    if fails:
        print("   改法：每个分句补回主语，每处细节后跟一句人物自己的判断"
              "（用'应该/怕是/看样子/原来'带出来）。不是把句子拉长，是把'谁、为什么'补回去。")

    return 0 if not fails else 1


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    verbose = "--verbose" in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    rc = 0
    for p in args:
        rc |= check(Path(p), verbose)
    sys.exit(rc)
