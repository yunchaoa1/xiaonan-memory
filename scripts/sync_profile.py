# -*- coding: utf-8 -*-
"""记忆与人格文件同步 —— dual-agent-memory-sync 技能配套工具

真相源：运行时文件（两台电脑各自在用、在改的那份）
    D:\\Hermes\\memories\\MEMORY.md  <->  xiaonan-memory\\MEMORY.md
    D:\\Hermes\\memories\\USER.md    <->  xiaonan-memory\\USER.md
    D:\\Hermes\\SOUL.md             <->  xiaonan-memory\\SOUL.md

用法:
    python sync_profile.py status    # 看两边差异
    python sync_profile.py push      # 运行时 -> 仓库（收工）
    python sync_profile.py pull      # 仓库 -> 运行时（开工，覆盖前自动备份）
"""
import shutil
import sys
from datetime import datetime
from pathlib import Path

# 路径自适应 —— 脚本放在 <HERMES_HOME>/scripts/ 下即可，两端无需改代码
HERMES_HOME = Path(__file__).resolve().parent.parent
REPO = HERMES_HOME / "xiaonan-memory"
BACKUP_ROOT = HERMES_HOME / "memories" / ".sync-backup"

PAIRS = [
    (HERMES_HOME / "memories" / "MEMORY.md", REPO / "MEMORY.md"),
    (HERMES_HOME / "memories" / "USER.md", REPO / "USER.md"),
    (HERMES_HOME / "SOUL.md", REPO / "SOUL.md"),
]


def read(p):
    try:
        return p.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return None


def status():
    same = diff = only_run = only_repo = 0
    print("文件同步状态:")
    for run, rep in PAIRS:
        a, b = read(run), read(rep)
        if a is None and b is None:
            print("  %s: 两边都缺 ⚠️" % run.name)
        elif a is None:
            print("  %s: 仅仓库有（可 pull）" % run.name)
            only_repo += 1
        elif b is None:
            print("  %s: 仅运行时有（可 push）" % run.name)
            only_run += 1
        elif a == b:
            print("  %s: 一致 OK" % run.name)
            same += 1
        else:
            print("  %s: 不同 ⚠️  运行时 %d 字 / 仓库 %d 字" % (run.name, len(a), len(b)))
            diff += 1
    print("\n合计: 一致 %d / 不同 %d / 仅运行时 %d / 仅仓库 %d" % (same, diff, only_run, only_repo))
    return 0


def backup(path):
    if not path.exists():
        return None
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    d = BACKUP_ROOT / ts
    d.mkdir(parents=True, exist_ok=True)
    dst = d / path.name
    shutil.copy2(path, dst)
    return dst


def push():
    print("push: 运行时 -> 仓库")
    for run, rep in PAIRS:
        a = read(run)
        if a is None:
            print("  %s: 运行时不存在，跳过" % run.name)
            continue
        if a == read(rep):
            print("  %s: 无变化" % run.name)
            continue
        rep.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(run, rep)
        print("  %s: 已导出 (%d 字)" % (run.name, len(a)))
    return 0


def pull():
    print("pull: 仓库 -> 运行时（覆盖前自动备份）")
    for run, rep in PAIRS:
        b = read(rep)
        if b is None:
            print("  %s: 仓库不存在，跳过" % rep.name)
            continue
        a = read(run)
        if a == b:
            print("  %s: 无变化" % run.name)
            continue
        if a is not None:
            dst = backup(run)
            print("  %s: 旧版已备份 -> %s" % (run.name, dst))
        run.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(rep, run)
        print("  %s: 已安装 (%d 字)" % (run.name, len(b)))
    return 0


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    if cmd == "status":
        return status()
    if cmd == "push":
        return push()
    if cmd == "pull":
        return pull()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
