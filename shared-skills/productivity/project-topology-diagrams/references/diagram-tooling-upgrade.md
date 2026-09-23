# 拓扑图画布容量与工具升级（2026-09-23）

来源：凡哥提出「一张纸盛不下了、字太小看不清，去找专门做拓扑图的本地免费软件」→ 小南核证官方源后整理。

## 一、问题定性

- 现有载体：WPS 演示 `.pptx`，固定画布 13.33×7.5 in（≈33×19 cm），单页最多容纳约 55–60 个原生形状。
- **超载信号**：要让内容放得下就必须把正文字号压到 <6pt（实际已压到 5.6–6.2pt）→ 打印/屏幕都难读。
- 根因不是排版技巧，是**载体模型**：PPT 是"一页纸"，内容只增不减的拓扑图必然撑爆它。

## 二、三条路（按推荐度）

| 方案 | 费用 | 离线 | 为什么选/不选 |
|---|---|---|---|
| **draw.io Desktop**（diagrams.net） | 免费·开源 | ✅ 完全离线 | 无限画布 + 多页 + 缩放 + 导出高清；`.drawio` = XML → **可程序化生成/更新**（和现在的 `gen_topology_pptx.py` 同思路）；凡哥可拖框改字 |
| **yEd Graph Editor**（yWorks） | 免费（商用也免费） | ✅ | 强项＝**一键自动排版**（层级/树形/正交布局），适合"图乱了想一键理顺"；编辑体验不如 draw.io 顺手 |
| WPS 演示（现状） | 免费 | ✅ | 保留作**导出/分享**用：要发人、塞 PPT 时从新工具导出 PNG/PDF；别再往里塞新内容 |
| ~~ProcessOn（WPS 插件内）~~ / ~~亿图图示~~ | 会员 / 收费 | ✗ / — | 凡哥要求"不要钱的"，不推荐 |

## 三、核到的官方事实（2026-09-23 实测）

- **draw.io Desktop**：最新 tag **v31.4.5**，发布 **2026-09-08**，非预发布；Windows 安装包 `draw.io-31.4.5-windows-installer.exe` 约 139MB（另有 zip / arm64 版）。官方离线说明页：`drawio.com/docs/manual/editor/offline/`（明确 desktop 版日常使用不需要联网）；微软商店有官方条目「draw.io Diagrams」，发布方 **draw.io Ltd**。
- **yEd**：官网 `yworks.com/products/yed/download`，当前 **3.25.1**；官网 FAQ 明确 "The use of yEd is free of charge, and you can even use yEd in a commercial environment at no cost."
- **本机网络（实测）**：`github.com` 直连超时（curl 28）；`api.github.com` 200、`objects.githubusercontent.com` 可连、`apps.microsoft.com` 302、`www.yworks.com` 200。
  → 查版本/资源名一律走 **api.github.com**（`/repos/jgraph/drawio-desktop/releases/latest`）；**下载**优先走 winget 或微软商店通道，不要死磕 Releases 直链。

## 四、安装通道（2026-09-23 **已走通并装好**，照这条走）

```bash
# ✅ 走通的通道：微软商店源（Store CDN；apps.microsoft.com 可达）
winget install 9MVVSZK43QQW --source msstore \
  --accept-package-agreements --accept-source-agreements --disable-interactivity
# winget 不在 PATH 时：$LOCALAPPDATA/Microsoft/WindowsApps/winget.exe
# 找不到 ProductId 时先 winget search draw.io —— 会同时给出 winget 源与 msstore 源两条，优先 msstore 那条
```

### ❌ 实测失败的通道（别再照旧文档走一遍）

- `winget install JGraph.Draw`（默认 winget 源里的"官方包"）→ **失败**：它的清单 URL 指向
  `github.com/jgraph/drawio-desktop/releases/...msi`，而本机 `github.com` 被挡 →
  `InternetOpenUrl() failed. 0x80072efd : unknown error`。
  **"命令看起来最官方" ≠ "网络走得通"**；失败就换商店源，别反复重试同一条。
- 官网 Releases 直链（`github.com/...`）→ curl 28 超时（沙箱里下载 139MB 也只会卡死）。
- 兜底（本次也验过）：镜像前缀 `https://gh-proxy.com/<原直链>` 能下（HTTP 206），
  但**下载件必须核验**（size + sha256 对比 GitHub API 的 `assets[].digest` + `Get-AuthenticodeSignature`）——
  完整配方见 `hermes-network-proxy` 的 `references/blocked-github-downloads.md`。

### 装完后的实测事实（可直接依赖）

- 包装名 `draw.io.draw.ioDiagrams`，版本 **31.4.5.0 x64**，装到 `C:\Program Files\WindowsApps\draw.io.draw.ioDiagrams_31.4.5.0_x64__1zh33159kp73c`；
  AppId ＝ `draw.io.draw.ioDiagrams`（用 `Get-AppxPackage *draw* | Select Name,PackageFamilyName,InstallLocation` 复核）。
- **能打开本地 D 盘文件**（实测：双击/文件关联打开 `D:\Documents\我的文档\拓扑图\*.drawio` → 正常渲染、中文界面）→ 沙箱不挡我们要用的场景。
- 程序化生成的 `.drawio` 能被它正确渲染（本次用一个 3 节点测试文件验证过）。
- **装软件前先问凡哥**；安装过程可能弹一次权限提示，那个点按钮的动作归他。
- 安装是 139MB 级下载，放后台跑 + `notify=true`，别阻塞对话。
- 装成功后**删掉已下载的安装包**（本次 140MB，已清），保留 sha256/签名记录即可。

## 五、迁移做法（待实施，尚未实测）

思路：把 `gen_topology_pptx.py` 的 DATA 层（项目/模块/状态/卡点/待办/日报明细）映射成 **mxGraphModel XML**（`mxCell` 节点 + `edge` 连线），一页 `<diagram>` = 现有的一页 PPT；输出 `.drawio` 文件供 draw.io Desktop 打开编辑。
- 未实测项（做之前先小样验证一次）：坐标/尺寸单位、自动布局用不用、中文换行、导出 PNG 的命令行。
- **诚实口径**：对凡哥只说"我先把现有图转一份 .drawio 给你看效果"，不要宣称已跑通。

## 六、画布与字号规则（两个载体都适用）

1. 单页正文字号 **≥7pt** 为可读底线；需要 <6pt → 说明该页超载。
2. 超载先**拆页**（一项目一页 / 明细独立成页），再考虑换载体。
3. 换到无限画布后仍要**分区**（项目分块 + 组框），否则"无限"会变成"无边界的乱"。
4. 对外交付统一**导出 PDF/PNG**（对方不一定装 draw.io）。
