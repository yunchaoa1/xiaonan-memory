#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""dy_grab_audio.py —— 长视频专用：抓抖音分离的音轨 → 下载 → 转写

为什么: 长视频(>~10min)抖音音视频分轨，dy_transcribe.py 只拿到 video 轨。
       本脚本用 Camoufox 真页面截获 media-audio-* 请求，立即下载(URL 带签名会过期)，
       再用本地 faster-whisper medium 离线转写。

用法: python dy_grab_audio.py "<视频页URL>" [输出前缀]
"""
import re
import sys
import time
import urllib.request

from camoufox.sync_api import Camoufox

url = sys.argv[1] if len(sys.argv) > 1 else ""
prefix = sys.argv[2] if len(sys.argv) > 2 else "dy_audio"
if not url:
    sys.exit("用法: python dy_grab_audio.py <URL> [前缀]")

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")

audio_url = None
with Camoufox(headless=True, humanize=True) as b:
    p = b.new_page()
    caps = []
    p.on("request", lambda r: caps.append(r.url))
    p.goto(url, wait_until="domcontentloaded", timeout=90000)
    p.wait_for_timeout(10000)
    try:
        p.evaluate("() => { const v=document.querySelector('video'); if(v){v.muted=true; v.play().catch(()=>{});} }")
        p.wait_for_timeout(8000)
    except Exception:
        pass
    audios = [u for u in caps if "media-audio" in u or "/audio/tos/" in u]
    if audios:
        audio_url = sorted(audios, key=len, reverse=True)[0]

if not audio_url:
    sys.exit("✗ 没截到音轨 URL")

print(f"✓ 音轨 URL 已截到（{len(audio_url)} 字符）")
m4a = f"{prefix}.m4a"
req = urllib.request.Request(audio_url, headers={"User-Agent": UA, "Referer": "https://www.douyin.com/"})
t0 = time.time()
with urllib.request.urlopen(req, timeout=300) as r, open(m4a, "wb") as f:
    while True:
        chunk = r.read(1 << 20)
        if not chunk:
            break
        f.write(chunk)
import os
print(f"✓ 下载完成 {os.path.getsize(m4a)/1048576:.1f} MB -> {m4a}  ({time.time()-t0:.0f}s)")

# 转 wav（whisper 友好）
import subprocess
wav = f"{prefix}.wav"
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", m4a, "-ar", "16000", "-ac", "1", wav], check=True)
print(f"✓ 转 wav 完成 -> {wav}")

# 本地 whisper 转写
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("OMP_NUM_THREADS", "8")
from faster_whisper import WhisperModel

print("… 转写中（medium 离线）")
model = WhisperModel("medium", device="cpu", compute_type="int8")
segments, info = model.transcribe(wav, language="zh", vad_filter=True, beam_size=5)
lines = []
for seg in segments:
    line = f"[{seg.start:6.1f}s] {seg.text.strip()}"
    lines.append(line)
    print(line, flush=True)

txt = f"{prefix}.zh.txt"
with open(txt, "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")
print(f"\n✓ 转写完成 {len(lines)} 段 -> {txt}")
