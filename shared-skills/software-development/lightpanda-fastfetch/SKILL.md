---
name: lightpanda-fastfetch
description: 抓网页/批量爬取太慢时用。WSL里的Lightpanda无头浏览器，实测快60倍。
version: 1.0.0
author: 小南
license: internal
metadata:
  hermes:
    tags: [抓取, 爬虫, 无头浏览器, WSL, Lightpanda, 性能]
    related_skills: [local-web-capabilities, agent-browser, video-learning, aria2-downloads]
---

# Lightpanda 快速抓取（WSL 里的 Zig 无头浏览器）

> **2026-10-11 吸收自抖音「专为AI打造的开源浏览器，比Chrome快9倍」** → 核证项目 `lightpanda-io/browser`
> （Zig 语言**从零写**的无头浏览器，不是 Chromium 分叉；本机装的是 `1.1.0-nightly.10426`，71MB 单二进制）。
> **官方基准**（933 个真实网页 / AWS m5.large）：执行 **9x 快**（5s vs 46s）、内存 **16x 省**（123MB vs 2GB）。
> **本机实测**（比官方更可信）：抓博客园首页 **670ms**，而 `wigolo fetch` 同页要 **34,450ms** —— **快约 60 倍**。

## When to Use（何时加载）
- 凡哥说：「**抓这个网页**」「**批量抓取**」「**爬取太慢**」「抓取效率」「把这个页面抓下来」
- 需要**批量**抓内容型页面（新闻 / 博客 / 文档 / 列表页 / 静态公司站）
- 想要 **Markdown 或 HTML 提取**，但不想等浏览器渲染几十秒

## ⚠️ 第一步：先看边界表（选错工具白费功夫）

| 场景 | 用谁 |
|---|---|
| **静态/半静态页面、批量抓取、要 Markdown** | **本技能 lightpanda** ⚡ |
| 强反爬站（抖音/小红书/今日头条） | ❌ lightpanda 抓不到（实测 **0 字节**）→ 用 `agent-browser`（真浏览器）或 Scrapling 隐身抓取 |
| 需要**截图** / 登录态 / 真实点击交互 | `agent-browser`（lightpanda **不含图形渲染**） |
| 搜索引擎式检索 | `wigolo`（MCP 里的 search） |
| 只要原始 HTML、不要提取 | `curl`（微快，但没提取） |
| 下载文件（非抓页面） | `aria2-downloads` |

## 装在哪（本机已验证）
```
WSL Ubuntu-24.04 内：
  /root/lightpanda/lightpanda     ← 71MB 单二进制
  /root/lightpanda/lp             ← wrapper（已内置关闭遥测 + 路径自适应）
```
> ⚠️ WSL 的默认用户是 **root** → 路径是 `/root/lightpanda/`，**不是** `/home/<user>/lightpanda/`

## 用法（Windows 侧一行搞定）

```bash
# Markdown（最常用）
wsl.exe -d Ubuntu-24.04 -- /root/lightpanda/lp fetch --dump markdown --log-level error "<URL>"

# 原始 HTML
wsl.exe -d Ubuntu-24.04 -- /root/lightpanda/lp fetch --dump html --log-level error "<URL>"
```
- `--log-level error` 抑制日志噪音（结果只走 stdout）
- 需要等 JS 渲染时加：`--wait-until networkidle0` / `--wait-ms 3000` / `--wait-selector "#app"`
- 礼貌抓取可加 `--obey-robots`
- 还支持 `--dump png` / `--dump pdf`（**文本版渲染**，不是真截图）

## 实测数据（2026-10-11 · 本机 · 同一页面）

| 工具 | 博客园首页 | 输出 |
|---|---|---|
| curl | 399 ms | 原始 HTML（无提取） |
| `wigolo fetch` | **34,450 ms** | 6,328 字符 markdown |
| **lightpanda** | **670 ms** | **21,248 字节 markdown** |

其他实测：`example.com` 923ms ✓ ｜ 抖音 486ms → **0 字节** ｜ 今日头条 494ms → 0 字节 ｜ 36kr 293ms → 只有图片占位
→ **规律：服务端渲染/半静态页神速；强反爬站快速失败（不浪费时间拖 30 秒）**

## 坑（都踩过）
- **遥测默认开启** → 必须带 `LIGHTPANDA_DISABLE_TELEMETRY=true`（wrapper 已内置，直接用 `lp` 即可）
- **没有 Windows 原生二进制**（官方原话：装 WSL 里）→ 别想着本机直跑；Docker 也行（本机无 docker）
- **WSL 里默认用户是 root** → 路径按 `/root/` 写
- **跨 WSL 传参**：用 `wsl.exe -d <发行版> -- <绝对路径> <参数...>` **直接执行**；用 `bash -lc "..."` 包一层，URL/引号会被外层 shell 吃掉（实测踩过）
- 二进制依赖 **glibc**（Ubuntu/Debian ✓；Alpine 报 `cannot execute`）
- **不含图形渲染** → 不能替代截图需求

## 可选：更强集成（本次未做，需要时再议）
项目自带 **MCP server**（`lp mcp` / `lp mcp --port 9223` 走 HTTP）和 **CDP 服务器**（`lp serve --port 9222`，Playwright / Puppeteer 可直接连，**WSL 会自动转发 localhost**）。
若要把抓取做成 Hermes 原生工具、或让 Playwright 复用它的速度，走这两条路；日常用上面的 CLI 已经够快。
