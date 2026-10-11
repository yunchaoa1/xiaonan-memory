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
- 需要**真浏览器交互**(点击/填表/登录/翻页)、或要复用 Chrome 登录态 → 用 **`agent-browser`** CLI(见 `agent-browser` 技能;内置在 `hermes-agent/node_modules/.agent-browser-*`,**必须 PTY 跑**)

## 能力清单(已验证)

| 工具 | 用途 | 实测证据 |
|---|---|---|
| **wigolo** (MCP, 10 工具) | 本地优先 search/fetch/crawl/extract/cache/research/agent;18 引擎,**零 API key** | `wigolo search`(中/英)均返回真实结果;`fetch` 抖音自动走 browser 渲染拿到标题 |
| **Scrapling** (MCP, 13 工具) | 自适应解析 + 隐身抓取(tls指纹)绕 Cloudflare | `stealthy_fetch nowsecure.nl` → 200 |
| **Playwright 直连** | 抖音单条视频音/视频流 | 见另一技能 `video-learning` → `references/douyin-capture.md` |
| **agent-browser** (CLI, v0.26.0) | 真浏览器交互、复用登录态、链式操作 | 2026-10-11:`doctor` → `4 pass/0 fail`;`open example.com` + `get title/url` + `snapshot -i` **四步全过**（PTY 模式）|
| **Lightpanda** (WSL, v1.1.0-nightly) | 无头浏览器快速抓取（静态/半静态页、批量） | 博客园 **670ms** vs wigolo **34,450ms**；抖音 0 字节 → 详见 `lightpanda-fastfetch` |
| **trafilatura** 2.3.1 | 正文清洗层（去掉广告/导航/垃圾） | 326ms 抽出 2,980 字正文 |
| **批量抓取脚本** (自写) | Lightpanda + trafilatura 串起来跑批 | 3 页并发**总 6 秒**全成 → `lightpanda-fastfetch/scripts/batch_fetch.py` |

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

## ⚠️ 实测限制:wigolo search 引擎池(2026-10-07 深度验收)

**现象**:本机直连网络下 `search` 常处 degraded(`engine_pool.degraded=true`,`pool_collapsed`),标称 18 引擎实际只有 bing 响应;中文查询质量差——曾被 `no_lexical_match` 过滤为空,或返回词典/百科等无关结果。

**根因(本机 curl 逐引擎实测)**:
- duckduckgo.com / wikipedia.org:**直连超时(被墙)** → wigolo 里 soft-deadline timeout
- mojeek.com / marginalia:网络可达,但对程序请求返回 **403 / 429**(反爬/限流)
- 仅 cn.bing.com 稳定可达——但对**无 cookie 机器人请求返回降级结果**(整句查询被拆成单词级匹配,结果是词典站),即质量不可用

**当前推荐用法(降级方案)**:
- 中文搜索主力 → Hermes 内置 `web_search`(Exa 后端;偶发 "Keyless Exa search failed" 稍后重试即可)
- wigolo `fetch` ✅ 好用(实测博客园文章全文干净抓取;知乎 403 属目标站反爬,会诚实上报 http_status)
- wigolo `research` ✅ standard 深度可用(~90s 出结构化报告,会诚实标注数据缺口);comprehensive 深度会超 300s 超时
- ❌ 别用 `fetch` 抓 cn.bing.com/search 结果页当搜索——返回的是降级结果,不可用(已实测)

**修复方向(待凡哥拍板)**:给 wigolo 挂代理(如 `HTTPS_PROXY=http://127.0.0.1:<port>` 走本机 v2rayN/Clash)→ DDG/Wikipedia 可达 → 引擎池恢复。

## 2026-10-11 扩容（本轮新装 · 已实测）

- **Lightpanda**（WSL 里的 Zig 无头浏览器）→ 独立技能 `lightpanda-fastfetch`：
  **静态/半静态页快约 60 倍**（670ms vs wigolo 34s）；强反爬站抓不到（**0 字节，但快速失败不拖时间**）；**不含图形渲染 → 不能截图**
- **trafilatura 2.3.1**：正文清洗层（326ms/页），已串进 `batch_fetch.py`
- **aria2c**：下载引擎（大文件/BT/磁力/断点续传）→ 独立技能 `aria2-downloads`
- **Camoufox**（反检测 Firefox）：**内核已下载、尚未安装/验证** —— 装好并实测通过前，**不要把它写成可用能力**
- ⚠️ **新发现的瓶颈**：跨 WSL 调 Lightpanda 时，单页开销主要是 **`wsl.exe` 启动（约 4 秒）**，不是引擎本身（670ms）。
  要更快得改用它的 `serve` 常驻模式（CDP 服务器）—— 待优化项
- 装新工具的环境规则（**绝不污染 Hermes venv**、镜像表、GitHub 限流绕行）见新技能 **`local-tool-provisioning`**

## 边界(法律红线,务必守)

- **只抓公开数据**:不碰个人信息、不绕过登录墙抓私密内容、不抢被爬方自身服务
- wigolo 遇到登录壳会诚实标注 `content_completeness.level: shell` —— 别当完整内容用
- reranker 模型首次用时才下载(可选),它失败**不影响**搜索
