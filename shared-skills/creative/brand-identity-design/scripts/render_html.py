#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""把本地 HTML 渲染成 PNG —— 交付前自检用（不要只看"文件写成功了"）。

用法:
    python render_html.py <本地html> <输出png> [宽=1400] [高=2200]

为什么必须有这一步:
    HTML 交付页里引用的图片走相对路径，路径写错、文件名多个空格、
    CSS 撑破容器，都只会"静默破图/静默溢出"。渲染成 PNG 自己看一眼，
    破图 / 文字截断 / 深底格看不见 / 排版错位立刻暴露。

配套: 渲染出的 PNG 直接丢给 vision 逐项核对。
"""
import os
import subprocess
import sys
import urllib.parse

BROWSERS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    "/usr/bin/google-chrome",
    "/usr/bin/chromium",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
]


def find_browser():
    for p in BROWSERS:
        if os.path.exists(p):
            return p
    raise SystemExit("未找到 Chrome/Edge，请把浏览器可执行文件路径加进 BROWSERS")


def render(html_path, out_png, width=1400, height=2200, timeout=180):
    """渲染本地 HTML 到 PNG。返回 True/False（文件是否真的产出）。"""
    abspath = os.path.abspath(html_path)
    if not os.path.exists(abspath):
        print("FAILED: 找不到 HTML -> " + abspath)
        return False
    # 中文路径 / 空格 / # 都要转义，否则浏览器打不开
    url = "file:///" + urllib.parse.quote(abspath.replace("\\", "/"))
    cmd = [
        find_browser(),
        "--headless=new",
        "--disable-gpu",
        "--hide-scrollbars",
        "--allow-file-access-from-files",
        "--screenshot=" + os.path.abspath(out_png),
        "--window-size=%d,%d" % (width, height),
        url,
    ]
    subprocess.run(cmd, capture_output=True, timeout=timeout)
    ok = os.path.exists(out_png)
    print(("OK " if ok else "FAILED ") + out_png +
          (" %dB" % os.path.getsize(out_png) if ok else ""))
    return ok


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 1
    w = int(sys.argv[3]) if len(sys.argv) > 3 else 1400
    h = int(sys.argv[4]) if len(sys.argv) > 4 else 2200
    return 0 if render(sys.argv[1], sys.argv[2], w, h) else 1


if __name__ == "__main__":
    sys.exit(main())
