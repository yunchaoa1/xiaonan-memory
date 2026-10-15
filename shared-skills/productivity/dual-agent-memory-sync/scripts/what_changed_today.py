#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""找痕迹第一步：列出「今天被改过的文件」+「今天的 git 提交」。

用途：怀疑另一个会话 / 另一台电脑已经改过同一批文件时，先跑这个。
配套：dual-agent-memory-sync §「另一个会话先做过了：动账前先查痕迹」。

用法（terminal 里一律用正斜杠）：
    python D:/Hermes/skills/productivity/dual-agent-memory-sync/scripts/what_changed_today.py
    python .../what_changed_today.py "D:/Documents/我的文档/思维导图" "D:/Hermes/xiaonan-memory"
不传参数 = 扫下面的 DEFAULT_DIRS。
"""
import os
import subprocess
import sys
import time

DEFAULT_DIRS = [
    r"D:\Documents\我的文档\思维导图",
    r"D:\Hermes\xiaonan-memory",
]
REPO = r"D:\Hermes\xiaonan-memory"
TOP_N = 40


def walk_today(dirs):
    """返回 (mtime, path)，只含今天被改过的文件，新的在前。"""
    today = time.strftime("%Y-%m-%d")
    hits = []
    for d in dirs:
        if not os.path.isdir(d):
            print("  (跳过，目录不存在)", d)
            continue
        for root, _dirs, files in os.walk(d):
            if ".git" in root.replace("/", "\\").split("\\"):
                continue
            for f in files:
                p = os.path.join(root, f)
                try:
                    m = os.path.getmtime(p)
                except OSError:
                    continue
                if time.strftime("%Y-%m-%d", time.localtime(m)) == today:
                    hits.append((m, p))
    hits.sort(reverse=True)
    return hits


def git_today():
    try:
        out = subprocess.run(
            ["git", "-C", REPO, "log", "--since=midnight",
             "--pretty=%h %ad %s", "--date=format:%m-%d %H:%M"],
            capture_output=True, text=True, timeout=30)
        return out.stdout.strip()
    except Exception as e:  # noqa: BLE001
        return "(git 读取失败: %s)" % e


def main():
    dirs = sys.argv[1:] or DEFAULT_DIRS
    today = time.strftime("%Y-%m-%d")
    hits = walk_today(dirs)
    print("== 今天(%s)被改过的文件：%d 个 ==" % (today, len(hits)))
    for m, p in hits[:TOP_N]:
        print(" ", time.strftime("%H:%M", time.localtime(m)), "|",
              os.path.getsize(p), "字节 |", p)
    if len(hits) > TOP_N:
        print("  ...(还有 %d 个)" % (len(hits) - TOP_N))
    if not hits:
        print("  (无 —— 今天还没人动过这些目录)")
    print()
    print("== 今天的 git 提交（%s）==" % REPO)
    print(git_today() or "  (无)")


if __name__ == "__main__":
    main()
