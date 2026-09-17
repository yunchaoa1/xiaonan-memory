#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""锁标排版器：标志 PNG + 中文标准字 + 全大写 letter-spaced 英文副标 → 横版/竖版锁标。

用法:
    python lockup.py --mark mark.png --name 天使OPC数字社区 \
        --sub "ANGEL OPC DIGITAL COMMUNITY" \
        --bg "#FFFFFF" --name-color "#0A1533" --sub-color "#7A8494" \
        --out lockup-h.png

    # 竖版 / 深底反白
    python lockup.py --mark mark-white.png --name 天使OPC数字社区 \
        --sub "ANGEL OPC DIGITAL COMMUNITY" --vertical \
        --bg "#0A1533" --name-color "#FFFFFF" --sub-color "#9FB2CC" \
        --out lockup-v.png

比例基准（实测协调，--h 是标志高度）:
    中文标准字 ≈ 0.57H  英文副标 ≈ 0.16H  英文副标字距 ≈ 0.33em  标志↔文字间距 ≈ 0.30H
注意:
    小字标签一律用思源黑体（Noto Sans SC）——Source Han Serif 缺 U+00B7(·) 会出方框。
    标志 PNG 必须是透明底（RGBA），否则贴图会带一块底色。
"""
import argparse
import os

from PIL import Image, ImageDraw, ImageFont

FONT_BOLD = [
    r"C:\Windows\Fonts\Noto Sans SC Bold (TrueType).otf",
    r"C:\Windows\Fonts\msyhbd.ttc",
    r"C:\Windows\Fonts\simhei.ttf",
]
FONT_MED = [
    r"C:\Windows\Fonts\Noto Sans SC Medium (TrueType).otf",
    r"C:\Windows\Fonts\msyh.ttc",
    r"C:\Windows\Fonts\simhei.ttf",
]


def load_font(candidates, size):
    for p in candidates:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    raise SystemExit("找不到可用中文字体，候选: %s" % candidates)


def tracked(draw, xy, text, font, fill, track):
    """逐字绘制 + 字距（中文字标必须这样排，整串直接写会挤在一起）。"""
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        x += draw.textlength(ch, font=font) + track
    return x


def tracked_width(draw, text, font, track):
    if not text:
        return 0
    return sum(draw.textlength(ch, font=font) for ch in text) + track * (len(text) - 1)


def make(mark_path, name, sub, bg, name_color, sub_color, out,
         vertical=False, mark_h=288):
    m = Image.open(mark_path).convert("RGBA")
    m = m.resize((max(1, int(m.width * mark_h / m.height)), int(mark_h)), Image.LANCZOS)
    H = int(mark_h)

    bh = int(H * 0.57)          # 中文标准字字号
    sh = int(H * 0.16)          # 英文副标字号
    tr = int(sh * 0.33)         # 英文副标字距
    nt = int(bh * 0.02)         # 中文字距
    gap_mark = int(H * 0.30)    # 标志 ↔ 文字
    gap_line = int(H * 0.10)    # 中文行 ↔ 英文行
    pad = int(H * 0.34)         # 外边距

    f_name = load_font(FONT_BOLD, bh)
    f_sub = load_font(FONT_MED, sh)
    # 量文字必须先有一个 draw 对象（不能反过来）
    tmp = ImageDraw.Draw(Image.new("RGB", (8, 8)))

    nw = tracked_width(tmp, name, f_name, nt)
    sw = tracked_width(tmp, sub, f_sub, tr)
    tw = max(nw, sw)
    block_h = bh + gap_line + sh

    if vertical:
        W = int(max(m.width, tw) + pad * 2)
        Hc = int(pad * 2 + m.height + gap_mark + block_h)
    else:
        W = int(pad * 2 + m.width + gap_mark + tw)
        Hc = int(pad * 2 + max(m.height, block_h))

    img = Image.new("RGB", (W, Hc), bg)
    d = ImageDraw.Draw(img)

    if vertical:
        img.paste(m, ((W - m.width) // 2, pad), m)
        ty = pad + m.height + gap_mark
        tracked(d, ((W - nw) // 2, ty), name, f_name, name_color, nt)
        tracked(d, ((W - sw) // 2, ty + bh + gap_line), sub, f_sub, sub_color, tr)
    else:
        img.paste(m, (pad, (Hc - m.height) // 2), m)
        by = (Hc - block_h) // 2
        tx = pad + m.width + gap_mark
        tracked(d, (tx, by), name, f_name, name_color, nt)
        tracked(d, (tx, by + bh + gap_line), sub, f_sub, sub_color, tr)

    img.save(out)
    return img.size


def main():
    ap = argparse.ArgumentParser(description="品牌锁标排版器")
    ap.add_argument("--mark", required=True, help="标志 PNG（透明底）")
    ap.add_argument("--name", required=True, help="中文标准字，如 天使OPC数字社区")
    ap.add_argument("--sub", default="", help="英文副标（会自动转大写）")
    ap.add_argument("--bg", default="#FFFFFF", help="背景色，如 #FFFFFF 或 #0A1533")
    ap.add_argument("--name-color", default="#0A1533")
    ap.add_argument("--sub-color", default="#7A8494")
    ap.add_argument("--out", required=True, help="输出 PNG 路径")
    ap.add_argument("--vertical", action="store_true", help="竖版（标志在上、文字在下）")
    ap.add_argument("--h", type=int, default=288, help="标志高度（px），默认 288")
    a = ap.parse_args()

    size = make(a.mark, a.name, a.sub.upper(), a.bg, a.name_color, a.sub_color,
                a.out, vertical=a.vertical, mark_h=a.h)
    print("OK %s %dx%d" % (a.out, size[0], size[1]))


if __name__ == "__main__":
    main()
