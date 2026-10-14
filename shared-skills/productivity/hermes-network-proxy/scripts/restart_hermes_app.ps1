# 彻底重启 Hermes 桌面版（绕过托盘 / 单实例锁）
#
# 用途：改了 venv/Lib/site-packages/** 或任何「import 期加载」的文件后，
#       桌面 App 里的后端进程仍持有旧模块 —— 必须真重启才生效。
#       而点窗口 X 只是收进托盘，进程不退出；再点图标又把老实例唤回来。
#
# 用法（推荐后台延时执行，先给 Agent 把话说说完）：
#   powershell -NoProfile -Command "Start-Process powershell -ArgumentList @('-NoProfile','-ExecutionPolicy','Bypass','-File','D:\Hermes\scripts\restart_hermes_app.ps1','-DelaySeconds','90') -WindowStyle Hidden"
#
# 刹车：提前创建 D:\Hermes\logs\restart_cancel.flag → 脚本放弃，一个进程都不杀。
# 日志：D:\Hermes\logs\restart_app.log（含重启前后进程 CreationDate，可核对是否真的重启）
#
# ⚠️ 会杀掉宿主进程 → 当前窗口自己关掉再开，并打断其它会话正在跑的轮次。
#    替用户执行前必须先发消息讲清时间和取消方式，禁止静默执行。

param(
  [int]$DelaySeconds = 90
)

$log = 'D:\Hermes\logs\restart_app.log'
$exe = 'D:\Hermes\hermes-agent\apps\desktop\release\win-unpacked\Hermes.exe'
$cancelFlag = 'D:\Hermes\logs\restart_cancel.flag'

function W($m) { "$([DateTime]::Now.ToString('yyyy-MM-dd HH:mm:ss'))  $m" | Out-File -FilePath $log -Append -Encoding utf8 }

function Get-Targets {
  Get-CimInstance Win32_Process | Where-Object {
    $_.Name -eq 'Hermes.exe' -or
    ($_.Name -eq 'python.exe' -and $_.CommandLine -and (
        $_.CommandLine -match 'hermes_cli\.main\s+serve' -or
        $_.CommandLine -match 'hermes_cli[\\/]main\.py"?\s+serve' -or
        $_.CommandLine -match 'scrapling-mcp'))
  }
}

W ""
W "=========================================================="
W "=== 收到重启请求，等待 $DelaySeconds 秒（留给 Agent 说完话） ==="
Start-Sleep -Seconds $DelaySeconds

if (Test-Path $cancelFlag) {
  W "!!! 检测到取消标记 $cancelFlag —— 已放弃重启"
  Remove-Item $cancelFlag -Force -ErrorAction SilentlyContinue
  exit 0
}

if (-not (Test-Path $exe)) {
  W "!!! 找不到 $exe —— 为保证安全，放弃重启（未杀任何进程）"
  exit 1
}

W "--- 重启前进程 ---"
Get-Targets | ForEach-Object { W ("  PID {0}  {1}  启动于 {2}" -f $_.ProcessId, $_.Name, $_.CreationDate) }

# 1) 先关 Electron 主程序（连带它的子进程一起走）
Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'Hermes.exe' } | ForEach-Object {
  W ("kill Hermes.exe PID {0}" -f $_.ProcessId)
  try { Stop-Process -Id $_.ProcessId -Force -ErrorAction Stop }
  catch { W ("  kill 失败: " + $_.Exception.Message) }
}
Start-Sleep -Seconds 3

# 2) 清扫残留后端 / MCP
Get-Targets | ForEach-Object {
  W ("kill 残留 {1} PID {0}" -f $_.ProcessId, $_.Name)
  try { Stop-Process -Id $_.ProcessId -Force -ErrorAction Stop }
  catch { W ("  kill 失败: " + $_.Exception.Message) }
}

# 3) 等进程彻底退干净（单实例锁释放）
$deadline = (Get-Date).AddSeconds(30)
while ((Get-Date) -lt $deadline) {
  if (-not (Get-Targets)) { break }
  Start-Sleep -Seconds 2
}
$left = @(Get-Targets)
if ($left.Count -gt 0) {
  W ("WARN 仍有残留: " + (($left | ForEach-Object { "$($_.Name):$($_.ProcessId)" }) -join ', '))
} else {
  W "OK 全部进程已退出，单实例锁应已释放"
}

# 4) 重新拉起桌面版
W ("启动: " + $exe)
try { Start-Process -FilePath $exe } catch { W ("  启动失败: " + $_.Exception.Message) }
Start-Sleep -Seconds 25

W "--- 重启后进程（CreationDate 必须晚于改动文件 mtime） ---"
Get-CimInstance Win32_Process | Where-Object {
  $_.Name -eq 'Hermes.exe' -or
  ($_.Name -eq 'python.exe' -and $_.CommandLine -and $_.CommandLine -match 'hermes_cli\.main\s+serve')
} | ForEach-Object { W ("  PID {0}  {1}  启动于 {2}" -f $_.ProcessId, $_.Name, $_.CreationDate) }
W "=== 重启流程结束，请测试语音播报 / 目标功能 ==="
