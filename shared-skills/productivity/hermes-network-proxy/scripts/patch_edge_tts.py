#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
patch_edge_tts.py —— 修复 edge-tts 语音合成 403（2026-10 微软换接口）

背景（2026-10-12 实测）:
    微软 Edge「大声朗读」的合成 WebSocket 从
        wss://speech.platform.bing.com/consumer/speech/synthesize/readaloud/edge/v1
    迁到新地址，老地址自 2026-10 起对多数地区返回 403，2026-10-12 起美国也 403。
    Edge 155 走的新地址 = api.msedgeservices.com/tts/cognitiveservices/websocket/v1
    新地址同样接受老 token，但要以 Ocp-Apim-Subscription-Key 传。
    音色列表接口（VOICE_LIST）仍在老地址正常工作，不要改。

上游: rany2/edge-tts PR #491（本脚本落地时尚未合并进 7.2.8）。

为什么需要脚本（而不是改一次就完）:
    `pip install -U edge-tts` 会覆盖 constants.py，补丁丢失 → 语音播报再次 403。
    任何 edge-tts 升级后重跑本脚本即可。幂等，可反复执行。

⚠️ 跑完必须重启 Hermes 桌面 App —— edge_tts 是 App 进程里懒加载的，
   进程不重启则内存中仍是老常量（磁盘改了也不生效）。实测过。

用法:
    python D:/Hermes/scripts/patch_edge_tts.py            # 打补丁（幂等）
    python D:/Hermes/scripts/patch_edge_tts.py --verify   # 只看状态并真实合成一条
    python D:/Hermes/scripts/patch_edge_tts.py --revert   # 还原备份
"""

import argparse
import datetime as _dt
import glob
import os
import shutil
import sys

VENV_GLOBS = [
    r"D:\Hermes\hermes-agent\venv\Lib\site-packages\edge_tts\constants.py",
    r"D:\Hermes\hermes-agent\venv\Lib\site-packages\edge_tts\constants.py",
    r"D:\Hermes\**\Lib\site-packages\edge_tts\constants.py",
]

OLD_LINE_FRAGMENT = 'WSS_URL = f"wss://{BASE_URL}/edge/v1?TrustedClientToken={TRUSTED_CLIENT_TOKEN}"'
NEW_BLOCK = '''# --- local patch (upstream rany2/edge-tts#491, not merged as of 7.2.8) ---
# Since October 2026 the legacy host refuses speech synthesis with a 403.
# Microsoft Edge 155 synthesizes through api.msedgeservices.com, which also
# accepts the legacy token, given as Ocp-Apim-Subscription-Key. The voice
# list is still served by the legacy host.
# NOTE: `pip install -U edge-tts` overwrites this -- re-run
#       D:\\Hermes\\scripts\\patch_edge_tts.py afterwards.
WSS_URL = (
    "wss://api.msedgeservices.com/tts/cognitiveservices/websocket/v1"
    f"?Ocp-Apim-Subscription-Key={TRUSTED_CLIENT_TOKEN}"
)'''
MARKER = "edge-tts#491"          # 出现在磁盘上的补丁注释里
NEW_MARKER_FALLBACK = "msedgeservices.com/tts/cognitiveservices"  # 双重判定


def find_constants():
    seen, out = set(), []
    for g in VENV_GLOBS:
        for p in glob.glob(g, recursive=True):
            p = os.path.normpath(p)
            if p not in seen and os.path.isfile(p):
                seen.add(p)
                out.append(p)
    return out


def status(path):
    src = open(path, encoding="utf-8").read()
    if MARKER in src or NEW_MARKER_FALLBACK in src:
        return "patched"
    if OLD_LINE_FRAGMENT in src:
        return "unpatched"
    return "unknown"


def apply(path):
    st = status(path)
    if st == "patched":
        return "already patched", True
    if st == "unknown":
        return "!! 找不到老 WSS_URL 行，文件结构与预期不符，未改动（人工看一下）", False
    bak = path + ".bak-" + _dt.datetime.now().strftime("%Y%m%d")
    if not os.path.exists(bak):
        shutil.copy2(path, bak)
    src = open(path, encoding="utf-8").read()
    open(path, "w", encoding="utf-8", newline="").write(
        src.replace(OLD_LINE_FRAGMENT, NEW_BLOCK)
    )
    return ("patched (备份 %s)" % os.path.basename(bak)), True


def revert(path):
    baks = sorted(glob.glob(path + ".bak-*"))
    if not baks:
        return "没有备份，无法还原", False
    shutil.copy2(baks[-1], path)
    return "reverted from " + os.path.basename(baks[-1]), True


def verify():
    """新进程里真实合成一条，确认能出声。"""
    try:
        import asyncio
        import edge_tts
        import edge_tts.communicate as CM
    except Exception as e:
        return "!! import edge_tts 失败: %r" % (e,), False
    print("  实际使用的 WSS_URL:", CM.WSS_URL.split("?")[0])
    if "msedgeservices" not in CM.WSS_URL:
        return "!! 仍是老地址 —— 补丁没生效（或忘了重启 App）", False
    out = os.path.join(
        os.environ.get("LOCALAPPDATA", "."), "Temp",
        "edge_tts_verify_%s.mp3" % _dt.datetime.now().strftime("%H%M%S"),
    )
    try:
        async def _go():
            c = edge_tts.Communicate("语音播报自检，一切正常。", "zh-CN-XiaoxiaoNeural")
            await c.save(out)
        asyncio.run(_go())
    except Exception as e:
        return "!! 合成失败: %r" % (e,), False
    n = os.path.getsize(out) if os.path.exists(out) else 0
    return "合成成功: %s (%d 字节)" % (out, n), n > 1000


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verify", action="store_true", help="只看状态并真实合成一条")
    ap.add_argument("--revert", action="store_true", help="还原备份")
    a = ap.parse_args()

    targets = find_constants()
    if not targets:
        print("!! 没找到 edge_tts/constants.py，检查 venv 路径")
        return 2
    print("找到 %d 个 edge_tts/constants.py" % len(targets))

    ok_all = True
    for p in targets:
        st = status(p)
        print("\n[%s] %s" % (st, p))
        if a.verify:
            msg, ok = verify()
            print("   ", msg)
            ok_all &= ok
            continue
        msg, ok = (revert(p) if a.revert else apply(p))
        ok_all &= ok
        print("   ", msg)
        if a.revert and ok:
            continue
        msg, ok = verify()
        print("   ", msg)
        ok_all &= ok

    print("\n" + "=" * 60)
    if ok_all:
        print("✅ 全部就绪")
        print("⚠️  如果 Hermes 桌面 App 在补丁之前就已启动 → 必须重启 App 才生效")
        print("    判断方法: 让 Hermes 播报一次；仍报 403 speech.platform.bing.com = 没重启")
    else:
        print("❌ 有问题，见上面输出")
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())
