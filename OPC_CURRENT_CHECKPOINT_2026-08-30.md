# OPC Skill 当前执行断点 · 2026-08-30

> 用途：上下文压缩、网络中断、换会话或换机器后的唯一执行恢复入口。读取顺序：`DASHBOARD.md` → 本文件 → 当前候选产物。不得凭旧会话摘要覆盖本文件中的最新状态。

## 一、当前正确流水线

`创意/写作 → 小说改剧本 → 剧本资产提取 → 主体资产提示词/生成 → 锁定人物/场景/道具主体图 → 15秒分镜结构绑定资产ID → 以主体图为参考生成动态宫格故事板 → 拆关键帧/首尾帧 → H3/视频提示词 → 生视频`

硬边界：

- 资产提取先于正式分镜生产和GPT Image生图提示词。
- 分镜结构可以先设计，但主体图缺失时，宫格故事板只能标记`ASSET_BLOCKED`，不得凭文字重新设计人物、场景、道具。
- 宫格故事板实际出图必须引用已锁定主体图及版本ID。
- 节点不采访、不反问、不提供候选、不等待用户确认；内部自动质检，向下游交付唯一成品。

## 二、已创建的测试Skill

1. 小说改剧本：`D:\Hermes\skills\creative\novel-to-screenplay-opc-test\SKILL.md`
2. 剧本改15秒分镜：`D:\Hermes\skills\creative\screenplay-to-15s-storyboard-opc-test\SKILL.md`
3. 剧本资产提取：`D:\Hermes\skills\creative\screenplay-asset-extraction-opc-test\SKILL.md`

注意：Skill运行目录不在`xiaonan-memory` Git仓库内。换机器后不能只靠`git pull`推断Skill已安装；必须实查运行目录或从共享源安装。

## 三、小说改剧本状态

- 固定输入：`D:\Documents\我的文档\十二时辰_第一卷_01.md`
- 通过正文：`D:\Documents\我的文档\十二时辰_第一章_小说改编剧本_Skill测试版v0.3.md`
- 正文SHA-256：`c84057a6ee79ec709f56cb7691da53304ea0ae708bad4d128631335a194e8747`
- 回归报告：`D:\Hermes\xiaonan-memory\references\十二时辰_第一章_Skill回归报告_v0.3.md`
- 内容能力：`38/44`，11项全部≥3；A项事实全部保留；内容能力测试通过。
- 权属：未知，仅供内部测试，不得商业发布。
- 拟态表达门禁已加入：区分时代/叙述视角的近似命名、可观察现象、源内机制、未知和戏剧功能。
- “老了五十年”已还原为蓝火接触后的快速热损伤与组织变形外观；不表示真实年龄瞬间增加。
- 拟态检查清单：`references/小说改剧本_拟态表达还原检查清单_v0.1.md`

## 四、分镜Skill状态

- 第一章S01—S15结构链路已完成；各镜≤15秒、核心≤14秒。
- 已包含观众情绪起承转落、演员触发—行动—反应、声音来源/透视/进出/功能、动态宫格、无文字占位图、顶视角调度、状态ID和首尾接口。
- 情绪知识：`references/分镜节点情绪导演知识证据地图_v0.1.md`
- 样板文件位于`D:\Documents\我的文档\十二时辰_第一章_S*.md`。
- 分镜Skill已加入主体图门禁：主体图/版本缺失时只输出结构并标记`ASSET_BLOCKED`；生产级宫格故事板必须引用锁定主体图。

## 五、资产提取Skill当前状态

### 目标

将已通过剧本编译为人物、场景、道具、能力、完整人物快照、状态转移、来源、连续性和逐镜绑定；输出先于分镜/主体图/宫格故事板，不写提示词正文。

### 历史失败版本（均保留，不覆盖）

- v0.1：混用剧本场1—9与S镜号；绑定简称；异地场景字段不足。
- v0.2：仍有错误场次、非完整ID、状态链/ledger不闭合。
- v0.3：人物状态不是完整快照；多地点绑定靠排列；Transition不全；拟态记录不全；空间坐标不足。
- v0.4：快照有场次分支；逐镜绑定不够原子；Transition仍有缺口。
- v0.5：S08提前绑定打火机/蓝火；拟态旧快照；蓝火主链矛盾。
- v0.6：逐场表与CSV的S08真相冲突；S09首尾未原子化。
- v0.7：10个变化镜仍把互斥状态放同一行；S08两套真相；蓝火能力定义冲突。
- v0.8：人物快照内嵌外部道具/能力状态，与CSV冲突；场景映射遗漏。
- v0.9独立验收失败：快照仍内嵌外部资产（王二持有物件、金纹少年锁链、未来人场景/火柴）；蓝火多重定义；地牢“牢门”轴线无来源；Manifest缺回归补充材料。

### 当前资产提取回归（已通过）

- 最终主包：`D:\Documents\我的文档\十二时辰_第一章_剧本资产提取_Skill测试版v0.11.md`
- 逐镜CSV：`D:\Documents\我的文档\十二时辰_第一章_逐镜资产绑定_v0.11.csv`
- 独立验收：PASS；问题数0。
- 报告：`references/十二时辰_第一章_资产提取Skill回归报告_v0.11.md`
- 下一阶段：创建GPT Image主体资产提示词/生成Skill；先生成并锁定人物、场景、道具主体图，再由分镜绑定主体版本并生成宫格故事板。

### 历史断点说明

- 快照ID已从带道具名改为纯人物阶段名：
  - `snapshot.niu-man.awakened-frozen.v0.1`
  - `snapshot.niu-man.awakened-restored.v0.1`
  - `snapshot.niu-man.awakened-controlled.v0.1`
  - `snapshot.niu-man.cost-felt.v0.1`
  - `snapshot.niu-man.cost-felt-late.v0.1`
- 牛满快照正文已去除外部道具/能力状态，只保留人物可见外观、伤情、金纹、姿态和情绪。
- 外部道具/能力状态只应由CSV和Transition Records提供。
- S08B CSV已显式补`future-lighter.absent`与`blue-flame.absent`。
- S14/S15接口已明确蓝火保持extinguished；普通火柴只做跨镜匹配，不同帧、不同时空共存。

### v0.9下一步（恢复后立即做）

1. 扫描所有Appearance Snapshot，确保区块内没有`prop-state.*`、`ability-state.*`、道具名或场景名；特别检查王二“持有搜出物件”、金纹少年“锁链束缚”、未来年轻人“现代街边/持火柴”。这些应分别移到CSV的prop或scene列。
2. 将铁链创建为独立道具和状态：`prop.chain.v0.1`、`prop-state.chain.locked.v0.1`，绑定S12B-2。
3. 删除地牢无来源的“牢门”坐标；改为以石墙/锁链固定点构成稳定轴线，未知出口方向保持未知。
4. 统一蓝火唯一真相：Ability Asset、Prop/Ability state chain、Continuity Ledger、Transition Records必须全部为`absent→active→contact→active→extinguished`。
5. Source Manifest补登记：`D:\Documents\我的文档\十二时辰_第一章_小说改编剧本_回归补充材料_v0.3.md`及实际SHA-256。
6. 重算v0.9 CSV SHA-256并写回主包。
7. 运行机器审计：快照纯人物、CSV单行互斥状态=0、missing ID=0、非法场次=0、提示词污染=0、逐场/逐镜S08/S09真相一致。
8. 再派verifier独立验收；未PASS前不进入主体图生成。

## 六、图片生产顺序（用户最新纠正）

1. 资产提取列出所有人物、场景、道具主体及状态版本。
2. GPT Image主体资产Skill生成并锁定人物、场景、道具主体图。
3. 分镜结构绑定锁定的主体资产ID/版本。
4. 以主体图为参考生成具体动态宫格故事板。
5. 从宫格故事板拆独立关键帧、首帧、尾帧。
6. 再写H3/视频提示词并生视频。

## 七、待办优先级

1. 创建/测试GPT Image主体资产提示词/生成Skill。
2. 生成并锁定第一章人物、场景、道具主体图。
3. 分镜绑定锁定主体资产。
4. 使用主体图生成动态宫格故事板。
5. 拆关键帧/首尾帧。
6. 创建/测试MiniMax H3全能参考提示词Skill。
7. 再处理创作者候选证据补强；它不是当前生产链阻断项。

## 九、停机状态 · 2026-08-30 22:53

- 资产提取Skill第一章回归v0.11已独立PASS，问题数0。
- S01—S15分镜结构链已完成。
- 后台子代理0，进行中待办0，可以安全关机。
- 明日启动后不要重做v0.1—v0.10；直接从GPT Image主体资产Skill开始。
- 正确顺序：资产提取→主体图→锁定版本→分镜绑定→主体图参考宫格→关键帧→视频提示词。

## 八、恢复命令与核验

新会话：

```bash
cd D:/Hermes/xiaonan-memory
git pull origin main
```

然后读取：

- `D:/Hermes/xiaonan-memory/DASHBOARD.md`
- `D:/Hermes/xiaonan-memory/OPC_CURRENT_CHECKPOINT_2026-08-30.md`

核验本地Skill：

```bash
python D:/Hermes/skills/software-development/skill-library-maintenance/scripts/health_check.py
```

禁止根据旧todo的`in_progress`推断员工正在运行；必须调用delegate列表。禁止根据员工完成消息推断文件落地；必须检查文件存在、大小和内容。
