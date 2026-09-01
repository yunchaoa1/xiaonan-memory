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
next OPC nodes. Extract reusable identity masters, story states, locations, props,
abilities, sound, and set elements only when they affect staging or continuity.
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
## Asset Boundaries
An identity master is a stable entity, not an appearance. A story state is a
source-supported version at a defined scene range. A location is a reusable space,
not a shot. A prop is an identity with ordered condition and holder relations. An
ability is an owned capability with trigger, effect, limitation, and cost. A scene
binding names versions present; it does not describe camera language.

Every downstream-required asset has a stable machine-readable ID. Version only a
meaningful change. Never create arbitrary Cartesian combinations of age, wardrobe,
hair, makeup, injury, or props.
## Hard Gates (10)
1. **Package:** approved ID/version, scope, scene list, and source boundary are frozen.
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
   location function, object function, and evidence. Completion: no scene condition
   is masquerading as identity.
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
