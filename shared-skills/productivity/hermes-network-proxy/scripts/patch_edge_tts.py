#!/usr/bin/env python
"""确保 Hermes 的 edge TTS 语音播报可用（幂等）。

2026-10-27 定论：403 的正解是 edge-tts >= 7.3.0（PR #492 Sec-MS-GEC v2 令牌）。
早期"把 WSS_URL 改成 api.msedgeservices.com"的打法已废弃 —— 那个网关会把公共
TRUSTED_CLIENT_TOKEN 当订阅键，频繁 429 限流。

用法：
    python patch_edge_tts.py            # 确保 >= 7.3（必要时升级）+ 真实合成自检
    python patch_edge_tts.py --verify   # 只查状态 + 试合成
    python patch_edge_tts.py --revert   # 强制重装官方 wheel，冲掉任何手改

退出码 0 = 可用。
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile

VENV_PY = r"D:\Hermes\hermes-agent\venv\Scripts\python.exe"
TARGET_VERSION = "7.3.1"
MIN_VERSION = (7, 3, 0)
LEGACY_HOST_MARKER = "msedgeservices.com"

PROBE = r'''
import json, edge_tts
c = edge_tts.constants
print(json.dumps({
    "version": getattr(edge_tts, "__version__", "?"),
    "path": edge_tts.__file__,
    "wss_url": c.WSS_URL,
    "gec_version": getattr(c, "SEC_MS_GEC_VERSION", ""),
}))
'''

SYNTH = r'''
import asyncio, os, sys, tempfile
import edge_tts
out = os.path.join(tempfile.gettempdir(), "edge_tts_selfcheck.mp3")
if os.path.exists(out):
    os.remove(out)
asyncio.run(edge_tts.Communicate("语音播报自检，一二三四五。", "zh-CN-XiaoxiaoNeural").save(out))
print(os.path.getsize(out))
'''


def py() -> str:
    return VENV_PY if os.path.exists(VENV_PY) else sys.executable


def run(code: str, timeout: int = 180) -> subprocess.CompletedProcess:
    return subprocess.run(
        [py(), "-c", code], capture_output=True, text=True, timeout=timeout
    )


def probe() -> dict:
    import json

    p = run(PROBE, timeout=90)
    if p.returncode != 0:
        return {"error": (p.stderr or p.stdout).strip().splitlines()[-1:] or ["unknown"]}
    try:
        return json.loads(p.stdout.strip().splitlines()[-1])
    except Exception:
        return {"error": p.stdout.strip()[:200]}


def vtuple(v: str):
    try:
        return tuple(int(x) for x in v.split(".")[:3])
    except Exception:
        return (0, 0, 0)


def install(force: bool = False) -> bool:
    args = [py(), "-m", "pip", "install", "--no-deps"]
    args += ["--force-reinstall"] if force else ["-U"]
    args.append(f"edge-tts=={TARGET_VERSION}")
    print("→", " ".join(args))
    p = subprocess.run(args, capture_output=True, text=True, timeout=600)
    ok = p.returncode == 0
    tail = (p.stdout or "").strip().splitlines()[-2:]
    print("\n".join(tail) if tail else (p.stderr or "")[:400])
    return ok


def synthesize() -> tuple[bool, str]:
    p = run(SYNTH, timeout=180)
    if p.returncode == 0:
        n = p.stdout.strip().splitlines()[-1]
        return True, f"合成成功 {n} 字节"
    err = (p.stderr or p.stdout).strip().splitlines()
    return False, (err[-1] if err else "未知错误")


def report(info: dict) -> None:
    if info.get("error"):
        print(f"  ⚠️  探测失败: {info['error']}")
        return
    print(f"  版本    : {info['version']}")
    print(f"  路径    : {info['path']}")
    print(f"  GEC 代次: {info.get('gec_version') or '(无)'}")
    url = info.get("wss_url") or ""
    host = url.split("://")[-1].split("/")[0] if "://" in url else "(空)"
    print(f"  合成域名: {host}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--verify", action="store_true", help="只查状态 + 试合成")
    ap.add_argument("--revert", action="store_true", help="强制重装官方 wheel")
    a = ap.parse_args()

    print("=" * 60)
    info = probe()
    print("当前状态：")
    report(info)

    if a.verify:
        ok, msg = synthesize()
        print(f"\n自检：{'✅' if ok else '❌'} {msg}")
        return 0 if ok else 1

    needs_install = a.revert
    if not info.get("error"):
        ver = info.get("version", "0")
        legacy = LEGACY_HOST_MARKER in (info.get("wss_url") or "")
        gec = info.get("gec_version") or ""
        if legacy:
            print("\n⚠️  检测到 2026-10 的旧手改（WSS_URL 指向新域名）—— 那会引发 429，必须冲掉")
            needs_install = True
        if vtuple(ver) < MIN_VERSION:
            print(f"\n⚠️  版本 {ver} < 7.3.0（缺 v2 令牌 = 403 根因）")
            needs_install = True
        if gec and not gec.startswith("2-"):
            print(f"\n⚠️  SEC_MS_GEC_VERSION = {gec!r}，不是 v2 代次")
            needs_install = True
        if not (needs_install):
            print("\n✅ 版本与令牌代次都对，无需改动")

    if needs_install:
        print("\n→ 安装官方版本…")
        if not install(force=a.revert):
            print("❌ 安装失败，见上面 pip 输出")
            return 1
        info = probe()
        print("\n安装后：")
        report(info)

    ok, msg = synthesize()
    print(f"\n自检：{'✅' if ok else '❌'} {msg}")
    print("=" * 60)
    print("✅ 全部就绪" if ok else "❌ 自检失败")
    if ok:
        print("⚠️  若 Hermes 桌面 App 在安装之前就已启动 → 必须重启 App 才生效")
        print("    一键彻底重启：powershell -File D:\\Hermes\\scripts\\restart_hermes_app.ps1 -DelaySeconds 5")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
