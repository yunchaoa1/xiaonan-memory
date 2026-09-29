---
name: minimax-h3-shot-prompt
description: Use when compiling approved shots into H3 prompts.
version: 0.3.0-rc
author: Hermes Agent
license: MIT
metadata:
  hermes:
    category: creative
    tags: [opc, minimax-h3, shot-prompt, asset-binding]
---
# MiniMax H3 Shot Prompt

## When to Use
Use when an approved OPC shot needs a MiniMax H3 prompt and asset-binding package.

## 官方规范（Singularity 模型自带，2026-09-15 取得）
`references/MiniMax_H3_Singularity_Prompt_Writing_Specification_Enhanced_EN.md` —— 来自 HF `WarmBloodAban/Minimax-h3_Singularity`，是 H3「**全参考图生视频**」的官方写作规范。与下文六段硬检查表互补，**冲突时以本规范 + 项目锁定口径为准**。四个最易漏的点：
1. **`<Subject N>` 与 `<Picture N>` 必须区分**：参考图**不自动等于第一帧**。只提供外貌/身份/服装/环境/风格关系的 → 一律写进 Subject 定义；只有真当首帧/关键帧/构图锚时才用 `<Picture N>`。
2. **retention 词汇表**：画面 = `fully_preserved`／`partially_preserved`／`attribute_transfer`／`weak_reference`／`newly_generated`；音频 = `fully_copy`／`partially_copy`／`reference`／`weak_reference`。
3. **多镜从第 2 镜起带时间戳**：`[Shot 2] At 00:03.000, ...`；第 1 镜不带。
4. **台词用稳定说话人号**：`(S1) speaks: "..."`／`(S2) replies: "..."`，跨镜保持一致。

另：动作要写**因果链**（准备→触发→加速→主动作→接触→反应→恢复→终态），运镜要写**五要素**（机位+运动+方向+速度/幅度+跟随对象），情绪要落到**可观察微动作**（眼/脸/呼吸/姿态/手/注意力）；禁 `cinematic`／`dynamic camera`／`cool VFX` 这类空词。

## 六段编译规则（写 prompt 时直接满足 — 2026-09-09 云电脑首测教训；以下每条都是 prompt 的写法，违反即该 prompt 不成立）

1. **每个 `<Subject N>` 定义点名来源参考图槽位**：写 `defined by <Picture N>` / `supplies her appearance from <Picture N>`（实测事故：Director 公共参考图已上传、prompt 未点名槽位，模型不跟参考图）。
2. **六段字段名裸写开头**：`subject_definitions:` 直接起行；**不用** `<subject_definitions>`…`</subject_definitions>` XML 包裹整段。尖括号只用于 `<Subject N>` / `<Picture N>` / `<d>` 三种标签。
3. **六段顺序与字段名固定**：subject_definitions → summary → retention_analysis → detailed_description → overall_soundscape → non_diegetic_music（summary 带 `[reference generation]` 前缀；retention 用 `fully_preserved - ` 官方标记）。
4. **`<d>` 格式**：`<d>[Chinese] 台词</d>`——`[Chinese]` 后带一个空格；台词句末有 `。？！`；无装饰标点/emoji/重复符号。
5. **单镜声明**：全镜只有一个 `[Shot N]` 时写 `The camera stays locked in this single continuous shot throughout, no cuts.`
6. **方位锚点**：画面方向以主体自身方向为参照（before her / behind him / to his right），不用 frame/screen/left of frame 表述。
7. **六段全英文**（仅 `<d>` 内台词保留中文）；长度 ≤7000 字符。

## Purpose
Compile one approved OPC shot into one MiniMax H3 per-shot prompt and asset-binding package. This node only compiles approved decisions. It does not write stories, adapt screenplays, design shots, create assets, run models, or judge media. Use the locked project style and the multi-view character/scene subject sheets when supplied.

## Input Boundary
Read only one closed, versioned shot package, its approved source records, locked asset references, and the selected dialect rules. Do not read chat additions, history, web pages, unregistered files, other projects, or secrets.

Required input:
- shot ID, schema/version, source IDs and hashes;
- approved action, camera intent, duration and mode;
- first/core/tail states and continuity;
- dialogue and audio events;
- ordered asset references with ID, version/state, role, URI/path, hash and approval/lock status;
- exactly one dialect and adapter version.

输入以这一份闭合包为唯一来源；不修补相邻镜头、不发明事实。

## Responsibility Boundary
Upstream owns story facts, screenplay, asset extraction, shot duration, camera plan, sound intent and state transitions. This node preserves and compiles them.

The executor owns credentials, queueing, provider calls, retries, downloads, task status and cost. The QC owner inspects actual media. A successful submission is not a successful video.

## Four Dialects

### MiniMax Cloud API
Compile the approved provider request shape with shot ID, prompt version, mode, duration, ordered conditions and explicit parameters. Authentication, submission, polling and download belong to the executor.

### ComfyUI Partner Nodes
Compile API-format graph inputs for the locked Partner template. Keep OPC asset IDs, versions, hashes and lineage beside any URI or slot mapping. Slot order is transport only, never identity.

### ComfyUI Native Nodes
Compile inputs for the locked local H3 T2V, I2V, FLF2V or R2V graph. Bind typed image/video/audio conditions without guessing model paths, sampler, resolution, fps or audio behavior.

### AIMixer Director
Compile external groups, segments, material ordering and shared prompt fields. Preserve OPC shot and asset identity outside Director numbering. Director reports are execution telemetry, not OPC truth.

## Prompt Compilation

The prompt must faithfully express only approved facts:

1. beginning state;
2. continuous core action in approved temporal order;
3. ending state;
4. approved camera intent;
5. dialogue and audiovisual cues.

### Official Ref2VA Six-Section Format (authoritative)

For full-reference shots (multi-view character/scene references — the local R2V/Ref2VA graph), compile the prompt body in MiniMax's official six-section rewrite format, in this fixed order with these exact field names:

1. `subject_definitions:` — one line per tracked reference (`<Subject N>` etc.), defining what the label denotes, its reference role, and the main features to follow. A multi-view character sheet stays ONE `<Subject N>` whose appearance follows the sheet; sheet layout, borders, panels and watermarks are never content.
2. `summary:` — one short paragraph, beginning with the `[reference generation]` task-type prefix, summarizing the target video and the roles of the reference assets using only already-defined labels.
3. `retention_analysis:` — one line per label, official marker only: `<Subject N> (appears in [Shot 1], ...): fully_preserved - <what is kept>`.
4. `detailed_description:` — the main body, shot by shot in playback order. Style is established in one or two sentences before `[Shot 1]`; later shots open with `[Shot N] At MM:SS.mmm, the shot cuts to ...` (cut times to the millisecond). Speakers keep stable `(Sx)` IDs; dialogue is written only inside `<d>[Language] ...</d>`, verbatim.
5. `overall_soundscape:` — 1–4 sentences summarizing ambience and physical sounds across the whole video.
6. `non_diegetic_music:` — 1–3 sentences of audience-only music (instrumentation, tempo, dynamics), or `N/A`.

Language rule (official, 2026-09-03 修正): all six sections are written in English — field names, reference labels, shot markers, millisecond timestamps, speaker IDs, `<d>` dialogue tags, retention markers, AND all descriptive content (subject appearance, actions, environment, camera-path prose, soundscape wording). Only dialogue inside `<d>` keeps its original language (Chinese). The earlier "Chinese body" deviation is void — it violated the official guide and was part of the prompt defect chain.

Authoritative unchanged copy: `prompt-master-pipeline/references/minimax-h3-ref2va-official-en.txt`.

### Performance Delivery Rules (human liveness)

Every emotional beat must resolve to performed micro-behavior. For each state in `detailed_description`, write the liveness trio:

- **eye_line** — gaze path with targets and shifts, never a fixed stare: eyes on the other person → flick away when the emotion hits → down to one's own hands → back up.
- **micro_action** — the hands and body do something specific while feeling: thumb rubbing an apron seam, knuckles curling, weight shifting to the back foot.
- **breath** — pauses are breathing, not stillness: chest rising and falling, an inhale held then released.

Dialogue delivery:

- Punctuation is the emotion code; only standard marks `，。？！`. `，` short breath stop; `。` falling close; `？` rising question; `！` burst. Break position = tempo point.
- Forbidden: tildes, repeated marks (`！！！`), emoji, decorative punctuation (the official guide requires their removal).
- Delivery lives outside `<d>`: pace (fast then slowing = emotion rising), pitch direction (rising/falling/shaking), breath pattern (deep inhale → held → then speak).
- Speech is never isolated: state the accompanying brows/gaze/gesture for each line.

### Self-Contained Group Prompts (per-group isolation rule)

Each director group is an **independent sample pass** — no frame/state context carries over between groups (r2v/v2v/rv2v: stock ReferenceToVideo, no motion-context pin). Write every group prompt as a self-contained video:

- Open `detailed_description` with the group's **starting visual state written out directly**: who is where, prop state (tissue already in hand / on table / absent), pose, gaze. Never open with a cross-group carry-over word such as "递纸后", "承接上一段", "after the previous shot" — the model will re-enact the previous group's action instead of starting from its result.
- Cross-group continuity is expressed as **written state**, not as an action sequence spanning groups. If a prop transfer must appear, it either completes inside one group, or the receiving group simply starts with the prop already transferred.
- Match-on-action cutting is safe **inside one group** (one sample pass remembers its own earlier frames); it is unsafe **across groups** (two independent samples). Do not split one continuous action across two groups.
- 4 组以上连拍时：段与段之间默认设"状态跳点"（每段起始状态可独立成立），不写跨段连续动作。

The executor may run the shot through the AIMixer Director plugin's r2v (reference-to-video) UI, which splits the final prompt into a shared block and per-group blocks that are concatenated. Distribute the six sections accordingly:

- **Shared params (公共提示词, auto-prepended to every group)**: `subject_definitions`, `summary`, `retention_analysis`. Reference images uploaded to the shared slots are the identity/environment sheets; cite them by their Picture-slot numbers.
- **Group prompt (每组提示词)**: `detailed_description` for that segment plus `overall_soundscape` and `non_diegetic_music`. Group-level images continue Picture numbering after the shared slots (shared Picture 1–3 → group starts at Picture 4); same-slot uploads override shared content.
- Reference images are addressed in the prompt as `<Picture N>` matching the upload slot (or `@` auto-completion in the Director UI). `<Subject N>` stays the stable identity label; each `<Subject N>` definition names the `<Picture N>` slot it comes from.
- fl2v (first/last-frame) segments: write only the middle motion/camera/transition in the prompt; never write "keep the first/last frame" lock phrases — the plugin injects the hard lock itself.

### Official Prompt Syntax Rules (官方语法规则 — 2026-09-03 定稿，源自官方 h3-prompt-writing skill 与 ref-en.txt 全文)

来源：MiniMax-AI/MiniMax-H3 官方仓库 `skills/h3-prompt-writing/references/ref-en.txt` + 社区 landon2022/minimax-h3-prompt-writer + AIReiter 官方指南。以下每一条都有官方原文对应。

1. **六段全英文**：subject_definitions/summary/retention_analysis/detailed_description/overall_soundscape/non_diegetic_music 全部英文书写；**仅 <d> 内的台词/歌词保留原文语言**（我们=中文台词）。"骨架英文血肉中文"作废。
2. **故事板 Picture 官方写法**：`<Picture 4> is a storyboard reference for [Shot 1] and [Shot 2], defining their viewpoint, subject placement, and shot order.` ——只写"提供什么规划信息"，**永远不写"宫格/边框/第X格/从左到右"**，不把格内容写进定义。
3. **detailed_description 引用 Picture 只在内容出现点**——绝不写"构图对应 <Picture 4> 第一至第四格"这类映射（诱发宫格渲染）。
4. **单镜头显式声明**：全镜只有一个 [Shot N] 时，写 "The camera stays locked in this single continuous shot throughout, no cuts."（官方：request 'no cuts' wording for single-take shots）。
5. **切镜只在实质变化处**：cut 仅用于视点/状态/空间/时间的实质变化；cut 语言只用 "the camera cuts to" / "the shot transitions to" / "the shot switches to"。
6. **场景 Subject 单空间**：`<Subject 3> is the home kitchen with its wooden counter, sink, and warm overhead light.` ——一镜一空间，只写该镜实际出现的空间。
7. **每个 shot 写死三件**：表情 + 手部动作 + 手持物（官方示例每个状态都有，如 "She smiles and raises the cookie in a small toast-like gesture"）——不留白，模型就没有空间自创（历史：母亲自创手绢抹泪）。
8. **detailed_description 开篇 1-2 句风格句**：`The target video uses a 3D animated film style with warm kitchen lighting at night.` 然后才 [Shot 1]。
9. **retention_analysis 官方格式**：`<Subject 1> (appears in [Shot 1], [Shot 2]): fully_preserved - 具体保留哪些特征`（"- "后写保留内容）。
10. **对白标签**：身份/动作/语态在 <d> 外；<d> 内只有 [Chinese] 台词原文；说话角色首次出现带 (Sx) 稳定 ID；非说话角色写明确不说话（如 "silent, her lips closed"——同款规则用于手部：写死手部状态）。
    - **<d> 空格格式（官方原文 line 220 + 全部官方示例）**：`<d>[Chinese] 台词</d>` —— `[Chinese]` 后**必须带一个空格**（官方原文："Write dialogue and lyrics as `<d>[Language] ...</d>`"；官方示例全是 `<d>[English] Last summer, ...</d>`）。禁止删这个空格（2026-09-03 教训：小南凭直觉删了 43 处空格，对照官方原文发现删错了，已回滚）。
    - **标点净化（官方原文 line 274）**：完整句必须句末标点（`。？！`）后再 `</d>`——"妈"→"妈。"合规；`……`→`，`合规；删除重复标点/表情/装饰符号。
    - **长台词拆段**：按时间戳/节奏可拆多段 `<d>`，每段仍完整包裹；拆段后拼接必须与卡台词逐字一致（检查脚本按拼接对比）。
11. **Prompt ≤7000 字符**；六段顺序固定不可乱。
12. **六个落项（写 prompt 时直接对齐；源自官方 checklist）**：①每个资产图只承担一个明确角色；②模式/时长/画幅/时间线彼此兼容；③身份/服装/道具/地点跨切镜一致；④每句台词长度适配该镜时长；⑤音轨分类正确且无多余 BGM；⑥帧锚点落在声明的 shot/时间上。
13. **方位锚点（凡哥铁律，2026-09-03）**：画面内方向一律以**主体自身方向**为锚点——`the closed door directly before him`、`half a step behind him to his right`、`in front of her`。禁止以画面/镜头为参照系：`left of the frame`、`on the right side of the screen`、`at the left edge of the picture` 一律改写为主体参照。

## Reference Image Usage Rule (参考图使用规则 — 2026-09-03 修正版)

**四视图资产图与四格故事板都是主流成熟做法，可以正常用作参考图**（凡哥定论）。历史事故的分屏/双人物根因**不在参考图结构，在提示词写法**（见上官方语法规则 1-7）。此处只定参考图使用纪律：

1. 每镜只传该镜出场的图：S01 无母亲 → 不传母亲图；无台词动作镜不传无关图。
2. 场景资产图（多空间宫格）仍可整张传，但 Subject 定义只写当镜单空间。
3. 故事板图整张传，绑定写法按官方语法规则第 2 条。
4. 参考图顺序固定：人物图 → 场景图 → 故事板图 → 道具图，与 <Picture N> 编号一一对应。
5. 历史教训：v3 时代把分屏根因错判为"180° 翻转提示词/四格参考图结构"——真根因是提示词写法（宫格映射语句诱发宫格渲染）。诊断必须查官方依据，不脑补。

Never write a turn-around (front→back ~180° flip) inside one segment. With multi-view reference sheets (front/back side by side), a turn-around prompt makes the model render BOTH views simultaneously — a left/right split screen of the same character doing the same motion. Rules:

- One facing orientation per segment; small angular shifts only.
- Back views enter as established states: write the character as ALREADY back-facing at segment start, never shoot the turning process.
- Front emotion + back-view exit = two segments (A ends front-facing at peak; B starts back-facing as established state).
- Prefer side profile / medium / back view over continuous face close-ups when stability matters.

### Shot Count Stability Default

Official H3 guidance: 5-10s segments with one subject and one main action use at most 2 `[Shot N]` cuts. Extra cuts are allowed only with real motivation (emotion beat, reverse shot, rhythm cut) and accept lower stability.

State evolution stays **inside one [Shot]** by default: continuous action + emotion progression + small camera moves (`Push In / Tracking Shot with small amplitude at slow speed`), advancing through millisecond timestamps. **Do not advance states by cutting to a new [Shot].** The storyboard grid panels are state-frame references for the shot — not cut points.

A new `[Shot N]` = one real cut, requiring a motive: emotional beat (change distance), narrative shift, rhythm point (beat-sync cutting allowed), eye-line transfer (shot/reverse-shot), or a large shot-size/angle change. When cutting, the shot-size change must be large (wide↔medium, medium-close↔close-up, reverse angle, side↔front); **never cut to a slightly closer variant of the same angle** (Murch's beehive: the most disorienting cut). No hard cap on cut count — cut whenever there is a motive.

**切镜必须携带新信息或情绪**：每次写 `the shot cuts to` 时，该切镜必须带来新的信息或情绪变化；无新信息就不切，改写为同一镜头内的连续动作。

### 占框与尺度稳定（2026-09-24 增；治"大小比例忽大忽小"；社区共识 + 模型官方指引）

- **占框写进 prompt**：每个 [Shot] 声明主体占画面高度百分比（`the figure occupies about 30 percent of the frame height`）＋**头顶留白**（`comfortable headroom, eyes on the upper third`）——不写，模型每次自己猜（30% 还是 85% 随机）。
- **首帧锚定优先**：同一场的各镜尽量从**同一张标准帧（构图锚点）**衍生，跨镜只改表情/手部/微动作，不换占框、不换机位（一个世界，锁首帧，衍生所有镜头）。
- **镜头顺序先近后远更稳**（Reverse Framing）：特写对位置误差最敏感（5% 偏移在广角看不出、在特写就切额头）——先把最难的近景锁死，再往远景走。
- **运镜幅度量化为小**：写"推近约 15% 画面宽 / 4 秒"这类可核验小量；大幅运镜人物易崩（本机实测），优先小幅慢速（`small amplitude at slow speed`）。
- **不写"居中"**：不写 subject centered——会与画面自带空间线索冲突致抖；位置写坐标或相对主体方向。
- **尺度连续性靠措辞钉住**：同一角色/道具在全片用**逐字相同**的尺寸与位置写法（换词=漂移）。
- **禁止裁剪放大冒充景别**：不用中景裁剪放大当特写（透视崩）；每个景别独立构图。

### Storyboard Keyframe Binding (mandatory — official phrasing)

Every shot's approved storyboard keyframe grid is a `<Picture N>` shot-planning anchor and MUST be bound as a reference image (the whole grid, uncropped). Official phrasing (ref-en.txt §2.2):

`<Picture 4> is a storyboard reference for [Shot 1], defining their viewpoint, subject placement, and shot order.`

Rules:
- State WHICH shots it maps to and WHAT planning info it provides (viewpoint / subject placement / shot order) — never describe panel contents, never mention "grid / borders / panels / left-to-right", never map panels inside detailed_description ("corresponds to the second panel" is forbidden — it induces grid rendering).
- In `retention_analysis`, mark it `partially_preserved` - its viewpoint, subject placement and shot order are realized; layout details never enter the final frames.
- In `detailed_description`, reference it only where the planned content actually takes effect (per official guide: "the points where referenced content actually appears or takes effect").

Use stable asset references for subjects and props. Do not add a beat, motivation, character, prop, camera idea, setting, style or visual fact. Keep structured fields beside readable prompt text.

Carry supplied state changes literally, such as complete→broken, held→scattered or visible→mud-covered. Preserve identity master, state snapshot, scene, prop, group and ability as separate bindings.

Preserve the upstream high-attractiveness identity block when no screenplay exception is
present. Use the approved facial-detail reference for facial identity and the three full-
body views for proportions; do not replace these with a generic beauty adjective.

For multi-view consistency, label each reference with its job: character identity/front/side/back,
facial-feature detail, scene structure/landmark, style, or concrete keyframe. Use the same stable subject across
views and state the invariant features to preserve. Ordinary props such as food, filling,
rolling pins, cups, pots, and vinegar remain in the shot description with explicit scale,
holder, contact, and action relations; they do not require separate references unless
upstream marks them continuity-critical.

## Output Contract

输出一份完整编译包（本节点只产出编译结果）。

A successful compile contains:
- status `SUCCESS`;
- package and prompt schema versions;
- shot/source IDs and hashes;
- selected dialect and adapter version;
- compiled prompt, language, mode and duration;
- first/core/tail state timeline;
- ordered asset bindings with IDs, versions/states, roles, hashes and transport mappings;
- unchanged dialogue/audio structures;
- executor handoff;
- `execution_status: NOT_RUN`.

输出不声称已渲染视频、已做运行时 QC 或已获人工验收——执行与验收属节点外环节。

## 编译前提（输入事实，由上游闭合包提供；本节点只读、只编译，不判定不阻断）

1. Shot 与来源的版本、批准、哈希与闭合边界；
2. 时长、模式、动作、运镜意图、状态时间线、台词、音频与连续性；
3. 每个可见主体/场景/道具/群组/能力的已批准锁定绑定；
4. 资产 ID、版本/状态、哈希、角色、顺序与血缘；
5. prompt 不新增未批准事实、不遗漏必需事实；
6. 恰有一个受支持的方言与适配器版本；
7. URI/槽位映射保留 OPC 身份、不依赖槽位次序；
8. 输出完整、`execution_status: NOT_RUN`、不声称媒体验收。

## 参考样例（历史三镜包，供写法对照；非门禁）

样例包路径：
- `D:\Hermes\xiaonan-memory\opc-mvp\05_h3_prompt_package\h3_prompt_package.json`
- `D:\Hermes\xiaonan-memory\opc-mvp\03_storyboard_timeline\opc_shots.json`
- `D:\Hermes\xiaonan-memory\references\reuse-scout\video-pipeline-reuse-scout-v0.1.md`

该样例含三镜、四个方言声明与 `selected_dialect: aimixer_director`（仅作写法对照）。

