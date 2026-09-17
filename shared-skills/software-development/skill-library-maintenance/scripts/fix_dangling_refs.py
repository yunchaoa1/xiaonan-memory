# -*- coding: utf-8 -*-
"""批量修复保留技能的悬空 [ref:xxx] 引用。

背景：官方技能包扁平化安装（只拷 SKILL.md，references 缺失）导致
[ref:xxx] 指向不存在的文件。正文自足时替换为明确提示，不影响功能。

用法：
1. 编辑 DISABLED 集合（已停用技能跳过）
2. 运行：python fix_dangling_refs.py
"""
import re
import yaml
from pathlib import Path

root = Path(r"D:\Hermes\skills")
DISABLED = {
    # 已停用技能不用修，示例：
    # "seedance-vocab-en", "powerpoint",
}

pat = re.compile(r"\[ref:([A-Za-z0-9_./-]+)\]")
changed = 0

for p in root.rglob("SKILL.md"):
    if ".archive" in p.parts:
        continue
    text = p.read_text(encoding="utf-8", errors="replace")
    m = re.search(r"^---\s*\n(.*?)\n---", text, re.S)
    if not m:
        continue
    try:
        fm = yaml.safe_load(m.group(1)) or {}
    except Exception:
        fm = {}
    name = str(fm.get("name") or p.parent.name)
    if name in DISABLED:
        continue

    def repl(mm):
        ref = mm.group(1)
        cand = p.parent / "references" / (ref + ".md")
        if cand.exists():
            return mm.group(0)  # 保留存在的引用
        return f"[参考:{ref}未安装扩展，以本正文为准]"

    new_text = pat.sub(repl, text)
    if new_text != text:
        p.write_text(new_text, encoding="utf-8")
        changed += 1
        print(f"fixed {name}")

print("changed skills:", changed)
