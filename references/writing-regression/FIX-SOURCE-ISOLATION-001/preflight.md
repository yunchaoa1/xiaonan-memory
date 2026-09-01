# FIX-SOURCE-ISOLATION-001 写前预演

- 测试对象：写作 Skill `v0.5.1-test`
- 运行类型：仅写前预演与污染扫描
- 执行边界：不生成小说、标题、梗概、样章、候选正文或情节答案
- 客户提交次数：`1`
- 客户中途干预次数：`0`
- 外露内部草稿数：`0`
- 小说正文数：`0`

## 1. 客户事实

来源统一锁定为本次请求 `SRC-USER-001`。

| PAD 引用 | 类型 | 客户显式事实 | 来源 | 状态 |
|---|---|---|---|---|
| PAD-001 | user_fact | 主体是一位修伞匠。 | SRC-USER-001 | locked |
| PAD-002 | user_fact | 该修伞匠能够听见别人没有说出口的告别。 | SRC-USER-001 | locked |
| PAD-003 | user_fact | 上述能力只能在下雨时发生。 | SRC-USER-001 | locked |
| PAD-004 | decision | 本次仅执行写前预演和污染扫描，不生成小说。 | SRC-USER-001 | adopted |

未由客户提供的姓名、性别、时代、地点、人物关系、告别对象、冲突解法、结局、篇幅、类型与叙事声音均保持未设定；本次不从历史、网络或其他项目补齐。

## 2. 内部路径摘要

本节只记录审计级路径框架，不包含候选正文或具体情节。

| 路径 | 检查维度 | 摘要 | 预演状态 |
|---|---|---|---|
| PATH-001 | 题材表达、人物关系、冲突机制 | 仅验证三条锁定事实能否支持人物选择与冲突；不新增专名、专属道具或情节答案。 | retained_for_future_internal_comparison |
| PATH-002 | 结构、叙事声音、节奏 | 仅验证线性与非线性、克制与其他声音、慢燃与其他节奏均未被客户锁定；不在预演中替客户定稿。 | retained_for_future_internal_comparison |
| PATH-003 | 来源隔离、下游边界 | 仅允许本次客户载荷提供创意事实；方法契约只约束流程，不贡献创意内容。 | selected_for_this_preflight |

- 选定预检路径：`PATH-003`
- 选定路径数：`1`
- 内部候选正文数：`0`
- 对外候选正文数：`0`

## 3. 来源清单

| 来源引用 | 内容类别 | 是否可提供本次创意事实 | 使用结果 |
|---|---|---:|---|
| SRC-USER-001 | 本次固定客户输入与“不生成小说”约束 | 是 | 唯一运行时外部创意来源 |
| RULE-SKILL-051 | `writing-opc-entry-test v0.5.1-test` 的程序性契约 | 否 | 仅用于来源隔离、预检字段与门禁定义 |
| 历史会话 | 禁止来源 | 否 | 未读取、未采用 |
| 历史样本/既有小说/其他项目 | 禁止来源 | 否 | 未读取、未移植 |
| 网络与链接内容 | 禁止来源 | 否 | 未访问、未采用 |
| 内部候选路径或未验收草稿 | 禁止来源 | 否 | 未生成、未采用 |

下游禁止来源保持为：`customer_chat_supplement`、`history`、`network`、`oral_explanation`、`other_projects`、`internal_candidate_paths`、`unaccepted_drafts`、`production_distillation_material`。

## 4. 污染探针扫描

扫描口径：对 `SRC-USER-001` 的客户创意文本，以及本文件“客户事实”和“内部路径摘要”中的创意陈述做 UTF-8 精确字面匹配；探针字典本身及本结果表的标签列不计入扫描语料，避免测试词自计数。未读取历史样本作为扫描语料。

| 污染探针 | 命中数 |
|---|---:|
| 牛满 | 0 |
| 十二神位 | 0 |
| 齐白兰 | 0 |
| 顾蓝汐 | 0 |
| 齐镇海 | 0 |
| 蓝宝石 | 0 |
| 寻亲 | 0 |

扫描结论：七项禁用探针均为 `0`；未发现历史内容污染。

## 5. 六门预检

说明：本次没有小说正文，以下仅检查“是否具备进入后续内部验证的条件”，不冒充正文门禁已通过；无 `BODY-*` 证据，不填写 `pass_first_check` 或 `pass_after_revision`。

| 门禁引用 | 门禁 | 写前检查 | 状态 |
|---|---|---|---|
| GATE-PREFLIGHT-001 | story_facts | 三条客户事实已拆分、锁定并指向本次 `SRC-USER-001`；未加入历史事实。 | preflight_ready_not_executed |
| GATE-PREFLIGHT-002 | character_agency | 已保留人物动机、知识、机会、选择、代价、后果的后续检查位；预演未代写行动。 | preflight_ready_not_executed |
| GATE-PREFLIGHT-003 | causality | 已保留能力条件、信息路径、转折铺垫及伏笔责任的后续检查位；预演未生成因果链。 | preflight_ready_not_executed |
| GATE-PREFLIGHT-004 | pacing | 已保留每个主要单元必须改变状态的后续检查位；预演未生成叙事单元。 | preflight_ready_not_executed |
| GATE-PREFLIGHT-005 | sustainability | 已保留扩展依靠新后果而非重复套路的后续检查位；预演未生成扩展内容。 | preflight_ready_not_executed |
| GATE-PREFLIGHT-006 | plot_continuity | 已保留相邻单元承接和人物、地点、道具、目标、信息状态连续性的后续检查位；预演未生成剧情。 | preflight_ready_not_executed |

六门预检结论：`6/6` 已建立检查位，`0/6` 被宣称为正文门禁通过，正文证据数 `0`。

## 6. 运行计数与结论

```yaml
case_id: FIX-SOURCE-ISOLATION-001
execution_scope: preflight_only
customer_submission_count: 1
customer_midprocess_intervention_count: 0
exposed_internal_draft_count: 0
novel_body_count: 0
runtime_external_creative_source: SRC-USER-001
history_read_count: 0
network_source_count: 0
historical_content_migration_count: 0
forbidden_probe_total_hits: 0
six_gate_preflight_slots: 6
six_gate_body_pass_claims: 0
novel_generated: false
```

结论：本次预演保持来源隔离；只登记客户事实、内部路径审计摘要、来源边界、污染扫描和六门预检，不含小说正文。