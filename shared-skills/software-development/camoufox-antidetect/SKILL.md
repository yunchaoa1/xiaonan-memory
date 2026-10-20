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

---

## 小红书实测（2026-10-15，小南）

### 必须登录

未登录时搜索页正文只有「登录后查看搜索结果」+ 登录框，**有效内容 0 字**。
搜索引擎也救不了（`site:xiaohongshu.com` 几乎无索引）。

**登录档做法**（登录一次，以后无头复用）：

```python
from camoufox.sync_api import Camoufox
with Camoufox(headless=True, humanize=True,
              persistent_context=True,
              user_data_dir=r"D:\Hermes\data\camoufox\xhs-profile") as ctx:
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
```

有头模式打开 → 自动点 `text=登录` → 手机扫码。实测 **75 秒**检测到登录成功。

⚠️ **登录态判断别信 cookie 名** —— 小红书给**未登录访客也发 a1/webId**，按 cookie 判会 100% 误报。
**正确判据**：页面出现 `登录后查看` / `登录后推荐` / `手机号登录` = 未登录；`section.note-item` 数量 > 3 = 已登录。

### ⚠️ 风控阈值（实测踩到，血泪）

**几分钟内访问 27 个博主主页 + 十几次搜索 → 触发风控**：

| 页面 | 被拦表现 |
|---|---|
| 博主主页 | **硬拦截**：302 到 `website-login/captcha`，标题 `Security Verification`，滑块 "Drag the arrow to complete the puzzle" |
| 搜索结果 | **软降级**：页面正常打开、无验证码，但 `note-item: 0`（内容不渲染）、`user-links` 只剩自己 |

- **两种都解不了**：滑块无人能解；软降级只能等冷却。**硬试只会加重风控。**
- 触发后**立即停手**，冷却期通常几十分钟至数小时。

### ✅ 恢复与正确跑法（2026-10-20 实测恢复，已验证）

**结论先说：小红书不是"技术墙"，是"节奏墙"。** 风控＝频率 + 行为被判机器，不是签名问题。
**只要放慢到一个真人的速度，同一个 profile、headless、无任何代理也能稳定进主页。**

**实测记录（2026-10-20）**

| 测试 | 结果 |
|---|---|
| 10-15 触发风控 → 10-20 再测（冷却 5 天） | ✅ 首页 `section.note-item` = **30**，搜索页 = **30**，用户链接带新 `xsec_token` |
| 连续进 3 个博主主页，间隔 8 / 31 / 37 秒 | ✅ **3/3 正常**，每个 **36 张笔记卡片**，0 次验证码 |

**固定跑法（照抄，别再自己加频率）**

1. **先热身**：打开 `https://www.xiaohongshu.com/explore`，等 6 秒，`mouse.wheel(0,800)` 滚一下，再等 4 秒 —— 模拟"人先刷两眼"
2. **每个动作之间 sleep 25–40 秒随机**（第一个可以短些）
3. **单次会话 ≤ 10 个主页**；被拦的标志是 URL 里出现 `captcha` —— **立刻 break，不要重试**
4. 关键操作后 `wait_for_timeout(7000)` 再取内容（渲染慢，取早了是 0）
5. 只剩搜索页软降级（`note-item: 0`）时也是**等冷却**，不要换关键词硬刷

**判定"是否已恢复"的一行判据**：`document.querySelectorAll('section.note-item').length` ≥ 30 = 好了；= 0 = 还在罚站。

**配套脚本（本机已存，直接跑）**

```bash
# 探状态：首页+搜索两个动作，报 blocked/正常
python D:/Hermes/scripts/xhs_status_probe.py
# 慢速抓主页：关键词 → 用户tab → 主页（25-40秒间隔，被拦自动停）
python D:/Hermes/scripts/xhs_profile_slow.py "胖男生穿搭" 3
```

**社区主流方案对照（2026-10 调研）**：MediaCrawler（42k★）的做法**不是**逆向签名，而是 Playwright/CDP 用真浏览器让页面自己生成 `x-s`/`x-t`，再拦截请求复用 —— 跟我们这条路同源，差别只在**它把限速和登录态做成了配置**。Spider_XHS / xhshow 那类"纯算签名"是暴力逆向，版本一变就废，且明确违规，**不采用**。


### 抓取要点

- 搜索页 tab：`全部 / 图文 / 视频 / 用户`，切换用 `page.get_by_text("用户", exact=True).first.click()`
- 笔记卡片：`section.note-item`；标题 `a.title`；作者 `a[href*="/user/profile/"]`；点赞 `.count`
- **链接必须带 `xsec_token`**（不带访问不了，且 token 有时效）
- 「用户」tab 的卡片文本是**换行分隔**（不是 `|`）：`昵称\n更新时间\n小红书号\n认证标签\n粉丝・N\n笔记・N\n关注`
- 结果质量警告：搜「男士穿搭 / 夏季穿搭」这类大众词，**大量女装号 + 清仓店铺号**混入；**小众细分词**（如"胖男生穿搭""大码男装"）反而更对口
- **粉丝量 ≠ 权威**：高粉丝号常见同质化营销矩阵（两个号简介一字不差）、刷量号（同一标题重复 10 遍）

### 配套脚本（本机已存）

`D:\Hermes\scripts\` 下：`xhs_login.py`（登录档）、`xhs_search_probe.py`、`xhs_crawl_notes.py`、`xhs_find_bloggers.py`、`xhs_profile_probe.py`

---

## 把一篇笔记的"内容"真正拿到手（2026-10-20 全链路实测）

> 教训：能进主页 ≠ 拿到内容。三个坑连在一起，逐个记：

### 坑 1：卡片裸链会掉进登录墙

`section.note-item` 里有 4 个 `a`。第一个是 **`/explore/{id}` 无 token** → 进去只有 901 字的登录页。
**token 在 `.title` / `a.cover` 那个锚点上**：

```
/user/profile/{uid}/{note_id}?xsec_token=...&xsec_source=pc_user
```
取法：`sec.querySelector('a.title')`（或 `.title` 的 `closest('a')`）；也能直接**点卡片**，跳转后 URL 自动带 token。

### 坑 2：正文可能根本不在文字里

- `window.__INITIAL_STATE__` **新版网页已没有**（2026-10 实测 `hasState:false`）
- 图文笔记的 `<img>` 是**懒加载占位**（`//picasso-static...png`），`og:image` 也是占位图 → 抓 img 全空
- **干货号大多拍口播视频**：`document.querySelectorAll('video').length === 1`，`src` 是 `blob:`，画面文字是烧进视频的

### 坑 3：视频直链这样取（唯一稳定解）

```python
# 播一下，让视频流真正发请求，然后从 performance 里拿
page.locator("video").first.click()
cands = page.evaluate("""() => performance.getEntriesByType('resource')
    .map(e => e.name).filter(n => /\\.mp4/.test(n) && n.includes('sns-video'))""")
```
下载必须带 `Referer: https://www.xiaohongshu.com/`（否则 403），直链形如 `sns-video-qc.xhscdn.com/stream/..._258.mp4?sign=...&t=...`（**有时效**）。

### 视频 → 文字（本机已装齐）

```bash
ffmpeg -y -v error -i x.mp4 -vn -ac 1 -ar 16000 -c:a pcm_s16le x_16k.wav
# 模型常驻 D:\Hermes\models\faster-whisper-large-v3，GPU float16
```
**实测速度：60 秒口播 → 转写 27 秒（≈2.2× 实时）**，中文准确度直接可用（只需压少量同音词，如"缩质面料"疑为"硬挺/挺括面料"，标待确认）。
⚠ ffmpeg 用 `subprocess.run([...])` 传参列表，**别拼字符串**（`os.system` 在 MSYS 下报 "filename syntax is incorrect"）。
术语表 `initial_prompt` 写本领域词（版型/正肩/落肩/克重/微胖/大肚腩…），错词明显减少。

### 本次新增脚本

| 脚本 | 作用 |
|---|---|
| `xhs_status_probe.py` | 探风控状态（首页/搜索卡片数 → 是否已解） |
| `xhs_profile_slow.py` | 慢速抓博主主页笔记清单 |
| `xhs_blogger_notes2.py` | 抓笔记标题/标签 + 存卡片 token 链接 |
| `xhs_videos_batch.py` | 按 token 链接批量下 mp4（慢速） |
| `xhs_transcribe.py` | 批量 ffmpeg + large-v3 转写（txt/json） |
| `xhs_card_diag.py` / `xhs_note_shot.py` | 结构诊断（卡片锚点 / 页面截屏） |

