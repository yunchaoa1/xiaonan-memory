---
name: screenplay-asset-extraction
description: "Use when compiling one approved screenplay package into traceable reusable production assets."
version: 0.2.0-rc
author: Xiaonan
license: MIT
metadata:
  hermes:
    tags: [opc, screenplay-breakdown, asset-extraction, continuity]
    related_skills: [novel-to-screenplay]
---
# Screenplay Asset Extraction
## Overview
Compile one approved screenplay package into one structured asset package for the
next OPC nodes. Extract reusable identity masters, story states, locations, continuity-critical props,
abilities, sound, and set elements only when they affect staging or continuity. Ordinary
working props stay as shot-level objects unless they carry a clue, identity, or cross-shot
state that must be reproduced.
The package must carry the platform-selected locked `style_id`; this node inherits it and
does not choose or change the visual style.
Preserve source references so every scene binds without guessing.

This node owns extraction and binding. It does not rewrite facts, design shots,
write prompts, render assets, or build a registry or production platform.
## When To Use
Use after novel-to-screenplay produces an approved package and before subject-asset
or storyboard work. Do not use for novel adaptation, screenplay repair, shot/camera
design, storyboard generation, image/video prompts, model calls, rendering, database
work, or workflow orchestration.
## Contract
**Unique input:** one complete approved screenplay package with package ID/version,
scope, scene boundaries, scene actions/dialogue/sound/results, source/change
references, and available character, prop, ability, and project-state material.
A summary without scene-level actions and results is insufficient. Missing action,
boundaries, source references, or key states returns `INPUT_ERROR`.

**Unique output:** exactly one external result: `SUCCESS` with the complete structured
asset package, `INPUT_ERROR` for missing input, or `EXTRACTION_FAIL` for an
irreconcilable fact/state conflict or blocking dependency. Never expose partial data,
alternates, reasoning, or prompt prose.

Priority is locked constraints, approved screenplay facts, verified project rules,
then conservative defaults. Keep fact, rule, inference, and unknown distinct.
## Black-Box Node Boundary

This Skill is a fixed closed node, not a conversational Agent. It reads only one explicit,
approved upstream screenplay package/version plus the current Skill rules, then outputs one
complete typed asset package. It never reads chat, user-side amendment language, external
project facts, unapproved drafts, or prior delivery text as implicit input.

Customer-requested local rewriting belongs to the platform model: it interprets the request,
locates the affected scope, creates a new controlled approved upstream version, and invokes
this node again. This Skill does not interpret local rewrite requests, patch its previous
output in place, offer alternatives, or decide downstream reruns.

## Asset Boundaries
An identity master is a stable entity, not an appearance. A story state is a
source-supported version at a defined scene range. A location is a reusable space,
not a shot. A prop is an identity with ordered condition and holder relations. An
ability is an owned capability with trigger, effect, limitation, and cost. A scene
binding names versions present; it does not describe camera language.

Every downstream-required asset has a stable machine-readable ID. Version only a
meaningful change. Never create arbitrary Cartesian combinations of age, wardrobe,
hair, makeup, injury, or props.

## Asset Tiering

Use `D:\\Hermes\\xiaonan-memory\\references\\opc-style-and-asset-tiering-v0.1.md`.
Script breakdown and subject-asset generation are separate decisions. Record every object
that an actor handles as a prop/working-prop binding, but generate a standalone prop master
only for a **hero/high-visual-continuity prop**.

A prop qualifies for a standalone subject asset only when at least one primary condition is
true: (a) it is planned for a close-up/insert where design details must read; (b) it has a
unique, story-specific silhouette, markings, construction, or identity that the audience must
recognize; (c) the same distinctive object recurs as a visual focus across shots/scenes; or
(d) a visible condition change must be recognized as the same designed object. Mere handling,
holder transfer, symbolic meaning, or a text-only state chain is insufficient by itself.

Tier A subject assets are generated separately: principal characters use exactly front/one-side/back
full-body views plus a facial detail; important scenes require a locked spatial master before
any alternate views; qualifying hero props receive a master. Tier B hand/working props such as
ordinary keys, cups, food, filling, rolling pins, pots, tissues, and generic utensils remain in
shot/storyboard bindings with holder, position, scale, orientation, and state. They do not
receive an independent subject image unless a later shot plan upgrades them under the criteria
above.
## Prop Three-Element Rule (凡哥 2026-09-04 定)

凡哥观察规律：**但凡道具类，小说都会描述其三要素**——①**作用**（function：道具在剧情里干什么，如帽子的"门缝遮拦与放下"）②**出处**（首次出现的 holder/来源，如"周野头上 S01 开场"）③**落幕**（最终去向/结局，如"S02 置鞋柜，此后不再入画"）。提取每个道具时必须核对三要素：源文齐=全提取进 function/holder_chain/state_chain；源文缺某一项=该要素写"源文未交代"+裁定行（不脑补）。三要素全缺的"物件"根本不算道具（降为场景陈设或忽略）。

例：周野的帽子——作用=门缝先见帽檐的识别锚点、摘帽=不再需要遮挡；出处=S01 开场戴在头上；落幕=S02 置鞋柜不再入画。三要素齐备=典型道具。

穿戴物归类的唯一标准=**剧中行为**：
- **有摘/脱/换/转移动作**（摘帽、脱围裙、递包）→ 该物=**道具**（prop）：要有 identity、holder 链、状态链（戴→摘→置放）。
- **始终穿戴不动**（围裙一直系着、夹克一直穿着）→ 该物=**角色形象/服装的一部分**（identity 的 wardrobe），不单列道具。

例：周野的帽子——剧中有「摘帽」动作 → 道具；母亲的围裙——始终穿着 → 形象一部分。判定看**源文动作**，不看物件类别。

## Location Merging Rule (凡哥 2026-09-04 定)

场景空间提取时按**连通性+叙事同一性**合并：
- **同一住宅内的连通空间**（玄关/客厅/厨房/餐厅）在剧本无特殊视觉要求时=**一个空间**（一个 location_master，一张场景图）。判定：人物走动无需离场即可到达=同一空间；同一场戏跨区域=同一空间。
- **独立/隔离的特殊空间**（楼道=门外公共区，有空间门槛且叙事独立）才单独成立一个 location_master。
- **目的**：减少参考对象数量、减少生成工序。默认合并，除非剧本有"必须独立呈现"的特殊视觉要求。

例（《饺子出锅前》）：玄关+客厅+厨房+餐桌=一个"家"空间（1 张场景图）；楼道（门外）=独立空间（1 张）。总共 2 张场景图，不是 4 张。

## State-Version Reference Standard (凡哥 2026-09-04 定)

人物状态版本需要**独立参考图**的两种情况（且只能是完整人物图，禁止部件拼贴）：
- **换装**（剧情中换衣服）→ 每套服装一个状态版本图（同人+全套新衣的完整人物图）。衣服永远不能从人物身上剥离成独立道具图——参考图不可能光着身子，把衣服当道具组合谁都接受不了。
- **受伤**（绷带/伤口/血污等身体状态）→ 受伤状态单独一个版本图（同人+伤的完整人物图）。伤在身体上，无法从人身上剥离单独参考。
- 判定：换装/受伤=新 story state → 对应新版本参考图；不换装不受伤=母版单一版本即可（当前《饺子出锅前》全程一套衣服无受伤，只有 identity 版本）。

**配饰边界（2026-09-04 凡哥纠偏）**：可摘脱配饰（帽子/围巾/眼镜/手包等）按 Worn-Item 标准=**道具**，**永远不触发人物状态版本图**。人物图始终是无配饰基线（如周野无帽母版）；配饰的佩戴状态由「人物图+道具图」在下游故事板/分镜环节绑定组合（S01 戴帽=周野无帽图+帽子道具图共同作参考）。只有①服装整体更换（换衣服）②受伤等身体状态，才生成新的人物状态版本图。实战教训：曾把「戴帽/无帽」当换装处理生成两张人物图——错误，帽子是道具不是服装。
### 1. **Package:** approved ID/version, scope, scene list, source boundary, and locked style are frozen.
2. **Entities:** every continuity-relevant character, location, prop, ability, sound,
   or set element has one canonical identity and evidence.
3. **States:** masters and story states are separate; states have range, cause, source,
   and invariant/allowed fields.
4. **Snapshots:** each appearance binds one complete character snapshot; it never
   embeds external location, prop, or ability truth.
5. **Transitions:** prop and ability changes form ordered, caused, sourced directed
   chains with no unexplained jump.
6. **Locations:** each location has spatial core, facing direction, landmarks, fixed
   structures, variable dressing, and scenes; never use screen-coordinate geography.
7. **Expressions:** high-impact figurative expressions have recovery decision,
   observable result, unknown boundary, and no invented law.
8. **Bindings:** every scene resolves required identity/state/location/prop/ability
   IDs; changing external states use atomic start/end rows.
9. **Dependencies:** no orphan, duplicate alias, missing dependency, contradictory
   version, or unresolved blocking conflict remains.
10. **QC:** isolated review passes all preceding gates and confirms v0.11 independent
    PASS with zero issues. Never label unrun media work as PASS.
11. **Source-Clue Alignment (2026-09-04 凡哥定):** every visible clue in the frozen
    upstream screenplay (wardrobe, worn props, held items — e.g. 帽檐/摘帽, 围裙,
    拎包) has one of: a matching wardrobe/prop entry in the output, or an explicit
    adjudication row (裁定: kept/removed + reason + source line). A clue with neither
    returns `EXTRACTION_FAIL` (漏项). Customer-supplied appearance material enters
    ONLY as a platform-authored controlled upstream version followed by a full node
    rerun — never as a hand-written master file outside this node (2026-09-04 实战:
    master drafted by hand bypassed this node and silently dropped the 帽 clue).
A failed gate returns to the earliest responsible field and reruns the complete gate.
Up to five hidden repairs are allowed; unresolved conflict returns `EXTRACTION_FAIL`.
## Short Pipeline
1. **Freeze and audit.** Record package identity, scope, scenes, source references,
   locked constraints, unresolved items, and defaults. Completion: every scene has
   boundaries, actions, results, and trace status.
2. **List entities.** Deduplicate recurring characters, locations, meaningful props,
   abilities, sound, wardrobe, vehicles, VFX, and set dressing only when staging or
   continuity requires them. Completion: each maps to one identity or explicit unknown.
3. **Make identity masters.** Record supported names/aliases, type/species, locked
   facts, silhouette/recognition anchors, behavior, voice, costume structure, props,
   location function, object function, and evidence. When the screenplay gives an
   identity/state fact but no visible detail (e.g. "服役结束复原"), derive the visible
   detail by plain common sense and record it as a DERIVED_DEFAULT — what an ordinary
   person would regard as reasonable for that identity, never a counterintuitive choice.
   Example: a recently discharged serviceman → short crew cut (板寸), upright posture,
   simple civilian clothing. Completion: no scene condition is masquerading as identity.
4. **Make story states.** Record state ID, owner, appearance/condition, holder or
   location relation, ability/social/temporal phase, range, transition cause, source,
   invariants, and permitted change. Completion: every state is reachable or marked
   first appearance; no arbitrary combination exists.
5. **Make character snapshots.** Bind each participant to identity plus one snapshot
   of body, face, hair, wardrobe, injury/dirt, posture, and emotional/social condition.
   Bind props, locations, and abilities separately. Completion: every snapshot is
   coherent and supported.
6. **Extract locations.** Record interior/exterior, supported time/weather, spatial
   core, facing direction, landmarks, fixed structures, variable dressing, scenes,
   and source. Use subject/space-core front/back/left/right/up/down, never screen
   left/right. Completion: adjacent scenes preserve required orientation.
7. **Extract props and abilities.** Props include identity, function, visual anchors,
   holder, scope, and state chain. Abilities include owner, trigger, target,
   manifestation, effect, limitation/cost, unknown boundary, and state chain.
   Completion: every transition is ordered, caused, sourced, and scene-bound.
8. **Recover expressions.** Separate era/narrator label, observable phenomenon,
   supported mechanism, unknown, dramatic function, state change, risk, and added-rule
   flag. Completion: every high-impact recovery is recorded.
9. **Bind and QC.** Output manifest, masters, states, snapshots, locations, props,
   abilities, recoveries, continuity ledger, scene bindings, and downstream
   placeholders. Use atomic `.start`/`.end` rows for changing external assets.
   Completion: downstream resolves every scene without rereading prose.
## ID Rules
Use `identity.<slug>.v<revision>`, `state.<identity-slug>.<state-slug>.v<revision>`,
`scene.<slug>.v<revision>`, `prop.<slug>.v<revision>`,
`prop-state.<slug>.<state-slug>.v<revision>`, `ability.<slug>.v<revision>`,
`ability-state.<slug>.<state-slug>.v<revision>`, and `expression.<slug>.v<revision>`.
A state revision records meaningful appearance, condition, holder, location, ability,
social, or temporal change; it never silently renames an identity.
## Output Shape
`SUCCESS` contains only structured data: source manifest; identity masters; story
states; character snapshots; locations; prop/ability chains; expression recoveries;
continuity ledger; scene-to-asset bindings; downstream placeholders; and QC status.
Separate `required_subject_assets` from `storyboard_bindings`. Placeholders are
fields, never prompt sentences.
## Optional Mature Bases
ScriptBreak and OSF may inform categories such as Cast, Extras, Props, Wardrobe,
Vehicles, VFX, Sound, and Set Dressing, plus scene-to-assets aggregation. They are
optional classification references, not dependencies. Do not build DVC, database
tables, an asset registry, a universal runner, or a platform around them.
## Fixed Regression
Use the approved v0.3 Chapter One screenplay package and source/change materials.
The v0.11 regression is independent PASS with `0` issues. Minimum entities include
牛满, 王二, red-eye girl, gold-mark boy, green-eye boy, future young person,群众 group;
village old locust tree, market, dungeon, ruined temple, future street; rope,
ox-shaped wooden hairpin, redemption coins, future lighter, and match.

Verify time agency and stopped/flowing states, blue flame, lifespan cost, empty or
blinking divine seat, aged-half-face/aged-hands, and hidden/held/broken/mud/returned
prop states. Verify no duplicate identity, no prop jump, no screen-coordinate
geography, no prompt prose, and complete scene bindings.
## Common Pitfalls
1. Making every appearance a new character.
2. Putting props, locations, or abilities inside a snapshot.
3. Inventing unsupported wardrobe, injury, age, or state combinations.
4. Jumping a prop from hidden to destroyed without evidence.
5. Using screen coordinates as world geography.
6. Treating metaphor or ability labels as modern science.
7. Extracting nouns without staging or continuity function.
8. Letting location assets absorb shot/camera decisions.
9. Passing orphan assets or incomplete bindings downstream.
10. Writing image/video prompt prose in output.
## Verification Checklist
- [ ] One approved screenplay package and scope were frozen.
- [ ] Ten gates passed and no blocking conflict remains.
- [ ] Masters and states are separate and source-backed.
- [ ] Every appearance has one coherent snapshot.
- [ ] Props and abilities have complete directed state chains.
- [ ] Locations use spatial-core orientation.
- [ ] Expression recovery is recorded without new rules.
- [ ] Every scene binds valid IDs, including atomic start/end changes.
- [ ] Regression is independent PASS with zero issues.
- [ ] Output is one complete `SUCCESS` package or one blocking result.
