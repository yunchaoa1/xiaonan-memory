#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""拓扑图 .drawio 校验探针（确定性，可重复跑）

用法：
    python drawio_verify.py 项目拓扑图_WBS_布局后.drawio
    python drawio_verify.py 图.drawio --svg 图.svg --expect "公司级 Agent,待办事项,漫剧发布平台"
    python drawio_verify.py 图.drawio --min-nodes 60

检查项（任一不过 → 退出码 1；全过 → 0）：
  1) 顶点 / 连边计数（--min-nodes 可设下限）
  2) 两两矩形重叠断言（布局后应为 0 —— 这是"内容被盖住"的硬指标）
  3) 内容包围盒是否在声明的画布（pageWidth/pageHeight）内
  4) --expect：在导出的 SVG 里逐字检索关键节点名（SVG 是文本，比看缩略图可靠）
"""
import argparse
import sys
import xml.etree.ElementTree as ET


def load_rects(path):
    """返回 (顶点列表, 连边数, 画布) —— 顶点=(id,标签首行,x,y,w,h)"""
    model = ET.parse(path).getroot().find(".//mxGraphModel")
    if model is None:
        raise SystemExit(f"不是有效的 .drawio（找不到 mxGraphModel）：{path}")
    canvas = (float(model.get("pageWidth") or 0), float(model.get("pageHeight") or 0))
    verts, edges = [], 0
    for c in model.findall(".//mxCell"):
        if c.get("vertex") == "1":
            g = c.find("mxGeometry")
            if g is None:
                continue
            verts.append((
                c.get("id"),
                (c.get("value") or "").split("\n")[0],
                float(g.get("x") or 0), float(g.get("y") or 0),
                float(g.get("width") or 0), float(g.get("height") or 0),
            ))
        elif c.get("edge") == "1":
            edges += 1
    return verts, edges, canvas


def overlaps(verts):
    out = []
    for i in range(len(verts)):
        _, li, x1, y1, w1, h1 = verts[i]
        for j in range(i + 1, len(verts)):
            _, lj, x2, y2, w2, h2 = verts[j]
            if x1 < x2 + w2 and x2 < x1 + w1 and y1 < y2 + h2 and y2 < y1 + h1:
                out.append((li[:24], lj[:24]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("drawio")
    ap.add_argument("--svg", help="同时核对的 SVG 导出文件")
    ap.add_argument("--expect", default="", help="逗号分隔的关键节点名（应出现在 SVG 里）")
    ap.add_argument("--min-nodes", type=int, default=1)
    a = ap.parse_args()

    verts, edges, canvas = load_rects(a.drawio)
    print(f"节点 {len(verts)} · 连边 {edges} · 画布 {canvas[0]:.0f}×{canvas[1]:.0f}")

    ok = True
    if len(verts) < a.min_nodes:
        print(f"✗ 节点数 {len(verts)} < 下限 {a.min_nodes}")
        ok = False

    ov = overlaps(verts)
    print(f"{'✓' if not ov else '✗'} 重叠对数 {len(ov)}")
    for p in ov[:10]:
        print(f"    {p[0]}  ×  {p[1]}")
    ok = ok and not ov

    xmax = max((x + w for _, _, x, _, w, _ in verts), default=0)
    ymax = max((y + h for _, _, _, y, _, h in verts), default=0)
    inside = xmax <= canvas[0] and ymax <= canvas[1]
    print(f"{'✓' if inside else '✗'} 内容右下角 ({xmax:.0f}, {ymax:.0f}) 在画布内")
    ok = ok and inside

    if a.svg:
        svg = open(a.svg, encoding="utf-8").read()
        missing = [k for k in (s.strip() for s in a.expect.split(",")) if k and k not in svg]
        print(f"{'✓' if not missing else '✗'} SVG 关键词核对（缺 {missing}）")
        ok = ok and not missing

    print("结果:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
