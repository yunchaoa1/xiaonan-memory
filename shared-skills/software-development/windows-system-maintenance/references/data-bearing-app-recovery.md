# 带用户数据的软件：误删后如何救回来（好用便签实战 · 2026-10-20）

## 事故经过（记着，别重演）

凡哥说"思维导图留，其余可以删"。好用便签在那个"其余"里 → 我**先备份了数据再卸载**，还清了目录和注册表。
他下一句话是："好用便签先留着，我有用。"

判断没错（清单确实包含它），**错在没单独问一句**。带用户数据的软件永远不并入"批量删"。

## 前置：什么叫"带用户数据"

装之前先看它的安装目录 / 用户目录里有没有这些东西（本次实例 `C:\Users\bobby\haoyongbianqian\`）：

- `data\*.db`、`*.ini`、`backup\*.bk` ← 真正的用户数据
- `image\`（头像、附图）
- `dump\` `temp\` `update\` `*.log` ← 垃圾，不用备

备份只要 `data` + `image` 就够（本次 8.55MB）。
落点固定：`D:\Documents\_卸载备份_<YYYYMMDD>\<软件名>\`。

## 救回六步（全部实测跑通）

### 1. 确认备份里有真数据
看 `data` 里主库的 `LastWriteTime` 是不是他最后使用的那天（本次 10:24:55 = 当天上午）。

### 2. 官网直连大概率抓不到 → 走 Clash 代理
```
curl -sL "<官网下载页>"            # → 0 字节，exa/crawl 也返回 CRAWL_EMPTY_CONTENT
netstat -ano | grep -E "7897|7890" # → 127.0.0.1:7897 LISTENING（Clash Verge 混合端口）
curl --proxy http://127.0.0.1:7897 -sL -A "Mozilla/5.0 ..." "<官网下载页>"
```
本机实测：直连 0 字节，挂 7897 立刻 8KB 正常页面。

### 3. 下载页给的是跳转页，再抓一层才有真链
```
downloadCenter.html → href="xiazai_pc.html?v=8.0.5"
xiazai_pc.html      → location.href = "https://dl.haoyong333.com/.../HaoYongBianQianSetup_v8.0.5.exe"
```
小技巧：`grep -oiE 'https?://[^"'"'"' <>\\]*\.(exe|zip)'` 直接从 JS 里抠真链。

### 4. 下载完先验签，再装
```powershell
$s = Get-AuthenticodeSignature 'D:\下载\xxx.exe'
$s.Status                    # 必须 Valid
$s.SignerCertificate.Subject # 签名者要对得上公司名
```
本次：`CN="Shenzhen Qianbaichi Network Technology Co., Ltd."` = 深圳千百尺，官网一致 → 才装。

### 5. 静默装回原路径
```powershell
Start-Process -FilePath $setup -ArgumentList '/VERYSILENT /SUPPRESSMSGBOXES /NORESTART /DIR="D:\Program Files\haoyongbianqian"' -Wait -PassThru
```
⚠️ **别按"猜的路径"判断安装失败**：新版装到了 `D:\Program Files\haoyongbianqian`，
不是原来的 `D:\Program Files (x86)\haoyongbianqian`（少了 x86），我第一次按旧路径检查 → 误判"安装未成功"，
脚本中途 `exit`，白跑一轮。**装完一律读注册表确认**：
```powershell
Get-ItemProperty $keys | Where DisplayName -like '*便签*' | Select InstallLocation, UninstallString
```

### 6. 杀进程 → 另存新版初始数据 → 回填 → 启动 → **看日志**
```powershell
Get-Process | Where { $_.Path -like '*haoyong*' } | Stop-Process -Force
Copy-Item "$dataDir\*" "D:\Documents\_卸载备份_<日期>\新版初始数据" -Recurse   # 保底
Copy-Item "<备份>\data\*"  "$dataDir\data"  -Recurse -Force
Copy-Item "<备份>\image\*" "$dataDir\image" -Recurse -Force
Start-Process "<安装目录>\<主程序>.exe"
```

**验证只认日志，不认进程**：
- `Get-Process` 有进程但 `MainWindowTitle` 是空的 → 这软件是贴边/托盘型，正常，**不能据此判失败**
- 真凭据：程序自己的 log（`haoyongnote.log`）尾部出现业务动作
  `sync_manager.cpp:580 同步团队提醒便签数据......完成` = 真的读库成功了
- 再加一条：`data\*.db` 的 `LastWriteTime` 被程序改成当前时间 = 库被打开并写入了

## 通用化（下次遇到别的软件照这个骨架走）

1. 备份 `data`/`image`/`*用户内容目录*`
2. `netstat` 找代理端口 → 挂代理取官网 → 抓真链
3. 验签名（Valid + 公司名对得上）
4. `/VERYSILENT ... /DIR="<原路径>"` 装回
5. **读注册表确认实际安装位置**
6. 杀进程 → 另存新版初始数据 → 回填 → 启动 → **看它自己的日志**
