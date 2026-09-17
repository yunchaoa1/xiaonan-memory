---
name: agent-cost-optimization
description: "Use when reducing Agent token cost."
version: 0.1.0
author: 小南
license: MIT
platforms: [windows, macos, linux]
metadata:
  hermes:
    tags: [agent, tokens, prompt-cache, context, cost, hermes]
    related_skills: [hermes-agent, autonomous-ai-agents]
---

# Agent Cost Optimization

## When to Use

Use when an Agent is consuming too many tokens, prompt-cache hit rate is unstable, context is
repeatedly carrying bulky tool output, or a provider-specific cache optimization needs verification.

Reduce recurring AI Agent cost while preserving task quality. The class covers prompt-cache
stability, context growth, tool-result retention, request count, and provider-path verification.
It applies to Hermes and other OpenAI-compatible Agent runtimes.

## Core Model

Treat cost as two separate levers:

1. **Request work**: reduce unnecessary turns, duplicate tool calls, retries, and oversized
   tool output.
2. **Repeated prompt work**: keep the stable prefix identical so the provider can reuse cached
   processing. Put volatile task state, timestamps, progress, and per-turn data after the stable
   prefix.

Do not assume that a cache-related parameter supported by one runtime or API mode works in
another. Cache behavior is a property of the complete runtime path: model, provider, endpoint,
API mode, request payload, proxy transformations, and server-side billing policy.

## Procedure

### 1. Establish a baseline

Record the actual running machine, Hermes profile, model, provider, endpoint, API mode, context
window, and a recent usage window. Use `hermes insights --days 7` for a first baseline. Capture
input tokens, output tokens, request counts, and any provider-reported cached-input fields when
available. Do not promise a percentage reduction from configuration alone.

### 2. Read the real source material

When the recommendation comes from a locally saved webpage, parse the document payload rather
than repeatedly loading the full HTML shell. Separate article body, code examples, navigation,
CSS, and runtime noise. Preserve the source path and record which claims are generic versus
provider-specific. Treat OpenClaw examples as OpenClaw evidence until Hermes behavior is verified.

### 3. Map the cache boundary

Identify what is stable across turns:

- system prompt and personality;
- tool schemas and enabled toolsets;
- durable project rules and selected skills;
- stable reference facts.

Keep these in the same order and wording during a session. Append dynamic user intent, current
state, tool results, timestamps, and progress after them. Avoid changing tools, system rules,
model routing, or skill loading halfway through a session because that can break the reusable
prefix and may require a fresh session.

### 4. Control context growth

Prefer deterministic controls before adding an auxiliary summarization call. In Hermes, inspect
and tune `compression` settings. For large-context models, enable proactive pruning of old,
bulky tool results because ratio-based compression may not fire for a long time. Use a minimum
result-size threshold and a minimum reclaim threshold so small outputs are not churned. Use idle
compaction for long-lived sessions that resume after a substantial pause.

A conservative Hermes starting point is:

```yaml
compression:
  enabled: true
  tail_mode: lean
  in_place: true
  proactive_prune_tokens: 48000
  proactive_prune_min_result_chars: 8000
  proactive_prune_min_reclaim_tokens: 4096
  idle_compact_after_seconds: 1800
```

These values are starting points, not universal truths. Verify the live defaults and semantics
against the installed Hermes version before applying them.

### 5. Protect the stable prefix

Use stable system-level instructions for durable behavior. Do not repeatedly paste the same long
rules into each user turn. Keep session-specific notes in compact structured records and place
them after stable instructions. Read large files in bounded, relevant windows; extract only the
needed section; write a concise reference when the information will be reused. Avoid sending
full HTML, full logs, or duplicated tool output when a targeted extraction is sufficient.

When studying a locally saved webpage, parse its document payload and reconstruct the article body
from ordered records. Exclude CSS, scripts, navigation, catalogue headings, recommendation blocks,
and runtime noise. A heading such as "Hermes cache prompt" is not evidence that the body contains a
Hermes implementation; verify the actual code and configuration claims separately.

For Hermes, keep the prompt/tool prefix stable during a session. Avoid changing enabled toolsets,
MCP discovery, system rules, or model routing after the first provider request unless a new session
is acceptable, because tool-schema or system-prompt changes can invalidate reusable prefix work.

### 6. Verify provider-specific claims

Before adding `prompt_cache_key`, `prompt_cache_retention`, `store`, Responses-only fields, or
proxy patches:

1. Confirm the active endpoint and API mode.
2. Inspect the runtime request builder or provider adapter.
3. Confirm the provider documents and bills the field as intended.
4. Check whether a proxy strips, rewrites, or rejects it.
5. Back up configuration and change one narrow variable.
6. Read back configuration and compare usage on a repeated, controlled request.

Never inject Responses-specific fields into a `chat_completions` path just because a different
Agent runtime uses them.

### 7. Apply and verify safely

Back up the active configuration before changes. Preserve unrelated dirty work. Make the smallest
supported change, restart only when the runtime requires it, and read the effective configuration
back. Compare a before/after window with the same kind of workload. If cache statistics are not
exposed, report reduced context/request work as a proxy and state that cache hit rate itself is
unverified.

## Hermes-Specific Notes

- `proactive_prune_tokens` performs deterministic, no-LLM pruning of old tool-result payloads.
- `proactive_prune_min_result_chars` limits the pruning pass to materially large results.
- `proactive_prune_min_reclaim_tokens` prevents low-value churn.
- `idle_compact_after_seconds` compacts a stale session before its next reply.
- `tail_mode: lean` retains a smaller tail and carries continuity through summaries/anchors.
- `in_place: true` avoids unnecessary session-id rotation during compaction.
- Config changes generally require a fresh Hermes process or gateway restart; tool/skill changes
  require a new session.

## Pitfalls

- Do not confuse a cheaper model with better cache reuse; measure both quality and repeated-input cost.
- Do not lower context retention so aggressively that the Agent repeats research or re-reads files.
- Do not enable an auxiliary LLM compression pass for every turn without accounting for its cost.
- Do not edit provider packages or proxy code before proving the active runtime path is affected.
- Do not treat a saved webpage's navigation title or code-block heading as the article body.
- Do not claim cache improvement solely because a config command succeeded; verify effective config and usage.
- Do not alter API keys, model IDs, or proxy addresses as an incidental optimization.

## Verification Checklist

- [ ] Baseline usage and active runtime path recorded.
- [ ] Stable prefix and dynamic suffix identified.
- [ ] Large tool-result retention addressed with supported deterministic controls.
- [ ] Provider/API-mode compatibility checked before cache fields are added.
- [ ] Configuration backed up and read back after modification.
- [ ] Before/after usage compared, with unverified metrics labeled honestly.

## References

See `references/hermes-cache-and-provider-mapping.md` for the Hermes settings, source checks,
and provider-specific boundary captured from the initial implementation.
