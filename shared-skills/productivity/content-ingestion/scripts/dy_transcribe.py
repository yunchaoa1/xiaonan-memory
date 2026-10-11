#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""dy_transcribe.py —— 抖音视频：截直链 → 下载 → 提音频 → 转写

为什么需要它：抓页面只能拿到**文案和评论**，博主**口播的内容**必须转写音频才能听到。
流程：Camoufox 截获视频直链 → urllib 下载 → ffmpeg 提 16k 单声道 wav → faster-whisper 转写

用法:
    python dy_transcribe.py "<抖音视频页URL>"

实测踩过的坑（2026-10-11）:
  1. yt-dlp 读 Chrome cookie 常被锁（Chrome 正在运行）→ 改用 Camoufox 截 request 直链
  2. HuggingFace 直连超时 → 用本地已缓存的模型 + HF_HUB_OFFLINE=1
  3. large-v3 缓存为空壳（下过但没下完）→ medium / small 是完整的，优先用它们
"""
import os
import re
import glob
import subprocess
import sys
import urllib.request

os.environ.setdefault("HF_HUB_OFFLINE", "1")   # 强制用本地缓存，避免 HF 直连超时

CACHE = r"D:\Hermes\cache"
os.makedirs(CACHE, exist_ok=True)


def pick_whisper_model():
    """挑一个本地完整的 faster-whisper 模型目录；找不到就退回名字（会走下载）。"""
    hub = os.path.expanduser(r"~\.cache\huggingface\hub")
    for name in ("medium", "small", "large-v3"):
        pat = os.path.join(hub, f"models--Systran--faster-whisper-{name}", "snapshots", "*")
        for snap in glob.glob(pat):
            # 必须真的有权重文件才算“完整”
            if glob.glob(os.path.join(snap, "*.bin")) or glob.glob(os.path.join(snap, "model.bin")):
                return snap, name
    return "medium", "medium(未找到本地缓存)"


def camoufox_video_url(page_url: str) -> str | None:
    """用 Camoufox 打开视频页，从网络请求里截获视频直链。"""
    from camoufox.sync_api import Camoufox

    found = []
    with Camoufox(headless=True) as b:
        p = b.new_page()
        p.on("request", lambda r: found.append(r.url)
             if re.search(r"douyinvod|/video/tos/|\.mp4", r.url) else None)
        p.goto(page_url, wait_until="domcontentloaded", timeout=70000)
        p.wait_for_timeout(9000)
        try:
            src = p.eval_on_selector("video", "el => el.src")
            if src:
                found.append(src)
        except Exception:
            pass

    cands = [u for u in set(found) if ("douyinvod" in u or "/video/tos/" in u)]
    cands.sort(key=len, reverse=True)
    return cands[0] if cands else None


def download(url: str, dest: str) -> int:
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://www.douyin.com/",
    })
    with urllib.request.urlopen(req, timeout=180) as r, open(dest, "wb") as f:
        while True:
            chunk = r.read(1 << 20)
            if not chunk:
                break
            f.write(chunk)
    return os.path.getsize(dest)


def main() -> int:
    if len(sys.argv) < 2:
        print("用法: python dy_transcribe.py <视频页URL>")
        return 2
    page_url = sys.argv[1]
    m = re.search(r"/(?:video|modal_id=|note)/(\d+)", page_url)
    tag = m.group(1)[:14] if m else "vid"

    # 1) 截直链
    direct = camoufox_video_url(page_url)
    if not direct:
        print("FAIL 没截到视频直链（站点结构可能变了，或需要登录）")
        return 1
    print(f"OK 截到直链（长度 {len(direct)}）")

    # 2) 下载
    mp4 = os.path.join(CACHE, f"dyv_{tag}.mp4")
    if not (os.path.exists(mp4) and os.path.getsize(mp4) > 100_000):
        print(f"OK 视频 {download(direct, mp4):,} 字节 -> {mp4}")
    else:
        print(f"SKIP 已有视频 {os.path.getsize(mp4):,} 字节")

    # 3) 提音频
    wav = os.path.join(CACHE, f"dyv_{tag}.wav")
    subprocess.run(["ffmpeg", "-y", "-i", mp4, "-vn", "-ac", "1", "-ar", "16000", wav],
                   capture_output=True)
    print(f"OK 音频 {os.path.getsize(wav):,} 字节 -> {wav}")

    # 4) 转写
    from faster_whisper import WhisperModel
    model_path, model_name = pick_whisper_model()
    print(f"转写模型: {model_name}")
    model = WhisperModel(model_path, device="cpu", compute_type="int8")
    segs, info = model.transcribe(wav, language="zh", vad_filter=True)

    lines = []
    for s in segs:
        lines.append(f"[{s.start:6.1f}s] {s.text}")
    txt = "\n".join(lines)
    out = os.path.join(CACHE, f"dyv_{tag}.txt")
    with open(out, "w", encoding="utf-8") as f:
        f.write(txt)

    print(f"=== 口播转写（{len(txt)} 字符）-> {out} ===")
    print(txt)
    return 0


if __name__ == "__main__":
    sys.exit(main())
