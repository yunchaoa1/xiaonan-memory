# 《十二时辰》第一章 GPT Image 主体资产覆盖矩阵 v0.1

## 1. 审计边界与判定口径

- 角色：asset-auditor；只核对人物、场景、道具、状态版本、来源 ID 与是否可进入 GPT Image 主体资产节点。
- 不核对能力资产，不新增人物特点、剧情、服装或场景事实，不生成图片，不修改上游文件。
- 上游事实源：
  - `D:\Documents\我的文档\十二时辰_第一章_剧本资产提取_Skill测试版v0.11.md`
  - `D:\Documents\我的文档\十二时辰_第一章_逐镜资产绑定_v0.11.csv`
- 验收依据：`D:\Hermes\xiaonan-memory\references\十二时辰_第一章_资产提取Skill回归报告_v0.11.md`，独立验收为 `PASS`、问题数 `0`。
- “可进入主体资产节点”判定：必须同时具备稳定主体 ID、适用状态版本、来源/逐镜绑定，以及足以在“不补事实”前提下形成可锁定主体图的上游可见事实。`否（阻断）`不表示资产提取失败，只表示不能在当前事实边界内直接生成并锁定 GPT Image 主体资产。

## 2. 实际读取范围与统计

### 2.1 实际读取范围

| 文件 | 实际读取范围 | SHA-256（本次实算） |
|---|---:|---|
| 资产提取主包 | 第 1—483 行（全文） | `e3729383348a4b735b137c9d30221ca76faec52c4b3247157f23e6435e2751a1` |
| 逐镜 CSV | 第 1—41 行（表头 1 行 + 数据 40 行，全文） | `e2addd365217f9e8e26300640bca296b285e766318d4cee81df4f662be322066` |
| 独立验收报告 | 第 1—37 行（全文） | `ddf89e92eea4191f68cbc7adde809445c473cb5dd163808b39d13455433dff8c` |

CSV 实算 SHA-256 与主包第 458 行声明一致。

### 2.2 覆盖统计

| 类别 | 主包定义数 | CSV 唯一引用数 | ID/逐镜覆盖 | 当前可直接进入主体资产节点 | 阻断数 |
|---|---:|---:|---:|---:|---:|
| 人物 identity | 7 | 通过 18 个 appearance snapshot 覆盖全部 7 类人物 | 7/7 | 1/7（牛满） | 6/7 |
| 人物 appearance snapshot | 18 | 18 | 18/18 | 7/18（均属牛满） | 11/18 |
| 场景 | 5 | 5 | 5/5 | 1/5 | 4/5 |
| 道具 | 6 | 通过 15 个 prop-state 在 CSV 中引用 | 6/6 均有定义及状态链 | 0/6 | 6/6 |
| 道具状态 | 18 | 15 | 15/18 | 0/18 | 18/18 |
| 逐镜键 | — | 40 个，全部唯一 | 40/40 | — | — |

未进入 CSV 的 3 个已定义道具状态为：`prop-state.ox-hairpin.broken.v0.1`、`prop-state.redemption-coins.scattered.v0.1`、`prop-state.future-lighter.held.v0.1`。CSV 使用原子 `.start/.end` 行表达变化，直接绑定的是变化前后静态状态；这 3 项不构成未声明 ID，但不能单独据此宣称已有对应主体状态图。

## 3. 人物主体覆盖矩阵

| 人物 | 稳定 identity ID | 状态/快照版本 | 来源 ID / 逐镜覆盖 | 可进入 GPT Image 主体资产节点 | 缺失/阻断项 |
|---|---|---|---|---|---|
| 牛满 | `identity.niu-man.v0.1` | `snapshot.niu-man.bound.v0.1`; `snapshot.niu-man.awakened-frozen.v0.1`; `snapshot.niu-man.awakened-restored.v0.1`; `snapshot.niu-man.awakened-controlled.v0.1`; `snapshot.niu-man.cost-felt.v0.1`; `snapshot.niu-man.cost-felt-late.v0.1`; `snapshot.niu-man.changed.v0.1` | 主包 source：场1—9；原文5—195行。CSV：S01—S15 的对应行 | **是，仅按 7 个已定义快照分别锁版** | 年龄范围未知；不得补年龄事实。现有稳定锚点与快照可见状态足以按上游字段进入，但节点必须保留未知，不得把外部道具/能力写入人物主体底板。 |
| **王二（必检样本）** | `identity.wang-er.v0.1` | `snapshot.wang-er.abuser.v0.1`; `snapshot.wang-er.frozen.v0.1`; `snapshot.wang-er.fear.v0.1`; `snapshot.wang-er.heat-damaged.v0.1` | 主包 source：场1—5；原文11—133行。CSV：abuser=S02A/S02B/S03/S03B/S04A.start/S04A.end/S04B.start/S04B.end；frozen=S05/S06A/S06B/S07A.start/S07A.end/S07B/S08A.start；fear=S08A.end/S08B/S09.start/S09.end/S10A.start/S10A.end；heat-damaged=S10B.start/S10B.end/S11A/S11B/S12A.start/S12A.end/S13A.start/S13A.end/S13B/S14A.start/S15A/S15B | **否（阻断）** | gender、age_range 均明确为未知；identity 仅有“体面衣着、兰花指、强行抬脸、跪地姿态”等锚点，缺少可锁定同一身份的脸部/体型定义。不得自行补性别、年龄、脸、体型或服装细节。受损版还必须继承同一身份，基础主体未锁定前不能锁 `heat-damaged`。 |
| 红瞳少女 | `identity.red-eye-girl.v0.1` | `snapshot.red-eye-girl.dragged.v0.1` | 主包 source：场6；原文145—147行。CSV：S12B-1 | **否（阻断）** | 快照明确“服装/年龄未知”；现有可见锚点不足以锁定可复用身份主体。 |
| **金纹少年（必检样本）** | `identity.gold-mark-boy.v0.1` | `snapshot.gold-mark-boy.chained.v0.1` | 主包 source：场6；原文148—149行。CSV：S12B-2 | **否（阻断）** | 快照明确“服装/年龄未知”；人物自身仅锁额间金纹及受约束/震动/抬眼状态。铁链必须由独立道具层绑定，不能补进人物底板；基础身份外观不足以锁版。 |
| 绿瞳少年 | `identity.green-eye-boy.v0.1` | `snapshot.green-eye-boy.exiled.v0.1` | 主包 source：场6；原文150—151行。CSV：S12B-3 | **否（阻断）** | 快照明确“服装/年龄未知”；基础身份外观不足以锁版。 |
| **未来年轻人（必检样本）** | `identity.future-young-person.v0.1` | `snapshot.future-person.smoking.v0.1` | 主包 source：场8；原文179—180行。CSV：S14B.start、S14B.end | **否（阻断）** | 快照明确“年龄/服装细节未知”；场景和火柴必须由外部资产层绑定。不能由“未来年轻人”名称自行推导具体年龄、性别、脸、体型或服装。 |
| 村民群体 | `identity.village-crowd.v0.1` | `snapshot.village-crowd.background.v0.1`; `snapshot.village-crowd.frozen.v0.1`; `snapshot.village-crowd.kneeling.v0.1` | 主包 source：场1—5；原文9—21、131—133行。CSV：S01—S15 对应群体行 | **否（阻断）** | 只有围观/低笑/冻结/分批跪地等群体动作状态，未定义群体构成与可复用主体外观；不得补成员数量、性别、年龄、脸、体型或服装。 |

## 4. 场景主体覆盖矩阵

| 场景 | scene ID | 状态/适用范围 | 来源 ID / CSV 覆盖 | 可进入 GPT Image 主体资产节点 | 缺失/阻断项 |
|---|---|---|---|---|---|
| 村口老槐树 | `scene.village-old-locust-tree.v0.1` | 场1—5、7—9；同一稳定轴线与地标 | 原文5—143、157—177、181—195行；CSV 34 行引用 | **是** | 只能使用主包已锁定的空间核心、轴线、地标、泥地与三月寒风；不得扩写建筑或村庄陈设。 |
| 集市 | `scene.market.placeholder.v0.1` | 场6.market | 剧本场6；原文145—147行；CSV S12B-1 | **否（阻断）** | ID 明确为 placeholder；具体时代、建筑、陈设未知。 |
| 地牢 | `scene.dungeon.placeholder.v0.1` | 场6.dungeon | 剧本场6；原文148—149行；CSV S12B-2 | **否（阻断）** | ID 明确为 placeholder；具体建筑结构、出口、人物面向、具体光源未知。 |
| 破庙 | `scene.ruined-temple.placeholder.v0.1` | 场6.temple | 剧本场6；原文150—151行；CSV S12B-3 | **否（阻断）** | ID 明确为 placeholder；庙宇具体形制未知。 |
| 未来街边 | `scene.future-street.placeholder.v0.1` | 场8.future | 剧本场8；原文179—185行；CSV S14B.start/S14B.end | **否（阻断）** | ID 明确为 placeholder；城市、年代、街道细节、天气、光线未知。 |

## 5. 道具主体覆盖矩阵

| 道具 | prop ID | 状态版本 | 来源 ID / CSV 覆盖 | 可进入 GPT Image 主体资产节点 | 缺失/阻断项 |
|---|---|---|---|---|---|
| 麻绳 | `prop.rope.v0.1` | `prop-state.rope.taut.v0.1`; `prop-state.rope.broken.v0.1` | 主包场1—3/Transition `tr.rope.break`；CSV S01—S08B 对应行 | **否（阻断）** | 有功能、位置与断裂链，但无可锁定材质/结构外观；不得补。 |
| 牛形木簪 | `prop.ox-hairpin.v0.1` | hidden→held→broken→mud 四版 | 主包场1—2/Transition `tr.hairpin.take/break/mud`；CSV 引用 hidden/held/mud | **否（阻断）** | 仅锁“簪头模糊小牛”；不足以锁完整主体外观。`broken` 已定义但 CSV 无独立静帧引用。 |
| 赎身铜钱 | `prop.redemption-coins.v0.1` | hidden→held→scattered→mud 四版 | 主包场1—2/Transition `tr.coins.take/scatter/mud`；CSV 引用 hidden/held/mud | **否（阻断）** | 无可锁定主体外观；`scattered` 已定义但 CSV 无独立静帧引用。 |
| 未来打火机 | `prop.future-lighter.v0.1` | absent→held→active→returned-pending→returned 五版 | 主包场4—9/Transition `tr.lighter.take/activate/return-pending/return-confirm`；CSV 引用 absent/active/returned-pending/returned | **否（阻断）** | 主包未提供足以锁定复用道具主体的完整外观；`held` 已定义但 CSV 无独立静帧引用。不得用“未来”补设计。 |
| 火柴 | `prop.match.v0.1` | `prop-state.match.unlit.v0.1`; `prop-state.match.lit.v0.1` | 主包场8/Transition `tr.match.light`；CSV S14B.start/S14B.end | **否（阻断）** | 只有普通替代物、未点燃/点燃状态，无可锁定主体外观；不得补火柴盒、材质或式样。 |
| 铁链 | `prop.chain.v0.1` | `prop-state.chain.locked.v0.1` | 剧本场6；原文148—149行；CSV S12B-2 | **否（阻断）** | 主包明确“具体材质和结构未知”；不能直接生成锁版主体。 |

## 6. 阻断清单与交接结论

1. **人物阻断 6/7**：王二、红瞳少女、金纹少年、绿瞳少年、未来年轻人、村民群体均缺少足以锁定复用身份主体的上游可见事实；不得用模型默认补齐。
2. **场景阻断 4/5**：四个 `.placeholder` 场景均带显式未知字段；只能作为结构化占位 ID 传递，不能直接产出锁版场景主体。
3. **道具阻断 6/6**：状态链完整，但主体外观定义不足；状态链完整不等于可生成主体底图。
4. **逐镜 ID 覆盖无断链**：40 个镜头键唯一；18/18 人物快照、5/5 场景均在 CSV 出现；CSV 中出现的 15 个道具状态均在主包声明。
5. **允许进入的当前范围**：牛满 1 个 identity 的 7 个快照，以及村口老槐树 1 个 scene；进入时仍必须保留未知字段并禁止补事实。其余项目只可进入节点的“输入校验/阻断返回”阶段，不可进入生成与锁版阶段。
6. **非本报告动作**：未生成图，未修改任何上游文件，未修改 GPT Image 主体资产 Skill。
