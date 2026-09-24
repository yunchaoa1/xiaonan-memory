# draw.io CLI 与格式速查（现役拓扑图路线 · 2026-09-23 实测）

现役生成器：`D:\Hermes\scripts\gen_topology_tree.py`（树形 WBS，单页）。
本文只记**会用到命令与判据**，规则与画法见 SKILL.md。

## 一、一条命令出全套（日常只用这条）

```
python D:\Hermes\scripts\gen_topology_tree.py --layout
```

顺序（脚本内部自动做）：
1. 生成骨架 `.drawio` + **骨架重叠断言**（打印 `节点 N · 连边 M · 骨架重叠对数 0`）
2. 官方**内置树布局**重排坐标（`--layout horizontalTree`，见 §三）
3. **按内容重设画布** pageWidth/pageHeight（见 §四）
4. 导出 PNG（`--scale 2`）/ SVG / PDF

产物（`D:\Documents\我的文档\拓扑图\`）：`项目拓扑图_WBS.drawio / .png / .svg / .pdf`
（`_布局后.drawio` 是布局引擎的输出，供导出用；要改内容改脚本，别改它。）

## 二、CLI 调用：Store 版必须走 PowerShell

程序路径（微软商店版，**bash 因 ACL 调不了，PowerShell 可以**）：

```
C:\Program Files\WindowsApps\draw.io.draw.ioDiagrams_31.4.5.0_x64__1zh33159kp73c\app\draw.io.exe
```

```powershell
$exe = "C:\Program Files\WindowsApps\draw.io.draw.ioDiagrams_31.4.5.0_x64__1zh33159kp73c\app\draw.io.exe"
& $exe --export --format png --scale 2 --size diagram --output out.png in.drawio
& $exe -x -f xml -u --layout horizontalTree -o laid.drawio in.drawio    # 布局 + 未压缩 XML 输出
```

常用参数（官方 `--help` 实测）：`--format png|svg|pdf|xml|html|jpg`、`--scale N`、
`--size diagram|page`、`--page-index N`（1 起）、`--all-pages`（**只对 PDF/HTML 有效**）、
`--layout <preset|json>`、`-u/--uncompressed`、`--theme dark|light|auto`。

**跑 CLI 前先 `Stop-Process -Name draw.io`**：已打开的实例会让 CLI 卡住不返回。

## 三、离线只有内置布局预设（ELK 是联网加载的）

- `--layout '{"layout":"elkLayered",...}'` → **本机（GitHub/CDN 不通）会卡死**（不是慢，是等不到资源）。
- 离线可用预设：`horizontalTree` / `verticalTree` / `organic` / `radialTree` / `verticalFlow` / `horizontalFlow`。
- 树形/WBS 用 **`horizontalTree`**（左→右，正交连线、零重叠、层间距自动算）。

## 四、布局后必须重设画布（否则"画布框"小于内容）

布局引擎会把页面尺寸重置成默认值（实测被改成 827×1169），而内容可能有 3681×2748 →
- 导出（`--size diagram`）仍能按内容裁剪，图是完整的；
- 但**在软件里用"页面视图"打开时，框装不下内容**，且后续按 page 尺寸导会出问题。

做法（脚本已内置）：解析布局后文件 → 算出内容包围盒 + 40 单位留白 → 写回
`mxGraphModel@pageWidth/pageHeight` → 再导出。**布局后要再跑一次重叠断言**（坐标被重排过）。

## 五、`.drawio` 格式要点（官方依据，别猜）

- 官方规范 + 14 条校验清单：https://www.drawio.com/docs/reference/diagram-generation/style-reference/
- 官方 XML 参考：https://github.com/jgraph/drawio-mcp/blob/main/shared/xml-reference.md
- 必须元素：
  - `<mxCell id="0"/>` 与 `<mxCell id="1" parent="0"/>`（固定两根）
  - 顶点：`vertex="1" parent="1"` + `<mxGeometry x y width height as="geometry"/>`
  - 连线：`edge="1" parent="1" source="..." target="..."` + `<mxGeometry relative="1" as="geometry"/>`
  - **id 在单页内唯一**；用未压缩 XML（`-u`）
- 标签换行用 `&#10;`（实测可正常渲染）；XML 里 `&`/`<` 用 `xml.sax.saxutils.escape`，别手拼。
- 连线走 WBS 惯例：`endArrow=none;strokeColor=#909090;strokeWidth=1.2`（分解关系不是流程，不带箭头）。

## 六、验证配方（三层，别开窗口截图猜）

1. **断言层**：骨架 + 布局后各跑一次两两重叠断言（`重叠对数 0`），或直接 `scripts/drawio_verify.py`。
2. **几何层**：解析布局后 XML，核对 `内容包围盒 ⊂ 画布`、顶层分支的 y 坐标分布。
3. **文本层**：**SVG 是文本** → 直接在里面检索关键节点名（比看缩略图可靠得多）：
   ```python
   svg = open("项目拓扑图_WBS.svg", encoding="utf-8").read()
   [k for k in ["公司级 Agent", "待办事项", "漫剧发布平台"] if k not in svg]  # 应为空列表
   ```
   需要目视时用 PIL 按节点坐标裁剪局部（`im.crop(...)`）再看，别整图缩略——**缩略图会把我看错**（本次把完整的图误判成"底部被裁"）。

## 七、本次踩坑（写死）

- **交互窗口画布空白 ≠ 文件坏**。文件一直是对的；真要判合不合法，**跑一次 CLI 导出**——能出图＝合法。
- **禁止用正则从 `.drawio` 里剪 `<mxCell>`**：非贪婪 `.*?` 会在 `<mxGeometry ... />` 处截断，产出坏 XML → 得到"解析失败"的**假失败**。用 `xml.etree.ElementTree` 解析。
- 别在窗口里"改一个变量→开一次窗→截一次图"试错（凡哥：试错成本很高）；先读官方规范 + 用官方 CLI 一次定论。
- Python 写文件时 `open(..., "w", encoding="utf-8", newline="\n")`；`re.sub` 的**替换串里 `\n` 会被解释成真换行**（要写 `\n` 字面量得用 lambda 或字符串拼接）。
