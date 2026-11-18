#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""技能恢复脚本 —— 把归档到 skills-archive 的技能拉回 skills/。

配套 §3.8「激进瘦身全流程」。归档是可逆的：本脚本把
skills-archive/<分类>/<技能> 移回 skills/<分类>/<技能>，
并从 config.yaml 的 skills.disabled 里删掉该名字（如果被禁用过）。

用法:
    python restore_skills.py                     # 列出归档里的全部技能
    python restore_skills.py --all               # 全部拉回（慎用）
    python restore_skills.py 名字1 名字2          # 只拉回指定的（推荐）

验证（拉回后必须做）:
    hermes skills list | grep <名字>     # 应显示 enabled
"""
import os
import sys
import shutil
import glob
import re
import io

ARCH = r"D:/Hermes/skills-archive"
ROOT = r"D:/Hermes/skills"
CFG = r"D:/Hermes/config.yaml"


def index_archive():
    """返回 {技能目录名: 目录绝对路径}。"""
    m = {}
    for f in glob.glob(os.path.join(ARCH, "**", "SKILL.md"), recursive=True):
        d = os.path.dirname(f)
        m[os.path.basename(d)] = d
    return m


def un_disable(names):
    """从 config.yaml 的 skills.disabled 里删掉这些名字。"""
    if not os.path.exists(CFG):
        print("  !! 找不到 config.yaml: %s" % CFG)
        return
    text = io.open(CFG, encoding="utf-8").read()
    o = text
    for n in names:
        text = re.sub(r"^[ \t]*- %s\s*\n" % re.escape(n), "", text, flags=re.M)
    if text != o:
        io.open(CFG, "w", encoding="utf-8", newline="\n").write(text)
        print("  已从 config.yaml 的 disabled 移除")


def main():
    arc = index_archive()
    args = [a for a in sys.argv[1:] if not a.startswith("--")]

    if not args and "--all" not in sys.argv:
        print("归档中已有 %d 个技能：\n" % len(arc))
        for n in sorted(arc):
            print("  ", n)
        print("\n用法: python restore_skills.py --all  |  python restore_skills.py <名字>")
        return

    if not arc:
        print("归档目录是空的: %s" % ARCH)
        return

    targets = list(arc) if "--all" in sys.argv else args
    done = []
    for n in targets:
        src = arc.get(n)
        if not src:
            print("  !! 归档里没有: %s（先不带参数跑一次看清单）" % n)
            continue
        cat = os.path.basename(os.path.dirname(src))
        dst_dir = os.path.join(ROOT, cat)
        os.makedirs(dst_dir, exist_ok=True)
        dst = os.path.join(dst_dir, n)
        if os.path.exists(dst):
            print("  !! 目标已存在，跳过: %s" % n)
            continue
        shutil.move(src, dst)
        done.append(n)
        print("  恢复 %s -> skills/%s/" % (n, cat))

    if done:
        un_disable(done)
    print("\n共恢复 %d 个。跑 hermes skills list 确认 enabled。" % len(done))


if __name__ == "__main__":
    main()
