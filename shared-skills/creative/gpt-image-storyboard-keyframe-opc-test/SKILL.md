---
name: gpt-image-storyboard-keyframe-opc-test
description: 生成分镜故事板宫格关键帧时加载。用分镜脚本+主体资产图生成宫格关键帧供H3用。
version: 0.1.0-rc
---

# 分镜故事板关键帧（OPC v2 测试）

## When to Use

当分镜脚本包（storyboard_package.json）已产出、需要生成宫格故事板关键帧时加载。触发：凡哥说「生成故事板」「出关键帧」「分镜故事板」。

## 定位

OPC 链路第 6 个节点。输入分镜脚本（shot cards）+ 主体资产图，输出每镜的宫格故事板关键帧。关键帧是 H3 全能参考的「时间轴画面锚点 + 参考图」，不是装饰性概念图，是下游 H3 生成视频的约束系统。

## Input Gate

- 分镜脚本包（storyboard_package.json）：shot cards（identity_ids、grid_count、playable_action、emotion、cut_interface、dispatch）
- 主体资产图：人物四格、场景四宫格、道具四视图
- 资产包（asset_package.json）：identity_masters（身份事实：服装/发型/年龄/配饰）
- 画风：继承全局 style_id

## 核心规则

### 1. 人物一致性（最高优先级规则）

- **每个镜头，必须为「所有出场人物」绑定参考图**。出场人物 = shot card 的 identity_ids，一个都不能漏。
- 参考图**直接传人物四格原图**（正面/侧面/背面/特写，完整身份参考），**不裁切、不抠单格**。参考图不限制张数（最多 16 张），可同时传：所有人物的四格图 + 场景四宫格 + 道具四视图。
- **身份细节写进 INVARIANTS**：从资产包 identity_masters 读取服装/发型/年龄/配饰，逐项写进 prompt，声明「跨所有宫格保持不变」。
- 缺失任一出场人物的参考图 → 阻断，不生成（人物一致性是硬门禁，不是可选项）。

### 2. 宫格数=切镜数（2026-09-03 凡哥定方向，对齐官方 storyboard 语义）

- **宫格数 = 该镜的切镜数（Shot 数）**，不是状态数。官方语义：storyboard 是「切镜规划图」（one Shot = one composition anchor），不是状态帧序列。
- **无切镜的单镜头（绝大多数情况）→ 单图故事板**：一张 16:9 全幅构图锚点图，给主体位置+机位+关键道具；状态演进全部交给提示词文字，画面里不放多图混控（多图会干扰单镜走向：实战=背景漂移/人物换位）。
- 有切镜（正反打已拆成独立镜，所以当前全片每镜都是单图）→ 切几个镜就几格，每格=一个 Shot 的构图，按 left→right 顺序；4 格才用 2×2 田字（每格横版=成片构图），禁止一横排竖窄条。
- 单图故事板 prompt 布局措辞：「a single full-frame storyboard image, no grid, no panels, no dividers, no text」。宫格/分界线措辞只在多切镜时使用。
- **内容只画构图锚点**：该镜最代表的一个构图（人物位置+机位+关键道具+灯光），不画动作序列、不画多个状态。

### 3. 精致度（继承主体资产的画风声明）

- 画风声明来自 opc-style-prompt-vocabulary-v0.1.md：次世代 3D CG quality + highly detailed + rim light（轮廓光）+ warm-cool contrast（冷暖对比）+ detailed skin/hair/fabric（材质细节）。
- [STYLE] 填结构化声明（风格名 + 2~3 特征 + 1 明确排除），不堆关键词，不裸写笼统词。

### 4. 场景与道具参考

- 场景参考图绑定 shot card 的 space 对应的场景四宫格。
- 道具参考图绑定 prop_before/prop_after 对应的道具四视图（按需）。

### 5. 方位锚点（凡哥铁律，2026-09-03 定稿）

- 故事板 prompt 中画面内方位一律以**主体自身方向**为锚点：「母亲站在周野右后方」「门在周野正前方」，禁止「画面左侧/右侧」「镜头左侧」等以画面/镜头为参照系的写法。
- 宫格布局词（top-left panel / top-right panel）指**宫格位置**，不是画面内方位，两者不冲突、可并存。

6. **人物比例写死**：成年人真实头身比（头高≈身高 1/7.5），3D animated film style 下禁止卡通化大头/短身。prompt 措辞：「realistic adult proportions, head about one-seventh of total height, natural human anatomy」。（实战违规 2026-09-03：S10a 头身比不对，凡哥验收抓出；vision 对比例细节不敏感，凡哥人眼为准。）

### 6. 跨镜一致性（凡哥铁律，2026-09-03 定稿）

## 剧情核对铁律（最高优先级，防执行犯错）

**目的：让执行者犯错也不可能丢剧情。**

1. 生成每张故事板 prompt 前，先读该镜 shot card，把 `playable_action` 里的核心动词**逐字抄进 prompt**（揉面就是揉面，不能凭印象写成模糊的"在厨房"）。
2. prompt 写完，调生图**之前**，对照卡自检一遍：卡里每个剧情动作词都在 prompt 里吗？缺一个=违规，重写 prompt，不生成。
3. 抄丢剧情动作=最严重违规。实战案例：S07 卡写「周野揉面+母亲按面团」，prompt 写成模糊场景→模型画成切黄瓜炒菜，整部戏的剧情被改变。

### 7. 单图 prompt 五大写死（2026-09-03 实战违规 4 连，凡哥抓）

单图故事板 prompt 必须把以下五类细节写死，禁止给模型自由发挥空间。违规实例全部来自实战：

1. **朝向写死**：用身体朝向+手部动作链锁定——❌「standing sideways facing the door」（模型画成背对门看镜头）→ ✅「his body angled toward the closed door directly before him, his free hand raised to the door surface」。人物面朝什么方向、视线看哪，一句写死。
2. **人物写死**：❌「the person across the table」（模型自创年轻女性）→ ✅「Zhou Ye sits across the table, seen from behind, his dark navy jacket and crew cut」——**出场人物一律写全名+身份锁定词（发型/服装），禁止 the person / someone / the other figure 等模糊指代**。正反打里画外/背影人物也必须写死身份。
2b. **手持物写死**：❌「carries a backpack low in one hand」（模型画成背着）→ ✅「holds the backpack by its top handle in one hand at his side, the bag hanging straight down, straps not on his shoulders」。
3. **空间衔接写死**：跨镜空间关系正向写死——❌「home entryway」（模型把门外画成室外，两次犯）→ ✅「inside the doorway is the warm entry hall; outside the door gap is the same indoor stairwell corridor, dim, with the stair railing」。**「同一空间」必须用「the same indoor ...」正向声明，不能只说空间名**。
4. **家具写死**：❌「sitting」（模型画成沙发）→ ✅「seated at the wooden dining table, the two chairs across the table」。
5. **核心动作+道具清单写死**：❌「kneads dough at the counter」（模型画成切黄瓜，自加菜刀/生菜）→ ✅「kneading a ball of dough in a mixing basin, both hands pressing into the dough; the counter holds only the basin and a small flour bowl」——**动作动词+道具白名单**，白名单外的道具不写（实战：白米饭/托盘饮料都是模型自创道具）。

- **灯光**：照分镜卡 project_defaults 的灯光基调写，逐图统一措辞（如「warm home lighting at night」）；特殊镜（S01 楼道 dusk）单独声明且全片仅此一处。
- **空间**：照分镜卡的 space 字段写死（S02 门外=与 S01 同一楼道）；相邻镜的空间关系不许漂。
- **时间**：照分镜卡的 time 字段写死（黄昏/刚入夜/深夜），禁止自行演绎。
- **道具连续性**：关键道具（包/面盆/饺子）在图内状态写死——该镜里包在哪、有没有入画，与分镜卡 prop_before/prop_after 一致。
- **人物位置**：人物在场景中的位置照分镜卡 blocking 的道具参照写死；正反打拆镜后每镜单机位，人物位置不许在格子间互换。

## 输出

每镜一张宫格故事板关键帧图（16:9 原生 4K，3840x2160），宫格数 = grid_count。

## 画风锁定（凡哥 2026-09-04 定稿 v2）

项目 style_id=`3d_animated_film` 时，每张故事板 prompt 必须用**中国 3D CG 动漫锁风措辞**（国漫 3D 动画风：《凡人修仙传》《雄狮少年》质感，非皮克斯非写实）：`Chinese 3D donghua animation style, Chinese 3D CG anime character, oriental facial features: oval face, refined phoenix eyes, slender small nose, slender realistic 7.5-head-tall proportions, elegant smooth skin, fine detailed hair strands, refined fabric folds, cinematic CG render, soft warm lighting, gentle depth of field` + 显式排除 `not Pixar style, not Disney style, not western cartoon, no rounded chubby body proportions, no big circular western eyes, not photorealistic, not realistic skin pores, not flat 2D cel anime, no ink outlines`。
**禁用写实渲染词**：subsurface scattering skin / PBR material detail / volumetric lighting 漂向写实 CG（凡哥实测），不得单独使用。
凡哥历次纠正：裸标签漂 2 次元 → subsurface/PBR 偏写实 → large eyes/rounded 偏皮克斯欧美。**东方五官+修长比例+国漫渲染三锚点缺一不可**。

## 宫格规格（凡哥 2026-09-04 定稿 v2）

凡哥要求：但凡是宫格图（含故事板 2×2 宫格、四视图资产图）：
- **子图间分割线**（prompt 必写）：`uniform ultra-thin hairline dividers between panels, every divider exactly the same 1mm thickness, thin light-gray hairline lines`
- **宫格外无边框**（prompt 必写）：`no outer frame, no outer border around the whole sheet`
- **禁止项**（凡哥实测边框粗细不稳定，prompt 必写）：`no thick borders, no black frames, no comic panel outlines, no double lines, no colored dividers, no decorative edges`
- 子图本身无描边，画面直达细线。

## 生成规则（写 prompt 时直接满足，生成即完成）

1. 所有出场人物都有参考图绑定（不遗漏）。
2. 身份细节（服装/发型/年龄）跨宫格一致。
3. 宫格数 = grid_count。
4. 精致度画风声明到位。
5. 无文字标签；格子间用统一 1mm 细线（uniform ultra-thin hairline dividers, equal thickness），粗细一致。
6. 宫格布局：4 格=2×2 田字（每格横版=成片构图），禁止一横排竖窄条。
