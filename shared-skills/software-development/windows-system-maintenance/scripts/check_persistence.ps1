# 启动项 / 持久化 只读审计（不改任何东西）
# 用法：powershell -NoProfile -ExecutionPolicy Bypass -File check_persistence.ps1
# 输出：屏幕摘要 + D:\Temp\persistence_audit.txt
# 背景与判读方法见 references/injected-persistence-response.md

$ErrorActionPreference = 'SilentlyContinue'
$out = 'D:\Temp\persistence_audit.txt'
if (-not (Test-Path 'D:\Temp')) { New-Item -ItemType Directory 'D:\Temp' -Force | Out-Null }
if (Test-Path $out) { Remove-Item $out -Force }
function W([string]$m) { $m | Out-File $out -Append -Encoding UTF8; Write-Host $m }
function H([string]$t) { W ''; W ('=== ' + $t + ' ===') }

W ('审计时间: ' + (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'))
W ('管理员: ' + ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator))

# ---------- 1. 启动文件夹路径是否被篡改 ----------
H '1. 启动文件夹路径（最容易被做手脚的地方）'
$usf = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders'
$sf  = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders'
$vU = (Get-ItemProperty $usf -Name Startup).Startup
$vS = (Get-ItemProperty $sf  -Name Startup).Startup
W ('  User Shell Folders = [' + ($vU -replace "`0", '<NUL>') + ']')
W ('  Shell Folders      = [' + ($vS -replace "`0", '<NUL>') + ']')
$expectTail = 'AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup'
$bad = $false
foreach ($v in @($vU, $vS)) {
  if (-not $v) { continue }
  if ($v -match "`0") { W '  !! 含 NUL 空字符 —— 规避手法，必须清'; $bad = $true }
  if ($v -notmatch [regex]::Escape($expectTail)) { W ('  !! 非标准路径: ' + $v); $bad = $true }
  if ($v -match 'Public') { W '  !! 指向 Public 目录 —— 高可疑（谁都能写）'; $bad = $true }
}
if (-not $bad) { W '  OK 正常' }
$realStartup = Join-Path $env:APPDATA 'Microsoft\Windows\Start Menu\Programs\Startup'
W ('  实际用户启动夹: ' + $realStartup)
W '  内容:'
Get-ChildItem -LiteralPath $realStartup -Force | ForEach-Object { W ('    ' + $_.Name + '  ' + $_.LastWriteTime) }

# ---------- 2. 启动项（三处来源分开列） ----------
H '2. Win32_StartupCommand（Location 字段告诉你在哪）'
Get-CimInstance Win32_StartupCommand | Sort-Object Location, Name | ForEach-Object {
  W ('  [' + $_.Location + ']  ' + $_.Name)
  W ('      ' + $_.Command)
}

# ---------- 3. Run / RunOnce ----------
H '3. Run / RunOnce 键'
foreach ($k in @(
  'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run',
  'HKCU:\Software\Microsoft\Windows\CurrentVersion\RunOnce',
  'HKLM:\Software\Microsoft\Windows\CurrentVersion\Run',
  'HKLM:\Software\Microsoft\Windows\CurrentVersion\RunOnce',
  'HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Run'
)) {
  $p = Get-ItemProperty $k
  if (-not $p) { continue }
  W ('  --- ' + $k)
  $p.PSObject.Properties | Where-Object { $_.Name -notlike 'PS*' } | ForEach-Object {
    W ('      ' + $_.Name + ' = ' + $_.Value)
  }
}

# ---------- 4. 计划任务（Run 之外最常被忽略） ----------
H '4. 非微软计划任务'
Get-ScheduledTask | Where-Object {
  $_.TaskPath -notlike '\Microsoft\*' -and $_.TaskName -notmatch '^(OneDrive|Adobe|NVIDIA|MicrosoftEdge|GoogleSystem)'
} | Sort-Object TaskPath, TaskName | ForEach-Object {
  $act = ($_.Actions | ForEach-Object { $_.Execute }) -join '; '
  $miss = ''
  $p = ($_.Actions | Select-Object -First 1).Execute
  if ($p -and $p -notmatch '^%' -and -not (Test-Path -LiteralPath $p)) { $miss = '   << 目标不存在(僵尸)' }
  W ('  ' + $_.TaskPath + $_.TaskName + ' -> ' + $act + $miss)
}

# ---------- 5. 运行中的非系统服务 ----------
H '5. 运行中的非 Windows 路径服务'
Get-CimInstance Win32_Service | Where-Object {
  $_.PathName -and $_.PathName -notmatch 'C:\\Windows\\' -and $_.State -eq 'Running'
} | Sort-Object Name | ForEach-Object { W ('  ' + $_.Name + ' | ' + $_.PathName) }

# ---------- 6. Public 目录可疑文件夹 ----------
H '6. C:\Users\Public\Documents 下的目录（随机名=可疑）'
Get-ChildItem 'C:\Users\Public\Documents' -Directory -Force | Sort-Object LastWriteTime |
  ForEach-Object { W ('  ' + $_.Name + '   ' + $_.LastWriteTime) }
W '  判读：厂商名(Adobe/Alibaba)=正常；随机5字母、同批时间创建=投放痕迹'

# ---------- 7. 浏览器调试端口暴露 ----------
H '7. 浏览器远程调试端口（绑 0.0.0.0 = 局域网可接管）'
$dbg = Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match 'remote-debugging' }
if ($dbg) {
  $dbg | ForEach-Object {
    $flag = if ($_.CommandLine -match '0\.0\.0\.0') { '  << 危险：绑全网卡' } else { '' }
    W ('  PID ' + $_.ProcessId + ' ' + $_.Name + $flag)
    W ('      ' + $_.CommandLine)
  }
} else { W '  无' }
Get-ItemProperty 'HKLM:\Software\Microsoft\Windows\CurrentVersion\Run' |
  Select-Object -Property * -Exclude PS* | ForEach-Object {
    $_.PSObject.Properties | Where-Object { $_.Value -match 'remote-debugging-address=0\.0\.0\.0' } |
      ForEach-Object { W ('  !! Run 键里有全网卡调试端口: ' + $_.Name) }
  }

# ---------- 8. 父进程是 explorer 且贴着登录时间的进程（启动项拉起特征） ----------
H '8. 由 explorer 拉起的进程（疑似自启，参考用）'
$logon = (Get-CimInstance Win32_OperatingSystem).LastBootUpTime
Get-CimInstance Win32_Process | Where-Object {
  $_.ParentProcessId -and $_.ExecutablePath -and
  $_.ExecutablePath -notmatch 'C:\\Windows\\' -and
  $_.CreationDate -gt $logon
} | ForEach-Object {
  $par = (Get-CimInstance Win32_Process -Filter "ProcessId=$($_.ParentProcessId)").Name
  if ($par -eq 'explorer.exe') { W ('  ' + $_.Name + '  ' + $_.ExecutablePath) }
}

H '完成'
W ('报告: ' + $out)
