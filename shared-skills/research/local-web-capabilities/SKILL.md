---
name: local-web-capabilities
description: "Use when 搜索/抓取被拒、403、反爬、SPA空白时。本机零key搜索+反爬抓取栈。"
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [Web, Scraping, MCP, Search, AntiBot]
    related_skills: [blocked-page-recovery, hermes-network-proxy]
---

# 本机搜索/抓取能力栈

2026-10-07 装好并实测。**搜索/抓取卡点先走这里,别再修 Hermes 内置 browser_exec。**

## When to Use · 什么时候用

- `web_search` 报 `Keyless Exa search failed` → 改用 wigolo 的 `search`
- `web_extract` 抓不到(403 / SPA 空白 / 需要登录) → wigolo `fetch` 或 Scrapling `stealthy_fetch`
- `browser_exec` 报 `DevToolsActivePort not found` → **别修它**,直接用下面两条(旧方法 Playwright 直连也能用)

## 能力清单(已验证)

| 工具 | 用途 | 实测证据 |
|---|---|---|
| **wigolo** (MCP, 10 工具) | 本地优先 search/fetch/crawl/extract/cache/research/agent;18 引擎,**零 API key** | `wigolo search`(中/英)均返回真实结果;`fetch` 抖音自动走 browser 渲染拿到标题 |
| **Scrapling** (MCP, 13 工具) | 自适应解析 + 隐身抓取(tls指纹)绕 Cloudflare | `stealthy_fetch nowsecure.nl` → 200 |
| **Playwright 直连** | 抖音单条视频音/视频流 | 见另一技能 `video-learning` → `references/douyin-capture.md` |

## 用法

MCP 工具(前缀即服务名):wigolo → `search` / `fetch` / `crawl` / `research` / `extract` / `cache`;scrapling → `stealthy_fetch` / `fetch` / `bulk_get` / `screenshot` / `open_session`。

CLI 直调(排查或脚本里):
```bash
wigolo search "查询" --json
wigolo fetch "URL" --force-refresh --mode=stealth --json   # 绕缓存 + 强制浏览器渲染
wigolo cache clear --url-pattern="*douyin.com*"            # 清掉旧的空缓存
scrapling extract stealthy-fetch "URL" out.md
```

## 安装踩坑(国内网络 · 关键)

所有"下载超时"= **国外 CDN / HuggingFace 受限**。统一解法:国内镜像。

```bash
export PLAYWRIGHT_DOWNLOAD_HOST=https://cdn.npmmirror.com/binaries/playwright
export HF_ENDPOINT=https://hf-mirror.com
python -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --progress-bar off <pkg>
```

- npm 装 wigolo 必须带 `--allow-scripts=@google/genai,better-sqlite3,protobufjs,onnxruntime-node,sharp`,否则原生模块(better-sqlite3 / onnxruntime)不编译
- wigolo 装完要 `wigolo warmup --all` 预下浏览器引擎 + 本地模型
- Scrapling 依赖要手动补齐:`curl_cffi patchright msgspec browserforge markdownify`,再 `python -m patchright install chromium`
- `hermes mcp add` 是**交互式**:用 `printf 'y\ny\n' |` 喂确认(重新添加时前面会多一个 `Overwrite? [y/N]`)
- **加/改 MCP 后需新会话才加载工具**

## 边界(法律红线,务必守)

- **只抓公开数据**:不碰个人信息、不绕过登录墙抓私密内容、不抢被爬方自身服务
- wigolo 遇到登录壳会诚实标注 `content_completeness.level: shell` —— 别当完整内容用
- reranker 模型首次用时才下载(可选),它失败**不影响**搜索
