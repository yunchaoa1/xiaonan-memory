#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""a2rpc.py —— aria2 JSON-RPC 客户端（aria2-downloads 技能配套）

让「智能体/脚本」不用手搓 JSON 就能调度 aria2。
注意：需要先起 aria2c 的 RPC 服务（见 SKILL.md 用法 2）。

用法:
    set ARIA2_SECRET=你的口令            (Windows)  / export ARIA2_SECRET=...
    python a2rpc.py version
    python a2rpc.py add <URL> [--out 文件名] [--dir D:/下载目录]
    python a2rpc.py list                 # 进行中任务
    python a2rpc.py all                  # 全部任务（含已完成）
    python a2rpc.py status <gid>
    python a2rpc.py pause <gid> | unpause <gid> | remove <gid>

可选: --port 16800 (默认)  |  --secret <口令> 覆盖环境变量
"""
import argparse
import json
import os
import sys
import urllib.request

ENDPOINT = "http://127.0.0.1:{port}/jsonrpc"

# Windows 控制台 UTF-8，防中文/符号报 UnicodeEncodeError
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except Exception:
        pass


def call(port, method, params):
    data = json.dumps({"jsonrpc": "2.0", "id": "a2rpc",
                       "method": method, "params": params}).encode()
    req = urllib.request.Request(ENDPOINT.format(port=port), data=data,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        out = json.load(r)
    if "error" in out:
        print("!! aria2 返回错误:", json.dumps(out["error"], ensure_ascii=False))
        sys.exit(1)
    return out.get("result")


def main():
    ap = argparse.ArgumentParser(description="aria2 JSON-RPC 客户端")
    ap.add_argument("cmd")
    ap.add_argument("args", nargs="*")
    ap.add_argument("--out", default=None, help="保存文件名")
    ap.add_argument("--dir", default=None, help="保存目录")
    ap.add_argument("--port", type=int, default=16800)
    ap.add_argument("--secret", default=os.environ.get("ARIA2_SECRET", ""))
    a = ap.parse_args()
    tok = [f"token:{a.secret}"] if a.secret else []

    if a.cmd == "version":
        print(json.dumps(call(a.port, "aria2.getVersion", tok), ensure_ascii=False))

    elif a.cmd == "add":
        if not a.args:
            sys.exit("用法: a2rpc.py add <URL> [--out 名] [--dir 目录]")
        opts = {}
        if a.out:
            opts["out"] = a.out
        if a.dir:
            opts["dir"] = a.dir
        gid = call(a.port, "aria2.addUri", tok + [a.args, opts])
        print(f"已提交 gid={gid}")

    elif a.cmd in ("list", "all"):
        method = "aria2.tellActive" if a.cmd == "list" else "aria2.tellAll"
        keys = ["gid", "status", "completedLength", "totalLength", "downloadSpeed", "files"]
        if method == "aria2.tellAll":
            res = call(a.port, "aria2.tellWaiting", tok + [0, 100, keys]) \
                + call(a.port, "aria2.tellActive", tok + [keys]) \
                + call(a.port, "aria2.tellStopped", tok + [0, 100, keys])
        else:
            res = call(a.port, method, tok + [keys])
        if not res:
            print("(无任务)")
        for t in res:
            tot = int(t.get("totalLength") or 0)
            done = int(t.get("completedLength") or 0)
            pct = f"{done * 100 // tot}%" if tot else "-"
            name = ""
            if t.get("files"):
                name = os.path.basename(t["files"][0].get("path", ""))
            sp = int(t.get("downloadSpeed") or 0)
            print(f"{t['gid']}  {t['status']:<8} {pct:>5}  {sp // 1024} KiB/s  {name}")

    elif a.cmd == "status":
        keys = ["gid", "status", "completedLength", "totalLength", "downloadSpeed",
                "errorMessage", "files"]
        print(json.dumps(call(a.port, "aria2.tellStatus", tok + [a.args[0], keys]),
                         ensure_ascii=False, indent=2))

    elif a.cmd in ("pause", "unpause", "remove"):
        call(a.port, f"aria2.{a.cmd}", tok + [a.args[0]])
        print(f"{a.cmd} {a.args[0]} ok")

    else:
        sys.exit(f"未知命令: {a.cmd}（见文件头用法）")


if __name__ == "__main__":
    main()
