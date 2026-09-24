---
name: project-topology-diagrams
description: 凡哥要画/更新项目拓扑图时用。本地 draw.io 生成 + 官方 CLI 出图（WPS pptx 备选）。
version: 1.0.0
author: 小南
license: internal
metadata:
  hermes:
    tags: [拓扑图, WPS, pptx, 项目管理, 日报]
    related_skills: [dashboard-tree, project-dashboard, dual-agent-memory-sync]
---

# 项目拓扑图（本地生成 · 树形 / WBS）

凡哥的项目进展拓扑图：**本地画、按日报更新、最下方是待办事项**。
豆包（飞书）不再负责画图（2026-09-20 起工作交接给小南）。

**路线现状（2026-09-23 定，别再搞混）**：
- **现役**：`gen_topology_tree.py` → **draw.io 单页树形图**（WBS 编号 + 内置树布局 + 正交连线）→ 出 PNG/SVG/PDF。规则见「拓扑图到底是什么」「WBS 成熟画法」两节，命令与格式细节见 `references/drawio-cli-and-format.md`。
- **备选**：`gen_topology_pptx.py` → WPS 演示 `.pptx`（老路线，字会缩，仅备用）。
- **已废**：曾做过的「draw.io 四页版」（总览/模块/日报/版图）＝ PPT 分页思路，**凡哥 2026-09-23 否决**，脚本与产物已删；别再走这条路。

## When to Use
- 凡哥说"画拓扑图 / 更新拓扑图 / 把豆包的工作接过来 / 补齐 WPS 拓扑图功能"
- 凡哥说"按日报更新"、给了新的项目口径/卡点/日期
- 要给外部（需求方、CEO）看项目全貌

## 先定死的两个事实（2026-09-20 实测，别再重复找）
1. **WPS 桌面版没有独立的本地流程图组件**。`D:\Program Files\WPS Office\<ver>\office6\addons` 里与本话题相关的是 `kpromeprocesson`（＝WPS × ProcessOn，**在线**版，要会员）等 `kproME*` 应用 → **"去 WPS 官网下载流程图板块"这条路不存在**，不要去找安装包。
2. 因此本地方案 = **python-pptx 生成 `.pptx`**，图里全部是**原生形状**（圆角矩形/箭头/文本框）→ 在 WPS 演示里双击就能改字、拖框、连线；**本地、离线、免登录**。

## 路线二（2026-09-23）：draw.io Desktop 本地版
（CLI 用法与官方依据本节仍然有效；**生成脚本已换成树形版**，见「拓扑图到底是什么」「WBS 成熟画法」；命令细节见 `references/drawio-cli-and-format.md`）

**为什么换**：WPS 演示一张纸塞不下、字缩得看不清 → 换 **draw.io Desktop**（免费、开源、完全离线、中文界面、无限画布、多页、字号自选）。
软件：**微软商店官方版「draw.io Diagrams」**（发布方 draw.io Ltd，`9MVVSZK43QQW`），程序在 `C:\Program Files\WindowsApps\draw.io.draw.ioDiagrams_31.4.5.0_x64__1zh33159kp73c\app\draw.io.exe`（**PowerShell 能调它的 CLI**，bash 受 ACL 限制调不了）。

| 项 | 内容 |
|---|---|
| 生成脚本 | **现役** `D:\Hermes\scripts\gen_topology_tree.py`（树形，单页）｜旧 4 页脚本 `gen_topology_drawio.py` **已废**（PPT 分页思路，凡哥 2026-09-23 否决） |
| 产物 | `D:\Documents\我的文档\拓扑图\项目拓扑图_WBS.{drawio,png,svg,pdf}` |
| 出图命令 | `& $EXE --export --format png --page-index 1 --scale 2 --output 拓扑图_p1.png 项目拓扑图_xxx.drawio`（逐页导） |
| 常用参数 | `--size page` 导整页 / `--format png|svg|pdf` / `--all-pages`（只对 PDF、HTML 有效） |

**官方依据（生成前必读，禁止靠试错猜格式）**
- 规范 + 14 条校验清单：https://www.drawio.com/docs/reference/diagram-generation/style-reference/
- 官方 XML 参考：https://github.com/jgraph/drawio-mcp/blob/main/shared/xml-reference.md
- 要点：必须有 `<mxCell id="0"/>` 与 `<mxCell id="1" parent="0"/>`；内容元素 `parent="1"`；顶点 `vertex="1"` + `<mxGeometry x y width height as="geometry"/>`；边 `edge="1"` + `<mxGeometry relative="1" as="geometry"/>`；id 在单页内唯一；用未压缩 XML。

**踩坑（2026-09-23，写死）**
- **CLI 能导出 ＝ 文件合法**。当时文件本来就是对的，我却在交互窗口里"改一个变量→开一次窗→截一次图"试了十几轮（还因自己用正则剪 XML 切坏了格子，得到两次假失败）→ 凡哥纠正：**不知道就第一时间找依据**。
- 交互窗口截图空白 ≠ 文件坏（窗口/实例状态问题）。**验证一律走 CLI 导出**，不开窗口截图猜。
- 别用正则从 .drawio 里剪 `<mxCell>`（会在 `<mxGeometry ... />` 处截断）→ 用 `xml.etree.ElementTree`。

---

## 图的硬规则（凡哥 2026-09-20 定，长期有效）

1. **模块制**：每个项目在进行时拆成**功能模块**；搭建/开发**先有框架，再一个一个实现**。
2. **模块卡必须写**：`开始时间 / 预计交付时间 / 状态`。
3. **超出预计交付时间 → 必须写**：`⚠卡点在哪 / 解决方案 / 再次交付时间`（三件套缺一不可）。
4. **图的最下方固定「待办事项」区**（编号列，写明谁做）。
5. **更新源 = 四人的每日日报**（小何 / 小吴 / 小李 / 小唐；2026-09-23 起四人当日 18:00 后交齐）→ 读图后按「工作日期」入台账与树。
6. **状态四色图例**：✅已完成（绿）/ ▶进行中（蓝）/ ⚠卡点（橙）/ ○未开始（灰）。
7. **易混口径必须显式区分**，例：`OPC 平台的应用需求未定` ≠ `影剧工坊的卡点`；**已独立的项目必须独立成卡**，不能继续挂在原父节点下（影剧工坊就是这样从 OPC 里拆出来的）。

## 拓扑图到底是什么（凡哥 2026-09-23 纠正 · 最高优先）

**拓扑图 ＝ 一个大领域不断往下拆分成模块的「树」**，不是 PPT 内容分页，也不是把日报原文堆成段落框。

- **一张画布、一棵树**：根（技术部 · 项目主管）→ 项目 → 功能模块 → 子模块/节点，统一往同一方向展开。
- **每个框只写短标签**：`模块名 + 状态`（例：`用户与社区 ✅ 已完成`）。**卡点也只是一句短语**，不写段落（段落＝内容页，已否决）。
- **状态四色**：✅已完成 / ▶进行中 / ⚠卡点 / ○未开始。
- **每个节点必须标负责人**（凡哥 2026-09-24 要求）：标签末尾统一加 `｜ 责任人`（多人写 `｜ 小何 · 小吴`）；**没人认领的写 `｜ 待指派`**；图例里放人名对照 `小何＝何锦波 · 小吴＝吴伟俊 · 小李＝李林 · 小唐＝唐光辉`。**归属以日报署名为准**（凡哥 2026-09-24：「日报是谁写的就是谁做的」）——谁在日报里写了这项，责任人就是他；**不要按岗位去推**（别拿「后端=小何 / 前端=小吴」套）。日报没写到的节点＝「待指派」；项目主干只用凡哥亲口说过的分工。
- **待办事项 = 树最下面的一个分支**（凡哥原规则：图最下方放待办）。
- **生成脚本**：`D:\Hermes\scripts\gen_topology_tree.py`（树数据写在脚本顶部 `TREE` 里，改数据重跑）。
- **零重叠是硬指标**：脚本自算「整齐树」布局后**必须通过两两重叠断言**（打印 `重叠对数 0`）才允许出图 —— 根治"内容被盖住"。
- **层间距必须 > 上一层框宽**（否则父子框会横向压住，2026-09-23 被断言查出来）。
- **交付格式**：`.drawio`（可编辑源）+ **PNG**（发飞书/聊天）+ **SVG / PDF**（矢量，放大不糊，给外部看/打印）。

### WBS 成熟画法（凡哥 2026-09-23 要我"查成熟做法"后落地）

| 规范 | 来源 | 落地方式 |
|---|---|---|
| **层级编号（账目编码）** 1 / 1.1 / 1.1.1 | Microsoft Project / Dynamics 365 WBS 文档 | 每个框前加编号 → **层级靠编号就能读，不必死盯连线** |
| **100% 原则**；**支路不必对称**；层级 4–6 层够用（>20 层过度） | PMI / WBS 权威词条 | 拆到能估准的层级即停 |
| **同级对齐 + 颜色区分分支/状态** | WBS 绘制指南（ProcessOn / Atlassian） | 同级同列；状态四色 |
| **正交折线 + 无箭头**（分解关系不是流程） | WBS 图惯例 | `edgeStyle=orthogonalEdgeStyle;endArrow=none;strokeColor=#909090;strokeWidth=1.2` |
| **连线交给布局引擎，不手画** | draw.io 官方布局文档（ELK 在大/深嵌套图上正交连线更整洁） | `--layout horizontalTree` |

**一键流程（2026-09-23 实测通过）**
```
python D:\Hermes\scripts\gen_topology_tree.py --layout
# 骨架 .drawio（含零重叠断言）→ 内置树布局重排 → 导出 PNG / SVG / PDF
```

**实测坑**
- ⚠ **ELK（elkLayered）是联网加载的**：本机 GitHub/CDN 不通时 `--layout` 会**卡死**（不是慢）→ 离线只用内置预设 `horizontalTree / verticalTree / organic / radialTree`。
- 跑 CLI 前先 `Stop-Process -Name draw.io`（已开的实例会让 CLI 挂住）。
- 布局引擎会**重排坐标** → 布局后要**再跑一次重叠断言**（脚本两步都验）。
- `--size diagram` 按内容裁剪，不留白；PNG 加 `-s 2` 出 2 倍图。

### （历史）旧分页做法 —— 仅作参照，已被上面替代

| 页 | 内容 | 何时更新 |
|---|---|---|
| **1 · 总览** | 项目 / 模块 / 状态 / 时间行 / 卡点三件套 + 底部待办事项 | 每次日报 |
| **2 · 日报明细** | 当天各人日报的原文要点（今日完成 / 卡点 / 解决方法）+ 处理说明；**逐日累积** | 每次日报 |
| **3 · 集团版图 · 我们的位置** | 集团产业闭环（企业介绍）+「我们的活落在哪一格」映射表 + 今后重点 + 待确认口径 | 口径变化时 |

- 日报明细/集团版图**不再作为拓扑图的页**：日报明细归台账（`任务台账_2026-09.xlsx`），集团背景留在 DASHBOARD 10.17 与 `references/`。
- **集团背景是必读层**：画图、排优先级、判断"这活值不值得做"之前先对齐集团版图 → 详见 `references/group-context-and-report-parsing.md`。
- 新增页不要在旧脚本上手画：在生成脚本里 `prs.slides.add_slide(...)` 追加，helper 全部带 `s=` 参数（默认首页），**每页都要跑一次越界自检**。

## 日报解析规则（小何/小吴 → 图的字段）

1. **日报是三段式**：`今日工作完成情况` / `遇到的工作卡点` / `解决方法` → 依次映射到 模块进展、⚠卡点、解决方案。
2. **按「工作日期」归档，不按提交日期**（凡哥 2026-09-23 纠正，最重要的一条）：
   - 小吴：**当日 18:00 左右提交**（内容＝当日）；小何：**次日上午补交前一日**（例：标题写"09-23 09:56 提交"的那份，内容其实是 **09-22** 的工作）。
   - 图 / 台账 / 第 2 页一律按**内容工作日**归，不按提交日期归。
   - 凡哥一次会发**多份（两天的量，如 4 份 = 2 天 × 2 人）**→ 先按工作日分组，再逐人核对；**看着像"重复"的那份往往不是重复，先问再丢**。
3. **人名口径**：小何＝**何锦波**（后端 · 整体框架/接口/数据）；小吴＝**吴伟俊**（前端/UI）；小李＝**李林**（大模型上下文 · LangGraph）；小唐＝**唐光辉**（多 agent 体系；凡哥 2026-09-23 明确「**是姓唐，我打错了**」——他此前打成"堂光辉"，**以"唐"为准**）。图与台账统一用"小何/小吴"。
4. **术语纠偏**（按凡哥口径写，不照抄日报）：智题分→**智提分**；影视工坊→**影剧工坊**；产品名 **浪浪椰 APP**（集团介绍里可能印成"浪浪耶"，**以"椰"为准**）。
5. **卡点会换**：新日报的卡点与图上旧卡点不一致时，**先问"是同一问题的不同说法，还是变成了新问题"**，别默默替换。
6. 日报没给的字段写 `待定` / `待更新`，并在回复里列出"还差你一句话"的清单（凡哥要看缺什么，不要含糊过去）。

## computer_use 实操（打开 WPS 验收、读飞书）

- **click 之前必须先 capture**：否则直接报 `No active window — call capture() first`。
- capture 的 `element bounds` 是 **native desktop 坐标**（WPS 窗口实测约 1.76× 截图像素）→ **能读就别点**；必须点就先 `mode='som'` 拿元素、点完**再 capture 复核**是否落地。
- **多页目视验收**：点左侧幻灯片缩略图切页，capture 后从状态栏 `幻灯片 N / M` 确认当前页，再核对版面。
- 文件被 WPS 打开时锁着删不掉 → 让凡哥**关掉标签页**再清旧版本。

## 画布容量上限 → 工具升级（2026-09-23 凡哥提出）

**症状**：内容逐日累积后，PPT 一页（13.33×7.5 in）塞 55+ 个形状 → 字号被迫压到 6pt 以下。凡哥原话：「这个幻灯片的方式，**一张纸内容现在感觉盛不下了，字太小也看不清**，我记得是由专门做拓扑图的本地软件啊？你去找找，**最好找不要钱的那种软件**」。

**判断阈值（经验值）**：单页正文需要 <6pt 才放得下 = 已超载。**零成本即时动作＝拆页**（一项目一页 / 明细独立成页），现有生成脚本加一页即可，不必等新工具。

**根治方案 = 无限画布的本地免费软件**（核到官方版本与通道，2026-09-23）：
1. **draw.io Desktop（＝diagrams.net）★ 首选**：免费 + 开源 + **完全离线**；**画布无限**（不用再缩字）、**一个文件多页**、可缩放、导出 PNG/PDF 高清；文件本质是 **XML（`.drawio`）** → **可像 `gen_topology_pptx.py` 一样程序化生成/更新**（凡哥发日报→改数据→重跑），同时他能在软件里直接拖框改字。官方最新版 **v31.4.5**（2026-09-08 发布，GitHub `jgraph/drawio-desktop`）。
2. **yEd Graph Editor（yWorks）**：免费（官网写明**商用也免费**）、离线；强项＝**一键自动排版**（层级/树形布局，把乱图理顺）。版本 **3.25.1**。
3. 不再考虑：WPS×ProcessOn 在线版（要会员）、亿图图示（收费）。

**获取通道（本机网络实测 · 2026-09-23 已装好）**：GitHub Releases 直连常超时（`github.com` 不通、**`api.github.com` 通**——查版本/资源名用 API 就够）。⚠️ **`winget install JGraph.Draw` 实测失败**（它的清单 URL 指向 github.com，同样被墙，报 `InternetOpenUrl() failed 0x80072efd`）→ **走通的命令是商店源**：`winget install 9MVVSZK43QQW --source msstore --accept-package-agreements --accept-source-agreements --disable-interactivity`（发布方 draw.io Ltd，约 80s）→ **已装好并实测**：能双击打开 D 盘本地 `.drawio` 文件（中文界面）。**装软件先问凡哥**；下载件核验（size + sha256 + Authenticode）与镜像兜底见 `hermes-network-proxy` 的 `references/blocked-github-downloads.md`。
→ 对比表、迁移做法与画布规则见 `references/diagram-tooling-upgrade.md`。

## 标准做法（照做即可，别手画）
0. **现役＝树形脚本**：`D:\Hermes\scripts\gen_topology_tree.py` → 改顶部 `TREE` 数据 → `python gen_topology_tree.py --layout` → 一条命令走完（骨架＋重叠断言＋内置树布局＋画布重设＋PNG/SVG/PDF）。命令与坑见 `references/drawio-cli-and-format.md`。
1. **旧脚本（仅备用）**：`D:\Hermes\scripts\gen_topology_pptx.py`（WPS 版；顶部注释含全部规则与版本变更史；`DATA`/`box()`/`arrow()` 结构，改数据重跑 3 秒出图）。
   - 新机器/新环境：用 `templates/topology_slide_skeleton.py` 起手（同结构的最小骨架）
2. 输出到 `D:\Documents\我的文档\拓扑图\项目拓扑图_YYYYMMDD[_vN].pptx`。
3. **校验**：跑形状越界检查（脚本内会打印"形状数/越界数"；判据＝每个形状 `x≥0 && y≥0 && x+w≤画布宽 && y+h≤画布高`）。
4. **打开**：用 WPS 演示的 exe 直呼，别用文件关联：
   `cmd /c start "" "D:\Program Files\WPS Office\<ver>\office6\wpp.exe" "<文件.pptx>"`
   （`start "" "文件.pptx"` 实测可能不弹窗口）
5. **目视验收**：`computer_use capture(app='wps.exe', mode='som')` → 拿 `screenshot_path` → 核对版面。
   **注意**：窗口缩放会让主视图只显示一部分、右列看起来"被裁"——**先看左侧幻灯片缩略图**确认整体，别误判成图错了。
6. 交付时同时给 **.pptx（可编辑）** 和 **截图 PNG（直观看）**；说明导出图片/PDF 用 WPS 演示「文件 → 输出为图片/PDF」。

## 数据从哪来（日报）
- **飞书里没有"汇报"板块**（左侧导航实测只有：消息/豆包工作/云文档/推荐/多维表格/视频会议/工作台/应用中心/通讯录/日历/飞行社/更多/任务/收藏/知识库）。日报入口 = **「汇报」机器人会话**（会发"汇报提交统计"）或工作台里的「汇报」应用。
- **读飞书窗口（已验证可靠）**：`computer_use capture(app='Feishu.exe', mode='ax')` → 完整文字落在响应里的 `elements_file` 指向的 JSON（**读那个 JSON**，别只看被截断的响应文本）。
- **点击飞书仍是弱项**：裸 `element_index` 会被拒（要求 `element_token` 或 `snapshot_id`+`element_index`）；坐标点击的映射不可靠（可能落空或误切会话）。**优先请凡哥打开目标页、我只读**；必须动手就先说明"会切前台"。
- 豆包写共享文件那条通道见 `dual-agent-memory-sync`（A 区口径 / B 区豆包写入 / 按需读取，不做轮询）。

## 坑（都踩过）
- `pip install python-pptx` 可能没装 → 先 `python -c "import pptx"` 探一下。
- `RGBColor(0xFBFCFE)` 会 `TypeError: missing 2 required positional arguments` → **必须三个参数** `RGBColor(0xFB,0xFC,0xFE)`。
- **WPS 打开中的 pptx 锁文件删不掉** → 旧版本（v1/v2…）让凡哥**关掉标签页后**再删，别硬删；同时提醒他只留最新版。
- **数据不确定就别写死**：日期/结果未知时写 `待定` 或 `⚠…待更新`（例：演示日已过 → 标"演示日已过·结果待更新"），**不脑补**。
- **口径冲突要摆出来问**，不自己拍：例"① 标 ✅已完成 但内含 ⚠卡点"这种矛盾，指出来让凡哥定（他默认会改成"▶ 进行中 · 第一版可演示"）。
- **批量改生成脚本：用 Python 字符串替换逐条自检**（每条打印 `OK`/`MISS`）。脚本 300+ 行、一次要改十几处时**别连发多个 `patch`**：`patch`/`write_file` 被中断（`[Command interrupted]`）后**部分改动可能已落盘**——接着改必然 `MISS`。**中断后先核验实际内容**（替换自检 / `search_files`），再续改；改完 `py_compile` 通过、再跑生成 + 越界自检。
- **旧版本用完就清**：输出目录只留最新版；删之前看有没有 `~$<文件名>` 锁文件（＝正被 WPS 打开）——有锁就让凡哥关标签页，别硬删。
- 改完图**顺手更新口径源**：`DASHBOARD.md` + 共享文件 A 区 + git 提交（拓扑图是给外部看的东西，口径必须和总控台一致）。
- **写总控台/共享文件的字符串替换必须"先断言锚点、后核验落盘"**（2026-09-23 踩过）：锚点写错时 `str.replace()` **静默无效**，脚本照旧打印"已更新"、git 也报 `nothing to commit`——**口径其实没写进去，但看起来成功了**。做法：① 改前 `assert 锚点 in s` ② 改后断言新标题/关键词确实存在 ③ 提交输出里**不该出现 `nothing to commit`**（一出现就说明这批没落盘）。

## 三个产物的分工（别搞混）
| 产物 | 用途 | 载体 |
|---|---|---|
| **项目拓扑图**（本技能） | 项目全貌/模块/卡点/待办/**负责人**，给外部看 | **draw.io 树形（WBS）**：`项目拓扑图_WBS.drawio` + PNG/SVG/PDF（本地） |
| 树形总控台 | 我自己的知识总览 | `dashboard-tree.html`（git 同步） |
| 工作总控台 | 真相源/长期条款 | `DASHBOARD.md` |

## 支撑文件
- `references/drawio-cli-and-format.md` — **现役路线必读**：CLI 命令（PowerShell 调商店版）、离线布局预设（ELK 会卡死）、布局后画布重设、格式要点与三层验证配方
- `scripts/drawio_verify.py` — 一条命令校验：节点/连边计数 + 零重叠断言 + 画布包含 + SVG 关键词核对
- `templates/topology_slide_skeleton.py` — 最小可跑骨架（换机器/新环境起手用：四色图例 + 模块卡 + 卡点三件套 + 待办区）
- `references/wps-feishu-facts.md` — 现场实测事实：WPS 组件清单（为什么没有本地流程图）、pptx 打开命令、生成/验收固定套路、飞书读取与点击现状、卡点排查四步
- `references/group-context-and-report-parsing.md` — **集团版图（企业介绍要点）+「我们的活落在哪一格」映射表 + 日报三段式解析 + 人名/术语口径 + 挂着的待确认口径**（画图前必读）
- 关联技能：**multi-agent-architecture** — 团队镜像 agent / LangGraph 全局图·子图 / 上下文溢出治理（影剧工坊卡点的技术方案、李林/唐光辉两位新同事的方向都记在那）

## 验证
- **树形（现役）**：`python gen_topology_tree.py --layout` 先打 `骨架重叠对数 0`、布局后再验一次；或 `python scripts/drawio_verify.py <布局后.drawio> --svg <导出.svg> --expect "关键词,…"` → `PASS`
- 旧 WPS 版：`python gen_topology_pptx.py <out>` 输出 `形状数/越界数=0`；WPS 打开截图无错位；待办区、卡点三件套、模块时间行都在
- `DASHBOARD.md` 与共享文件 A 区已同步同一条口径
