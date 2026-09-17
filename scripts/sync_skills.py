# -*- coding: utf-8 -*-
"""技能同步脚本 —— dual-agent-memory-sync 技能配套工具

架构（单一真相源 + 运行镜像）:
    D:\\Hermes\\xiaonan-memory\\shared-skills\\    ← 唯一编辑源，Git 同步
              ↓ install (pull)        ↑ export (push)
    D:\\Hermes\\skills\\                          ← Hermes 实际加载的运行副本

用法:
    python sync_skills.py status          # 对比两边差异（只读，不改动）
    python sync_skills.py push            # 运行目录的自建技能 → shared-skills（导出）
    python sync_skills.py pull            # shared-skills → 运行目录（安装/更新）
    python sync_skills.py push --mirror   # 严格镜像：shared-skills 里多余的自建技能会被删除
    python sync_skills.py pull --mirror   # 严格镜像：运行目录里多余的自建技能会被删除

只同步 source=local 的自建技能；builtin 技能由 Hermes 自身维护，不进仓库。
"""
import subprocess
import os
import sys
import shutil
import hashlib
import re
from pathlib import Path

# 路径自适应 —— 脚本放在 <HERMES_HOME>/scripts/ 下即可，两端无需改代码
HERMES_HOME = Path(__file__).resolve().parent.parent
SKILLS = HERMES_HOME / "skills"
SHARED = HERMES_HOME / "xiaonan-memory" / "shared-skills"
SKIP_DIRS = {"__pycache__", ".git", ".archive", "node_modules", ".venv"}
SKIP_EXT = {".pyc", ".pyo"}


def local_skill_names():
    """从 hermes skills list 取 source=local（自建）技能名 —— 这是权威清单"""
    env = os.environ.copy()
    env.update({"COLUMNS": "1000", "TERM": "dumb", "NO_COLOR": "1"})
    try:
        o = subprocess.run(["hermes", "skills", "list"], capture_output=True, text=True,
                           encoding="utf-8", errors="replace", env=env).stdout
    except FileNotFoundError:
        print("!! 找不到 hermes 命令")
        return set()
    names = set()
    for line in o.splitlines():
        if line.strip().startswith("│"):
            p = [x.strip() for x in line.strip().strip("│").split("│")]
            if len(p) == 5 and p[0] != "Name" and p[2] == "local":
                names.add(p[0])
    return names


def skill_name(skill_md):
    """从 SKILL.md frontmatter 读 name —— 目录名可能与技能名不同
    （实测：目录 writing-opc-entry-test 里的技能名是 writing-opc-entry；
      Hermes 以 frontmatter 的 name 为准，不是目录名）"""
    try:
        txt = skill_md.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return None
    m = re.match(r"^---\s*\n(.*?)\n---", txt, re.S)
    if not m:
        return None
    for line in m.group(1).splitlines():
        s = line.strip()
        if s.startswith("name:"):
            return s.split(":", 1)[1].strip().strip("\"'")
    return None


def scan(root):
    """扫描技能根目录 → {技能名: 相对路径}（技能名取 frontmatter，不是目录名）"""
    out = {}
    for p in Path(root).rglob("SKILL.md"):
        if any(s in p.parts for s in SKIP_DIRS):
            continue
        out[skill_name(p) or p.parent.name] = p.parent.relative_to(root)
    return out


def tree_hash(d):
    """目录内容哈希（用于比对是否需要更新）"""
    h = hashlib.sha256()
    for root, dirs, files in sorted(os.walk(d)):
        dirs[:] = sorted(x for x in dirs if x not in SKIP_DIRS)
        for f in sorted(files):
            if Path(f).suffix in SKIP_EXT:
                continue
            fp = Path(root) / f
            h.update(str(fp.relative_to(d)).encode("utf-8", "replace"))
            h.update(fp.read_bytes())
    return h.hexdigest()


def copy_tree(src, dst):
    if dst.exists():
        shutil.rmtree(dst)
    for root, dirs, files in os.walk(src):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        rel = Path(root).relative_to(src)
        (dst / rel).mkdir(parents=True, exist_ok=True)
        for f in files:
            if Path(f).suffix in SKIP_EXT:
                continue
            shutil.copy2(Path(root) / f, dst / rel / f)


def cmd_status():
    names = local_skill_names()
    run, shr = scan(SKILLS), scan(SHARED)
    run_mine = {n: p for n, p in run.items() if n in names}
    shr_names = set(shr)

    only_run = sorted(set(run_mine) - shr_names)
    only_shr = sorted(shr_names - set(run_mine))
    both = sorted(set(run_mine) & shr_names)
    diff, same = [], []
    for n in both:
        a = SKILLS / run_mine[n]
        b = SHARED / shr[n]
        (same if tree_hash(a) == tree_hash(b) else diff).append(n)

    print(f"自建技能（hermes 认定 local）: {len(names)}")
    print(f"运行目录 D:\\Hermes\\skills 里的自建技能: {len(run_mine)}")
    print(f"共享源 shared-skills 里的技能: {len(shr_names)}")
    print(f"  仅本地有（待 push）: {len(only_run)} {only_run if only_run else ''}")
    print(f"  仅共享有（待 pull）: {len(only_shr)} {only_shr if only_shr else ''}")
    print(f"  两边都有-内容一致: {len(same)}")
    print(f"  两边都有-内容不同: {len(diff)} {diff if diff else ''}")
    return 0


def cmd_push(mirror=False):
    names = local_skill_names()
    run = {n: p for n, p in scan(SKILLS).items() if n in names}
    shr = scan(SHARED)
    SHARED.mkdir(parents=True, exist_ok=True)

    added, updated = [], []
    for n, rel in sorted(run.items()):
        a, b = SKILLS / rel, SHARED / rel
        if n not in shr:
            added.append(n)
        elif tree_hash(a) != tree_hash(b):
            updated.append(n)
        else:
            continue
        copy_tree(a, b)
    print(f"push: 新增 {len(added)} 个 {added}")
    print(f"push: 更新 {len(updated)} 个 {updated}")

    if mirror:
        removed = []
        for n, rel in sorted(shr.items()):
            if n not in run:
                shutil.rmtree(SHARED / rel, ignore_errors=True)
                removed.append(n)
        print(f"push --mirror: 删除 shared-skills 里多余的 {len(removed)} 个 {removed}")
    return 0


def cmd_pull(mirror=False):
    names = local_skill_names()
    run_before = scan(SKILLS)
    shr = scan(SHARED)
    if not shr:
        print("!! shared-skills 为空（先在另一端 push，或先 git pull）")
        return 1

    installed, updated, skipped_builtin = [], [], []
    for n, rel in sorted(shr.items()):
        if n in run_before and n not in names:
            skipped_builtin.append(n)   # 本地已有同名且是内置技能 → 不动
            continue
        a, b = SKILLS / rel, SHARED / rel
        if not a.exists():
            installed.append(n)
        elif tree_hash(a) != tree_hash(b):
            updated.append(n)
        else:
            continue
        copy_tree(b, a)
    print(f"pull: 新装 {len(installed)} 个 {installed}")
    print(f"pull: 更新 {len(updated)} 个 {updated}")
    if skipped_builtin:
        print(f"pull: 跳过同名内置技能 {len(skipped_builtin)} 个 {skipped_builtin}")

    if mirror:
        removed = []
        for n, rel in sorted(run_before.items()):
            if n in names and n not in shr:
                shutil.rmtree(SKILLS / rel, ignore_errors=True)
                removed.append(n)
        print(f"pull --mirror: 删除运行目录里多余的 {len(removed)} 个 {removed}")

    print("\n⚠ 装完请让 Hermes 重扫技能（新会话或 /reload-skills）")
    return 0


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in ("status", "push", "pull"):
        print(__doc__)
        return 2
    mirror = "--mirror" in sys.argv
    return {"status": cmd_status, "push": lambda: cmd_push(mirror),
            "pull": lambda: cmd_pull(mirror)}[sys.argv[1]]()


if __name__ == "__main__":
    sys.exit(main())
