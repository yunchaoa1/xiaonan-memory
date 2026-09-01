# FIX-DIVERSITY-001 独立对照验收

```yaml
verification:
  verification_id: FIX-DIVERSITY-001
  skill_version: 0.5.1-test
  scope: preflight_diversity_comparison_only
  inputs:
    - FIX-DIVERSITY-A-001/preflight.md
    - FIX-DIVERSITY-B-001/preflight.md
  novel_generated_by_verifier: false
  input_modified_by_verifier: false

score_rubric:
  4: 六个创作维度均实质分化，且无跨样本运行时污染，计数与preflight声明完整可信。
  3: 创作分化充分，但存在不改变所选剧情的轻度跨样本审计或提示污染。
  2: 有明显差异，但共享主要结构/发动机/回报模板，或隔离证据不足。
  1: 大部分仅换皮，或有显著跨样本内容移植。
  0: 无法证明多样性，或两案实质相同。

result:
  score_0_to_4: 3
  verdict: FAIL
  strict_fail_reasons:
    - B的运行材料显式读取并写入了A的专属内容作为排除项，与其“customer_idea_only”“diversity_A_content_used_as_template: false”“不读取A”的来源隔离声明不相容。
  diversity_only_assessment: PASS
  protocol_and_source_isolation_assessment: FAIL
  note: 两案创作方案本身高度分化，未发现A剧情机制被正向移植到B；但本验收要求来源隔离，故不能以创作差异抵消跨样本污染。

case_accounting:
  A:
    selected_path_count: 1
    selected_path_check: PASS
    novel_body_count: 0
    external_exposure_count: 0
    midprocess_intervention_count: 0
    source_isolation_check: PASS
  B:
    selected_path_count: 1
    selected_path_check: PASS
    novel_body_count: 0
    external_exposure_count: 0
    midprocess_intervention_count: 0
    source_isolation_check: FAIL
  combined_contract:
    selected_each_equals_one: PASS
    body_each_equals_zero: PASS
    external_exposure_each_equals_zero: PASS
    midprocess_intervention_each_equals_zero: PASS
    source_isolation: FAIL
```

## 六维实质差异核验

| 维度 | A：暖喜剧慢燃、关系修复 | B：推想黑色、锋利快节奏、制度追查 | 实质不同 | 判定 |
|---|---|---|---|---|
| 题材 | 退休厨师、失传家常菜、日常温暖喜剧 | 无影极昼城、不存在的公共支出、推想黑色调查 | 类型承诺、世界尺度和冲突烈度均不同 | PASS |
| 人物发动机 | 双主角共同劳动；对抗记忆偏差、旧日自尊和未说开的伤害；目标是恢复平等友谊 | 单主角审计追责；对抗删证、记录系统与受益执行者；目标是建立可追责因果链 | A由关系需求和互相选择发动，B由职业职责、证据与制度风险发动 | PASS |
| 结构 | 线性双主角五单元，从疏远到有限合作、争执、看见付出、主动选择彼此、重启友谊 | 线性倒计时调查六单元，从异常、删证、转查实物流、制度反击到公开证据和承担代价 | 虽同为线性递进，但单元功能、推进变量和终点不同，不构成同一剧情模板 | PASS |
| 声音 | 克制温暖、生活观察、动作承载情感、轻而持续的喜剧 | 短句动词优先、权力与信息攻防、冷硬制度讽刺 | 语气、句法目标、幽默机制与叙述关注点相反 | PASS |
| 节奏 | slow_burn；保留买菜、备料、等火、尝味等呼吸，关系分级变化 | fast；开场即异常，线索迅速产生行动后果，禁止连续说明与慢燃等待 | 场景密度、信息兑现速度和停顿策略明确相反 | PASS |
| 回报类型 | 关系和解、共同创造、新版本菜品与重新分享 | 程序追责、世界规则揭示、主动性兑现及职业/身份/生存代价落地 | A回报亲密关系，B回报责任链、机制暴露和代价 | PASS |

### 共用剧情模板检查

**判定：PASS。** 两案只有“线性递进”“每单元产生状态变化”“主角主动选择并承担后果”这类通用质量约束相同。A的关键链条是“共同试做 → 旧伤显影 → 选择彼此 → 关系重启”；B的关键链条是“核验异常 → 删证 → 转查实物流 → 制度反击 → 公开证据/承担代价”。未发现把同一人物关系、核心冲突、转折功能或结局回报换名复用。

## 互相污染与来源隔离

### A

**判定：PASS。** A仅登记 `SRC-USER-001_only`，并声明未读取历史、网络、其他项目或历史样本。其方案内未出现B的极昼城、无影、审计、公共支出、制度追查、删证或身份注销机制。

### B

**判定：FAIL。** B的创作实体没有正向采用A模板，但运行材料已显式写入A专属信息：

- `explicit_exclusions` 明列“A的退休厨师关系模板”；
- 明列“A的失传家常菜、重归于好等剧情模板”；
- `relationship_policy` 再次以“A的旧友复合与温情和解发动机”为排除对象；
- `payoff_types.forbidden` 再次引用“A的友情修复或家常菜复原”。

这些内容不属于B固定夹具的客户输入，却进入了B的写前运行材料。因此，即使它们只被当作负向排除项，也证明B接触并使用了另一case的专属创意信息；这与同文件的 `runtime_external_creative_source: customer_idea_only`、`diversity_A_content_used_as_template: false` 以及“仅作为明确排除项，不读取”的说法发生内部矛盾。严格来源隔离不能通过。

**修复要求：** 重做B preflight时，删除所有对A、退休厨师、家常菜、旧友复合和温情和解的跨case引用；仅从B本次 `SRC-USER-001` 推导正向类型、人物、结构、声音、节奏和回报约束。独立产出完成后，才可由本对照验收层读取A、B并比较。

## selected / 正文 / 外露 / 中途

| case | selected | 正文 | 外露 | 中途 | 判定 |
|---|---:|---:|---:|---:|---|
| A | 1 | 0 | 0 | 0 | PASS |
| B | 1 | 0 | 0 | 0 | PASS |

A的 `divergence_record.selected_path_count: 1`，B同样为1；两者均声明 `external_candidate_bodies: 0`。A的暴露计数为正文0/外露0/中途0；B的 `novel_body_count`、`external_body_count`、`exposed_internal_draft_count`、`customer_midprocess_intervention_count` 均为0。未发现候选正文、小说正文或中途客户干预。

## 六门状态核验

| 门禁 | A | B | 验收结论 |
|---|---|---|---|
| story_facts | `ready_not_run` | `preflight_ready` | 仅准备，未执行 |
| character_agency | `ready_not_run` | `preflight_ready` | 仅准备，未执行 |
| causality | `ready_not_run` | `preflight_ready` | 仅准备，未执行 |
| pacing | `ready_not_run` | `preflight_ready` | 仅准备，未执行 |
| sustainability | `ready_not_run` | `preflight_ready` | 仅准备，未执行 |
| plot_continuity | `ready_not_run` | `preflight_ready` | 仅准备，未执行 |

**判定：PASS（仅指状态诚实性）。** A明确写明 `overall_status: ready_for_internal_draft_not_executed` 且“无正文，门禁不得虚称已通过”；B也明确声明写前预检只确认路径具备过门条件，不宣称正文门禁实际通过。两者没有把六门写成 `pass_first_check` 或 `pass_after_revision`，因此未发现虚假正文PASS。

但上述PASS不代表六门本身已通过。由于正文数为0，六门当前统一只能记为：

```yaml
six_gate_execution_verdict:
  phase: preflight_only
  body_evidence_available: false
  executed_gate_count: 0
  passed_gate_count: 0
  failed_gate_count: 0
  status: NOT_RUN
  completed_novel_gate_pass_claim_allowed: false
```

## 最终结论

- **0–4评分：3/4**
- **最终判定：FAIL**
- **多样性实质差异：PASS**（六维全部明显分化，无共用剧情模板）
- **计数契约：PASS**（两者均 selected 1、正文0、外露0、中途0）
- **六门声明诚实性：PASS**（只做preflight准备，正文门禁为NOT_RUN，无虚假PASS）
- **来源隔离：FAIL**（B以负向约束形式使用了A的专属内容；必须清除后独立重跑B并重新验收）

---

## 修复后最终复核（追加记录）

> 本节为修复后的追加验收；上方首次 `FAIL` 记录原样保留，不作覆盖或改写。

```yaml
final_reverification:
  verification_id: FIX-DIVERSITY-001
  scope: post_fix_source_isolation_and_regression_check
  inputs:
    - FIX-DIVERSITY-A-001/preflight.md
    - FIX-DIVERSITY-B-001/preflight.md
  input_modified_by_verifier: false

  B_source_isolation:
    A_exclusive_fact_role_prop_relationship_goal_hits: 0
    other_fixture_content_read: false
    other_fixture_content_used_as_template: false
    contamination_count: 0
    verdict: PASS

  diversity_six_dimensions:
    genre: PASS
    character_engine: PASS
    structure: PASS
    voice: PASS
    pacing: PASS
    payoff_type: PASS
    shared_plot_template_detected: false
    verdict: PASS

  contract_regression:
    A_selected_path_count: 1
    B_selected_path_count: 1
    selected_each_equals_one: PASS
    A_novel_body_count: 0
    B_novel_body_count: 0
    body_each_equals_zero: PASS
    A_external_exposure_count: 0
    B_external_exposure_count: 0
    external_exposure_each_equals_zero: PASS
    A_midprocess_intervention_count: 0
    B_midprocess_intervention_count: 0
    midprocess_intervention_each_equals_zero: PASS

  gate_honesty_regression:
    false_completed_body_gate_pass_claims: 0
    A_gate_state: ready_not_run
    B_gate_state: preflight_ready
    executed_gate_count: 0
    passed_gate_count: 0
    status: NOT_RUN
    verdict: PASS

  final_score_0_to_4: 4
  final_verdict: PASS
```

### B污染重扫

**判定：PASS。污染计数为0。** 对B全文重新扫描后，未再出现A专属事实、角色、道具或关系目标，包括两位退休厨师、失传家常菜、旧友重新成为朋友、友情/关系修复等内容，也未出现对A case的显式指称。B现有排除语句仅使用“本次客户输入之外”“其他测试样本”等抽象来源边界，不携带另一fixture的专属创意信息。

B的来源隔离字段明确为：

- `other_fixture_content_read: false`
- `other_fixture_content_used_as_template: false`（对应本次核对所称 `used=false`）

二者与B正文内容一致，未发现声明与运行材料互相矛盾。

### 六维与计数回归

| 核验项 | A | B | 结论 |
|---|---|---|---|
| 题材 | 暖喜剧、日常关系修复 | 推想黑色、制度追查 | PASS |
| 人物发动机 | 双主角共同劳动与友情重启 | 单主角审计、证据与追责 | PASS |
| 结构 | 线性双主角五单元慢燃 | 线性倒计时调查六单元 | PASS |
| 声音 | 克制温暖、生活观察 | 锋利短句、制度讽刺 | PASS |
| 节奏 | slow_burn | fast | PASS |
| 回报类型 | 关系和解与共同创造 | 程序追责、规则揭示、主动性与代价 | PASS |
| selected | 1 | 1 | PASS |
| 正文 | 0 | 0 | PASS |
| 外露 | 0 | 0 | PASS |
| 中途 | 0 | 0 | PASS |

六维差异均保持实质分化，没有回退为共用剧情模板。A/B仍各仅选择1条路径，正文0、外露0、中途0。

### 无虚假门禁PASS回归

**判定：PASS。** A六门仍为 `ready_not_run`，B六门仍为 `preflight_ready`；两者均明确处于preflight阶段，正文证据为0，没有出现 `pass_first_check`、`pass_after_revision` 或其他已完成正文门禁PASS声明。原“状态诚实性PASS、六门实际NOT_RUN”的结论未回退。

### 修复后最终结论

- **污染：0**
- **来源隔离：PASS**
- **六维实质差异：PASS**
- **计数契约：PASS**（A/B各selected 1、正文0、外露0、中途0）
- **无虚假门禁PASS：PASS，未回退**
- **修复后最终评分：4/4**
- **修复后最终判定：PASS**
