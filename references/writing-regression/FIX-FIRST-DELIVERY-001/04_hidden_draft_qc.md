# FIX-FIRST-DELIVERY-001 · 隐藏工作稿独立交付前 QC

> 核验对象：`03_hidden_working_draft.md`  
> 核验依据：`writing-opc-entry-test` v0.5.1-test  
> 唯一客户输入（`SRC-USER-001`）：`一名钟表修理师发现全城只有一只钟还在记录真实时间。`  
> 核验边界：仅复核实际隐藏正文；不修改稿件、不外露正文、不登记 `ART-*`、不生成外部成品。

## 1. 最终判定

```yaml
case_id: FIX-FIRST-DELIVERY-001
verification_stage: independent_postdraft_hidden_qc
verdict: PASS_FOR_FIRST_EXTERNAL_ARTIFACT_REGISTRATION
pass_threshold_each: 3
all_six_logic_gates_pass: true
pass_count: 6
fail_count: 0
blocking_gate_refs: []
internal_revision_items: []
artifact_registration_performed: false
external_artifact_ref: NONE
customer_submission_count: 1
customer_midprocess_intervention_count: 0
exposed_internal_draft_count: 0
first_external_novel_count: 0
```

**结论：六门实际正文评分均达到 `>=3`，本隐藏稿通过首次外部成品登记前的逻辑底线检查。状态仅为 `PASS_FOR_FIRST_EXTERNAL_ARTIFACT_REGISTRATION`；本报告没有登记 `ART-*`，也没有把隐藏稿改写为外部小说成品。**

## 2. 重点约束逐项复核

### 2.1 客户事实与“全城唯一真钟”

| 检查项 | 实际正文证据 | 结论 |
|---|---|---|
| 主角身份 | `BODY-001` 中沈砚经营修理铺、上弦并检查多种钟表；后续以维修日志、机芯和撞停痕迹完成专业判断 | 保留“钟表修理师”，未偷换主体 |
| 全城范围 | `BODY-001` 写手机、药店钟、公交站牌、银行、收银机、电子表及铺内仍运行计时器统一快七分钟，并以十二处公开计时器取样；叙事明确落定“全城只有这一只” | “全城”仍是城市范围，公共取样只是可见佐证，并未把客户事实缩成“只有公共联网钟异常” |
| 唯一持续真钟 | `BODY-001` 的母钟按旧速率连续摆动，其他仍运行计时器均快七分钟；`BODY-002/003/006/008` 的事故手表始终停在十点十六分 | 停表只保存事故瞬间，不再持续记录流逝时间，不构成第二只真钟；唯一真钟未被偷换成“唯一有证据资格的钟” |
| “发现”行为 | `BODY-001—003` 由七分钟差异、维修日志、停表与公开时钟录像逐步形成判断 | 客户事实完整落入正文 |

判定：**PASS。** 唯一真钟从开端、互证、封存到结尾留下的墙面印记始终是同一只修理铺母钟；事故停表、临时闹钟及其他快七分钟的运行计时器均未取代它的世界事实地位。

### 2.2 掩盖目的仍是假设

- `BODY-003`：沈砚明确说现有差异只能支持“应该重新查”。
- `BODY-005`：带数字签名的邮件和回执只能证明事故后发生全城统一校时，不能证明命令是为掩盖事故。
- `BODY-007`：复核通知不写“掩盖”、不写谁有罪；统一校时目的仍需调查。

判定：**PASS。** 正文没有把“人为掩盖责任”升级为已证事实；人物怀疑、证据能力和制度结论三层保持分离。

### 2.3 三证与辅助取样边界

| 类型 | 正文中的固定身份 | 可支持的结论 | 明确边界 |
|---|---|---|---|
| 核心证据 1 | 母钟与封存维修日志 | 母钟离线、走时连续，提供独立时间基准 | 不能单独证明全城异常、命令主体或目的 |
| 核心证据 2 | 事故停表的公证检验记录 | 撞停状态与十点十六分相符，和母钟形成独立交叉点 | 不能单独证明统一校时或责任主体 |
| 核心证据 3 | 带数字签名的校时任务邮件与执行回执 | 证明事故后存在统一校时命令、时刻、范围及执行链 | 邮件与回执是同一证据包；不能单独证明掩盖目的 |
| 辅助佐证 | 十二处公开时钟录像 | 佐证城市范围内存在一致七分钟偏差 | 不计入三项核心证据，不证明异常来源 |

`BODY-007` 对三项核心材料逐项列名，并把十二处录像明确置于“辅助佐证”。判定：**PASS。** 三证基数、身份、证明能力和辅助取样角色无混用，也没有一证定责。

### 2.4 林秋、沈禾的转变触发与代价

- **林秋**：`BODY-002` 因保护遗物拒绝拆检；`BODY-004` 在“原表不离手、全程录像、公证员在场、只检不修、保持十点十六分”的保护条件形成后主动同意；`BODY-006` 亲手启封并签署提交，代价是让哥哥最后七分钟进入公共记录。触发、选择、代价连续。
- **沈禾**：`BODY-005` 最初以权限边界拒绝提供材料；公司随后要求删除旧回执并准备把异常归为她个人录入错误，形成新增压力；她为拒绝独自背责而保留并提交自己合法持有的签名邮件与回执；`BODY-006/008` 兑现停职、失业及家庭裂痕。触发、自主目的、代价连续。
- **沈砚**：由职业判断推动核验和提交，只使用自有日志、公开录像及经持有人授权的材料；`BODY-006/008` 兑现母钟封存、失去时间基准和营业风险。他不是靠外援自动获胜，三名证据持有人分别签名并承担后果。

判定：**PASS。** 两个重点人物均非突然转念，关键转变由可观察的新条件或新威胁触发，并有实际代价落地。

### 2.5 合法取证与复核程序

1. `BODY-001/004`：沈砚只拍公开场所计时器，使用自己合法持有的维修日志，明确没有进入后台或复制他人数据。
2. `BODY-004/006`：事故手表由林秋持有并授权；原件不离持有人，公证员记录封条、全程见证，只检查撞停和机芯状态，不修表；原件由林秋带走。
3. `BODY-005/006`：校时邮件与回执由合法持有人沈禾自愿提交，并核验数字签名。
4. `BODY-004`：事故复核窗口先说明两类独立材料、第三方见证和公证检验门槛。
5. `BODY-006/007`：三人分别签署证据提交声明；窗口逐项登记、出具收件编号，并因原事故时刻与新独立计时证据存在重大矛盾而重新受理。
6. `BODY-007`：程序效果仅为重新受理，不是直接定罪；主观目的留待后续调查。

判定：**PASS。** 信息持有、授权、公证、签名核验、提交对象、收件回执和重新受理门槛均有正文动作承接，未用专业能力替代权限或程序。

### 2.6 八个 BODY 锚点连续性

| 锚点 | 状态变化 | 与下一锚点的承接 |
|---|---|---|
| `BODY-001` | 发现母钟与全城运行计时器相差七分钟 | 林秋携事故停表进入，提供独立事故时间痕迹 |
| `BODY-002` | 得知官方事故时刻；林秋拒绝拆表 | 母钟日志与未拆停表先进行非破坏性比对 |
| `BODY-003` | 两只机械计时器指向十点十六分；明确只能要求重查 | 沈砚整理合法材料并询问正式复核门槛 |
| `BODY-004` | 获知证据程序；林秋在保护条件下同意公证检验 | 公共录像日期触发沈禾识别事故后校时任务 |
| `BODY-005` | 公司删回执、甩责压力触发沈禾提交签名证据包 | 三项材料分别完成公证、核验、封存和签署 |
| `BODY-006` | 三人各自承担提交代价 | 完整证据包进入事故复核窗口 |
| `BODY-007` | 收件、重新受理、公共时间恢复，定责仍开放 | 进入各人物代价与关系余波 |
| `BODY-008` | 母钟仍封存、沈禾失业、林秋保留停表、调查未结 | 短篇在事实已保存而责任未越权裁定处闭环 |

判定：**PASS。** 八个锚点均实际存在且顺序为 `BODY-001` 至 `BODY-008`，相邻单元在人物、地点、道具、知识、目标或程序上有明确承接，无须客户补写桥段。

### 2.7 首次交付内部状态

| 指标 | 要求 | 实际值 | 证据与结论 |
|---|---:|---:|---|
| 客户提交 | 1 | 1 | 稿首 YAML、稿末 `internal_provenance_summary` 一致 |
| 客户中途参与 | 0 | 0 | 两处状态记录一致；无中途询问或等待 |
| 外露内部稿 | 0 | 0 | `artifact_status: INTERNAL_NOT_EXTERNAL`，正文明确仅供内部 QC |
| 外部小说 | 0 | 0 | `first_external_novel_count: 0`，`external_artifact_ref: NONE` |

判定：**PASS。** 当前确为“提交 1／中途 0／外露 0／外部小说 0”。本 QC 的放行令不追溯改变上述计数；只有后续另行生成并登记合约完整的首次外部成品后，外部小说数才可变为 1。

## 3. 六门 0—4 实际正文评分

评分口径：`4` 表示实际正文完整且边界清楚；`3` 表示达到首次外部成品登记前的最低逻辑标准，仅保留不阻断交付的软性优化空间；任一门 `<3` 即整体 `FAIL` 并产生内部修订项，禁止登记 `ART-*`。

| gate_result_id | gate | 分数 | 状态 | 实际正文依据 |
|---|---|---:|---|---|
| `GATE-001` | `story_facts` | 4/4 | PASS_FIRST_CHECK | `BODY-001—008` 保持修理师、全城、唯一持续真钟和发现行为；停表不是第二只运行真钟；掩盖目的始终未获证；三证身份前后一致 |
| `GATE-002` | `character_agency` | 4/4 | PASS_FIRST_CHECK | `BODY-002—006` 中林秋由原件保护方案触发、沈禾由删回执与个人追责触发；三人分别选择、签字并承担公开、停职、封存及关系裂痕等代价 |
| `GATE-003` | `causality` | 4/4 | PASS_FIRST_CHECK | `BODY-001—007` 形成异常发现→独立停表交叉→合法取样→程序门槛→公证／签名证据→收件编号→重新受理的完整链；无巧合解局或一证定责 |
| `GATE-004` | `pacing` | 4/4 | PASS_FIRST_CHECK | 八个锚点持续改变知识、风险、关系、资源或制度状态；技术说明均直接服务证据边界和人物决定，无连续空转 |
| `GATE-005` | `sustainability` | 3/4 | PASS_FIRST_CHECK | 本次短篇在“时间恢复、调查重启、责任未定、家庭代价保留”处完成承诺；后果可继续生长且不依赖重复发现新真钟。开放调查属于受控余波，不是未完成核心冲突 |
| `GATE-006` | `plot_continuity` | 4/4 | PASS_FIRST_CHECK | `BODY-001—008` 的时间、材料、持有人、授权、触发、签署、复核与余波逐段承接；八锚点无跳号、无道具或信息无来源跳变 |

```yaml
hard_gate_results:
  - gate_result_id: GATE-001
    gate: story_facts
    score: 4
    status: pass_first_check
    evidence_body_refs: [BODY-001, BODY-002, BODY-003, BODY-005, BODY-007, BODY-008]
    revision_decision_refs: []
  - gate_result_id: GATE-002
    gate: character_agency
    score: 4
    status: pass_first_check
    evidence_body_refs: [BODY-002, BODY-004, BODY-005, BODY-006, BODY-008]
    revision_decision_refs: []
  - gate_result_id: GATE-003
    gate: causality
    score: 4
    status: pass_first_check
    evidence_body_refs: [BODY-001, BODY-002, BODY-003, BODY-004, BODY-005, BODY-006, BODY-007]
    revision_decision_refs: []
  - gate_result_id: GATE-004
    gate: pacing
    score: 4
    status: pass_first_check
    evidence_body_refs: [BODY-001, BODY-002, BODY-003, BODY-004, BODY-005, BODY-006, BODY-007, BODY-008]
    revision_decision_refs: []
  - gate_result_id: GATE-005
    gate: sustainability
    score: 3
    status: pass_first_check
    evidence_body_refs: [BODY-007, BODY-008]
    revision_decision_refs: []
  - gate_result_id: GATE-006
    gate: plot_continuity
    score: 4
    status: pass_first_check
    evidence_body_refs: [BODY-001, BODY-002, BODY-003, BODY-004, BODY-005, BODY-006, BODY-007, BODY-008]
    revision_decision_refs: []
pass_threshold_each: 3
pass_count: 6
fail_count: 0
all_six_logic_gates_pass: true
```

## 4. 内部修订项与登记边界

```yaml
internal_revision_required: false
internal_revision_items: []
failed_internal_draft_externalization_allowed: false
art_registration_allowed_after_this_qc: true
art_registration_performed_in_this_qc: false
registered_art_refs: []
next_allowed_state: PASS_FOR_FIRST_EXTERNAL_ARTIFACT_REGISTRATION
```

没有门禁低于 3，因此本轮不生成强制内部修订项。`sustainability` 的 3 分表示结局刻意把定责调查保留为后果空间，不是逻辑失败；无需为了升到 4 分擅自补写调查结论。

## 5. 最终放行声明

**PASS_FOR_FIRST_EXTERNAL_ARTIFACT_REGISTRATION**

放行范围仅限：后续流程可据本次六门通过结果，另行组装并核验符合 completed 分支完整输出契约的第一次外部小说成品。当前隐藏稿仍保持内部状态；本文件不登记 `ART-*`，不把 `external_artifact_ref` 从 `NONE` 改写为任何值，也不把 `first_external_novel_count` 从 `0` 改为 `1`。
