---
name: writing-opc-entry
description: Use when OPC must turn one customer's idea into one first-usable novel autonomously, with six hard gates, hidden revision, and a closed downstream handoff.
version: 0.6.0-rc
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [opc, writing, novel, one-submission, quality-gates]
    related_skills: [opc-creative-skill-authoring, short-drama-story-engine]
---

# OPC 写作入口

## Overview
本 Skill 把客户一次提交的创意，自动发展为第一次对外即可使用的唯一小说底稿。
它只负责小说写作入口，不负责改编剧本、拆分镜、设计资产、生成媒体或搭建平台。

客户在过程中不参与选择、不接收候选正文、不被要求补写。内部可以反复推演、检查和定向修订；
第一次对外出现的正文必须是已经通过逻辑底线的唯一成品。

## When to Use
- 客户提交一句话、关键词、人物关系、世界设定、片段、主题或混合创意，要求生成小说。
- 需要保持题材、语言、结构和节奏开放，而不是套用固定类型模板。
- 需要将完成小说交给下游 OPC 节点，并隔离聊天历史、网络和其他项目素材。

不用于剧本改编、分镜或提示词生成、外部资料检索、客户共创问答或多候选交付。

## Core Contract
1. **唯一开放入口**：运行时唯一外部创意来源是本次客户提交 `customer_idea` 及同一载荷中的明确约束。
2. **一次提交**：客户提交次数为 1；写作过程中不提问、不等待确认、不接收外部创意补料。
3. **唯一首交**：完成时只对外交付一部完整小说；内部草稿、备选路径和失败稿不得外显。
4. **下游封闭**：输出完成后，下游只能使用本版本小说、随附记录及已验收的结构化上游产物。
5. **事实不越权**：客户显式事实和明确限制不可静默改写；缺项只能保守补齐并留下记录。
6. **结果可判定**：最终只能是 `completed` 或 `blocked`，两者互斥。

## Input Boundary

最小输入是一个非空、具有小说语义的 `customer_idea`。接受自然语言、结构化对象、数组或混合形式。
题材、受众、语言、声音、节奏、结构、结局方向、必须包含和必须避免，只有在本次载荷中明确出现时才生效。

运行前登记：

- `user_facts`：客户明确说出的事实、限制、偏好和禁区，保持原意并绑定本次来源。
- `inferences`：由客户内容直接推出的最小必要信息，不冒充客户事实。
- `decisions`：为解决缺项、冲突或结构问题所作的选择，附简短理由和风险。

不得从历史会话、其他项目、网络、未提供的链接内容或口头补充获取创意事实。链接只有在本次提交中已经给出摘要时，
才按该摘要处理。显式事实冲突时，不任选其一冒充事实；采用能同时容纳它们的最窄解释，或进入 `blocked`。

## Open Entry And Diversity

入口对表达方式开放，但输出仍只有一条选定路径。根据本次输入自主选择题材表达、人物关系、冲突机制、结构、声音和节奏。
不得把所有输入压成爽文、固定反转、统一叙事声音、统一章节数或单一情绪模板。

内部可比较多个方向摘要，但只保留选择结论和可审计理由，不记录逐步思维链。必须确认选定方向尊重客户口味，
且没有把其他项目的角色、道具、情节或世界观带入本次作品。

## State And Branches

使用简洁运行记录表达状态：

```yaml
provenance_and_decisions:
  schema_version: opc-writing/0.6.0-rc
  run_status: completed | blocked
  input_state: complete | missing_resolved | conflict_resolved | blocked
  selected_path_count: 1
  customer_submission_count: 1
  customer_midprocess_intervention_count: 0
  exposed_internal_draft_count: 0
  hard_gate_results: []
  downstream_handoff: {}
```

- `completed`：顶层只能有 `novel` 和记录；小说正文恰好一部，首交为 1，六门禁全部通过。
- `blocked`：顶层只能有 `blockage` 和记录；不得有标题、梗概、样章、空正文或候选正文。

不得同时出现 `novel` 与 `blockage`。不得用 `completed` 隐藏已知失败，也不得用 `blocked` 隐藏可交付小说。
空输入、无小说语义单元，或无法在不违反锁定事实的情况下消解核心冲突时，进入 `blocked`。
阻断对象说明原因、相关来源、是否需要新请求以及 `question_asked: false`；本次运行不通过追问恢复。

## Automatic Internal Loop

1. **锁定输入**：登记本次事实、限制、偏好和来源；每条显式内容可回溯后完成。
2. **处理状态**：以最少新增设定、最少巧合和人物自主选择补齐非关键缺项；记录推导、默认、决策与风险。
3. **维护故事状态**：内部跟踪事实、人物关系、目标、资源、知识、地点、时间、事件后果和伏笔责任。
4. **选择路径**：比较必要的题材、冲突、结构、声音和节奏方向，只保留一个 `selected` 路径；候选正文为 0。
5. **生成工作稿**：沿选定路径写作，人物行动来自欲望、知识、机会和选择，并产生代价与后果。
6. **执行门禁**：逐项检查正文和状态证据；失败项回到内部工作稿定向修订，不得外显。
7. **全书复核**：修订后复查受影响门禁，再做全书连续性复核；六项均通过才可完成。
8. **唯一输出**：输出唯一小说和最小记录，或唯一阻断对象；结束后不得回开入口。

内部修订可循环多次。“一次生成”指一次提交后第一次看到的版本可用，不限制内部检查次数。
任何失败稿都不得成为客户的返工任务。

## Six Hard Gates

六门禁是对外交付的最低标准，必须全部有本次运行的正文证据；任一最终失败只能 `blocked`。

1. **故事事实**：时间、地点、规则、能力、道具和事件不矛盾；新增关键事实可追溯。
2. **人物能动性**：身份、关系和知识连续；关键行动有动机、机会、选择、代价和后果，核心解局不靠外力救援。
3. **因果**：转折有铺垫；信息取得有路径；巧合不承担核心解局；伏笔有兑现或延后责任。
4. **节奏**：主要单元改变知识、风险、关系、资源、地位或选择；无连续空转和重复说明。
5. **可持续性**：矛盾由新后果继续生长；扩展依靠新选择而非重复套路；结局符合本次承诺。
6. **剧情连续性**：相邻章节或段落有承接；人物、地点、道具、目标和信息状态不无来源跳变。

```yaml
hard_gate_results:
  - gate: story_facts | character_agency | causality | pacing | sustainability | plot_continuity
    status: pass_after_revision | pass_first_check | blocked
    evidence: [body_location_or_state_observation]
    revision_note: concise_reason_or_none
```

不得预填或臆称 `pass`。只有实际检查到正文/状态证据才能记录通过。文采、意象、商业偏好和惊艳度是软诊断，
不能替代六门禁，也不能把未通过的逻辑稿升级为 `completed`。

## Minimal Output

完成分支只交付一部小说，以及说明来源、关键决策、六门禁和下游边界的最小记录。无某类内容使用空数组或 `NONE`，不得编造。

```yaml
completed:
  novel: one_complete_novel
  provenance_and_decisions:
    run_status: completed
    first_external_novel_count: 1
    all_six_logic_gates_pass: true
    hard_gate_results: six_actual_results
    selected_path_count: 1
    downstream_handoff:
      availability: complete
      allowed_sources: [this_novel, this_record, accepted_upstream_artifacts]
      forbidden_sources: [customer_chat_supplement, history, network, other_projects, drafts]
```

```yaml
blocked:
  blockage: {message: nonempty_reason, question_asked: false, novel_count: 0}
  provenance_and_decisions:
    run_status: blocked
    first_external_novel_count: 0
    all_six_logic_gates_pass: false
    downstream_handoff: {availability: blocked}
```

## Downstream Closed Boundary

下游从本节点结束即封闭，只读当前版本小说、当前记录、已验收的结构化上游产物和下游已锁定规则。
禁止读取客户聊天补充、历史会话、网络资料、临时口头解释、其他项目、内部候选路径、未验收草稿和制作期材料。

下游不得静默改写事实、人物状态、时间线或因果；缺失信息只能使用已验证默认值，或返回自身 `blocked`。
不得向客户追问，不得回开写作入口；`blocked` 交接不得被当作可用小说继续生产。

## Completion Checklist

- [ ] 一次提交，过程中无提问、等待或外部创意补料。
- [ ] 显式事实已锁定，缺项/冲突有最小决策记录。
- [ ] 内部只选一条路径，外部候选正文为 0。
- [ ] 六门禁均有实际证据，失败项已修订并复核。
- [ ] 输出恰好命中 `completed` 或 `blocked`，二者互斥。
- [ ] `completed` 只有一部完整小说；`blocked` 没有小说正文。
- [ ] 下游来源边界已写明，不读取聊天历史或其他项目。
- [ ] 未把静态夹具或未执行结果写成运行时 PASS。

## Fixed Regression Status

固定状态：`PASS`。

- `FIX-FIRST-DELIVERY`：最终 `PASS`，结果 `1/0/0/1`。
- 六门禁：最终 `PASS`，评分 `[4,4,4,4,3,4]`。
- 多样性 A/B：最终 `PASS`。
- `blocked` 与来源隔离：最终 `PASS`。

证据路径：

- `D:\Hermes\xiaonan-memory\opc-lean-plan\evidence\FIX-FIRST-DELIVERY-final-PASS.md`
- `D:\Hermes\xiaonan-memory\opc-lean-plan\evidence\diversity-ab-final-PASS.md`
- `D:\Hermes\xiaonan-memory\opc-lean-plan\evidence\blocked-source-isolation-final-PASS.md`
