---
name: gpt-image-subject-assets
description: Use when compiling approved OPC asset manifests into one direct GPT Image subject-asset sheet (character 4-view, scene 4-panel, or prop).
version: 0.3.0-rc
author: Hermes Agent
license: MIT
metadata:
  hermes:
    category: creative
    tags: [opc, gpt-image, subject-assets, direct-generation]
    related_skills: []
---
# GPT Image Subject Assets (Direct Generation)

## Style Selection

Use `references/opc-style-and-asset-tiering-v0.1.md`. GPT Image has no fixed official
style menu; OPC presents five customer-friendly directions: 3D animated film, Japanese
anime, Korean full-color webtoon, Chinese ink/gongbi, and realistic cinematic concept
design. Lock one project style before generating characters or scenes and carry the same
style descriptor into every asset request.

The style is a platform-level global parameter chosen outside the node through a
customer-facing dropdown (`style_id`), inherited and never chosen or changed by this node.
It is adjustable across the project lifetime without rewriting subject facts. Character,
scene, and prop visible facts are decoupled from style: switching style changes only the
rendering language, not facial geometry, hairstyle, wardrobe structure, spatial topology,
materials, or palette logic. When compiling prompts, fill the `[STYLE]` placeholder with the structured style declaration for the locked `style_id` from `opc-style-prompt-vocabulary-v0.1.md` (style name + 2-3 key traits + one explicit exclusion, placed near the front of the prompt) — never a bare label such as "3D animated film style" (drifts toward realistic CGI), and never an over-stuffed keyword stack (GPT Image 2 uses a reasoning layer and wants minimal prompting).

## High-Attractiveness Character Baseline

Unless the approved screenplay marks an ugly comic role or another appearance exception,
use `references/opc-high-attractiveness-character-rules-v0.1.md`. Encode attractiveness
through stable observable facial geometry, balanced feature proportions, clear eye shape
and spacing, defined nose/lips/jaw, readable hairline, healthy natural skin, stable body
proportions, and coherent clothing. The face detail reference has highest identity priority.
Do not use "beautiful" or "handsome" as the sole specification, and do not turn every
character into the same face.

## Purpose

Compile one approved upstream asset specification into one direct GPT Image subject-asset
sheet for one character, scene, or prop. The node generates the final asset in one pass; it
does not first produce a separate template and then expand it. It owns only fixed-rule prompt
compilation and image generation.

## Boundary

This node is a closed black-box production function with one single job: read one approved
upstream asset package/version, apply its own fixed rules, generate the designated visual asset
**once**, and deliver it. It does not read chat messages, customer requests, platform-side
instructions, other project files, or unapproved drafts. It never interviews or proposes
options. It never generates a second image for the same asset in one run.

A customer-requested local rewrite is a platform-model and version-orchestration concern, not a
node capability. The platform creates a new controlled approved input version, then this node
runs the same fixed rule again. Every prompt fact must resolve to a source field or a rule in
this Skill.

## Required Input

Input is one versioned JSON-like request containing:
- `node_run_id` and `prompt_schema_version`;
- approved `source_manifest[]` with path/URI, version, approval status, and SHA-256;
- `asset_spec` with `asset_id`, `asset_type`, `spec_version`, and `state_version`;
- sourced `visible_facts`, `required_invariants`, `allowed_changes`, and `explicit_unknowns`;
- controlled runtime `provider`, `runtime_model_id`, endpoint, and credential reference;
- requested size, quality, background, and output format;
- ordered `reference_images[]`, or an explicit empty list.
A credential reference may identify a secret but must never contain a secret value.

## Input Interpretation

A character input supplies stable visible identity facts and a declared state delta. The character's
stable visible identity facts (facial geometry, hair, skin, body proportions, wardrobe structure, and
worn accessories) come from two lawful sources only: (a) the visible fields of the approved upstream
asset package (identity masters and character snapshots), or (b) a customer-supplied appearance
specification delivered by the platform as a new controlled input version. The node never interviews,
prompts the user, or invents these facts. When neither source provides enough stable visible identity
facts to compile a four-view sheet, return `ASSET_BLOCKED` and do not infer appearance from occupation,
kinship role, or dramatic personality. A scene input
supplies spatial core, orientation/topology, visible anchors, and requested views. A prop input
supplies repeatable geometry, material, structure, state, and its social-use context when that
context is sourced by the approved upstream package. For wearable or carried props, that context
may include the user's life stage, era, daily environment, carrying need, and visible history of
use. These facts guide a common-sense design inference without becoming a literal occupational
costume. Explicit unknowns remain absent from the compiled prompt. The node does not resolve
missing information through questions, self-diagnosis, or invented design; it applies only the
declared input and fixed Skill defaults.

## Style Lock (凡哥 2026-09-04 定稿 v2)

项目 style_id=`3d_animated_film` 时，prompt 必须用**中国 3D CG 动漫锁风措辞**（国漫 3D 动画风：《凡人修仙传》《雄狮少年》质感——3D 建模+东方审美，非皮克斯非写实）：
- 结构：`Chinese 3D donghua animation style, Chinese 3D CG anime character, oriental facial features: oval face, refined phoenix eyes, slender small nose, slender realistic 7.5-head-tall proportions, elegant smooth skin, fine detailed hair strands, refined fabric folds, cinematic CG render, soft warm lighting, gentle depth of field`
- 显式排除（凡哥实测去皮克斯）：`not Pixar style, not Disney style, not western cartoon, no rounded chubby body proportions, no big circular western eyes, not photorealistic, not realistic skin pores, not flat 2D cel anime, no ink outlines`
- **禁用写实渲染词**：subsurface scattering skin / PBR material detail / volumetric lighting 会漂向写实 CG（凡哥实测），不得单独使用；要 3D 质感用 "Chinese 3D donghua cinematic render"。
- 凡哥历次纠正：裸标签漂 2 次元 → subsurface/PBR 偏写实 → large eyes/rounded 偏皮克斯欧美。**东方五官+修长比例+国漫渲染三锚点缺一不可**。
- 每张资产图的 prompt 都带这组锁风措辞，与 `references/opc-style-and-asset-tiering-v0.1.md` 的结构化风格声明合并使用。

## Universal Pure-White Background Rule

Every subject-asset image uses a pure-white canvas background (`#FFFFFF`) for every asset type.
Characters and props are isolated directly against pure white. A location keeps its approved
interior materials inside the floor-plan or camera-view footprint, while all unused canvas,
outer margin, panel backing, gutters, and separators are pure white. No gray, beige, colored,
transparent, textured, gradient, environmental, checkerboard, or decorative background is part
of the generated asset specification.

## Asset Sheet Contract

All deliverables use **16:9 native 4K, 3840x2160** and a pure-white (`#FFFFFF`) canvas, panel
backing, gutters, and separators. Do not upscale and call it native 4K.

**Grid Format Rule (凡哥 2026-09-04 定稿 v2，边框稳定约束)**：任何多面板宫格图（四视图人物/四格场景/四视图道具）：
- **子图间分割线**（prompt 必写）：`uniform ultra-thin hairline dividers between panels, every divider exactly the same 1mm thickness, thin light-gray hairline lines`——每根线同粗细，禁粗细不一。
- **宫格外无边框**（prompt 必写）：`no outer frame, no outer border around the whole sheet`。
- **禁止项**（凡哥实测边框粗细不稳定，prompt 必写）：`no thick borders, no black frames, no comic panel outlines, no double lines, no colored dividers, no decorative edges`。
- 子图本身无描边，画面直达细线。

## Character Sheet

Principal character assets are a four-panel multi-view set, not a single portrait: exactly three
full-body standing views (front, one side, back) plus one enlarged facial-feature detail view.
"One side" means one side view only; never split it into left-side and right-side views. The face
detail is the highest-priority identity reference.

**State-Version Rule (凡哥 2026-09-04 定)**: a changed outfit or an injury state is a new state
version — generate a complete new four-view character sheet of the same person wearing the full
new outfit, or with the injury on the body. Never render clothing as a separate wearable prop
sheet to composite onto the character, and never render an injury (bandage/wound/blood) as a
standalone patch sheet: reference images are always fully dressed, complete people, because
combining clothes or wounds onto a base body is unacceptable.

**Accessory Boundary (凡哥 2026-09-04 纠偏)**: removable accessories (hat, scarf, glasses,
handbag) are PROPS, not outfits — they never trigger a character state-version sheet. The
character sheet is always the accessory-free baseline; wearing states are combined downstream
at the storyboard/staging level by referencing the character sheet + the prop sheet together.
Only an actual clothing change or a body injury justifies a new character state version.

Establish sourced facial geometry, hair, skin, shoulder/upper-body proportions, current wardrobe
structure, worn accessories, and visible expression. Classify each visible fact as SOURCE_FACT,
DERIVED_DEFAULT, or UNKNOWN. A DERIVED_DEFAULT is allowed only when the approved identity/state
strongly entails a minimal, reality-grounded consequence. The standard for every DERIVED_DEFAULT
is plain common sense — what an ordinary person would regard as reasonable for that identity and
state, never a counterintuitive or attention-grabbing choice. Examples: a recently discharged
serviceman gets a short crew cut (板寸) with tapered sides and nape; a middle-aged homemaker gets
natural fine lines and a few white strands. Write the derived fact precisely (use "crew cut", not
"short hair") so the model actually enforces the detail instead of blurring it into a generic term.
External props are a separate responsibility and are absent. Do not infer bags, props, decorative design, or unrelated
biography from occupation or relationship. Keep age, clothing, hair, body proportions, palette,
style, and stable identity anchors consistent across the set.

## Scene Sheet

A scene asset is one unlabeled four-panel empty-location sheet. Top-left is the actual interior
top-down view of the approved scene (the shared spatial truth). The other three panels are
selected in-scene detail views derived from screenplay actions, fixed landmarks, character
staging, and required prop contact. All four panels belong to the same scene and preserve its
spatial identity.

The screenplay selects which empty spatial regions and fixed landmarks must be visible. It does
not authorize rendering characters, body parts, actions, plot props, shot labels, captions, or
storyboard annotations. Every panel is an unoccupied location view containing architecture,
fixed furniture, and permanent landmarks only. People, performance, handled objects, and prop
contact enter later in the storyboard node. Plot-critical ordinary props remain deferred to
storyboards.

### Common-Sense Base + Screenplay Addition

Establish a believable common-sense base first, then add the screenplay's fixed structures.
For a modern home, a living-room base normally includes a sofa seating area, a low coffee
table, a television on a low console, and a usable open activity area. A kitchen base reads as
a usable kitchen with its worktop/chopping-board area, hob, sink, and normal counter line. A
dining area reads as a usable dining area with a table and ordinary chairs. These are everyday
common-sense impressions, not a checklist. Incidental plants, ordinary furniture, small
appliances, and household details may appear when they are consistent with the dwelling and do
not contradict the screenplay; they do not trigger rework for quantity or unnamed source.

On top of that base, add only the screenplay's extracted fixed structures, such as an entrance
door with a clear wall-side area for a bag, a window sill with a green pothos, a washed-blue
dining cloth, a hob, or a chopping-board worktop. Do not render the extracted structure list
as an empty room; the base must remain recognizable and usable.

### Subject-Centered Spatial Anchoring

The scene compiler expresses cross-view consistency through visible subject anchors, not
camera-relative words alone. For each panel:

1. Select one visible fixed subject from the scene's visible fixed landmarks as the panel anchor
   (entrance door, sofa, coffee table, TV console, kitchen worktop, hob, dining table).
2. Describe every other visible fixed object from that anchor's own front, back, left, or right.
   Object-relative directions do not rotate when the camera moves.
3. Repeat the same object's unique identity, count, material, orientation, and nearest-neighbor
   relationships in every panel where it is visible.
4. A camera change may alter screen-left/screen-right, projection, occlusion, crop, and visible
   range only. It must not change real object coordinates, adjacency, orientation, or quantity.
5. Use at least two shared fixed landmarks between neighboring panels whenever the approved scene
   makes them visible.
6. Relationships unsupported by the approved scene facts remain unknown and are not invented.
   Plot props are not promoted into fixed landmarks.

The top-left overview is the shared spatial truth. Each detail panel must be reversible: its
anchor and visible neighbor relationships must map to one unambiguous position in that overview.
Each panel repeats the empty-location contract independently: zero people, zero body parts, zero
text, zero labels, zero numbers, zero arrows, and zero loose plot props.

## Prop Sheet

A prop asset is a four-panel multi-view set, not a single front view: exactly four panels in one
16:9 native 4K sheet — straight-on front, one side, back, and one functional view. The functional
view shows the prop performing its core physical function (for example, a bag with its main
compartment opened, a lighter with the flame lit), derived from the prop's sourced physical
function rather than its story meaning. Establish silhouette, proportions, material, color, part
count, fasteners, controls, and current state. If the screenplay requires visible functional
states, the functional panel shows the primary function state; additional function states are
separate sheets with invariant parts and changed parts explicitly recorded. Ordinary keys, cups,
food, utensils, and generic household objects remain shot-level bindings. For wearable or carried
props, derive common-sense positioning from sourced user life stage, era, daily environment,
carrying need, and use history; do not equate occupation with military design or gender-coded color.

## Prompt Compilation

## One-Shot Generation Rule (凡哥 2026-09-04 定)

每个 asset_id 只调**一次**生成，结果生成后**立即交付并登记**。禁止重新生成、筛选、
择优、修图、或任何形式的"不满意再来一张"——节点没有第二次机会。生成一张 = 交付一张。

1. Read the selected asset's approved visible facts and explicit unknowns.
2. Select the matching sheet job (character / scene / prop).
3. Compile the fixed prompt in the order: task, output, camera/projection, visible facts,
   layout/topology, invariants, allowed change, background/light, exclusions.
4. Send one generation request with the controlled runtime settings.
5. Output the generated image.

## Prompt Rules

The prompt contains only sourced visible facts, required invariants, the current state delta,
and neutral presentation wording. It may describe framing, plain presentation, or a clean
background for subject presentation. It must not add biography, motivation,
cinematic action, setting history, symbols, text, decorative architecture, or style facts.
Unknowns are not negative prompts and are not silently filled by model convention. Preserve
them as unknown in the fact map; use neutral wording only when it does not assert a value.
Keep external props, abilities, and scene bindings outside the identity master prompt.

## Runtime Resolution

Use the controlled runtime provider, model ID, endpoint, output size, quality, background, and
format supplied by the platform. The node generates at the requested output size. Runtime
telemetry, file validation, acceptance, and asset lifecycle management belong outside the Skill.

## Output

Output the one generated image for the selected asset. Delivery, storage, and versioning of the
delivered asset happen outside this node.

## Prompt Templates

Use `references/prompt-compilation-templates-v0.1.md` for the character, scene, and prop sheet
prompt structures.
