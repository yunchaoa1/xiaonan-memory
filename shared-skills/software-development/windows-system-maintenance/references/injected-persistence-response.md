# 被植入的持久化：识别与清除（2026-10-20 实证）

> 触发场景：清理开机启动项时，顺手核了一下「启动文件夹到底在哪」，发现路径被篡改。
> 结论：**2026-07-12 20:23 那一分钟，有安装包往本机投放了一套隐蔽自启。**
> 本文是完整证据链 + 可直接复用的清除命令。凡哥机器已按此清完（见文末状态）。

---

## 一、这类东西长什么样（不是典型病毒）

**它有合法数字签名。** `security_cad.exe` 验签 `Valid`，
签名主体 `CN="BEIJING QIYI CENTURY SCIENCE&TECHNOLOGY CO.,LTD."`（爱奇艺），
文件描述「爱奇艺嵌入式浏览器子进程」。

**所以「签名有效 = 安全」是错的判定。** 判据要加三条：

| 判据 | 正常软件 | 本例 |
|---|---|---|
| 放哪 | Program Files / AppData | `C:\Users\Public\Documents\` 下随机名目录 |
| 名字 | 与产品名一致 | `security_cad.exe`（伪装成"安全CAD"）、目录 `Bctive` / `Wctive` |
| 怎么自启 | 自己的 Run 键 / 服务 | **篡改系统「启动文件夹」指向它** |
| 卸载 | 有 ARP 条目 | **ARP 里查不到**（没有卸载项，用户无从发现） |
| 权限 | 普通目录 | **给自己加了 DENY 删除锁** |

> 判定口径：**签名只排除"这是病毒"，不排除"这是偷偷塞进来的东西"。**
> 有签名 + 藏位置 + 改系统路径 + 拒绝删除 = 不能留。

---

## 二、五项检测（发现靠这几条，逐条跑）

### 1. 启动文件夹路径是否被改（最关键）

```powershell
$usf = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders'
$sf  = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders'
(Get-ItemProperty $usf -Name Startup).Startup
(Get-ItemProperty $sf  -Name Startup).Startup
```

**正常值**：`%USERPROFILE%\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup`
**本例值**：`C:\Users\Public\Documents\Wctive` —— 且**末尾带一个 `\u0000` 空字符**。

⚠️ 两个坑：
- 值末尾的 NUL 会让某些工具/安全软件解析失败（规避手法）。比较时先 `-replace "`0",'<NUL>'` 再打印，
  否则终端里根本看不出来。
- `[Environment]::GetFolderPath('Startup')` 返回的是**注册表值算出来的路径**，
  它被骗了也会跟着返回假路径。所以**必须回注册表核对**，不能只信这个 API。

### 2. 启动项三处来源分开看（Location 字段）

```powershell
Get-CimInstance Win32_StartupCommand | Select-Object Name, Location, User, Command
```

`Location` 会告诉你在哪：

| Location 值 | 实际位置 | 清除方式 |
|---|---|---|
| `Startup` | `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup` | 删 .lnk / .vbs 文件 |
| `Common Startup` | `C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup` | 删 .lnk（需提权） |
| `HKU\S-1-5-21-...\...\Run` | HKCU Run | `Remove-ItemProperty` |
| `HKLM\SOFTWARE\...\Run` | HKLM Run | `Remove-ItemProperty`（需提权） |

> **只查 Run 键会漏。** 本例主载荷就藏在「启动文件夹」里、指向 Public 目录，Run 键干干净净。

### 3. 计划任务也是持久化（Run 之外）

```powershell
Get-ScheduledTask | Where-Object {
  $_.TaskPath -notlike '\Microsoft\*' -and $_.TaskName -notmatch '^(OneDrive|Adobe|NVIDIA|MicrosoftEdge)'
} | ForEach-Object { $_.TaskPath + $_.TaskName + ' -> ' + (($_.Actions | ForEach-Object { $_.Execute }) -join '; ') }
```

本机实例：`\BeyondNetTunnel -> D:\Program Files\beyondnetwork.net\beyond_tunnel\beyond_tunnel.exe`
——**内网穿透工具是靠计划任务自启的**，程序删了任务还留着（指向空文件）。
删除：`schtasks /Delete /TN "BeyondNetTunnel" /F`

> 教训：删完软件要**回头扫一遍计划任务**，否则留一堆指向空路径的僵尸任务。

### 4. 进程来源反查（谁拉起来的）

```powershell
Get-CimInstance Win32_Process -Filter "Name='security_cad.exe'" |
  Select-Object ProcessId, ParentProcessId, CommandLine, CreationDate
```

本例 `ParentProcessId` → **`explorer.exe`**，且 `CreationDate` 等于**当天登录时间**（10:25:01）。
→ **父进程是 explorer + 时间戳贴着登录 = 走"启动项"拉起的**，不是用户手动开的。这个组合非常好认。

### 5. Public 目录下的可疑文件夹

```powershell
Get-ChildItem 'C:\Users\Public\Documents' -Directory -Force | Select-Object Name, LastWriteTime
```

本例：`Bctive`(20:23:27) 和 `Wctive`(20:23:10) —— **同一分钟内创建、命名同构（5 字母 + ctive）、
其他目录（Adobe / Alibaba）都是正常厂商名**。这种"随机名 + 同批时间"就是投放痕迹。

---

## 三、清除（ACL 锁是难点，普通管理员删不掉）

### 现象

```
Access to the path is denied.        ← 即使提权也删不掉
```

`icacls` 看一眼就明白了：

```
C:\Users\Public\Documents\Bctive BUILTIN\Users:(OI)(CI)(DENY)(DE,DC)   ← 元凶
                                 BUILTIN\Users:(OI)(CI)(RX)
                                 BUILTIN\Administrators:(I)(OI)(CI)(F)
```

`(DENY)(DE,DC)` = **显式拒绝「删除」和「删除子项」**。显式 DENY **优先级高于 Allow**，
所以管理员有 `(F)` 也删不动。**必须先把这个 DENY 条目摘掉。**

### 正确顺序（实测跑通，缺一步就失败）

```powershell
$d = 'C:\Users\Public\Documents\Bctive'

icacls "$d" /remove:d "BUILTIN\Users" /t /c          # ① 摘掉 DENY（第一步，顺序不能换）
icacls "$d" /reset /t /c                             # ② ACL 重置成继承
takeown /f "$d" /r /d y                              # ③ 夺取所有权
icacls "$d" /grant "*S-1-5-32-544:(OI)(CI)F" /t /c   # ④ 管理员完全控制
Remove-Item -LiteralPath $d -Recurse -Force          # ⑤ 删
if (Test-Path -LiteralPath $d) { cmd /c "rd /s /q `"$d`"" }   # ⑥ 兜底
```

- `*S-1-5-32-544` 是 Administrators 的 SID —— **用 SID 不用名字**，避免中文/本地化系统上名字对不上。
- ② `icacls /reset` 有时不认，跳过也行，① ③ ④ 是关键。
- ⑤ 删不掉时别硬刚循环：重命名成 `<原名>.DELETEME`，重启后再删。

### 删除前先留证

```powershell
# 先把内容复制到隔离区，再删壳（本例 5 个文件：322.txt / falcon.dll / security_cad.exe / unload.txt / helper.lnk）
Copy-Item -LiteralPath $_.FullName -Destination $iso -Recurse -Force
```

---

## 四、善后三件事（少一件就还有隐患）

1. **修复启动文件夹路径**（并去掉 NUL）：
   ```powershell
   Set-ItemProperty -Path $usf -Name Startup `
     -Value '%USERPROFILE%\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup' -Type ExpandString -Force
   Set-ItemProperty -Path $sf -Name Startup `
     -Value "$env:USERPROFILE\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup" -Type String -Force
   ```
   改完**回读一次**，确认 `-match "`0"` 为假。注意类型：`User Shell Folders` 要 `ExpandString`。

2. **留备份**：`reg export "HKCU\...\User Shell Folders" backup.reg /y`，把原值（含 NUL）写进 txt。
   凡哥要的是"能还原"，一个 reg 导出胜过解释。

3. **建议全盘扫描**：既然被投放过一次，跑 Defender 全盘确认没第二窝。
   （提权 `Start-MpScan -ScanType FullScan`，几十分钟，后台跑。）

---

## 五、本机已处置状态（2026-10-20，别再重复诊断）

**已清除：**
- `C:\Users\Public\Documents\Bctive`、`...\Wctive`（拆 ACL 锁后彻底删除）
- `security_cad.exe` 进程已杀
- `C:\jaiwcdzzydmz.exe`（138MB）已隔离
- 计划任务 `\BeyondNetTunnel` 已删
- 隔离备份在 `D:\Documents\_隔离_20261020\`

**启动文件夹路径已修复**为正常值（原值备份在同目录 `registry-startup-backup.txt`）。

**开机启动项按凡哥要求收到只剩：**
微信(Weixin) / 飞书(Feishu) / 豆包(doubao) / 好用便签(HaoYongBianQian) —— 他自己点名的四个，
外加 `Hermes_Gateway`（Hermes 自启）、`RtkAudUService`（Realtek 声卡，**关了可能没声音**）、
`SecurityHealth`（Windows 安全中心）。**后三个别当垃圾关掉。**

**已取消**：企业微信(WXWork)、汽水音乐、QuarkUpdater、UC、RustDesk Tray、
Virtual Pet（虚拟宠物）、**EdgeDebug**。

> ⚠️ `EdgeDebug` 是 `msedge.exe --remote-debugging-port=19222 --remote-debugging-address=0.0.0.0`
> —— 调试端口绑 `0.0.0.0` 等于**局域网谁都能接管你的浏览器**。这种项看到就删，
> 需要调试时改成 `--remote-debugging-address=127.0.0.1`。

**已卸载**：GlideX（手机投屏，MSI，`/X{A06BDD76-D95C-4AC7-A0DA-73971F366D9B}`）、
Virtual Pet（无 ARP 条目，只能删目录 + 删启动项）。

**保留**（凡哥 2026-10-20 明确）：AURA 灯效、风扇监控、Armoury Crate（ASUS 那套只删虚拟宠物和投屏）。

---

## 六、反推来源

时间戳是关键：`jaiwcdzzydmz.exe`(20:23:09)、`Wctive`(20:23:10)、`Bctive`(20:23:20-27)
—— **同一分钟投放三样东西 = 某个安装包捆绑的**。

`D:\下载` 留存了那批原始安装包（`mrds_windows_1.0.0.exe`、`Luzi_0.1.13_x64-setup.exe`、
`Ximalaya`、`UCWin`、`td-setup`、`猫抓一键安装工具b4.exe`），可据此反推。
**没有安装日志就直接说"查不到确凿来源"，别编故事**（凡哥的尺子：禁推测）。
