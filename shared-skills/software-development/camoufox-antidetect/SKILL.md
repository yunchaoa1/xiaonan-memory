---
name: camoufox-antidetect
description: 强反爬站抓不到时用。Camoufox反检测浏览器，抖音实测抓到92万字节。
version: 1.0.0
author: 小南
license: internal
metadata:
  hermes:
    tags: [反爬, 反检测, 浏览器, 指纹, Playwright, Camoufox]
    related_skills: [agent-browser, local-web-capabilities, lightpanda-fastfetch]
---

# Camoufox 反检测浏览器

> **2026-10-11 装**（社区调研选出，补"强反爬站抓不到"这个短板）。
> **一句话证据**：抖音 → **920,392 字节**（同期 Lightpanda 抓同一站是 **0 字节**）。

## When to Use（何时加载）

- 凡哥说「这个站抓不到」「被拦了」「403 / 人机验证 / 反爬」
- 其他工具（`lightpanda-fastfetch`、`curl`）抓回来是 **0 字节 / 空内容** 时
- 需要**真实浏览器 + 反指纹检测**的场合

## ⚠️ 先看边界表（选错工具白费功夫）

| 场景 | 用谁 |
|---|---|
| **强反爬站（抖音 / 小红书 / Cloudflare）** | **本技能 Camoufox** |
| 静态/半静态页、批量抓取、要 Markdown | `lightpanda-fastfetch`（**快 60 倍**，别用 Camoufox 做批量） |
| 要复用登录态 / 截图 / 真实交互 | `agent-browser`（真 Chrome） |
| **验证码** | ❌ **谁都解不了**（Camoufox 也没有解题器）→ 只能人工或付费打码 |
| **登录** | ❌ 仍需凡哥先登一次；Camoufox 可**持久化 profile** 复用他的会话 |

## 装在哪

- **Python 包**：`D:\Hermes\hermes-agent\venv`（`camoufox` 0.5.8 + Playwright 1.61）
- **浏览器内核**：`C:\Users\bobby\AppData\Local\camoufox\camoufox\Cache\`（official / v156.0.1-beta.36）

## 用法

```python
from camoufox.sync_api import Camoufox
with Camoufox(headless=True, humanize=True) as browser:
    page = browser.new_page()
    page.goto("目标URL", wait_until="domcontentloaded", timeout=45000)
    page.wait_for_timeout(2500)
    print(page.title(), len(page.content()))
```
（异步版用 `camoufox.async_api`；也支持 Playwright server 模式）

## 实测对比（2026-10-11 本机）

| 站点 | Lightpanda（快档） | **Camoufox（反爬档）** |
|---|---|---|
| 博客园 | 670 ms ✓ | 26.6 s / 90,160 字节 ✓ |
| **抖音** | **0 字节** ❌ | **10.6 s / 920,392 字节** ✓ |

⚠️ **Camoufox 慢**（首次启动要下 fpgen 模型 + Firefox 冷启动）：**只在反爬必需时用**。

## 踩过的坑（都是 2026-10-11 真踩的）

1. **`COMPAT_FLAG` 缺失 → 全删重装**：`Cache\.0.5_FLAG` 不存在时，`camoufox path` / `fetch` 会判定整个安装目录是"旧版不兼容数据"，`shutil.rmtree` 直接删光。**手动装完必须建这个空文件**（否则下一次调用就把你装好的删了 —— 这个坑吃过一次）。
2. **手动安装三件套**：解压到 `Cache\browsers\official\<version>-<build>-<sha8>\` + 写 `version.json` + `config.json` 的 `active_version`；`<sha8>` 是 asset sha256 前 8 位（`repo_cache.json` 里有真值）。
3. **GitHub API 限流会卡死安装**：`fetch` 只用 api.github.com 查版本（匿名 60/小时）。被限流时**直接从 releases 用 ghproxy 镜像下**（文件名 `camoufox-<ver>-<build>-win.x86_64.zip`，约 **1.3 GB**）。
4. **uBlock 扩展下载失败（451）**：`addons.mozilla.org` 被限制；报错但**不影响抓取**，可忽略。
5. **首次启动慢**（要下 fpgen 模型）、**二次启动快**。
6. **GeoIP 未装**：不传 `geoip=` 即可用；要用需单独下数据库。
