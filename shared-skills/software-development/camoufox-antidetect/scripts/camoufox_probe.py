#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""camoufox_probe.py —— Camoufox 反检测浏览器探针

验证三件事：
  1. 浏览器能否启动（二进制装好了吗）
  2. 普通站点能否抓到（基本功能）
  3. 强反爬站（抖音/头条）能否抓到 —— 这是它存在的意义

用法: python camoufox_probe.py [url ...]
默认测：blogs / douyin / toutiao
"""
import sys
import time

TARGETS = sys.argv[1:] or [
    "https://www.cnblogs.com/",
    "https://www.douyin.com/",
    "https://www.toutiao.com/",
]


def probe(url: str) -> None:
    from camoufox.sync_api import Camoufox

    t0 = time.time()
    with Camoufox(headless=True, humanize=True) as browser:
        page = browser.new_page()
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=45000)
            page.wait_for_timeout(2500)
            title = page.title()
            html = page.content()
            text = page.inner_text("body")[:400].replace("\n", " ")
            print(f"[OK  ] {time.time()-t0:5.1f}s  html={len(html):>7}  title={title[:60]!r}")
            print(f"       正文开头: {text[:200]}")
        except Exception as e:
            print(f"[FAIL] {time.time()-t0:5.1f}s  {type(e).__name__}: {str(e)[:150]}")


if __name__ == "__main__":
    print("=== Camoufox 反检测浏览器探针 ===")
    for u in TARGETS:
        print(f"\n>>> {u}")
        try:
            probe(u)
        except Exception as e:
            print(f"[FATAL] {type(e).__name__}: {str(e)[:200]}")
