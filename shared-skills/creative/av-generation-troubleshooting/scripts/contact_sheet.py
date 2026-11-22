#!/usr/bin/env python
"""
成片联系表（contact sheet）生成器 —— 验收长片用，别只抽几帧。

用法:
    python contact_sheet.py <视频路径> [--segs 4] [--step 0.5] [--out D:/Hermes/cache]

输出:
    每段一张 sheet_segN.jpg（4 列网格，每 step 秒取一帧，宽 320）

为什么要用:
    单帧只能看出"这一帧姿势对不对"，看不出"他有没有在动""动作连不连贯"
    "后半段是不是僵住了"。实测过一次只抽 4 帧就下结论"全部成功"，结论是错的。

看什么:
    1. 哪几秒开始两个人都不动了   -> 单镜有效动作窗口只有 5-7 秒
    2. 动作是不是变成比划         -> 写法问题（只写了动词没写物理链）
    3. 场景有没有中途换           -> 正文漏引 Subject，参考图白挂
    4. 段缝接不接得上             -> 上一段末帧姿势 vs 下一段首帧
    5. 有没有多出来的人/手         -> 反光面 / 贴身缠斗
"""
import argparse
import os
import sys

import cv2
import numpy as np


def build(path, segs=4, step=0.5, out_dir=None, tile_w=320, cols=4):
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        raise SystemExit(f"打不开视频: {path}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 24.0
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    dur = total / fps
    print(f"fps {fps:.1f}  帧数 {total}  时长 {dur:.2f}s")

    seg_len = dur / segs
    written = []

    for s in range(segs):
        t0 = s * seg_len
        t1 = (s + 1) * seg_len
        tiles = []
        t = t0
        while t < t1:
            cap.set(cv2.CAP_PROP_POS_FRAMES, int(t * fps))
            ok, fr = cap.read()
            if ok:
                h, w = fr.shape[:2]
                tiles.append(cv2.resize(fr, (tile_w, int(tile_w * h / w))))
            t += step

        if not tiles:
            continue

        rows = (len(tiles) + cols - 1) // cols
        th, tw = tiles[0].shape[:2]
        sheet = np.zeros((rows * th, cols * tw, 3), np.uint8)
        for i, tile in enumerate(tiles):
            r, c = divmod(i, cols)
            sheet[r * th:(r + 1) * th, c * tw:(c + 1) * tw] = tile

        out_dir = out_dir or os.path.dirname(os.path.abspath(path))
        dst = os.path.join(out_dir, f"sheet_seg{s + 1}.jpg")
        cv2.imwrite(dst, sheet)
        written.append((dst, len(tiles), t0, t1))
        print(f"段{s+1}  {len(tiles)} 帧  {t0:.1f}-{t1:.1f}s -> {dst}")

    cap.release()
    return written


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--segs", type=int, default=4, help="分几段（按设计的分段数填）")
    ap.add_argument("--step", type=float, default=0.5, help="每隔几秒取一帧")
    ap.add_argument("--out", default=None, help="输出目录")
    a = ap.parse_args()
    build(a.video, a.segs, a.step, a.out)
