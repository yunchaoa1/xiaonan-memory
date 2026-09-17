#!/usr/bin/env python3
"""装第三方 ComfyUI 节点包前：同名节点撞车体检（只读，不改任何文件）。

背景
----
两个自定义节点包注册同名节点类时，ComfyUI 后加载的会覆盖先加载的。若两边
INPUT_TYPES 参数表不同代，所有引用该节点的已存工作流都会「参数整体错位 →
校验失败 → 整条 prompt 秒退」。装插件前先跑本脚本，比装完再排障省一轮。

用法
----
    python audit_node_pack_collision.py <新包目录> <已装包目录> [更多包目录...]
    python audit_node_pack_collision.py <包A> <包B> --class MiniMaxH3MotionContext

参数
----
    pack_dirs   自定义节点包目录，可给多个，逐一比对
    --class X   额外并排对比各包中 class X 的 INPUT_TYPES 参数名，判「参数表是否同代」
    --quiet     只打印撞车结论

输出
----
    每个包注册的节点数；跨包同名节点清单；可选参数表对比与差异。
    退出码恒为 0（这是体检工具，不是断言工具）。

注意
----
纯静态正则启发式：不做 import（第三方包常有重依赖，导入即失败）。字符串里
出现花括号可能干扰块边界计数，极端情况以人工核对为准。
"""

import argparse
import os
import re

SKIP_DIRS = {"__pycache__", ".git", "node_modules", ".pytest_cache", ".venv", "venv"}

CLASS_MAP_RE = re.compile(r"NODE_CLASS_MAPPINGS\s*=\s*\{")
KEY_RE = re.compile(r"""["']([A-Za-z_][A-Za-z0-9_.]*)["']\s*:""")
SKIP_KEYS = {"required", "optional", "hidden"}


def iter_py(pack_dir):
    for root, dirs, files in os.walk(pack_dir):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for name in files:
            if name.endswith(".py"):
                yield os.path.join(root, name)


def read_text(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            return fh.read()
    except OSError:
        return ""


def matching_block(text, start):
    """从 start（'{' 之后的下标）取到与之配对的 '}' 之前的内容。"""
    depth = 1
    i = start
    while i < len(text):
        ch = text[i]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start:i]
        i += 1
    return text[start:]


def node_classes(pack_dir):
    """{节点类名: 首次出现的文件（相对包目录）}"""
    found = {}
    for path in iter_py(pack_dir):
        text = read_text(path)
        for m in CLASS_MAP_RE.finditer(text):
            brace = text.find("{", m.start())
            if brace < 0:
                continue
            block = matching_block(text, brace + 1)
            for key in KEY_RE.findall(block):
                found.setdefault(key, os.path.relpath(path, pack_dir))
    return found


def input_types_block(pack_dir, cls):
    """抓 class <cls> 的 INPUT_TYPES 段（到 RETURN_TYPES / RETURN_NAMES 为止）。"""
    pat = re.compile(r"\s*class\s+" + re.escape(cls) + r"\b")
    for path in iter_py(pack_dir):
        text = read_text(path)
        if not pat.search(text):
            continue
        out = []
        started = False
        for line in text.splitlines():
            if not started and pat.match(line):
                started = True
            if started:
                out.append(line.rstrip())
                if re.search(r"\bRETURN_(TYPES|NAMES)\b", line):
                    break
        if out:
            return "\n".join(out), os.path.relpath(path, pack_dir)
    return None, None


def param_names(block):
    """(required 段参数名, 该节点全部参数名)"""
    all_keys = set(KEY_RE.findall(block)) - SKIP_KEYS
    required = set()
    m = re.search(r"""["']required["']\s*:\s*\{""", block)
    if m:
        brace = block.find("{", m.start())
        required = set(KEY_RE.findall(matching_block(block, brace + 1))) - SKIP_KEYS
    return required, all_keys


def main(argv=None):
    ap = argparse.ArgumentParser(description="ComfyUI 同名节点撞车体检（只读）")
    ap.add_argument("pack_dirs", nargs="+", help="自定义节点包目录（≥1）")
    ap.add_argument("--class", dest="cls", default=None,
                    help="额外对比这个节点类的 INPUT_TYPES 参数名")
    ap.add_argument("--quiet", action="store_true", help="只打印撞车结论")
    args = ap.parse_args(argv)

    order = []
    maps = {}
    for d in args.pack_dirs:
        if not os.path.isdir(d):
            print("跳过（不是目录）: %s" % d)
            continue
        name = os.path.basename(os.path.normpath(d)) or d
        order.append((name, d))
        maps[name] = node_classes(d)

    if not maps:
        print("没有可检查的包目录。")
        return 0

    if not args.quiet:
        print("=== 各包注册的节点 ===")
        for name, _ in order:
            print("  %-45s %4d 个" % (name, len(maps[name])))

    owners = {}
    for name, _ in order:
        for cls in maps[name]:
            owners.setdefault(cls, []).append(name)

    clashes = {c: o for c, o in owners.items() if len(o) > 1}
    print()
    if not clashes:
        print("撞车结果: 无 ✅  这些包之间没有同名节点，可以共存。")
    else:
        print("撞车结果: %d 个同名节点 ⚠️" % len(clashes))
        for cls in sorted(clashes):
            print("  - %-42s <- %s" % (cls, ", ".join(clashes[cls])))
        print()
        print("同名 = 后加载者覆盖先加载者。下一步先查已存工作流有没有引用它们：")
        print('  grep -rl "<类名>" <ComfyUI>/user/default/workflows/')
        print("再 grep 新工作流用不用同名节点——不用则不致命（但两包仍互相覆盖）。")

    if args.cls:
        print()
        print("=== class %s 的 INPUT_TYPES 对比 ===" % args.cls)
        info = {}
        for name, d in order:
            block, src = input_types_block(d, args.cls)
            info[name] = (block, src)
            if block is None:
                print("\n[%s] 没有这个类\n" % name)
                continue
            required, all_keys = param_names(block)
            print("\n[%s]  源文件 %s" % (name, src))
            print("  required 参数: %s" % (", ".join(sorted(required)) or "(未识别)"))
            print("  全部参数    : %s" % (", ".join(sorted(all_keys)) or "(未识别)"))

        got = {n: v for n, v in info.items() if v[0]}
        if len(got) >= 2:
            names = list(got)
            base_req, base_all = param_names(got[names[0]][0])
            print()
            print("--- 差异判定（基准 = %s）---" % names[0])
            same = True
            for other in names[1:]:
                req, all_keys = param_names(got[other][0])
                extra = sorted(req - base_req)
                missing = sorted(base_req - req)
                extra_all = sorted(all_keys - base_all)
                missing_all = sorted(base_all - all_keys)
                if not (extra or missing or extra_all or missing_all):
                    print("  %s: 参数名一致 ✅（仍可能默认值/取值范围不同，需人工核）" % other)
                    continue
                same = False
                print("  %s: 参数表不同代 ❌" % other)
                if extra_all:
                    print("      多出: %s" % ", ".join(extra_all))
                if missing_all:
                    print("      缺少: %s" % ", ".join(missing_all))
                if extra:
                    print("      (required 多出: %s)" % ", ".join(extra))
                if missing:
                    print("      (required 缺少: %s)" % ", ".join(missing))
                print("      → 同名类互不兼容：两包不能同时生效，引用它的已存工作流会参数错位")
            if same and len(names) > 1:
                print("  结论：至少参数名同代，但仍要核 default / min / max / 枚举值是否一致")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
