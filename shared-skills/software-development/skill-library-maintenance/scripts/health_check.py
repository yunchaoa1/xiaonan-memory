# -*- coding: utf-8 -*-
"""
技能库体检脚本 —— skill-library-maintenance 技能配套工具
用法: python health_check.py [--verbose]
输出: 技能数量/新增、YAML损坏、悬空引用、重复相似对、curator参数
退出码: 0=正常, 1=发现异常（供 cron/脚本调用判断）
"""
import re
import sys
import json
import yaml
import subprocess
import os
from pathlib import Path

SKILLS = Path(r"D:\Hermes\skills")
VERBOSE = "--verbose" in sys.argv

def enabled_list():
    env = os.environ.copy()
    env["COLUMNS"] = "500"; env["TERM"] = "dumb"; env["NO_COLOR"] = "1"
    o = subprocess.run(["hermes", "skills", "list", "--enabled-only"],
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace", env=env).stdout
    enabled = set()
    for l in o.splitlines():
        p = [x.strip() for x in l.strip("│").split("│")]
        if l.startswith("│") and len(p) >= 5 and p[4] == "enabled" and p[0] != "Name":
            enabled.add(p[0])
    return enabled

def main():
    problems = []
    enabled = enabled_list()
    print(f"启用技能: {len(enabled)}")

    # 1. YAML 完整性 + 中文描述覆盖
    total = zh = 0
    broken = []
    for p in SKILLS.rglob("SKILL.md"):
        if ".archive" in p.parts:
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        m = re.search(r"^---\s*\n(.*?)\n---", text, re.S)
        if not m:
            broken.append((p.parent.name, "no frontmatter"))
            continue
        try:
            fm = yaml.safe_load(m.group(1))
            if not isinstance(fm, dict) or not fm.get("name"):
                broken.append((p.parent.name, "bad yaml"))
                continue
            name = str(fm["name"])
            if name in enabled:
                total += 1
                if re.search(r"[\u4e00-\u9fff]", str(fm.get("description") or "")):
                    zh += 1
        except Exception as e:
            broken.append((p.parent.name, str(e)[:50]))
    if broken:
        problems.append(f"YAML损坏: {broken}")
        print("YAML损坏:", broken)
    else:
        print(f"YAML完好: {total}个启用技能, 中文描述 {zh}/{total}")

    # 2. 悬空引用（仅查引用文件路径缺失的）
    pat = re.compile(r"\[ref:([A-Za-z0-9_./-]+)\]")
    dangling = []
    for p in SKILLS.rglob("SKILL.md"):
        if ".archive" in p.parts:
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        m = re.search(r"^---\s*\n(.*?)\n---", text, re.S)
        if not m:
            continue
        try:
            fm = yaml.safe_load(m.group(1)) or {}
        except Exception:
            continue
        name = str(fm.get("name") or p.parent.name)
        if name not in enabled:
            continue
        for mm in pat.finditer(text):
            ref = mm.group(1)
            # 跳过占位符示例（文档里举例的 [ref:xxx] 不是真引用）
            if ref in ("xxx", "yyy", "example", "name") or re.fullmatch(r"[a-z]+", ref) and len(ref) <= 4:
                continue
            if not (p.parent / "references" / (ref + ".md")).exists():
                dangling.append((name, ref))
    if dangling:
        problems.append(f"悬空引用 {len(dangling)} 处")
        if VERBOSE:
            for n, r in dangling[:20]:
                print(f"  悬空: {n} -> [ref:{r}]")
    else:
        print("悬空引用: 无")

    # 2.5 正文脏数据：字面 \n 转义块
    # （frontmatter 被当成字符串误写进正文的典型症状 —— 2026-09-17 从 barnum-effect 发现，
    #   原脚本的 YAML 检查只看第一个 block，抓不到这种"正文里的假 frontmatter"）
    dirty = []
    junk_pat = re.compile(r"\\n(name|description|version|metadata|tags|triggers|category)\b")
    for p in SKILLS.rglob("SKILL.md"):
        if ".archive" in p.parts:
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        m = re.search(r"^---\s*\n(.*?)\n---", text, re.S)
        if not m:
            continue
        try:
            fm = yaml.safe_load(m.group(1)) or {}
        except Exception:
            continue
        name = str(fm.get("name") or p.parent.name)
        if name not in enabled:
            continue
        hits = junk_pat.findall(text[m.end():])   # 只看正文，不误报 frontmatter 本身
        if hits:
            dirty.append((name, len(hits)))
    if dirty:
        problems.append(f"正文脏数据 {len(dirty)} 个技能")
        for n, c in dirty:
            print(f"  脏数据: {n} ({c} 处字面\\n，需清理)")
    else:
        print("正文脏数据: 无")

    # 3. 重复相似对（desc Jaccard > 0.7 且非同族白名单）
    white = {"seedance-vocab", "seedance-examples"}
    items = []
    for p in SKILLS.rglob("SKILL.md"):
        if ".archive" in p.parts:
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        m = re.search(r"^---\s*\n(.*?)\n---", text, re.S)
        if not m:
            continue
        try:
            fm = yaml.safe_load(m.group(1)) or {}
        except Exception:
            continue
        name = str(fm.get("name") or p.parent.name)
        if name not in enabled:
            continue
        desc = re.sub(r"\s+", "", str(fm.get("description") or "").lower())
        body = re.sub(r"```.*?```", "", text[m.end():], flags=re.S)
        body = re.sub(r"\s+", "", body.lower())
        items.append((name, desc, body))
    pairs = []
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            a, b = items[i], items[j]
            da, db = set(a[1][k:k+3] for k in range(max(0, len(a[1])-2))), set(b[1][k:k+3] for k in range(max(0, len(b[1])-2)))
            sim = len(da & db) / max(1, len(da | db))
            if sim > 0.7 and not any(a[0].startswith(w) and b[0].startswith(w) for w in white):
                pairs.append((a[0], b[0], round(sim, 2)))
    if pairs:
        problems.append(f"疑似重复 {len(pairs)} 对")
        for x in pairs:
            print(f"  疑似重复: {x[0]} <-> {x[1]} (desc_sim={x[2]})")
    else:
        print("疑似重复: 无")

    # 4. curator 关键参数（防被改回）
    cfg_path = Path(r"D:\Hermes\config.yaml")
    if cfg_path.exists():
        cfg = yaml.safe_load(cfg_path.read_text(encoding="utf-8")) or {}
        cur = cfg.get("curator") or {}
        if cur.get("archive_after_days", 90) < 1000:
            problems.append(f"curator 归档线被改小: {cur.get('archive_after_days')}天（应≥36500）")
        if cur.get("consolidate"):
            problems.append("curator consolidate 被打开了（应关闭）")
        print("curator:", {k: cur.get(k) for k in ("stale_after_days", "archive_after_days", "consolidate", "prune_builtins")})

    # 5. 技能索引体积
    idx = 0
    for p in SKILLS.rglob("SKILL.md"):
        if ".archive" in p.parts:
            continue
        try:
            m2 = re.search(r"^---\s*\n(.*?)\n---", p.read_text(encoding="utf-8", errors="replace"), re.S)
            if not m2:
                continue
            fm2 = yaml.safe_load(m2.group(1)) or {}
            if not isinstance(fm2, dict):
                continue
            desc = str(fm2.get("description") or "")
            idx += len(str(fm2.get("name") or p.parent.name)) + len(desc) + 8
        except Exception:
            continue
    print(f"技能索引估算: ~{idx}字符")

    print("\n结论:", "⚠️ 发现异常，需人工处理" if problems else "✅ 健康")
    return 1 if problems else 0

if __name__ == "__main__":
    sys.exit(main())
