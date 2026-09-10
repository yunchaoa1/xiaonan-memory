# OPC GPT Image 主体资产提示词编译模板 v0.3

## 1. 通用编译原则

每次出图直接生成一张主体资产图，不再先出模板再扩展。提示词按固定顺序编译：

1. `TASK`：这张图的唯一用途。
2. `OUTPUT`：单图/视图数量、画幅、分辨率、主体占比。
3. `CAMERA_OR_PROJECTION`：景别、视点、投影、方向。
4. `VISIBLE_FACTS`：只写来源支持且画面可见的事实。
5. `LAYOUT_OR_TOPOLOGY`：主体或空间的明确位置关系。
6. `INVARIANTS`：必须保持不变的身份、几何、材质、数量、服装或空间结构。
7. `ALLOWED_CHANGE`：编辑/扩展时唯一允许变化的内容。
8. `BACKGROUND_AND_LIGHT`：检视型背景和中性光照。
9. `EXCLUSIONS`：最可能出现的额外内容、文字、重复主体、裁切和漂移。

禁止直接输入会诱发自由设计的非视觉叙事标签。先转译为可见事实：

- “复原军人”不能直接作为人物造型事实；只有剧本明确的发型、服装、姿态或物件才能进入图像提示词。
- “母亲”不能自动推出年龄、围裙、发髻或慈祥微笑；这些必须来自已批准资产事实。
- “家”不能自动推出卧室、卫生间、电视、书架或装饰；场景只允许明确列出的空间和固定物件。
- “重要、伤感、温暖、英雄”等抽象词不能替代脸部动作、体态、材质或空间关系。

## 2. 人物四格

### 输入字段

- 视觉媒介/画风
- 性别、年龄段（有来源时）
- 脸型、眼睛、眉毛、鼻、嘴、下颌、耳朵、发际线、发型、肤色
- 全身与肩颈比例
- 当前服装结构、材质、颜色
- 佩戴配饰
- 表情的可见动作
- 显式未知项

资料不足时不得用职业、亲属身份或剧情性格补齐五官和服装。缺少稳定身份事实时返回 `ASSET_BLOCKED`。

### 编译模板

```text
TASK
Create one production character subject-asset sheet for [CHARACTER_ID] in [STYLE].

OUTPUT
One 16:9 native 4K image, 3840x2160. Exactly four vertical panels with equal visual rhythm and clean separators. Panel 1: front full-body standing. Panel 2: one side full-body standing. Panel 3: back full-body standing. Panel 4: enlarged straight-on facial detail. No fifth panel.

CAMERA_OR_PROJECTION
Neutral orthographic-like inspection views, consistent subject scale in the three full-body panels, eye-level, feet on one shared ground line, head tops on one shared guide line. Arms relaxed with body silhouette readable. Full body including feet visible.

VISIBLE_FACTS
[FACE_GEOMETRY]. [HAIR]. [SKIN]. [BODY_PROPORTIONS]. [WARDROBE]. [WORN_ACCESSORIES]. [VISIBLE_EXPRESSION].

INVARIANTS
Preserve one identity across all four panels: facial geometry, skull and jaw shape, hairline, hairstyle, skin, wardrobe structure, material, color palette, worn accessories, age state, and body proportion logic.

BACKGROUND_AND_LIGHT
One uniform pure-white (#FFFFFF) background and one consistent soft inspection light across all four panels.

EXCLUSIONS
No external props, bags, handheld objects, scenery, text, labels, logos, extra people, repeated side view, three-quarter view replacing a required panel, cropped feet, different outfits, different faces, different ages, panel count changes, or decorative layout.
```

### 验收

严格四格；三张全身加一张五官特写；同一头高线/地面线；全身不裁脚；侧面只有一张；五官、发型、衣服、配饰跨格一致。

## 3. 场景四宫格

### 前置条件

从资产提取节点的场景主体信息直接生成，不再先出场景模板。左上格固定为场景内部真实俯视图；其余三格固定为该场景内、服务于剧本动作的细节视角。

### 编译模板

```text
TASK
Create one unlabeled four-panel empty-location reference sheet for [LOCATION_ID] in [STYLE].

OUTPUT
One single 16:9 native 4K image, 3840x2160, with exactly four equal image panels and clean white gutters. All four panels show the same unoccupied approved location and share one spatial identity. The sheet has no header, title, footer, legend, caption area, metadata block, or written annotation.

SCENEPLAY_TO_SPACE_RULE
The screenplay may choose only empty areas and fixed landmarks already represented by the approved scene facts. A missing region or object is omitted from this asset version, not invented. Translate actions only into required free space, circulation, fixed furniture, and architectural visibility. Do not render the characters, actions, handled objects, plot props, emotions, or story event that motivated the view.

COMMON_SENSE_BASE
Establish the believable common-sense base first: a modern living room normally has a sofa seating area, a low coffee table, a television on a low console, and a usable open activity area; a kitchen reads as a usable kitchen with worktop/chopping-board area, hob, sink and normal counter line; a dining area reads as a usable dining area with a table and ordinary chairs. Incidental plants, ordinary furniture and small appliances may appear when consistent with the dwelling and not contradicting the screenplay.

SCREENPLAY_ADDITIONS
Add only the screenplay's extracted fixed structures on top of that base, such as an entrance door with a clear wall-side area for a bag, a window sill with a green pothos, a washed-blue dining cloth, a hob, or a chopping-board worktop. Do not render the extracted list as an empty room.

PANEL_LAYOUT
Top-left: the actual interior top-down view of the approved scene, showing its complete footprint, fixed boundaries, doors/openings, permanent landmarks, activity area, circulation paths, and the spatial relationship needed to understand the other three panels. This panel is the shared spatial truth. EMPTY_PANEL_CONTRACT: architecture and fixed furnishings only; zero people, zero body parts, zero loose props, zero text or symbols.
Top-right: [SCREENPLAY_REQUIRED_EMPTY_AREA_VIEW_1]. ANCHOR: [FIXED_SUBJECT_1]. ANCHOR_RELATIONS: [OTHER_VISIBLE_OBJECTS_DESCRIBED_FROM_ANCHOR_1_OWN_FRONT_BACK_LEFT_RIGHT]. EMPTY_PANEL_CONTRACT: architecture and fixed furnishings only; zero people, zero body parts, zero loose props, zero text or symbols.
Bottom-left: [SCREENPLAY_REQUIRED_EMPTY_AREA_VIEW_2]. ANCHOR: [FIXED_SUBJECT_2]. ANCHOR_RELATIONS: [OTHER_VISIBLE_OBJECTS_DESCRIBED_FROM_ANCHOR_2_OWN_FRONT_BACK_LEFT_RIGHT]. EMPTY_PANEL_CONTRACT: architecture and fixed furnishings only; zero people, zero body parts, zero loose props, zero text or symbols.
Bottom-right: [SCREENPLAY_REQUIRED_EMPTY_AREA_VIEW_3]. ANCHOR: [FIXED_SUBJECT_3]. ANCHOR_RELATIONS: [OTHER_VISIBLE_OBJECTS_DESCRIBED_FROM_ANCHOR_3_OWN_FRONT_BACK_LEFT_RIGHT]. EMPTY_PANEL_CONTRACT: architecture and fixed furnishings only; zero people, zero body parts, zero loose props, zero text or symbols.

ANCHOR_DIRECTION_RULE
Every directional statement uses the fixed subject's own front, back, left, and right. Never replace object-relative direction with screen-left or screen-right. When the camera moves, screen position and occlusion may change, but real coordinates, adjacency, orientation, quantity, material, and nearest-neighbor relations stay unchanged.

PRESERVE_EXACTLY
Preserve one scene identity across all panels: approved topology, boundary walls, door/opening positions, fixed furniture and landmarks, materials, palette, scale relationships, and circulation logic. The three detail views are different camera framings of this same scene, not three new rooms.

BACKGROUND_AND_LIGHT
Pure-white #FFFFFF outside the scene image areas, in gutters, and in unused margins. Use coherent neutral inspection lighting across the three detail views.

EXCLUSIONS
No fifth panel, no extra room, no expanded bedroom/bathroom/laundry/storage interior, no duplicate kitchen or dining area, no loose plot prop, no person, no human silhouette, no hand, no shoulder, no reflection of a person, no portrait/photo/TV image containing a person, no perspective plan replacing the top-left overhead view, no title, header, footer, caption, scene description, camera term, panel label, number, letter, word, pseudo-text, arrow, grid, logo, watermark, or collage of different scenes.
```

### 四格选择原则

左上俯视图负责空间总览；三个细节格必须分别对应剧本中真正需要拍摄的区域、动作或接触关系，不按“客厅/厨房/餐区”机械凑格。某细节没有剧本依据时，不得加入该格。

## 4. 道具四视图

### 输入字段

- 道具类别
- 精确数量（通常1）
- 外轮廓和长宽厚比例
- 材质、颜色、表面
- 部件数量、位置、连接方式
- 开口、铰链、按钮、拉链、提手、接口等
- 文字/品牌策略
- 初始功能状态
- 核心物理功能（功能图来源，如背包主口袋打开、打火机点火）
- 使用者的年龄阶段、时代/生活环境、携带或使用需求，以及由上游事实支持的使用历史
- 常识定位约束：由上述事实共同推导大众第一识别，不把职业直接等同为制服、军用品、性别化配色或品牌符号

### 编译模板

```text
TASK
Create one production prop subject-asset sheet for [PROP_ID] in [STYLE].

OUTPUT
One 16:9 native 4K image, 3840x2160. Exactly four panels with clean separators. Panel 1: straight-on front view. Panel 2: one side view. Panel 3: back view. Panel 4: functional view showing the prop performing its core physical function. No fifth panel.

CAMERA_OR_PROJECTION
Neutral orthographic-like inspection views, consistent object scale across panels, object centered in each panel. Front plane parallel to image plane for the front view. One side view only, never split into left-side and right-side. Back view directly opposite the front. Functional view keeps the same object axis while showing the active function state.

PRODUCT_TRUTH
Silhouette: [SHAPE_AND_RATIO]. Material: [MATERIAL]. Color: [COLOR]. Parts: [COUNT_POSITION_CONNECTION]. Surface: [FINISH]. Base state: [STATE].

FUNCTIONAL_VIEW
[FUNCTION_DESCRIPTION] — for example, the main compartment zipper opened and the bag mouth open revealing the interior, or the lighter flame lit. Preserve the same geometry, material, color, and parts; change only the function state.

INVARIANTS
Preserve one identity across all four panels: silhouette, body dimensions, material, color, surface finish, part count, seam/control/fastener positions, and object scale.

BACKGROUND_AND_LIGHT
Pure-white (#FFFFFF) clean seamless background, even catalog inspection light across all four panels, subtle contact shadow only when physically required.

EXCLUSIONS
No person, hand, body part, clothing, scenery, pedestal unless structurally required, accessory not included in the asset, second product, three-quarter view replacing a required panel, collage, text, logo, watermark, invented control, invented port, clipped edge, or a functional panel showing a different prop.
```

### 验收

严格四视图：正面/侧面/背面/功能图；单一物件跨格一致；正面严格正面、侧面只有一张、背面正对正面；功能图展示核心物理功能且身份不变；完整不裁切；部件数可核对；材质清楚。模糊"普通包"不足以锁定主体资产时，应先补结构事实或降级为B级镜头道具。

## 5. 道具状态

### 状态规划

先从剧本动作建立最小状态集。每个状态记录：

- `state_id`
- 触发动作
- 变化部件
- 不变部件
- 可见效果
- 起止镜头

例如打火机：`closed`（盖合/无火焰）、`open_unlit`（盖开/点火轮静止）、`open_lit`（盖开/同一燃烧口出现火焰）。未在剧情出现的状态不生成。

### 单状态编译模板

```text
TASK
Create the [TARGET_STATE] state of [PROP_ID] in [STYLE].

OUTPUT
One single image, same front inspection framing and adaptive size as the prop's base view.

STATE_FACTS
[EXACT_VISIBLE_STATE_DESCRIPTION].

INVARIANTS
Preserve the object's silhouette, body dimensions, material, color, surface finish, part count, hinge/control/fastener positions, front camera, object scale, background, and lighting from its base view.

ALLOWED_CHANGE
Change only [MOVING_PARTS_AND_VISIBLE_EFFECT] from [SOURCE_STATE] to [TARGET_STATE].

EXCLUSIONS
No redesign, extra part, missing part, changed material, changed color, changed camera, hand, person, scenery, text, logo, duplicate object, or unrelated effect.
```

### 正式扩展

每个状态都需身份一致性检查，不能只检查“动作对了”。所有最终扩展统一16:9原生4K。
