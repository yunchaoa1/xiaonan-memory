# GPT Image 主体资产 Skill 测试版最终短复审 v0.1

- 验收对象：`D:\Hermes\skills\creative\gpt-image-subject-assets-opc-test\SKILL.md`
- 对象版本：`0.1.0-test`
- 对象 SHA-256（实算）：`48fc8edfd0bc7c6c81026fc3e2fc26dd05f09fcd3bcc27ba2ab8b75a93d4a1f5`
- 复审性质：独立 verifier 最终短复审；只更新本报告，不修改 Skill 或任何输入
- 最新评分：**40 / 44（90.9%）**
- 总结论：**文档结构 PASS；静态 fixture/preflight PASS；运行时图片生成与锁版 PENDING（未完成）；整体运行验收不能完整 PASS。**

## 1. 已核对材料

| 材料 | 行数 | SHA-256（实算） | 复审用途 |
|---|---:|---|---|
| `D:\Hermes\skills\creative\gpt-image-subject-assets-opc-test\SKILL.md` | 204 | `48fc8edfd0bc7c6c81026fc3e2fc26dd05f09fcd3bcc27ba2ab8b75a93d4a1f5` | 节点职责、状态、硬门禁、输出契约 |
| `opc-gpt-image-subject-assets-regression-v0.1.md` | 166 | `3123676d37f2509389663fd159daac3b5fbe0e89064115d5124ddfb562401735` | 固定 fixture 与预期边界 |
| `opc-gpt-image-subject-assets-machine-audit-v0.1.md` | 93 | `172029bed594b6cd2614631a94dc18c465dbd33fbe2d297c682e8cfbfbba2554` | 机器审计字段及枚举 |
| `opc-gpt-image-subject-assets-coverage-v0.1.md` | 78 | `d7daa9a5109bf08f40b74156893fc0c43a0556a395fd021bb4fb35e0806f308a` | 资产覆盖及 eligible/blocked 基线 |
| `opc-gpt-image-subject-assets-preflight-v0.1.md` | 88 | `d48b79fece3d3b0bb7a933dc75367ba72f5b546b4a6ed6eda17f59b394e92027` | 已交付的纯静态预检实跑证据 |

## 2. 三层最终判定

| 证据层 | 最终状态 | 已证实 | 尚未证实 |
|---|---|---|---|
| A. 文档结构 | **PASS** | 职责边界、封闭输入、充分性门禁、模型运行时校验、输出解码/哈希、QC、唯一锁版原则成立 | 不证明运行实现已经执行 |
| B. 静态 fixture / preflight | **PASS** | 纯静态预检已经真实交付：逐项 **21 PASS / 0 FAIL**；其中 **8 eligible**，**13 `ASSET_BLOCKED`**；固定输入哈希、ID、CSV 唯一性、未知字段及预期阻断边界均已核对 | 不证明 API、图片字节、人工可见事实或锁版 |
| C. 运行时图片生成与锁版 | **PENDING / 未完成** | 当前仅有应执行的规则 | 真实 GPT Image API 请求/响应、图片解码与元数据、输出 SHA-256、人工可见事实 QC、human confirmation、唯一 lock record 均无实证 |

因此，静态层通过不能上推为运行层通过；整体运行验收当前不得写为完整 `PASS` 或 `LOCKED`。

## 3. 静态预检实跑复核

预检报告已明确记录并逐项列出：

- `ASSET_ITEM_PASS=21`，`ASSET_ITEM_FAIL=0`；
- `ELIGIBLE_PRECHECK_PASS=8`：牛满 7 个显式快照 + `scene.village-old-locust-tree.v0.1`；
- `EXPECTED_ASSET_BLOCKED_CONFIRMED=13`：3 个必检人物主体（王二、金纹少年、未来年轻人）+ 4 个 placeholder 场景 + 6 个道具主体；
- `STATIC_CHECK_PASS=7`，`STATIC_CHECK_FAIL=0`，`STATIC_CHECK_WARN=1`；
- `GPT_IMAGE_API_CALLS=0`，`GENERATED_IMAGES=0`，`HUMAN_IMAGE_QC=NOT_RUN`，`LOCKED_ASSETS=0`。

逐项表的 21 个“PASS”是**测试对照结果**：8 项实际状态为 `ELIGIBLE_PRECHECK_PASS`，13 项实际状态为预期的 `ASSET_BLOCKED`。预期阻断被正确触发属于静态测试 PASS，不等于该资产可生成。

唯一静态 WARN 是上游主包第 483 行 checklist 未勾选“独立 verifier 复审”，但第 470 行声明 `PASS_VERIFIED_V0.11`，独立验收报告实体存在、正文为 PASS/问题数 0 且 SHA 匹配；该表述差异不推翻本次静态预检结论。

## 4. 旧硬失败关闭情况

因“预检尚未交付”产生的旧项已经关闭，并从当前剩余硬失败中删除：

- **旧 HF-01（固定 fixture 实际 preflight 输出缺失）：CLOSED。** `opc-gpt-image-subject-assets-preflight-v0.1.md` 已存在，含逐项 expected/actual、typed status、reason code、affected fields 和汇总。
- **旧 HF-02（必检阻断用例未实跑）：CLOSED。** 王二、金纹少年、未来年轻人、4 个 placeholder 场景及 6 个道具主体均在静态预检中按预期返回 `ASSET_BLOCKED`；没有通过 prompt 补事实解阻。

关闭以上两项只关闭静态证据缺失，不代表运行时生成、图片 QC 或锁版完成。

## 5. 状态枚举分层复核

当前仍存在两套不同语义的枚举：

1. Skill 的**节点结果**：`LOCKED | RETRYABLE_FAILED | ASSET_BLOCKED | PROVENANCE_BLOCKED | MODEL_BLOCKED | POLICY_BLOCKED | QC_FAILED`；
2. 机器审计规范的**生命周期状态**：`DRAFT | GENERATED | QC_PENDING | QC_PASS | QC_FAIL | LOCKED`，另有 `qc_status=PENDING|PASS|FAIL` 与 `lock_status=UNLOCKED|LOCKED`；
3. 静态预检报告还使用测试阶段值 `ELIGIBLE_PRECHECK_PASS`，它不是 Skill 的终态，也不是机器审计生命周期终态。

最小必要分层应固定为：

- `preflight_result`：`ELIGIBLE | BLOCKED`；
- `node_result`：Skill typed result；
- `lifecycle_status`：运行阶段；
- `machine_qc_status` 与 `human_qc_status`：分开记录，禁止机器代填人工结论；
- `lock_status`：`UNLOCKED | LOCKED`。

还需声明合法组合。例如：`ASSET_BLOCKED` 必须发生在调用模型前、允许没有输出文件，并强制 `lock_status=UNLOCKED`；`QC_FAILED` 对应 `lifecycle_status=QC_FAIL`；只有机器 QC 与人工 QC 均 PASS、human confirmation 有效且 lock record 完整时，才允许 `node_result=LOCKED`、`lifecycle_status=LOCKED`、`lock_status=LOCKED`。

## 6. 最小机器契约缺口

静态预检报告已经补足逐项静态证据，但尚未形成可无歧义承载全流程的最小机器契约，缺口为：

- 没有统一 JSON Schema 将 `ELIGIBLE_PRECHECK_PASS`、Skill typed result 与 lifecycle/QC/lock 枚举分层映射；
- 缺 blocked preflight 的条件必填规则；现机器审计规范把 `model_id`、`output_file`、尺寸、输出哈希一律要求非空，无法合法表示模型调用前的 `ASSET_BLOCKED`；
- 缺 generation request/response 的字段级 required/optional 规则，以及 endpoint/model 条件下的参数约束；
- `source_manifest` 哈希映射、`fact_to_source_map`、`reason_code`、`affected_fields`、reference manifest 尚无统一机器 schema；
- `locked_fields` / required invariants 没有统一字段路径、值、来源和适用状态结构；
- `human_confirmation` 缺确认人、确认对象、证据定位、时间、结果枚举及“聊天确认不得补事实”的机器规则；
- 缺 `LOCKED` 合法组合、唯一正式输出、版本不可覆盖及失败资产不得锁定的机器断言；
- 尚无真实 audit input/output JSON 对运行产物做逐检查读回。

这些缺口不推翻静态 fixture/preflight PASS，但会阻止运行时结果获得可审计的完整 PASS。

## 7. 最新评分

沿用 11 项、每项 0—4 分的既有口径：

| 检查项 | 分数 |
|---|---:|
| YAML 与职责边界 | 3 |
| 运行时封闭信息边界 | 4 |
| 人物/场景/道具母版与状态版本 | 4 |
| ID/版本/来源哈希追溯 | 3 |
| `model_id` 不写死与参数校验 | 4 |
| 阻断结果与状态枚举 | 3 |
| 参考图、输出元数据、QC 和唯一锁版 | 3 |
| 硬门禁与软诊断分离 | 4 |
| 未验证能力边界 | 4 |
| 聊天/网络/项目外设定隔离 | 4 |
| 覆盖矩阵、固定回归及静态预检边界 | 4 |

**总分：40 / 44（90.9%）。** 分数未因静态预检交付而虚增：原评分中的覆盖/回归项已是满分；当前扣分仍来自 frontmatter/独立契约字段、最小机器 schema、状态分层、human confirmation 与真实产物/锁版证据缺口。结构高分与静态 PASS 均不等于运行验收 PASS。

## 8. 当前剩余硬失败

以下运行硬门禁仍未关闭：

1. **HF-R01：真实 GPT Image API 生成缺失。** 至少一个 eligible 项尚无真实请求/响应、request ID、实际 model ID、endpoint、显式参数、reference manifest 和 provider usage/error 记录。
2. **HF-R02：图片字节解码及产物核验缺失。** 尚无真实返回图片的 base64/字节解码、MIME、实际格式、宽高、alpha/background、字节数及输出 SHA-256 读回核验。
3. **HF-R03：可见事实 QC 与 human confirmation 缺失。** 无真实图片可核验身份、未知保留、场景拓扑、道具/职责污染和逐不变量结果；人工结果必须保持 `PENDING`，不得由机器代填。
4. **HF-R04：唯一锁版缺失。** 尚无完整且唯一的 lock record；`LOCKED_ASSETS=0`，不得向下游交付正式锁版。
5. **HF-R05：运行机器审计闭环缺失。** 尚无与分层状态、条件必填规则相容的 audit input/output JSON 对真实产物逐项执行并读回。

任一项未关闭，整体运行验收均不能完整 PASS。

## 9. 下一步最小真实生成条件

只选择 8 个 eligible 项中的 **1 个** 做最小真实闭环；推荐先用单一牛满快照或老槐树场景。调用前必须满足：

1. 引用已经通过的逐项静态 preflight 记录，保持所有 explicit unknowns；
2. 从受控运行配置取得并实测 `runtime_model_id`、权限、endpoint 与参数 schema，禁止静默默认或降级；
3. 固化一次运行的最小 request/response schema，显式记录 source/fact map、prompt schema、node run ID、requested/actual parameters；
4. `reference_images` 明确为空，或每张均有批准来源、版本、SHA、角色和顺序；
5. 保存真实响应和图片字节，完成解码并读回 MIME/格式/尺寸/alpha/background/bytes/SHA-256；
6. 分开执行 machine QC、独立人工可见事实 QC 与 `human_confirmation`，未完成时保持 PENDING；
7. 仅当全部硬门禁 PASS 时生成一个且仅一个 lock record，并以机器审计 JSON 读回验证合法组合与唯一输出。

## 10. 最终判定

- **文档结构：PASS**
- **静态 fixture/preflight：PASS（21/21 对照 PASS；8 eligible；13 `ASSET_BLOCKED`）**
- **运行时图片生成、解码、可见事实 QC、human confirmation、唯一锁版：PENDING / 未完成**
- **整体运行验收：不能完整 PASS**

当前最准确结论：**静态预检已经真实完成，旧 HF-01/HF-02 已关闭；节点已具备进入最小真实生成测试的静态前提，但在真实 API 图片、解码核验、人工可见事实确认、机器审计闭环和唯一锁版证据出现前，运行验收仍为未完成。**
