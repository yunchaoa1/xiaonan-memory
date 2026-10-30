---
name: windows-system-maintenance
description: C盘满了/清理/搬家/装软件时用。本机Windows磁盘与路径治理。
version: 1.0.0
author: 小南
license: internal
metadata:
  hermes:
    tags: [windows, 磁盘, 清理, 路径迁移, winget, junction, 维护, C盘]
    related_skills: [local-tool-provisioning, comfyui-env-ops, skill-library-maintenance]
---

# 本机 Windows 维护（磁盘 / 路径 / 清理 / 软件）

> 2026-10-20 定。那天凡哥先问「社区有没有维护 Windows 的方案」，我给了 UniGetUI / WinUtil 一堆项目清单，
> 他当场纠正：**「我是想让你拥有成熟的能力，帮我维护系统，并不是找到一个项目我来操作」**。
> 所以本技能的第一条规矩是**姿态**，第二条才是技术。

## When to Use（何时加载）

- 凡哥说：C 盘满了 / 电脑卡 / 清理垃圾 / 把东西搬到 D 盘 / 默认路径改掉 / 整理文件 / 装软件 / 升级软件 / 卸软件 / 开机慢 / 这个文件是不是毒
- 凡哥问「**社区有没有 XX 方案 / 有没有工具 / 有没有项目**」，而上下文是「维护我这台电脑」
- 我自己发现磁盘吃紧、缓存膨胀，想主动提议维护

## 铁律 0 · 凡哥问"有没有方案"，多数意思是"这件事你替我干"

- 他要的是**能力长在我身上**：以后他说一句「清一下」「把这几个装上」「下载夹归一下类」，我直接执行 + 回报结果。
- 所以回答结构是：**我的触发话术 → 我实际会做什么 → 风险/可回滚 → 需要他做的只有"点一次管理员确认"这类物理动作**。
- 社区项目只当**我的内核**看（winget 就是内核，UniGetUI 只是它的 GUI 壳）。**别把 GUI 清单丢给他让他自己点。**
- 例外：他明确说"我想自己看着界面操作"时，才推 GUI（UniGetUI / BCUninstaller）。
- 贴项目地址给凡哥时**反链接化**（`github[.]com/owner/repo`，协议名不写全）—— 桌面版会自动开窗弹窗。

## 铁律 1 · 先只读侦察，再谈方案

**没有实盘数字就定路径表 = 脑补**，必被凡哥打回（他的尺子：禁推测、要先核证）。

```bash
# 1) 权限（决定哪些活能干）
net session >/dev/null 2>&1 && echo "ELEVATED: YES" || echo "ELEVATED: NO"

# 2) 完整侦察（只读，不修改任何东西；输出到 %TEMP%\disk_scan_report.txt）
powershell -NoProfile -ExecutionPolicy Bypass -File "<技能目录>/scripts/scan_disk.ps1"
```

脚本已经吐这几块，**照它看就够**：C 根大文件（pagefile/hiberfil）、AppData\Local 与 Roaming 子目录 TOP、
ProgramData TOP、C:\Windows 关键子目录、用户隐藏缓存点、已重定向的 shell 文件夹、TEMP/TMP、已有 junction。

⚠️ 全量递归扫 AppData 要 1~4 分钟 → 用 `terminal(background=true, notify=true)` 起，再 `process(wait)`，
**别在前台干等**。报告写文件、边扫边落盘，超时也不丢。

## 铁律 2 · 删除和搬移一律「先出清单，他点头才动」

- 清单要写**要动什么、从哪到哪、回收多少 GB、动了有什么后果**。
- 搬移先 `dry-run` 出计划表；删除分**安全级 / 需确认级**，需确认级永不自动跑。
- 所有动作写日志（时间、路径、大小、结果），留可回滚痕迹。
- **绝不自动删他的工作文件**（文档、素材、剧本、图片资产）——只搬不删，要删必须他点名。
- **带用户数据的软件（便签 / 笔记 / 聊天记录 / 云文档）先备份，再单独问一句。**
  凡哥说"清单里其余的可以删"**不等于**授权删这类软件。2026-10-20 翻车实录：好用便签在他的"可以删"
  清单里，我备份数据后卸了，他下一句是"好用便签先留着我有用"——虽然靠备份 + 官网重装救回来了，
  但这是**白干一轮 + 打断他手头的事**。以后固定顺序：
  **备份 → 单独问"这个里面有你的数据，要不要留" → 才动**。救回流程见 `references/data-bearing-app-recovery.md`。
- **禁删清单**（2026-10-20 凡哥确认在用）：Xmind（他要我用它画思维导图）、炉子（待研究用法）、
  好用便签、Chrome / Edge / UC / 夸克（四个浏览器都在真用）、WPS / 飞书 / 微信 / 剪映 / ComfyUI 及依赖。

## 铁律 3 · 改系统设置前记下原值

改注册表 / 环境变量前，先把当前值写进报告。凡哥不喜欢不可逆的改动，一句话"能还原"比十句解释管用。
（**pagefile 不在此列** —— 见下面专章，凡哥已定不动，别把它当可优化项。）

---

## 本机基线（2026-10-20 实测，复查时先核对是否已变）

- Windows 11 **家庭版** build **26200**，内存 **31.4 GB**，C: 298.7G、D: 624G
- **2026-10-20 一天下来的 C 盘曲线**（同一天多轮，别把旧数字当现状）：
  起始 **33.7G** → 清完软件 39.1G → 缓存改路径+清空 58.0G → 系统垃圾 63.1G →
  搬软件缓存(junction) 76.3G → 搬浏览器内核 **81.1G**。**当日净腾 47.4GB**，软件 99→69 个。
- **已经重定向好了**（别重复做）：桌面 `D:\admin桌面`、文档 `D:\Documents`、下载 `D:\下载`、
  图片/视频/音频 → `D:\数字资产\{图片资产,视频资产,音频资产}`、**TEMP/TMP（用户+系统）→ `D:\Temp`**
- D 盘既有目录（接在它们上，别另起一套）：`Program Files`、`Program Files (x86)`、`Programs`、
  `MovedApps`（飞书/剪映/豆包/网易云）、`AppData`（微信/WPS/企业微信/剪映/录屏/迅雷）、`temp`、`数字资产`、`下载`、`Documents`、`Hermes`
- 已有 junction：`AppData\Local\Doubao`、`AppData\Local\NetEase` → `D:\MovedApps`
- 默认**不是管理员**；winget 已装（v1.29.380）但**不在 PATH**
- **凡哥真实在用的软件只有三个**（2026-10-20 他亲口）：**ComfyUI（主力）、WPS（办公输出）、剪映（偶尔）**。
  同日又补：「可能 blender 用一用……**可能会让你操控去 3d 建模**」→ Blender 列进「可能要用」。
  **它走 Python（bpy）驱动，跟 .NET 无关**；真要建模时我写 bpy 脚本或用 computer_use 直接操控，不用他手点。
  其余大半是历史残留 → 删软件时判断可以果断，但**每件仍要逐个问**（他定的规矩："一个一个过，你来问我"）。
- 已装软件 **99 个**（ARP 原始 236 条含补丁/重复，别照 236 报）；清单与候选见 `references/software-inventory-2026-10.md`
- **2026-10-20 已清**（别再当他还在）：NVIDIA Nsight ×5、提示词大师、.NET 3.0/3.1/5.0/6.0/7.0/9.0（留 8.0.6/8.0.21）、
  老古董 8 个（Games for Windows LIVE / Marketplace、XNA 3.1 + 4.0、AppLocale、MSXML 4.0、Silverlight、
  Visual Basic/C++ Runtime）、Copilot、Ollama（程序）、LibLibAI、beyond_tunnel、GitHub Desktop、喜马拉雅、每日大赛、
  好用便签（**已重装 8.0.5 恢复，数据完好**）。
  C 盘 33.7G → **39.1G**，D 盘 112.4G → **134.8G**（合计 **27.8G**，其中 Ollama 17G 模型占大头）。
- **Ollama 17GB 模型已删**（2026-10-20 凡哥确认「删」；`D:\Program Files\Ollama` 整个目录清空，
  D 盘 118.24 → 134.76GB。教训：卸载器不删模型，卸完必须量残留目录）
- **2026-10-20 同日另完成（别重复诊断）**：植入自启已清除（`Bctive`/`Wctive`/`security_cad.exe`/
  `jaiwcdzzydmz.exe`）、启动文件夹路径已修复、开机启动精简到「微信/飞书/豆包/便签 + 3 个系统项」、
  GlideX(手机投屏) 与 Virtual Pet(虚拟宠物) 已卸、`\BeyondNetTunnel` 计划任务已删。
  AURA 灯效与风扇监控**凡哥要求保留**。详见 `references/injected-persistence-response.md`。
- **下一步最大单点（2026-10-20 收工时仍剩）**：Chrome 9.5G + 飞书 7.0G + QQ/Tencent 6.9G + WPS 2.0G =
  **25.5G** 还在 C 盘，**必须关掉那四个软件才能搬**（Chrome 的 Service Worker 一项就 3.5G）。
  约到位一次搬完可到 **105G 左右**。汽水音乐 / 剪映 / 直播伴侣 / playwright+camoufox 内核**已搬完**。
- 详细审计数字见 `references/disk-audit-2026-10.md`；社区工具取舍见 `references/community-tools.md`

### winget 必须走全路径

```bash
WG="/c/Users/bobby/AppData/Local/Microsoft/WindowsApps/winget.exe"
"$WG" --version     # → v1.29.380
```
bash 和 powershell 里 `winget` 都 `command not found`（WindowsApps 别名不在 PATH），
**别因此下结论"本机没 winget"**——那只是没登记路径。要长期省事就把 WindowsApps 加进用户 PATH。

## 路径规则（我们定的）

| 东西 | 放哪 |
|---|---|
| 软件本体 | `D:\Program Files\` |
| 软件数据 / 缓存 / 模型 | `D:\AppData\<软件名>\`（已有先例：WeChat、WPS、WXWork、剪映、迅雷） |
| 聊天文件 / 文档 | `D:\Documents\<软件名>\` |
| 素材资产 | `D:\数字资产\{图片资产,视频资产,音频资产,模型资产}` |
| 下载 | `D:\下载\` |
| 临时 / 中间产物 | `D:\Temp` |

## 文档目录树治理（凡哥说「整理某个文件夹」「太乱了」时走这套）

凡哥 2026-10-30 原话：「把 Documents 这个文件夹里的东西全部整理一遍，把类别分好，设计一套有序的文件夹级别，**以后框架就不要动，就像树一样有规律的增长**」。这类活 = **先诊断 → 再出树 → 他点头 → 才搬**，不许直接 mv。

**① 先分清楚「乱的是谁」**（这一步决定动不动手）
- 先扫真实数字：顶层每个目录的**文件数 / 总大小 / 最近修改时间**（扫描脚本见 `references/document-tree-governance.md`）
- **软件缓存 ≠ 他的资料**：本机 `D:\Documents` 6G 里 `xwechat_files`（微信 5G）＋ `WXWork`（企微 1G）是**软件自己管的**，动了丢聊天记录和收到的文件 → **永远不整理**；真正要理的是 `我的文档`（265 个文件 / 44M）
- 回话**第一句先说这条**，否则他以为你要动那 6G

**② 树要「一级固定、只增不改」**（他原话：以后框架不要动）
- 一级带**数字前缀**便于排序：`01_项目 02_团队 03_汇报与方案 04_规范与工具 05_个人 06_图表 07_素材 99_归档`
- **项目并列、不套娃**：他认为「十二时辰」和「南溟岛」是两个**独立项目** → 归哪儿拿不准就**问一句**，别按 IP/父子关系硬套
- 树根放一份 `目录规范.md`：三条判断（是项目？是团队/汇报？是规范模板？）＋铁律（一级不改名不新增）＋本次留痕

**③ 搬：dry-run → 执行 → 日志 → 改引用**（缺一步就翻车）
- 先 `DRY=1` 出全量映射给他看（本次 110 项：16 目录 + 94 散文件）
- 执行时每步记 `[旧路径, 新路径, 是否目录]` 到 `99_归档\整理日志_<时间>.json` —— **这就是回滚依据**
- 同名冲突加 `_dup`；**内容相同的重复稿**（md5 比对）进 `99_归档\重复文件\`（本次 17 份）；旧版本进 `99_归档\<主题>_旧版\`（本次 40 份 v0.1~v0.11 测试稿）
- **搬完必须扫引用**：脚本 / 技能 / DASHBOARD / 台账里写死的绝对路径会全断。按日志把 `旧路径→新路径` 逐条 `str.replace`（`\` 和 `/` 两种写法都换），**扫完所有目标确认 0 残留**才回话（本次 60+ 处）
- 空壳目录（「新建文件夹」这类）搬空后删掉；嵌套同名的（`X\X\`）拍平一层
- 现成脚本：`D:\Hermes\scripts\organize_documents.py`（`DRY=1` 预览 / `DRY=0` 执行）、`fix_paths_after_organize.py`（按日志修引用）

**④ 合并「近义目录」：「管理 / 考核 / 记录」这种抽象名最容易重复建两份（2026-10-30 凡哥：「为什么技术部管理和技术部考核要分开呢？我感觉里面内容都是考核啊」）**
- 现象：同一件事被切成两个目录，一个装**成果**（考核表 v4/v5/v6、下发版），一个装**制度**（归档规则、台账、日报模板）→ 凡哥的直觉是「这些都是考核」，问一句"为什么分开"就是要你合并。
- 正法：**按物件类型分子目录，不按抽象名词分** —— 一个 `考核与绩效\` 下面：`制度与模板\`｜`台账\`｜`月度成绩\YYYY年M月\`｜`日报质量\`｜`99_旧版\`。
- 判据：**一个新同事（或我下个月）能不能一眼知道"新东西放哪一格"**？放不进任何一格 → 说明分法错了，不是格子不够。
- 旧代版本（v4/v5/第一阶段）**别删**，全进该主题的 `99_旧版\`（凡哥会回头问演变）；凡哥否掉的**结论类文件**（这个月被否的判定）也不删，同理留证。
- 合并后同样要**再跑一次引用修复**（路径又变了）＋ 旧空目录 `rmtree` 前先走一遍确认无残留文件。

**⑤ 清理：只删"盘点清单上他点头的那几类"，删完给日志，并且诚实说清省的是什么（2026-10-30 实操）**
- 顺序：**盘点（只统计不删）→ 出表给他逐类点头 → 才删 → 写 `99_归档\删除日志_<时间>.json`（每条带原因）**
- 候选四类就够用：**md5 完全相同的重复稿**（原件还在才删）｜**旧版本号文件**（只留最新一版，如 v0.11）｜**有解压版还留着的 zip**｜**重复的压缩包**
- ⚠️ **别说"清出多少空间"当卖点**：本次删 58 个文件只有 677K，而 `我的文档` 44M 里 33M 是有声书成品 mp3 → 要**主动说"清的是看着乱，不是占地方"**（凡哥在意的是秩序，不是 GB；报个假的省空间预期反而掉信任）
- 反过来，**删得再多也要核"该留的还在"**：删完回读目录树 + 总文件数，把"从 N 个变成 M 个、根目录 0 个散文件"报给他。

**⑥ 这类活全程用脚本，别手敲**：本次三个脚本（`organize_documents.py` 整理 / `merge_kaohe_dirs.py` 合并 / `cleanup_junk.py` 清垃圾）都是 `write_file` 落到 `D:\Hermes\scripts\` 再 `python` 跑 —— **长脚本内联进 `execute_code` 会被静默截断**（本次踩 2 次 `SyntaxError: unterminated string literal`，白跑两轮），中文串里的引号用「」不用 `"`。

## 搬家三层手法（越往下越深，先试浅的）

**① 改软件自己的设置**（最安全）：微信/QQ/WPS/飞书/剪映/浏览器的"文件保存位置""缓存位置"。

**② 环境变量**（缓存类最有效，不用搬目录，改完新生效）：
```bash
powershell -NoProfile -Command "
[Environment]::SetEnvironmentVariable('UV_CACHE_DIR','D:\AppData\Cache\uv','User')
[Environment]::SetEnvironmentVariable('PIP_CACHE_DIR','D:\AppData\Cache\pip','User')
[Environment]::SetEnvironmentVariable('NPM_CONFIG_CACHE','D:\AppData\Cache\npm','User')
[Environment]::SetEnvironmentVariable('OLLAMA_MODELS','D:\AppData\Cache\ollama','User')
[Environment]::SetEnvironmentVariable('PLAYWRIGHT_BROWSERS_PATH','D:\AppData\Cache\playwright','User')
[Environment]::SetEnvironmentVariable('HF_HOME','D:\AppData\Cache\huggingface','User')
[Environment]::SetEnvironmentVariable('TORCH_HOME','D:\AppData\Cache\torch','User')
"
```
设置好后**新开的进程才认**；旧缓存目录要清空才真正回收空间（清之前先确认软件没在跑）。

**③ 目录 junction**（软件完全无感，它以为还在 C 盘）——**junction 不需要管理员**（符号链接才需要）：
```bash
# 顺序：复制 → 验源已空 → 建链（反了就是数据丢失）
robocopy "C:\Users\bobby\AppData\Roaming\LarkShell" "D:\AppData\LarkShell" /E /MOVE /R:1 /W:1 /NFL /NDL /NJH /NJS /NP
cmd //c mklink /J "C:\Users\bobby\AppData\Roaming\LarkShell" "D:\AppData\LarkShell"
```
⚠️ **顺序不能反**：复制 → 核对 → 删源 → 建链。反了就是数据丢失。
⚠️ 搬之前必须确认进程已退出（`Get-Process <名>` / 任务管理器），占用中的目录搬必失败。
⚠️ 出事回滚：删链接用 `cmd //c rmdir "链接路径"`（**只删链接，不删内容**，千万别用 `del /s`）。

**2026-10-20 实战**：11 个目录、合计 **18GB** 搬成功（camoufox_dl 1.22 / codex-runtimes 1.3 /
SodaMusic 5.06 / JianyingPro 2.34 / ms-playwright 2.5 / camoufox 2.39 / webcast_mate 1.97 /
UC 0.7 / Quark 0.65）。两条必须记住的坑：

- **`/MOVE` 遇占用会\"半成功\"**：文件复制过去了，源端被锁的 dll 删不掉 → 源目录不空 →
  如果脚本无条件接着建 junction 会失败，结果是 **C 盘空壳 + D 盘完整副本 + 没有链接**，
  软件读不到数据（webcast_mate 就这样翻的车，当时日志只写\"原目录仍有残留\"，没写\"链接失败\"，
  所以我差点报告成\"搬好了\"）。→ **建链前必须验\"源目录剩余 = 0\"；不为 0 就不建链，明确记成未完成。**
- **占用者可能不是这个软件本身**：webcast_mate（抖音直播伴侣）的虚拟摄像头 dll 被 **Chrome** 加载
  （浏览器把它当摄像头设备用），所以关直播伴侣没用，得关 Chrome 或重启。
  查占用：`Get-Process | Where-Object { $_.Modules.FileName -like '*<关键字>*' }`
- 搬完**逐个核 `LinkType`**：`(Get-Item $p -Force).LinkType` 要等于 `Junction`，否则等于没搬。

**④ 注册表**（少量场景）：已知文件夹重定向在
`HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders`（本机已做过，别再动）。

## 提权：一次确认，之后不打扰

```bash
powershell -NoProfile -Command "Start-Process powershell -Verb RunAs -ArgumentList '-NoProfile','-ExecutionPolicy','Bypass','-File','D:\...\script.ps1'"
```
- **提权前先用不需要管理员的 dry-run / 只读命令把参数验通，再提权一次跑完。** 提权进程的输出拿不回来，
  凡哥被弹一次窗就是一次打扰；本技能诞生那天我在 .NET 上连着写错三次参数，**让凡哥白点了 4 次 UAC 才跑通**
  （`--desktop` 根本不存在 → 真名是 `--windows-desktop-runtime`；两个 runtime 开关互斥；版本号不能跟在 `--all-but` 前面）。
  **教训：凡要报"工具不支持 / 删不掉"，先 `--help` + 不提权的 `dry-run` 试一遍，别拿他的确认框试错。**
- 系统级清理、卸载都必须提权；**UAC 弹窗只能凡哥点**（不是密码，但必须他）。
- 想以后免反复弹窗：建一个 `/RL HIGHEST` 的计划任务来跑维护脚本，之后触发任务不再弹 UAC（建任务本身仍需一次提权）。

## pagefile（🚫 凡哥亲定：不动，别再提议）

2026-10-20 实测：32GB 内存，页面文件被手动固定成 100GB（InitialSize=MaximumSize=102400，自动管理已关）。

**我当天建议"降到 8~16GB、能一次回收 100GB"，凡哥当场否决：**
> 「虚拟内存先保留着不动，comfyui 确实需要虚拟内存做支撑，不然确实跑不动。」

- 这是他的实机经验，**不是可优化项**。以后任何会话都**不许再拿 pagefile 当省空间手段**：
  不写进清理清单、不做进报告建议、不"顺便提一句"。
- C 盘腾空间只走两条路：**搬缓存**（软件自己长的那部分）+ **清过期垃圾**。别砍虚拟内存。
- `hiberfil.sys`（休眠文件）：本机已关，别去开。
- 只有凡哥自己主动说"内存不够 / 想调虚拟内存"，才谈这个；否则回避。

## 清理机制（三档，全留日志，先清单后删）

- **每天（安全级，可不问直接跑）**：`D:\Temp` 超 3 天的、`AppData\Local\Temp`、
  `CrashDumps`、回收站（`Clear-RecycleBin`）、`C:\Windows\Temp`
- **每周（需确认）**：各类 cache 超 30 天（pip/uv/npm/playwright/浏览器）、下载夹超 90 天没动的归档到 `D:\下载\_归档\<年月>\`
- **每月（提权）**：`C:\Windows\SoftwareDistribution\Download`、`Windows\Logs`、
  `DISM /Online /Cleanup-Image /StartComponentCleanup`（**不加 /ResetBase**，加了就不能卸载已装更新）、C 盘体检报告

**绝对不碰**：`C:\Windows\Installer`（删了软件无法卸载/修复，可用专用工具清孤立项）、
`C:\Windows\WinSxS` 手删、`pagefile.sys` 直接删文件（要改设置）、`System Volume Information`。

## 装 / 升 / 卸软件（winget 内核）

```bash
"$WG" list --upgrade-available                                        # 哪些能升
"$WG" upgrade --all --include-unknown --accept-source-agreements --accept-package-agreements
"$WG" install --id <包ID> -e --silent --accept-package-agreements --accept-source-agreements
"$WG" uninstall --id <包ID> -e
"$WG" export -o D:\Hermes\apps-<日期>.json                            # 一台机器导出清单
"$WG" import -i D:\Hermes\apps-<日期>.json                            # 新机器一键装回（团队装机最标准）
```
- 用户级安装（不加 `--scope machine`）通常**不需要提权**；装到 Program Files 才要。
- 卸载残留：winget 卸不干净的，用 `BCUninstaller`（Bulk Crap Uninstaller）批量扫残留。
- **别一次抛一堆软件给他挑**（凡哥铁律：事一件一件过）。

### 非 winget 装的软件：走"批量卸载脚本"（2026-10-20 实证跑通）

本机绝大多数软件是普通安装包，winget 认不全。**别一个个去点控制面板**，照 `templates/batch_uninstall.ps1` 走：

1. **先查卸载命令**（只读）——三处 Uninstall 键捞 `DisplayName / PSChildName / UninstallString / QuietUninstallString`：
   - MSI：`MsiExec.exe /X{GUID}` → 静默 `/X{GUID} /qn /norestart`
   - Inno Setup：`unins000.exe` → `/SILENT`
   - NSIS：`uninstall.exe` → `/S`
2. 写 ps1，**日志硬编码到 `D:\Temp\uninstall_<日期>.log`**（提权进程里 `$env:TEMP` 是管理员环境，别信它），
   每条带退出码，末尾写 `=== 完成 ===`
3. 提权跑（UAC 只能凡哥点 —— **提前一句"框弹出来了，点'是'"**，别让他莫名其妙看到弹窗）：
   ```bash
   powershell -NoProfile -Command "Start-Process powershell -Verb RunAs -ArgumentList '-NoProfile','-ExecutionPolicy','Bypass','-File','<ps1>'"
   ```
4. 提权进程独立、前台拿不到输出 → **轮询日志等完成标记**：
   ```bash
   for i in $(seq 1 40); do grep -q "=== 完成" "$LOG" && break; sleep 5; done
   ```

**退出码对照**：`0` 成功｜`1605` 该程序已不存在（正常，别当失败）｜`3010` 成功但需重启｜
`1618` 别的安装正在跑（重试）｜`1603` 真失败（看日志）

**卸完必须验四样，别只信退出码**：
```bash
# ① 注册表条目消失 ② 安装目录消失 ③ 两个盘实际空间变化 ④ 关键驱动/服务还活着
powershell -NoProfile -Command "nvidia-smi --query-gpu=name,driver_version --format=csv,noheader"
```
本机实测：卸完 5 个 NVIDIA Nsight 后 `C:\Program Files\NVIDIA Corporation` **整个目录消失**
（MSI 清空父目录的正常行为，别慌），但**必须立刻验 `nvidia-smi` 出卡 + `NvContainerLocalSystem` /
`NVDisplay.ContainerLocalSystem` 两个服务 Running**，才有资格说"驱动没事"。

#### .NET 运行时：msiexec 会"假成功"，必须换官方工具

**现象（2026-10-20 实测）**：对 .NET 的 MSI GUID 逐条 `msiexec /X{GUID} /qn`，**23 条全返回 0「成功」，
但 `C:\Program Files\dotnet` 一个字节没少，ARP 条目也全在**。原因是运行时文件由 Burn bundle / 共享组件持有，
卸内部 MSI 条目不动文件；机器上没有 SDK、没有 VS 也不代表能直接卸。
→ **拿退出码 0 当"删掉了"是本技能最容易犯的错，卸载类操作一律要验目录大小。**

正解：微软官方 `dotnet-core-uninstall`（`github[.]com/dotnet/cli-lab/releases` 的
`dotnet-core-uninstall.msi`，约 25MB，装到 `C:\Program Files (x86)\dotnet-core-uninstall\`）。
完整语法与坑见 `references/dotnet-runtime-cleanup.md`，最少记这三条：

```bash
EXE="/c/Program Files (x86)/dotnet-core-uninstall/dotnet-core-uninstall.exe"
"$EXE" list                                                    # 只列它管得了的，管不了的别硬删
"$EXE" dry-run --all-below 8.0.6 --windows-desktop-runtime      # 试跑，不需要管理员
"$EXE" remove  --all-below 8.0.6 --windows-desktop-runtime -y   # 真删，需要管理员
```
- ❌ `--desktop` 根本不存在　❌ `--runtime` 与 `--windows-desktop-runtime` 不能同时给（报 "exactly one of"），分两条命令跑
- 实测效果：`dotnet` 目录 1160MB → 230MB，**回收 930MB**，C 盘 33.7 → 36.6GB；
  剩 5 个工具管不到的孤儿 Core Runtime（341MB）**直接放弃**——手删目录还得连 ARP 一起清，风险大于那点空间。

## 证据手法

- **可疑 exe 先验签 —— 但签名有效 ≠ 没问题（重要纠错）**：
  ```bash
  powershell -NoProfile -Command "(Get-AuthenticodeSignature 'C:\x.exe').Status; (Get-AuthenticodeSignature 'C:\x.exe').SignerCertificate.Subject"
  ```
  ⚠️ **2026-10-20 我在这条上判错过一次，必须记住：** C 根那个乱码名 138MB `jaiwcdzzydmz.exe`，
  验签 `Valid` + `CN="Douyin Vision Co., Ltd."`，我当时下结论「抖音安装包残留，不是毒」。
  **同一天晚些时候发现它是植入事件的一部分**——和 `Bctive`/`Wctive` 是同一分钟（20:23）投放的。
  → **签名只排除"这是病毒"，不排除"这是偷偷塞进来的东西"。**
  判"无害"要多看三样：**① 放的位置正不正常**（系统盘根目录 / Public 目录 = 可疑）
  **② 创建时间有没有和别的可疑物同一分钟** **③ 有没有配套的自启机制**。
  完整判据与清除流程见 `references/injected-persistence-response.md`。
- 报空间一律给**实测 GB**，不给"大概"，并说清是"回收"还是"清掉会重新长回来"。

## 启动项与持久化审计（凡哥说"开机慢"、或清理触及自启时必跑）

一句话跑完整套只读审计：

```bash
powershell -NoProfile -ExecutionPolicy Bypass -File "<技能目录>/scripts/check_persistence.ps1"
# 出 D:\Temp\persistence_audit.txt：启动夹路径 / 三处启动项 / Run+RunOnce / 计划任务 /
# 运行中的非系统服务 / Public 目录 / 浏览器调试端口 / explorer 拉起的进程
```

**为什么必须单独成章**：2026-10-20 清理开机启动时，顺手核了一下"启动文件夹到底在哪"，
就挖出一整套 2026-07-12 投放的隐蔽自启（改注册表把启动夹指向 `C:\Users\Public\Documents\Wctive`、
用爱奇艺签名的 `security_cad.exe` 伪装、目录加 DENY 删除锁）。**完整证据链与清除命令见
`references/injected-persistence-response.md`。**

### 四条硬知识（记这四条就够用）

1. **启动夹路径要回注册表核，不能信 `GetFolderPath('Startup')`**
   —— 那个 API 是被注册表值算出来的，注册表被骗它也跟着骗你。
   正常值 = `%USERPROFILE%\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup`；
   出现 `Public` 或末尾带 `\u0000` 就是被动手脚了（NUL 是规避手法，打印时要 `-replace "`0",'<NUL>'` 才看得见）。

2. **只查 Run 键会漏**。持久化至少五处：启动文件夹 / Common Startup / Run+RunOnce / **计划任务** / 服务。
   `Win32_StartupCommand` 的 `Location` 字段直接告诉你在哪一处。
   本机实例：`beyond_tunnel` 就是靠**计划任务** `\BeyondNetTunnel` 自启的，Run 键里根本没有。

3. **ACL 锁：显式 DENY 优先于管理员权限**，`Access denied` 删不掉时先看 `icacls`。
   看到 `BUILTIN\Users:(OI)(CI)(DENY)(DE,DC)` 就按这个顺序拆：
   `icacls /remove:d "BUILTIN\Users" /t` → `/reset` → `takeown /r /d y` → `/grant "*S-1-5-32-544:(OI)(CI)F"` → 删。
   **顺序不能换，`/remove:d` 必须第一步。**

4. **`--remote-debugging-address=0.0.0.0` 是安全漏洞**，不是普通启动项：
   绑全网卡等于**局域网谁都能接管浏览器**。本机 `EdgeDebug` 就是这个，已删；
   真要调试改成 `127.0.0.1`。

### 关启动项的分寸（凡哥 2026-10-20 定的口径）

- **他点名的才留**：微信 / 飞书 / 豆包 / 好用便签。其余第三方自启一律取消。
- **但系统/驱动级别当垃圾关**：`RtkAudUService`（Realtek 声卡，关了**可能没声音**）、
  `SecurityHealth`（Windows 安全中心）、`Hermes_Gateway`（Hermes 自启）——**默认保留并说明理由**。
- 动手前把要保留/要关的两列**先报给他过一遍**（他这次就是自己点的名），别自作主张。
- 取消用"隔离"不用"直接删"：快捷方式移到 `D:\Documents\_隔离_<日期>\`，Run 键值先写进
  `run-backup.txt` 再删 —— **他随时能反悔**。
- 删软件后**回头扫计划任务**，否则留一堆指向空路径的僵尸任务（本机 `\BeyondNetTunnel` 就是这样）。

## 诚实边界（凡哥重视，别糊弄）

- **C 盘不可能"一点别的都没有"**：pagefile、休眠文件、系统更新缓存、驱动、组件库（WinSxS）、
  系统还原快照是系统本身，删了系统坏；只能压到很小。**能承诺的是：除了这些，软件/缓存/模型/素材/聊天记录都不留 C 盘。**
- 缓存搬家 ≠ 永久消失：软件还会长新缓存，所以"搬家 + 定时清理"必须一起上，光搬不治会反弹。
- 内部工艺跑通 ≠ 商业可用；涉及授权/发布的单独核。

## 坑（都踩过或实测过）

- **`winget` 在 bash/powershell 都找不到** → 是 PATH 没登记，走 WindowsApps 别名全路径，不是没装
- **MSYS 路径不转译**：`mklink` 是 cmd 内建 → `cmd //c mklink /J "C:\..." "D:\..."`，路径用 `C:\` 原生写法
- **C 盘剩余空间要自己算**：`C: free 33.7GB / total 298.7GB` 这种行是 bash 认不出的，用 PowerShell 取
- **桌面不一定在 C:\Users\x\Desktop**：本机桌面是 `D:\admin桌面`，必须用
  `[Environment]::GetFolderPath('Desktop')` 取真实路径，不能拼路径猜
- **D 盘可能已经被搬过一轮**（本机 `MovedApps` / `AppData`）→ 动手前先用
  `search_files (target='files', path='D:/')` 看 D 盘顶层 + 查已有 junction，否则两套规则打架
- **扫描别只扫 AppData**：ProgramData 里 NVIDIA 一家就 5.9GB，`Windows\Installer` 7.2GB、WinSxS 12.9GB 都要看
- **注册表 `EstimatedSize` 虚高 2~3 倍，一次都别信**。2026-10-20 连踩两次：报 6.9GB 实际回收 4GB；
  报 2.3GB 实际只有 1.13GB。要报数字就**先量目录**：
  `Get-ChildItem -Recurse -File -Force | Measure-Object Length -Sum`。
  报错了当场认、当场纠（凡哥认这个账），别事后圆。
- **ARP 条目数虚高一倍多**：原始 236 条里有补丁和重复 → **真实软件只有 99 个**。报数量前先过滤
  `SystemComponent`、`ParentKeyName`、`KB\d+`，并注意同一 MSI 会有 `{ABC}` / `{abc}` 两条大小写 GUID
  （卸掉一条，另一条回 `1605` 是正常的，不是失败）。
- **删软件前先看它装在哪个盘**：本机大半软件已在 D 盘，删了不省 C 盘。回收空间要**分盘报**
  （C 多少 / D 多少），不然凡哥会觉得你在忽悠。
- **性价比要主动算**：.NET 旧运行时 12 个实测只有 1.13GB、删旧的省 850MB → 为这点空间冒"某软件打不开"
  的风险不值。这时要**主动说"这笔不划算"并给 A/B 两条路**，别为了走完清单硬推。
  （凡哥要的是判断力，不是一个把清单勾完的执行器。）
- **判"哪个软件还在用"看数据不看嘴**：浏览器读 `User Data\Default\History` 的 `LastWriteTime`
  （实测 Chrome 当天、Edge 1 天前、UC 当天还更新了书签 → **四个浏览器全在用，一个都不能删**）。
  其他软件可用安装目录最后写入时间当旁证。
- **Chrome `User Data` 9.7G 的真实构成**（实测）：Service Worker 3.5G、Default 整目录 5.4G
  （Cache 432M / Code Cache 306M / IndexedDB 484M / Extensions 608M），**书签+历史只有 7MB**。
  → 清缓存安全（不动 `Network\Cookies`，登录态保留，能回收约 4.2G）；要根治就整目录 junction 到
  `D:\AppData\Google\Chrome`。**别把"删浏览器"当省空间手段，他三个都在用。**
- **流氓软件特征**（实例：每日大赛）：exe **无数字签名** + 目录里有 `app_install_plugin.dll`（推广应用安装）
  + `analytics_sdk_plugin.dll` + 版本 1.0.0 + 查不到的小公司。删前先验签，删后看有没有同批兄弟。
  本机 `D:\下载` 还留着这批原始安装包（mrds / Luzi / Ximalaya / UCWin / td-setup），能反推是谁装进来的。
- **认不清安装器类型 = 静默失败返回 0**：`unins000.exe` 是 Inno（用 `/VERYSILENT /SUPPRESSMSGBOXES`），
  `uninstall.exe` 多是 NSIS（用 `/S`）。**给 Inno 传 `/S` 会返回 0 但什么都不做**（好用便签就这样，
  注册表条目还在）。不确定先查 `(Get-Item $f).VersionInfo | Select FileDescription, CompanyName`。
- **卸载器不删大文件残留**：Ollama 卸完 `D:\Program Files\Ollama` 里还躺 17GB 模型（6 个 blobs 文件）。
  卸完务必逐个量残留目录大小，别只看"程序删掉了"。

## 分工

- 本技能：**磁盘/路径/清理/装升降卸软件/系统设置**（这台机器怎么治理）
- `local-tool-provisioning`：**装哪个工具、装哪个 venv、依赖会不会打架**（装东西的决策树）
- `comfyui-env-ops`：ComfyUI 版本/模型/CUDA 那摊
- 支撑文件：`scripts/scan_disk.ps1`（只读磁盘侦察）、`scripts/check_persistence.ps1`（启动项/持久化只读审计）、
  `templates/batch_uninstall.ps1`（批量卸载脚本模板）、
  `references/software-inventory-2026-10.md`（99 个软件清单、已清/待清、判断依据）、
  `references/disk-audit-2026-10.md`（首次审计实证）、
  `references/community-tools.md`（社区方案取舍与"已死"名单）、
  `references/dotnet-runtime-cleanup.md`（.NET 假成功实证 + dotnet-core-uninstall 语法坑，含三次参数写错记录）、
  `references/data-bearing-app-recovery.md`（带用户数据的软件被误删后怎么救回：备份取舍 → 挂代理取官网真链 →
  验签 → 静默装回原路径 → 回填 data/image → 看程序日志确认读库）、
  `references/injected-persistence-response.md`（被植入的隐蔽自启：五项检测 / 签名有效≠安全 /
  ACL DENY 删除锁的拆除顺序 / 修复启动夹路径 / 善后三件事）、
  `references/document-tree-governance.md`（**文档目录树治理**：扫描脚本 / 2026-10-30 我的文档实测数字 /
  8 大类树 / DRY+规则表迁移 / 按日志修引用 / md5 去重 / 拍平嵌套 / 「别动清单」= 微信·企微缓存）
