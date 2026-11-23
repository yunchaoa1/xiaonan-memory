# -*- coding: utf-8 -*-
"""检测 forest-laoli-h3 的本地改动是否还在（防作者更新覆盖）

用法：
    python check_drift.py                 # 对比当前 vs 基线
    python check_drift.py --against <dir> # 对比当前 vs 指定的新版目录
"""
import argparse, hashlib, io, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
BASE = os.path.join(HERE, "baseline_20261123")

# 我们改过 / 新增的文件（相对技能根目录）
PATCHED = [
    "scripts/h3_lint.py",
    "references/acting-facs.md",
    "references/h3-format.md",
]
ADDED = [
    "references/emotion-curve.md",
]

# 基线哈希（2026-11-23 备份时记录的，前 16 位）
BASELINE_HASH = {
    "scripts/h3_lint.py": "928c7ed1a48b6f90",
    "references/acting-facs.md": "598a6368d1ddeb4a",
    "references/h3-format.md": "4418f14e0925ade3",
}


def sha16(p):
    if not os.path.exists(p):
        return None
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--against", default=None, help="对比目录（如新版技能解压位置）")
    a = ap.parse_args()

    root = a.against or SKILL
    print("对比基准：", BASE if not a.against else a.against)
    print("当前技能：", SKILL)
    print("=" * 64)

    problems = 0

    print("\n【一】我们改过的文件 —— 改动是否还在？")
    for rel in PATCHED:
        cur = sha16(os.path.join(SKILL, rel))
        base = sha16(os.path.join(BASE, rel))
        if cur is None:
            print(f"  ❌ {rel} 文件不见了")
            problems += 1
        elif cur == base:
            print(f"  ⚠️  {rel} 和基线一样 —— 我们的改动不见了（可能被更新覆盖）")
            problems += 1
        else:
            print(f"  ✅ {rel} 已改动（基线 {base} → 当前 {cur}）")

    print("\n【二】我们新增的文件 —— 是否还在？")
    for rel in ADDED:
        p = os.path.join(SKILL, rel)
        if os.path.exists(p):
            print(f"  ✅ {rel}（{os.path.getsize(p)} 字节）")
        else:
            print(f"  ❌ {rel} 不见了 —— 需要从 _fange_patches 重新部署")
            problems += 1

    if a.against:
        print("\n【三】新版技能 vs 我们的改动 —— 有没有冲突？")
        for rel in PATCHED:
            new = sha16(os.path.join(a.against, rel))
            cur = sha16(os.path.join(SKILL, rel))
            if new is None:
                print(f"  · {rel} 新版没有这个文件")
            elif new == cur:
                print(f"  ✅ {rel} 新版已经包含我们的改动")
            else:
                print(f"  ⚠️  {rel} 新版和我们的不一样 —— 要人工合并（以 11-21 实测结论为准）")
                problems += 1

    print("\n" + "=" * 64)
    if problems:
        print(f"发现 {problems} 个问题，详见上面 ❌ / ⚠️ 项")
        print("恢复命令：cp -r _fange_patches/baseline_20261123/* ./ （会退回到原始版本，慎用）")
        sys.exit(1)
    print("一切正常：我们的改动都在。")
    sys.exit(0)


if __name__ == "__main__":
    main()
