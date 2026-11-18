# 短剧资产链：剧本 → 视觉设定 → 生图提示词（2026-11-18 实跑）

> 场景：要用 H3 真跑一颗镜头，必须先有参考图；参考图要先出图；出图要先有资产设定。
> 这条链每部剧都走一遍，按本文件照做即可，别每次重新设计。

---

## 一、三步链条

```
剧本（定稿）
   ↓  short-drama-assets（zenstory 套装，★4.3k）
视觉设定.md —— 人物 / 地点 / 道具，跨场不变的写"外观特征"，本集变化写"本集状态"
   ↓  按本文件的提示词规则
生图提示词 —— 人物四视图 / 场景俯视主图 / 道具图鉴
   ↓  凡哥逐张生成
参考图 → 分镜技能 → H3 真跑
```

**为什么资产要先做**：短剧的核心成本在"人物一致性"，而一致性**只能靠参考图锁**（forest-laoli-h3 的原文判断）。没有参考图，后面所有分镜都是纸面。

---

## 二、视觉设定的字段规范（拆解时照填）

**文件顶部两行必写**：
```
- 制作形态：国漫 3D CG（半写实）· 横屏 16:9
- 时代背景：当下（2020 年代）；设备：…；陈设：…；室内照明：…
```

**每个条目用二级标题** `## <人物|造型|地点|道具> · <名称>`，下面按类型填：

| 类型 | 必填 | 关键要求 |
|---|---|---|
| **人物** | 外观特征 / 本集状态 / 角色声线 / 提示词名称 | **禁止"年轻漂亮""气质冷峻"这类空泛词**；必须写脸型骨相、眉眼鼻唇、发际线与发质、**正侧背都能认人的体态特征**、**身高体型参照**（"比林小满高半个头"） |
| **地点** | 空间布局 / 出入口连通 / 固定陈设 / 主材尺度 / 本集状态 / 机位视角 | **先立空间结构再写氛围**；室内方位用陈设相对位置或固定朝向（"配电箱钉在柜台后墙靠北门一端"），**别写"左侧大窗"**（正反打一换机位左右全反）；家具写明人体高度参照（"桌高 75cm，齐成年人腰带"） |
| **道具** | 外观特征 / 尺寸参照 / 字迹处理 / 本集状态 | 尺寸要有参照物（"A4（21×29.7cm）""折成四折后约 7.4×10.5cm"）；**字迹必须五选一**（清晰可读／只留版式／表面无字／待拍板／后期叠加） |

**跨场连戏锁**：对跨镜反复出现、画偏即穿帮的不变外观加锁。**服装锁挂在"造型"条目下写"镜头：入画"**。

**角色声线**：一旦本集启用这一项，所有有发声台词（含对白、VO、OS）的人物都必须填写，不能写"无"。

---

## 三、生图提示词：三条铁律（踩过才写在这）

### 铁律一：人物四视图 = 一次直出，四个格子

**四格固定**：正面全身 / **单张**侧面全身 / 背面全身 / 五官特写。
- 不许拆成"左面 + 右面"（凡哥实测崩点：会出现两个背面、缺侧面）
- 不许 1:1 半身像（凡哥原话：「为什么是 1 比 1 的比例半身照呢？」）
- 不许逐视角分步生成再拼合（凡哥否决：「这个步骤不对」）
- **五官特写是最高优先级的身份参考**

**宫格约束三句必须写进 prompt**：
```
uniform ultra-thin hairline dividers between panels, every divider exactly the same 1mm thickness, thin light-gray hairline lines
no outer frame, no outer border around the whole sheet
no thick borders, no black frames, no comic panel outlines, no double lines, no colored dividers, no decorative edges
```

**一致性段（INVARIANTS）也要写**："Exact same hair length, clothing, shoes, and facial bone structure across all four panels. No change of outfit or hairstyle between panels."

### 铁律二：场景不许一次四宫格，必须先出「正俯视主图」

**为什么**：一次生成场景四宫格，四格会**像四个不同房间**（材质/光线/尺度对不上）—— 凡哥实测 ✗。角色和道具四视图可以一次多格（已成熟），**只有场景要分步**。

**主图规格**：从正上方垂直向下看的**平面图**，锁死完整平面布局、四面墙及门窗位置、固定地标、走道关系，同时锁材质配色光线氛围。**这张是该场景资产的唯一身份源**，其他角度后面派生。

**主图必写**："This is a floor plan identity reference, so the layout must be complete and readable from above: every wall, every partition, every door, every desk cluster." + "No text, no labels, no arrows, no annotations."

### 铁律三：纸面文字只生成「版式」，不生成可辨认字

末位榜、记分纸、工牌、打分表这类 —— **生图模型写中文必然出乱码/错字**。

**统一写法**：描述表格线、红圈、色块、手写密度感，末尾写 **"Only layout blocks, no readable letters or numbers anywhere."** / "no readable characters"。
**字后面用别的方式加**（后期叠字或素材替换）。

---

## 四、9 张图的清单结构（一部 6 场戏的短剧，实测量级）

| # | 图 | 类型 | 说明 |
|---|---|---|---|
| 1-5 | 主要人物 | **四视图** | 主角 → 对手 → 关键配角 → 高层 → 功能性配角（最后两个可砍） |
| 6-8 | 主要地点 | **俯视主图** | 每个独立空间一张（办公室 / 主管室 / 走廊） |
| 9 | 道具 | **六宫格一次直出** | 6 个道具合一张，每格一个、三视角、白底居中 |

**参数统一：`size="2K"`，16:9 = 2816×1584**（Seedream 5.5 天花板，别写 4K）。
**纯白底 #FFFFFF**（`background` 不用透明，资产图要白底）。

---

## 五、锁风措辞（3d_animated_film 必须三锚点齐全）

每张资产图 prompt 开头都带这一组：

```
Chinese 3D donghua animation style, Chinese 3D CG anime character, oriental facial features: oval face, refined phoenix eyes, slender small nose, slender realistic 7.5-head-tall proportions, elegant smooth skin, fine detailed hair strands, refined fabric folds, cinematic CG render, soft warm lighting, gentle depth of field
```

结尾显式排除（凡哥实测去皮克斯）：

```
not Pixar style, not Disney style, not western cartoon, no rounded chubby body proportions, no big circular western eyes, not photorealistic, not realistic skin pores, not flat 2D cel anime, no ink outlines
```

**三锚点缺一不可**：东方五官 + 修长比例 + 国漫渲染。
**禁用写实渲染词**：`subsurface scattering skin` / `PBR material detail` / `volumetric lighting` —— 会漂向写实 CG（凡哥实测）。

---

## 六、出图后的自检（四视图专用，不合格重跑别往下走）

1. **四格齐不齐** —— 正面/侧面/背面/五官；**特别看有没有"两个背面"或"缺侧面"**
2. **服装鞋袜配饰跨格一致** —— 袖口卷到哪、裤脚、鞋型，四格必须一样
3. **格子之间的线** —— 等宽浅灰细线；整图外面**不能有边框**

---

## 七、⚠️ 剧本文件的 `Episode 00N` 编号 ≠ 第 N 集

**2026-11-18 实证**：文件标题写 `Episode 002: 末位`，我按标题以为测的是第二集；凡哥纠正「测试第一集吧」。翻开正文第一行：

```
> 上集观众记得什么：第一集，无。
> 开场回钩：无（第一集，以入职第一天的陌生感开场）
```

**它就是第一集，"002" 是模板残留编号。**

**规则**：拿到剧本先读开头三行（上集回钩 / 开场 / 本集一句话），**别看标题就下结论**；同一目录里可能同时躺着"初稿"和"第 N 稿"，按 mtime + 文件名版本号取最新的那份。
