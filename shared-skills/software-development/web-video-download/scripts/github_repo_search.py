#!/usr/bin/env python3
"""GitHub 开源项目取证：星数 / 语言 / 最后推送 / 最新 release。

用途：凡哥说"你去 GitHub 里找开源项目"时，别凭印象报数，跑这个拿真数据。
不限视频下载，任何选型任务都能用。

用法：
  python github_repo_search.py "video downloader" "m3u8 downloader"
  python github_repo_search.py --top 10 "视频下载"
  python github_repo_search.py --releases putyy/res-downloader nilaoda/N_m3u8DL-RE

退出码：0 正常；2 参数错误。
限额：未认证 10 次/分钟（搜索）、60 次/小时（普通接口）。设 GITHUB_TOKEN 可提高。
"""
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

API = "https://api.github.com"


def _get(path, **params):
    url = API + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={
        "Accept": "application/vnd.github+json",
        "User-Agent": "xiaonan-repo-vet",
    })
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8", "replace"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")[:300]
        print(f"[HTTP {e.code}] {path} :: {body}", file=sys.stderr)
        return None


def search(query, top=8):
    """按星数排序搜仓库。

    ⚠️ 坑（2026-10-18 踩过）：查询串里的中文/空格必须 percent-encode。
    直接把原始 UTF-8 拼进 URL（或只把空格换成 '+'）时，GitHub 会返回非 JSON 正文，
    下游 json.loads 直接崩 'Expecting value: line 2 column 1'。
    urllib.parse.urlencode 会做正确的 quote，别手拼 URL。
    """
    data = _get(
        "/search/repositories",
        q=query,
        sort="stars",
        order="desc",
        per_page=max(1, min(top, 50)),
    )
    if not data or "items" not in data:
        print(f"!! 查询失败：{query}", file=sys.stderr)
        return []

    rows = []
    for r in data["items"]:
        desc = (r.get("description") or "").replace("\n", " ")[:90]
        rows.append({
            "repo": r["full_name"],
            "stars": r["stargazers_count"],
            "lang": r.get("language") or "-",
            "pushed": (r.get("pushed_at") or "")[:10],
            "desc": desc,
            "url": r["html_url"],
        })

    print(f"\n=== {query} ===")
    for x in rows:
        print(f"{x['repo']:<45} {x['stars']:>7}  {x['lang']:<12} {x['pushed']}  {x['desc']}")
    return rows


def releases(repo, asset_limit=6):
    """看最新 release 的版本号、发布时间、安装包大小（判断好不好装、是不是停更）。"""
    data = _get(f"/repos/{repo}/releases/latest")
    if not data:
        print(f"{repo}: 无 release 或接口失败")
        return
    print(f"\n=== {repo} ===")
    print(f"{data.get('tag_name')}  published {str(data.get('published_at'))[:10]}")
    for a in (data.get("assets") or [])[:asset_limit]:
        print(f"   {a['name']}  {a['size'] / 1048576:.1f} MB")


def main(argv):
    if not argv:
        print(__doc__)
        return 2

    top = 8
    if argv[0] == "--top":
        if len(argv) < 2:
            print("--top 需要一个数字", file=sys.stderr)
            return 2
        top = int(argv[1])
        argv = argv[2:]

    if argv and argv[0] == "--releases":
        for repo in argv[1:]:
            releases(repo)
        return 0

    for q in argv:
        search(q, top=top)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
