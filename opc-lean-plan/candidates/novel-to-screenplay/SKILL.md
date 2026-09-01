---
name: novel-to-screenplay
description: "Use when converting an identified novel chapter into one traceable, performable screenplay package."
version: 0.2.0-rc
author: Xiaonan
license: MIT
metadata:
  hermes:
    tags: [opc, novel-adaptation, screenplay, traceability]
    related_skills: [screenplay-asset-extraction]
---
# Novel To Screenplay
## Overview
Convert one identifiable novel or chapter into one complete, performable screenplay
package for the OPC pipeline. Preserve source facts, agency, causality, information
timing, dramatic cost, and continuity while making prose observable or audible.
This node is closed after source submission: no interview, candidate drafts, or
exposed internal reasoning.
## When To Use
Use for novel-to-screenplay, web-fiction-to-screenplay, and chapter dramatization.
Do not use for original fiction, continuation, shot design, storyboards, asset
extraction, image/video prompts, model settings, generation, or platform engineering.
## Contract
**Unique input:** one identifiable source prose package: novel/chapter text, user-
locked constraints, and available project/source version metadata. A summary alone
is not source prose. Missing identifiable prose returns `INPUT_ERROR`.

**Unique output:** exactly one external result: `SUCCESS` with the complete package,
`INPUT_ERROR` for missing input, or `ADAPTATION_FAIL` for unresolved conflict,
rights/provenance uncertainty, or failed gates. Never emit a partial success.

Priority is user-locked constraints, source prose, verified project rules, then
conservative defaults. Separate fact, rule, research conclusion, inference, and
unknown. Never silently repair a core contradiction. Missing scope becomes one
complete unit; missing character detail stays unknown; ambiguity takes the smallest-
change reading preserving causality.
## Hard Gates (10)
1. **Source:** prose, scope, version boundary, and provenance are identifiable.
2. **Facts:** locked identities, relationships, proposition, ethics, results, and
   ending nature are preserved or explicitly declared changed.
3. **Phenomena:** figurative/mimetic labels are separated from observable event,
   supported mechanism, unknowns, and retained dramatic function.
4. **Agency:** each decisive choice has a character, motive, knowledge, opportunity,
   action, result, and cost.
5. **Information:** each reveal has possessor, audience, timing, transfer reason,
   and consequence; unauthorized knowledge is blocked.
6. **Scenes:** each scene has entry state, task, conflict/turn, action, result, and
   exit state; compression cannot erase agency or repayment.
7. **Performance:** key turns are visible/audible and live; no retrospective
   replacement of awakening or unplanted coincidence carrying the plot.
8. **Continuity:** identity anchors and story-state versions are explicit; props,
   abilities, injuries, and social/temporal changes have ordered causes.
9. **Trace:** key causality, choices, reveals, and compensation trace both ways to
   source or explicit addition; at least 90% of scenes are traceable.
10. **Release:** local 11-item rubric is at least 38/44, every item at least 3,
    regression passes, and no veto remains.
A failed gate returns to its earliest responsible step; never invent a missing fact.
## Short Pipeline
1. **Freeze source.** Record identity, scope, version boundary, locked constraints,
   provenance/rights status, and unknowns. Completion: every segment has an ID.
2. **Set spine.** State proposition, protagonist objective, opposition, irreversible
   turn, cost, and immediate debt. Completion: it explains the main causal chain.
3. **Layer information.** Track source, character, audience/opponent knowledge,
   secrets, misbeliefs, and hooks. Completion: every key reveal has owner and effect.
4. **Recover phenomena.** Record phrase, observer label, observable event, smallest
   supported mechanism, function, and risk. Do not turn era labels into science or
   add supernatural rules. Completion: every high-impact case is decided or unknown.
5. **Externalize psychology.** Convert trigger to reaction, choice, consequence via
   action, dialogue, sound, objects, witnesses, or hesitation. Completion: beats
   change the situation rather than merely narrating it.
6. **Compile scenes.** Record time/place, participants, entry state, task, pressure,
   turn, action, dialogue/sound, result, and exit state. Use live reversal: pressure,
   trigger, manifestation, reaction, cost, new problem. Completion: each scene is
   irreplaceable and performable.
7. **Lock states.** Separate invariant identity from age, clothing, hair, makeup,
   injury/dirt, props, body, ability, voice, and speech state. Each appearance uses
   supported identity plus state. Completion: changes have range, cause, and source.
8. **Register changes.** Mark retain, compress, merge, reorder, externalize, add, or
   delete with source/reason. Record compensation for lost information, evidence,
   action, or payoff. Completion: no material change is unaccounted for.
9. **Review package.** Assemble screenplay scenes, character/state table, prop/
   ability flow, beats/hooks, capacity estimate, trace and compensation registers,
   and continuity constraints. Run all gates and rubric; up to five hidden repair
   rounds rerun the complete check. Completion: one release decision exists.
## Optional Mature Bases
Dramatron may inform the order constraints -> characters/locations -> scene beats ->
action/dialogue. Fountain or screenplay-tools may optionally parse/format screenplay
text. These are optional methods/libraries, not dependencies or platform scope.
Do not build a runner, database, API controller, checkpoint system, or scoring service.
## Fixed Regression
Use `D:\Documents\我的文档\十二时辰_第一卷_01.md`,
`D:\Hermes\xiaonan-memory\references\十二时辰_第一章_小说改剧本回归验收表.md`, and
`D:\Hermes\xiaonan-memory\references\小说改剧本_专业能力评分量表_v0.1.md`.
The verified release line is `38/44`. Preserve: 牛满为女性且是首位觉醒时神；村口老槐树下
吊缚一天一夜；王二羞辱并欲卖入窑子；牛形木簪折断；赎身钱入泥；时间停止而非变慢；
挣绳撼树；未来蓝火令王二衰老；牛满支付寿数；十二神位、其他时神和龙神线索只埋下不解释完；
打火机借入、使用、定时消失归还、现代火柴替代闭环。
## Common Pitfalls
1. Treating a summary as source.
2. Giving decisive action to a helper, system, or power.
3. Presenting metaphor as unsupported science.
4. Replacing a live turn with backstory.
5. Mixing incompatible character states.
6. Explaining every buried mystery in the first unit.
7. Hiding compression without compensation.
8. Adding camera, prompt, or model decisions.
9. Passing below 38/44 or any veto.
10. Returning multiple drafts or unfinished text.
## Verification Checklist
- [ ] One prose input and scope boundary were frozen.
- [ ] Ten gates passed and no veto remains.
- [ ] Decisive actions have motive, knowledge, opportunity, result, and cost.
- [ ] High-impact figurative expressions have decisions or unknowns.
- [ ] Every scene is state-changing and performance-ready.
- [ ] Identity and story state are separate and supported.
- [ ] Trace and compensation registers are bidirectional.
- [ ] Score is at least 38/44 and every item at least 3.
- [ ] Fixed regression assertions passed on the complete package.
- [ ] Only `SUCCESS`, `INPUT_ERROR`, or `ADAPTATION_FAIL` was exposed.
