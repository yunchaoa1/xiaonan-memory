# OPC Qwen-Image 2.1 主体资产提示词编译模板 v0.4

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
One Qwen-Image 2.1 native-maximum image (landscape 2752x1536 or portrait 1536x2752). Exactly four vertical panels with equal visual rhythm and clean separators. Panel 1: front full-body standing. Panel 2: one side full-body standing. Panel 3: back full-body standing. Panel 4: enlarged straight-on facial detail. No fifth panel.

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

### 交付形态

严格四格；三张全身加一张五官特写；同一头高线/地面线；全身不裁脚；侧面只有一张；五官、发型、衣服、配饰跨格一致。

## 3. 场景（主图先行 + 逐机位派生，2026-10-08 凡哥定改版）

### 前置条件

场景资产**不再一次生成四宫格**（实测四格会看着像四个不同场景：材质/光线/尺度对不上）。流程改为三步：**先出单张场景主图（身份锚）→ 以主图为参考图逐机位图生图派生 → 需要多格交付时机械拼合**。

### 3.1 场景主图编译模板（单张 · 正俯视，一次生成）

```text
TASK
Create one production scene master view for [LOCATION_ID] in [STYLE].

OUTPUT
One single Qwen-Image 2.1 native-maximum image (landscape 2752x1536 or portrait 1536x2752) showing one **true top-down orthographic view** of the unoccupied approved location — camera directly overhead, looking straight down at the floor, showing the complete plan layout with all surrounding walls. No header, title, footer, legend, caption, metadata block, or written annotation.

CAMERA_OR_PROJECTION
True top-down orthographic view from directly above, no perspective tilt: the complete footprint is visible, including every boundary wall and its orientation, door/opening positions, fixed furniture seen from above, permanent landmarks, and circulation paths. The view must show the fixed landmarks needed for later angle derivation: [LANDMARK_LIST].

SCENEPLAY_TO_SPACE_RULE
The screenplay may choose only empty areas and fixed landmarks already represented by the approved scene facts. A missing region or object is omitted from this asset version, not invented. Do not render characters, actions, handled objects, plot props, emotions, or story events.

COMMON_SENSE_BASE
[SCENE_COMMON_SENSE_BASE].

SCENE_FACTS
[ARCHITECTURE]. [FIXED_FURNITURE]. [PERMANENT_LANDMARKS]. [MATERIALS]. [PALETTE]. [TOPOGRAPHY_AND_LAYOUT]. Light: [TIME_OF_DAY_LIGHT_DIRECTION_QUALITY].

EMPTY_SCENE_CONTRACT
Architecture and fixed furnishings only; zero people, zero body parts, zero loose props, zero text or symbols.

BACKGROUND_AND_LIGHT
[IN_SCENE_LIGHTING_DESCRIPTION]. One coherent single-time-of-day lighting across the whole image.

EXCLUSIONS
No person, human silhouette, hand, shoulder, reflection of a person, or portrait/photo/TV image containing a person; no loose plot prop; no title, caption, camera term, label, number, letter, pseudo-text, arrow, logo, watermark, or frame.
```

### 3.2 逐机位派生编译模板（图生图，每次一个机位）

```text
TASK
Derive one additional camera-angle view of the SAME approved location, using <image1> (the approved scene master) as the identity source.

OUTPUT
One single Qwen-Image 2.1 native-maximum image showing one different camera framing of the same unoccupied location.

CAMERA_OR_PROJECTION
Change only the camera: [NEW_ANGLE_DESCRIPTION]. Everything else stays as in <image1>.

PRESERVE_EXACTLY
Keep the architecture, boundary walls, door/opening positions, fixed furniture and landmarks, materials, palette, scale relationships, circulation logic, and lighting identical to <image1>. The same objects keep their unique identity, count, material, orientation, and nearest-neighbor relationships.

ANCHOR_DIRECTION_RULE
Every directional statement uses the fixed subject's own front, back, left, and right, not screen-left or screen-right.

EMPTY_SCENE_CONTRACT
Architecture and fixed furnishings only; zero people, zero body parts, zero loose props, zero text or symbols.

EXCLUSIONS
No new room, no redesigned architecture, no changed material, palette, or lighting, no person, no hand, no loose plot prop, no text or labels or watermark, no frame.
```

### 3.3 交付形态

主图 + 派生图（按剧本需要的机位数）；需要多格时**机械拼合**为宫格（俯视/平面图可另出为独立辅助素材）。所有视图共享主图身份。

### 机位选择原则

主图负责空间总览并为后续派生留对照物；派生机位必须分别对应剧本中真正需要拍摄的区域、动作或接触关系，不按“客厅/厨房/餐区”机械凑格。某机位没有剧本依据时，不得加入。派生时每张只允许改变“机位”一个变量（其余写“与参考图完全一致”），保持项点到为止。

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
One Qwen-Image 2.1 native-maximum image (landscape 2752x1536 or portrait 1536x2752). Exactly four panels with clean separators. Panel 1: straight-on front view. Panel 2: one side view. Panel 3: back view. Panel 4: functional view showing the prop performing its core physical function. No fifth panel.

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

### 交付形态

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

每个状态都需身份一致性检查，不能只检查“动作对了”。所有最终扩展统一 Qwen-Image 2.1 原生最大尺寸（横屏 2752×1536 / 竖屏 1536×2752）。
