# Hermes 桌面版「链接标题抓取」——弹窗元凶取证记录（2026-10-11）

## 现象
凡哥屏幕上**自动**弹出两类窗（无任何点击，他本人确认两次都不是他点的）：
1. Chromium 风格「另存为」框 —— **标题栏显示的是 URL**（不是文件名），默认存到 `D:\下载`
2. Windows「获取打开此 '<协议名>' 链接的应用」—— 提示本机没有可处理该协议的程序

两次间隔约 7 分钟，第二次弹窗背景里正好是我上一条回复。

## 排查过程（排除法，按顺序）
| 怀疑对象 | 查法 | 结果 |
|---|---|---|
| 我跑的命令本身 | 受控复现：同款 curl 下载同 URL | ❌ 零弹窗 |
| Chrome 的下载器 | 读 `Chrome\User Data\Default\History` 的 `downloads` 表 | ❌ 无该记录 |
| 迅雷类接管下载 | 进程表 + 安装目录 + `D:\下载\.accelerate` | ❌ 都空 |
| Chrome 扩展 | 读 `Default\Preferences` 的 `extensions.settings` | ❌ 扩展数 = 0 |
| Hermes 日志 | 搜 `desktop.log` / `gui.log` / `agent.log` | ❌ 无相关记录 |
| **进程监控（命中）** | 后台脚本记录**新进程 + 父进程链** | ✅ 抓到 `curl.exe` 的 **parent = Hermes.exe** |

> **可复用手法**：轮询 `Win32_Process` 记录新进程与 `ParentProcessId`，
> 是定位"哪个程序背着我干了事"的通用办法（脚本见文末）。日志查不到 ≠ 没发生。

## 根因（源码为准）
`D:\Hermes\hermes-agent\apps\desktop\dist\electron-main.mjs` 第 **24544–24710** 行：

```js
var TITLE_BYTE_BUDGET = 96 * 1024;
var TITLE_TIMEOUT_MS = 5e3;
var TITLE_MAX_REDIRECTS = 3;
var TITLE_USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_6_0) ... Chrome/136.0.0.0";

function fetchHtmlTitleWithCurl(rawUrl)   // ① 跑 curl 抓 <title>（伪装 Mac 版 Chrome）
function runRenderTitleJob(rawUrl)        // ② 开一个真 BrowserWindow 加载该 URL
  → createLinkTitleWindow(BrowserWindow2, session.fromPartition("hermes:link-titles"))
```

渲染层守卫（`apps/desktop/src/lib/external-link.tsx`）：
```js
const SKIP_PROTO_RE = /^(?:file|data|mailto|javascript|blob|chrome|about|hermes):/i
export function isTitleFetchable(value) { /* 只放行 http/https */ }
```
→ **"预览"这条路只走 http(s)**；自定义协议那类弹窗来自另一条路径 ——
`openLink()` 对非 http(s) 直接交给 OS（`shell.openExternal`）。

## 后果链
- 加载**下载型** URL（`Content-Disposition: attachment`）→ Electron 判定为下载 → **弹「另存为」**
- 加载**自定义协议** → Windows 找不到处理器 → **弹「获取打开此链接的应用」**
- 实测触发源样本：① 我在终端里跑过的 GitHub release 下载链接；② **我 `read_file` 读过的文件内容里的 URL**
  → 说明扫描范围**不止聊天消息，文件内容/工具输出同样会被送去加载**（这条最容易被低估）
- **对照实验**：终端里 `echo` 一个 URL → 不会被抓

## 已确认：没有开关
- Hermes `Preferences` / `config.yaml` 里**无**相关项
- 源码里搜 `DISABLE_LINK|LINK_TITLE|LINK_PREVIEW|env.*LINK` → **0 命中**
- 结论：**写死的产品行为**，只能改本体或提 issue

## 缓解（凡哥 2026-10-11 决定：先不动本体，"也没什么影响"）
- **我方行为规避（已在执行）**：聊天消息/终端输出**不产生可被加载的链接** ——
  URL 反链接化（`ghproxy[.]net`）、**协议名别写"名字+双斜杠"的完整形式**、命令静默、只报「路径+字节数」
- **未采纳但可行**（日后要根治时用，须凡哥点头 —— 动的是 Hermes 本体、**升级会被覆盖**）：
  1. 改 `getLinkTitleSession()` 的 `onBeforeRequest` → `callback({ cancel: true })` 全取消
  2. 在 `openExternal` 的 IPC 入口加协议白名单（只放 http/https）
  3. 给 Nous Research 提 issue（本次复现链完整，证据充足）

## 附：进程级取证脚本（PowerShell，通用）
```powershell
$log = 'D:\Hermes\logs\popup_watch.log'
$prevWin = ''
$knownProc = @{}
Get-CimInstance Win32_Process | ForEach-Object { $knownProc[[int]$_.ProcessId] = $_.Name }
while ($true) {
  $cur = (Get-Process | Where-Object { $_.MainWindowTitle } |
          ForEach-Object { "$($_.Id):$($_.ProcessName):$($_.MainWindowTitle)" } |
          Sort-Object) -join ' | '
  if ($cur -ne $prevWin) {
    "$(Get-Date -Format 'HH:mm:ss.fff') [WINDOWS] $cur" | Out-File $log -Append -Encoding utf8
    $prevWin = $cur
  }
  foreach ($p in (Get-CimInstance Win32_Process)) {
    $id = [int]$p.ProcessId
    if (-not $knownProc.ContainsKey($id)) {
      $knownProc[$id] = $p.Name
      $par = (Get-CimInstance Win32_Process -Filter "ProcessId=$($p.ParentProcessId)" -ErrorAction SilentlyContinue).Name
      "$(Get-Date -Format 'HH:mm:ss.fff') [NEWPROC] $($p.Name) pid=$id parent=$($p.ParentProcessId)($par)" | Out-File $log -Append -Encoding utf8
    }
  }
  Start-Sleep -Milliseconds 500
}
```
> `MainWindowTitle` 抓不到模态子对话框 —— 所以真正命中的是**"新进程 + 父进程"那条线**
> （本次正是 `curl.exe ← parent=Hermes.exe` 暴露了真相）。
