# -*- coding: utf-8 -*-
"""
mono_pipeline.py —— 白底纯色稿 → 精确单色 + 真透明 + 光学居中 + 尺寸集 + 反白版

用法
    python mono_pipeline.py <输入图 或 目录> -o <输出目录> [-c #0052d9] [-s 1024] [--pad 0.10]

例
    python mono_pipeline.py art\\*.png -o D:\\数字资产\\图片资产\\logo-X\\mono
    python mono_pipeline.py D:\\Hermes\\cache\\images -o .\\out -c #0052d9

原理（关键，别用别的办法）
    对「纯白底 + 单色图形」的图，alpha = 255 - min(R, G, B) 是**精确解**：
      纯白 (255,255,255) → 0     全透明
      饱和色 (0,82,217)  → 255   不透明
      抗锯齿混合像素      → 线性正确，边缘天然干净
    再把颜色整体刷成目标色，即得「精确目标色 + 真透明」。
    不要用「白底去背 / 容差抠图」——边缘会脏、会有残留。

适用边界（重要）
    · 源图必须是**白底纯色图形**（AI 直出 flag 稿、flat 2D 稿）。
    · 若是**材质/光效渲染稿**（渐变、发光、反光、3D 浮雕），本脚本不适用 ——
      那种稿子抠不出干净的单色剪影，正解是用 flat 2D 单色提示词重新生成
      （见 SKILL.md 铁律 ⑤）。

输出
    <名称>-mono.png    精确目标色 + 透明，居中，正方形，默认 1024
    <名称>-white.png   反白版（同一 alpha 填白），深色底专用
    scale/ 下 16/32/64/128 px 缩小实测
依赖: pillow, numpy
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image


def flatten_on_white(img: Image.Image) -> Image.Image:
    """把带 alpha 的图合成到白底上（保证公式成立）。"""
    if img.mode in ("RGBA", "LA", "P"):
        img = img.convert("RGBA")
        base = Image.new("RGBA", img.size, (255, 255, 255, 255))
        img = Image.alpha_composite(base, img)
    return img.convert("RGB")


def alpha_from_white(arr: np.ndarray) -> np.ndarray:
    """白底纯色图 → alpha 通道。255 - min(R,G,B) 是精确解。"""
    a = 255 - arr.min(axis=2)
    a[a < 12] = 0          # 去噪：极浅的底色/纸纹
    return a.astype(np.uint8)


def centered_square(alpha: np.ndarray, pad_ratio: float = 0.10) -> np.ndarray:
    """按 alpha 包围盒裁切 → 补白底成正方形 → 四周均匀留白（光学居中）。"""
    ys, xs = np.where(alpha > 8)
    if len(xs) == 0:
        raise ValueError("图上没有找到任何实心内容（全白？）")
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    a = alpha[y0:y1, x0:x1]
    h, w = a.shape
    side = int(max(h, w) * (1 + 2 * pad_ratio))
    canvas = np.zeros((side, side), dtype=np.uint8)
    oy, ox = (side - h) // 2, (side - w) // 2
    canvas[oy:oy + h, ox:ox + w] = a
    return canvas


def emit(alpha_sq: np.ndarray, out_dir: str, stem: str, color, size: int):
    def build(rgb):
        a = Image.fromarray(alpha_sq, "L").resize((size, size), Image.LANCZOS)
        solid = Image.new("RGB", (size, size), rgb)
        return Image.merge("RGBA", (*solid.split(), a))

    mono = build(color)
    white = build((255, 255, 255))
    p1 = os.path.join(out_dir, f"{stem}-mono.png")
    p2 = os.path.join(out_dir, f"{stem}-white.png")
    mono.save(p1)
    white.save(p2)

    scale_dir = os.path.join(out_dir, "scale")
    os.makedirs(scale_dir, exist_ok=True)
    made = []
    for px in (16, 32, 64, 128):
        a = Image.fromarray(alpha_sq, "L").resize((px, px), Image.LANCZOS)
        solid = Image.new("RGB", (px, px), color)
        Image.merge("RGBA", (*solid.split(), a)).save(
            os.path.join(scale_dir, f"{stem}-{px}.png"))
        made.append(px)
    return p1, p2, made


def hex_to_rgb(s: str):
    s = s.strip().lstrip("#")
    if len(s) == 3:
        s = "".join(c * 2 for c in s)
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))


def main():
    ap = argparse.ArgumentParser(description="白底纯色稿 → 精确单色 + 真透明 + 尺寸集")
    ap.add_argument("inputs", nargs="+", help="输入图或目录")
    ap.add_argument("-o", "--out", required=True, help="输出目录")
    ap.add_argument("-c", "--color", default="#0052d9", help="目标色（默认品牌主色）")
    ap.add_argument("-s", "--size", type=int, default=1024, help="主输出边长")
    ap.add_argument("--pad", type=float, default=0.10, help="四周留白比例（0.10=10%）")
    args = ap.parse_args()

    color = hex_to_rgb(args.color)
    os.makedirs(args.out, exist_ok=True)

    files = []
    for p in args.inputs:
        if os.path.isdir(p):
            files += [os.path.join(p, f) for f in sorted(os.listdir(p))
                      if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))]
        else:
            files.append(p)
    if not files:
        print("没有找到输入图"); sys.exit(1)

    ok = 0
    for f in files:
        stem = os.path.splitext(os.path.basename(f))[0]
        try:
            rgb = flatten_on_white(Image.open(f))
            a = alpha_from_white(np.asarray(rgb).astype(np.int16))
            a = centered_square(a, args.pad)
            p1, p2, scales = emit(a, args.out, stem, color, args.size)
            print(f"{stem}: OK -> {os.path.basename(p1)} / {os.path.basename(p2)} "
                  f"| scale {scales}")
            ok += 1
        except Exception as e:
            print(f"{stem}: 失败 —— {e}")
    print(f"完成 {ok}/{len(files)}  输出: {args.out}")


if __name__ == "__main__":
    main()
