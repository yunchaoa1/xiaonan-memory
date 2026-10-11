#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""batch_fetch.py —— 批量抓取（Lightpanda 快抓 + trafilatura 提正文）

替代 crawl4ai 的轻量组合：不背 Playwright/框架依赖，只用 WSL 里的 Lightpanda。

用法:
    python batch_fetch.py urls.txt -o D:\\out [-j 4] [--mode auto|lightpanda|trafilatura]
    python batch_fetch.py "网址1" "网址2" -o D:\\out

模式:
    lightpanda  —— 用 Lightpanda 自带的 markdown 导出（最快，推荐）
    trafilatura —— 先抓 HTML 再用 trafilatura 提正文（正文更干净，慢一点）
    auto        —— 先 lightpanda，正文过短(<200字)时自动回退 trafilatura

特性:
    - 并发抓取（-j 指定线程数，默认 4）
    - 断点续传：输出目录已存在同名 .md 就跳过（--force 覆盖）
    - 每篇单独存 .md，另存 summary.json 汇总
"""
import argparse
import concurrent.futures as cf
import json
import os
import re
import subprocess
import sys
import time
from hashlib import md5

LP_BIN = "/root/lightpanda/lp"
WSL_DISTRO = "Ubuntu-24.04"


def slugify(url: str) -> str:
    s = re.sub(r"^https?://", "", url)
    s = re.sub(r"[^A-Za-z0-9._-]+", "_", s)[:80].strip("_")
    h = md5(url.encode("utf-8")).hexdigest()[:8]
    return f"{s}_{h}" if s else h


def lp_fetch(url: str, dump: str, timeout: int = 90) -> str:
    """用 WSL 里的 Lightpanda 抓取，返回文本（stdout）。"""
    cmd = ["wsl.exe", "-d", WSL_DISTRO, "--", LP_BIN,
           "fetch", "--dump", dump, "--log-level", "error", url]
    try:
        r = subprocess.run(cmd, capture_output=True, timeout=timeout)
        return r.stdout.decode("utf-8", "replace")
    except subprocess.TimeoutExpired:
        return ""


def trafilatura_extract(html: str, url: str) -> str:
    try:
        import trafilatura
        return trafilatura.extract(html, url=url, include_comments=False,
                                   include_tables=True) or ""
    except Exception:
        return ""


def fetch_one(url: str, mode: str) -> dict:
    t0 = time.time()
    if mode in ("lightpanda", "auto"):
        text = lp_fetch(url, "markdown")
        src = "lightpanda"
        if mode == "auto" and len(text.strip()) < 200:
            html = lp_fetch(url, "html")
            alt = trafilatura_extract(html, url)
            if len(alt.strip()) > len(text.strip()):
                text, src = alt, "trafilatura(fallback)"
    else:
        html = lp_fetch(url, "html")
        text = trafilatura_extract(html, url)
        src = "trafilatura"
    return {
        "url": url,
        "chars": len(text.strip()),
        "source": src,
        "seconds": round(time.time() - t0, 2),
        "text": text,
        "ok": len(text.strip()) > 0,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="批量抓取（Lightpanda + trafilatura）")
    ap.add_argument("targets", nargs="+", help="URL 列表文件（每行一个）或直接给 URL")
    ap.add_argument("-o", "--out", required=True, help="输出目录")
    ap.add_argument("-j", "--jobs", type=int, default=4, help="并发数（默认 4）")
    ap.add_argument("--mode", choices=["auto", "lightpanda", "trafilatura"], default="auto")
    ap.add_argument("--force", action="store_true", help="重抓已存在的")
    args = ap.parse_args()

    urls = []
    for t in args.targets:
        if os.path.isfile(t):
            with open(t, encoding="utf-8") as f:
                urls += [ln.strip() for ln in f if ln.strip() and not ln.startswith("#")]
        else:
            urls.append(t)
    urls = list(dict.fromkeys(urls))
    os.makedirs(args.out, exist_ok=True)

    todo = []
    for u in urls:
        fp = os.path.join(args.out, slugify(u) + ".md")
        if os.path.exists(fp) and not args.force:
            print(f"[跳过] 已存在: {os.path.basename(fp)}")
        else:
            todo.append(u)

    print(f"共 {len(urls)} 个目标，待抓 {len(todo)} 个，并发 {args.jobs}，模式 {args.mode}")
    results = []
    with cf.ThreadPoolExecutor(max_workers=max(1, args.jobs)) as ex:
        futs = {ex.submit(fetch_one, u, args.mode): u for u in todo}
        for fut in cf.as_completed(futs):
            u = futs[fut]
            try:
                r = fut.result()
            except Exception as e:
                r = {"url": u, "chars": 0, "source": "-", "seconds": 0,
                     "text": "", "ok": False, "error": str(e)}
            fp = os.path.join(args.out, slugify(u) + ".md")
            if r.get("text"):
                with open(fp, "w", encoding="utf-8") as f:
                    f.write(r["text"])
            results.append({k: v for k, v in r.items() if k != "text"})
            flag = "OK " if r.get("ok") else "FAIL"
            print(f"[{flag}] {r['chars']:>7} 字  {r['seconds']:>6.2f}s  {r['source']:<22} {u[:70]}")

    with open(os.path.join(args.out, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=1)
    ok = sum(1 for r in results if r.get("ok"))
    print(f"\n完成: 成功 {ok} / 共 {len(results)}；汇总 -> {os.path.join(args.out, 'summary.json')}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
