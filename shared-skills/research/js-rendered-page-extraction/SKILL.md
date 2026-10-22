---
name: js-rendered-page-extraction
description: "Use when JS渲染/SPA页抓不到正文、要对标分析页面结构时。结构+文案+视觉三份合抓。"
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows]
metadata:
  hermes:
    tags: [scraping, spa, browser, 对标分析, vision]
    related_skills: [local-web-capabilities, agent-browser, website-cloning]
---

# JS 渲染页（SPA）抓取 · 结构 + 文案 + 视觉三份合抓

**解决的问题**：静态抽取器抓 JS 渲染的页面，正文是空的（只回来页脚/备案链接），于是"抓不到"——其实不是抓不到，是**用错了工具层级**，而且**只抓文本也永远不够**。

**中文触发**：SPA 抓取、页面抓不到正文、空白页、对标页面、竞品页面分析、复刻前摸结构、JS 渲染、动态加载页、要看页面长什么样。

---

## When to Use

- 凡哥给了个**对标/竞品/参考页**，要摸清它的模块和布局（做需求分析、复刻、或产品设计参考）
- `web_extract` 抓回来**只有页脚链接 / 备案号 / 协议**（典型 SPA 症状）
- `browser_exec` / 预览窗不响应，但页面必须看
- 需要回答**布局类问题**（几列、横排竖排、有没有弹幕/评论区、首屏怎么分栏）

**Don't use for**：SSR/静态页（`web_extract` 一遍就够）；已配置的官方 API；纯下载（走 `aria2-downloads`）。

---

## 阶梯（按序试，出了结果就停）

| # | 手段 | 什么时候够 |
|---|---|---|
| 1 | `web_extract` | SSR / 静态页 |
| 2 | ⭐ **直取前端包**——`curl` 站点 `/assets/index-*.js` + 正则抽 `path:"…"` 与中文文案串 | **免浏览器、最快**；只想知道「全站有哪些页面 / 功能词」时这一层就够（2026-10-13 实测：**15 条路由 + 236 条中文文案**一次到手） |
| 3 | 强制渲染类抓取（如 wigolo `fetch --force-refresh --mode=stealth`） | 文档化的 force-render 路径，见 `local-web-capabilities`。**本轮未验证**，按需试 |
| 4 | `browser_exec` | 能用时最省事（截图自动进视野）；daemon 起不来就下一步 |
| 5 | ⭐ **`agent-browser` CLI** | **本类任务最可靠的一层**（真浏览器 + 无障碍树快照） |
| 6 | **Playwright 直连**（本机已装 `playwright` python） | 要**逐路由真渲染**取正文/截图、而 4/5 两层当下不可用时：`chromium.launch()` → 逐路由 `goto(..., wait_until="networkidle")` + `inner_text("body")` + `full_page` 截图（2026-10-13 实测一把跑通 13 个路由，全程不需交互） |
| 7 | **截图 → `vision_analyze`** | **布局类问题非它不可**，见下 |

第 2 层与第 6 层的**可复制代码**（15 路由抽法、登录墙识别、凡哥给的存档 HTML 抽正文）：
`project-topology-diagrams` → `references/站点取全量-路由与文案抽取.md`。

⚠️ `open_preview` / `read_preview` / `drive_preview` 对重 SPA **可能超时无响应** —— 试一次不成就走阶梯 4，**别在预览窗上耗轮次**。

---

## agent-browser 一页抓全（2026-10-13 实测走通）

**先拿 BIN**（目录名带哈希）：

```bash
ls -d D:/Hermes/hermes-agent/node_modules/.agent-browser-*/
# → D:/Hermes/hermes-agent/node_modules/.agent-browser-xbGs7Fy5/
BIN="D:/Hermes/hermes-agent/node_modules/.agent-browser-xbGs7Fy5/bin/agent-browser.js"
node "$BIN" --version
```

⚠️ **BIN 路径坑（实测）**：`ls -d "<前缀>".agent-browser-*/bin/agent-browser.js | head -1` 这种"引号 + glob 拼一行"的取法，glob **不展开**，变量里进了**字面 `*`** → node 报
`Cannot find module '...\node_modules\.agent-browser-xbGs7Fy5\bin\agent-browser.js*'`。
**正确姿势：先 `ls -d` 列出哈希目录，再 `BIN="<真实路径>"`。**

**三份一起抓**（PTY 后台跑，用 `process(action='poll'/'wait')` 读结果 —— agent-browser 要求真 tty，不能管道）：

```bash
node "$BIN" open "https://目标页"
node "$BIN" snapshot -i -c                                    # ① 结构
node "$BIN" screenshot --full "D:/Hermes/cache/fun/full.png"   # ③ 视觉（全页）
node "$BIN" eval "document.body.innerText.substring(0,2500)"   # ② 文案
node "$BIN" close --all
```

---

## ⭐ 为什么必须"三份合起来"

只抓一份一定漏：

| 来源 | 给什么 | 给不了 |
|---|---|---|
| `snapshot -i -c` | 模块边界、卡片、可交互元素、链接文案、每部剧的标题+简介 | **视觉排布、栏数、有没有弹幕/评论** |
| `eval innerText` | 全量文案（剧名、标签、筛选词、简介） | **哪些是并排、哪些是上下** |
| `screenshot` + `vision_analyze` | **布局真相**：几列、横排/竖排、Hero 区分栏、角标位置、右下角按钮 | 精确文案、alt/链接 |

**2026-10-13 实证**：快照+文本都**看不到"人气排行"是横排大卡片**，是**看截图**才确认的 —— 布局问题必须以截图为权威。

**vision 提问要具体**（泛泛问"描述这个页面"会得到废话）：
> "从上到下描述视觉布局：首屏大图怎么呈现、模块有哪些、每个模块里卡片是几列/横排还是竖排、有没有评论区或弹幕、顶部和底部各有什么。"

---

## Common Pitfalls

1. **拿静态抽取的结果下结论** → 只回来页脚就等于什么都没抓到，别把它当"页面内容"写进分析。
2. **BIN 用"引号+glob 一行流"** → 字面 `*` 进变量 → `Cannot find module`。见上。
3. **忘了 PTY** → `stdin is not a tty`，exit 1。必须 `terminal(background=true, pty=true)`。
4. **输出管道给 head/grep** → `stdout is not a tty` 失败。整段跑完从 process log 读。
5. **在预览窗上死磕** → 重 SPA 的 `read_preview`/`drive_preview` 会超时，一次不成就换阶梯 4。
6. **只抓文本就写对标结论** → 布局类结论必须回头看截图。
7. **收工不 close** → 留 daemon 和 Chrome 进程，记得 `close --all`。
8. **页面一变还用旧 ref** → `@eN` 每次快照重分配，操作前重新 `snapshot`。
9. **只抓首页就下结论** → SPA 首页常常只是营销页。**先抽路由表**（阶梯第 2 层），再逐路由抓；同一段文字在多个路由重复出现＝**登录墙**（2026-10-13 实测：`/workbench` `/wallet` `/onboarding` 渲染出的都是同一个登录页）。
10. **把前端包里抓到的中文串直接当页面结构** → ⚠ **枚举级**（含格式模板、时间单位、报错提示），只能当**功能词表**，要按路由分组后才写成结构。
11. **抓一次就下结论** → 重 SPA 的**同一次访问渲染结果都不一样**（登录态/风控/网络波动）。2026-10-15 抖音实测：同一 URL 连抓三次的可见正文分别是 **4579 / 3249 / 1637 / 1115 字符**。
    **判据：字符数 < 2000 基本就是空壳**（只出了页脚）→ 别当成"这页没内容"。抓取脚本应**重试 3 次、取最丰富的一次**。
12. **URL 形式决定渲染** → 同一个内容的**分享链接形式**可能渲染不出主体。2026-10-15 抖音实测（各 3 次）：`/user/self?...&modal_id=<id>`（个人主页弹窗形式）**三次都只有 ~1.1K 字符**；换成 `/video/<id>` **第一次就 3.1K**（主体文案 + 评论区全出）。
    → **收到分享链接先规范化**（把 `modal_id=` 的值抽出来拼成规范路径），能省一整轮。

> 抖音（SPA + 音视频分离流）的完整实测取证 —— URL 形式对照、字符数、长视频"没有音频轨"、口播拿不到时的兜底：
> `references/douyin-spa-and-media-streams-2026-10.md`

---

13. **在 `page.evaluate()` 的 JS 里做字符串分割/正则** → Python 三引号与 JS 转义互相打坏，报 `SyntaxError: Invalid or unexpected token`（2026-10-21 连踩两次：`body.split('\\n')`、含 `\\s` 的正则全炸，各浪费一轮）。
    ✅ **正确姿势：`text = page.inner_text("body")` 把正文拿回 Python，切分和正则全部用 Python 做**；JS 里只留最简取值（`el.innerText`、`el.getAttribute('data-sku')`）。
    → 这正是上面「阶梯第 6 层」的写法：`goto(...)` + `inner_text("body")`，本来就不该在 JS 里解析文本。

14. **用 `terminal(background=true)` 起的 Chrome 会被主脚本连带杀死** → 脚本一中断（超时 / Ctrl+C），浏览器和登录态一起完蛋，得重新扫码登录（2026-10-21 一个任务里死了三次）。
    ✅ 用 PowerShell 真正分离进程：
    ```bash
    powershell -NoProfile -Command "Start-Process '<chrome.exe 路径>' -ArgumentList '--remote-debugging-port=9222','--remote-allow-origins=*','--user-data-dir=<独立目录>','<URL>'"
    ```
    - **`--remote-allow-origins=*` 必需**，否则 CDP 连 WebSocket 报 **403**
    - 登录态靠独立 `--user-data-dir` 持久化，进程重启后**不用重新扫码**（实测有效）
    - 探活：`curl -s -m 5 http://localhost:9222/json/version`；连接被拒（exit 7）＝已死
    - ⚠️ `cmd //c start "" "..."` 在 git-bash 下会掉进交互式 cmd，**不可靠**，用上面的 powershell 版

## Verification Checklist

- [ ] 正文**不是**只有页脚/备案链接（否则说明抓的是空壳）
- [ ] BIN 路径是 **`ls -d` 看来的真实路径**，不是拼出来的 glob
- [ ] 命令在 PTY 下跑、输出**没管道**
- [ ] 结构 / 文案 / 截图**三份都拿到**了
- [ ] 凡哥问布局时，**结论出自截图**而不是快照
- [ ] 收工 `close --all`

---

## 沉淀去向

抓完别只停在聊天里：结构 + 文案 + 视觉三份合起来写成**需求底稿/对标分析文件**（凡哥的产出习惯：先落盘再谈），再据此出思维导图或复刻清单。

**真实案例记录**：`references/fun-tv-cartoon-2026-10-13.md`（风行漫剧频道页 · 完整命令与观察）
