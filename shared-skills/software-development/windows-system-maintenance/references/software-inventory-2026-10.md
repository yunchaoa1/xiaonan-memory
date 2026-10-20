# 软件盘点与清理进度（2026-10-20）

> 这项工作**没做完**，凡哥是「一个一个过、你问我」的节奏。下次接着说，从「未过完的候选」往下走。

## 盘点口径

- ARP 原始条目 **236 条** → 过滤 `SystemComponent` / `ParentKeyName` / `KB\d+` / 大小写重复 GUID 后，**真实软件 99 个**。
- **以后一律报 99，别报 236**（凡哥当场会追问数字怎么来的）。
- 卸载命令枚举模板见 `templates/batch_uninstall.ps1` 顶部注释。

## 凡哥的使用画像（他亲口，2026-10-20）

> 「我现在除了 comfyui，wps，貌似没有其他的办公输出软件再用，剪映有时用一用」

- **主力**：ComfyUI
- **办公输出**：WPS
- **偶尔**：剪映
- 推论：绝大多数装着的是历史残留 → 判断可以果断。但**每件仍要问**，别自作主张批量清。

## 已完成（2026-10-20）

| 软件 | 类型 | 结果 |
|---|---|---|
| NVIDIA Nsight Visual Studio Edition 2025.4.0 | MSI | ✅ 退出码 0 |
| NVIDIA Nsight Systems 2023.4.4 | MSI | ✅ 退出码 0 |
| NVIDIA Nsight Systems 2024.4.2 | MSI | ✅ 退出码 0 |
| NVIDIA Nsight Compute 2024.3.0 | MSI | ✅ 退出码 0 |
| NVIDIA Nsight Systems 2025.5.2 | MSI | ✅ 退出码 0 |
| 提示词大师 2.9.0（D 盘 2457MB） | Inno `/SILENT` | ✅ 目录已删 |

**实际回收：C 盘 ~1.7GB + D 盘 ~2.3GB ≈ 共 4GB**（我事先估 6.9GB，虚高 —— 教训已写进 SKILL.md 坑列表）。

**驱动验证**：`nvidia-smi` 出 RTX 5080 Laptop / 596.36 / 16303MiB，`NvContainerLocalSystem` 与
`NVDisplay.ContainerLocalSystem` 均 Running。卸完 `C:\Program Files\NVIDIA Corporation` 整个目录消失属正常。

## 未决：.NET 运行时（等凡哥在 A/B 里选）

12 个版本，`C:\Program Files\dotnet` 实测合计 **1.13GB**（注册表报 2.3GB，又虚高）。

| 版本 | 状态 | 实测 |
|---|---|---|
| 3.0.3 / 3.1.32 / 5.0.17 | 已停止支持（2022 年前） | 各 ~65-85MB ×2 |
| 6.0.11 / 6.0.16 / 6.0.31 | 2024-11 停止 | ~68MB |
| 7.0.20 | 2024-05 停止 | ~69MB |
| 9.0.4 | 2026-05 停止 | ~74MB |
| **8.0.6 / 8.0.21** | 保留（一线） | ~160MB |

- 方案 A：只清 3.0/3.1/5.0 → 回收 ~470MB，近零风险
- 方案 B：这笔跳过，直接攻缓存搬家（60GB+）
- **我的判断：为 850MB 冒「某软件打不开」的风险不值**。ComfyUI 是 Python、WPS/剪映不吃 .NET，技术上可全删，但性价比低。
- 重装兜底：`"$WG" install Microsoft.DotNet.DesktopRuntime.6`

## 下一批候选（还没问过）

按「收益 × 判断清晰度」排序：

1. **ASUS 全家桶 ~14 个**（Armoury Crate / AURA 灯效 ×3 / ROG Live Service / GlideX / Virtual Assistant 等）
   → 灯效和监控组件，占空间不多但拖开机、占后台。问一次「主板灯效你还调吗」就能定。
2. **浏览器四选一**：Edge 2.8G(D) / Chrome 9.5G 缓存(C) / UC 1.14G / 夸克 1.15G
3. **Copilot 2.8GB**（D:\Program Files (x86)\Microsoft\Copilot）
4. **来路不明的小软件**：每日大赛 133MB、beyond_tunnel 427MB、好用便签 127MB、LibLibAI Client 411MB、
   喜马拉雅 194MB、汽水音乐 5.06G 缓存、webcast_mate（直播伴侣）1.97G
5. **废弃微软老组件**（合计仅几百 MB，顺手清）：Games for Windows LIVE ×2、Silverlight、
   XNA 3.1/4.0、AppLocale、MSXML 4.0 SP3
6. **确定留**：炉子(luzi 60MB，凡哥自己的)、RustDesk、Ditto、PotPlayer、FileZilla、GitHub Desktop、CC Switch

## 真正的大头（软件删完也解决不了）

C 盘 265GB 用量里，**60GB+ 是缓存**，不是软件：

- Python 三件套：`AppData\Local\uv` 12.35G + `pip` 6.87G + `npm-cache` 0.88G
- 浏览器内核：`ms-playwright` 2.50G + `camoufox` 2.39G + `camoufox_dl` 1.22G
- 聊天/办公缓存：`Roaming\LarkShell`(飞书) 7.02G、`Tencent`(QQ) 6.87G、`SodaMusic` 5.06G、
  `kingsoft`(WPS) 2.00G、`webcast_mate` 1.97G
- `AppData\Local\Google`(Chrome) 9.52G、`~\.cache` 4.60G、`Ollama` 1.47G

手法见 SKILL.md「搬家三层手法」——缓存类**优先环境变量**（改完新生效，不用搬目录）。
