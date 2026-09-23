---
name: media-learning
description: Learn from videos, articles, and tutorials that 凡哥 shares — watch, read, absorb, then apply to the pipeline.
triggers:
  - "学一下这个视频"
  - "看看这篇文章"
  - 凡哥分享链接并期待你学习其中内容
  - B站/抖音/YouTube 视频链接
platforms: [windows]
---

# Media Learning

凡哥分享外部内容（视频教程、文章、文档）时，目标是**吸收知识并应用到工作管线中**，不是仅仅做摘要。

## 视频学习流程

### 1. 首选：浏览器 + 视觉直看

对于 B站、YouTube 等视频平台，优先用浏览器打开 + `browser_vision` 截图直接看画面。

**不要做：** 一上来就抠字幕、抓 transcript、调 API 提取文本。画面才是视频的核心信息载体，字幕只是辅助。

### 2. 备选：下载到本地

如果浏览器遇到验证码/登录墙无法播放，用 yt-dlp 下载：

```bash
# 安装（如果没装）
uv pip install yt-dlp

# 下载
yt-dlp -o "下载路径/%(title)s.%(ext)s" "视频链接"
```

下载后用 `vision_analyze` 逐帧/关键帧分析。

### 2b. 教学/方法类短视频的「双线对齐」管线（2026-09-14 实测有效）

带口播的教程/方法类视频，**画面和口播各有各的信息**，两条线都要拿，然后对齐：

```bash
V="视频.mp4"
mkdir -p frames
ffmpeg -hide_banner -loglevel error -i "$V" -vf "fps=1/1.8" -q:v 2 "frames/f_%03d.jpg" -y   # 1.8s 一帧，50s 短片约 28 帧
ffmpeg -hide_banner -loglevel error -i "$V" -vn -acodec pcm_s16le -ar 16000 -ac 1 audio.wav -y
```

```python
# 转写（后台跑，中文用 medium；短音频几分钟内出结果）
from faster_whisper import WhisperModel
m = WhisperModel('medium', device='cpu', compute_type='int8')
segs, info = m.transcribe('audio.wav', language='zh', vad_filter=True)
for s in segs: print(f'[{s.start:.1f}-{s.end:.1f}] {s.text}')
```

**做法**：转写在后台跑的同时，用 `vision_analyze` 分批读关键帧（一次 6 张左右，`image_url` 用 Windows 绝对路径），
然后把**口播说的规则**和**画面展示的步骤**对齐 —— 两边对上的那条才是可执行的方法。

**实测收获（BV1ka411M7kV，51 秒）**：口播讲了「减去一笔 → 加细节 → 调空间」的四步法，画面展示了每一步的中间稿，
两者对齐后才还原出完整方法（已固化为 `logo-generator` 的「字母减法法」）。
**结论：口播给"为什么"，画面给"怎么做"，缺一条都只能得到半套方法。**

**抽帧密度**：短教学片（<2 分钟）用 `fps=1/1.8`（约 1.8s 一帧）；长片先 `fps=1/10` 粗扫定位章节，再对目标段落加密。

### 3. 输出：应用到管线

学习完不是"总结一下"，而是：
- 提取可操作的规则/步骤
- 写入对应的管线文件或 memory 日志
- 更新 DASHBOARD 进度

## 外部工具/平台类链接（不是教程）——先判形态与可接入性

凡哥发链接时先分两类，动作完全不同：

- **教程/方法类**（"学一下这个""这个炉子有点小厉害"）→ 走上面的双线对齐管线，产出 = **可执行规则**
- **工具/平台类**（"你看我们能不能把它加入进来给我们赋能"）→ 产出 = **能否接入的判断 + 接入路径**，不是内容摘要

工具/平台类三步：

1. **判形态**：网页社区 / 桌面客户端 / SaaS+API / 本地工具。判据看**安装包名与体积**（`*_x64-setup.exe` = Tauri 桌面端；几十 MB = 纯客户端、不内置模型）和**官网自述**（"交给熟悉的 AI 运行" = 它自己不是 AI，是能力包分发器）。
2. **判可接入性**：读它的**前端 JS bundle** 挖 API 端点、数据结构、内置的集成定义（配方见 `references/platform-integration-recon.md`）。**同一套数据标准 = 接入成本极低**；封闭自有字段 = 只能人工搬运。
3. **给结论 + 他该做的事**：技术侧只读侦察我做完；**申请/扫码/登录/安装授权一律他本人做**（凡哥环境纪律：不擅启无关软件）。结论里必须写清**边界**——哪些能流通、哪些绝不外发（南溟岛 IP / 剧本 / 客户项目）。

纪律：评估阶段**别先把软件装上**——本次只下载安装包做静态检查、未安装，报告时明确说清"只下载没装、要装吗"。

> 实例：**炉子 LUZI**（`luzi.top`，秋芝2046 团队的桌面端「AI 能力网络」；能力包 = zip + `SKILL.md` 入口，资产分 skill/prompt/reference 三类；**Hermes 是它代码里写死的官方支持 Agent 之一**，支持 copy/link 两种部署模式；它默认扫 `~/.hermes/skills`，而凡哥的技能库在 `D:\Hermes\skills` → 需 junction 联通）。完整侦察记录与 JS 挖法：`references/platform-integration-recon.md`。

## 平台取流对照（2026-09-18 更新）

| 平台 | 取流方式 |
|---|---|
| B站 | ✅ yt-dlp 直取（提取器成熟、无需签名参数；代理被拒时改走国内直连） |
| YouTube | ⚠️ 公司网络可能被墙 |
| **抖音** | ❌ yt-dlp 直取必 403（需 fresh cookies ＋ 页面会话态）→ **改走 CDP 路线**：起带 `--remote-debugging-port` 的独立 Chrome → Playwright `connect_over_cdp` → 抓 network 里的**签名 CDN 直链**（`<video>` 只有 blob:） → curl ＋ Referer 下载 → ffmpeg 合流。完整的抓取全链（失败路清单、双流下载、ASR 字段名、抽帧接触表坑、同音错字校验）见 **`video-learning` skill 的 `references/douyin-capture.md`** |

- 抖音三条别再试的路：`web_extract` 抓页面（JS 渲染无正文）、yt-dlp 传 `jingxuan?modal_id=` 形态（Unsupported URL）、`--cookies-from-browser chrome`（Chrome 运行时 cookie 库被独占）。
- yt-dlp 用 `uv pip install` 安装，不要用系统 pip（可能不在 PATH）
