---
name: opc-workflow-reuse
description: Use when improving OPC workflows with proven foundations.
version: 0.1.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    category: creative
    tags: [opc, ai-manga, workflow, reuse, one-click, validation]
    related_skills: [opc-creative-skill-authoring, novel-to-screenplay-opc-test, screenplay-asset-extraction-opc-test, screenplay-to-15s-storyboard-opc-test, gpt-image-subject-assets-opc-test]
---

# OPC Workflow Reuse

## Purpose

Use this skill when the OPC one-click manga-drama pipeline is becoming slow or over-engineered. The goal is to preserve the user's verified creative results, borrow mature foundations for unfinished work, and deliver the smallest testable Skill package first.

This is a workflow decision skill. It does not replace the creative node Skills, build an OPC platform, or decide story content.

## When to Use

Load this skill when:

- the user asks whether similar products or workflows already exist;
- an OPC node is incomplete and a mature implementation may shorten delivery;
- the work is expanding into schemas, runners, databases, adapters, or multi-provider infrastructure;
- a deadline requires a small testable version;
- the team has accumulated more research and reports than usable Skill output.

## Core Principle

> Keep our verified creative rules as the product core. Use mature external projects as scaffolding for unfinished mechanics. Analyze their strengths and weaknesses, then adapt only what improves the OPC node.

Never restart a validated node merely because a similar commercial product exists. Never turn a research report into a new platform project.

## Decision Order

1. Lock the immediate deliverable and deadline.
2. Inventory existing artifacts and their real evidence status.
3. Classify each capability as `KEEP`, `BORROW`, `ADAPT`, `DEFER`, or `REJECT`.
4. Search only for the missing capability, not for a perfect all-in-one replacement.
5. Verify candidate license, maintenance, actual capability, and runnable evidence.
6. Extract the smallest transferable module or method.
7. Add OPC-specific rules, boundaries, and regression evidence.
8. Produce one candidate Skill without replacing the validated original.
9. Run a fixed sample and an independent review.
10. Replace the original only after the candidate passes comparison.

## Artifact Classification

### KEEP

Use for rules, samples, and node outputs that already have real acceptance evidence. Examples include the one-click first-delivery contract, six logic gates, the v0.11 asset extraction rules, emotion-directed shot fields, and verified native image-generation behavior.

Do not weaken a KEEP item merely to match an external tool's simpler schema.

### BORROW

Use for a mature general-purpose mechanism that can be isolated behind the OPC node boundary. Examples include Fountain/screenplay-tools parsing, OpenTimelineIO time arithmetic, or an established outline-to-draft orchestration pattern.

Borrow the mechanism, not unrelated UI, database, business model, or undocumented behavior.

### ADAPT

Use when the external mechanism solves only part of the OPC need. Add OPC provenance, identity/state, continuity, source boundaries, first-delivery rules, or model-specific prompt constraints as required.

### DEFER

Use for platform concerns that do not improve the current Skill's professional conversion: databases, job queues, billing, generic runner frameworks, full multi-provider routing, enterprise collaboration, and large-scale stress suites.

### REJECT

Use when the license is incompatible or unclear, the candidate has no reliable evidence, the mechanism conflicts with the user's one-click boundary, or it would import more complexity than it removes.

## Minimal Candidate Shape

A candidate Skill should normally contain:

- one purpose and explicit non-responsibilities;
- one required-input section;
- one short transformation procedure;
- one unique output contract;
- no more than ten hard gates;
- one fixed regression sample with evidence paths;
- one failure/blocked path;
- a short note identifying what was kept, borrowed, and adapted.

A Skill is not improved by adding every possible field. Add a field only when it protects a real downstream decision, continuity fact, or acceptance gate.

## Market and Open-Source Reconnaissance

Evaluate candidates in this order:

1. Does the candidate cover the exact missing capability?
2. Is the license compatible with the intended use, or can the component remain process-isolated?
3. Is it maintained enough for the required use?
4. Is there runnable evidence such as local tests, release artifacts, official examples, or a reproducible demo?
5. What is the smallest module we can transfer?
6. What does the candidate fail to guarantee for Chinese AI manga production?

Record evidence separately from marketing claims. A product page that says “consistent characters” is not proof of continuity across a real sequence. A repository with tests proves code behavior, not creative quality. A generated image proves model execution, not asset correctness.

The reusable comparison template is in `references/reuse-evaluation-template.md`.

## Known Reuse Pattern

For the OPC creative pipeline, a practical combination is:

- writing orchestration: borrow automatic outline → draft → fact-check → targeted revision from mature long-form writing tools;
- hard story state: borrow deterministic state and continuity checks from a tested novel-state engine;
- screenplay ingest: borrow Fountain and screenplay-tools parsing;
- production taxonomy: borrow ScriptBreak/OSF categories while keeping OPC identity/state rules;
- shot timing: borrow OpenTimelineIO time and serialization;
- storyboard relations: borrow Kitsu-like sequence/shot/casting concepts without importing its server;
- image generation: use the verified GPT Image backend and keep OPC asset sufficiency/QC rules;
- H3 prompting: borrow official workflow shapes and Director group boundaries, while keeping OPC shot and asset IDs as the source of truth.

This is a composition of foundations, not permission to copy any one project wholesale.

## Deadline Mode

When the user sets a near deadline:

1. freeze the smallest useful sample;
2. stop non-blocking reconnaissance;
3. preserve completed artifacts in place;
4. make unfinished nodes output a testable package or explicit blocked state;
5. prefer one to three real shots over a speculative full-season implementation;
6. verify files and execution output rather than trusting agent summaries;
7. report separately: structural PASS, model execution PASS, media QC PASS, and commercial-release readiness.

The user should receive a working test artifact, not a plan for a future platform.

## One-Click Boundary

The writing node is the only open creative entrance. It may enrich one customer idea internally and expose one usable novel or one explicit blocked result.

After the novel is accepted, downstream nodes are closed: they read the approved version, accepted upstream artifacts, and locked Skill defaults only. They do not read chat supplements, history, other projects, network material, or unaccepted drafts.

Internal revision is allowed before first delivery. Candidate drafts, QC notes, and repair history are not external outputs. Customer editing after receiving a usable draft is outside the node run.

## Verification Discipline

A delegated completion message is not evidence. After every delegated task:

- check target files exist;
- read the files;
- parse structured outputs;
- rerun the smallest available test;
- compare the result against the requested scope;
- mark the task complete only after verification.

When a long task is truncated or a service call fails, do not restart the same large task. Inspect the artifact matrix, keep complete items, and shrink missing work to one file or one to three shots.

## Failure Modes

- Rebuilding verified creative logic because an external product has a nicer interface.
- Treating market claims as executable evidence.
- Letting mature infrastructure become the new main task.
- Adding schemas that no current node or test consumes.
- Calling a static manifest a successful model run.
- Calling an enlarged image native 4K without checking the model's returned pixels.
- Passing external candidates, internal drafts, or research material through a closed downstream boundary.
- Estimating completion from the number of reports instead of the number of usable, verified Skills.

## Completion Check

The reuse task is complete when:

- existing verified results are preserved;
- every unfinished capability has a justified KEEP/BORROW/ADAPT/DEFER/REJECT decision;
- external evidence and license boundaries are recorded;
- the candidate Skill is shorter and more executable than the prior version;
- a fixed sample or explicit blocked path is verified;
- no platform engineering has been smuggled into a creative Skill;
- the user can test the result without reading the entire research history.
