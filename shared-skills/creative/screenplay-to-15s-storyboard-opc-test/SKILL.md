---
name: screenplay-to-15s-storyboard
description: "Use when converting an approved screenplay into a production-ready storyboard shot package of 15 seconds or less."
version: 0.3.0-rc
author: Xiaonan
license: MIT
metadata:
  hermes:
    tags: [storyboard, shot-list, opc, fifteen-second, continuity]
    related_skills: [screenplay-to-15s-storyboard-opc-test, shot-language]
---

# Screenplay to 15s Storyboard

## Overview

Convert one approved screenplay package into one structured storyboard shot package. Decide shot boundaries, timing, staging, emotion, sound, grid density, and continuity interfaces.

This node does not rewrite the story, create image or video prompts, generate media, choose model parameters, or build a platform. It produces the smallest complete handoff that a later asset, image, or video node can execute.

## When to Use

Use for an approved screenplay that must be divided into AI-manga storyboard shots.

Do not use for novel adaptation, screenplay writing, asset generation, prompt writing, media rendering, or platform/database/runner implementation.

Project defaults are 16:9 horizontal, one generation task per shot, and dialogue and sound assigned for downstream execution. Inherit an upstream lock when it explicitly differs and record its source.

## Input Gate

Require a screenplay package with scene and beat IDs, action, dialogue or sound, causal result, character state, prop state, and source trace.

Reject with `INPUT_ERROR` when scene boundaries, actions, or state information are missing. Unknown identity, causality, or state remains unknown; do not invent it.

The package may reference approved identity masters, story-state versions, locations, props, abilities, and accepted tail frames. Missing required locked assets block the shot card with `ASSET_BLOCKED`.

## Core Limits

Every shot must satisfy all of these limits:

- generated duration `<=15s`;
- dramatic core duration `<=14s`, leaving edit safety;
- one continuous space and one narrative objective;
- one core action and one primary camera movement;
- normally one main speaker;
- one causal or emotional state change visible at the end.

The duration rule is hard. The five-part emotional beat template is a staging aid, not a promise about fixed seconds.

## Execution Path Lock (2026-09-04 凡哥定，锁定生成方式)

拆镜框架是**项目已定决策**，重跑禁止重新推演。生成走固定四步：

1. **读上游一次读全**（剧本+资产包+skill），不允许反复读文件。
2. **按固定框架逐镜写卡**：框架=29 镜正反打 A 方案（S05a→a1/a2、S05b→b1/b2/b3、S11a→a1/a2、S11b→b1/b2、S11c→c1/c2，grid_count 全 1，S12 承接 S11c2 match-on-action）。上游设定变化（帽/围裙/空间合并/道具/灯光）只**更新镜卡数据字段**，不重推镜数/拆镜结构/时长。
3. **一次性写出完整 storyboard_package.json**（可拆 2-3 个 write_file 追加），禁止中途跑任何中间核算/逐段验证脚本。
4. **交付**。

**宫格数=切镜数（凡哥 2026-09-03/09-04 定）**：不切镜的镜 grid=1（单图构图锚点，同一画面禁止多图）。**镜内切镜**（同一叙事单元内有机位切换，如中景推近切特写、正反打以外的机位切换）→ grid=切镜数，grid_reason 写清每格对应哪个切镜画面。凡哥原话："没有切镜时只需要参考一张图，有切镜时需要切镜时的关键帧"。实战：S02「门缝帽檐首见→摘帽对视」镜内切近景有动机 → grid=2（格1中景/格2近景），此前被误写成单图。



框架重推的**唯一触发条件**：上游剧本场次/台词结构发生变化（场数增减、台词重写导致情感节拍变化）→ 重新推演框架并记录原因。仅设定数据变化→永远沿用框架。

凡哥实战：v6 子代理自创脚本转换 13 分钟；重跑子代理老实走 7 步推演 1 小时+未完成且结构漂移——执行路径不锁=速度与产物都不稳定。**框架锁定+四步路径=每次重跑同速度同结构**。

## Conversion Flow

1. Lock the scene objective and inherited entry state. Completion means the entry state and one executable objective are written.
2. Extract setup, trigger, action, resistance, reveal, reaction, result, and exit beats. Completion means every source beat is mapped or marked as blocked.
3. Estimate dialogue, performance, action, effects, and transition time separately. Completion means total duration and core duration are explicit.
4. Group beats only when they share space, objective, core action, axis, and primary speaker. Completion means each group has one clear reason to remain one shot.
5. Split at a change of space, time, objective, principal speaker, axis, major state, or core action. Completion means no shot carries incompatible causal actions.
6. Place the cut where information or emotion changes: trigger, evidence, visible reaction, completed action, or relationship repositioning. Completion means each shot has a checkable cut interface.
7. Write the complete package per the fixed frame and deliver.

## Emotion Direction

Use this chain for every shot:

`audience emotion -> required information -> shot choice -> playable actor action -> dialogue/environment sound/effect -> edit point`

State an observable audience target, such as “recognize danger approaching,” rather than a vague atmosphere. Record emotional start, turn, and landing.

Translate emotion into trigger, action, and reaction: glance away, tighten fingers, swallow, pause, retreat, reach, listen, or look from a prop to a person. Do not instruct “act frightened” without a concrete behavior, target, and ending state.

This node feeds an AI video model that cannot infer emotion from adjectives. Every emotion term must resolve to a playable on-screen behavior (a glance, a hand movement, a pause, a breath, a posture shift). Remove director-layer planning such as “build tension” or “the audience should feel”; the shot card states only what the model must render and how it moves. Leave nothing to interpretation where the model must not improvise.

Use distance and movement for information: wider views establish spatial relations, medium views carry interaction, and close views carry evidence or emotional peak. A camera move must have a narrative object and must not reduce readability.

## Shot Language Decision Rules (镜头语言决策规则，内联自 shot-language skill，2026-09-04)

每镜写卡时按以下决策表定景别，禁止全片中景平铺：

**景别六档**：远景（人物极小，疏离/开场）｜全景（全身+背景，登场/动作展示）｜中景（膝上，日常对话最常用）｜近景（胸上，内心/情绪交流）｜特写（肩上，情感爆发/悬念）｜大特写（局部器官，极致强调）。

**情感→景别速查（写卡必用）**：
- 孤独渺小→远景；日常对话→中景正反打；内心思考→近景；**喜悦感动→近景→特写（柔光推镜）**；悬念紧张→特写（浅景深）；亲密爱恋→特写近景。
- 情绪峰值镜（落泪/碰脸/关键道具落点）必须特写或大特写，不允许中景带过。

**切镜动机清单（有其一就切，切镜数不设上限）**：
1. 情感时刻（最强）：情感到关键点换距离看（泪落→切特写）
2. 叙事需要：信息转换/时间地点跳变/新事件
3. 节奏点：卡点切镜
4. 视线引导：观众该看另一个人/物（正反打）
5. 景别/机位大变化有叙事意义（建立镜头→进入→强调）
无动机不切：状态变化/情绪微变/小动作递进默认同镜内连续演进（连续动作+小幅度运镜）。

**切镜时景别变化要够大**：全景↔中景、近景↔特写、正反打、侧↔正；禁止同角度小步推切（Murch 蜜蜂巢——观众最迷惑的切法）。

**全片景别弧线**：开场建立（中景/全景）→对白段（中景+正反打中近景）→情绪爆发段（特写递进）→回落（中景）→终场收束（中景或远景）——景别曲线跟随情绪曲线，禁止全程一条平线。

**组接句式**：前进式（远→近）=情绪高涨；后退式（近→远）=情绪下沉。

**开场镜选择（首镜 S01 写卡时直接满足，凡哥 2026-09-21 定）**：
- 剧本开场是**冲突驱动型或人物塑造型**（第一句台词已落在冲突中段、或先声后人/延迟识别）→ 首镜用**中近景、特写或低机位仰拍**，**禁大全景/大远景平铺**。依据：好莱坞五公式要点页原文"**冲突型开场不建议一开始大量使用大全景**"，推荐中景/近景/特写/大特写/低机位仰拍。
- 仅**世界观震撼型**开场（大远景＋渺小参照物＋一个反常细节）可用远景/大远景，且一个镜头内必须给足"未知感"，不得空镜铺城。
- **反面实例（2026-09-18 第 1 集）**：剧本开场已是"村民吊人议论＋牛满被吊"的冲突中段（S01 前已有冲突在演），分镜却把 S01 写成"**全景｜建立→转说话场**"——首镜退化成环境介绍，与开场结构不符；此类情况首镜应改**中近景或低机位仰拍**切入冲突动作。
- 与《全片景别弧线》配合：开场用中近景切入不等于全片无远景——世界观/落差需要在后续镜或终场释放（弧线照旧跟随情绪曲线）。

## Timing and First/Middle/Tail

Use `first` for location, subject, orientation, and the initial abnormality. Use `middle` for trigger, playable action, resistance, and the key reveal. Use `tail` for reaction, result, changed state, and the next-shot interface.

A simple shot may use `abnormality -> action -> result`; a complex event must split at its causal boundary. Preserve the protagonist's choice, cost, and causal result rather than compressing them away.

Record `duration`, `core_duration`, `edit_safety`, and frame-rate math. For OTIO exchange, represent seconds as rational frame ranges using the declared frame rate; do not build an OTIO service or adapter platform.

## Action Duration Estimation (time is emotion tempo)

Never split shot time evenly across states — that produces walk-through pacing (点卯/走过场). Time is assigned by the emotion's tempo, and every action carries a natural duration.

- `natural_duration`: every playable action is timed by how long a real person takes. Pressing dough until fingertips sink: 2.5s. A hand slowing to a stop: 1.5s. A held-breath pause: 0.8–1s. Turning away: 2s. These come from observed behavior, never from dividing the shot's total time.
- `beat_pause`: emotion beats are their own time cost — the stop, the swallow, the glance down. A beat is never compressed away to fit a state list.
- Duration formula: `duration = Σ natural_durations + Σ beat_pauses + entry/exit states`. Compute duration from the actions; never fix a duration first and then squeeze states into it.
- State-density cap: at most 4 core playable states per shot. More states → split the shot or raise the duration, never pack them. Any shot where states receive ≈2s each of point-to-point motion reads as a walk-through and fails.
- Tempo shape: write the emotional rhythm explicitly, e.g. `slow start (2s) → held pause (1s) → key action (2.5s) → micro-expression build (1.5s) → release (2s)`, each phase with its seconds.

Shot cards record per-action `natural_duration`, `beat_pause`, `tempo_shape`, `eye_line`, `micro_action`, and `breath`.

## Sound Contract

For every dialogue, environment sound, effect, silence, sound bridge, or pre-lap, record source, perspective, entry, exit, timing, and function. State what the sound makes the audience attend to and what emotional turn it supports.

Dialogue carries information or strategy that the picture cannot clearly carry. Environment sound establishes the space. Effects mark action, danger, evidence, or psychological change. Avoid competing attention centers.

Sound may be in-frame, off-screen, subjective, bridged, or anticipatory. Mark these properties and test for misreading downstream; do not assign music per shot.

## Spatial Direction and Blocking

Describe world layout from the main subject or spatial core's own up/down/left/right/front/back orientation. Do not use screen-left or screen-right as geography.

**违规实例（2026-09-03 实战教训，凡哥铁律）**：❌「门板在镜头左侧，周野侧立」→ ✅「门在周野正前方，周野面门侧立」；❌「周野在画面边缘」→ ✅「周野在母亲左前侧揉面」。方位一律挂在主体上：his right / her left / in front of him / behind her，禁止「镜头左/画面右/屏幕边缘」等以镜头为参照系的描写。**优先用道具/场景固定物作参照**（母亲在灶台侧、周野在水槽侧、门在他正前方），跨镜方位关系保持同一套道具参照、不许互换。

## 2026-09-03 全片重跑新增铁律（凡哥定方向）

1. **动作必须符合身份母版**：先查 identity_masters（服装/发型/配饰清单）再写动作。母版里没有帽子 → 禁止「摘帽/帽檐/压帽檐」类动作（实战：S02 摘帽是身份母版外脑补动作，已删）。道具/动作超出母版清单=违规。
2. **时间锁定**：每镜 time 写具体时间点（黄昏/刚入夜/深夜），禁止「dusk→night」这类跨镜模糊渐变（模型自由发挥→相邻镜白天黑夜乱跳）。
3. **空间衔接**：相邻镜空间关系写死（S02 门外=与 S01 同一楼道，S02 门内=玄关）；禁止笼统「连续空间」。
4. **灯光锁定**：全片统一灯光基调写进 project_defaults（如「warm home lighting at night」），每镜不另起灯光描述；特殊镜（S01 楼道）单独声明。
5. **正反打=真切镜，必须拆镜**：两人对话的正反打机位切换是真切镜动机，拆成独立镜（每镜一个机位），禁止在单镜里写「镜头在两人之间切换」。拆镜按说话轮次/情感动机，每镜≥4s 有完整台词落点；拆镜后总数与时长重新记账。

Establish the spatial core's facing direction, axis, eyelines, subject positions, camera position, and movement paths. Preserve axis and eyeline matching unless disorientation is an intentional, traced decision.

Each shot includes a separate top-view dispatch diagram specification. It uses symbols and geometry only: red circle protagonist, blue circle supporting subject, purple triangle opponent, yellow diamond prop, gray spatial core, black triangle camera. Use distinct line colors for subject movement, prop movement, camera movement, and eyeline.

The dispatch diagram contains no text, names, numbers, IDs, labels, dialogue, legend, or technical annotations. It is a geometry constraint, not a character or scene reference for a video model.

## Dynamic Grid

Count essential checkable visual states before choosing a grid. Use the smallest grid that covers first state, trigger, action, peak, reaction, endpoint, and any necessary spatial transition.

Use 3 or 4 panels for a simple action; 6 for setup/trigger/transition/peak/reaction/endpoint; 8 or 9 for moderate spatial or reaction changes; 12 only when every panel remains one coherent objective. If the states do not fit, split the shot.

Every panel maps to a checkable state and records its source beat or frame function. A director board may include labels in its private representation, but the model-clean board and dispatch diagram contain no text.

## Continuity Interface

Maintain a compact ledger across shots for identity master and story-state ID, age, wardrobe, hair, face, injury or dirt, carried props, body condition, spatial orientation, axis, eyeline, start/end position, prop ownership and state, ability trigger/result/cost, accepted tail frame, required next first frame, speaker, and unresolved risk.

A state change records source, cause, start shot, end shot, changed fields, and invariant fields. Never create a new visual identity to solve a difficult shot. Never write “same as previous shot”; name the inherited state or accepted frame.

Cross-shot continuity uses match-on-action, never a straight single-shot extension. Split one continuous action across two adjacent shots: the previous shot ends mid-action (e.g. the car door pulled halfway open), and the next shot switches angle, resumes from that same mid-action pose, and completes the action. The two shots match on the mid-action pose and position. Do not extend the same action in the same angle — a visible stutter is certain.

Borrow the Kitsu relationship only as a naming and handoff shape: `Project -> Episode -> Sequence -> Shot`, with casting and preview references. Do not implement Kitsu integration or a task-state system.

## Role Action Division in Shared Scenes (动作分工)

Two characters in the same space must never perform the same task in parallel — a mother rolling dough while her son also kneads dough reads as contradictory duplicate labor (重复劳动，观感矛盾). For shared-scene staging:

- Assign a distinct, complementary task per character (one kneads, the other picks vegetables / sets the table / hands tools / stands by), or an explicit cooperative split (one rolls, one wraps).
- If the screenplay genuinely has both doing one job, write the division explicitly: who does which half, in what sequence, or one assists the other — never two people each doing the full same action side by side.
- A character who just arrived or has no stated task should not be given one for blocking convenience; watching, resting, or standing by is a valid staging.

## View Orientation Stability (180° Flip Ban / 主体视角翻转禁令)

A subject must not flip its facing orientation by ~180° inside one generated segment (front → back facing camera). When the prompt demands a turn-around and the reference sheet places front and back views side by side, the model renders both views simultaneously as a split screen — the same character duplicated left and right doing the same motion.

- Keep one facing orientation per segment (small angular shifts only). Stage the back view as an established entry state: the character is ALREADY back-facing at segment start — never shoot the turning process.
- If the story needs front emotion AND a back-view exit, split into two segments: segment A ends front-facing at peak emotion; segment B starts with the character back-facing (established state), no turn.
- Fallback staging (official guidance): use side profile, medium shot, or back view instead of demanding continuous face close-ups.

## Shot Count Stability Default (官方稳定性建议)

MiniMax H3 official guidance: first videos should stay at 5–10s, one subject, one main action, max 2 shots. Each extra cut lowers adherence stability. This is a stability default, not a hard cap — cuts with real motivation (emotion beat, reverse shot, rhythm/beat-sync cut) are allowed, accepting lower stability.

Return one package containing project defaults, shot index, shot cards, continuity ledger, grid decisions, dispatch specifications, handoff placeholders, source trace, and QC status.

Each shot card must contain: shot ID and scene/beat IDs; objective; inherited consequence; duration/core/edit safety; identity and story-state IDs; space/time/orientation; shot size, height, angle, stable position, and primary movement; first/middle/tail states; blocking and playable trigger/action/reaction; gaze and emotion start/turn/landing; dialogue and sound events; prop/ability before and after; cut interface; grid count and reason; diagram specification; overload and continuity risks; fallback split; and source/adaptation trace. Each shot card also records action complexity (simple/coordinated/complex) with its split steps, and every playable action records its natural_duration, beat_pause, tempo_shape, eye_line, micro_action, and breath.

Prompt fields remain placeholders. External output is exactly `SUCCESS` with one complete package, `INPUT_ERROR` for missing input, or `ADAPTATION_FAIL` when locked story facts cannot fit without deletion or alteration. `ASSET_BLOCKED` is a shot-level blocking reason inside the package, not a fourth external result.

## Shot Complexity and Action Split

Mark each shot's action complexity so a complex action is split into playable steps, never flagged for a retry loop.

- SIMPLE: one subject, minimal movement, standard framing.
- COORDINATED: two subjects, one interaction, a single moving prop, or one camera direction change.
- COMPLEX: three or more subjects, overlapping dialogue with action, complex blocking, fast or multi-axis movement, effects, or a reveal depending on precise timing.

A complex action is split into explicit playable steps at segmentation time instead of being left as one hard move. The split is a staging aid that keeps generation single-pass; it does not add a difficulty tier, a retry order, or a re-roll policy to the workflow.

## Shot Card Rules (写卡时直接满足，写入包即完成)

1. Every shot is `<=15s` and core content is `<=14s`.
2. Every shot has one space, objective, core action, primary movement, and speaker policy.
3. Every shot has first, middle, tail states and an information or emotional cut interface.
4. Emotion is expressed as audience target plus playable trigger/action/reaction.
5. Every sound event has source, perspective, timing, and attention/emotion function.
6. Subject direction, axis, eyelines, positions, and continuity interfaces are explicit.
7. Dynamic grid follows counted states; every panel has a checkable state.
8. Dispatch geometry is separate and contains no text or labels.
9. Identity, prop, ability, and story-state transitions have IDs and source trace.
10. No story event, motivation, identity, result, or causal cost is changed; overload has a fallback split.
11. Every action carries a natural duration and emotion beats; duration is derived from actions, never averaged over states; max 4 core playable states per shot.
12. Characters sharing one space have distinct, complementary actions — no two characters doing the same task in parallel (duplicate-labor contradiction).
13. No subject flips facing orientation ~180° within one segment (split-screen risk); back views enter as established states, never as a turning process.

## Common Pitfalls

1. Treating a whole scene as one shot.
2. Extending beyond 15 seconds or hiding core overload in prose.
3. Replacing playable action with emotion adjectives.
4. Using screen coordinates for world direction.
5. Choosing a fixed grid before counting visual states.
6. Putting labels into the text-free dispatch diagram.
7. Re-randomizing identity, props, wardrobe, or state between shots.
8. Losing the causal event, choice, cost, or result to fit time.
9. Claiming OTIO/media PASS from an unrun test.
10. Building platform integrations inside this conversion skill.
11. Distributing shot time evenly across states (walk-through pacing).
12. Two characters performing the same task in the same scene (e.g. both kneading dough — duplicate-labor contradiction).
13. Writing a turn-around (front→back 180° flip) inside one segment — the model renders both views side by side as a split screen.
14. Deleting, merging, or rewriting screenplay dialogue to fit the shot budget — every dialogue line of the episode must land in a shot's dialogue event. Violation instance (2026-09-18, 《十二时辰》E1): 8 lines ≈90 chars never landed (村民丙「管家，吊一宿了，别真把人吊死了。」、王二「死不了。死了，那两吊钱你出？」、牛满「你们……把我当成牲口。」「笑啊。」「你们刚才，笑得那么响。怎么不笑了。」、王二「牲口能拉磨。你呢？克爹克娘，就剩克人。」、村民甲「她、她能动了！」、村民乙「绳子！绳子是自己断的！」).
15. Letting the package total duration drift far from the screenplay's own duration estimate (violation instance: screenplay E1 estimated 102–117s, package came out 172s ≈ +47%). Calibrate to ≤±15% before delivering.
16. Averaging the episode's screen time across shots instead of deriving each shot from its action's natural duration + beat pauses — this is what makes totals inflate.

## Verification Checklist

- [ ] Input is an approved, traceable screenplay package.
- [ ] All shots pass the ten hard gates.
- [ ] S01-S15 sample assertions are represented without inlining the fixture.
- [ ] OTIO frame math is explicit where exchange is required.
- [ ] Only the allowed Kitsu relationship is borrowed.
- [ ] External result is exactly one of `SUCCESS`, `INPUT_ERROR`, or `ADAPTATION_FAIL`.
- [ ] Every screenplay dialogue line of the episode lands in a shot dialogue event — zero deletion, merging, or rewriting (verify with a line-level diff against the source episode, not by eye).
- [ ] Package total duration within ±15% of the screenplay's own episode duration estimate; each shot's duration derives from action natural duration + beat pauses, never from averaging.
- [ ] No prompts, media, platform, database, or runner were fabricated.
