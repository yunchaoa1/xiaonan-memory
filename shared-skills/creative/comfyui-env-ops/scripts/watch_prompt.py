#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
盯一个 ComfyUI 任务，并区分三种结局：正常结束 / 崩溃 / ⚠️队列卡死。

为什么需要它：
  · 第三方节点（tiled sampler / latent upscaler / turbo sampler）**不上报进度**，
    UI 与日志都可能长时间没新行 —— 「安静」本身不代表出事。
  · 真出事有两种，长得不一样但**都不会自己恢复**：
      ① 崩溃：日志出现 `Exception during processing` / `prompt_worker` / `CUDA error: out of memory`
      ② 卡死：CUDA OOM 打死 prompt_worker 线程后，/queue 永远 pending>=1 而 running=0，
         之后提交的 `got prompt` 无人处理 —— **CUDA 上下文已坏，必须重启实例，等不来**。

用法：
  python watch_prompt.py <port> [--comfyui <ComfyUI 目录>] [--prompt-id <id>]
                              [--timeout 3600] [--interval 15] [--stuck-polls 4]

退出码：0 正常结束 ｜ 2 崩溃 ｜ 3 队列卡死（需重启）｜ 4 超时仍未结束
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.request

DONE, CRASH, STUCK, TIMEOUT = 0, 2, 3, 4
CRASH_MARKERS = (
    "Exception during processing",
    "prompt_worker",
    "CUDA error",
    "out of memory",
    "RuntimeError",
    "AcceleratorError",
)


def get_json(url: str, timeout: float = 30.0):
    with urllib.request.urlopen(url, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def queue_counts(port: int) -> tuple[int, int, str | None]:
    """-> (running, pending, 首个 running 的 prompt_id)"""
    q = get_json(f"http://127.0.0.1:{port}/queue")
    run = q.get("queue_running") or []
    pend = q.get("queue_pending") or []
    # 条目形如 [num, prompt_id, prompt, extra, outputs]
    pid = run[0][1] if run and len(run[0]) > 1 else None
    return len(run), len(pend), pid


def history(port: int, pid: str):
    try:
        h = get_json(f"http://127.0.0.1:{port}/history/{pid}")
    except Exception:
        return None
    return (h or {}).get(pid)


def tail(path: str, n: int = 40) -> list[str]:
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read().splitlines()[-n:]
    except OSError:
        return []


def log_size(path: str) -> int:
    try:
        return os.path.getsize(path)
    except OSError:
        return 0


def report_outputs(comfyui: str, entry: dict) -> None:
    outs = entry.get("outputs") or {}
    total = 0
    for node_id, kinds in outs.items():
        for kind, items in kinds.items():
            if not isinstance(items, list):
                continue
            for it in items:
                if not isinstance(it, dict) or "filename" not in it:
                    continue
                sub = it.get("subfolder") or ""
                p = os.path.join(comfyui, "output", sub, it["filename"])
                try:
                    size = os.path.getsize(p)
                except OSError:
                    size = -1
                total += 1
                flag = "✅" if size > 0 else "❌(文件不在)"
                print(f"  #{node_id} {kind}: {p}  ({size} 字节) {flag}")
    if total == 0:
        print("  （这次没有产物落盘 —— 检查 SaveVideo / VHS_VideoCombine 是否在链上）")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("port", type=int)
    ap.add_argument("--comfyui", default=".", help="ComfyUI 根目录（用于定位 output/ 与日志）")
    ap.add_argument("--prompt-id", default=None)
    ap.add_argument("--timeout", type=int, default=3600)
    ap.add_argument("--interval", type=int, default=15)
    ap.add_argument("--stuck-polls", type=int, default=4,
                    help="连续几次「running=0 且日志不增长」判为卡死")
    a = ap.parse_args()

    logfile = os.path.join(a.comfyui, "user", f"comfyui_{a.port}.log")
    pid = a.prompt_id
    if not pid:
        _, _, pid = queue_counts(a.port)
        if not pid:
            print("✋ /queue 里没有运行中的任务，且未给 --prompt-id")
            return STUCK
    print(f"盯着 prompt_id={pid}（日志 {logfile}）")

    t0 = time.time()
    last_size, stuck = -1, 0
    while True:
        el = int(time.time() - t0)
        if el > a.timeout:
            print(f"⏱ 超过 {a.timeout}s 仍未结束 —— 用 /queue 再查")
            return TIMEOUT

        running, pending, _ = queue_counts(a.port)
        size = log_size(logfile)
        grew = size > last_size
        delta = size - last_size if last_size >= 0 else 0
        last_size = size
        entry = history(a.port, pid)

        print(f"[{el:>5}s] 运行中={running} 排队={pending} 日志+{delta}B"
              + ("" if grew else "（无新行）"))

        # ① 正常结束
        if entry and (entry.get("status") or {}).get("completed"):
            st = entry.get("status") or {}
            print("=" * 60)
            print(f"✅ 任务结束 status_str={st.get('status_str')}")
            report_outputs(a.comfyui, entry)
            return DONE if st.get("status_str") != "error" else CRASH

        # ② 崩溃（历史里 status_str=error，或日志出现崩溃标记）
        if entry and (entry.get("status") or {}).get("status_str") == "error":
            print("=" * 60)
            print("❌ 任务以 error 结束。日志尾部：")
            for line in tail(logfile, 40):
                print("   » " + line)
            return CRASH

        lines = tail(logfile, 12)
        hit = [l for l in lines if any(m in l for m in CRASH_MARKERS)]
        if hit and running == 0 and pending == 0:
            print("=" * 60)
            print("❌ 日志里出现崩溃标记，且队列已空。日志尾部：")
            for line in tail(logfile, 40):
                print("   » " + line)
            return CRASH

        # ③ 卡死：有排队、没人跑、日志不增长
        if running == 0 and pending >= 1 and not grew:
            stuck += 1
            if stuck >= a.stuck_polls:
                print("=" * 60)
                print("⚠️ 队列卡死：pending≥1 但 running=0 且日志不增长")
                print("   根因通常是 CUDA OOM 打死了 prompt_worker 线程，CUDA 上下文已坏、热恢复不了。")
                print("   处置（必须重启实例）：")
                print(f"     netstat -ano | grep {a.port}      # 取 PID")
                print('     powershell -NoProfile -Command "Stop-Process -Id <pid> -Force"')
                print(f"     cd /d {a.comfyui} && ./.venv/Scripts/python.exe main.py"
                      f" --listen 0.0.0.0 --port {a.port} --disable-cuda-malloc")
                print("   日志尾部：")
                for line in tail(logfile, 30):
                    print("   » " + line)
                return STUCK
        else:
            stuck = 0

        time.sleep(a.interval)


if __name__ == "__main__":
    sys.exit(main())
