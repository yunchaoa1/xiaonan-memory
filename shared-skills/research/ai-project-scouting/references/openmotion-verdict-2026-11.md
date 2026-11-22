# OpenMotion 核实记录（2026-11-21）

凡哥原话：「**看一下这个项目，我感觉对我们有大用**」，附一条抖音链接（11 万赞）。

---

## 一、溯源路径（标题里根本没有项目名）

| 步骤 | 结果 |
|---|---|
| 1. `wigolo fetch` 抓抖音页 | 只拿到 shell（扫码登录页），**标题有、项目名没有** |
| 2. 抓页面截图 → vision 读 | ⭐ **网页搜索框里躺着 `opendesign/lopenmotion`** —— 博主自己搜过，字还留在框里 |
| 3. 按 `opendesign/lopenmotion` 猜 GitHub API | **404**（`opendesign/openmotion` 也 404） |
| 4. `web_search "lopenmotion openmotion GitHub 开源 视频 动画"` | **命中真身：`nexu-io/openmotion`** |

**教训**：博主记得的 owner 是错的，但 repo 名足够近似。
**猜两三次 404 不能推断"项目不存在"，必须回搜索撞一轮。**

附带：`raw.githubusercontent.com` 直连 DNS 失败（`getaddrinfo failed`）时，`https://ghfast.top/https://raw.githubusercontent.com/...` 可用；
`ghfast.top` 代理 `api.github.com` 会 403（FORBIDDEN），但代理 raw 文件正常。

---

## 二、仓库事实（API 核实）

- `full_name`: `nexu-io/openmotion`
- ★ **9,511 → 9,600**（截止本记录）
- License: **Apache 2.0**
- `created_at`: 2026-05-11；Releases: 0 / Tags: 0
- 团队：**OpenDesign**（同团队另一款开源 AI 设计工具 GitHub 超 10 万星）
- 官网：`https://open-design.ai/motion/`

**第三方报道**（智东西）：OpenDesign 出品，配合 DeepSeek Harness 做产品动效，实测几个动效视频成本约 13 元。

---

## 三、它到底在做什么（README 原文口径）

> **the first full-stack agentic video generator**
> Upload a reference video or paste a social video link to **recreate it with your own brand kit (logo, colors and fonts) and copy**.
> **Code video with HTML.** OpenMotion uses HTML, CSS and JavaScript to describe scenes, typography, layout, transitions and timing. Recorded footage, generated clips, images, music and voice-over become media inside the composition. The same project opens in Studio and renders to MP4.
> **Motion.md** — a Markdown format for shot order, timing and transitions.

**关键：不是"提示词生成画面"，是"用代码编排 + 素材拼装"。**

---

## 四、skills 目录 = 能力清单（`api.github.com/.../contents/skills`）

| 技能 | 干什么 |
|---|---|
| `openmotion-director` | 动效导演：动态叙事、镜头衔接、状态延续、声画关系。**电竞集锦、解说、产品演示、品牌片** |
| `openmotion-recreate` | **复刻参考片**：链接/文件 → 拆解 → 重建可编辑工程。"Make one like this" / "I want this feel" 都算 |
| `openmotion-video-to-template` | 视频 → 可复用模板包 |
| `openmotion-template-to-video` | 模板 → 视频 |
| `openmotion-production` | 既定工程的执行/导出 |
| `openmotion-design` | 设计 |
| `openmotion-media` | 素材生成（图/视频/音乐/语音） |
| `openmotion-game` | 游戏向 |
| `openmotion` | 入口 |

`director` 的 description 原文里有一句值得抄的口径：

> Motion 感来自经过设计的变化与节奏，**不等于运动量、镜头速度或特效数量**，准确性与可读性仍须成立。

`recreate` 的边界原文（很重要）：

> References that also contain **portraits, product photography, live-action or AI footage, narration or music are in scope**: those parts use configured media generation **while the structure stays editable**.

→ 也就是说：**人物/实拍部分交给 AI 生成，结构（镜头顺序、时长、转场）保持可编辑**。这是它和"生成式视频"的根本分工。

---

## 五、安装（官方 install.md 口径）

需要 **Git、npm、Node.js 26.11.1**；源码预览与导出还要 **Chrome/Chromium + FFmpeg/FFprobe**。

```sh
git -c filter.lfs.process= -c filter.lfs.smudge= -c filter.lfs.required=false clone \
  --depth 1 --single-branch --branch main https://github.com/nexu-io/openmotion.git
cd openmotion
npm ci
npm run build:studio
npm start
```

⚠️ README 里另有一段 `git clone --branch feature/motion ... html-anything.git openmotion` —— **是不同分支/时期的写法，别照抄**，以 `main` 那条为准。

## 六、内置模型目录（BYOK，自带 key）

| 素材 | 内置模型 |
|---|---|
| 图片 | Codex Image；Atlas Cloud 的 **Nano Banana 2**；fal.ai 的 FLUX Schnell |
| 视频 | Atlas Cloud 的 **Seedance 2.0**；fal.ai 的 Wan 2.2 |
| 音乐 | Atlas Cloud 的 **Suno v4** |
| TTS | fal.ai 的 **Kokoro** |

**只用自己已有的素材、不调生成 API 也能跑**（本地工作流不收软件订阅费、不收单次渲染费）。

---

## 七、三层判词

| 层 | 结 |
|---|---|
| ① 装软件 | **能装**。本机已有 FFmpeg/Chrome，缺 Node 26.11.1。是"一个下午"的量，不是一键 |
| ② 用思路 | ⭐ `recreate`：丢链接 → 拆结构 → 重建，适合**学爆款节奏**；`video-to-template`：逆向竞品动效规律 |
| ③ 用数据 | 无（没有可迁移到短剧的评测数据） |

**关键区分（回答"我们能不能用"必须先说）：**

| | 动效视频 | 剧情视频 |
|---|---|---|
| 做什么 | 产品宣传片、界面演示、文字动画、数据可视化、品牌片 | 角色演戏、对话、情绪 |
| 靠什么 | 代码编排 + 素材拼装 | 模型生成画面（H3 / Seedance） |

**结论**：做不了短剧正片，**补的是"包装层"空白** —— 片头片尾/演职员表/平台 Logo 动效、预告片文字卡、给客户演示的产品动画、拆爆款节奏。
**一句话**：解决包装层，不解决内容层；正片质量还没吃透之前，优先级不该排它前面。

---

## 八、诚实边界

- **没装、没跑过。** 以上全部来自 GitHub API + README 原文 + 两个第三方报道。
- 视频宣传的「还原度超 95%」「300+ 模板」「152+ Brandkit」**均未核实**。
- 凡哥拍板"先装一个试"时，才算进入实测。
