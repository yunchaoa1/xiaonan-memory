"""去除豆包 / Seedream 网页版出图右下角的「豆包 AI 生成」水印。

用法：
    python strip_doubao_watermark.py "<图片目录>"              # 处理（首次自动备份原图）
    python strip_doubao_watermark.py "<图片目录>" --restore    # 从备份还原
    python strip_doubao_watermark.py "<图片目录>" --radius 9   # 调整 inpaint 半径

三条实测教训（2026-11-19，《末位》12 张资产图）：
1. **按固定像素坐标算，不要按百分比。** 同一批图尺寸可能不同（人物四视图
   2848x1600、道具 1728x2304），水印是固定像素大小，百分比会漏掉左边一截，
   留下「豆包」两个字。
2. **不要裁底。** 人物四视图的脚就在图片最下沿，裁 80px 直接切鞋。
   用 inpaint 只填右下角那一小块。
3. **中文路径必须走 imdecode/imencode。** cv2.imread 遇到中文路径静默返回 None。
"""

import argparse
import os
import shutil
import sys

import cv2
import numpy as np

# 水印区：右下角 480x110（实测水印本体约 300x60，距右/下边各 30，多留余量）
MASK_W = 480
MASK_H = 110
BAK_DIRNAME = "_原图备份"
EXTS = (".png", ".jpg", ".jpeg", ".webp")


def imread_unicode(path):
    data = np.fromfile(path, dtype=np.uint8)
    if data.size == 0:
        return None
    return cv2.imdecode(data, cv2.IMREAD_COLOR)


def imwrite_unicode(path, img):
    ext = os.path.splitext(path)[1] or ".png"
    ok, buf = cv2.imencode(ext, img)
    if not ok:
        return False
    buf.tofile(path)
    return True


def process(path, radius):
    img = imread_unicode(path)
    if img is None:
        return "读不出", None
    h, w = img.shape[:2]
    x1, y1 = max(0, w - MASK_W), max(0, h - MASK_H)
    mask = np.zeros((h, w), dtype=np.uint8)
    mask[y1:h, x1:w] = 255
    out = cv2.inpaint(img, mask, radius, cv2.INPAINT_TELEA)
    imwrite_unicode(path, out)
    return "已处理", (w, h, x1, y1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("directory")
    ap.add_argument("--restore", action="store_true", help="从 _原图备份 还原")
    ap.add_argument("--radius", type=int, default=7)
    args = ap.parse_args()

    src = os.path.abspath(args.directory)
    if not os.path.isdir(src):
        sys.exit(f"目录不存在：{src}")
    bak = os.path.join(src, BAK_DIRNAME)

    if args.restore:
        if not os.path.isdir(bak):
            sys.exit(f"没有备份目录：{bak}")
        n = 0
        for name in os.listdir(bak):
            if name.lower().endswith(EXTS):
                shutil.copy2(os.path.join(bak, name), os.path.join(src, name))
                n += 1
        print(f"已从备份还原 {n} 张")
        return

    os.makedirs(bak, exist_ok=True)
    targets = sorted(f for f in os.listdir(src) if f.lower().endswith(EXTS))
    if not targets:
        sys.exit("目录里没有图片")

    print(f"共 {len(targets)} 张")
    for name in targets:
        path = os.path.join(src, name)
        backup = os.path.join(bak, name)
        if not os.path.exists(backup):
            shutil.copy2(path, backup)
        status, info = process(path, args.radius)
        if info:
            w, h, x1, y1 = info
            print(f"{name} ({w}x{h}): {status} [{x1},{y1}]-[{w},{h}]")
        else:
            print(f"{name}: {status}")

    print(f"\n完成，原图已备份到 {bak}")


if __name__ == "__main__":
    main()
