#!/usr/bin/env python3
"""
SVG -> PNG converter.

Backend order (first one that works wins):
  1. resvg_py  -- single-binary Rust renderer, no native deps. VERIFIED on this
                  Windows box (cairosvg fails here: libcairo-2.dll missing).
  2. cairosvg  -- used when libcairo is present (Linux/macOS, most dev machines).

Usage:
  python scripts/svg_to_png.py logo.svg -o logo.png -w 1024 -H 1024
"""

import sys
import argparse
from pathlib import Path

DEFAULT_W = 1024
DEFAULT_H = 1024


def _via_resvg(svg_text: str, png_path: str, width: int, height: int) -> bool:
    try:
        import resvg_py
    except ImportError:
        return False
    try:
        data = resvg_py.svg_to_bytes(svg_string=svg_text, width=width, height=height)
        if not isinstance(data, (bytes, bytearray)):
            return False
        with open(png_path, "wb") as f:
            f.write(data)
        print(f"[resvg-py] OK  {width}x{height} -> {png_path}")
        return True
    except Exception as e:
        print(f"[resvg-py] failed: {type(e).__name__}: {e}")
        return False


def _via_cairosvg(svg_path: str, png_path: str, width: int, height: int) -> bool:
    try:
        import cairosvg
    except ImportError:
        return False
    try:
        cairosvg.svg2png(url=svg_path, write_to=png_path,
                         output_width=width, output_height=height)
        print(f"[cairosvg] OK  {width}x{height} -> {png_path}")
        return True
    except Exception as e:
        print(f"[cairosvg] failed: {type(e).__name__}: {e}")
        return False


def svg_to_png(svg_path: str, png_path: str, width: int = DEFAULT_W,
               height: int = DEFAULT_H) -> bool:
    p = Path(svg_path)
    if not p.exists():
        print(f"Error: SVG file not found: {svg_path}")
        return False
    svg_text = p.read_text(encoding="utf-8")

    if _via_resvg(svg_text, png_path, width, height):
        return True
    if _via_cairosvg(svg_path, png_path, width, height):
        return True

    print("Error: no working SVG renderer.")
    print("  Fix (Windows / no cairo):  pip install resvg-py")
    print("  Fix (has libcairo):        pip install cairosvg")
    return False


def main():
    ap = argparse.ArgumentParser(description="Convert SVG to PNG (resvg-py / cairosvg)")
    ap.add_argument("svg_file", help="Path to SVG file")
    ap.add_argument("--output", "-o", help="Output PNG path (default: same name .png)")
    ap.add_argument("--width", "-w", type=int, default=DEFAULT_W)
    ap.add_argument("--height", "-H", type=int, default=DEFAULT_H)
    a = ap.parse_args()

    out = a.output or str(Path(a.svg_file).with_suffix(".png"))
    sys.exit(0 if svg_to_png(a.svg_file, out, a.width, a.height) else 1)


if __name__ == "__main__":
    main()
