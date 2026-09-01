---
name: screenplay-to-15s-storyboard
description: "Use when converting an approved screenplay into a production-ready storyboard shot package of 15 seconds or less."
version: 0.2.0-rc
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

## Conversion Flow

1. Lock the scene objective and inherited entry state. Completion means the entry state and one executable objective are written.
2. Extract setup, trigger, action, resistance, reveal, reaction, result, and exit beats. Completion means every source beat is mapped or marked as blocked.
3. Estimate dialogue, performance, action, effects, and transition time separately. Completion means total duration and core duration are explicit.
4. Group beats only when they share space, objective, core action, axis, and primary speaker. Completion means each group has one clear reason to remain one shot.
5. Split at a change of space, time, objective, principal speaker, axis, major state, or core action. Completion means no shot carries incompatible causal actions.
6. Place the cut where information or emotion changes: trigger, evidence, visible reaction, completed action, or relationship repositioning. Completion means each shot has a checkable cut interface.
7. Run the hard gates below and repair the earliest failed segmentation choice. Completion means one external result is ready.

## Emotion Direction

Use this chain for every shot:

`audience emotion -> required information -> shot choice -> playable actor action -> dialogue/environment sound/effect -> edit point`

State an observable audience target, such as “recognize danger approaching,” rather than a vague atmosphere. Record emotional start, turn, and landing.

Translate emotion into trigger, action, and reaction: glance away, tighten fingers, swallow, pause, retreat, reach, listen, or look from a prop to a person. Do not instruct “act frightened” without a concrete behavior, target, and ending state.

Use distance and movement for information: wider views establish spatial relations, medium views carry interaction, and close views carry evidence or emotional peak. A camera move must have a narrative object and must not reduce readability.

## Timing and First/Middle/Tail

Use `first` for location, subject, orientation, and the initial abnormality. Use `middle` for trigger, playable action, resistance, and the key reveal. Use `tail` for reaction, result, changed state, and the next-shot interface.

A simple shot may use `abnormality -> action -> result`; a complex event must split at its causal boundary. Preserve the protagonist's choice, cost, and causal result rather than compressing them away.

Record `duration`, `core_duration`, `edit_safety`, and frame-rate math. For OTIO exchange, represent seconds as rational frame ranges using the declared frame rate; do not build an OTIO service or adapter platform.

## Sound Contract

For every dialogue, environment sound, effect, silence, sound bridge, or pre-lap, record source, perspective, entry, exit, timing, and function. State what the sound makes the audience attend to and what emotional turn it supports.

Dialogue carries information or strategy that the picture cannot clearly carry. Environment sound establishes the space. Effects mark action, danger, evidence, or psychological change. Avoid competing attention centers.

Sound may be in-frame, off-screen, subjective, bridged, or anticipatory. Mark these properties and test for misreading downstream; do not assign music per shot.

## Spatial Direction and Blocking

Describe world layout from the main subject or spatial core's own up/down/left/right/front/back orientation. Do not use screen-left or screen-right as geography.

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

Borrow the Kitsu relationship only as a naming and handoff shape: `Project -> Episode -> Sequence -> Shot`, with casting and preview references. Do not implement Kitsu integration or a task-state system.

## Shot Card Output

Return one package containing project defaults, shot index, shot cards, continuity ledger, grid decisions, dispatch specifications, handoff placeholders, source trace, and QC status.

Each shot card must contain: shot ID and scene/beat IDs; objective; inherited consequence; duration/core/edit safety; identity and story-state IDs; space/time/orientation; shot size, height, angle, stable position, and primary movement; first/middle/tail states; blocking and playable trigger/action/reaction; gaze and emotion start/turn/landing; dialogue and sound events; prop/ability before and after; cut interface; grid count and reason; diagram specification; overload and continuity risks; fallback split; and source/adaptation trace.

Prompt fields remain placeholders. External output is exactly `SUCCESS` with one complete package, `INPUT_ERROR` for missing input, or `ADAPTATION_FAIL` when locked story facts cannot fit without deletion or alteration. `ASSET_BLOCKED` is a shot-level blocking reason inside the package, not a fourth external result.

## Hard Gates (10)

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

A failed gate repairs the earliest responsible segmentation or staging decision, then reruns all gates. Do not return a structurally passing package that claims media quality has been tested.

## Fixed Regression Evidence

Use the first chapter S01-S15 structure chain as the fixed sample. Verify that shot IDs, source beats, durations, first/middle/tail states, grid reasons, and continuity transitions are all present. Do not inline the full fixture.

The MVP three-shot OTIO test is an exchange and time-math reference only. Its real status is `PASS` when the existing test evidence says `PASS`; do not claim a new media or OTIO run unless it was actually executed.

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

## Verification Checklist

- [ ] Input is an approved, traceable screenplay package.
- [ ] All shots pass the ten hard gates.
- [ ] S01-S15 sample assertions are represented without inlining the fixture.
- [ ] OTIO frame math is explicit where exchange is required.
- [ ] Only the allowed Kitsu relationship is borrowed.
- [ ] External result is exactly one of `SUCCESS`, `INPUT_ERROR`, or `ADAPTATION_FAIL`.
- [ ] No prompts, media, platform, database, or runner were fabricated.
