---
name: gpt-image-subject-assets
"description": "Use when compiling approved OPC asset manifests into one auditable GPT Image subject-asset result."
version: 0.2.0-rc
author: Hermes Agent
license: MIT
metadata:
  hermes:
    category: creative
    tags: [opc, gpt-image, subject-assets, provenance, qc]
    related_skills: []
---
# GPT Image Subject Assets
## Purpose
Compile an approved upstream asset specification into one GPT Image subject-asset task,
then accept exactly one result only after byte-level and visible-fact QC pass. The node
owns asset sufficiency, prompt compilation, controlled generation, and asset lock evidence.
It does not repair upstream definitions or design missing assets.
## Use When
- An approved character, scene, or prop manifest is ready for subject-asset generation.
- A character identity master needs a sourced state version.
- A locked asset must be regenerated with the same provenance and declared variables.
Do not use this node to extract assets, write story, split shots, design motion, or create
an unsourced visual concept. A static preflight pass is not a generated image pass.
## Boundary
The node reads only the approved manifest, its declared source files, approved reference
images, locked runtime configuration, and this Skill. It does not read chat additions,
web pages, unregistered files, another project's settings, or model defaults as facts.
Every prompt fact must resolve to a source field or a rule in this Skill.
The node may return `SUCCESS` only for one formally accepted image after real generation,
byte/pixel verification, and independent visible-fact QC. It may otherwise return one
explicit blocking or failure result. Internal candidates are implementation detail and are
never reported as final alternatives.
## Required Input
Input is one versioned JSON-like request containing:
- `node_run_id` and `prompt_schema_version`;
- approved `source_manifest[]` with path/URI, version, approval status, and SHA-256;
- `asset_spec` with `asset_id`, `asset_type`, `spec_version`, and `state_version`;
- sourced `visible_facts`, `required_invariants`, `allowed_changes`, and `explicit_unknowns`;
- controlled runtime `provider`, `runtime_model_id`, endpoint, and credential reference;
- requested size, quality, background, output format, and bounded retry count;
- ordered `reference_images[]`, or an explicit empty list.
A credential reference may identify a secret but must never contain a secret value.
## Asset Sufficiency
A character is sufficient only when stable identity facts support repeatable recognition.
A state version contains sourced changes only; it never absorbs a scene, prop, or ability.
Unknown age, gender, face, body, costume detail, or other identity fact remains unknown.
A scene is sufficient only when its spatial core, orientation/topology, visible anchors,
and requested state are sourced. A `.placeholder` scene is not drawable merely because
its name is specific.
A prop is sufficient only when repeatable geometry, material, structure, and state facts
are available. A state chain does not prove that a reusable prop master exists.
If sufficiency fails, stop before generation with `ASSET_BLOCKED` and list affected fields.
Do not ask the customer to fill a gap inside this node and do not turn a vague noun into
a design brief.
## Closed-Input Compilation
1. Verify source paths, versions, approvals, hashes, IDs, and state version.
2. Resolve every visible prompt fact to a source location or rule identifier.
3. Copy explicit unknowns into the internal unknown-preservation set.
4. Separate identity master, state delta, scene, prop, and ability bindings.
5. Apply the character/scene/prop sufficiency test above.
6. Validate runtime model, endpoint, size, quality, background, format, and retry budget.
7. Validate every reference image and preserve its declared order and role.
8. Emit one compiled task or one typed block; completion means every field is accounted for.
## Prompt Rules
The prompt contains only sourced visible facts, required invariants, the current state delta,
and neutral inspection requirements. It may describe framing, plain presentation, or a clean
background when required to inspect the subject. It must not add biography, motivation,
cinematic action, setting history, symbols, text, decorative architecture, or style facts.
Unknowns are not negative prompts and are not silently filled by model convention. Preserve
them as unknown in the fact map; use neutral wording only when it does not assert a value.
Keep external props, abilities, and scene bindings outside the identity master prompt.
## Reference Order
For an edit, the reference manifest is ordered, explicit, and auditable. Each item has a
reference ID, version, source, SHA-256, role, related asset ID, invariants, and allowed
changes. The compiler follows the approved order exactly. The order is a semantic input,
not a cosmetic list.
Use the OpenAI-style anchor-to-continuation sequence when that sequence is approved:
identity anchor first, then approved state or scene references, then narrowly scoped detail
references. Do not infer that multiple images guarantee identity preservation. An image
without provenance, role, or order is not a valid reference.
## Runtime And 4K
Read the actual `runtime_model_id`, endpoint, provider, and supported parameters from
controlled configuration at execution time. Never promote a provider default or display
label into a controlled model ID. Record requested and actual values separately.
Native 4K is a hard requirement for a 4K request: verify actual decoded pixels, not a
requested size string. The confirmed baseline is GPT Image 2 landscape `3840x2160` with
decode, pixel readback, and SHA-256 PASS. This does not establish portrait or square 4K;
each aspect ratio needs its own real test. Do not upscale and call it native 4K.
## Generation And Unique Result
Generate a bounded set of internal candidates only when preflight is eligible and runtime
validation passes. Retry only by changing a declared generation variable or supported
parameter. Never add facts to rescue drift. Stop when the retry budget is exhausted.
The node returns exactly one formal result. A result is `SUCCESS` only when one image is
selected by the node's QC record and all lock evidence is complete. The existence of an
API response, URL, or plausible preview is not acceptance. More than one formal final
asset is a contract failure.
## Actual-Pixel QC
Decode the returned bytes and read back MIME, format, byte count, width, height, alpha or
background behavior where relevant, and output SHA-256. Compare actual values to the lock
record and requested constraints. Verify that the file is readable after saving, not just
that the provider response parsed.
Run independent visible-fact checks for identity, state, scene topology, prop structure,
unknown preservation, and responsibility separation. Machine checks cannot fill human
checks. Keep `human_qc=PENDING` until a reviewer has inspected the actual image.
## Minimal Hard Gates
1. Closed approved inputs, versions, IDs, approvals, and source SHA-256 are complete.
2. Asset sufficiency passes for the requested character, scene, or prop.
3. Every prompt fact is sourced; explicit unknowns are preserved and responsibilities stay separate.
4. Every reference has approved provenance, ID/version/SHA, role, and exact order.
5. Controlled runtime model, endpoint, provider, and parameters are supported and verified.
6. Actual decoded output format, bytes, pixels, alpha/background, and output SHA-256 match the record.
7. Required invariants and independent visible-fact QC pass, including no invented unknowns.
8. One and only one formal result has a complete provenance, audit, and lock record.
Any failed gate returns a typed block or failure and leaves the asset unlocked.
## Result Contract
Return one structured result with `node_run_id`, `status`, timestamp, source manifest,
asset ID/type/state, compiled prompt and fact-to-source map, runtime model/endpoint,
requested and actual parameters, ordered reference manifest, artifact path, MIME/format,
bytes, dimensions, alpha/background result, output SHA-256, QC checks, retry history,
and lock record when successful.
Use `SUCCESS` only for the accepted single image. Use `ASSET_BLOCKED` for insufficient
facts, `PROVENANCE_BLOCKED` for illegal or unverifiable inputs, `MODEL_BLOCKED` for runtime
or parameter problems, `POLICY_BLOCKED` for provider refusal, and `QC_FAILED` when outputs
exist but no candidate passes. No blocked result may carry a lock record.
## Fixed Regression Boundary
Use these existing materials without embedding their fixture bodies:
- `D:\Documents\我的文档\十二时辰_第一章_剧本资产提取_Skill测试版v0.11.md`
- `D:\Documents\我的文档\十二时辰_第一章_逐镜资产绑定_v0.11.csv`
- `D:\Hermes\xiaonan-memory\references\opc-gpt-image-subject-assets-preflight-v0.1.md`
- `D:\Hermes\xiaonan-memory\opc-mvp\04_gpt_image_request\request_manifest.json`
The runtime/static evidence for this candidate must be read from the current regression
artifacts before claiming a PASS. The confirmed runtime baseline is the real native
landscape `3840x2160` test recorded in `D:\Hermes\xiaonan-memory\opc-mvp\04_gpt_image_request\`.
If the referenced preflight comparison report cannot be independently read and matched,
record the static comparison as `PENDING_REVIEW`, not `21/21 PASS`. The runtime baseline
does not establish portrait or square 4K, or every story asset.
## Verification Checklist
- [ ] Only approved files and references were read.
- [ ] Sufficiency and unknown-preservation decisions are recorded.
- [ ] Model and parameter values came from controlled runtime configuration.
- [ ] Actual image pixels and SHA-256 were read back from bytes.
- [ ] Machine QC and human visible-fact QC are separate.
- [ ] Exactly one SUCCESS artifact or one explicit block was returned.
- [ ] A failed or pending asset remains unlocked.
