# OPC 写作入口 Skill v0.4.0-test 静态复审报告

- 复审对象：`D:\Hermes\skills\creative\writing-opc-entry-test\SKILL.md`
- 对象版本：`0.4.0-test`
- 复审日期：2026-08-31
- 复审方式：只读静态审查；**未修改 Skill**，未生成小说，未执行新的一键首交回归。
- 对照：v0.3 静态复审报告、Skill 内 `FIXSET-WRITING-ENTRY-003` 固定夹具及已存在的回归产物目录。

## 一、结论

- **总判定：FAIL（静态结构）**
- **综合评分：2 / 4**
- 客户体验边界、内部隐藏 QC、流程顺序和逻辑底线的自然语言要求基本正确。
- 但新增的“剧情连续性/无剧情断点”成为第六个硬门禁后，没有进入 `hard_gate_results.gate` 枚举；同时既有 `FIX-GATES-001` 仍强制 `exactly_five_gate_results`。这使“全部逻辑硬门禁均有本次实际结果”的 completed 条件无法被现有 schema 与 fixture 一致地证明，是本轮结构硬伤。
- `first_delivery_usability` 有明确字段和值，但没有被纳入两分支共同必填输出，也没有对应结果对象、引用或断言闭环，只能指导行为，尚不能完整机器核验。

> **范围声明：本报告只是静态复审。它不代表新的“一键首交”回归已运行或已通过，也不代表真实长篇写作能力、首次交付可用性或最终验收通过。**

## 二、评分口径

| 分数 | 含义 |
|---:|---|
| 4 | 静态契约完整、可机器核验，且存在相应真实执行证据 |
| 3 | 静态结构完整且可执行，但尚无真实回归证据 |
| 2 | 核心意图已覆盖，但存在字段、枚举、基数或 fixture 冲突 |
| 1 | 只有原则描述，不能稳定执行或核验 |
| 0 | 缺失或与要求相反 |

## 三、指定检查项

| # | 检查项 | 静态证据与结论 | 评分 | 判定 |
|---:|---|---|---:|---|
| 1 | 区分“客户中途不参与”与“交付后可修改” | `human_confirmation` 禁止运行中反问、等待和确认；`first_delivery_usability.customer_midprocess_intervention: false` 与 `customer_post_delivery_editing: allowed` 分开表达；工作流和 Completion Check 再次说明交付后精修不属于节点内返工。边界清楚，没有把交付后自由修改误写为中途参与。 | 3 | PASS（静态） |
| 2 | 允许内部隐藏 QC、禁止外露漏洞稿 | 明确允许 `internal_hidden_draft_qc: allowed`；内部可修正未展示工作稿；`external_draft_count_before_pass: 0`；失败稿、问题单、候选正文、返工轮次不得外露。第一次出现的正文必须先过逻辑底线。 | 3 | PASS（静态） |
| 3 | `first_delivery_usability` 字段可执行性 | 字段值具体，能指导“一次提交、内部多轮、第一次只交一份合格小说”。但该对象不在 `output_contract.provenance_and_decisions.required_in_both_branches`，也不在 `provenance_and_decisions` schema 中；没有 `result/status/evidence_refs`，既有 fixture 也未逐项断言。因此不能从实际输出机器确认该契约已执行。 | 2 | FAIL（可核验闭环） |
| 4 | 写前推演→工作稿→门禁→首次交付顺序 | completed 路径的步骤 4—7 顺序一致：先选择路径并建表，再生成不外露工作稿，再定向修正和复检，最后首次对外交付。blocked 在步骤 3 可提前退出，步骤 8是结果说明，不要求伪造 completed 流程。 | 3 | PASS（静态） |
| 5 | 事实/时间线/动机/因果/剧情断点/伏笔责任底线 | 六项均有自然语言覆盖：故事事实含时间线；人物门禁含欲望、知识、机会、选择、代价、后果；因果门禁含转折、信息路径、巧合与伏笔责任；剧情连续性单列无来源跳变和无需客户补写。`first_external_novel_must_pass` 也列出六类。问题是结构化门禁枚举仍只有五类，无法记录新增的剧情连续性门禁。 | 2 | FAIL（结构记录） |
| 6 | 精彩程度只作软诊断 | `aesthetic_optimality_required: false`；工作流将精彩程度、意象密度、语言惊艳度明确归入软诊断；Soft Diagnostics 不得把个人审美强制成模板。逻辑合格但审美非最优仍可交付，符合边界。 | 3 | PASS（静态） |
| 7 | 与 completed/blocked 输出契约一致性 | 分支仍互斥穷尽：completed 仅 `[novel, provenance_and_decisions]`，blocked 仅 `[blockage, provenance_and_decisions]`；交付数、正文基数、handoff 空值规则无直接冲突。可是 completed 要求“全部逻辑硬门禁均有本次实际结果”，而结果枚举不能表示 `plot_continuity/no_plot_gap`，故 completed 的完成证明不闭合。 | 2 | FAIL（完成条件闭环） |
| 8 | 与既有回归 fixture 一致性 | `FIX-GATES-001` 的 `covers` 仍为 `five_hard_gates`，只注入 story_facts、character_agency、causality、pacing、sustainability，并断言 `exactly_five_gate_results`。当前 Quality Control 已列六个硬门禁，且首交合同包含 `no_plot_gap`。旧 fixture 与新契约发生实质冲突；不能用“剧情连续性已被因果隐含覆盖”消解，因为 Skill 已将其单列为独立 Hard Gate。 | 1 | FAIL（fixture 冲突） |

## 四、流程和责任底线复核

### 4.1 顺序一致性

静态顺序是：

1. 解析并锁定客户事实；
2. 自主处理缺项/冲突并判定分支；
3. completed 路径内部写前推演；
4. 只沿选定路径生成隐藏工作稿；
5. 逐项执行硬门禁，失败则内部定向修正并复检；
6. 全部逻辑门禁通过后，第一次对外仅交付一份小说和审计记录；
7. 无法在锁定事实下完成时走 blocked，绝不交漏洞稿；
8. 客户收到成品后可在节点外自由精修。

该叙事顺序没有倒置，也没有要求客户参与中间返工。

### 4.2 六类底线

| 底线 | 文本覆盖 | 结构化覆盖 |
|---|---|---|
| 事实 | `locked_customer_facts`、故事事实门禁 | `story_facts` 可记录 |
| 时间线 | `timeline_consistency`，事实表/时间线 | 归入 `story_facts`，可记录但粒度合并 |
| 动机与能动性 | `character_motive_and_agency` | `character_agency` 可记录 |
| 因果 | `causal_continuity` | `causality` 可记录 |
| 剧情断点 | `no_plot_gap`、独立“剧情连续性”硬门禁 | **无对应 gate 枚举，不能独立记录** |
| 伏笔责任 | `setup_payoff_responsibility`、因果门禁与 handoff | 可归入 `causality`，并由 `setups_and_payoffs` 记录 |

自然语言责任底线齐全；机器结果层缺“剧情连续性”类型，因此不能判结构 PASS。

## 五、结构硬伤

### 硬伤 1：六个 Hard Gates 与五值结果枚举冲突

Quality Control 列出：故事事实、人物、因果、节奏、可持续性、剧情连续性，共六项；但：

```yaml
gate: story_facts|character_agency|causality|pacing|sustainability
```

只有五值。新增的剧情连续性无法生成合法 `hard_gate_results` 项，却又被 Completion Check 要求包含在“全部逻辑硬门禁均有本次实际结果”中。

### 硬伤 2：既有 fixture 固定要求恰好五个门禁结果

`FIX-GATES-001` 仍注入五类故障并断言 `exactly_five_gate_results`。若新增第六个 `plot_continuity` 结果，旧断言失败；若只输出五个结果，则新契约的剧情断点责任没有实际结果。两者当前不可同时满足。

### 硬伤 3：`first_delivery_usability` 不是输出结果契约的一部分

它作为 Skill 内静态契约可指导执行，但没有：

- 被列入 `provenance_and_decisions.required_in_both_branches`；
- 出现在输出 schema 中；
- completed/blocked 分支差异规则；
- `status`、证据引用、失败处理；
- 对应 fixture 断言。

因此“客户未中途参与、内部 QC 隐藏、首个外部正文已过六类底线、交付后可修改”不能从一次输出被完整机器验证。

## 六、需要修正项

以下仅是复审建议；本次未修改 Skill：

1. **统一硬门禁基数和枚举。** 二选一并全局一致：
   - 推荐新增 `plot_continuity`（或命名一致的 `no_plot_gap`）到 `hard_gate_results.gate`，明确六个门禁结果；或
   - 若坚持五门禁，必须把剧情连续性正式定义为某一现有 gate 的必检子项，并取消“独立第六门禁”的结构表达。不能同时保留“六项列表”和“五结果断言”。
2. **同步固定 fixture。** 若采用六门禁：把 `FIX-GATES-001.covers`、fault injection、`exactly_five_gate_results` 和覆盖矩阵同步为六门禁，并增加剧情断点故障注入与断言。fixture 版本/set id 如按不可变语义管理，应升级而不是原地改写旧夹具身份。
3. **闭合 `first_delivery_usability`。** 将其作为输出中可核验结果对象，或增加 `first_delivery_usability_result`，至少包含契约版本、状态、六门禁引用、外部草稿计数、首次小说计数及证据引用；并规定 blocked 时的适用/不适用值。
4. **增加首交专项 fixture。** 固定断言客户无中途交互、内部工作稿不外露、首个外部正文只有一份且引用全部硬门禁 pass、失败稿不能成为外部输出、交付后编辑仅是边界声明而非节点返工。
5. **回归前不要声称通过。** 修正静态结构后，仍需实际执行新的“一键首交”fixture，保存输出、逐断言结果、artifact refs 和独立 verifier 证据。

## 七、PASS / FAIL 汇总

- 客户中途不参与 vs. 交付后可修改：**PASS（静态）**
- 内部隐藏 QC vs. 禁止外露漏洞稿：**PASS（静态）**
- `first_delivery_usability` 可执行且可核验：**FAIL**
- 写前推演、工作稿、门禁、首交顺序：**PASS（静态）**
- 六类责任底线的自然语言覆盖：**PASS（静态）**
- 六类责任底线的结构化结果覆盖：**FAIL**
- 精彩程度仅作软诊断：**PASS（静态）**
- completed/blocked 顶层互斥与基数：**PASS（静态）**
- completed 完成条件与门禁结果闭环：**FAIL**
- 与既有 `FIX-GATES-001` 一致：**FAIL**

**最终：2 / 4，FAIL（静态结构）。**

## 八、静态复审边界

本报告未运行模型生成小说，未执行 fault injection，未验证隐藏工作稿是否真的不外露，也未验证第一次对外交付是否在真实运行中满足事实、时间线、动机、因果、剧情断点和伏笔责任底线。即使上述结构修正完成，也只能重新获得静态复审资格；**不能据此宣称新的一键首交回归已通过。**

## 九、落盘核验

- 报告路径：`D:\Hermes\xiaonan-memory\references\opc-writing-skill-verification-v0.4.md`
- 文件存在：`true`
- 最终字节数：`10768` 字节
- 最终行数：`136` 行
