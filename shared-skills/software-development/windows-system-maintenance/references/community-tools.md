# 社区 Windows 维护方案取舍（2026-10-20 核过 star / pushed_at / archived）

> **这份清单是我自己的内核参考，不是给凡哥的下载清单。**
> 2026-10-20 他把一屏 GUI 项目清单打回：「我是想让你拥有成熟的能力，帮我维护系统，并不是找到一个项目我来操作」。
> 提 GUI 之前先问自己：命令行内核能不能直接干？能，就别推界面。

## 装 / 升 / 卸软件

| 项目 | ★ | 状态 | 我怎么用 |
|---|---|---|---|
| `microsoft/winget-cli` | 26.5k | 活跃（2026-10-14） | **主力内核**，本机已装，走 WindowsApps 全路径调用 |
| `Devolutions/UniGetUI`（原 marticliment/UniGetUI） | 26.7k | 活跃（2026-10-19） | 统一 winget/Scoop/Choco/pip/npm 的 GUI；**只有凡哥要自己看界面时才装** |
| `BCUninstaller/Bulk-Crap-Uninstaller` | 22.0k | 活跃（2026-09-07） | winget 卸不干净时的批量卸载 + 扫残留 |
| `ScoopInstaller/Scoop` | 24.8k | 活跃 | 便携式命令行软件；和 winget 互补，本机未用 |
| `chocolatey/choco` | 11.5k | 活跃 | 老牌包管理器，服务端/团队场景 |

## 系统维护 / 去广告 / 优化

| 项目 | ★ | 状态 | 取舍 |
|---|---|---|---|
| `ChrisTitusTech/winutil` | 64.6k | 活跃（2026-10-19） | 装软件 + tweaks + 修系统 + 更新缓存，支持配置文件无人值守。**单脚本，可读可审**，适合我拿来当"批量设置"参考 |
| `Raphire/Win11Debloat` | 60.1k | 活跃（2026-10-18） | 删预装、关遥测、关推荐；有图形菜单也能命令行批量 |
| `farag2/Sophia-Script-for-Windows` | 9.8k | 活跃（2026-10-19） | 150+ 功能，**每项可一键还原**，会自动建清理计划任务。最规范的一个 |
| `files-community/Files` | 46.1k | 活跃 | 现代化资源管理器（多标签/双面板），整理素材时好用 |
| `microsoft/PowerToys` | 139.5k | 活跃（2026-10-20） | PowerRename 批量改名、批量图片改尺寸——整理素材主力 |
| `qarmin/czkawka` | 34.4k | 活跃（2026-09-16） | 找重复文件/空文件夹/相似图片/大文件 |
| `harry0703/MangoDisk` | 4.4k | 活跃（2026-10-18） | 磁盘空间分析 + 清理，跨平台 |

## 文件自动归档

| 项目 | ★ | 状态 | 取舍 |
|---|---|---|---|
| `tfeldmann/organize` | 3.2k | 活跃（2026-10-19） | YAML 规则自动归档（"下载夹 mp4 超 30 天挪 D 盘归档"）；跨平台、纯命令行，**最契合我的用法** |

## ⛔ 已归档，别用

| 项目 | ★ | 归档时间 | 原因 |
|---|---|---|---|
| `hellzerg/optimizer` | 18.2k | **2026-01-20 归档** | 名气大但停更，跟着新系统改注册表容易出事 |
| `Sycnex/Windows10Debloater` | 18.8k | **2023-03-10 归档** | 同上，年代太久 |

→ 凡哥问"哪个火"时，**别按 star 排**，先看 `archived` 和 `pushed_at`。他的尺子：「最新」按 pushed_at 核。

## 查证手法（GitHub API 实战）

```bash
curl -sL --max-time 20 -H "User-Agent: check" "https://api.github.com/repos/<owner>/<repo>" |
python -c "import sys,json;d=json.load(sys.stdin);print(d['full_name'],d['stargazers_count'],d['pushed_at'],d['archived'])"
```

踩过的坑：
- **必须 `-sL` 跟重定向**：仓库改名/迁组织（`marticliment/UniGetUI` → `Devolutions/UniGetUI`、
  `Klocman/Bulk-Crap-Uninstaller` → `BCUninstaller/Bulk-Crap-Uninstaller`）时不跟会拿不到数据
- 匿名 API 限流很紧（约 60 次/小时/IP），**批量查要 `sleep 1~2`**，否则一半返回空
- 返回 `None` 不代表项目不存在 → 先怀疑限流或重定向，重试一次再下结论
