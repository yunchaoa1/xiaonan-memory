# OPC GPT Image 主体资产纯静态预检报告 v0.1

## 1. 结论与边界

- **预检结论：PASS（静态 fixture 与覆盖矩阵的预期结论一致）**。
- **资产逐项结果：21 PASS / 0 FAIL**；其中 8 项通过主体充分性预检、可进入后续生成流程，13 项按预期返回 `ASSET_BLOCKED`。
- **文件/结构检查：7 PASS / 0 FAIL / 1 WARN**。唯一 WARN 是资产提取主包第 483 行仍为未勾选的“独立 verifier 复审”，但同一主包第 470 行声明 `PASS_VERIFIED_V0.11`，且独立验收报告实体存在、SHA-256 匹配、正文明确 `PASS` / 问题数 `0`。本报告不改写该上游内部表述差异。
- 本报告仅是 **preflight（纯静态输入、来源、ID、状态、未知字段和充分性门禁检查）**。
- 本次 **未调用 GPT Image API、未生成图片、未做 API/模型/端点/参数实测、未做图片人工 QC、未创建输出图哈希、未锁版**。因此“可进入”不等于 `LOCKED`，也不表示节点或 Skill 已完成最终验收。
- 未修改覆盖矩阵、固定回归材料、资产提取主包、逐镜 CSV、验收报告或目标 Skill。

## 2. 固定输入与哈希核验

| 检查对象 | 存在 | 覆盖矩阵/固定材料声明 SHA-256 | 实算 SHA-256 | 结果 |
|---|---:|---|---|---|
| `D:\Documents\我的文档\十二时辰_第一章_剧本资产提取_Skill测试版v0.11.md` | 是 | `e3729383348a4b735b137c9d30221ca76faec52c4b3247157f23e6435e2751a1` | `e3729383348a4b735b137c9d30221ca76faec52c4b3247157f23e6435e2751a1` | PASS |
| `D:\Documents\我的文档\十二时辰_第一章_逐镜资产绑定_v0.11.csv` | 是 | `e2addd365217f9e8e26300640bca296b285e766318d4cee81df4f662be322066` | `e2addd365217f9e8e26300640bca296b285e766318d4cee81df4f662be322066` | PASS |
| `D:\Hermes\xiaonan-memory\references\十二时辰_第一章_资产提取Skill回归报告_v0.11.md` | 是 | `ddf89e92eea4191f68cbc7adde809445c473cb5dd163808b39d13455433dff8c` | `ddf89e92eea4191f68cbc7adde809445c473cb5dd163808b39d13455433dff8c` | PASS |
| `D:\Hermes\xiaonan-memory\references\opc-gpt-image-subject-assets-coverage-v0.1.md` | 是 | 不适用（本次判定输入） | `d7daa9a5109bf08f40b74156893fc0c43a0556a395fd021bb4fb35e0806f308a` | PASS |
| `D:\Hermes\xiaonan-memory\references\opc-gpt-image-subject-assets-regression-v0.1.md` | 是 | 不适用（本次判定输入） | `3123676d37f2509389663fd159daac3b5fbe0e89064115d5124ddfb562401735` | PASS |
| `D:\Hermes\skills\creative\gpt-image-subject-assets-opc-test\SKILL.md` | 是 | 不适用（预检规则） | `48fc8edfd0bc7c6c81026fc3e2fc26dd05f09fcd3bcc27ba2ab8b75a93d4a1f5` | PASS |

逐镜 CSV 实算：40 条数据、40 个唯一 `shot_id`、0 个重复；18 个唯一人物快照 ID、5 个唯一场景 ID、15 个实际引用的道具状态 ID。与覆盖矩阵声明一致。主包定义的 3 个未被 CSV 独立静帧引用的道具状态仍为：`prop-state.ox-hairpin.broken.v0.1`、`prop-state.redemption-coins.scattered.v0.1`、`prop-state.future-lighter.held.v0.1`；这不是未声明 ID，但不得据此宣称已有对应主体状态图。

## 3. reason_code 口径

- `ELIGIBLE_SUFFICIENT_SOURCED_FACTS`：稳定 ID、显式版本、来源/逐镜绑定与主体充分性均满足；仅代表可进入后续生成流程。
- `CHARACTER_IDENTITY_INSUFFICIENT`：人物身份的稳定可见事实不足，不能在不补事实的前提下锁定可复用主体。
- `SCENE_PLACEHOLDER_TOPOLOGY_INSUFFICIENT`：场景 ID 明确为 `.placeholder`，结构/拓扑/环境事实不足。
- `PROP_MASTER_GEOMETRY_INSUFFICIENT`：道具状态链存在，但主体几何、材质或结构不足。
- `EXPECTED_BLOCK_CONFIRMED`：静态实测阻断与覆盖矩阵预期一致；该项的测试结果记 PASS，而不是把预期阻断误记为测试失败。

## 4. 逐项资产预检

> `affected_fields` 只列阻断或必须保持未知/分离的字段；不得把未知字段补成提示词事实。`source` 同时核对主包定义与 CSV 引用。

| # | asset_id | type | state | source | 预期状态 | 实际预检状态 | reason_code | affected_fields | 对照结果 |
|---:|---|---|---|---|---|---|---|---|---|
| 1 | `identity.niu-man.v0.1` | character | `snapshot.niu-man.bound.v0.1` | 主包场1—2；CSV S01—S04B | 可进入预检 | `ELIGIBLE_PRECHECK_PASS` | `ELIGIBLE_SUFFICIENT_SOURCED_FACTS` | `age_range=unknown`；外部道具/能力不得写入人物底板 | PASS |
| 2 | `identity.niu-man.v0.1` | character | `snapshot.niu-man.awakened-frozen.v0.1` | 主包场3；CSV S05—S08A.start | 可进入预检 | `ELIGIBLE_PRECHECK_PASS` | `ELIGIBLE_SUFFICIENT_SOURCED_FACTS` | `age_range=unknown`；能力状态独立绑定 | PASS |
| 3 | `identity.niu-man.v0.1` | character | `snapshot.niu-man.awakened-restored.v0.1` | 主包场4前段；CSV S08A.end/S08B/S09.start | 可进入预检 | `ELIGIBLE_PRECHECK_PASS` | `ELIGIBLE_SUFFICIENT_SOURCED_FACTS` | `age_range=unknown`；打火机/能力独立绑定 | PASS |
| 4 | `identity.niu-man.v0.1` | character | `snapshot.niu-man.awakened-controlled.v0.1` | 主包场4后段—场6；CSV S09.end—S13A.start 对应行 | 可进入预检 | `ELIGIBLE_PRECHECK_PASS` | `ELIGIBLE_SUFFICIENT_SOURCED_FACTS` | `age_range=unknown`；打火机/蓝火独立绑定 | PASS |
| 5 | `identity.niu-man.v0.1` | character | `snapshot.niu-man.cost-felt.v0.1` | 主包场7；CSV S13A.end—S14A.start | 可进入预检 | `ELIGIBLE_PRECHECK_PASS` | `ELIGIBLE_SUFFICIENT_SOURCED_FACTS` | `age_range=unknown`；寿数机制/数值保持未知 | PASS |
| 6 | `identity.niu-man.v0.1` | character | `snapshot.niu-man.cost-felt-late.v0.1` | 主包场8；CSV S14A.end | 可进入预检 | `ELIGIBLE_PRECHECK_PASS` | `ELIGIBLE_SUFFICIENT_SOURCED_FACTS` | `age_range=unknown`；道具归还与能力熄灭独立绑定 | PASS |
| 7 | `identity.niu-man.v0.1` | character | `snapshot.niu-man.changed.v0.1` | 主包场9；CSV S15A/S15B | 可进入预检 | `ELIGIBLE_PRECHECK_PASS` | `ELIGIBLE_SUFFICIENT_SOURCED_FACTS` | `age_range=unknown`；外部道具/能力不得混入底板 | PASS |
| 8 | `scene.village-old-locust-tree.v0.1` | scene | 场1—5、7—9稳定空间状态 | 主包原文5—143、157—177、181—195行；CSV 34 行引用 | 可进入预检 | `ELIGIBLE_PRECHECK_PASS` | `ELIGIBLE_SUFFICIENT_SOURCED_FACTS` | 未锁定建筑/村庄陈设；仅用空间核心、轴线、地标、泥地、三月寒风 | PASS |
| 9 | `identity.wang-er.v0.1` | character | `snapshot.wang-er.abuser/frozen/fear/heat-damaged.v0.1`（4 个显式快照 ID） | 主包场1—5；CSV S02A—S15 对应行 | `ASSET_BLOCKED` | `ASSET_BLOCKED` | `CHARACTER_IDENTITY_INSUFFICIENT;EXPECTED_BLOCK_CONFIRMED` | `gender=unknown`; `age_range=unknown`; `face`; `body`; 服装细节；受损版依赖未锁定 identity | PASS |
| 10 | `identity.gold-mark-boy.v0.1` | character | `snapshot.gold-mark-boy.chained.v0.1` | 主包场6；CSV S12B-2 | `ASSET_BLOCKED` | `ASSET_BLOCKED` | `CHARACTER_IDENTITY_INSUFFICIENT;EXPECTED_BLOCK_CONFIRMED` | `age=unknown`; `costume=unknown`; `face`; `body`; 铁链必须保持独立 prop 绑定 | PASS |
| 11 | `identity.future-young-person.v0.1` | character | `snapshot.future-person.smoking.v0.1` | 主包场8；CSV S14B.start/S14B.end | `ASSET_BLOCKED` | `ASSET_BLOCKED` | `CHARACTER_IDENTITY_INSUFFICIENT;EXPECTED_BLOCK_CONFIRMED` | `age=unknown`; `gender`; `face`; `body`; `costume_details=unknown`; 未来街边/火柴必须独立绑定 | PASS |
| 12 | `scene.market.placeholder.v0.1` | scene | 场6.market | 主包场6；CSV S12B-1 | `ASSET_BLOCKED` | `ASSET_BLOCKED` | `SCENE_PLACEHOLDER_TOPOLOGY_INSUFFICIENT;EXPECTED_BLOCK_CONFIRMED` | 具体时代、建筑、陈设未知 | PASS |
| 13 | `scene.dungeon.placeholder.v0.1` | scene | 场6.dungeon | 主包场6；CSV S12B-2 | `ASSET_BLOCKED` | `ASSET_BLOCKED` | `SCENE_PLACEHOLDER_TOPOLOGY_INSUFFICIENT;EXPECTED_BLOCK_CONFIRMED` | 建筑结构、出口、人物面向、具体光源未知 | PASS |
| 14 | `scene.ruined-temple.placeholder.v0.1` | scene | 场6.temple | 主包场6；CSV S12B-3 | `ASSET_BLOCKED` | `ASSET_BLOCKED` | `SCENE_PLACEHOLDER_TOPOLOGY_INSUFFICIENT;EXPECTED_BLOCK_CONFIRMED` | 庙宇具体形制未知 | PASS |
| 15 | `scene.future-street.placeholder.v0.1` | scene | 场8.future | 主包场8；CSV S14B.start/S14B.end | `ASSET_BLOCKED` | `ASSET_BLOCKED` | `SCENE_PLACEHOLDER_TOPOLOGY_INSUFFICIENT;EXPECTED_BLOCK_CONFIRMED` | 城市、年代、街道细节、天气、光线未知 | PASS |
| 16 | `prop.rope.v0.1` | prop | `prop-state.rope.taut.v0.1`; `prop-state.rope.broken.v0.1` | 主包场1—3/`tr.rope.break`；CSV S01—S08B 对应行 | `ASSET_BLOCKED` | `ASSET_BLOCKED` | `PROP_MASTER_GEOMETRY_INSUFFICIENT;EXPECTED_BLOCK_CONFIRMED` | material；structure；repeatable_visual_identity | PASS |
| 17 | `prop.ox-hairpin.v0.1` | prop | hidden→held→broken→mud | 主包场1—2/`tr.hairpin.*`；CSV 引用 hidden/held/mud | `ASSET_BLOCKED` | `ASSET_BLOCKED` | `PROP_MASTER_GEOMETRY_INSUFFICIENT;EXPECTED_BLOCK_CONFIRMED` | 完整几何/材质/结构；仅“簪头模糊小牛”不足；broken 无独立 CSV 静帧引用 | PASS |
| 18 | `prop.redemption-coins.v0.1` | prop | hidden→held→scattered→mud | 主包场1—2/`tr.coins.*`；CSV 引用 hidden/held/mud | `ASSET_BLOCKED` | `ASSET_BLOCKED` | `PROP_MASTER_GEOMETRY_INSUFFICIENT;EXPECTED_BLOCK_CONFIRMED` | geometry；material；structure；scattered 无独立 CSV 静帧引用 | PASS |
| 19 | `prop.future-lighter.v0.1` | prop | absent→held→active→returned-pending→returned | 主包场4—9/`tr.lighter.*`；CSV 引用 absent/active/returned-pending/returned | `ASSET_BLOCKED` | `ASSET_BLOCKED` | `PROP_MASTER_GEOMETRY_INSUFFICIENT;EXPECTED_BLOCK_CONFIRMED` | 完整外观/几何/材质/结构；不得由“未来”补设计；held 无独立 CSV 静帧引用 | PASS |
| 20 | `prop.match.v0.1` | prop | `prop-state.match.unlit.v0.1`; `prop-state.match.lit.v0.1` | 主包场8/`tr.match.light`；CSV S14B.start/S14B.end | `ASSET_BLOCKED` | `ASSET_BLOCKED` | `PROP_MASTER_GEOMETRY_INSUFFICIENT;EXPECTED_BLOCK_CONFIRMED` | 可复用外观、材质、式样；不得补火柴盒 | PASS |
| 21 | `prop.chain.v0.1` | prop | `prop-state.chain.locked.v0.1` | 主包场6；CSV S12B-2 | `ASSET_BLOCKED` | `ASSET_BLOCKED` | `PROP_MASTER_GEOMETRY_INSUFFICIENT;EXPECTED_BLOCK_CONFIRMED` | `material=unknown`; `structure=unknown`; 与金纹少年保持独立绑定 | PASS |

## 5. ID、状态、未知字段与阻断结论核验

| 检查 | 实际结果 | 结论 |
|---|---|---|
| 上游文件存在 | 3 个固定上游文件、覆盖矩阵、固定回归材料及目标 Skill 均存在 | PASS |
| 固定上游 SHA-256 | 主包、CSV、独立验收报告均与覆盖矩阵/固定回归材料声明逐字一致 | PASS |
| CSV 结构与唯一性 | 40 数据行；40 唯一 `shot_id`；无重复 | PASS |
| 覆盖 ID | 18 唯一人物快照、5 唯一场景、15 个 CSV 实际引用道具状态；本表所列 ID 均可在主包及相应 CSV 绑定中定位 | PASS |
| 可进入项 | 牛满 7 个快照 + 村口老槐树 1 个场景，共 8 项；均仅通过静态充分性门禁 | PASS |
| 必检阻断人物 | 王二、金纹少年、未来年轻人均保持 `ASSET_BLOCKED`，未补性别/年龄/脸/体型/服装等未知事实 | PASS |
| placeholder 场景与 6 类道具 | 4/4 placeholder 场景、6/6 道具均保持 `ASSET_BLOCKED` | PASS |
| 上游验收表述一致性 | 独立验收报告为 PASS/问题数0且哈希匹配；主包第470行也声明 PASS，但第483行 checklist 未勾选 | WARN |

## 6. 最终统计与门禁解释

- `ASSET_ITEM_PASS=21`
- `ASSET_ITEM_FAIL=0`
- `ELIGIBLE_PRECHECK_PASS=8`
- `EXPECTED_ASSET_BLOCKED_CONFIRMED=13`
- `STATIC_CHECK_PASS=7`
- `STATIC_CHECK_FAIL=0`
- `STATIC_CHECK_WARN=1`
- `GPT_IMAGE_API_CALLS=0`
- `GENERATED_IMAGES=0`
- `HUMAN_IMAGE_QC=NOT_RUN`
- `LOCKED_ASSETS=0`

静态预检通过只证明固定输入在当前哈希下可复现覆盖矩阵的“可进入/应阻断”结论。后续若执行真实生成，仍必须提供并验证受控 `runtime_model_id`、endpoint、参数、reference manifest，执行图片解码/元数据/输出 SHA-256 检查和独立人工 QC；在这些步骤完成前，任何项目均不得标为 `LOCKED`。
