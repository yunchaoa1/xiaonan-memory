# 批量卸载脚本模板 —— 复制本文件，改 $Targets 即可用
# 必须提权运行：
#   powershell -NoProfile -Command "Start-Process powershell -Verb RunAs -ArgumentList '-NoProfile','-ExecutionPolicy','Bypass','-File','<本文件>'"
# 外层轮询：for i in $(seq 1 60); do grep -q "=== 完成" "D:\Temp\uninstall.log" && break; sleep 5; done
#
# ⚠️ 三条硬规矩（踩过）
#   1. 日志路径硬编码，别用 $env:TEMP —— 提权进程的 TEMP 可能不是你以为的那个
#   2. 退出码 0 不代表删掉了，必须复查目录大小（.NET 就是返回 0 但一字节没少）
#   3. 带用户数据的软件（便签/笔记/聊天）先备份再问，不要放进这个脚本

$ErrorActionPreference = 'Continue'
$Log = 'D:\Temp\uninstall.log'
if (Test-Path $Log) { Remove-Item $Log -Force }
function L([string]$m) {
  $line = '[{0}] {1}' -f (Get-Date -Format 'HH:mm:ss'), $m
  $line | Out-File $Log -Append -Encoding UTF8
  Write-Host $line
}

# ============ 改这里 ============
# Kind: msi | inno | nsis | squirrel | custom
# msi 要填 Id（即 PSChildName，形如 {GUID}）
$Targets = @(
  @{ Name = '示例-MSXML 4.0'; Kind = 'msi';      Id   = '{196467F1-C11F-4F76-858B-5812ADC83B94}' }
  @{ Name = '示例-Inno软件';  Kind = 'inno';     Path = 'D:\Program Files\XXX\unins000.exe' }
  @{ Name = '示例-NSIS软件';  Kind = 'nsis';     Path = 'D:\Program Files\YYY\uninstall.exe'; Args = '/S' }
  @{ Name = '示例-Electron';  Kind = 'squirrel'; Path = 'C:\Users\<用户>\AppData\Local\XXX\Update.exe' }
  @{ Name = '示例-自定义';    Kind = 'custom';   Path = 'D:\XXX\setup.exe'; Args = '--uninstall --system-level' }
)
# 要一并关掉的进程路径关键词
$KillPatterns = @('*示例*')
# ================================

$c0 = [math]::Round((Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='C:'").FreeSpace / 1GB, 2)
$d0 = [math]::Round((Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='D:'").FreeSpace / 1GB, 2)
L '=== 批量卸载开始 ==='
L ('管理员: ' + ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator))

L '--- 关闭占用进程 ---'
Get-Process -ErrorAction SilentlyContinue | Where-Object {
  $p = $_.Path; $p -and ($KillPatterns | Where-Object { $p -like $_ })
} | ForEach-Object { L ('   关闭: ' + $_.ProcessName); try { $_.Kill() } catch {} }
Start-Sleep -Seconds 2

L '--- 卸载 ---'
foreach ($t in $Targets) {
  switch ($t.Kind) {
    'msi' {
      try {
        $p = Start-Process msiexec.exe -ArgumentList "/X$($t.Id) /qn /norestart" -Wait -PassThru -ErrorAction Stop
        $note = switch ($p.ExitCode) { 0 {'成功'} 1605 {'未安装'} 3010 {'成功(需重启)'} 1618 {'另一安装占用'} 1603 {'失败'} default {"码$($p.ExitCode)"} }
        L ("   {0,-28} {1}" -f $t.Name, $note)
      } catch { L ("   {0,-28} 启动失败" -f $t.Name) }
    }
    { $_ -in 'inno','nsis','squirrel','custom' } {
      $a = if ($t.Args) { $t.Args } else {
        switch ($t.Kind) { 'inno' {'/SILENT'} 'nsis' {'/S'} 'squirrel' {'--uninstall -s'} default {''} }
      }
      if (-not (Test-Path -LiteralPath $t.Path)) { L ("   {0,-28} 卸载程序不存在，跳过" -f $t.Name); break }
      try {
        $p = Start-Process -FilePath $t.Path -ArgumentList $a -PassThru -ErrorAction Stop
        if ($p -and $p.WaitForExit(180000)) { L ("   {0,-28} 退出码 {1}" -f $t.Name, $p.ExitCode) }
        else { L ("   {0,-28} 超时(可能弹窗等待)，强制结束" -f $t.Name); try { $p.Kill() } catch {} }
      } catch { L ("   {0,-28} 异常: {1}" -f $t.Name, $_.Exception.Message) }
    }
  }
}

Start-Sleep -Seconds 3

# ============ 复查（必做）============
L '--- 复查 ---'
$names = $Targets | ForEach-Object { $_.Name }
$keys = @(
  'HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*',
  'HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*',
  'HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*'
)
$still = Get-ItemProperty $keys -ErrorAction SilentlyContinue | Where-Object {
  $n = $_.DisplayName
  $n -and ($names | Where-Object { $n -like ('*' + $_ + '*') })
} | Select-Object -ExpandProperty DisplayName -Unique
if ($still) { $still | ForEach-Object { L ('   注册表仍存在: ' + $_) } } else { L '   注册表已清干净' }

$c1 = [math]::Round((Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='C:'").FreeSpace / 1GB, 2)
$d1 = [math]::Round((Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='D:'").FreeSpace / 1GB, 2)
L ("C 盘: $c0 -> $c1 GB (增加 " + [math]::Round($c1 - $c0, 2) + ' GB)')
L ("D 盘: $d0 -> $d1 GB (增加 " + [math]::Round($d1 - $d0, 2) + ' GB)')
L '=== 完成 ==='
