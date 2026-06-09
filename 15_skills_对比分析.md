# 🦐 小南 vs 视频「OpenClaw 15 个必装 Skills」——逐项对比分析

> 数据来源：ClawHub 官方页面、OpenClaw 官方文档、本地技能文件、视频 Whisper 转录
> 分析日期：2026-06-06

---

## 对比结论（先看总结）

| 状态 | 数量 | 说明 |
|------|------|------|
| ✅ **已有，能力接近或更强** | 4 个 | 浏览器操控、图片分析、天气、文件操作 |
| ⚠️ **部分覆盖，但有差距** | 4 个 | 搜索、内容摘要、知识库、Git 操作 |
| ❌ **没有，但值得关注** | 3 个 | 技能发现、自主代理、任务分解 |
| ❌ **没有，且与凡哥需求无关** | 4 个 | Google 全家桶、智能音箱、编程工作流、代码管理 |

---

## 逐项详细对比

### 1. Spy Skill / Find Skills（AI 专属猎头）

**视频描述：** 说需求→AI自动在 ClawHub 搜索匹配技能→自动安装

**官方数据：** ClawHub 有注册 (`find-skills`, `spy-skill`)，但页面为 JS 渲染无法抓取。推测是一个帮助 OpenClaw Agent 自动搜索 ClawHub 技能市场的元技能。

**小南现在：** ❌ 没有。

**差距：** 我现在无法自己搜索 ClawHub 找技能然后建议你安装。需要你来告诉我有什么技能，或者你主动去 ClawHub 浏览。`openclaw skills search` 是 CLI 命令但我不在能运行它的上下文中。

**对凡哥的价值：** 中等。如果这个技能能用，你就不用自己去 ClawHub 翻找新技能了，问我我就会自己去搜。

---

### 2. Superpowers（联动总指挥 / 开发工作流）

**视频描述：** "所有技能的联动总指挥"，技能相互配合协同工作

**官方数据：** [ClawHub 已确认](https://clawhub.ai/wlshlad85/superpowers) — 作者 wlshlad85，下载 18.3k，⭐14

实际功能与视频描述**有重大差异**：
- 这是一个 **软件开发工作流** 技能，不是"技能协作调度器"
- 包含 5 个阶段：Brainstorm→Plan→Subagent TDD→Debug→Finish
- 强制 TDD（测试驱动开发）、Spec-first（规格先行）
- 使用 `sessions_spawn` 驱动子代理执行任务+代码审查

**小南现在：** ❌ 没有安装这个技能。但我有 `sessions_spawn` 和 `taskflow` 能力。

**差距：** 视频里把它描述成"技能总开关/协调器"，但实际它是一个严格的软件开发方法论。视频的描述有偏差。对凡哥的 AI 短剧工作流意义不大。

**对凡哥的价值：** 低。这是给软件工程师用的。

---

### 3. Self-Improved Agent（AI 自我进化智能大脑）

**视频描述：** 每次出错或被纠正后自动记录问题和正确方法，吃一堑长一智，越用越聪明

**官方数据：** ClawHub 有注册 (`self-improved-agent`)，页面 JS 渲染无法抓取

**小南现在：** ⚠️ 部分有。

- ✅ 我有 MEMORY.md 记录长期经验、纠错、偏好
- ✅ 我有 memory/YYYY-MM-DD.md 日常日志
- ❌ 但不是自动触发——需要凡哥纠正或我主动识别错误后才记录
- ❌ 没有结构化的"错误→纠正→验证"闭环

**差距：** 视频展示的是自动化自改进机制。我目前是"被动+主动手记"模式。

**对凡哥的价值：** 高。每次你说我哪里做错了，如果能自动消化成行为修正，长期下来体验会好很多。

---

### 4. Pro at Agent（AI 工作自主操盘手）

**视频描述：** 让 AI 从听命行事的被动模式，变成自己思考步骤、记录过程、优化方法的主动模式

**官方数据：** ClawHub 有注册 (`pro-at-agent`)，页面 JS 渲染无法抓取

**小南现在：** ⚠️ 部分有。

- ✅ AGENTS.md 已定义了主动心跳检查、自动沉淀记忆
- ✅ 有 `taskflow` 用于多步骤任务编排
- ✅ 有 `sessions_spawn` 可自主派生子代理
- ❌ 但触发条件还是依赖配置，不是真正的"自主思考要不要做"

**差距：** Pro at Agent 可能提供了一套结构化的自主规划框架。我需要看它的 SKILL.md 才能确认。

**对凡哥的价值：** 中高。如果我能更主动地在你没说话的时候干有用的事（比如提前检查素材、预生成提示词），效率会提升。

---

### 5. Playing with Files（复杂任务拆解小能手）

**视频描述：** 事情多文件杂的时候，把繁琐任务拆解成清晰步骤，按部就班推进

**官方数据：** ClawHub 有注册 (`playing-with-files`)，页面 JS 渲染无法抓取

**小南现在：** ⚠️ 部分有。

- ✅ 有 `taskflow` 用于多步骤任务管理
- ✅ 有文件读写能力（read/write/edit/exec）
- ❌ 但没有一个专门针对"文件处理任务分解"的技能

**差距：** 可能是把文件批处理操作（批量重命名、格式转换、归档整理）与任务分解结合起来的一个工具。

**对凡哥的价值：** 中等。凡哥经常需要管理大量素材文件（图片、音频、视频），如果有自动化批处理能力会很实用。

---

### 6. Brave Search（AI 专属联网搜索）

**视频描述：** 给 OpenClaw 装上联网功能，访问互联网，实时获取最新信息

**官方数据：** [ClawHub 已确认](https://clawhub.ai/steipete/brave-search) — 作者 steipete，下载 59k，⭐186

- 使用 Brave Search API，需要 `BRAVE_API_KEY`
- 基于 Node.js 脚本：`search.js` 和 `content.js`
- 支持搜索+内容提取（markdown）

**小南现在：** ⚠️ 有工具但 API Key 缺失。

- ✅ 有 `web_search` 工具接口
- ✅ 有 `web_fetch` 工具接口（URL 内容提取）
- ❌ `web_search` 需要 Brave API Key，**当前环境未配置，调用会报错**
- ❌ `web_fetch` 可用但某些 JS 渲染页面（如 ClawHub）抓不到内容

**差距：** Brave Search 技能提供了一套脚本化的搜索工具。OpenClaw 内置的 `web_search` 功能更原生，但需要 API Key 才能工作。

**解决方案：** 给 OpenClaw 配置 Brave API Key 即可激活 `web_search`。不需要额外安装 brave-search 技能。

**对凡哥的价值：** 高。激活搜索后我可以帮你查最新技术、教程、资讯。

---

### 7. Notebook LM（资料整理收纳大师）

**视频描述：** 梳理各类零散资料，搭建专属知识库，分类规整后查阅

**官方数据：** ClawHub 有注册 (`notebooklm`)，页面 JS 渲染无法抓取

**小南现在：** ⚠️ 部分有。

- ✅ 已为凡哥手动搭建了 `psychology-kb/`（心理学知识库）和 `director-kb/`（导演知识库）
- ✅ 有 `memory_search` 和 `memory_get` 用于知识检索
- ✅ 有 `web_fetch`+`pdf` 可摄入新资料
- ❌ 但知识库是手动搭建的，不是自动化流程
- ❌ 没有统一的"摄入→整理→索引→检索"工具链

**差距：** Notebook LM 技能可能提供了类似 Google NotebookLM 的知识库管理能力——自动整理、分类、索引。

**对凡哥的价值：** 高。凡哥经常让我学习和整理资料（心理学、导演、角色设计），有自动化知识库工具会大幅提升效率。

---

### 8. Aichrome Pro（网页操作自动化助手）

**视频描述：** 不用编写任何代码，让 AI 替你操作浏览器，自动完成各类网页操作

**官方数据：** ClawHub 有注册 (`aichrome-pro`)，页面 JS 渲染无法抓取。推测是基于 Chrome DevTools Protocol 的浏览器自动化技能。

**小南现在：** ✅ **已有且更强。**

- ✅ OpenClaw 内置了完整的 `browser` 工具（基于 Playwright）
- ✅ 支持页面导航、截图、元素操作、表单填写、JS 执行
- ✅ 附带 `browser-automation` 技能指导多步骤浏览器任务
- ✅ 支持 sandbox 和 host 两种模式

**差距：** Aichrome Pro 可能是一个更轻量/简化版的浏览器操控。OpenClaw 内置的 `browser` 工具功能更全。

**对凡哥的价值：** 已覆盖，无需额外安装。

---

### 9. Any Content Summarize（内容提炼快刀手）

**视频描述：** 网页/PDF/音频/视频都能快速提取核心重点

**官方数据：** OpenClaw 内置技能 `summarize`，依赖 CLI 工具 `summarize`（需 brew 安装），需要 API Key（OpenAI/Anthropic/Google/xAI）

**小南现在：** ⚠️ 部分有，但 CLI 工具未安装。

- ✅ 有 `web_fetch` 可提取网页文本内容
- ✅ 有 `pdf` 可分析 PDF
- ✅ 有 Whisper 可转录音频
- ✅ 我能用我的大模型能力做摘要
- ❌ `summarize` CLI 未安装在 WSL 中
- ❌ 不能直接处理 YouTube 视频链接

**差距：** `summarize` CLI 是一个专门优化的摘要工具，对 YouTube 等富媒体有特殊处理。我现在的做法是手动组合多个工具（下载→转录→分析），多了一步。

**对凡哥的价值：** 中。目前的工具组合基本够用，但 `summarize` CLI 会让流程更流畅。

---

### 10. Vision（图片处理 / AI 火眼金睛）

**视频描述：** 直接识别截图、表格、网页页面内容，不用手动打字输入

**官方数据：** [ClawHub 已确认](https://clawhub.ai/xueyetianya/vision) — 作者 xueyetianya，下载 4.5k，⭐1

⚠️ **重要发现：这个技能与视频描述有重大差异！**

ClawHub 上的 `vision` 是 **ImageMagick 图片处理工具**（resize/crop/convert/watermark），**不是 AI 视觉识别**！视频中的描述"AI 专属火眼金睛"应该是泛指 AI 看图能力，和 ClawHub 这个同名技能不完全对应。

**小南现在：** ✅ **已有且更强。**

- ✅ `image` 工具：AI 模型直接分析图片内容（物体识别、文字提取、场景理解）
- ✅ 支持多图同时分析
- ✅ 比 ImageMagick 的"图片格式转换"高级得多

**差距：** 如果是图片格式处理（resize/convert），我目前用 ffmpeg 可以替代。如果是 AI 视觉识别，我比 ClawHub 的 vision 技能强太多。

**对凡哥的价值：** 已覆盖。我的 `image` 工具可以直接分析首帧图、参考图、视频帧，不需要额外安装。

---

### 11. Table Search（AI 专用精准搜索器）

**视频描述：** 避开普通搜索的杂乱信息，返回结果干净又贴合需求

**官方数据：** ClawHub 有注册 (`table-search`)，页面 JS 渲染无法抓取

**小南现在：** ❌ 没有。

**差距：** 这可能是一个专门针对表格/结构化数据的搜索工具。具体实现未知（可能使用特定 API 或数据库查询）。

**对凡哥的价值：** 低到中。如果有表格数据查询需求（如角色对标表、档期表）可能有用，但目前工作流中不常见。

---

### 12. Weather（全球天气查询）

**视频描述：** 无需任何配置，想问哪里直接问，结果秒出

**官方数据：** [ClawHub 已确认](https://clawhub.ai/steipete/weather) — 作者 steipete，下载 160k，⭐408

- 基于 wttr.in（主）+ Open-Meteo（备）
- 无需 API Key
- 纯 curl 命令

**小南现在：** ✅ **完全覆盖，一模一样。**

- ✅ 已加载 `weather` 技能（OpenClaw 内置，内容与 ClawHub 版本一致）
- ✅ 同在 `<available_skills>` 列表中

**差距：** 零差距，同一个技能。

**对凡哥的价值：** 已覆盖。

---

### 13. Gog（Google 全家桶专属管家）

**视频描述：** 统一管理谷歌各类应用和服务，不用在不同工具间来回切换

**官方数据：** [ClawHub 已确认](https://clawhub.ai/steipete/gog) — 作者 steipete，下载 185k，⭐912

- 功能强大：Gmail 收发、Calendar 管理、Drive 搜索、Sheets 读写、Docs 导出
- 需要 OAuth 认证
- 已有内置 SKILL.md（~/.npm-global/lib/node_modules/openclaw/skills/gog/SKILL.md）

**小南现在：** ⚠️ 有技能文件，但 CLI 未安装。

- ✅ OpenClaw 已内置 `gog` 技能
- ❌ `gog` CLI 未安装在 WSL 中（需 `brew install steipete/tap/gogcli`）
- ❌ 即使安装了也需要 OAuth 配置才能用

**差距：** 技能定义已有，但可执行环境和认证都缺。

**对凡哥的价值：** 低。凡哥在国内用飞书为主，Google 生态使用场景很少。

---

### 14. Solo Co AI 终端（智能音箱隔空操控师）

**视频描述：** 不用打开 APP 不用敲命令行，直接用指令控制 Solo 音箱，还能一键传音乐

**官方数据：** ClawHub 有注册 (`solo-co-ai`)，页面 JS 渲染无法抓取

**小南现在：** ❌ 没有。

**差距：** 这是针对特定硬件（Solo 音箱）的 IoT 控制技能。完全不在我的能力范围。

**对凡哥的价值：** 低。除非凡哥家里有 Solo 音箱想用我控制。

---

### 15. Gitup（代码管理小白之友）

**视频描述：** 用自然语言管理代码，不用死记复杂命令

**官方数据：** ClawHub 有注册 (`gitup`)，页面 JS 渲染无法抓取。注意：与 OpenClaw 内置的 `github` 技能（使用 `gh` CLI）**不同**。

**小南现在：** ❌ 没有 Gitup。有 `github` 技能但 `gh` CLI 未安装。

- ✅ 有 `github` 技能文件（使用 `gh` CLI 操作 GitHub Issues/PRs/CI）
- ❌ `gh` CLI 未安装在 WSL
- ❌ `exec` 可以直接运行 `git` 命令操作本地仓库
- ⚠️ `gitup` 如果是一个"自然语言→git 命令"的翻译层，我没有

**差距：** Gitup 可能是把自然语言映射为 git 操作的封装。我现在可以直接用 `exec` 跑 git 命令，但需要我知道具体命令。

**对凡哥的价值：** 中。凡哥的 workspace 本身就是 Git 仓库（记忆同步），如果我能用自然语言帮你管理 git（提交、推送、回滚），会省心很多。

---

## 📊 综合评价

### 对凡哥最有价值、应该优先获取的技能：

| 优先级 | 技能 | 原因 |
|--------|------|------|
| 🔴 **P0** | Brave Search（配置 API Key） | 现有工具只需配 Key 就能激活，解锁联网搜索能力 |
| 🟡 **P1** | Notebook LM / 知识库能力 | 凡哥经常需要我学习整理资料，自动化知识库工具直接提效 |
| 🟡 **P1** | Self-Improved Agent | 让犯错记录→行为修正更自动化，长期体验提升 |
| 🟢 **P2** | Find Skills / Spy Skill | 我能自己搜技能市场推荐给你 |
| 🟢 **P2** | Playing with Files | 素材批量管理自动化 |
| ⚪ **P3** | Summarize CLI | 锦上添花，现有工具已基本够用 |
| ⚪ **P3** | Gitup | 自然语言 Git 操作，对记忆同步有帮助 |

### 已有且够用的：
- ✅ 浏览器操控（browser 工具 > Aichrome Pro）
- ✅ AI 图片分析（image 工具 > ClawHub Vision）
- ✅ 天气查询（weather 技能，完全一致）
- ✅ 文件读写（read/write/edit/exec）

### 与凡哥场景无关的：
- ❌ Gog（Google 全家桶，凡哥用飞书）
- ❌ Solo Co AI（智能音箱控制）
- ❌ Superpowers（软件工程工作流）
- ❌ Table Search（当前无明确需求）

---

## ⚠️ 一个重要的认识纠正

视频中有些技能的实际功能与视频描述**不完全一致**：

1. **Superpowers** ≠ "技能联动总指挥"，实际是 TDD+Subagent 开发流水线
2. **Vision（ClawHub版）** ≠ "AI 火眼金睛"，实际是 ImageMagick 图片格式处理
3. "15个必装 Skills" 中有 4 个（weather, gog, github, summarize）**已经是 OpenClaw 内置技能**，不需要额外安装

视频是一个很好的介绍，但它更偏向"吸引眼球的内容创作"而非精确的技术文档。
