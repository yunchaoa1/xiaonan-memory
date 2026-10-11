#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""dy_audio_transcribe.py —— 抖音视频：截直链 → 下载 → 提音频 → 转写

为什么需要它：抓取页面只能拿到**文案和评论**，博主**口播的内容**必须转写音频才能听到。
流程：Camoufox 截获视频直链 → urllib 下载 → ffmpeg 提 16k 单声道 wav → faster-whisper 转写。

用法: python dy_audio_transcribe.py "<抖音视频页URL>"
"""
import os
import re
import subprocess
import sys
import urllib.request

CACHE = r"D:\Hermes\cache"
VIDEO_URL = sys.argv[1] if len(sys.argv) > 1 else ""
if not VIDEO_URL:
    print("用法: python dy_audio_transcribe.py <抖音视频页URL>")
    sys.exit(1)
m = re.search(r"/video/(\d+)", VIDEO_URL)
TAG = m.group(1)[:12] if m else "vid"

# ---------- 1) 用 Camoufox 截获视频真实直链 ----------
from camoufox.sync_api import Camoufox

found = []


def _grab(req):
    u = req.url
    if re.search(r"douyinvod|/video/tos/", u):
        found.append(u)


with Camoufox(headless=True) as b:
    page = b.new_page()
    page.on("request", _grab)
    page.goto(VIDEO_URL, wait_until="domcontentloaded", timeout=70000)
    page.wait_for_timeout(9000)
    try:
        src = page.eval_on_selector("video", "el => el.src")
        if src:
            found.append(src)
    except Exception:
        pass

cands = [u for u in set(found) if "douyinvod" in u or "/video/tos/" in u]
if not cands:
    print("FAIL 没抓到视频直链（可能需登录）")
    sys.exit(1)
best = max(cands, key=len)
print("OK 抓到直链（长度 %d）" % len(best))

# ---------- 2) 下载 ----------
mp4 = os.path.join(CACHE, "dyv_%s.mp4" % TAG)
req = urllib.request.Request(best, headers={
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://www.douyin.com/",
})
with urllib.request.urlopen(req, timeout=180) as r, open(mp4, "wb") as f:
    while True:
        chunk = r.read(1 << 20)
        if not chunk:
            break
        f.write(chunk)
print("OK 视频 %d 字节" % os.path.getsize(mp4))

# ---------- 3) ffmpeg 提音频 ----------
wav = os.path.join(CACHE, "dyv_%s.wav" % TAG)
subprocess.run(["ffmpeg", "-y", "-i", mp4, "-vn", "-ac", "1", "-ar", "16000", wav],
               capture_output=True)
print("OK 音频 %d 字节" % os.path.getsize(wav))

# ---------- 4) faster-whisper 转写 ----------
from faster_whisper import WhisperModel

model = WhisperModel("large-v3", device="cpu", compute_type="int8")
segs, info = model.transcribe(wav, language="zh", vad_filter=True)
txt = "".join(s.text for s in segs)
out = os.path.join(CACHE, "dyv_%s.txt" % TAG)
with open(out, "w", encoding="utf-8") as f:
    f.write(txt)
print("=== 转写结果（%d 字）===" % len(txt))
print(txt)
