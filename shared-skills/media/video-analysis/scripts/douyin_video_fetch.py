#!/usr/bin/env python
"""抓取抖音单条视频的文案与媒体流（无登录、无 cookie、无代理）。

用法:
    python douyin_video_fetch.py <video_id 或 完整链接> [输出目录]

输出:
    1) stdout: JSON —— 标题 / meta description（含完整文案 + 发布方 + 发布日期）/ ID 解码的发布时刻
    2) 输出目录下 video.mp4 / audio.mp4（音视频分离，抽帧只需 video.mp4）

原理:
    web_extract 抓抖音页面只会拿到混淆 JS（_$jsvmprt…）；
    真实 Chromium 渲染后才拿得到标题、meta 与 douyinvod 媒体流。
    媒体 URL 带时效签名 —— 捕获后必须立刻下载。
"""
import json
import os
import re
import sys
import time
from datetime import datetime, timedelta, timezone

from playwright.sync_api import sync_playwright

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
CN = timezone(timedelta(hours=8))


def posted_at(vid: str) -> str:
    """抖音 snowflake ID 高 32 位 = Unix 秒。"""
    return datetime.fromtimestamp(int(vid) >> 32, CN).strftime("%Y-%m-%d %H:%M:%S +08")


def main(raw: str, outdir: str) -> None:
    m = re.search(r"(\d{15,20})", raw)
    if not m:
        sys.exit(f"无法从 {raw!r} 解析出视频 ID")
    vid = m.group(1)
    url = f"https://www.douyin.com/video/{vid}"
    os.makedirs(outdir, exist_ok=True)

    media = {"video": [], "audio": []}

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True, args=["--disable-blink-features=AutomationControlled"]
        )
        ctx = browser.new_context(locale="zh-CN", user_agent=UA,
                                  viewport={"width": 1400, "height": 950})
        page = ctx.new_page()

        def on_response(r):
            u = r.url
            if "douyinvod" in u or "douyinstatic" in u:
                if "media-video" in u:
                    media["video"].append(u)
                elif "media-audio" in u:
                    media["audio"].append(u)

        page.on("response", on_response)
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        time.sleep(6)
        # 媒体流只有在播放开始后才发出请求
        try:
            page.evaluate("document.querySelector('video')?.play()")
        except Exception as exc:  # 自动播放被拦也不影响后续重试
            print(f"[warn] play() 失败: {exc}", file=sys.stderr)
        time.sleep(6)

        info = {
            "url": url,
            "video_id": vid,
            "posted_at": posted_at(vid),
            "title": page.title(),
            "meta_description": page.evaluate(
                "document.querySelector('meta[name=description]')?.content"
            ),
        }
        print(json.dumps(info, ensure_ascii=False, indent=2))

        for kind, urls in media.items():
            if not urls:
                print(f"[warn] 未捕获到 {kind} 流（页面可能未播放）", file=sys.stderr)
                continue
            body = ctx.request.get(
                urls[-1], headers={"Referer": "https://www.douyin.com/"}
            ).body()
            path = os.path.join(outdir, f"{kind}.mp4")
            with open(path, "wb") as fh:
                fh.write(body)
            head = body[:16]
            ok = b"ftyp" in head  # 校验确实是媒体文件
            print(f"saved {kind} {len(body)} bytes -> {path} (valid_mp4={ok})")

        ctx.close()
        browser.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "D:/Hermes/cache/douyin")
