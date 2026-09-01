---
name: minimax-h3-shot-prompt
"description": "Use when compiling approved OPC shots into one MiniMax H3 per-shot prompt and asset-binding package."
version: 0.2.0-rc
author: Hermes Agent
license: MIT
metadata:
  hermes:
    category: creative
    tags: [opc, minimax-h3, shot-prompt, asset-binding, dialects]
    related_skills: []
---
# MiniMax H3 Shot Prompt
## Purpose
Compile one approved OPC shot and its locked asset references into one executable-facing
MiniMax H3 per-shot prompt package. This node owns prompt compilation and material binding
only. It does not generate video, choose a provider, or judge the resulting video.
## Use When
- An approved shot record already contains duration, action, first/core/tail states,
  sound/dialogue, continuity, and asset IDs.
- Locked character, scene, prop, group, or ability assets can be resolved by ID and version.
- A downstream executor needs the same package expressed in one of four H3 dialects.
Do not use this node for novel writing, screenplay adaptation, shot design, asset creation,
model execution, rendering, post-production, or media QC.
## Strict Responsibility Boundary
Upstream owns story facts, screenplay structure, asset extraction, shot duration, camera
plan, sound intent, state transitions, and approvals. This node preserves those decisions
and compiles them. It may normalize syntax required by a dialect, but may not add a new
beat, character, prop, camera idea, or visual fact.
The executor owns queueing, credentials, provider calls, retries, downloads, task status,
cost, and generated media. The QC owner inspects the actual output. A successful submission
is not a successful video, and this node must never report execution as completed.
## Required Input
One closed, versioned package contains:
- `shot_id`, shot schema/version, source IDs and source hashes;
- duration, mode, prompt language, approved shot prompt facts, and camera intent;
- `first_state`, `core_state`, `tail_state`, continuity constraints, dialogue, and audio;
- ordered `asset_refs[]` with stable asset ID, version/state, role, path/URI, SHA-256,
  approval/lock status, and the exact shot relationship;
- selected H3 dialect and its versioned adapter rules;
- `package_run_id` and prompt schema version.
No secret, provider credential, unapproved URL, chat-only fact, or unregistered asset may
enter the package. If a required upstream field is missing, stop and block.
## Input Discipline
1. Verify shot ID, source version, hash, duration, and required fields.
2. Verify every asset reference resolves to an approved locked record with matching ID,
   version/state, hash, and role.
3. Confirm that references cover every visible subject or prop named by the shot.
4. Preserve the shot's first/core/tail state and continuity wording.
5. Preserve dialogue and audio events as separate structured fields.
6. Select exactly one dialect adapter and compile its syntax.
7. Emit one package or one explicit block; done means every visible dependency is bound.
## Four H3 Dialects
### 1. MiniMax Cloud API
Compile the provider-facing request shape required by the approved API adapter. Keep
`shot_id`, prompt version, ordered conditions/material refs, mode, duration, and explicit
parameters in the OPC envelope. The executor, not this node, supplies authentication,
submits the request, polls the task, and downloads the result.
Do not assume a cloud response, model availability, task ID, pricing, resolution, or
reference limit. Those belong to runtime verification and remain unverified here.
### 2. ComfyUI Partner Nodes
Compile the API-format graph inputs or adapter payload for the approved Partner template,
including mode, prompt, duration, and ordered material conditions. Keep OPC asset UUIDs,
versions, hashes, and lineage in the envelope even if the Partner node accepts only URIs.
The adapter may map UUIDs to URI inputs; it must not make `<Picture N>` the business ID.
Partner authentication, queue execution, hosted inference, and returned media are outside
this node. Template compatibility must be checked by the executor against its locked version.
### 3. ComfyUI Native Nodes
Compile inputs for the locked local H3 T2V, FLF2V, I2V, or R2V graph according to the
approved shot mode. Bind image/video/audio conditions to the graph's typed slots while
retaining stable OPC asset references beside those slots. The graph is an execution
adapter, not the source of story truth.
Do not infer local model paths, sampler defaults, resolution, frame rate, or audio behavior.
The executor validates those values and records actual runtime results.
### 4. AIMixer Director
Compile the Director-compatible external groups and report correlation fields, preserving
OPC shot and asset identity outside Director's internal group numbering. Use the adapter
boundary for groups, segments, material ordering, and shared prompt parameters. Director's
report is execution telemetry, not OPC state truth.
Do not copy Director UI state into this package, and do not treat cache, segment selection,
or report success as media acceptance.
## Prompt Compilation
The per-shot prompt is a faithful compilation of approved facts: subject identity by asset
reference, scene by scene reference, one approved action chain, shot motion already chosen
upstream, first/core/tail states, continuity, dialogue, and sound function. Keep the main
prompt readable and keep structured fields beside it.
Use temporal ordering when the shot supplies it: beginning state, continuous core action,
ending state, then the approved audiovisual cues. Do not rewrite the shot into screenplay,
add motivation, invent blocking, or use a generic cinematic style instruction not present in
approved inputs.
A reference is bound by stable ID, version/state, SHA-256, role, and order. The dialect may
also require a URI or slot index, but that transport value never replaces the OPC identity.
Missing, stale, duplicate, or ambiguous bindings block compilation.
## State And Continuity
Carry state transitions literally enough for the executor to preserve them. State changes
such as complete-to-broken, held-to-scattered, or visible-to-mud-covered remain explicit
when supplied upstream. Keep identity master, state snapshot, scene, prop, group, and
ability as separate bindings.
Continuity is an input constraint, not a license to repair neighboring shots. If the prior
or next state is contradictory, return `SHOT_BLOCKED` with the conflicting fields. Do not
choose which source is correct and do not silently omit the conflict.
## Output Contract
Return exactly one JSON-like package with:
- `status`, `package_run_id`, package/schema version, and timestamp;
- shot ID, source manifest/hashes, selected dialect and adapter version;
- compiled prompt, language, mode, duration, explicit parameters, and state timeline;
- ordered `asset_bindings[]` with OPC IDs, versions/states, roles, URIs/slot mappings,
  hashes, approval/lock evidence, and lineage;
- dialogue and audio structures unchanged from input;
- executor handoff fields and a clear `execution_status=NOT_RUN`;
- block code and affected fields when compilation does not pass.
The normal successful result is `SUCCESS` for a valid package, not a video. The only other
result is one explicit block: `SHOT_BLOCKED`, `ASSET_BINDING_BLOCKED`, `PROVENANCE_BLOCKED`,
or `DIALECT_BLOCKED`. No result may claim rendered media, runtime QC, or human acceptance.
## Minimal Hard Gates
1. The shot and all upstream sources are versioned, approved, hashed, and closed.
2. Duration, mode, state timeline, action, camera intent, dialogue, audio, and continuity are present.
3. Every visible subject, scene, prop, group, and ability is bound to an approved locked asset record.
4. Asset ID/version/state/hash/role/order are valid, unique where required, and lineage-preserved.
5. The compiled prompt adds no story, shot, asset, or visual fact and omits no required fact.
6. Exactly one supported dialect and locked adapter version are selected.
7. Dialect transport mappings preserve OPC IDs and cannot rely on slot order as identity.
8. The output package is complete, has `execution_status=NOT_RUN`, and contains no media acceptance claim.
Any failed gate blocks compilation and leaves execution untouched.
## Fixed Regression Boundary
Use the existing static package without embedding its full fixture:
- `D:\Hermes\xiaonan-memory\opc-mvp\05_h3_prompt_package\h3_prompt_package.json`
- `D:\Hermes\xiaonan-memory\opc-mvp\03_storyboard_timeline\opc_shots.json`
- `D:\Hermes\xiaonan-memory\references\reuse-scout\video-pipeline-reuse-scout-v0.1.md`
The MVP baseline contains three `reference_to_video` shots, four declared dialects,
`selected_dialect=aimixer_director`, and static structure PASS. Its execution, model ID,
asset binding, media QC, and package status are `NOT_RUN`/pending because locked assets and
a runtime submission were not established. Do not promote this baseline to video PASS.
## Verification Checklist
- [ ] Closed shot and source hashes were checked.
- [ ] Every visible dependency has one approved locked binding.
- [ ] Prompt, state, continuity, dialogue, and audio preserve upstream meaning.
- [ ] Exactly one dialect adapter and version were used.
- [ ] URI/slot mappings retain OPC IDs, versions, hashes, and order.
- [ ] Output is one complete package with `execution_status=NOT_RUN`.
- [ ] No video, runtime, media QC, or human acceptance claim was made.
