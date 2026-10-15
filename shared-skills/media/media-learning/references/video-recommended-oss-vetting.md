# 视频里推荐的开源项目：定位 + 核证 + 判断（案例库）

配套 `media-learning` SKILL.md「外部工具/平台类链接」章节。
2026-10-15 一晚三连：凡哥连发三条抖音，问「**看看这个博主说的项目，是不是我们需要的？**」
「**分析学习这个视频的开源项目，看看对我们是否有帮助？**」「**帮我部署下一个视频的项目，这个项目对我挺重要的**」。

⚠️ 这是**固定作业**，不是一次性任务。DASHBOARD 里的同类记录：2026-10-11 Browser-Use、
2026-10-11 book-to-skill（抖音「书籍转Skill」教程）。

## 一、三条的处置结果

| # | modal_id | 项目 | 官方数据 | 结论 |
|---|---|---|---|---|
| 1 | 7688037823143873842 | `CursorTouch/Windows-MCP` | ★8,933 / MIT / v0.8.8 / Python≥3.14 / 2026-10-14 push | **不用** |
| 2 | 7696049324175010531 | `hmjz100/LinkSwift` | ★22,098 / 1,319 fork / AGPL-3.0 / 油猴脚本 | 凡哥说"挺重要" → **待部署** |
| 3 | 7684620636584430874 | `ThreeFrontTeeth/mengya-knowledge`（萌芽知识库） | ★42 / 2 fork / **7 commits** / **无许可证** | **不用** |

**1 · Windows-MCP**：与 Hermes 内建 `computer_use`（cua-driver，后台不抢焦点）重叠约 **80%**；
README 自曝「系统默认语言非英文时 App-Tool 会出问题需禁用」——**中文 Windows 正好踩**；带 posthog 遥测。
可借鉴（思路非代码）：`WaitFor`（一次调用内轮询等元素/窗口，本机只有固定 `wait`）、
`Screenshot region=[左,上,右,下]`（按矩形截图省 token）。
防仿冒：搜 "windows-mcp" 命中至少 4 个同名搬运（Macco2024、13888285815、iflow-mcp/aidotnet、dividden）。

**2 · LinkSwift**：类型 = **Tampermonkey 油猴脚本**（`.user.js`），不是独立软件 → "部署" = 装篡改猴扩展 + 装脚本。
九大网盘直链 + 推送 Aria2/IDM/Motrix/比特彗星/ABDM/cURL。装**走脚本猫国内源**（GitHub raw 墙内常不通）。
安全提醒：脚本要读网盘页面数据（含 AccessToken/Cookie）→ **只从官方源装**。
⚠️ 视频真卖点其实是"**让豆包/Agent 帮你部署**"，脚本本身是 2022 年的老项目。

**3 · 萌芽知识库**：**纯 markdown 模板 + 一份 AI 规则文档，不含任何代码**。
八层：`00-灵感库 / 01-进行中 / 02-成品库 / 03-外部资源 / 04-历史记录 / 05-Skills / 06-Wiki`。
判断为"不用"的依据：凡哥已有 **198 个 SKILL.md**、`closed-source-ai-kb`/`director-kb`/`image-kb` 多个知识库、
`D:\Hermes\xiaonan-memory\AGENTS.md`、`dashboard-tree.html`（可视化）——**每一层都被覆盖且更强**。
唯一真值得借的一层：**`00-灵感库`（随手记、先不整理）**，凡哥确实没有这个落脚点。
（它那份 17.8KB《知识库工作流.md》写得挺严谨 —— "下载成功 ≠ 整理完成"、"有网址不等于有证据"，
但**凡哥的 SOUL.md 已有等价条款**，所以不是缺，是两边走在同一方向上。）

## 二、本次真正省时间的定位技巧

### 1. B站同名原版 = 项目名的金矿 ⭐
抖音页面**没有任何仓库地址**，HTML 正则也挖不到（命中全是推荐流）→ 搜视频标题 →
命中 B站同博主同名视频（BV1wAYS6cEWu，2026-09-12，6841 播放）→ 简介原话：
> "我也把这套「**萌芽知识库**」开源到了 GitHub，相关提示词和操作文档都会一起提供。"

一步锁定。**没有这一步就卡死在"视频没说仓库"上。**

### 2. 博主昵称直译成仓库 owner
"三颗门牙" → `ThreeFrontTeeth`。**owner 对得上 = 双重确认不是仿冒。**

### 3. 中文项目名原样搜最有效
`萌芽知识库` → 一次命中（41 条里第 6 条）；
`萌芽 obsidian` → 0；`mengya knowledge` → 1；`sprout knowledge base obsidian` → 0。

### 4. GitHub 核证两条路
- `api.github.com/search/repositories?q=...` —— 快；**未认证 60 次/小时**，连发几组就 `HTTP 403: rate limit exceeded`
- 限流后 → `web_extract` 拉 `https://github.com/<owner>/<repo>` —— **无配额**，拿到完整 README 渲染正文 + 文件树 + star/fork（本次靠它拿全）
- 单仓体检脚本：`D:\Hermes\cache\gh_check.py <owner/repo>`（同样走 api.github.com，同样受配额限制）

## 三、抖音取流的两个当前边界（如实报，别硬圆）

1. **长视频（10min+）音视频分轨**：13:11 的视频下载成功 35MB，但 ffmpeg 报
   `Output file does not contain any stream`；`ffmpeg -i` 看流只有 `Stream #0:0 Video`，**没有 Audio**。
   短视频（<1min）抖音返回合并流所以一直没暴露。**此坑未解决**（需分别捕获 audio 轨再合并）。
2. **页面自带「章节要点」可兜底**：抖音长视频页有 8 段带时间戳的小节说明 + AI 摘要，
   全落在抓页 txt 里。**长视频先用它拿骨架**，不依赖转写 —— 本次 13:11 那条全靠它完成判断。
