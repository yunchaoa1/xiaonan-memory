# FIX-MULTIFORMAT-001 · 终稿独立差异与断言核验

- 核验对象：`01_initial_output.md`（0.1-initial）与 `03_revised_final.md`（0.2-revised）
- 参考但不继承结论：`02_gate_report.md`
- 方法：逐段比较初稿/终稿正文，独立检查终稿正文、source registry、provenance、handoff 与 fixture；**未依据终稿自报的 `pass_after_revision` 放行**。
- 评分：每门 0–4；3–4 为 PASS，0–2 为 FAIL；任一硬门禁 FAIL 则总 FAIL。

## 一、初稿 → 终稿的具体差异

1. **来源定位**：终稿新增 `source_registry`（L5–L10），定义 `SRC-USER-001`、固定客户输入原文、运行时外部来源数 1、历史/网络来源数 0；初稿仅引用该 ID 而未定义。
2. **BODY 锚点**：终稿在正文加入 `BODY-001`—`BODY-008` 八个唯一 HTML 锚点（L22、29、34、45、52、71、79、120）；初稿的同名引用全部悬空。
3. **“每位”全称量词**：初稿只写“三名乘客没有下车”，不能证明全车范围；终稿明确“当晚的末班车总共只有三名乘客”且逐一核对每一名都缺失当天最后一段记忆（L30–L32）。
4. **返程机制前置试验**：终稿新增倒出站台十几米的小规模试验（L53–L55）：周岚仅恢复病房号碎片，男孩无恢复，并明确不保证找回；随后司机才据此决定返程（L63–L65）。初稿直接从“七分钟中断”跳到完整返程。
5. **恢复结果去整齐化**：初稿在相邻路口让周岚、男孩依次恢复关键记忆；终稿改为周岚分两阶段恢复、男孩依靠笔迹和缴费单推断且未恢复更多、罗庆仍未完整恢复（L73–L77、L104）。
6. **不情愿盟友落实**：终稿新增周岚要求下车、男孩说服她留下，以及三人以信息和路线互相支撑返程（L73、L110）；初稿主要是三条平行私人行动。
7. **provenance 补登记**：终稿新增 PAD-012（逆向移动只触发不完整碎片且不保证有效，`inference`）与 PAD-013（先小试验再完整返程，`decision`），均定位 BODY-005（L227–L242）。
8. **版本和状态**：小说版本由 `0.1-initial` 改为 `0.2-revised`；fixture stage 由 `initial_output_only` 改为 `revised_final_pending_independent_qc`。终稿中五门禁自报为 `pass_after_revision`，本报告不采用该自报作为证据。
9. **正文文本差异统计**：按 `### body` 至 provenance 前逐行比较，共 14 个非等同 diff 区块，新增/替换侧 20 行、删除/替换侧 7 行（锚点行计入）。

## 二、指定断言独立核验

| 断言 | 结果 | 独立依据 |
|---|---|---|
| “每位”量词完整落实 | **PASS** | L30 将当班总人数封闭为三人，L32 明确逐一核对且每一名都缺失当天最后一段记忆；未再把全称命题缩成“留下的三人”。 |
| 返程恢复有小规模试验 | **PASS** | L55 的十几米倒车是先于完整返程的有限试验。 |
| 小试验结果不完整 | **PASS** | 周岚只恢复病房号碎片并说“只记得这一点”，男孩无恢复；正文明确“不保证能够找回”（L55）。 |
| 小试验及不完整恢复有 provenance | **PASS** | PAD-012、PAD-013 均指向 BODY-005，并分别登记不完整/个体差异与先试验后返程（L227–L242）。 |
| `SRC-USER-001` 有 source registry | **PASS** | L5–L10 存在唯一 registry，含 exact_customer_input；正文内共出现该 ID 6 次（定义 1、五个 user_fact 引用 5）。 |
| `BODY-001`—`BODY-008` 均可定位 | **PASS** | 八个锚点各定义恰好 1 次，均在小说正文内；无缺号、无重复定义。 |
| provenance 五类 items | **PASS** | 13 项：`user_fact=5`、`inference=2`、`default=1`、`decision=3`、`risk=2`，五类齐全。 |
| selected 恰好 1 | **PASS** | 仅 PATH-002 的 `status: selected`；`selected_path_id` 与 `selected_path_count: 1` 一致。 |
| `external_candidate_bodies=0` | **PASS** | 终稿唯一该字段值为 0；未发现候选正文。 |
| 历史污染词 0 | **PASS** | 对 `牛满、十二神位、齐白兰、顾蓝汐、齐镇海、蓝宝石、寻亲` 逐词扫描，7 个词总命中 0。 |
| 客户事实保留 | **PASS** | 夜班公交司机（BODY-001）、每位乘客缺失当天记忆（BODY-002）、城市/记忆/克制（全篇及 PAD-003）、司机见证者与乘客不情愿盟友（BODY-003/006/007）、钟慢七分钟（BODY-004）均保留。 |
| 唯一交付/分支互斥 | **PASS** | 恰有 1 个 `## novel`、0 个 `## blockage`，1 份小说正文；run_status 为 completed，未出现第二方案或 alternate novel。 |

## 三、五类硬门禁重新评分

### GATE-001 · 故事事实 — **2/4，FAIL**

- **通过部分**：时间差、三名总乘客、“每位”覆盖、小试验及个体差异在正文内一致；BODY 锚点与 source registry 已修复。
- **独立失败点**：终稿仍把若干承担因果/设定作用的新增事实直接写入正文，却未登记为 `inference/default/decision`：陈渡“开夜班十二年”（L23）、罗庆“连续三晚”及前两晚具体经历（L53）、陈渡所忆前两晚其他相似病例（L61）。其中“连续三晚/前两晚病例”用于证明异常并促成司机行动，不只是无关修辞。PAD-006只登记“记忆缺失集中于终点前七分钟”，PAD-012/013只登记逆向试验规则，均不能回溯这些新增事实。
- Skill 的故事事实门禁明确要求“新增事实可追溯”；`02_gate_report.md` 也已把这些列为定向修订项，但终稿没有完成。因此不能因正文逻辑顺畅或自报 `pass_after_revision` 放行。

### GATE-002 · 人物能动性 — **4/4，PASS**

司机先排查、试验、提供退出机会、申请绕行并承担责任；周岚拒绝、男孩以物证推断并劝留、罗庆提供路线与钥匙，三人均以自己的选择推动行动，且司机没有替乘客解决人生问题。

### GATE-003 · 因果 — **3/4，PASS**

十几米试验先产生有限且有反例的结果，再触发完整返程；后续恢复不齐，男孩靠物证，核心解局不再依赖“每站自动完整恢复”。扣 1 分：罗庆指路仍较依赖身体恐惧，钥匙牌街道名直到 L110 才补述，线索前置仍可更清晰，但不足以构成硬失败。

### GATE-004 · 节奏 — **4/4，PASS**

试验、拒绝、物证推断、绕行代价与协作连续改变知识/关系/风险；初稿的相邻路口同构恢复和结尾排队结算已被明显打散，无连续空转。

### GATE-005 · 可持续性 — **3/4，PASS**

作为完整短篇有闭环且保留人物后续选择；机制未被绝对化，个体差异可产生新后果。扣 1 分：换钟后异常停止，若扩成长篇仍需另建非重复引擎；但当前承诺仅为完整短篇，不构成失败。

**门禁统计：PASS 4，FAIL 1；分数 `[2, 4, 3, 4, 3]`，合计 16/20。**

## 四、fixed fixture 断言统计

固定 case `FIX-MULTIFORMAT-001` 的 `expected_assertions` 共 3 条，本次实际核验：

1. `input_accepted_without_question` — **PASS**：completed 分支；`input_state.question_asked: false`，无提问/等待。
2. `explicit_units_have_SRC_refs` — **PASS**：五个显式客户单元分别由 PAD-001—005 登记，均指向已定义的 `SRC-USER-001`。
3. `output_matches_exactly_one_contract_branch` — **PASS**：completed 分支仅有一份 novel、无 blockage；唯一交付成立。

- fixture 断言总数：3
- PASS：3
- FAIL：0
- 断言通过率：3/3（100%）
- 注意：fixture 三项通过**不覆盖**全部硬门禁，不能抵消 GATE-001 的新增事实溯源失败。

## 五、总判定与剩余问题

# **总判定：FAIL**

原因：五类硬门禁中 **GATE-001 故事事实为 2/4 FAIL**；按“任一硬门禁失败则总 FAIL”执行。终稿自报的五个 `pass_after_revision` 不成立为独立验收证据。

**剩余问题（阻断放行）：**

1. 为 BODY-001/BODY-005 中“十二年夜班经验”“罗庆连续三晚及前两晚经历”“前两晚其他相似病例”补逐项 provenance，明确其 `kind/source_ref/body_ref/rule_ref/status/related_refs`；若不保留，则应从正文删除不必要新增事实。
2. 修复后须再次独立重跑 GATE-001；不得只修改终稿内自报状态。

**非阻断改进项：**可把钥匙牌街道名提前到罗庆指路之前，使辅路选择同时由物证与身体记忆导出。

---

## 六、最终复核追加段（GATE-001 修复后）

> 本段为对上文唯一失败门禁的追加复核；**保留上文原始 `GATE-001 2/4，FAIL` 与总判定 FAIL 作为修复历史，不覆盖、不删除。** 本段结论以 `03_revised_final.md` 当前内容为准，只复核新增事实 provenance、既有客户事实/BODY 锚点/污染隔离是否回退。

### 6.1 三组原悬空事实逐项闭合

| 正文新增事实 | provenance 项 | 六字段完整性与定位 | 结果 |
|---|---|---|---|
| 陈渡有十二年夜班驾驶经验（BODY-001） | `PAD-014` | `kind: default`；`source_ref: PAD-001`（已存在，指向夜班公交司机客户事实）；`body_ref: BODY-001`（正文唯一锚点）；`rule_ref: RULE-CHARACTER-COMPETENCE-MINIMUM`；`status: adopted`；`related_refs: [PAD-009]`（已存在） | **PASS** |
| 罗庆连续三晚乘车，前两晚分别遗忘旧城区经历、医院签字经历（BODY-005） | `PAD-015` | `kind: inference`；`source_ref: PAD-002`（已存在，指向末班乘客记忆缺失客户事实）；`body_ref: BODY-005`（正文唯一锚点）；`rule_ref: RULE-CAUSAL-PREFLIGHT`；`status: adopted`；`related_refs: [PAD-006, PAD-012]`（均已存在） | **PASS** |
| 陈渡回忆前两晚其他相似病例：年轻男人忘记道歉对象、护士忘记调班原因（BODY-005） | `PAD-016` | `kind: decision`；`source_ref: PAD-014`（已存在）；`body_ref: BODY-005`（正文唯一锚点）；`rule_ref: RULE-PROTAGONIST-WITNESS-AGENCY`；`status: adopted`；`related_refs: [PAD-013, PAD-015]`（均已存在） | **PASS** |

复核结论：`PAD-014/015/016` 均具有非空且合法的 `kind/source_ref/body_ref/rule_ref/status/related_refs`；所有 `PAD-*` 来源/关联引用均能在本稿 items 中定位，所有 `BODY-*` 引用均能在正文定位。三组曾阻断放行的新增事实已分别登记，**未发现仍悬空的上述关键事实**。

### 6.2 回退检查

- **原有客户事实未回退：PASS。** PAD-001—PAD-005 仍分别锁定夜班公交司机、每位末班乘客缺失当天记忆、城市/记忆/克制、见证者—不情愿盟友关系、终点钟慢七分钟；正文对应 BODY-001—BODY-004/006/007 的表达仍在。
- **BODY 锚点未回退：PASS。** `BODY-001`—`BODY-008` 八个锚点仍各定义一次、无缺号、无重复；PAD-014 指向 BODY-001，PAD-015/016 指向 BODY-005，均非悬空引用。
- **污染隔离未回退：PASS。** `source_registry` 仍声明本次运行外部创意来源 1、历史/网络来源 0；`forbidden_downstream_sources` 仍完整保留 `[customer_chat_supplement, history, network, oral_explanation, other_projects, internal_candidate_paths, unaccepted_drafts, production_distillation_material]`；污染探针词 `牛满、十二神位、齐白兰、顾蓝汐、齐镇海、蓝宝石、寻亲` 仍为 0 命中。
- **provenance 清单覆盖：PASS。** `downstream_handoff.provenance_item_refs` 已包含 PAD-014、PAD-015、PAD-016；当前 items 共 16 项，类型统计为 `user_fact=5`、`inference=3`、`default=2`、`decision=4`、`risk=2`，五类仍齐全。

### 6.3 修复后最新门禁评分与最终判定

- **GATE-001 · 故事事实：4/4，PASS（修复后最新评分）。** 正文事实一致性、客户事实锁定、稳定 BODY 定位均保持；此前唯一缺陷——十二年经验、罗庆连续三晚及前两晚经历、其他相似病例的 provenance 缺失——已由 PAD-014/015/016 逐项闭合。
- GATE-002 · 人物能动性：4/4，PASS（沿用上文独立评分，无回退）。
- GATE-003 · 因果：3/4，PASS（沿用上文独立评分，无回退）。
- GATE-004 · 节奏：4/4，PASS（沿用上文独立评分，无回退）。
- GATE-005 · 可持续性：3/4，PASS（沿用上文独立评分，无回退）。

**五门最终统计：PASS 5，FAIL 0；分数 `[4, 4, 3, 4, 3]`，合计 18/20。**

# **修复后最终总判定：PASS**

说明：本 PASS 是对当前终稿的最终独立复核结论；上文原 `FAIL` 记录属于修复前历史，继续保留。
