# 2026-10-20 首次 C 盘审计（实证数字，全部来自 scan_disk.ps1 实跑）

> 用途：下次维护前对照，判断哪些已处理、哪些反弹。**这是快照，不是永久事实——先重跑脚本再下结论。**

## 基本面

- Windows 11 家庭版，build 26200
- 内存 31.4 GB
- C: 298.7 GB（剩 33.7 GB）／ D: 624 GB（剩 112.4 GB）
- 当前会话**非管理员**
- winget v1.29.380 已装，但 bash / powershell 都找不到 → 走别名全路径

## 占用真相（按大小）

| 项 | 占用 | 性质 |
|---|---|---|
| **pagefile.sys** | **100.0 GB** | 手动固定 102400MB（自动管理已关），32G 内存配 100G 完全没必要 → **最大回收点** |
| AppData 合计 | 79.15 GB | 见下 |
| Windows\WinSxS | 12.88 GB | 系统组件库，只能 DISM 清理，禁手删 |
| Windows\Installer | 7.17 GB | 卸载/修复要用，禁删 |
| ~\.cache | 4.60 GB | 用户缓存 |
| Windows\SoftwareDistribution | 4.77 GB | 更新缓存，可清 |
| ProgramData\NVIDIA Corporation | 4.65 GB | 驱动缓存 |
| hiberfil.sys | 无 | 休眠已关 ✅ |

### AppData\Local TOP

uv 12.35 / Google 9.52 / pip 6.87 / ms-playwright 2.50 / Packages 2.40 / camoufox 2.39 /
JianyingPro 2.34 / Microsoft 2.32 / NetEase 1.96 / Ollama 1.47 / Temp 1.25（TEMP 已改 D，这是历史残留）/
camoufox_dl 1.22 / OpenClaw 1.08 / Doubao 0.98（已 junction 到 D）/ GitHubDesktop 0.91 / npm-cache 0.88

### AppData\Roaming TOP

LarkShell 7.02（飞书）/ Tencent 6.87（QQ）/ SodaMusic 5.06（汽水音乐）/ kingsoft 2.00（WPS）/
webcast_mate 1.97（直播伴侣）/ Adobe 0.95

## 已重定向（不用再做）

- 桌面 → `D:\admin桌面`
- 文档 → `D:\Documents`
- 下载 → `D:\下载`
- 图片 → `D:\数字资产\图片资产`
- 视频 → `D:\数字资产\视频资产`
- 音乐 → `D:\数字资产\音频资产`
- TEMP / TMP（用户 + 系统）→ `D:\Temp`

## 已有 junction

- `AppData\Local\Doubao` → `D:\MovedApps\Doubao`
- `AppData\Local\NetEase` → `D:\MovedApps\NetEase`

## 可疑文件核查结论

`C:\jaiwcdzzydmz.exe` 145,061,704 字节，2026-07-12 创建。
验签：Status = **Valid**，Subject = `CN="Douyin Vision Co., Ltd."`（抖音视觉，北京石景山）
→ **不是病毒**，是抖音系软件安装包残留，可清或归档。

## 估算可回收

- pagefile 改小/搬 D：**100 GB**
- 缓存搬 D + 清：uv 12.4 + pip 6.9 + npm 0.9 + ollama 1.5 + playwright 2.5 + camoufox 3.6 ≈ **28 GB**
- Roaming 大户搬 D：飞书 7.0 + QQ 6.9 + 汽水 5.1 + WPS 2.0 + 直播伴侣 2.0 + Adobe 1.0 ≈ **24 GB**
- Chrome 9.5 + .cache 4.6 ≈ **14 GB**
- 系统垃圾：SoftwareDistribution 4.8 + C:\Temp 残留 1.3 + 抖音安装包 0.15 ≈ **6 GB**

合计 ≈ **170 GB**；保守讲 C 盘空闲可从 33.7 GB 回到 **150 GB 以上**。

## 当时对凡哥的口径

- 先坦白"**C 盘不可能一点别的都没有**"，再给"除了系统本体，其它一律不留 C 盘"的承诺
- 分档给方案，**只建议先干一件**（pagefile 100GB），等他点头
