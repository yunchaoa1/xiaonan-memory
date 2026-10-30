# -*- coding: utf-8 -*-
"""塔罗抽牌器 · 真随机 + 留凭证（只用标准库）

凡哥的牌由这个脚本抽：78 张标准韦特牌库，不重复，正逆位各 50%，
抽完把结果写进凭证文件，随时可核。

用法:
  python draw_tarot.py --spread five-career --topic 事业
  python draw_tarot.py --spread three --topic 感情
  python draw_tarot.py --spread one --topic 今天 --no-file
  python draw_tarot.py --spread five-career --topic 事业 --seed 42   # 复现同一手牌
"""
import argparse
import datetime
import hashlib
import os
import random
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

MAJOR = [
    "愚者", "魔术师", "女祭司", "皇后", "皇帝", "教皇", "恋人", "战车",
    "力量", "隐者", "命运之轮", "正义", "倒吊人", "死神", "节制", "恶魔",
    "高塔", "星星", "月亮", "太阳", "审判", "世界",
]
SUITS = ["权杖", "圣杯", "宝剑", "星币"]
RANKS = ["Ace", "2", "3", "4", "5", "6", "7", "8", "9", "10",
         "侍从", "骑士", "王后", "国王"]

SPREADS = {
    "one": ["这一张"],
    "three": ["过去", "现在", "未来"],
    "three-alt": ["现状", "障碍", "建议"],
    "five-career": ["现在的底子", "推你的力量", "绊住的阻力", "机遇", "落点"],
}

DEFAULT_DIR = r"D:\Documents\我的文档\05_个人\塔罗"


def build_deck():
    """22 张大阿卡纳 + 56 张小阿卡纳 = 78 张，编号 1-78。"""
    deck = []
    for i, name in enumerate(MAJOR, start=1):
        deck.append({"no": i, "组": "大阿卡纳", "名": name})
    no = 23
    for suit in SUITS:
        for rank in RANKS:
            deck.append({"no": no, "组": "小阿卡纳", "名": suit + rank})
            no += 1
    return deck


def draw(cards_n, seed=None):
    deck = build_deck()
    rng = random.SystemRandom() if seed is None else random.Random(seed)
    picks = rng.sample(deck, cards_n)          # 不重复
    out = []
    for card in picks:
        upright = rng.choice([True, False])     # 正逆位各 50%
        out.append({**card, "位": "正位" if upright else "逆位"})
    return out


def fingerprint(picks):
    raw = "|".join(f'{c["no"]}:{c["位"]}' for c in picks)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def main():
    ap = argparse.ArgumentParser(description="塔罗抽牌（真随机 + 凭证）")
    ap.add_argument("--spread", default="three", choices=sorted(SPREADS),
                    help="牌阵: " + " / ".join(sorted(SPREADS)))
    ap.add_argument("--topic", default="未命名", help="主题，例如 事业 / 感情 / 今天")
    ap.add_argument("--seed", type=int, default=None, help="固定种子（复现用，默认真随机）")
    ap.add_argument("--outdir", default=DEFAULT_DIR, help="凭证目录")
    ap.add_argument("--no-file", action="store_true", help="不写凭证文件")
    args = ap.parse_args()

    positions = SPREADS[args.spread]
    picks = draw(len(positions), seed=args.seed)
    now = datetime.datetime.now()

    src = "SystemRandom（真随机）" if args.seed is None else "Random(seed=%d)" % args.seed
    head = "%s | 牌阵 %s | %s" % (args.topic, args.spread, now.strftime("%Y-%m-%d %H:%M:%S"))

    lines = []
    lines.append("=" * 56)
    lines.append("主题: %s" % args.topic)
    lines.append("牌阵: %s（%d 张）" % (args.spread, len(positions)))
    lines.append("时间: %s" % now.strftime("%Y-%m-%d %H:%M:%S %A"))
    lines.append("随机源: %s" % src)
    lines.append("牌库: 标准韦特 78 张（大阿卡纳 22 + 小阿卡纳 56）")
    lines.append("=" * 56)
    for i, (pos, card) in enumerate(zip(positions, picks), start=1):
        lines.append("%d %-8s | No.%-2d %-6s %-6s | %s" % (
            i, pos, card["no"], card["组"], card["名"], card["位"]))
    lines.append("-" * 56)
    lines.append("清单指纹: %s" % fingerprint(picks))
    if args.seed is not None:
        lines.append("复现命令: --spread %s --topic %s --seed %d" % (
            args.spread, args.topic, args.seed))

    body = "\n".join(lines)
    print(body)

    if not args.no_file:
        try:
            os.makedirs(args.outdir, exist_ok=True)
            fname = "%s_%s_抽牌凭证.txt" % (now.strftime("%Y-%m-%d"), args.topic)
            path = os.path.join(args.outdir, fname)
            with open(path, "a", encoding="utf-8") as f:
                f.write(body + "\n\n")
            print("\n凭证已存: %s" % path)
        except Exception as e:              # 目录不可写也别影响解读
            print("\n[警告] 凭证写入失败: %s" % e)


if __name__ == "__main__":
    main()
