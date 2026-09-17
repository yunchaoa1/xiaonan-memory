#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
render_qc.py —— 品牌标志渲染 + 质检工具（可复用）

用途：把「渲染 SVG → 光学居中归一化 → 拼版自检 → HTML 交付页截图核对」
四件事固化成一条命令，避免每次手写重复代码、避免交未核对的成品。

依赖：  pip install resvg-py pillow
       （本机 cairosvg 因缺 libcairo-2.dll 不可用，统一用 resvg-py）

用法：
    python render_qc.py center  in.svg out.svg [pad]      # 光学居中归一化
    python render_qc.py png     in.svg out.png [px]       # 渲染透明 PNG
    python render_qc.py sheet   "a.png,b.png" out.png [cols]   # 拼版（白底/深底两张）
    python render_qc.py shot    page.html out.png [w] [h]      # Chrome 无头截图
"""
import io
import os
import subprocess
import sys
import urllib.parse

import resvg_py
from PIL import Image, ImageDraw, ImageFont

CHROME_CANDIDATES = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
]
CJK_FONT = r"C:\Windows\Fonts\msyh.ttc"


# ---------------------------------------------------------------- 渲染
def render(svg_text, px=1024):
    """SVG 文本 → RGBA PIL Image（透明背景）。"""
    raw = resvg_py.svg_to_bytes(svg_string=svg_text, width=px, height=px)
    return Image.open(io.BytesIO(raw)).convert("RGBA")


def render_file(svg_path, out_png, px=1024):
    with open(svg_path, encoding="utf-8") as f:
        img = render(f.read(), px)
    img.save(out_png)
    return out_png


# ------------------------------------------------- 光学居中归一化
def optical_center(svg_text, pad=6.0, probe=512):
    """
    读 alpha 包围盒 → 反算 viewBox(0 0 100 100) 平移量 → 把内容包进 translate 组。
    注意：多色/多层稿按【所有层的并集】居中（alpha 通道天然是并集）。

    返回 (新 svg 文本, (dx, dy))。
    """
    img = render(svg_text, probe)
    bbox = img.getchannel("A").getbbox()  # (l, t, r, b)
    if bbox is None:
        return svg_text, (0.0, 0.0)
    scale = 100.0 / probe
    l, t, r, b = [v * scale for v in bbox]
    cx, cy = (l + r) / 2.0, (t + b) / 2.0
    dx, dy = 50.0 - cx, 50.0 - cy
    # 内容包进 <svg> 内部（保留外层 viewBox）
    head_end = svg_text.index(">") + 1
    inner_end = svg_text.rindex("</svg>")
    inner = svg_text[head_end:inner_end]
    wrapped = (
        svg_text[:head_end]
        + f'<g transform="translate({dx:.3f} {dy:.3f})">{inner}</g>'
        + svg_text[inner_end:]
    )
    return wrapped, (dx, dy)


# ---------------------------------------------------------------- 拼版
def contact_sheet(png_paths, out_png, cols=4, cell=300, bg="white", labels=None):
    """把若干透明 PNG 拼成一张核对图（白底 + 深底两张）。"""
    rows = (len(png_paths) + cols - 1) // cols
    made = []
    for suffix, background in (("", bg), ("_dark", "#0A1533")):
        sheet = Image.new("RGB", (cell * cols, cell * rows), background)
        d = ImageDraw.Draw(sheet)
        try:
            font = ImageFont.truetype(CJK_FONT, 20)
        except OSError:
            font = None
        for i, p in enumerate(png_paths):
            im = Image.open(p).convert("RGBA")
            im.thumbnail((int(cell * 0.72), int(cell * 0.72)))
            x = (i % cols) * cell + (cell - im.width) // 2
            y = (i // cols) * cell + (cell - im.height) // 2
            sheet.paste(im, (x, y), im)
            if labels:
                d.text(((i % cols) * cell + 8, (i // cols) * cell + 8),
                       labels[i], fill=("#111" if suffix == "" else "#EEE"), font=font)
        path = out_png.replace(".png", f"{suffix}.png")
        sheet.save(path)
        made.append(path)
    return made


# ----------------------------------------------------- HTML 交付页截图
def html_screenshot(html_path, out_png, width=1400, height=1800):
    """
    用 Chrome/Edge 无头模式截图核对 HTML 交付页。
    路径含中文必须 percent-encode，否则 Chrome 读不到。
    """
    url = "file:///" + urllib.parse.quote(os.path.abspath(html_path).replace("\\", "/"))
    for exe in CHROME_CANDIDATES:
        if os.path.exists(exe):
            cmd = [exe, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                   f"--window-size={width},{height}", f"--screenshot={out_png}", url]
            subprocess.run(cmd, capture_output=True, timeout=180)
            if os.path.exists(out_png):
                return out_png
    raise RuntimeError("未找到 Chrome/Edge，无法截图核对")


# ---------------------------------------------------------------- CLI
def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 1
    mode = argv[1]
    if mode == "center" and len(argv) >= 4:
        src = open(argv[2], encoding="utf-8").read()
        new, (dx, dy) = optical_center(src, float(argv[4]) if len(argv) > 4 else 6.0)
        open(argv[3], "w", encoding="utf-8").write(new)
        print(f"光学居中平移 dx={dx:.2f} dy={dy:.2f} -> {argv[3]}")
    elif mode == "png" and len(argv) >= 4:
        print(render_file(argv[2], argv[3], int(argv[4]) if len(argv) > 4 else 1024))
    elif mode == "sheet" and len(argv) >= 4:
        paths = [p.strip() for p in argv[2].split(",") if p.strip()]
        for p in contact_sheet(paths, argv[3],
                               int(argv[4]) if len(argv) > 4 else 4):
            print(p)
    elif mode == "shot" and len(argv) >= 4:
        print(html_screenshot(argv[2], argv[3],
                              int(argv[4]) if len(argv) > 4 else 1400,
                              int(argv[5]) if len(argv) > 5 else 1800))
    else:
        print(__doc__)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
