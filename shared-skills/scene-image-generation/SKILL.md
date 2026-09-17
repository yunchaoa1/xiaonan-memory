---
name: scene-image-generation
description: AI生图场景图规范——MV场景统筹、z-image出正面平视图、Qwen2511拓展其他角度。凡哥说"先生成场景图"时自动加载。
category: creative
---

# 场景图生图规范

## 平台职责先锁定

开始生图前必须确认视觉媒介与平台分工，不能看到“短剧”就默认真人写实。

对于3D动漫短剧的推荐职责拆分：

- GPT Image 2：人物、场景、道具主体底板设计；
- Nano Banana：换装、改年龄、场景状态变化、4/9宫格故事板、首尾帧与关键帧二创；
- 视频模型：只负责动态、运镜、声音与连续表演，不承担重新设计主体。

主体底板确认后，再做年龄和服装派生；幼年角色优先由成年角色底板做年龄变化，保留家族五官，不重新随机设计一张儿童脸。

故事板必须输出两版：导演标注版含镜号、箭头和站位；模型纯净版移除文字、箭头和格号。给支持多图参考的模型时，优先拆出单独关键帧，整张宫格只用于导演统筹。

站位俯视图与写实/3D故事板分开：俯视图用点、线、面和颜色表达人物、道具、摄影机、视场与移动方向，主要服务提示词推导和连续性检查。

## Common Layout Defaults and Screenplay Overrides

For modern residential scenes, establish a believable common layout as the base, then apply only
screenplay changes that affect space, access, safety, or staging. A living-room base normally
includes a television area, seating, a useful activity/circulation area, and ordinary household
furnishing at a plausible quantity. An open living-kitchen-dining scene may combine those zones
when the screenplay requires it. A kitchen base should read as a usable kitchen with its normal
work surfaces and essential fixtures; a dining area should read as a usable dining area.

These are common-sense defaults, not a demand to count every visible object. Plants, artwork,
small appliances, chairs, shelves, and ordinary household details may appear when they are
consistent with the dwelling and do not contradict the screenplay. They do not require separate
source proof or a rule change merely because the image contains them. The template QC asks only
whether the space is recognizable, usable, and free of material contradictions such as an
impossible layout, blocked access, duplicate structure that changes the room, or a dangerous
staging problem.

Plot-critical objects are not part of the location template by default. Food, utensils, bags,
keys, documents, tools, and similar ordinary objects are introduced at storyboard or shot
binding stage when the action requires them. The storyboard controls their exact presence,
state, holder, contact, and movement path. Add an object to the location template only when it
is a permanent spatial landmark or is necessary to understand the room's fixed function.

The screenplay overrides the common base only when it explicitly requires a different era or
regional layout, unusual placement, absence, structural change, safety constraint, or a fixed
landmark needed for continuity. Record meaningful overrides as `SCREENPLAY_ADDED`,
`SCREENPLAY_REMOVED`, or `SCREENPLAY_REPOSITIONED`; do not record incidental decoration.

## Portal-Only Scene Boundary

When the active scene is a hub room, distinguish `MAIN_SPACE` from `PORTALS`. Render exactly
one main space. A portal is only a door, doorway, threshold, or short blank circulation strip;
its destination room remains outside the frame and has no furniture, fixtures, colors, or
interior dressing. Do not put destination room names into the visual prompt as if they were
rooms to render. In the structured input, store the destination as metadata (`portal_target`)
and compile only its geometry into the image prompt.

If the model repeatedly renders portal destinations as rooms, stop text generation and use a
programmatic floor plan or a 3D blockout with the main room rendered and portal openings left
blank. The result is a valid spatial placeholder source; a decorative but semantically expanded
floor plan is not. For hub-room templates with several portal connections, the programmatic plan
is the preferred fallback because exact wall, door, portal count, and circulation geometry are
more important than generated decorative detail.

场景资产按单个拍摄场景建立，但要保留该场景在住宅或建筑中的空间角色。客厅作为住宅核心时，客厅本身是唯一完整展开的主体；入口、厨房、餐区、卧室、卫生间、书房、储物间、走廊等功能空间只以对应的门、门洞、短门槛和空白动线接口表示，不展开内部。其他空间名称只作为结构化数据中的`portal_target`，不能直接作为提示词里的可见房间内容。若当前场景不是核心空间，则完整展开当前场景，并保留它与核心动线的必要连接点。不同拍摄场景即使属于同一个家，也分别建立场景模板和ID。
俯视场景模板同时作为该单一场景的占位图模板：记录当前场景的墙体边界、门窗/开口、固定家具、关键地标、人物活动区、内部动线、尺度、材质、主色和后续机位位置。模板尺寸按场景形状和展示区域自适应，不强制16:9；正式扩展图统一16:9原生4K。
## 平台选择

| 平台 | 适用场景 | 语言 | 格式 |
|------|------|------|------|
| GPT Image 2 | 场景母版设计；基于母版逐角度编辑 | 英文 | 先单张母版，后逐视角生成并机械拼格 |
| z-image | 单视角正面平视图（后续Qwen扩展） | 中文 | 单图、1664×928 |
| Qwen 2511 | 基于锁定母版拓展其他角度 | 中文 | 每次都继承同一原图 |

凡哥说"先生成场景图"：先确认用哪个平台，再执行母版锁定流程。GPT Image 2=先单张空间母版，再基于同一母版逐角度编辑，最后机械拼格；z-image+Qwen=先单张母版，再继承同一原图逐角度拓展。

## 生成流程

1. **读完整分镜脚本** → 按空间归类拍摄场景与常识空间关系
2. **建立场景常识底座**：确定空间边界、固定结构、基本家具、活动区、动线和机位接口；不提前穷举剧情道具
3. **z-image 出正面平视图**：中文自然语言、16:9横版、8K超高清、No characters、不写光线
4. **Qwen 2511 拓展其他角度**：基于正面平视图生成侧面/背面/俯视；剧情道具在故事板阶段按镜头动作加入

## z-image 提示词规范

- 中文自然语言，只做正向描述。禁止否定词（不/别/没/无/非/否）
- 不写光线方向和色温（留给LTX视频处理）
- 写画面清晰度：8K超高清画面细腻锐利
- 结尾：`16比9横版。No characters。`
- **场景图给全景**——展示整个空间，不是某个角落或道具特写

## 道具三视图格式

单独物品（如小熊、礼物盒）用横排三视图：左格正面、中格侧面、右格背面，纯白背景，1mm白色细线分隔。

## AI短剧故事板参考图

当任务是短剧逐镜故事板，而非单纯场景图时，先加载`shot-language`并完成生产级分镜，不能直接从剧本跳到生图提示词。

- 4宫格：单人、单动作、普通对话；固定为起始构图→动作触发→核心动作／情绪峰值→结尾停点；
- 9宫格：多人、道具交接、灾难或复杂空间运动；
- 每套故事板生成导演标注版和模型纯净版；
- 导演标注版可含镜号、人物名和运动箭头；
- 模型纯净版去除文字、箭头和格号；
- 真正喂视频模型时，优先把关键格拆成独立图片，不把带字拼图当写实首帧；
- 站位俯视图与写实故事板分开制作。俯视图用于机位、视场、人物运动和提示词推导，避免污染写实画面风格；
- 每镜先确认首帧、核心帧、尾帧和剪辑接口，再写生图提示词。

详细规则见 `shot-language` 技能正文中的分镜工作流。
