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

> ⏱ **长音频另走一路**：会议/讲座这类 **>10 分钟**的素材别用上面 CPU medium 的写法（几十分钟会磨很久）→ 用 `meeting-recording-to-minutes` 的**本地 large-v3 GPU 管线**（RTX 5080 上 73 分钟 ≈ 18 分钟出稿，含 hf-mirror 取模型与 `initial_prompt` 术语表，外加"边跑边读"手法）。

**做法**：转写在后台跑的同时，用 `vision_analyze` 分批读关键帧（一次 6 张左右，`image_url` 用 Windows 绝对路径），
然后把**口播说的规则**和**画面展示的步骤**对齐 —— 两边对上的那条才是可执行的方法。

**实测收获（BV1ka411M7kV，51 秒）**：口播讲了「减去一笔 → 加细节 → 调空间」的四步法，画面展示了每一步的中间稿，
两者对齐后才还原出完整方法（已固化为 `logo-generator` 的「字母减法法」）。
**结论：口播给"为什么"，画面给"怎么做"，缺一条都只能得到半套方法。**

**抽帧密度**：短教学片（<2 分钟）用 `fps=1/1.8`（约 1.8s 一帧）；长片先 `fps=1/10` 粗扫定位章节，再对目标段落加密。

### 3. 输出：对照 → 报批 → 才落地（凡哥 2026-09-24 定，最高优先）

**只学凡哥投喂的**：他说"只学习我给你发的，其他的先不管"。即使挖到同一作者/相关主题的系列教程清单，也**先放着**——不主动收集、不批量抓、不顺手学。

**一点一点落，防规则打架**：凡哥原话"我担心我们学的多了会有冲突，我们一点一点来"。一次一条、**报批后才动 skill**，不批量落地。

落地标准流程（2026-09 三套方法——好莱坞开场 / 表情真实 / 空间不漂移 / 主体占框——均按此跑通）：

1. 抓取＋拆解（本 skill 取流管线：转写＋抽帧逐字读）
2. **对照现有 skill 做查重表**：列"我们已有什么 / 真新的是什么 / 写法级差异在哪"——先查重，防重复落规则
3. **报告凡哥**：方法要点＋示范句＋与现有体系的差异＋建议落到哪个 skill
4. **他说"落/改"才动 skill**；没批之前只存档笔记（`opc-sim/research/学习笔记_<主题>.md`），skill 一个字不动
5. 落完做三件收尾：`sync_skills.py push` ＋ DASHBOARD 记录 ＋ git 提交
6. **冲突哨兵**：新规则与现有条款重复/矛盾时立刻报告凡哥——"打架的规则还不如没有"

## 外部工具/平台类链接（不是教程）——先判形态与可接入性

凡哥发链接时先分两类，动作完全不同：

- **教程/方法类**（"学一下这个""这个炉子有点小厉害"）→ 走上面的双线对齐管线，产出 = **可执行规则**
- **工具/平台类**（"你看我们能不能把它加入进来给我们赋能"）→ 产出 = **能否接入的判断 + 接入路径**，不是内容摘要

工具/平台类三步：

1. **判形态**：网页社区 / 桌面客户端 / SaaS+API / 本地工具。判据看**安装包名与体积**（`*_x64-setup.exe` = Tauri 桌面端；几十 MB = 纯客户端、不内置模型）和**官网自述**（"交给熟悉的 AI 运行" = 它自己不是 AI，是能力包分发器）。
2. **判可接入性**：读它的**前端 JS bundle** 挖 API 端点、数据结构、内置的集成定义（配方见 `references/platform-integration-recon.md`）。**同一套数据标准 = 接入成本极低**；封闭自有字段 = 只能人工搬运。
3. **给结论 + 他该做的事**：技术侧只读侦察我做完；**申请/扫码/登录/安装授权一律他本人做**（凡哥环境纪律：不擅启无关软件）。结论里必须写清**边界**——哪些能流通、哪些绝不外发（南溟岛 IP / 剧本 / 客户项目）。

### 从「视频/链接里提到的项目」到仓库：先定位，再核证（2026-10-15 固化）

**⚠️ 视频里常常根本不给仓库地址** —— 抖音页面正则挖不到 github 链接（挖到的全是推荐流的别的视频）。
按顺序试这四条：

1. **先搜 B站同名原版** ⭐（本次唯一破局的一步）
   抖音版常是搬运/同步；**同一博主在 B站的原版简介写得更全，项目名往往只写在 B站简介里**。
   实例：抖音页零仓库线索 → 搜视频标题 → 命中 B站同博主同名视频 → 简介原话"我也把这套「**萌芽知识库**」开源到了 GitHub" → 一步锁定 `ThreeFrontTeeth/mengya-knowledge`。
   **做法**：拿文案里的独特短语（标题 / 账号名）去 `web_search`，命中 B站/知乎/公众号就拉全文。
2. **搜视频标题本身**（跨平台同步时，两边简介会互相泄露项目名）
3. **GitHub 搜项目中文全名 + 多写法**：`萌芽知识库` 一次命中，而 `萌芽 obsidian` / `mengya knowledge` / `sprout knowledge base obsidian` 全 0 结果 —— **中文名原样搜最有效**。
4. **博主昵称常被直译成仓库 owner** —— "三颗门牙" → `ThreeFrontTeeth`。**owner 对得上博主名 = 顺带把防仿冒做完了。**

**核证两条路（互为备份）**：
- `api.github.com`（快，直接给 star / pushed_at / license / owner type）—— **未认证 60 次/小时**，连发几组搜索就 `403 rate limit exceeded`
- 限流后 → `web_extract` 拉 `https://github.com/<owner>/<repo>` —— **无配额**，能读全 README 渲染正文 + 文件树（本次靠它拿全）

**必查**：star / fork / **最后 push**（别只看 star）/ 许可证 / **类型**（是软件？是脚本？还是**一堆 md 根本不含代码**？）/ 是否仿冒（高星项目必有同名搬运，**认 owner 不认仓库名**）。

### 判断交付模板（凡哥认这个）

1. **一句话结论先行**（"不需要部署 —— 但这个判断我给证据，你自己看"）
2. **项目体检表**：star / fork / 最后 push / 许可证 / 类型 / 是否官方
3. **对比表 —— 必须给**：把项目每一层拆开，逐条对上"我们已有的"，标 **谁强**。
   **只给结论不给对比表 = 没干活**，等于让凡哥自己判断。
4. **诚实标注**：我没实测的部分 / 无许可证（默认保留所有权利，不能再分发、不能进产品）/ AGPL 传染性（自用无妨，**进凡哥产品要单独提示**）
5. **值得借鉴的 1~2 个点 + 最薄做法**（凡哥偏好"最薄改造"，明确反对把 Skill 扩成平台工程）
6. 结尾**只问一件事**（凡哥铁律：事一件一件过）

**可信度信号（凡哥证据分级：实测 > 官方 > 传闻）**：
- 抖音页面会标 **"作者声明：内容由 AI 生成"** —— 减分项，要报
- ⭐ **项目 README 里的作者打假声明是最强反证。** LinkSwift 那条：视频标题"网盘界的天塌了"，
  而作者 README 原文否认 —— "项目未以任何形式承诺、宣传或实现对网盘限速机制、功能的破解……
  任何第三方在推广、转载或介绍本项目过程中所作出的夸大、误导性宣传*，均不代表本项目立场
  *（包括但不限于"加速下载""速度起飞""限速破解"等表述）"。
  → **视频宣传与项目作者原文冲突时，以作者原文为准，并直接告诉凡哥。**
- **顺手搜同题材反面视频**：B站"Karpathy 的 LLM-Wiki 火了——但我不推荐"（3.5万播放）、
  "别用 Obsidian 搞个人知识库了，真没用"（2.5万）—— 高播放反方是真实可信度信号，值得一并报。

> 三条实况案例（Windows-MCP / LinkSwift / 萌芽知识库）的完整数据与判断表：
> `references/video-recommended-oss-vetting.md`

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
