---
name: ai-project-scouting
description: 凡哥丢来AI项目视频/仓库要溯源、核实、判断能不能用时加载。含帧扫描溯源与三层判断法。
version: 1.0.0
author: 小南
license: internal
metadata:
  hermes:
    tags: [项目溯源, 开源评估, 视频挖掘, 证据分级, 选型]
    related_skills: [content-ingestion, local-tool-provisioning, video-learning, knowledge-base-utilization, ad-claim-verification]
---

# AI 项目侦察（溯源 → 核实 → 判断能不能用）

## When to Use（何时加载）

- 凡哥丢一个**抖音/B站/YouTube 链接**，问「**这个项目出自哪里**」「**这个项目仔细看看**」「**我们能不能用**」
- 凡哥丢一个 **GitHub 仓库**问「能在 X 上刷/装吗」「我不会安装」
- 要判断某个**开源项目/商业产品**值不值得本地落地、值不值得进产品
- ⚠️ 凡哥这类问题**高频且连续**（2026-10-15 一天 6 条），几乎每次都是「**一个视频 + 一句能不能用**」——别当闲聊答

---

## 一、溯源四步（命中率从高到低，前一步没结果才进下一步）

### 1️⃣ 页面文案里直接找
标题 / 口播稿 / `#标签` 常直接带项目名。抖音用 `content-ingestion` 的 `dy_page.py`，
**真信息在 `.txt` 中段**（开头全是页脚与备案号，别看前 400 字就下结论）。

### 2️⃣ 转写口播
行业号一定会念出「**由 XX 团队开源**」「**GitHub 多少星**」。
`content-ingestion` 的 `dy_transcribe.py` 一步到位（截直链→下载→提音频→转写）。

### 3️⃣ 抽帧 + vision 读画面 ⭐（最容易出决定性证据，别跳过）

```bash
ffmpeg -y -loglevel error -i "dyv_<id>.mp4" -vf "fps=1/2,scale=420:-1,tile=4x4" -frames:v 1 "sheet.jpg"
```

拼图看不清 → **单帧原尺寸 + `vision_analyze(region=[x1,y1,x2,y2])` 裁切放大**。能捞到：

| 画面里的东西 | 说明什么 |
|---|---|
| **水印 / 角标** | 直接点名产品。实例：Vidu S 那次第一帧印着「AI生成数字人 \| Vidu S」——一句话结案 |
| **桌面图标名**（录屏类视频左侧或底部） | 博主装了哪些软件，能反推工具链。实例：读到 `OBS Studio`+`直播伴侣`+`数字人直播助手` → 判定他在做**数字人直播** |
| 播放器控件 / 底部计时 | **计时在走 = 直播中录屏**，不是剪辑合成 |
| 首帧大字 / 标题页 | 常是项目名或口号，第一帧一定要看 |

**坑**：拼图缩到 800px 宽时图标文字会糊成乱码，我因此读错过两次（"Mixbook"→实为 MiniMax、"Geek Bot"→实为 Grok Bot）。**读数不确定就裁切放大复核，别把猜的当看的。**

### 4️⃣ 按特征搜 + GitHub API 核实真身

拿到候选名后**必须核实**，不许凭印象：

```bash
curl -sL --max-time 40 -H "User-Agent: Mozilla/5.0" \
  "https://api.github.com/repos/<owner>/<repo>" -o r.json
# 看 created_at / stargazers_count / license / pushed_at / language
```

- **认准 `owner/repo`** —— 同名仿冒仓库很多（LinkSwift 就有 4 个搬运仓库）
- 用 `api.github.com/search/repositories?q=<name>&sort=stars` 找候选，比网页搜索准
- **未认证 API 有 60 次/小时限流** → 超了就改用抓 github.com 页面 / raw

---

## 二、核实与下载的两个硬坑（都实测踩过）

| 坑 | 现象 | 解法 |
|---|---|---|
| **README 里的下载地址是死的** | 作者另建 `xxx-updates` 仓库当下载页，但**该仓库 Releases 为空** → API 返回 `404 Not Found`（**不是限流，别误判**） | 回**主仓库**查 `api.github.com/repos/<owner>/<repo>/releases`，取 `assets[].browser_download_url` 与 `tag_name` |
| **下载域名被墙但 API 通** | `api.github.com` 正常、页面能抓，但 `github.com/.../releases/download/...` 卡死 `curl: (28) Failed to connect ... 443` | 加镜像前缀 `https://ghfast.top/` + 原始 URL（实测秒下）；`ghproxy.net` / `gh-proxy.com` 备选。**下完核对 `SHA256SUMS`** 再交付 |

**交付安装包给凡哥的标准动作**：下载 → 核 SHA256 → 放到他好找的目录（如 `D:\Documents\我的文档\<用途>\`）→ **报完整绝对路径 + 字节数 + 校验是否一致**。

---

## 三、判「能不能用」——永远分三层答

凡哥问「我们能不能用」时，**不要只回一句能/不能**，按三层拆：

| 层 | 问的是 | 怎么看 |
|---|---|---|
| **① 装软件** | 我这台机器能不能跑起来 | 读官方 prerequisites **原文**（OS / Python / 依赖 / 执行器）。**别信博主的「小白秒上手」** —— OpenGCUA 视频说一键搞定，官方写的是「macOS 14+、还要装 Rust 和 Xcode」 |
| **② 用思路** | 它的设计能不能改进我们现有做法 | 多数项目的**价值在方法不在代码**。例：OpenGCUA「能写脚本就别点鼠标」、Harness²「提两个改法都跑一遍再挑」 |
| **③ 用数据** | 它的评测能不能当我们选型依据 | ⚠️ **先看它考的是不是我们的活**。它测办公文档/法律/编程，我们做短剧/提示词 → 分数**不可直接迁移**，要说明白 |

**成本必须转述**：Harness² 每任务跑 4 遍（token 四倍）、Vidu S 2.8 元/分钟、OpenGCUA 要 Mac。
凡哥最关心的从来是「**值不值**」，不是「它多先进」。

---

## 四、诚实线（凡哥的证据分级：实测 > 官方 > 传闻）

- **没跑过就必须说没跑过**：「我没实测，这是看官方材料得出的判断」——不许把查阅写成实测
- **博主夸大要主动点出来**：标题的「免费 / 一键 / 小白」一律回官方核；视频只说「第一集」、教程在「下集」时**明说这集只是介绍**
- **"开源" ≠ "能用"**：研究代码（v0.1.0）、要特定执行器、有安全警告的，都要说清
- **项目"厉害"不等于"对我们有用"** —— 结论要落到「**我们哪一步会因为它改变**」，否则就是复述广告

---

## 五、常见结论形态（给凡哥的话术）

- ❌ 装不了 → 「软件装不了，**思路全能用**，而且不花钱」
- ✅ 能装 → 「包我已经下好、校验过，路径在这，我带你一步步装」
- 🤔 商业产品 → 「它不是开源，是 X 家的商业服务，价格这样，我们先不用动，但要记下来」
- 🚫 有风险 → 「来源可疑（账号被封/整合包/破解），不建议跑在自己电脑上」

> 2026-10-15 六条视频（Windows-MCP / LinkSwift / 萌芽知识库 / Vidu S / OpenGCUA / Harness²）的完整证据链、官方原文摘录与最终判词：`references/case-log-2026-10.md`
> 内容吸收的按源型强制清单（口播/画面/评论一维都不能少）见 `content-ingestion` 技能。
