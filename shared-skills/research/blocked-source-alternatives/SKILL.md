---
name: blocked-source-alternatives
description: "直接抓取不通(DNS被墙/登录墙)时用。镜像源+URL换形+元数据替代正文。"
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [抓取, 镜像, 镜像源, 被墙, 登录墙, fallback]
    related_skills: [blocked-page-recovery, local-web-capabilities, agent-browser, video-learning]
---

# 直接路径不通时的替代路径

`blocked-page-recovery` 管的是**页面**被 403/付费墙/WAF 挡（走存档快照）；
`local-web-capabilities` 管**工具栈**（wigolo / Scrapling / agent-browser）；
本技能管第三类：**源本身在这台机器上不可达，或目标天然有登录墙**——换一条路拿同一份信息。

先判类型，再挑路径：

| 症状 | 走哪条 |
|---|---|
| 域名根本解析不了（`curl` **exit=6** `Couldn't resolve host`） | **① 镜像源**（下面第一节） |
| 域名可达但 `web_extract` 报 `Blocked: URL targets a private or internal network address` | 同上——`web_extract` 的拦截规则会误伤某些域名，**不是目标站的问题** |
| 页面是登录墙 / 只有壳（`content_completeness.level: shell`） | **② URL 换形 + 元数据替代正文**（下面第二节） |
| 真的被反爬/付费墙挡 | 转 `blocked-page-recovery`（存档快照） |

---

## ① 镜像源：换一个域拿同一份文件

原则：**内容同源、可校验**（比对字节数/哈希）；镜像失效就换下一个，别在一个死域名上重试。

| 目标 | 直连（本机常不通） | 镜像（实测可用） |
|---|---|---|
| GitHub raw 单文件 | `raw.githubusercontent.com/...` | `https://cdn.jsdelivr.net/gh/<owner>/<repo>@<branch>/<path>` |
| 同上备选 | — | `https://ghproxy.net/https://raw.githubusercontent.com/<owner>/<repo>/<branch>/<path>` |
| GitHub 仓库文件树（免 clone） | 需 clone | `https://data.jsdelivr.com/v1/packages/gh/<owner>/<repo>@<branch>` |
| GitHub 仓库元数据（stars/license/最后推送/默认分支） | — | `api.github.com` **通常直连通**，用它核"是否最新"（看 `pushed_at`，星多≠最新） |
| **GitHub Release 二进制**（APK / exe / zip / msix） | `https://github.com/<o>/<r>/releases/download/<tag>/<file>` —— 走 `objects.githubusercontent.com`，**常整段连不上**（`curl` 报 `Failed to connect to github.com port 443`） | 前面拼镜像：`https://ghfast.top/https://github.com/<o>/<r>/releases/download/<tag>/<file>`（2026-10 实测拿下 2.5MB APK，字节数与 API 报的 size 一致） |
| 同上备选 | — | `https://ghproxy.net/https://github.com/...` / `https://gh-proxy.com/https://github.com/...` |
| Release 校验值 | — | 同目录的 `SHA256SUMS` 也走镜像拿，下完 `sha256sum` 比对——**装到别人机器上的二进制必须验** |
| PyPI | pypi.org | `-i https://pypi.tuna.tsinghua.edu.cn/simple` |
| npm / playwright 下载 | registry.npmjs.org / playwright CDN | `PLAYWRIGHT_DOWNLOAD_HOST=https://cdn.npmmirror.com/binaries/playwright`；npm 装原生模块加 `--allow-scripts=<pkg,...>` |
| HuggingFace 模型 | huggingface.co | `HF_ENDPOINT=https://hf-mirror.com` |

```bash
B="https://cdn.jsdelivr.net/gh/<owner>/<repo>@<branch>"
curl -sL --max-time 25 "$B/SKILL.md" -o out.md; echo "exit=$? size=$(wc -c < out.md)"
```

**Release 定位的两个 API 坑（2026-10 实测）**：
- **`api.github.com` 通 ≠ 下载域通**。同一台机器上 `api.github.com` 与 `github.com` 页面都正常，
  `releases/download/` 却连不上（走的是 `objects.githubusercontent.com`）→ 别据此判断"项目没了"，直接上镜像。
- **`repos/<o>/<r>/releases/latest` 返回 404 ≠ 仓库不存在**。可能只是**没有 release**。
  正确动作：打 `repos/<o>/<r>/releases`（列表），从里面读 `tag_name` / `assets[].browser_download_url` / `assets[].size`。
  另外 README 里写的"更新仓库"（`<repo>-updates`）可能**存在但没有任何 release**，真正的新版在**主仓库**的 releases 里。

**读一个陌生仓库的正确顺序**：先拉文件树看清结构（`tools/`、`parsers/`、`scripts/` 往往是精华），再**按需**只下 README / SKILL.md / docs / tools，**不要整仓 clone**。要"学一个项目"时，先读它的 `SKILL.md` 或 `docs/how-it-works.md`——作者通常已经把方法论写好了。

**踩过的坑**：
- 给 `curl` 带 `-w "%{http_code}"` 再塞进 for 循环：MSYS 会把 `%{...}` 当路径转换 → 报 `README.md: No such file or directory` 且 http_code 显示 `000`。用最简形式 `curl -sL ... -o f; echo $?` 最稳。
- 一个 terminal 调用里塞多个 curl + 转义引号 + heredoc，会触发 hardline 拦截（`command parser limit / oversized inline payload`）→ 拆成小命令，或用 `read_file` / `search_files` 代替内联 `grep`。

## ② 登录墙：换 URL 形态，先用元数据代替正文

社交平台（抖音等）的**个人主页 / 喜欢·收藏列表**链接（`.../user/self?modal_id=<id>&showTab=like`）**必被登录墙**——任何抓取工具都只回登录壳。别在它上面耗时间。

1. **换算成内容直链**：`modal_id=<id>` / 收藏链接 → `https://www.douyin.com/video/<id>`（备选 `www.iesdouyin.com/share/video/<id>/`）。
2. **拿元数据**：`wigolo fetch` 后正文仍是壳，但 `metadata` / `evidence[].title` 里有**完整标题 + 简介 + 话题标签**——足够判断主题。
3. **关键词反查**：知识/工具类视频常把工具名写在简介或话题标签（如 `#booktoskill`）→ 拿它去 GitHub 反查项目，比解析视频便宜得多、也更可靠。
4. **要真内容**（口播/画面）才上重武器：`video-learning` 的 `references/douyin-capture.md`（CDP 借真浏览器会话取签名直链），或 `agent-browser`（**必须 PTY 跑、禁管道**）。

## 边界

- **只抓公开信息**：不绕登录墙取私密内容、不碰个人信息、不抢被爬方自身服务。
- 壳页诚实标注（`level: shell`）——**别当完整内容用**，也**别据此断言"抓不到"**。
- 镜像只用于**公开文件**；带凭据的请求永不经过第三方镜像（见 `blocked-page-recovery` 的 "Proxy relays: don't"）。
- 镜像可用性会变。失效时先换备选域名，再考虑挂代理（`hermes-network-proxy`），**不要**把某次失败写成"这条路不能走"。
