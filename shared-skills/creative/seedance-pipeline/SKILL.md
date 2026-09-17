---
name: seedance-pipeline
description: "This skill should be used when the user asks about Seedance 2.0 workflow operations, API planning, BytePlus ModelArk, Dreamina/Jimeng surfaces, provider/router APIs, China-facing surfaces, ComfyUI, post-production, stitching, batch workflow, or integration planning.（中文触发：问Seedance工作流操作、API参数、模型规格时加载）"
license: MIT
user-invocable: true
tags:
  - workflow
  - api
  - integration
  - seedance-20
metadata:
  version: "6.6.0"
  updated: "2026-07-04"
  parent: "seedance-20"
  author: "Iamemily2050 (@iamemily2050)"
  repository: "https://github.com/Emily2040/seedance-2.0"
  openclaw:
    emoji: "🎬"
    homepage: "https://github.com/Emily2040/seedance-2.0"
---

# seedance-pipeline

Use this for operational workflows, APIs, web surfaces, post-production, and integration planning.

## Intent

Behind every API question is a person with a deadline, a budget, and something at stake on this working tomorrow. The soul of this skill is being the one voice in the room that answers with dates, sources, and a path instead of optimism. Reliability is the kindness this user needs.

## Status Rule

Always load `[参考:api-status未安装扩展，以本正文为准]` for current API and platform claims. Load `[参考:model-name-map未安装扩展，以本正文为准]` when a user says Pro, Fast, V2, or a wrapper model ID. Do not rely on old release-status memory.
Load `[参考:api-workflow未安装扩展，以本正文为准]` for implementation planning, task lifecycle, Runway/Volcengine/provider field differences, pricing caveats, upload handling, and production readiness.
Load `[参考:pro-filmmaking-standards未安装扩展，以本正文为准]` for professional film, commercial, agency, localization, post, and delivery workflows. Load `[参考:delivery-qc未安装扩展，以本正文为准]` before saying an asset is delivery-ready.

## Workflow Split

1. Web workflow: Dreamina/Jimeng surface, references, prompt, output review.
2. API workflow: Volcengine, BytePlus, Runway, fal, or provider/router docs, model ID, auth, file handling, task creation, polling/querying, cancellation/deletion, task ledger, and retrieval.
3. Professional production workflow: treatment, shot list, continuity ledger, reference rights map, review loop, post handoff, and delivery/QC.
4. Post workflow: edit, conform, stitching, stabilization, audio cleanup, captions/subtitles, color, localization, versioning, textless, and delivery.
5. First/last-frame workflow: map first frame, last frame, transition action, identity locks, and ending target.
6. Runway workflow: model `seedance2`, `runway://` uploads, audio-reference combination rules, plan/region caveats, and SDK type lag are Runway-specific.
7. Provider/router workflow: EvoLink, OpenRouter, Kie.ai, PiAPI, LaoZhang, Runware, ModelsLab, AI/ML API, MuAPI, SeeGen, Segmind, or similar surfaces must be labeled provider-specific and rechecked before code or pricing guidance.
8. China-facing workflow: prefer official ByteDance/Volcengine/BytePlus/Doubao/Jimeng/Jianying sources; workflow hosts, Chinese-language blogs, and business-partner news are not public API providers without provider-owned docs.
9. Community workflow: ComfyUI or unofficial nodes must be labeled community/unverified unless sourced.
10. Corpus-mining workflow: classify sources before reuse; extract structure and vocabulary, not unsafe raw prompts.

## Output Contract

Return the workflow path, source status, required inputs, production phase, validation steps, delivery assumptions, and risks. For professional jobs, include the next artifact to create: brief, shot list, continuity ledger, prompt batch, review packet, localization matrix, or QC preflight.
