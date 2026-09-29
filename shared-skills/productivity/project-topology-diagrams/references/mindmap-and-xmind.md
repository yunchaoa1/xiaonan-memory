# 思维导图路线（XMind）与「拓扑图 vs 思维导图」知识库

> 2026-09-28 建，同日晚实测跑通"自动导入 + 存档 + 校验"全链，补第 7、8 节。
> 本文是官方依据的浓缩版（博赞规范 + XMind 官方文档/价格页），动手前先读这页，别猜。

## 1. 两者到底差在哪（做错东西的根因）

| | 拓扑图（WBS 式，本技能另一条线） | **思维导图（凡哥真正要的）** |
|---|---|---|
| 形态 | 方框树，正交折线，可编号 | **中心主题发散**，**曲线分支** |
| 视觉 | 统一细灰线 + 状态四色 | **一线一色**（每条主分支一色、分支内同色系）、近中心线粗大、往外递减 |
| 内容 | 模块名 + 状态 + 负责人（短标签） | **关键词式**（一线一词，忌长句）；状态用图标（✅▶⚠○） |
| 工具 | draw.io（`gen_topology_tree.py`） | **XMind**（专业软件） |

**思维导图规范（博赞/Tony Buzan 体系，中文通行版）**：
1. 中心主题居中（或单侧起），用图形/椭圆体现
2. **一线一色**：每条主分支一种颜色，分支内子节点同色系
3. **分支用曲线**（自然弯曲，不画直线折角）
4. **关键词**：一个节点一个词/短语，不长句
5. **粗细/字号渐变**：靠中心越粗越大，往外递减
6. 层级 3–5 级为宜；一级分支 3–7 条
7. 颜色/图标突出重点；同级间距一致、不重叠
8. 布局形态：有机放射型 / 树状型 / 逻辑型（单侧）——内容多时**单侧逻辑型**最清晰

## 2. XMind 官方事实（2026-09-28 从 xmind.cn 价格页与用户手册核）

- **版本**：Windows x64 安装包 `Xmind-for-Windows-x64bit-26.05.01107`（2026-09-08 构建，181MB）；下载入口 `https://xmind.cn/zen/download/win64/`（落到 `dl3.xmind.cn`，国内直连可用）
- **安装位置（本机）**：`C:\Users\bobby\AppData\Local\Programs\Xmind\Xmind.exe`（Electron 版；后台检测/启动都用这个路径）
- **一订阅 = 购买者本人 5 台电脑 + 5 台移动设备**

| | 免费版 ￥0 | Pro ￥380/年（188/3个月） | Pro+ ￥358/年（促销） |
|---|---|---|---|
| 本地导图/节点 | 不限 / 无限 | 不限 | 不限 |
| 导出 | PNG / PDF（**带水印**） | **无水印** PNG/SVG/PDF/**Markdown/OPML/Word/Excel/PPT** 等 10+ | 同 Pro |
| 额外 | 5 张幻灯片、10 张在线导图 | 自定义风格、按主分支自动拆分、插图片附件、PNG 2x/3x、密码保护 | 实时协作、云存储、甘特图、任务（优先级/分工/进度）、AI 500 次/月 |

- **报销**：官网「付款记录 → 申请发票」可开电子普通发票（14 天内发邮箱）
- **退款**：官网购买**一年及以上**订阅享 **7 天无理由退款**；连续包季不支持退款且默认自动续订
- **不提供个人永久买断**；企业方案（10 套起）有永久授权序列号

## 3. 导入导出（官方支持，别手打节点）

**导入**（`文件 > 导入`）：Markdown(.md)、OPML、TextBundle、FreeMind、MindManager、MindNode、**MindMaster/亿图**、Word(.docx)
**导出**：PNG、SVG、PDF、Markdown、OPML、Word、Excel、PowerPoint、TextBundle（无水印属 Pro）

**Markdown → 思维导图映射（官方文档原文口径）**：
| Markdown | XMind |
|---|---|
| **第一行**（文本/标题/链接） | **中心主题**（第一行不是文本时用文件名） |
| `#` ~ `######` 标题 | 节点层级（最多 6 级） |
| `-` / `*` / `+` / `1.` **带缩进**的列表项 | 子主题（**缩进决定父子**） |
| 纯文本 | 按位置作中心主题 / 子主题 / 备注 |

也可**直接把 Markdown 文本粘到画布**（自动识别）。

## 4. 我们的落地路径（不手打节点）

```
python D:\Hermes\scripts\gen_mindmap_md.py
# 数据源：D:\Hermes\scripts\project_tree_data.py（唯一数据源，拓扑图与脑图共用）
# 产物：D:\Documents\我的文档\思维导图\技术部项目思维导图.md
```

→ 之后要更新：改 `project_tree_data.py` → 重跑 md → 交付新 `.xmind`（见第 7 节，已不必手工导入）

**格式要点**：首行＝中心主题；其后全部用**两空格一级缩进的 `- ` 列表**；状态图标（✅▶⚠○）和 `｜ 负责人` 直接写在节点文本里（XMind 能显示 emoji）。

## 5. 备选工具（凡哥要换时报这几条）

| 工具 | 特点 |
|---|---|
| **万兴脑图（原亿图脑图）MindMaster** | 国产、更便宜、导入导出与 XMind 兼容性最好 |
| Freeplane / FreeMind | 完全免费开源（.mm 为 XML，可程序化生成），但界面笨重、中文一般 |
| draw.io（已装） | 免费，有官方 Mindmap 形状库；但**曲线/配色/一键布局不如 XMind**，且 `organic/radialTree` 布局走 ELK（**ELK 需联网，离线会卡死**） |

## 6. 常见误判（踩过）

- ❌ 把「大领域→拆模块」直接做成**方框树**交上去 → 凡哥 2026-09-23 说「不是拓扑图，是思维导图」——**形态**才是他关心的第一要素。
- ❌ 在 draw.io 里硬凑思维导图样式 → 结果既不像 WBS 也不像脑图；**专业形态交专业工具**。
- ❌ 想当然认为「免费版导出能用」→ 免费版导出**带水印**（官方对比表「去除水印」是 Pro 项）；要给外部看就得说清，别替凡哥省钱省出问题。

## 7. 实测：自动导入 + 存档 + 校验（2026-09-28 全链跑通）

**① 不用手点菜单 —— 用文件参数启动，XMind 自动走导入**
```powershell
Start-Process 'C:\Users\bobby\AppData\Local\Programs\Xmind\Xmind.exe' `
  -ArgumentList '"D:\Documents\我的文档\思维导图\技术部项目思维导图.md"'
# 约 20s 后即成图：中心主题「技术部 · 技术项目主管（凡哥）」，状态栏「主题: 74」
```
- 已验证：XMind 里 **74 个主题**，与 `project_tree_data.py` 的节点数一致。
- 先决条件：XMind 已装且**已登录**（凡哥自己登的；登录/扫码一律他本人做）。

**② 存档：按 Ctrl+S 即可，但存哪儿有惊喜**
- XMind 自动把文件命名成**中心主题名**：`技术部 · 技术项目主管（凡哥）.xmind`，且落在**应用上次使用的目录**（实测落在 `D:\Documents\我的文档\拓扑图\` 而不是 .md 所在的"思维导图"目录）。
- 所以存完要**找回来改名归位**：
  ```
  find /c/Users/bobby /d/Documents -iname "*.xmind" -newermt "-15 minutes"   # 找刚存的文件
  → 移到 D:\Documents\我的文档\思维导图\技术部项目思维导图.xmind
  ```
- 给凡哥的提醒：**应用内存里还记着旧路径**，他再按 Ctrl+S 可能又存回旧目录 → 让他用「文件 > 另存为」指到"思维导图"目录。

**③ 校验（比截图可靠，学自 draw.io 那次教训）**
```python
import zipfile, json
with zipfile.ZipFile(xmind_path) as z:
    names = z.namelist()          # ['content.json','metadata.json','Thumbnails/','Thumbnails/thumbnail.png','manifest.json','content.xml']
    d = json.loads(z.read("content.json").decode("utf-8"))
    rt = d[0]["rootTopic"]        # 中心主题
    def cnt(t): return 1 + sum(cnt(c) for c in t.get("children", {}).get("attached", []))
    print(rt.get("title"), cnt(rt))   # → 技术部 · 技术项目主管（凡哥） 74
```

## 8. `.xmind` 格式 = 可直接程序化生成（以后不必再手工导入）

`.xmind` 就是个 **zip**，内部结构：
| 文件 | 作用 |
|---|---|
| **`content.json`** | 主体：`[{ "rootTopic": { "title": …, "children": { "attached": [ … ] } } }]` |
| `content.xml` | 同一份内容的 XML 版本（兼容老版/其它工具） |
| `metadata.json` / `manifest.json` | 元数据、文件清单 |
| `Thumbnails/thumbnail.png` | 预览缩略图 |

→ **父子层级结构与我们数据一一对应**，因此**可直接由脚本写出 `.xmind`**（2026-09-29 实测跑通，见 §10 末尾示例）：以某个现有 `.xmind` 当模板，读进 `content.json` / `metadata.json` / `manifest.json` / `Thumbnails/thumbnail.png`，**只替换 `content.json` 里 sheet 的 `rootTopic`**（`title` + `children.attached`），再原样写回 zip —— XMind 双击正常打开、可编辑，右下角「主题: N」与数据一致。

- 可直接抄的示例脚本：`D:\Hermes\scripts\gen_mindmap_guozhiqin.py`（数据放在文件顶部 `TREE`，形态 `("父", ["子", ...])`；跑一次同时产出 `.md` + `.xmind`）
- topic 最小结构：`{"id": uuid4, "class": "topic", "title": ..., "titleUnedited": false, "children": {"attached": [...]}}`
- 布局：`rootTopic.structureClass` 用 `org.xmind.ui.map.balance`（左右平衡，适合"左一类/右一类"的双向结构）或 `org.xmind.ui.map.clockwise`
- 校验：重开 zip 读 `content.json`，比对中心主题 + 递归主题数（同 §7③）。**同时用 `capture(app='Xmind', mode='ax')` 读节点文字核对**——比截图 OCR 可靠，Electron 的 a11y 树能给每个主题的原文。

## 10. ⚠ 强杀 XMind 后它会「恢复旧工作副本」（2026-09-29 踩到）

- **现象**：`taskkill /F /IM Xmind.exe` 之后再用文件参数启动，界面里显示的是**上一版内容**（旧文字 / 旧布局），而磁盘上的 `.xmind` 其实已经是新版。
- **根因（两个缓存位置，缺一不可清）**：`%APPDATA%\Xmind\Electron v3\vana\` 下 ① `workbooks\<路径hash>\content.json`（工作副本）② **`file-cache\<路径hash>\*.xmind`（打开文件时的缓存副本）**；非正常退出后 XMind 按这两处恢复。**只清 workbooks 不够** —— 2026-09-29 实测：清了 workbooks 仍显示旧版、右下角主题数还是旧的，**连 `file-cache` 一起清掉再启动**才读到磁盘最新版（清完首次启动稍慢，可能 30s+ 才出窗口，别急着判失败）。
- **处理**：删掉 `workbooks\<hash>` + `file-cache\<hash>` 再启动（清前可整目录备份到 `%LOCALAPPDATA%\Temp`）；或把交付文件**改名**后重开（旧会话按路径关联）。**`vana\state\account.json` 是登录态，不要删**。
- **教训**：改完 `.xmind` 别用 taskkill 收尾 —— 要么让凡哥正常关闭，要么「先杀 → 再生成 → 再启动」；启动后一律用 `capture(mode='ax')` 核对文字是不是最新版（否则凡哥按 Ctrl+S 会把旧内容写回磁盘）。

## 9. 驱动 XMind（Electron）的 computer_use 硬规则

- **后台投递会被丢**：`click`/`key` 报 `Background delivery is not available for target window class 'Chrome_WidgetWin_1' ...` → 必须 `delivery_mode='foreground'`（实测 `keys='ctrl+s'` 前台 SendInput 成功）。前台会**短暂切走凡哥的窗口**，动手前在回复里说明。
- **`coordinate` 按"截图空间"传**：工具会按窗口偏移+缩放换算到 native。我第一次按 native 数学推算坐标 → 点空（落到了别处）。正确做法：从 `capture(mode='som')` 的元素 native bounds 反算截图坐标，或先点一次再看 `capture_after` 复核。
- **裸 `element_index` 会被拒**（要求 `element_token` 或 `snapshot_id`+`element_index`，而这两个字段不在工具入参里）→ 退回 `coordinate` 方案。
- 起手式：`Start-Process` 启动 → `sleep 20` → `capture(app='Xmind', mode='som')` 读 element 标签（Electron 的 a11y 树能给出**每个节点文字**，比截图 OCR 可靠）。
