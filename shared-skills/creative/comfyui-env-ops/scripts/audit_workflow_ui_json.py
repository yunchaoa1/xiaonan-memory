#!/usr/bin/env python3
"""UI 格式 ComfyUI 工作流自检：格式判定 / 坏链接 / inputs↔outputs 双向一致性 / 分组覆盖。

用法:
    python audit_workflow_ui_json.py <workflow.json> [more.json ...]

改动 UI 格式工作流（改连线、加节点、重排分组）后必须跑一次。
若传入的是 API 格式文件，会明确提示"不能建节点组"，请让用户 Export UI 格式。
退出码: 0 = 全部通过；1 = 存在结构性问题。
"""
import json
import os
import sys


def audit(path):
    print(f"===== {os.path.basename(path)} =====")
    try:
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
    except Exception as e:                                    # noqa: BLE001
        print(f"  ❌ 读取失败: {e}")
        return False
    if not isinstance(d, dict):
        print("  ❌ 顶层不是 JSON 对象")
        return False

    if not isinstance(d.get("nodes"), list):
        flat = [k for k, v in d.items() if isinstance(v, dict) and "class_type" in v]
        if flat:
            print(f"  ⚠️ 这是 API 格式（{len(flat)} 个扁平节点）：无坐标、无 links/groups —— 做不了节点组，"
                  f"请让用户在 ComfyUI 里 Workflow → Export 导出 UI 格式。")
            print("  （API 格式的连线体检请用 scripts/audit_workflow_json.py）")
        else:
            print("  ❌ 既不是 UI 格式也不是 API 格式")
        return False

    nodes = {n["id"]: n for n in d["nodes"] if isinstance(n, dict) and "id" in n}
    links = {}
    for l in d.get("links", []) or []:
        if isinstance(l, list) and len(l) >= 6:
            links[l[0]] = l
    print(f"  ✅ UI 格式 | 节点 {len(nodes)} | 链接 {len(links)} | 组 {len(d.get('groups', []) or [])}")

    bad_target = [l for l in links.values() if l[1] not in nodes or l[3] not in nodes]
    dangling_in = [(nid, it.get("name"), it.get("link"))
                   for nid, n in nodes.items()
                   for it in (n.get("inputs") or [])
                   if it.get("link") is not None and it["link"] not in links]
    missing_out = [(nid, si, lk)
                   for nid, n in nodes.items()
                   for si, o in enumerate(n.get("outputs") or [])
                   for lk in (o.get("links") or [])
                   if lk not in links]

    mismatch = []
    for lid, l in links.items():
        src, sslot, dst, dslot = l[1], l[2], l[3], l[4]
        outs = (nodes.get(src) or {}).get("outputs") or []
        ok_src = sslot < len(outs) and isinstance(outs[sslot].get("links"), list) and lid in outs[sslot]["links"]
        dins = (nodes.get(dst) or {}).get("inputs") or []
        ok_dst = dslot < len(dins) and dins[dslot].get("link") == lid
        if not (ok_src and ok_dst):
            mismatch.append((lid, "" if ok_src else "源outputs缺引用", "" if ok_dst else "目标inputs未指向"))

    def in_box(n, box):
        x, y = (n.get("pos") or [0, 0])[:2]
        w, h = (n.get("size") or [0, 0])[:2]
        bx, by, bw, bh = box
        return x >= bx and y >= by and (x + w) <= (bx + bw) and (y + h) <= (by + bh)

    boxes = [(g.get("title"), g.get("bounding")) for g in (d.get("groups") or []) if g.get("bounding")]
    covered = {nid for nid in nodes for _, b in boxes if in_box(nodes[nid], b)}
    uncovered = sorted(set(nodes) - covered)

    print("  --- 自检结果 ---")
    print("  链接指向不存在节点:", bad_target or "无 ✅")
    print("  悬空输入(link 不在 links 里):", dangling_in or "无 ✅")
    print("  outputs.links 反向引用丢失:", missing_out or "无 ✅")
    print("  inputs↔outputs 不同步:", mismatch or "无 ✅")
    print("  未入任何组的节点:", uncovered or "无 ✅")
    bad = bool(bad_target or dangling_in or missing_out or mismatch)
    print("  >>> " + ("存在结构性问题，导入前先修" if bad else "结构一致，可导入"))
    print()
    return not bad


def main():
    targets = sys.argv[1:]
    if not targets:
        print(__doc__)
        return 1
    ok = all(audit(p) for p in targets)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
