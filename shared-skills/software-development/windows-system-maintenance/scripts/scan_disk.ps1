# 只读侦察：C 盘占用真相。不改任何东西。
# 用法：powershell -NoProfile -ExecutionPolicy Bypass -File scan_disk.ps1
#      建议 background=true 跑（AppData 递归要 1~4 分钟），完成后读 $out
$ErrorActionPreference = 'SilentlyContinue'
$ProgressPreference    = 'SilentlyContinue'
$out = Join-Path $env:TEMP 'disk_scan_report.txt'
Remove-Item $out -Force -ErrorAction SilentlyContinue
function W($m) { $m | Out-File $out -Append -Encoding utf8; Write-Host $m }

W '=== C 盘根目录大文件（>100MB）==='
Get-ChildItem 'C:\' -File -Force | Where-Object { $_.Length -gt 100MB } |
  Sort-Object Length -Descending |
  ForEach-Object { W ("{0,10:N2} GB  {1}" -f ($_.Length/1GB), $_.Name) }

W ''
W '=== AppData\Local 子目录 TOP 30 ==='
Get-ChildItem "$env:LOCALAPPDATA" -Directory -Force |
  ForEach-Object {
    $s = (Get-ChildItem $_.FullName -Recurse -File -Force | Measure-Object Length -Sum).Sum
    [pscustomobject]@{ N = $_.Name; GB = [math]::Round($s/1GB, 2) }
  } | Sort-Object GB -Descending | Select-Object -First 30 |
  ForEach-Object { W ("{0,10:N2} GB  {1}" -f $_.GB, $_.N) }

W ''
W '=== AppData\Roaming 子目录 TOP 20 ==='
Get-ChildItem "$env:APPDATA" -Directory -Force |
  ForEach-Object {
    $s = (Get-ChildItem $_.FullName -Recurse -File -Force | Measure-Object Length -Sum).Sum
    [pscustomobject]@{ N = $_.Name; GB = [math]::Round($s/1GB, 2) }
  } | Sort-Object GB -Descending | Select-Object -First 20 |
  ForEach-Object { W ("{0,10:N2} GB  {1}" -f $_.GB, $_.N) }

W ''
W '=== C:\ProgramData 子目录 TOP 20 ==='
Get-ChildItem 'C:\ProgramData' -Directory -Force |
  ForEach-Object {
    $s = (Get-ChildItem $_.FullName -Recurse -File -Force | Measure-Object Length -Sum).Sum
    [pscustomobject]@{ N = $_.Name; GB = [math]::Round($s/1GB, 2) }
  } | Sort-Object GB -Descending | Select-Object -First 20 |
  ForEach-Object { W ("{0,10:N2} GB  {1}" -f $_.GB, $_.N) }

W ''
W '=== 用户目录 TOP 20 ==='
Get-ChildItem $env:USERPROFILE -Directory -Force |
  ForEach-Object {
    $s = (Get-ChildItem $_.FullName -Recurse -File -Force | Measure-Object Length -Sum).Sum
    [pscustomobject]@{ N = $_.Name; GB = [math]::Round($s/1GB, 2) }
  } | Sort-Object GB -Descending | Select-Object -First 20 |
  ForEach-Object { W ("{0,10:N2} GB  {1}" -f $_.GB, $_.N) }

W ''
W '=== C:\Windows 关键子目录 ==='
foreach ($d in 'Temp','SoftwareDistribution','Installer','WinSxS','Prefetch','Logs','Panther','assembly') {
  $p = Join-Path 'C:\Windows' $d
  if (Test-Path $p) {
    $s = (Get-ChildItem $p -Recurse -File -Force | Measure-Object Length -Sum).Sum
    W ("{0,10:N2} GB  Windows\{1}" -f ($s/1GB), $d)
  }
}

W ''
W '=== 隐藏缓存点 ==='
foreach ($d in '.cache','.ollama','.docker','.conda','.npm','.nuget','.gradle','.m2') {
  $p = Join-Path $env:USERPROFILE $d
  if (Test-Path $p) {
    $s = (Get-ChildItem $p -Recurse -File -Force | Measure-Object Length -Sum).Sum
    W ("{0,10:N2} GB  ~\{1}" -f ($s/1GB), $d)
  }
}

W ''
W '=== 已重定向的用户文件夹 ==='
$usf = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders'
$p = Get-ItemProperty $usf
$p.PSObject.Properties | Where-Object { $_.Value -is [string] -and $_.Value -match '^[A-Z]:' } |
  ForEach-Object { W ("{0,-40} : {1}" -f $_.Name, [Environment]::ExpandEnvironmentVariables($_.Value)) }

W ''
W '=== 环境变量 TEMP/TMP ==='
W ("User TEMP = " + [Environment]::GetEnvironmentVariable('TEMP','User'))
W ("User TMP  = " + [Environment]::GetEnvironmentVariable('TMP','User'))
W ("Machine TEMP = " + [Environment]::GetEnvironmentVariable('TEMP','Machine'))

W ''
W '=== 已有的目录链接（junction/symlink）==='
foreach ($base in "$env:LOCALAPPDATA", "$env:APPDATA", 'C:\ProgramData', 'C:\Program Files') {
  Get-ChildItem $base -Directory -Force |
    Where-Object { $_.LinkType -eq 'Junction' -or $_.LinkType -eq 'SymbolicLink' } |
    ForEach-Object { W ($_.FullName + ' -> ' + $_.Target) }
}

W ''
W '=== 磁盘 ==='
Get-CimInstance Win32_LogicalDisk -Filter 'DriveType=3' |
  ForEach-Object { W ("{0} 可用 {1} GB / 共 {2} GB" -f $_.DeviceID, [math]::Round($_.FreeSpace/1GB,1), [math]::Round($_.Size/1GB,1)) }

W ''
W '=== 扫描完成 ==='
