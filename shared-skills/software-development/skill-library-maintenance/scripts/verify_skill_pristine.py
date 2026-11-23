# -*- coding: utf-8 -*-
"""verify_skill_pristine.py —— 核「这个下载来的技能是不是最初的样子」

用途
----
凡哥问「你确保一下这个 skill 是不是最初的样子？」「这个是你下载的原版吗？」时，
不要口头保证，跑这个脚本给证据。

原理
----
GitHub API 的 git/trees 里每个 blob 自带 sha —— 那正是 git 的 blob sha1：
    sha1(b"blob <size>\\0" + 文件内容)
所以在本地把所有文件按同样算法算一遍，跟上游 sha 对撞即可，**一个文件都不用下载**。
（raw.githubusercontent.com 打不开也能核；只有 api.github.com 需要通。）

它比 mtime / 目测可靠：mtime 会被同步、解压刷新；目测看不出一个字的改动。

输出四分类（只报「一致/不一致」会漏掉最要命的两类）：
    完全一致 / 内容不同 / 本地多出（上游没有）/ 本地缺失（上游有）

用法
----
    python verify_skill_pristine.py --local "D:\\Hermes\\skills\\creative\\forest-laoli-h3" \\
        --repo lixiaoxiao9888-create/forest-laoli-h3 --subdir forest-laoli-h3

    # 代理没开、api 直连不通时：
    ... --proxy http://127.0.0.1:7897

退出码
------
0 = 本地与上游逐字节一致（无多出、无缺失、无改动）
1 = 有差异（多出/缺失/内容不同，任一非零）
2 = 取不到上游数据（网络/仓库路径问题）—— 此时**不要**下「一致」的结论

常见坑（都造成过假结论）
------------------------
1. 仓库内路径常多一层同名子目录：直接拼 main/SKILL.md 会拿到 14 字节的 "404: Not Found"。
   真身可能是 main/<name>/SKILL.md → 用 --subdir 指清，或先手动看 tree。
2. 「我下了 N 个」≠「仓库只有 N 个」：报告里必须同时说 上游总数 / 本地数 / 缺的是什么。
3. 自己为测试临时造的文件混进技能目录 → 会显示成「本地多出」。
   临时样本放 D:\\Hermes\\cache\\，技能目录只放上游文件（凡哥：不要掺杂我们自己的东西）。
"""
import argparse
import hashlib
import json
import os
import sys
import urllib.request


def blob_sha(path):
    with open(path, "rb") as f:
        data = f.read()
    h = hashlib.sha1()
    h.update(b"blob %d\0" % len(data))
    h.update(data)
    return h.hexdigest(), len(data)


def fetch_tree(repo, branch, proxy=None):
    url = "https://api.github.com/repos/%s/git/trees/%s?recursive=1" % (repo, branch)
    req = urllib.request.Request(url, headers={"User-Agent": "verify-skill-pristine"})
    if proxy:
        opener = urllib.request.build_opener(
            urllib.request.ProxyHandler({"http": proxy, "https": proxy})
        )
        resp = opener.open(req, timeout=60)
    else:
        resp = urllib.request.urlopen(req, timeout=60)
    return json.loads(resp.read().decode("utf-8"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--local", required=True, help="本地技能目录")
    ap.add_argument("--repo", required=True, help="owner/repo")
    ap.add_argument("--branch", default="main")
    ap.add_argument("--subdir", default=None,
                    help="仓库内对应子目录（默认取本地目录名）")
    ap.add_argument("--proxy", default=None, help="如 http://127.0.0.1:7897")
    args = ap.parse_args()

    local = os.path.abspath(args.local)
    if not os.path.isdir(local):
        print("本地目录不存在: %s" % local)
        return 2
    subdir = (args.subdir if args.subdir is not None else os.path.basename(local)).strip("/")

    try:
        tree = fetch_tree(args.repo, args.branch, args.proxy)
    except Exception as exc:  # noqa: BLE001 - 网络原因都要原样报出来
        print("取不到上游 tree：%s" % exc)
        print("→ 先确认代理 / 仓库名 / 分支；取不到时不要下『一致』的结论。")
        return 2

    up = {}
    for item in tree.get("tree", []):
        if item.get("type") != "blob":
            continue
        p = item["path"]
        if subdir and not p.startswith(subdir + "/"):
            continue
        rel = p[len(subdir) + 1:] if subdir else p
        up[rel] = item["sha"]

    if not up:
        print("上游目录下没取到文件（--subdir 写错了？）：%s" % subdir)
        print("先跑一次 `curl -s https://api.github.com/repos/%s/git/trees/%s?recursive=1` 看真实路径" % (args.repo, args.branch))
        return 2

    same, diff, missing = [], [], []
    for rel, sha in sorted(up.items()):
        path = os.path.join(local, rel.replace("/", os.sep))
        if not os.path.isfile(path):
            missing.append(rel)
            continue
        local_sha, size = blob_sha(path)
        if local_sha == sha:
            same.append(rel)
        else:
            diff.append((rel, size))

    seen = set()
    for root, _dirs, files in os.walk(local):
        for name in files:
            full = os.path.join(root, name)
            rel = os.path.relpath(full, local).replace(os.sep, "/")
            seen.add(rel)
    extra = sorted(seen - set(up))

    print("上游 %d 个文件 ｜ 本地 %d 个" % (len(up), len(seen)))
    print("完全一致 %d ｜ 内容不同 %d ｜ 本地多出 %d ｜ 本地缺失 %d"
          % (len(same), len(diff), len(extra), len(missing)))
    if diff:
        print("\n内容不同（本地字节数）：")
        for rel, size in diff:
            print("  - %s（%d 字节）" % (rel, size))
    if extra:
        print("\n本地多出（上游没有 → 我们自己塞进去的东西，按凡哥口径要移出到 cache）：")
        for rel in extra:
            print("  + %s" % rel)
    if missing:
        print("\n本地缺失（上游有 → 当初没下全，报数时要说明缺的是什么）：")
        for rel in missing:
            print("  ? %s" % rel)

    if diff or extra or missing:
        print("\n结论：与上游不完全一致。")
        return 1
    print("\n结论：逐字节一致，技能本体零改动，仍是最初版本。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
