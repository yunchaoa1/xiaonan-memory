# Hermes Cache And Provider Mapping

## Source Lesson
The locally saved Feishu article explains that repeated system prompts, tool definitions, and
background material can be reused when the stable prefix remains unchanged. Dynamic task state,
timestamps, progress, and per-turn tool output should follow the stable prefix. The article's
OpenClaw examples are provider/runtime-specific and are not proof that Hermes accepts the same
fields.

## Hermes Mapping

| Goal | Hermes mechanism | Notes |
|---|---|---|
| Trim old bulky tool output | `compression.proactive_prune_tokens` | Deterministic, no auxiliary LLM |
| Avoid pruning tiny results | `proactive_prune_min_result_chars` | Set a meaningful result-size floor |
| Avoid low-value churn | `proactive_prune_min_reclaim_tokens` | Commit only after useful reclaim |
| Compact stale conversations | `idle_compact_after_seconds` | Runs when a long-idle session resumes |
| Keep a compact recent tail | `tail_mode: lean` | Verify installed-version semantics |
| Preserve one session identity | `in_place: true` | Avoids unnecessary session rotation |

A tested conservative starting point on the referenced Hermes installation was `48000` prune
trigger tokens, `8000` minimum result characters, `4096` minimum reclaim tokens, and `1800`
seconds idle compaction. These are measured starting points, not universal defaults.

## Provider Boundary

The active route must be checked before adding cache fields. OpenAI Responses fields such as
`prompt_cache_key`, `prompt_cache_retention`, and `store` must not be injected into a
`chat_completions` request without provider documentation and request-level verification. A
proxy may strip, rewrite, reject, or bill fields differently from the upstream API.

## Verification Sequence

1. Record `hermes insights --days 7` and the active model/provider/API mode.
2. Back up the active config.
3. Change one supported compression or retention variable.
4. Read the effective config back.
5. Restart the relevant Hermes process when required.
6. Compare the same workload before and after.
7. Report cache hit rate only when the provider exposes a verified metric; otherwise report the
   measured context/request change and label cache status unverified.

## Local Evidence

The source article was saved at:
`D:\Hermes\attachments\__________________________________________________摆脱token焦虑，降低AI Agent的成本消耗的终极奥义——提高缓存命中率 - 飞书云文档.html`

The extracted body used for review was stored at:
`D:\Hermes\xiaonan-memory\references\agent-token-cache-feishu-body.txt`
