---
name: agent-browser
description: "Use when 抓网页/爬取/填表单/截图/浏览器自动化/browser-use时。"
version: 1.0.0
author: 小南
license: MIT
metadata:
  hermes:
    tags: [browser, automation, cdp, scraping, cli]
    related_skills: [local-web-capabilities, computer-use]
---

# agent-browser（浏览器自动化 CLI）

## Overview

`agent-browser` 是 **vercel-labs** 出的 Rust 浏览器自动化 CLI（Apache-2.0），**已经内置在 Hermes 里**（`hermes-agent/node_modules/.agent-browser-*`），不需要另外安装。

它通过 **CDP** 驱动真实 Chrome/Chromium，用**无障碍树快照 + `@eN` 元素引用**代替解析 HTML —— 一次快照 200~400 token，比读原始 DOM 省一个数量级。

**中文触发**（凡哥这么说时加载我）：抓网页、爬取、爬虫、抓数据、填表单、点击按钮、网页截图、登录网站、抓不到内容、页面空白、browser-use、浏览器自动化、反爬、403、SPA 空白。

用途：抓网页、填表单、点击、截图、登录、爬数据、测 Web 应用、自动化 Electron 应用。

官方技能内容随版本更新、永不过期：

```bash
agent-browser skills get core --full   # 完整命令参考（官方权威）
agent-browser skills list              # core / electron / slack / dogfood / vercel-sandbox / agentcore
```

## When to Use

- 凡哥要抓某个网页、公开数据、填表单、点按钮、截图
- **`browser_exec` 挂了**（如 `DevToolsActivePort not found`）→ 直接用这个顶上
- 遇到 403 / Cloudflare / 反爬 / SPA 空白页 / 需要登录态的页面
- 需要"像人一样"操作浏览器（点击、登录、翻页、上传）
- 需要复用浏览器里已有的登录态（`--profile`）

**Don't use for**：已配置好的官方 API（更快更稳，先试 API）；纯静态页面（`curl` 就够）；桌面原生应用窗口（用 `computer-use`）。

## 硬规则（实测，违反必失败）

### 1. 必须用 PTY

agent-browser 拒绝在非交互 shell 里执行：

```
stdin is not a tty        ← 直接 exit 1，什么都不做
```

**所以必须用 `terminal(background=true, pty=true)` 跑，再用 `process(action='poll'/'log')` 读结果。**

前台跑、后台不带 pty —— **100% 失败**，不管命令多简单。翻遍 `--help` 没有绕过的开关（官方就是要求真终端）。

### 2. 不能管道

```bash
agent-browser snapshot -i | head -30     ← "stdout is not a tty"，失败
```

`stdout` 也必须指向 tty。**要截断就整段跑完，从 process log 里读**，不要 `| head` / `| grep` / `> file`。

### 3. 浏览器常驻，别每条重开

daemon 保持会话，链式调用是常态：

```bash
agent-browser open example.com && agent-browser snapshot -i
```

收工用 `agent-browser close --all`。

## 本机调用

PATH 里没有，用包内 bin（**目录名带哈希、随版本变 → 必须 glob 获取，不要硬编码**）：

```bash
BIN=$(ls -d "D:/Hermes/hermes-agent/node_modules/".agent-browser-*/bin/agent-browser.js 2>/dev/null | head -1)
# 实测样例：D:/Hermes/hermes-agent/node_modules/.agent-browser-xbGs7Fy5/bin/agent-browser.js
node "$BIN" --version      # → agent-browser 0.26.0
```

标准骨架（PTY 后台 → poll）：

```bash
export BIN="<glob 拿到的路径>"
node "$BIN" open "https://目标网站"
node "$BIN" get title
node "$BIN" snapshot -i
node "$BIN" close --all
```

## 核心循环

```bash
agent-browser open <url>     # 1. 打开
agent-browser snapshot -i    # 2. 看有什么（只要可交互元素）
agent-browser click @e3      # 3. 按 ref 操作
agent-browser snapshot -i    # 4. 页面一变就重新快照
```

`@eN` 引用**每次快照重新分配**。页面一变（点击跳转、提交表单、动态渲染、弹窗），旧 ref **立即失效** → 操作前重新快照。

## 常用命令速查

**读页面**

```bash
snapshot -i              # 可交互元素（首选）
snapshot -i -u           # 带链接 URL
snapshot -i -c           # 紧凑（去掉空结构节点）
snapshot -i -d 3         # 限制深度
snapshot -i --json       # 机器可读
snapshot -s "#main"      # 限定 CSS 选择器
get text @e1 / get html @e1 / get attr @e1 href / get value @e1
get title / get url / get count ".item"
```

**操作**

```bash
click @e1 | click @e1 --new-tab | dblclick @e1 | hover @e1 | focus @e1
fill @e2 "text"          # 先清空再输入
type @e2 "text"          # 追加输入，不清空
press Enter | press Control+a
check @e3 | uncheck @e3 | select @e4 "value" | upload @e5 file.pdf
scroll down 500 | scrollintoview @e1 | drag @e1 @e2
```

**refs 不灵时的语义定位**（不需要先快照）

```bash
find role button click --name "Submit"
find text "Sign In" click [--exact]
find label "Email" fill "user@test.com"
find placeholder "Search" type "query"
find testid "submit-btn" click
find first ".card" click | find nth 2 ".card" hover
```

优先级：**快照 + `@eN`（最快最稳） > `find role/text/label`（次之，免快照） > 原生 CSS（兜底）**。

**截图**

```bash
screenshot                  # 临时路径，stdout 打印
screenshot page.png
screenshot --full full.png  # 全页滚动高度
screenshot --annotate map.png   # 带编号标签，N 对应快照 ref @eN
```

**多标签页**

```bash
tab                      # 列标签（稳定 tabId）
tab new https://...      # 新开并切过去
tab 2 | tab close 2
```

**并行会话**（各自独立 cookie/tab/refs）

```bash
agent-browser --session a open https://...
agent-browser --session b open https://...
```

**网络**

```bash
network requests                          # 看发过什么请求
network route "**/analytics" --abort      # 拦截
network route "**/api/users" --body '{"users":[]}'   # 打桩
network har start / har stop /tmp/trace.har
```

## 等待（最容易翻车的地方）

读这段：**agent 失败多半不是因为选择器差，而是因为等错了。**

```bash
wait @e1                              # 等元素出现
wait --text "Success"                 # 等文本出现
wait --url "**/dashboard"             # 等 URL 匹配（glob）
wait --load networkidle               # 等网络空闲（SPA 导航兜底）
wait --load domcontentloaded
wait --fn "window.myApp.ready === true"   # 等 JS 条件
wait 2000                             # 死等毫秒 —— 下策，只在调试时用
```

页面变化后**四选一**：等具体元素 / 等文本 / 等 URL / 等网络空闲。默认超时 25 秒。

## 全局 flag（有用的）

```bash
--session <name>        # 隔离会话
--json                  # JSON 输出
--headed                # 显示窗口（headless 被检测时改用）
--auto-connect          # 自动发现正在运行的 Chrome
--cdp <port>            # 连指定 CDP 端口
--profile Default       # ★ 复用 Chrome 登录态
--profile ~/.myapp      # 持久化自定义 profile
--state <path>          # 加载保存的登录状态
--session-name <name>   # 按名自动保存/恢复会话
--headers <json>        # 仅对该 origin 生效的请求头
--proxy <url>           # 代理
```

**抓需要登录的站**（抖音/小红书/飞书等）：

```bash
agent-browser --profile Default open "https://..."
agent-browser profiles          # 先看有哪些 profile
```

## 自检：doctor

任何异常**先跑它**（环境 / Chrome / daemon / 配置 / provider / 网络 / 启动测试全覆盖）：

```bash
agent-browser doctor                     # 全量诊断
agent-browser doctor --offline --quick   # 快，纯本地
agent-browser doctor --fix               # 附带破坏性修复
agent-browser doctor --json              # 结构化输出
```

本机实测基线：**`4 pass, 0 warn, 0 fail`**。退出码 0 = 全过，1 = 有 fail。

## 与 browser_exec 的分工

| | `browser_exec`（Hermes 内置封装） | `agent-browser` CLI |
|---|---|---|
| 截图进我视野 | ✅ 自动附加到上下文 | 需手动 `vision_analyze` |
| 命令行灵活度 | 中（helper 函数） | 高（完整 CLI + `&&` 链式） |
| 故障自检 | ❌ | ✅ `doctor --fix` |
| 复用登录态 | 取决于配置 | ✅ `--profile` 直接复用 Chrome |
| 会话隔离 | session 参数 | `--session` / `--session-name` |

**规则**：两个都能用时**优先 `browser_exec`**（截图自动进视野，省一轮）；它挂掉、或需要登录态/复杂链式操作时**用 `agent-browser`**。2026-10-11 实测：`browser_exec` 的 daemon 挂了（`DevToolsActivePort not found`），正是靠 agent-browser 顶上的。

## Common Pitfalls

1. **非 PTY 执行** → `stdin is not a tty`，exit 1。必须 `pty=true`。
2. **管道截断输出** → `stdout is not a tty`。整段跑完从 log 读。
3. **用过期 ref** → 页面一变必须重新 `snapshot -i`。
4. **元素在 DOM 里但快照没有** → 多半在屏幕外：`scroll down 1000` 或 `wait --text "..."` 后再快照。
5. **点击没反应** → 弹窗 / Cookie 横幅挡住：先快照找到关闭按钮点掉，再重新快照。
6. **fill/type 无效** → 自定义组件拦截按键：`focus @e1` 后试 `keyboard inserttext "text"`（绕过按键事件）或 `keyboard type "text"`。
7. **复杂 JS 引号地狱** → 用 `eval --stdin` heredoc（`cat <<'EOF' | agent-browser eval --stdin`）或 `eval -b <base64>`，别用内联。
8. **硬编码 bin 路径** → 目录名带哈希会随版本变，必须 glob 查找。
9. **headless 拿不到内容**（如抖音正文）→ 该站要登录态：加 `--profile Default` 或 `--headed`。
10. **没收工** → 留下 daemon 和一堆 Chrome 进程。养成 `close --all`。
11. **跨域 iframe 快照为空** → 跨域 iframe 会被静默跳过；`frame @e3` 显式切进去，或退回 `eval`。

## Verification Checklist

- [ ] 命令在 **PTY** 下跑（`pty=true`）
- [ ] 输出**没有**管道给 head/grep/tail，也没重定向
- [ ] 每条关键命令都看了 exit code（`echo "exit=$?"`）
- [ ] 页面变化后重新快照，没用过期 ref
- [ ] 收工前 `close --all`
- [ ] 出现异常先跑过 `doctor`

## One-Shot 食谱

**抓一个不用登录的页面**

```bash
export BIN="$(ls -d D:/Hermes/hermes-agent/node_modules/.agent-browser-*/bin/agent-browser.js | head -1)"
node "$BIN" open "https://目标" && node "$BIN" get title
node "$BIN" snapshot -i
node "$BIN" close --all
```

**抓需要登录态的页面（如抖音）**

```bash
node "$BIN" --profile Default open "https://www.douyin.com/video/<id>"
node "$BIN" get title
node "$BIN" snapshot -i
node "$BIN" close --all
```

**取整页文本做分析**：`get text @eN` 取正文块最稳；需要全文时用 `eval --stdin` 走 `document.body.innerText`。

**跑不通时的排查顺序**：`doctor --offline --quick` → 检查是否 PTY → 检查是否管道 → 换 `--headed` → 加 `--profile`。
