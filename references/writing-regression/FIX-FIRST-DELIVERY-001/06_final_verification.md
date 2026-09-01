# FIX-FIRST-DELIVERY-001 · 最终独立验收

> 核验依据：`writing-opc-entry-test` v0.5.1-test  
> 只读输入：`01_prewrite_simulation.md`、`02_prewrite_verification.md`、`03_hidden_working_draft.md`、`04_hidden_draft_qc.md`、`05_first_external_artifact.md`  
> 判定规则：任一哈希、计数或门禁不符，整体即 `FAIL`。

## 1. 总判定

```yaml
case_id: FIX-FIRST-DELIVERY-001
verification_stage: final_independent_acceptance
verdict: FAIL
pass_threshold_each: 3
blocking_checks:
  - HASH-DECLARED-SOURCE-BODY
  - COUNT-EXTERNAL-CANDIDATE
report_file_size_bytes: 07043
report_line_count: 132
```

**最终结论：FAIL。** 隐藏稿实际正文六门均通过，且 03/05 的 BODY 区实际逐字一致；但 `05` 登记的 `source_body_sha256` 与实算 BODY SHA-256 不符，同时 `external_candidate_count` 登记为 `1` 而验收要求候选为 `0`。按硬规则，任一哈希或计数不符即不得判定总 PASS。

## 2. 流程时序与门禁核验

| 核验项 | 实测证据 | 评分（0—4） | 结论 |
|---|---|---:|---|
| 写前首次 FAIL 被保留 | `02` 第 1—8 节保留 `verdict: FAIL`、`allow_hidden_working_draft: false`；第 9 节明确历史不追溯改写 | 4/4 | PASS |
| 首次 FAIL 时正文为 0 | `02` 首次记录 `novel_body_count: 0`、`first_external_novel_count: 0`，并明令不得生成正文 | 4/4 | PASS |
| 修复后预检六门全过才允许 hidden | `02` 第二次评分 `[3,4,3,3,3,3]`，`pass_count: 6`、`fail_count: 0`、`allow_hidden_working_draft: true`；该阶段仍为 `novel_body_count: 0` | 4/4 | PASS |
| hidden 在预检放行后生成 | `03` 为 `INTERNAL_NOT_EXTERNAL` 隐藏稿；前序 `02` 已给出 `PASS_FOR_HIDDEN_DRAFT_ONLY` | 4/4 | PASS |
| hidden QC 六门全过 | `04` 实际正文评分严格为 `[4,4,4,4,3,4]`，六项均 `PASS_FIRST_CHECK`，`pass_count: 6`、`fail_count: 0` | 4/4 | PASS |
| 首次客户可见正文为已 QC 版本 | `04` 先放行登记，`05` 后登记首次外部成品；03/05 BODY 区逐字相同 | 4/4 | PASS |

## 3. BODY 区逐字 SHA 与登记后正文

BODY 区统一取值边界：从 `<a id="BODY-001"></a>` 起，至各文件下一元数据二级标题前止；按文件原始 UTF-8/LF 字节逐字比较。

```yaml
body_region_comparison:
  hidden_file: 03_hidden_working_draft.md
  external_file: 05_first_external_artifact.md
  hidden_body_sha256_exact_region: 68924fd3b9f9f193bf19c945030f2612f352c62c7c77955f029991ad3adef2c7
  external_body_sha256_exact_region: 68924fd3b9f9f193bf19c945030f2612f352c62c7c77955f029991ad3adef2c7
  hidden_body_sha256_trailing_newlines_removed: c3175e5d655c4dba920315231c9171a3391931b72e690a3d2c506b938cc6bc89
  external_body_sha256_trailing_newlines_removed: c3175e5d655c4dba920315231c9171a3391931b72e690a3d2c506b938cc6bc89
  byte_for_byte_equal: true
  body_line_count_without_trailing_blank_lines: 149
  body_char_count_without_trailing_blank_lines: 2628
```

| 核验项 | 实测 | 评分（0—4） | 结论 |
|---|---|---:|---|
| 05 外部正文与 03 隐藏正文逐字一致 | 两文件 exact-region SHA 同为 `68924f...f2c7`；去尾换行 SHA 同为 `c3175e...bc89` | 4/4 | PASS |
| 登记后正文未改 | `05` 声明 `body_changed_after_qc: false`，实际外部 BODY 与已 QC 的 03 BODY 逐字一致 | 4/4 | PASS |
| 登记的来源正文 SHA 正确 | `05` 声明 `source_body_sha256: 228b7870...fc0d`，既不等于 exact-region SHA，也不等于去尾换行 SHA | 0/4 | **FAIL** |

> 硬失败 `HASH-DECLARED-SOURCE-BODY`：登记哈希为 `228b78707febf1240401ee8f6b9293e9fac73ed8fa369d37f7e330da6d9cfc0d`，实算 BODY SHA-256 为 `68924fd3b9f9f193bf19c945030f2612f352c62c7c77955f029991ad3adef2c7`（若去除末尾换行则为 `c3175e5d655c4dba920315231c9171a3391931b72e690a3d2c506b938cc6bc89`）。登记值与两种明确边界均不符。

## 4. 首次交付计数与字段核验

| 核验项 | 要求 | `05` 实测 | 评分（0—4） | 结论 |
|---|---:|---:|---:|---|
| 客户提交 | 1 | `customer_submission_count: 1` | 4/4 | PASS |
| 客户中途介入 | 0 | `customer_midprocess_intervention_count: 0` | 4/4 | PASS |
| 内部稿外露 | 0 | `exposed_internal_draft_count_before_pass: 0`；结果对象为 `exposed_internal_draft_count: 0` | 4/4 | PASS |
| 首次外部小说 | 1 | `first_external_novel_count: 1` | 4/4 | PASS |
| 外部候选正文 | 0 | 写前 `external_candidate_bodies: 0`，但登记记录为 `external_candidate_count: 1` | 0/4 | **FAIL** |
| 备选小说 | 0 | `alternate_novel_count: 0` | 4/4 | PASS |
| 交付后编辑 | allowed | `customer_post_delivery_editing_allowed: true` | 4/4 | PASS |

> 硬失败 `COUNT-EXTERNAL-CANDIDATE`：`05` 的 `external_candidate_count: 1` 与“候选 0”不符。即便该值原意可能是成品计数，字段名及登记值仍构成机器可核验的候选计数冲突；不得擅自改义后放行。

## 5. `first_delivery_usability_result` 核验

`05` 已包含规定字段，逐项值如下：

```yaml
contract_version: opc-writing-first-delivery/0.5-test
status: pass
customer_submission_count: 1
customer_midprocess_intervention_count: 0
exposed_internal_draft_count: 0
first_external_novel_count: 1
hard_gate_result_refs: [GATE-001, GATE-002, GATE-003, GATE-004, GATE-005, GATE-006]
all_six_logic_gates_pass: true
first_external_artifact_ref: ART-FIRST-DELIVERY-001
customer_post_delivery_editing_allowed: true
evidence_refs: [SRC-USER-001, GATE-001, GATE-002, GATE-003, GATE-004, GATE-005, GATE-006, ART-FIRST-DELIVERY-001]
```

- 字段完整性：4/4，PASS。
- 各字段值与 completed 分支契约：4/4，PASS。
- 与隐藏 QC 六门结果引用一致：4/4，PASS。
- 但该对象的 `status: pass` 不能覆盖同一成品登记中的错误来源哈希和候选计数；最终验收仍为 FAIL。

## 6. ART 唯一性与外部可见性

```yaml
art_audit:
  unique_art_refs: [ART-FIRST-DELIVERY-001]
  artifact_ref_declaration_count: 1
  unique_art_count: 1
  first_external_artifact_ref_matches: true
  customer_first_visible_body_is_post_qc_body: true
```

| 核验项 | 评分（0—4） | 结论 |
|---|---:|---|
| ART 标识唯一且结果对象引用一致 | 4/4 | PASS |
| 客户第一次可见正文是已通过 hidden QC 的版本 | 4/4 | PASS |
| 候选正文为 0 | 0/4 | **FAIL**（登记记录显式写为 1） |
| 客户交付后编辑允许 | 4/4 | PASS |

## 7. 六门最终评分与汇总

```yaml
hidden_qc_scores:
  GATE-001_story_facts: 4
  GATE-002_character_agency: 4
  GATE-003_causality: 4
  GATE-004_pacing: 4
  GATE-005_sustainability: 3
  GATE-006_plot_continuity: 4
hidden_qc_vector: [4, 4, 4, 4, 3, 4]
hidden_qc_verdict: PASS
final_integrity_checks:
  declared_source_body_hash: 0
  external_candidate_count: 0
final_verdict: FAIL
```

**总判定：FAIL。** 门禁本身通过，但最终完整性验收被两项硬错误阻断：来源 BODY 登记 SHA 不符、候选计数不为 0。依据本次规则，不得以多数通过、正文实际相同或结果对象自报 `pass` 抵消任一哈希／计数失败。

---

## 8. 元数据修复后追加复核（保留首次 FAIL 历史）

> 本节只追加复核结果，不删除、不覆盖第 1—7 节首次 `FAIL` 历史。复核输入仍为 `03_hidden_working_draft.md`、`04_hidden_draft_qc.md`、`05_first_external_artifact.md`；正文不得修改。判定规则仍为：BODY 逐字不一致或任一计数错误，整体继续 `FAIL`。

### 8.1 BODY 区重新实算与声明哈希

BODY 边界沿用首次复核口径：从 `<a id="BODY-001"></a>` 起，包含正文后空行，至下一元数据二级标题 `## ` 前止；直接按原始 UTF-8/LF 字节计算。

```yaml
repair_reverification_body:
  hidden_file: 03_hidden_working_draft.md
  external_file: 05_first_external_artifact.md
  hidden_body_region_bytes: 7254
  external_body_region_bytes: 7254
  hidden_body_sha256: 68924fd3b9f9f193bf19c945030f2612f352c62c7c77955f029991ad3adef2c7
  external_body_sha256: 68924fd3b9f9f193bf19c945030f2612f352c62c7c77955f029991ad3adef2c7
  byte_for_byte_equal: true
  declared_source_body_sha256: 68924fd3b9f9f193bf19c945030f2612f352c62c7c77955f029991ad3adef2c7
  declared_hash_matches_recomputed_body: true
  body_changed: false
```

结论：03 与 05 BODY 区逐字一致；`05` 的 `source_body_sha256` 已与 verifier 重算值完全一致。首次 FAIL 中的 `HASH-DECLARED-SOURCE-BODY` 阻断项已闭合。

### 8.2 唯一交付、计数与结果对象

| 核验项 | 要求 | 修复后实测 | 结论 |
|---|---:|---:|---|
| 客户提交 | 1 | `customer_submission_count: 1` | PASS |
| 客户中途介入 | 0 | `customer_midprocess_intervention_count: 0` | PASS |
| 内部稿外露 | 0 | `exposed_internal_draft_count_before_pass: 0`；结果对象 `exposed_internal_draft_count: 0` | PASS |
| 首个外部小说 | 1 | `first_external_novel_count: 1` | PASS |
| 外部候选正文 | 0 | `external_candidate_count: 0` | PASS |
| 正式外部成品 | 1 | `formal_external_artifact_count: 1` | PASS |
| 备选小说 | 0 | `alternate_novel_count: 0` | PASS |
| 交付后编辑 | allowed | `customer_post_delivery_editing_allowed: true` | PASS |

```yaml
repair_reverification_art_and_result:
  artifact_ref_declarations: [ART-FIRST-DELIVERY-001]
  artifact_ref_declaration_count: 1
  unique_art_count: 1
  art_unique: true
  first_delivery_usability_result:
    present: true
    contract_version: opc-writing-first-delivery/0.5-test
    status: pass
    customer_submission_count: 1
    customer_midprocess_intervention_count: 0
    exposed_internal_draft_count: 0
    first_external_novel_count: 1
    hard_gate_result_refs: [GATE-001, GATE-002, GATE-003, GATE-004, GATE-005, GATE-006]
    all_six_logic_gates_pass: true
    first_external_artifact_ref: ART-FIRST-DELIVERY-001
    customer_post_delivery_editing_allowed: true
```

结论：首次 FAIL 中的 `COUNT-EXTERNAL-CANDIDATE` 阻断项已由 `external_candidate_count: 0` 闭合；候选 0、正式外部成品 1、alternate 0，且唯一 ART 与结果对象引用一致。

### 8.3 六门与修复后总判定

```yaml
repair_reverification_gates:
  GATE-001_story_facts: 4
  GATE-002_character_agency: 4
  GATE-003_causality: 4
  GATE-004_pacing: 4
  GATE-005_sustainability: 3
  GATE-006_plot_continuity: 4
  pass_threshold_each: 3
  pass_count: 6
  fail_count: 0
  all_six_logic_gates_pass: true
repair_reverification_blocking_checks: []
repair_reverification_verdict: PASS
```

**修复后最终结论：PASS。** 首次 `FAIL` 历史完整保留；修复后 03/05 BODY 区逐字一致、05 声明哈希正确、候选 0、正式外部成品 1、alternate 0、ART 唯一、`first_delivery_usability_result` 完整一致、六门全 PASS，并满足“提交 1／中途 0／外露 0／首个外部 1／交付后可编辑”。两项原阻断均已闭合。
