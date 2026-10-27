---
name: content-ingestion
description: 凡哥丢视频/网页/文档/播客让我吸收时用。按源型强制取全,防漏口播画面。
version: 1.0.0
author: 小南
license: internal
metadata:
  hermes:
    tags: [内容吸收, 视频理解, 转写, 多模态, 防漏, 验收]
    related_skills: [video-learning, video-analysis, media-learning, ocr-and-documents, captcha-solving]
---

# 内容源吸收（按源型强制清单）

## When to Use（何时加载）

- 凡哥**丢来一个链接/视频/文件**说「**看下这个 / 学习一下 / 吸收 / 对比一下 / 这个项目怎么样**」
- 我要**从外部内容里提取知识并落地**（写技能、对比、决策）时
- **⚠️ 不管内容看起来多简单，先走本清单** —— 漏掉的往往不是"难的"，是"我以为是文字就够了"的

## 为什么要这张清单（血的教训 · 2026-10-11）

凡哥给了一条抖音视频，我**抓了网页就回话**：标题 + 描述 + 评论。
**结果漏掉了博主的口播内容** —— 而**关键信息恰好在口播里**（"云端隔离浏览器轻松突破验证码"）。
凡哥一句「**你是不是没学到**」才发现。

**根因**：我把**视频**当成**网页**处理。视频是**多模态**的（口播 + 画面 + 时序 + 文字），
**只取文字 = 只取了一维**。而且我**当时手上已经有 whisper 和 ffmpeg**，只是没接进"视频"这个场景。

## 铁律：按源型走清单，一维都不能少

| 源类型 | 必取（一维都不能少） | 工具（本机已就绪） |
|---|---|---|
| **视频（短视频/口播）** | ① 文案/标题/标签 ② **口播音频 → 转写**（❗最容易漏） ③ 评论区（常有干货） ④ 画面关键帧 | ① Camoufox 抓页 ② **Camoufox 截视频直链 → ffmpeg 提音频 → faster-whisper 转写** ③ 同上抓取 ④ PySceneDetect 切镜头 + vision |
| **视频（长片/教程）** | 上述全部 + **分段** + 时间轴（哪段讲什么） | 同上；转写带时间戳 |
| **网页/文章** | 正文 + 代码块 + 表格 + 图片说明 | `trafilatura` / Lightpanda / Camoufox |
| **文档（PDF/DOCX/PPT）** | 全文 + 表格 + 图注 | `markitdown`（先试）→ 不行再 pymupdf |
| **音频/播客** | 转写（带时间戳） | ffmpeg + faster-whisper |
| **GitHub 项目** | README + 目录结构 + 依赖 + 最近提交 + **是否官方仓库**（防仿冒） | Camoufox 抓页；`ghproxy` 拿 raw |
| **图片/截图** | OCR 文字 + 画面语义 | 视觉工具 |

## 视频吸收的标准动作（照抄即可）

```bash
# 1) 抓页面文字（标题·文案·点赞·发布时间·评论区）—— 本技能自带，专治抖音
python "D:\Hermes\skills\productivity\content-ingestion\scripts\dy_page.py" "<视频页URL>"
#    输出 dy_page_<tag>.html（整页 1.5MB，留给正则挖数据）+ dy_page_<tag>.txt（全部可见文字）
#    ⚠️ 抖音正文开头全是页脚/导航，真信息在中段 —— 必须整页存，别只看 probe 的前 400 字

# 2) 一步到位：截直链 → 下载 → 提音频 → 转写
python "D:\Hermes\skills\productivity\content-ingestion\scripts\dy_transcribe.py" "<视频页URL>"
#    内部：Camoufox 截 .mp4 直链 → urllib 下载 → ffmpeg 16k 单声道 → faster-whisper 转写
#    ⚠️ 坑：① 抖音需 cookie（yt-dlp 读 Chrome cookie 常被锁 → 用 Camoufox 截链绕过）
#           ② HF 直连超时 → 脚本已内置 HF_HUB_OFFLINE=1 + 自动挑本地完整模型
#           ③ large-v3 缓存是空壳（1KB 空目录）→ medium 完整（1.5G），脚本自动优先 medium
#           ④ 【2026-10-14 踩】别跑 D:\Hermes\cache\dy_transcribe.py 的旧副本（写死 large-v3，必卡
#              HF 超时 ~80s 后崩）；只跑上面技能目录里这份。cache 副本是历史遗留，已同步但不要引用
#           ⑤ 【实测铁证 2026-10-14】凡哥的分享链接形如
#              https://www.douyin.com/user/self?...&modal_id=<id>（个人主页弹窗形式）
#              → 原形抓 3 次都只有 ~1.1K 字符（只渲染出页脚，主视频根本没出来）；
#              → 换成 https://www.douyin.com/video/<id> 第 1 次就拿到 3.1K（主视频文案+评论）
#              收到抖音链接，先做这个替换，省一整轮。dy_page.py 已内置 3 次重试兜底
#           ⑥ 抖音 SPA 每次渲染内容不同（同一 URL 三次：4579/3249/1637/1115 字符都见过）
#              → 抓完先看字符数，<2000 基本是空壳，别当成"没内容"就下结论
#           ⑦ 【2026-10-27 解法】长视频（>10 分钟）抖音音视频分轨，dy_transcribe.py 抓到的
#              直链只有 Video 轨 → ffmpeg 报 "Output file does not contain any stream"。
#              yt-dlp 也救不了（要抖音自家反爬 cookie，导出浏览器 cookie 仍 403）。
#              正解 = scripts/dy_grab_audio.py：Camoufox 真页面截 media-audio-und-mp4a 请求
#              → 立刻下载（URL 带签名会过期）→ 转 16k wav → faster-whisper 内置转写。
#              判据：下载完 ffprobe 看有没有 audio 流，没有就换它
```

## 验收标准（怎么知道"吸全了"）

**逐条自问，答不上就是没吸全：**

1. **口播类内容**：转写字数 > 0 吗？（视频没转写 = 没吸收）
2. **画面类内容**：关键帧看过吗？画面里有没有文字/演示（架构图、代码、参数）？
3. **核心主张**：这个内容**主张什么**？**证据是什么**？
4. **可操作性**：有没有**具体到能做的动作**（工具名/命令/参数）？
5. **可信度**：说话人是**权威**还是**营销**？**数字有无出处**？（凡哥证据分级：实测 > 官方 > 传闻）
6. **与我有关**：对我们**现有能力**是补充、重叠、还是冲突？

**⚠️ 反向自检**：如果我只用"抓网页"就准备回话，**立刻停下** —— 问自己"这条内容的载体是什么？我取的是全部维度吗？"

## 本机现成的吸收工具链（别再临时找）

| 环节 | 工具 | 状态 |
|---|---|---|
| 抓页面（含反爬站） | Camoufox / Scrapling.StealthyFetcher / Lightpanda | ✓ |
| 截视频直链 | Camoufox 监听 request | ✓ |
| 下载 | urllib / aria2 | ✓ |
| 提音频 | ffmpeg | ✓ |
| 转写 | faster-whisper（medium 完整） | ✓ |
| 切镜头 | PySceneDetect | ✓ |
| 正文提取 | trafilatura | ✓ |
| 文档转换 | markitdown | ✓ |
| 验证码 | ddddocr（字符/滑块/点选） | ✓ |

## 落地（照 `local-tool-provisioning` 六步）

吸收完必须：**写进对应技能 → 挂 `skill-router` → 更新 `DASHBOARD.md` → 提交同步**。
**只"看懂了"不算吸收完 —— 要变成以后能自动用的东西。**
