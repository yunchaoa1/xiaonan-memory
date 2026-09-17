---
name: opc-creative-skill-authoring
description: Use when authoring OPC manga-drama node skills.
version: 0.1.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [opc, ai-manga, skill-authoring, screenplay, storyboard, image-prompt, minimax-h3]
    related_skills: [short-drama-story-engine, shot-language, prompt-master-pipeline, image-prompt, scene-image-generation]
---

# OPC 漫剧创作 Skill 制作总类

## Overview

本技能用于制作 OPC 漫剧创作应用中的专业节点 Skill。目标不是把多个能力塞进一个万能提示词，而是把传统影视、动画生产和 AI 执行经验转译为边界清楚、输入明确、输出可审阅、可复用、可回归测试的单节点能力。

第一批节点包括：写作、小说改剧本、剧本改 15 秒内分镜脚本、GPT Image 系列生图提示词、MiniMax H3 全能参考提示词。每个节点只完成自己的专业转换，不越权改写上游意图或替代下游节点。

## Scope Boundary

只负责 Skill 的研究、编写、测试、修订和定稿。不要扩展到 OPC 的产品架构、前后端、数据库、节点画布、任务队列、计费、存储或模型接入实现。

Skill 内部可以定义输入、输出、版本、引用和质量门禁，因为这些是专业交接的必要信息；它们不是产品工程实现方案。

## Non-Negotiable Workflow

1. **锁定节点职责**：先写“负责什么”和“不负责什么”。如果一个节点同时写故事、拆镜、设计资产和调用模型，先拆分职责。
2. **建立证据地图**：为规则标记法规/正式行业协议、官方模型资料、院校/教材方法、软件行为、本机实测、项目规则或创作经验。只有有证据的规则才能成为硬门禁。
3. **定义输入**：列出必填资料、可选资料、来源版本、用户锁定项和未知项。缺资料时报告缺项，不擅自补设定。
4. **定义输出**：同时给出机器可读结构和用户可读结果。输出必须包含来源、变更、风险和待确认项。
5. **分离硬门禁与软诊断**：格式、范围、引用完整性、因果断裂、连续性冲突和模型参数合法性可做硬门禁；审美、节奏偏好、风格选择和“模型更听哪种写法”只能做软诊断，除非项目实测反复证明。
6. **建立真实回归样例**：使用固定原文、固定输入和固定验收表。先生成测试版，再审查、修订、重跑，比较前后变化。
7. **独立验收**：创作者不得同时担任最终质检。验收必须能指出具体事实、字段、场次、画面或状态，不接受“整体不错”作为通过依据。
8. **定稿门禁**：只有权威依据已记录、输入输出稳定、失败路径可诊断、回归样例通过且没有一票否决项，才称为定稿版。
9. **委派产物核验**：子代理的完成报告不是完成证据。收到报告后必须核对目标文件是否存在、是否可读、内容是否完整，并检查路径、字节数、关键字段和测试输出；核验失败时将任务保持为未完成，不得进入验收或向下游推进。
10. **失败后收缩任务**：长任务超时、截断或未落地产物时，先保留失败事实，再把任务缩小为可独立验证的单个文件或小样本，重新执行并通过独立 QC 后再扩大范围。
11. **分层输入边界**：写作入口是 OPC 唯一接受客户外部创意的节点；它可接收一句话、人物关系、世界观、片段、情绪命题或混合输入，并自主发散、丰富和收束为唯一小说。小说输出后，下游节点才进入封闭边界，只读取明确版本小说、已验收上游产物和当前 Skill 规则。不能用下游的“封闭输入”误伤写作入口。
12. **经验蒸馏而非样本移植**：回顾历史会话和既有作品时，提炼灵感转化、人物推导、因果审计、逻辑卡点、回退简化、信息差和修订方法；逐条区分客户明确要求、共同推导、已验证经验、待测假设和项目专属设定。具体角色、道具、世界观和剧情不得升级为通用规则。
13. **证据层分开验收**：文档结构 PASS、静态 fixture/preflight PASS、真实模型运行/媒体 QC/锁版 PASS 是三个不同结论。静态预检通过不能上推为图片生成或完整运行通过；必须分别记录 API 响应、解码元数据、人工 QC、确认和唯一锁版证据。
14. **代理交付必须回读**：代理的完成摘要不是证据。收到结果后核验目标文件存在、内容完整、关键字段、字节数/行数和实际测试输出；报告生成早于依赖产物时，按时间点识别并重新复审，不沿用过时的缺失结论。
15. **同文件单写者**：并行提高效率时按职责和文件拆分任务；同一 `SKILL.md` 只允许一个执行者写入，测试工程、资产审计和 verifier 只写各自独立产物，制作代理不得兼任最终验收。
16. **黑匣子与测试分层**：先在节点外用固定样例真实生成、人工审图并修订规则；规则通过测试后，才封装为 Skill。Skill 是当前维度的一次性单功能生成工艺，只读取正式上游版本和自身规则，生成对应唯一产物。下游媒体 Skill 不内置自检、候选筛选、重试、修图、锁版、状态机、失败裁决或测试报告；验收、版本编排和客户局部修改均属于节点外的平台/测试层。不要把“正式运行只生成一次”误写成节点内的 QC/失败工作流。
17. **写前六门禁优先**：正式写作前至少检查 `story_facts | character_agency | causality | pacing | sustainability | plot_continuity`。任一门禁未达阈值时停在结构层修复，不生成正文。真实回归必须记录客户提交数、中途参与数、内部稿外露数、首次外部成品数及六门禁证据；静态契约存在不能替代专项 fixture 实跑。
18. **硬期限先冻结可执行 MVP**：当用户给出次日或明确下班前期限，立即停止非阻断研究，先锁两条最短可测链、固定样例、逐节点文件契约和验收标准。优先交付“真实可解析/可回读的小样本＋明确 `NOT_RUN`/`MODEL_BLOCKED` 分支”，不得用研究报告、全量设计或静态文档冒充可测试版本。
19. **成熟底座优先，OPC只补专属层**：通用解析、时间线、状态恢复和内容寻址资产库先侦察成熟实现，并用许可证、维护状态、本机测试和可移植模块四项筛选。已验证的典型组合是 Fountain＋screenplay-tools（剧本AST）、OpenTimelineIO（镜头时间线）、DVC式内容寻址（资产版本）；OPC自建 provenance、identity/state/transition、连续性、QC和lock，不重复造通用底座。
20. **模型接口与聊天Provider隔离**：GPT Image等付费媒体节点使用独立provider、endpoint、credential scope和输出目录，不覆盖Hermes当前聊天模型或第三方兼容站配置。ChatGPT/Codex OAuth不能被默认视作图像API额度；在官方key、计费、模型权限和一次低成本烟测齐全前，节点只能输出完整request manifest与真实阻断状态。
21. **截断批次按产物矩阵恢复**：并行批次遇到503/524/iteration cap/402余额断时，不整体重跑。先逐目标检查文件矩阵；完整项回读关键字段和真实执行证据后标PASS，缺失项缩成“单目录/单文件/一至三镜”重派。代理摘要中的`completed`不覆盖文件不存在或测试缺失事实。**402/429 实测（2026-09-08《十二时辰》17章批量）**：余额断时多数产物已落盘（子代理先写文件后写总结，被打断的只是总结段——9章批次402中断后8章文件完整）；恢复=目录清单对比目标清单只补缺失章+删除产物目录里的子代理临时文件（`_XX_json_check.json`/`_XX_自评.json`），不留中间物。整卷批量组织细节（命名/并行/单章成本/验收断言）见 `references/batch-chapter-execution.md`。
22. **冻结已通过 Skill**：测试通过的 Skill 一律冻结，除非用户明确说“要改”。下游节点出问题（漂移、人物/文字污染、一致性失败），只能在**当前出问题的 Skill 内部**解决，绝不回头修改已通过的上游 Skill 的输出契约来“配合”下游。已通过阶段的产物是冻结输入，不是可以回退重做的变量。改错方向时，先撤销越界修改、删除无效实验产物，再重新对齐边界；不要把已经验证通过的节点重新打开。
23. **先改 Skill 再测试**：测试的目的是验证 Skill 自身能力，不是验证场外推演逻辑。正确顺序是“先更新 Skill 正文与其调用的提示词/参考模板 → 再用同一正式上游输入跑一次生成 → 节点外人工审图”。不要在测试层先另做一套空间表、关系表或逻辑再喂给 Skill——那样测到的是场外逻辑，不是 Skill。用户给出的“先更新skill再测试，少走一步”就是这个意思。
24. **节点 Skill 单一生成形态（2026-09-04 凡哥实战纠偏）**：
   - 节点使命=一次生成唯一产物，节点没有第二次机会——第二次修改机会只留给客户。节点外的一切（验收、版本编排、清理、回归）不写进节点 Skill。
   - **skill 正文禁止出现检查形态词**：`self-check / QC / 复核 / inspect / score / accept / reject / retry` 这些概念词本身就会诱发模型自检重试（实战：家场景图被节点自检重试 8 次）。连 Boundary 里 “It does not self-check/retry...” 的否定列举也是概念泄漏源，应改成纯生成描述（“读上游+规则→生成一次→交付”）。
   - 门禁写成**生成规则形态**：写“生成时逐条对齐源文线索，对不齐就写裁定行”，不写“生成后检查漏项→判 FAIL”。
   - 平台没有另一个 Skill 约束节点——规则只进节点 Skill 本身；发现漏洞就补本节点 Skill，不新增环境级 Skill 去“约束节点”（对平台零约束力）。
   - **改 Skill → 同一回合立即重跑验证**（原子动作）：每次修改节点 Skill 后，下一个动作必须是按新 Skill 重跑该节点，验证“新规则有没有在产物中生效”。修订前启动的运行不算数；中间不允许插任何其他动作。
   - 2026-09-04 定稿的提取/生图新规则（道具三要素、配饰边界、场景合并、画风锁定迭代链、宫格边框稳定约束、One-Shot）细节见 `references/single-generation-lessons-2026-09-04.md`。

25. **规则必须内联进节点 SKILL.md 正文（2026-09-04 镜头语言丢失实战）**：related_skills 只是元数据引用，**黑盒节点执行时只加载自己的 SKILL.md，相关 skill 的方法论进不了节点**。凡哥实战：shot-language skill 有完整镜头语言决策规则（情感→景别速查/切镜动机清单/景别变化要够大/全片景别弧线），但分镜 skill 只把它列在 related_skills + 正文留一句抽象的"close views carry emotional peak"——子代理据此产出 29 镜全片中景平铺（特写 0/全景 0/镜内切镜 1），凡哥问"镜头语言完全抛掷脑后了？"。修复=把决策规则**整体内联**进节点 SKILL.md（分镜 skill 补 Shot Language Decision Rules：景别六档+情感速查表+切镜动机 1-5+弧线设计），同回合重跑后景别曲线恢复（特写 6/全景 1/镜内切镜 7 镜）。**检查节点 skill 是否只"引用"了方法论而没有内联，是 authoring 时的必查项**。
26. **宫格数=切镜数，不是"把切镜全拆掉"（2026-09-04 凡哥纠正）**：正反打类镜间切镜可以拆成独立镜（A 方案拆镜），但**镜内切镜**（同一叙事单元内机位切换，如中景推近切特写、情绪点切近景）要**保留在镜内**，该镜 `grid_count`=镜内切镜数（每切镜一个关键帧格），`grid_reason` 逐格写清对应画面。无镜内切镜的镜=单图（grid=1）。凡哥原话："没有切镜时只需要参考一张图就可以了，有切镜时需要切镜时的关键帧"。实战：S02「门缝帽檐首见→摘帽对视」镜卡自写"对视切近景有动机"却 grid=1——切镜被单图吞了；判据=逐镜问"这镜里有几次机位切换"，分镜包应保留切镜证据（如 cut_motivation 字段）而非靠拆镜消灭。

OPC 采用分层信息边界，不能把“唯一入口的客户想法”和“下游生产节点的封闭输入”混为一谈。

### Layer 0：写作入口节点

写作 Skill 是 OPC 唯一接受客户外部创意的最开始节点。它可以接收客户想法，并允许想法采用多样格式，例如一句话灵感、人物/关系、世界观设定、场景片段、情绪命题、类型偏好、现实观察、已有片段或混合素材。写作 Skill 负责识别意图、补齐创作结构、发散多个可能方向、选择最有生命力且可持续的创作路径，并直接产出唯一的小说成品及其来源/创作记录；不把所有作品压成同一种爽文口味。

写作 Skill 内部可以调用当前 Skill 已锁定的方法、已蒸馏的创作经验和经过验证的默认值来丰富客户想法，但不得把其他项目的角色、剧情、聊天补充或未授权材料偷偷移植进当前作品。客户没有提供的关键创作取舍，由 Skill 按内部规则自主完成，不通过提问把一键流程停住。

### Layer 1：小说及下游节点

写作 Skill 输出小说后，小说成为后续小说改剧本及生产链的核心源文件。下游节点的运行时唯一合法信息源为：

1. 写作节点输出的原始小说及明确版本；
2. 流程内上游节点已经验收的结构化产物；
3. 当前节点 Skill 中已经锁定的规则、默认值和输出契约。

下游运行时不得读取或采纳聊天补充、人工场外解释、网络资料、临时口头设定、其他项目资料或未验收草稿；不得把这些内容静默并入成品。缺少必要信息时，按已验证默认值处理，或输出机器可识别的缺项/阻断状态，不能向用户提问来补齐。

外部资料、历史创作会话和两部既有小说的过程经验，只能在 Skill 制作与验证阶段被审计、蒸馏为明确的通用方法；它们不是下游生产节点的隐式运行时输入。

每个 OPC Skill 至少定义：

- `purpose`：本节点唯一专业目的；
- `not_responsible_for`：明确越界行为；
- `required_inputs`：没有它不能可靠工作的资料；
- `optional_inputs`：可增强结果但缺失不阻断的资料；
- `locked_fields`：不得被模型静默修改的内容；
- `outputs`：结构化结果、可读结果、来源和风险；
- `provenance`：每项重要产物来自哪一版输入、哪条规则或哪次运行；
- `hard_gates`：失败即退回；
- `soft_diagnostics`：给建议但不冒充硬标准；
- `human_confirmation`：必须由用户确认的创作取舍；
- `regression_fixture`：用于重复测试的真实样例。

不要用一个大段自由文本替代所有字段。文本仍可作为最终阅读稿，但重要对象必须能被单独核对。

## Evidence Discipline

采用保守证据分级：

- **A**：法规、行业协议、政府/监管文件、模型官方文档与源码、正式奖项/平台原始记录；
- **B**：电影院校、行业协会、正式出版物、头部工作室公开管线和正式深度访谈；
- **C**：成熟软件文档、案例和经过交叉验证的行业实践；
- **P**：OPC 项目自己的生产约束，例如单次生成时长或故事板输出格式；
- **E**：个人经验和模型猜测，只能作为待测建议。

不要把人物知名度、作品热度或一段营销文案当成方法证据。学习知名导演/编剧时，不模仿在世创作者的个人风格，只提炼能被测试的通用方法，并记录个人贡献边界。

详细规则见 `references/evidence-and-validation.md`。本轮写作入口、GPT Image主体资产与委派验收的可复用细节见 `references/opc-regression-lessons-2026-08-31.md`。硬期限下的MVP收缩、成熟底座复用、媒体Provider隔离和截断批次恢复见 `references/emergency-mvp-and-reuse.md`。

## Cross-Node Rules

### Story and screenplay

小说改剧本不是缩写，也不是把旁白改成角色说话。它应识别核心命题、人物关系和关键因果，把心理、说明、回忆和抽象设定转成可见、可听、可表演的戏剧行动，并保留删改、合并、重排和新增的溯源。

剧本节点负责“发生什么、谁要什么、谁阻碍谁、选择造成什么结果”；它不提前替导演决定所有景别、运镜或模型提示词。

### Storyboard and image constraints

故事板采用按关键画面状态动态决定宫格数的多宫格模式，不固定 4 格或 9 格。每格必须对应一个可检查的状态；如果关键状态过多，应先检查镜头是否超载并拆镜。宫格数的产品口径（凡哥 2026-09-04）：**宫格数=切镜数**——不切镜的镜只用一张参考图（同一画面禁止多图控制，多图反而干扰视频走向）；有镜内切镜的镜按切镜数给关键帧（见第 26 条）。

故事板同时输出：

- 无文字的多宫格视觉故事板；
- 无文字、无编号、无名称的占位/调度图；
- 无文字的动作引导图。

约束图片只表达几何、主体关系和运动线。身份、动作含义、时序、情绪和叙事目的写入配套生图或生视频提示词。图片提供几何/运动约束，提示词提供语义/时序约束。

空间位置使用主角或主要主体自身的上下左右前后；纯场景先确定空间核心及其朝向。禁止用“画面左边/右边”作为跨格空间坐标。

多宫格一致性还必须考虑唯一母版、场景拓扑、资产版本、进入/变化/退出状态、相机透视、相邻重叠锚点、逐格增量编辑、变化预算、候选筛选和独立 QC。详见 `references/storyboard-consistency.md`。

### Character asset bundles

人物不是一个名字或一张图，而是：

> 身份母版 + 剧情状态版本 + 可复用资产合集。

剧本或分镜提到人物时，必须检查年龄、服装、发型、妆容/素颜、伤痕/污渍、携带道具、场景和状态起止范围。每种变化都要有来源、原因、适用场次、允许变化项和必须保持项。

身份母版保持脸型、五官比例、体型、核心识别特征和基础声音身份；状态版本承载年龄、服装、发型、妆容和剧情造成的临时变化。不能把所有维度任意组合，必须区分已确认组合、允许组合和禁止组合。

角色状态规则见 `references/character-asset-bundles.md`。

## GPT Image Skill Boundary

GPT Image 系列生图 Skill 只把已确认的人物、场景、道具、故事板关键画面和参考资产需求编译为图像生成任务。它不改变剧情、不重新拆分镜、不替视频模型设计运动、不把 z-image/Qwen 的专属规则直接套入 GPT Image。

“GPT Image 2”若未被官方模型目录核实，不得写死为正式模型 ID；使用可核验的 `model_id`，把用户称呼、官方型号和运行时可用型号分开记录。

## MiniMax H3 Skill Boundary

H3 Skill 必须区分云 API、ComfyUI Partner Nodes、本地 Native Nodes 和 AIMixer Director 的行为与提示词方言。不要把云 API 的引用写法、本地 tokenizer 的引用写法和插件自动补标签行为混为一个规则。

提示词编译、素材绑定、生成执行和结果 QC 是不同职责。生成成功不等于素材绑定正确、媒体可解码、声画同步或创作意图完成。

生视频节点的产品输入形态=**汉语镜头卡**（全中文可编辑字段：内容走向/台词/出场人物带参考维度/场景/音色参考/镜头中文选项/氛围；点【生成】后台才自动转 H3 六段，客户不知道底层模型）——字段规范、转换层边界与验收结论见 `references/hanshu-card-input-design.md`。

## Writing Entry Contract Lessons

写作入口与下游转换节点使用不同契约，不得套用同一套封闭输入规则：

1. **唯一开放入口**：写作节点允许客户想法作为唯一外部创意输入，接受一句话、关键词、人物关系、世界观、场景片段、情绪命题、已有文字、表格/JSON或混合载荷；历史会话、网络和其他项目仍不是运行时创意来源。
2. **内部发散、外部唯一**：内部至少比较题材表达、关系、冲突、结构、声音和节奏；只保留简短审计记录，最终仅交一个 selected 路径和一份小说正文，禁止把候选正文交给客户。
3. **不要统一口味**：固定夹具必须成对测试明显不同的题材、叙事声音和节奏，验证温情慢燃、悬疑锋利、群像、喜剧等不会被统一压成爽文、豪门、升级或固定反转模板。
4. **互斥输出分支**：`completed` 与 `blocked` 必须由显式 discriminator 区分并互斥穷尽。completed 交一份完整小说；blocked 不得伪造标题、梗概、样章或空正文，只交机器可读 blockage 对象及来源/决策记录。
5. **来源与决策逐项可查**：至少区分 `user_fact | inference | default | decision | risk`，每项带稳定 ID、`source_ref`、`body_ref`、`rule_ref`、状态和关联引用；禁止把推导或默认伪装成客户事实。
6. **缺项不靠追问补齐**：非关键缺项用经过测试的保守默认或推导，并显式登记；显式事实冲突只能做兼容它们的最窄解释，无法在锁定约束内完成时走 blocked 分支，不得静默删除事实。
7. **经验蒸馏不等于样本移植**：既有小说、短剧故事、剧本和历史会话只能在制作/验证阶段形成带出处、证据等级、适用条件、反例、排除项和状态的方法条目。`validated_for_testing` 只表示可进入新输入测试；`candidate_not_runtime` 不得进入运行规则。
8. **文体身份先审计**：小说、短剧故事、完整剧本必须分栏使用。短剧或剧本可提供人物动机、信息差、证据线与多线汇合的测试候选，但不能冒充小说正样例或直接证明长篇小说能力。
9. **一键式按客户体验验收**：客户只提交一次，生成过程中不参与选择、确认或修改；系统内部可以在对外前进行路径推演、事实表/时间线/人物动机/因果链/剧情连续性/伏笔责任检查，并修正未展示的工作稿。客户第一次看见的小说必须已达到“可用底稿”底线：锁定事实不冲突、人物行为有动机、信息取得有来源、因果连续、剧情无断点、关键伏笔有兑现或明确延后责任。文风惊艳度、意象密度和商业节奏可作为交付后由客户继续精雕的软项，不能用它们掩盖逻辑硬伤。
10. **内部返工不等于客户改稿**：禁止把漏洞初稿先交给客户再要求其补结构；内部失败稿、门禁报告、候选方案和返工轮次均不外露。客户收到合格底稿后可以自由修改、续写或精雕，这不违反一键式流程。

## Subject Asset Sufficiency Lessons

主体资产节点必须把“ID/状态链存在”与“足以生成可复用母版”分开：

- 人物需有足够稳定可见事实来锁定身份；性别、年龄、脸、体型、服装等明确未知时，不得依靠模型默认补全。
- 场景 `.placeholder` 或缺拓扑/结构时，在模型调用前返回 `ASSET_BLOCKED`。
- 道具拥有完整状态链不代表其几何、材质和结构足以生成主体母版。
- 外部道具、场景和能力保持独立绑定，不能并入人物底板。
- 固定 preflight 应逐资产输出 expected/actual、typed status、reason code、affected fields 和来源哈希；“预期阻断被正确触发”属于测试 PASS，但该资产仍不可生成。
- 状态必须分层：`preflight_result`、`node_result`、`lifecycle_status`、machine/human QC、`lock_status`。只有真实模型响应、图片解码与元数据核验、独立人工可见事实 QC、human confirmation、机器审计闭环和唯一 lock record 全部存在，才可称运行 PASS。

## Testing Standard

测试必须包含：

1. 固定原文/固定分镜/固定资产输入；
2. 原作事实清单或节点输入清单；
3. 结构化输出检查；
4. 硬伤和一票否决检查；
5. 0-4 或项目明确的评分量表；
6. 失败原因与定向返工建议；
7. 第一版与修订版的差异对照；
8. 独立质检结论。

小说改剧本的首个回归样例使用《十二时辰》第一卷第一章《慢下来的时间》，重点检查牛满、母簪、赎身钱、时间停止、蓝火反击、寿数代价、十二神位、龙悬念和未来打火机回收是否保留，并检查它们是否被转成可拍摄行动。

不要因为文字顺滑、画面漂亮或文件已生成就判定通过。必须验证节点是否完成了自己的专业职责。

## Execution Lessons From OPC Regression Work

### Prefer a small executable sample before a batch

When a delegated long-form node task times out or is truncated, do not trust its completion claim. Verify the target artifact exists and is complete. If it is absent, stop repeating the same large task and create a one-shot or three-shot sample with the same final fields. Pass the sample through independent QC before expanding the batch.

For long-running work, a completed child must be followed immediately by one of: artifact verification, independent QC, or the next bounded child task. Never leave a todo marked `in_progress` while no worker is running. A worker's report is not evidence; file existence, readable content, hashes, counts, and test output are evidence.

### Emotion-directed storyboard fields are mandatory

A production storyboard shot is not merely a screenplay excerpt. Each shot must declare:

- audience emotion target and emotional start/turn/landing;
- the minimum information the viewer must learn and what remains withheld;
- shot scale, camera position, and one primary movement with an information/emotion reason;
- a playable actor trigger -> action -> reaction -> end state, never an abstract instruction such as “act sad”;
- dialogue and sound events with speaker/source, diegetic/off-screen/subjective perspective, entry, exit, attention hierarchy, and emotional function;
- the cut point at an information or emotional state change;
- first/core/tail frame states, continuity interface, risk, and fallback split.

Treat the 15-second beat template as a project hypothesis until sample-tested. Use the smallest grid that represents all key visual states; if the states or objectives overload the shot, split at a causal boundary rather than lengthening the prompt.

### Continuity is a typed state graph

For every cross-shot handoff, record stable identity, story state, prop state, ability/time state, spatial-core orientation, axis, positions, eyelines, sound state, and accepted tail-to-next-first-frame interface. Use explicit state IDs and transitions such as `hidden -> held -> broken -> mud` or `flowing -> stopped`; prose-only continuity notes are insufficient for a production-ready package.

Separate no-text placeholder/dispatch diagrams from visual references. The diagram may contain only fixed symbols, spatial outlines, motion lines, eyelines, and camera geometry. Do not use screen-left/screen-right as world geography; establish the subject or spatial core's own orientation first.

## Common Pitfalls

1. **把产品架构当成 Skill 任务**：只定义 Skill 的专业边界，不继续设计前后端或节点系统。
2. **万能 Skill 越权**：写作、改剧本、分镜、资产和提示词必须保持交接边界。
3. **把经验冒充行业铁律**：规则必须带证据等级；没有来源的建议进入待测试区。
4. **把导演风格写进模板**：只学习可迁移的方法，不模仿个人风格。
5. **先写正文后找依据**：先建事实清单、方法证据和验收表。
6. **固定宫格数**：宫格数由关键状态数量和镜头容量决定。
7. **约束图出现文字**：占位图、调度图和动作引导图不得出现文字、编号、人物名或说明。
8. **用画面左右描述空间**：跨镜头必须使用主体自身方向或空间核心坐标。
9. **每格从零重绘**：连续画面优先引用批准母版和上一格的批准结果，并只改变声明过的变量。
10. **人物资产只做一张立绘**：年龄、服装、发型、妆容和剧情状态必须形成资产合集。
11. **状态任意组合**：状态组合必须有剧情或设计依据，不能把所有维度随意笛卡尔积。
12. **自动值静默覆盖用户锁定内容**：上游变更只产生影响提示和候选稿，不覆盖批准版本。
13. **自动筛选替代人工判断**：相似度和结构检测只能辅助，不能替代左右手、空间拓扑、剧情状态和审美 QC。
14. **把文件生成当能力证明**：Skill 必须经真实样例、评分量表和独立复审验证。
15. **地址或来源有矛盾时直接执行**：先停在只读核对阶段，向用户确认后再修改或安装；本条适用于 Skill 研究中发现来源冲突的情况。
16. **模板含匿名固定形状导致跨视角漂移**：场景模板图里任何未命名的白色/占位固定块，都会让图像模型在不同机位把它自由解释成衣柜、书桌、架子、柜子等不同物体，并可能把沙发换墙。锚点必须是模板自身确实可见、有唯一身份的地标；模板里没有的门、厨房、餐桌、电视、书架不能作为锚点，也不能被主体节点凭空补造。若提示词锚点法反复漂移，说明纯提示词到了上限，应评估显式3D空间真值（Blender blockout 等），不要继续堆“不要漂移”的排除词。
17. **把未通过的方案写成已验证工作流**：跨视角一致性若最终靠提示词只改善概率、未达几何保证，就如实记为“到达提示词上限、待3D真值”，不得把连续失败的尝试包装成可靠方法写进 Skill。

## Verification Checklist

- [ ] 节点唯一职责和禁区明确
- [ ] 每条硬规则有 A/B/C/P 证据或已标记为待测
- [ ] 输入、输出、锁定项、未知项和来源版本完整
- [ ] 硬门禁与软诊断分开
- [ ] 角色、场景、道具引用可追溯
- [ ] 故事板宫格数由关键状态决定
- [ ] 约束图片无文字，语义与时序写在配套提示词
- [ ] 空间使用主体自身方向或空间核心坐标
- [ ] 人物状态包含年龄、服装、发型、妆容和场次范围
- [ ] 失败有可读错误和定向修复建议
- [ ] 固定样例回归测试完成
- [ ] 创作者自审与独立质检分离
- [ ] 修订前后差异可说明
- [ ] 新技能未与现有技能重复堆叠
