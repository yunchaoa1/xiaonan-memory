#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
台词节奏检查：用《茶馆》第一幕的人写对白做基准，量一集剧本的台词节奏像不像人说的。

为什么用《茶馆》：老舍第一幕对白全是三教九流，句长参差、虚词密、有没说完的半句。
它的统计特征就是"人话"的统计特征，不是审美偏好。

基准（2026-11-17 从维基文库《茶馆》第一幕 400 句实测）：
  平均句长 14.0 字 ｜ 句长标准差 9.1 ｜ 8 字以下短句 30% ｜ 25 字以上长句 12%

用法：
  python check_dialogue_rhythm.py 剧本.md
  python check_dialogue_rhythm.py 剧本.md --verbose
"""
import re
import sys
import statistics
from pathlib import Path

# 人写的基准
BASE = {
    "mean": 14.0,        # 平均句长
    "stdev": 9.1,        # 句长标准差（参差度）
    "short_ratio": 0.30, # 8 字以下短句占比
    "long_ratio": 0.12,  # 25 字以上长句占比
}

# 判定线（不是等于基准，而是不许低于它的某个比例）
FLOOR = {
    "mean": 11.0,        # 平均句长不低于 11 字
    "stdev": 6.5,        # 参差度不低于 6.5
    "short_ratio_max": 0.42,  # 8 字以下短句不超过 42%
    "long_ratio_min": 0.06,   # 25 字以上长句至少 6%
}

QUOTE = re.compile(r'[“"]([^”"\n]{2,})[”"]')


def extract_dialogue(path: Path) -> list:
    """抽出所有引号里的台词，按句号问号感叹号省略号切句。"""
    text = path.read_text(encoding="utf-8")
    # 去掉创作说明区（> 开头）和表格（| 开头）
    lines = [l for l in text.split("\n") if not l.strip().startswith((">", "|"))]
    text = "\n".join(lines)
    quotes = QUOTE.findall(text)
    sents = []
    for q in quotes:
        for s in re.split(r'[。！？…]+', q):
            s = s.strip(" ，、")
            if len(s) >= 2:
                sents.append(s)
    return sents


def check(path: Path, verbose=False) -> int:
    sents = extract_dialogue(path)
    if len(sents) < 12:
        print(f"⚠  {path.name}：只抽到 {len(sents)} 句台词，样本太小，判断不可靠")
        return 0

    lens = [len(s) for s in sents]
    mean = statistics.mean(lens)
    stdev = statistics.pstdev(lens)
    short = sum(1 for n in lens if n <= 8) / len(lens)
    long_ = sum(1 for n in lens if n >= 25) / len(lens)

    fails = []
    if mean < FLOOR["mean"]:
        fails.append(f"平均句长 {mean:.1f} 字，低于 {FLOOR['mean']}。整集台词太短促，像发报。")
    if stdev < FLOOR["stdev"]:
        fails.append(f"句长参差度 {stdev:.1f}，低于 {FLOOR['stdev']}。句子长短太整齐，没有情绪起伏。")
    if short > FLOOR["short_ratio_max"]:
        fails.append(f"8 字以下短句占 {short*100:.0f}%，超过 {FLOOR['short_ratio_max']*100:.0f}%。短句过多。")
    if long_ < FLOOR["long_ratio_min"]:
        fails.append(f"25 字以上长句只占 {long_*100:.0f}%，低于 {FLOOR['long_ratio_min']*100:.0f}%。缺情绪上来时一口气说完的话。")

    head = "✅" if not fails else "❌"
    print(f"{head} {path.name}：{len(sents)} 句 · 平均 {mean:.1f} 字 · 参差 {stdev:.1f} "
          f"· 短句 {short*100:.0f}% · 长句 {long_*100:.0f}%")

    if verbose:
        print(f"   人写基准：《茶馆》第一幕 平均 {BASE['mean']} 字 · 参差 {BASE['stdev']} "
              f"· 短句 {BASE['short_ratio']*100:.0f}% · 长句 {BASE['long_ratio']*100:.0f}%")
        print("   最长的三句：")
        for s in sorted(sents, key=len, reverse=True)[:3]:
            print(f"     [{len(s)}字] {s}")

    for f in fails:
        print(f"   → {f}")

    if fails:
        print("   改法：找出全集情绪最顶点的那一处，让她把话说长——一口气说完、带重复、带没说完的半句。"
              "长句一定要落在有人急了、怕了、豁出去的那一拍上，不能放在平铺直叙的地方。")

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
