#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""dy_page.py —— 抖音视频页：抓 HTML + 全文文字 + 内嵌元数据

为什么需要它：camoufox_probe.py 只打印正文前 400 字，抖音的正文开头全是页脚/导航，
真正有用的【视频标题·文案·点赞数·发布会·评论区】在中段，必须整页存下来再提取。

用法:
    python dy_page.py "<抖音视频页URL>"

输出（写到 D:\\Hermes\\cache）:
    dy_page_<tag>.html  整页 HTML（1.5MB 左右，留给后续正则挖数据）
    dy_page_<tag>.txt   整页可见文字（标题/文案/评论/推荐位都在里面）
    同时打印内嵌 JSON 里的 desc / nickname / statistics

实测（2026-10-14）:
  - 凡哥给的分享链接形如 https://www.douyin.com/user/self?...&modal_id=<id>
    → 换成 https://www.douyin.com/video/<id> 更稳，标题/文案/评论能直接抓到
  - 页面需等 ~8s 才渲染出视频信息，goto 后必须 wait
"""
import re
import sys

CACHE = r"D:\Hermes\cache"

URL = sys.argv[1] if len(sys.argv) > 1 else ""
if not URL:
    print("用法: python dy_page.py <抖音视频页URL>")
    sys.exit(2)

# 支持 /video/<id> 或 ...modal_id=<id>
m = re.search(r"/video/(\d+)", URL) or re.search(r"modal_id=(\d+)", URL)
tag = m.group(1)[:14] if m else "vid"

from camoufox.sync_api import Camoufox

# 抖音是 SPA，主视频区是否渲染出来每次都不同（登录态/风控/网络波动都会影响）。
# 2026-10-14 实测：同一 URL 三次访问，可见文字分别是 4579 / 3249 / 1637 字符，
# 有一次只有页脚。故重试最多 3 次，取"文字最丰富"的那次，避免抓了个空壳还以为没内容。
html, text = "", ""
with Camoufox(headless=True, humanize=True) as b:
    page = b.new_page()
    for attempt in range(3):
        if attempt == 0:
            page.goto(URL, wait_until="domcontentloaded", timeout=70000)
        else:
            page.reload(wait_until="domcontentloaded", timeout=70000)
        page.wait_for_timeout(8000)
        cur_text = page.inner_text("body")
        print(f"  第{attempt + 1}次取到 {len(cur_text):,} 字符")
        if len(cur_text) > len(text):
            text = cur_text
            html = page.content()
        if len(text) > 3000:      # 已经足够丰富，不必再试
            break

html_out = rf"{CACHE}\dy_page_{tag}.html"
txt_out = rf"{CACHE}\dy_page_{tag}.txt"
with open(html_out, "w", encoding="utf-8") as f:
    f.write(html)
with open(txt_out, "w", encoding="utf-8") as f:
    f.write(text)
print(f"OK HTML {len(html):,} 字节 -> {html_out}")
print(f"OK TEXT {len(text):,} 字符 -> {txt_out}")

# 内嵌 JSON 里的元数据：抖音主视频数据多在 XHR 里、HTML 里只有推荐流 SSR，
# 硬挖正则不稳（2026-10-14 实测：desc 会匹配到推荐位别的视频）。
# 可靠做法 = 从渲染后的可见文字里挑长行（标题·文案·评论都在这），HTML 留着备查。
print("\n--- 正文长行（标题/文案/评论候选，>25 字）---")
seen = set()
for ln in text.splitlines():
    ln = ln.strip()
    if len(ln) > 25 and ln not in seen:
        seen.add(ln)
        print("  " + ln[:200])
