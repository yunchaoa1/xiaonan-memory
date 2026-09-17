---
name: image-asset-prompting
description: Use for structured AI image asset prompts and consistency.
version: 0.1.0
license: MIT
metadata:
  hermes:
    category: creative
    tags: [image-generation, asset-design, consistency, prompting]
    related_skills: [gpt-image-template-assets-opc-test, gpt-image-subject-assets-opc-test, scene-image-generation]
---
# Image Asset Prompting

## Purpose
Compile reliable prompts for reusable AI image assets. This is a class-level method for characters, locations, props, functional prop states, and controlled image expansion. It does not replace fixed black-box node contracts.

## Core Principle
Separate visual truth from narrative motivation. Classify every field as `SOURCE_FACT`, `DERIVED_DEFAULT`, or `UNKNOWN`. A derived default must be minimal, reality-grounded, observable, reversible at the template stage, and must not invent props, biography, decorative design, or plot. For example, a recently discharged serviceman may receive a short crew cut with natural side and nape taper. Broad labels such as “soldier”, “mother”, “home”, or “ancient residence” never authorize stereotype completion.

## Two Node Boundary

### Template Asset Node
Reads one approved upstream asset package and creates one customer-reviewable template. It owns no final expansion. Template dimensions adapt to the task:

- Character: vertical upper-body portrait, preferably 2:3 or 3:4, showing head through chest or upper waist. Lock face, hair, skin, shoulders, wardrobe structure, and worn accessories.
- Location: complete spatial plan, preferably strict orthographic top-down and roofless/cutaway, showing full footprint, four walls, doors, windows, openings, fixed furniture, circulation, scale, materials, palette, and future zones. The current screenplay-use zone is metadata; it does not delete bedrooms, bathrooms, service spaces, or connecting doors.
- Prop: one front template of one qualifying hero/high-visual-continuity prop. For visible functional states such as closed, open, or lit, create one front template per required state and record invariant and changed parts.

All template canvases are pure white `#FFFFFF`. Customer approval, regeneration, and version locking belong to the platform, not the node.

### Subject Expansion Node
Accepts only an immutable platform-approved template. It must not generate a template, understand customer rewrite language, patch an old delivery in place, or decide downstream reruns. It derives formal assets from the locked template:

- Character: one `16:9`, native `3840x2160` four-panel sheet containing exactly front full-body, one side full-body, back full-body, and enlarged facial detail.
- Location: requested camera/landmark views from the locked plan, changing only camera position and framing, then mechanically composed.
- Prop: requested views and approved functional states, preserving identity geometry and material.

All expansion canvases, panel backing, gutters, margins, and separators are pure white. Actual pixels, format, dimensions, bytes, and SHA-256 must be recorded. A requested 4K size is not proof of native 4K; provider experimental status must be recorded where applicable.

## Prompt Construction

Use this order: `TASK` -> `OUTPUT` -> `CAMERA_OR_PROJECTION` -> `VISIBLE_FACTS` -> `LAYOUT_OR_TOPOLOGY` -> `INVARIANTS` -> `ALLOWED_CHANGE` -> `BACKGROUND` -> `EXCLUSIONS`.

For editing, begin with `Change only [one variable]` and repeat the complete preservation list. One retry changes one variable. Generate individual views first and compose grids mechanically.

## Scene Consistency

A scene is a reusable spatial asset, not a single pretty room view. Build the complete space first, then identify the current-use area. Modern homes may use an open living/kitchen/dining public zone while preserving separate bedroom and bathroom zones connected by doors. Traditional Chinese settings require period and regional grounding; possible systems include courtyard-centered layouts, principal rooms, side rooms, service areas, entrance gates, corridors, moon gates, and partition gates. Do not transplant modern apartment logic into an ancient setting.

The reliable order is: define the spatial truth table; generate a customer-reviewable top-down plan with strict orthographic projection and four-wall graph; lock the template; generate each camera view from the locked plan or shared 3D scene; change only camera and framing; mechanically compose accepted views. If the model repeatedly outputs an oblique bird's-eye render, extra rooms, or changed furniture, return `ASSET_BLOCKED` or use procedural 2D/3D plan input.

## Character Consistency

Use the vertical template to lock face, hair, shoulders, chest, wardrobe, and worn accessories. Keep external props separate. For a recently discharged serviceman, “short crew cut, natural hair color, not permed or dyed, sides and nape gradually clipped shorter” is sufficient; do not specify millimeters or rigid regulations unless sourced. Expansion uses the approved template as the first reference, with shared head-height and ground-line logic. A side view means one side only.

## Prop Consistency

Script breakdown records every handled object; subject generation is a second decision. Standalone assets are for hero/high-visual-continuity items: planned close-up/insert, unique story-specific design, repeated visual focus, or a visible state change that must be recognized as the same designed object. Handling, handoff, symbolic meaning, or a text-only state chain is insufficient alone. Ordinary keys, cups, food, rolling pins, pots, and generic utensils remain shot-level bindings. State templates change only declared moving parts or active effects.

## White Background Gate

Every template and final asset uses a pure-white `#FFFFFF` canvas. Locations retain approved interior material inside the plan/view footprint, but unused canvas and margins are white. Final grids use white backing and gutters. Corner pixels and unoccupied margins are checked.

## Failure Routing

- Extra rooms or redecoration: list exact zones and topology before style.
- Oblique plan: put projection first; use procedural/3D geometry if needed.
- Too many panels: generate single views and compose mechanically.
- Character drift: edit from the locked template and change one variable.
- Prop contamination: remove external objects from the character and bind them separately.
- Hair over-specification: use simple length, natural color, and ordinary taper language.
- Narrative stereotype completion: classify facts as source, derived default, or unknown.

## Platform Boundary

Local rewrite requests belong to the platform model, which interprets intent, identifies scope, creates a new controlled version, and invokes the appropriate node. Neither node is a conversational Agent.

## References

Use `references/prompting-evidence.md` for condensed research and source notes.
