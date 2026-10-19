# 网页视频下载 · 开源项目矩阵

> 全部数据 **2026-10-18 通过 GitHub API 实拉**（`/search/repositories?sort=stars`、`/releases/latest`），
> 不是印象、不是二手博客。下次复核直接跑 `scripts/github_repo_search.py`，别照抄旧数字。

## 一、通用型（什么站都能试）

| 项目 | 星数 | 语言 | 最后推送 | 形态 | 备注 |
|---|---|---|---|---|---|
| `yt-dlp/yt-dlp` | 199,063 | Python | 2026-10-10 | 命令行 | 最强最全，1800+ 站点；本机已装（v2026.08.19 = 最新 release） |
| `imputnet/cobalt` | 45,089 | Svelte | 2026-04-06 | 网页/自建 | 界面漂亮，要自己搭服务 |
| `iawia002/lux` | 31,780 | Go | 2026-03-29 | 命令行 | Go 写的，快，中文站支持不错 |
| `alexta69/metube` | 15,027 | Python | 2026-10-09 | 自建 Web UI | 给 yt-dlp 套个网页界面，适合网络环境里共享用 |
| `Tyrrrz/YoutubeDownloader` | 16,463 | C# | 2026-10-09 | Windows GUI | 只管 YouTube |
| `JunkFood02/Seal` | 29,829 | Kotlin | 2026-09-25 | 安卓 App | 手机端 yt-dlp 壳 |

## 二、中文平台专用（抖音/快手/视频号/小红书）

| 项目 | 星数 | 语言 | 最后推送 | 形态 | 备注 |
|---|---|---|---|---|---|
| `putyy/res-downloader` | 20,717 | Go | 2026-10-16 | **图形界面** | **首选**。v3.1.3，Windows exe 仅 10.9MB。覆盖视频号、小程序、抖音、快手、小红书、直播流、m3u8、酷狗、QQ音乐 |
| `Evil0ctal/Douyin_TikTok_Download_API` | 20,762 | Python | 2026-10-18 | 自托管 API | 给程序员用，凡哥不需要 |

## 三、m3u8 / 流媒体（播放器切片那种）

| 项目 | 星数 | 语言 | 最后推送 | 形态 | 备注 |
|---|---|---|---|---|---|
| `nilaoda/N_m3u8DL-RE` | 8,920 | C# | 2026-10-12 | 命令行 | **主力**。v0.6.0-beta，多线程/AES-128 解密/自动合并 |
| `mediago-dev/mediago` | 9,268 | TypeScript | 2026-10-06 | **图形界面** | v3.5.0，能自动嗅探 HLS；Windows 安装包 161MB，偏重 |
| `nilaoda/N_m3u8DL-CLI` | 16,150 | C# | **2023-06-03** | 命令行 | ⚠️ **星多但停更三年，别推荐**，用 RE 版 |
| `Momo707577045/m3u8-downloader` | 7,105 | JS | 2025-04-22 | 网页工具 | 在线提取，偶尔够用 |

## 四、浏览器插件（不用装软件）

| 项目 | 星数 | 最后推送 | 备注 |
|---|---|---|---|
| `xifangczy/cat-catch`（猫抓） | 22,345 | 2026-10-14 | v2.7.2，crx 0.6MB，从 GitHub 下 crx 拖进浏览器即可，不用走应用商店 |

## 五、单站专用

- `ScottSloan/Bili23-Downloader` — 8,454★，2026-10-17 更新，B 站专用（多线程/音视频分离/弹幕）

## 选型结论（凡哥场景）

1. **一个 exe 就能用** → `res-downloader`（中文平台全覆盖，图形界面，10.9MB）
2. **网页里 m3u8 抓不到** → 猫抓嗅出真地址 + `N_m3u8DL-RE` 下载
3. **通用站点** → 本机 yt-dlp，已在 PATH，直接敲
4. **别推荐** → 停更的 N_m3u8DL-CLI、100MB+ 的 Electron 套壳（除非凡哥明确要图形界面）
