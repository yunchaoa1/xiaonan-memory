#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""模型文件完整性校验：字节数比对 + safetensors 头解析。

为什么需要它：`ls -la` / `du -h` 只能证明"文件在那儿/大概那么大"，
证明不了"能加载"。真正能定论的两件事是——
  ① 本地字节数 == 官方发布的精确字节数（HF API `?blobs=true` 给的是 LFS 精确值）
  ② safetensors 头（前 8 字节 = 小端 uint64 头长度，其后是 JSON）能解析出张量表
一个 0 字节文件、半截文件、或"字节数对但内容坏"的文件，只有 ② 能兜住。

用法 A —— 本地清单（不联网，最快）:
    python verify_model_files.py <文件> <期望字节> [<文件> <期望字节> ...]

用法 B —— 对 HF 仓库核对（自动走 hf-mirror，国内直连可用）:
    python verify_model_files.py --hf smhfacct/Minimax-H3-fl2va-ref2va-hybrid-models \
        --local-dir D:/SDkecheng/ComfyUI/models/diffusion_models/minimax_h3

用法 C —— 只验头（不比对大小；批量扫一个目录）:
    python verify_model_files.py --header-only <目录或文件> [<更多>...]

退出码：0 = 全部通过；1 = 有任一文件不通过（方便脚本串起来）。
"""
from __future__ import annotations

import argparse
import json
import os
import struct
import sys
import urllib.request

HF_MIRROR = "https://hf-mirror.com"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126 Safari/537.36"


def human(n: int) -> str:
    return f"{n:,}"


def read_safetensors_header(path: str) -> dict:
    """解析 safetensors 头。

    返回 {"ok": True, "n_tensors": int, "has_metadata": bool} 或
         {"ok": False, "error": str}
    """
    try:
        size = os.path.getsize(path)
        if size < 8:
            return {"ok": False, "error": f"文件 <8 字节（实际 {size}B）"}
        with open(path, "rb") as f:
            raw = f.read(8)
            (hdr_len,) = struct.unpack("<Q", raw)
            # 头长度本身必须落在文件内，且不该是天文数字
            if hdr_len <= 0 or hdr_len + 8 > size:
                return {
                    "ok": False,
                    "error": f"头长度 {human(hdr_len)} 超出文件范围（文件 {human(size)}B）→ 半截/损坏",
                }
            if hdr_len > 100 * 1024 * 1024:
                return {"ok": False, "error": f"头长度 {human(hdr_len)}B 离谱 → 大概率不是 safetensors"}
            hdr = json.loads(f.read(hdr_len).decode("utf-8"))
    except json.JSONDecodeError as e:
        return {"ok": False, "error": f"头不是合法 JSON：{e}"}
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "error": f"{type(e).__name__}: {e}"}

    has_meta = "__metadata__" in hdr
    n = len(hdr) - (1 if has_meta else 0)
    if n <= 0:
        return {"ok": False, "error": "头里没有任何张量"}
    return {"ok": True, "n_tensors": n, "has_metadata": has_meta}


def hf_sizes(repo: str, timeout: int = 60) -> dict:
    """取 HF 仓库每个文件的官方精确字节数（basename -> size）。"""
    url = f"{HF_MIRROR}/api/models/{repo}?blobs=true"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        data = json.load(r)
    out = {}
    for s in data.get("siblings", []):
        fn = s.get("rfilename") or ""
        sz = s.get("size")
        if fn and sz is not None:
            out[os.path.basename(fn)] = int(sz)
    return out


def check(path: str, expected: int | None, header_only: bool = False) -> bool:
    name = os.path.basename(path)
    if not os.path.exists(path):
        print(f"  ❌ {name:<58} 文件不存在")
        return False

    local = os.path.getsize(path)
    ok = True

    if expected is not None and not header_only:
        match = local == expected
        ok &= match
        flag = "✅ 一致" if match else f"❌ 差 {local - expected:+,}"
        print(f"  {'✅' if match else '❌'} {name:<58} {human(local):>16} / {human(expected):>16}  {flag}")
    else:
        print(f"  ℹ️  {name:<58} {human(local):>16}")

    hdr = read_safetensors_header(path)
    if hdr["ok"]:
        meta = "（含 __metadata__）" if hdr["has_metadata"] else ""
        print(f"      文件头: ✅ 合法，{human(hdr['n_tensors'])} 张量{meta}")
    else:
        ok = False
        print(f"      文件头: ❌ {hdr['error']}")

    return ok


def expand(paths: list[str]) -> list[str]:
    """把目录展开成其中的模型文件（按扩展名）。"""
    exts = (".safetensors", ".gguf", ".pth", ".pt", ".bin", ".ckpt")
    out = []
    for p in paths:
        if os.path.isdir(p):
            for root, _dirs, files in os.walk(p):
                out += [os.path.join(root, f) for f in sorted(files) if f.lower().endswith(exts)]
        else:
            out.append(p)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="模型文件完整性校验（字节 + safetensors 头）")
    ap.add_argument("pairs", nargs="*", help="用法A：<文件> <期望字节> 交替传入")
    ap.add_argument("--hf", metavar="REPO", help="用法B：对 HF 仓库核对官方字节数")
    ap.add_argument("--local-dir", default=".", help="用法B：本地目录（默认当前目录）")
    ap.add_argument("--header-only", nargs="*", metavar="PATH", help="用法C：只验文件头")
    args = ap.parse_args()

    # 用法 C
    if args.header_only is not None:
        targets = expand(args.header_only or ["."])
        if not targets:
            print("没找到任何模型文件")
            return 1
        print(f"=== 只验文件头（{len(targets)} 个）===")
        return 0 if all(check(t, None, header_only=True) for t in targets) else 1

    # 用法 B
    if args.hf:
        try:
            sizes = hf_sizes(args.hf)
        except Exception as e:  # noqa: BLE001
            print(f"取 HF 清单失败：{type(e).__name__}: {e}")
            return 1
        misses = []
        for fn, sz in sorted(sizes.items()):
            p = os.path.join(args.local_dir, fn)
            if os.path.exists(p):
                misses.append((p, sz))
        if not misses:
            print(f"本地目录里没有 {args.hf} 的任何文件：{os.path.abspath(args.local_dir)}")
            print("官方文件清单：")
            for fn, sz in sorted(sizes.items()):
                print(f"  {fn}  {human(sz)}")
            return 1
        print(f"=== 对 {args.hf} 核对（{len(misses)} 个）===")
        return 0 if all(check(p, sz) for p, sz in misses) else 1

    # 用法 A
    if len(args.pairs) % 2 != 0:
        print("用法A 需要成对传入：<文件> <期望字节> ...")
        return 1
    if not args.pairs:
        ap.print_help()
        return 1
    ok = True
    print(f"=== 本地清单核对（{len(args.pairs) // 2} 个）===")
    for i in range(0, len(args.pairs), 2):
        ok &= check(args.pairs[i], int(args.pairs[i + 1]))
    print("\n" + ("全部通过 ✅" if ok else "有文件未通过 ❌"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
