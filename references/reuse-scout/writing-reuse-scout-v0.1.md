# AI 小说 / 长篇写作工作流复用侦察 v0.1

- 侦察日期：2026-08-31（UTC+08）
- 目标：为 OPC「客户想法 → 小说 / 长篇写作」节点寻找真实、可运行、可复用实现。
- 重点：story bible、outline → draft、continuity checking、内部迭代 QC、第一次对外只交付一个最终成品。
- 结论先行：**以 Show Me The Story 的自动长篇闭环作主骨架，以 Novel OS 的结构化状态/确定性连续性引擎作硬门禁，以 NarraLume 的可恢复任务状态和证据化审稿作运行层；不要整仓照搬任何一个项目。**

## 一、推荐优先级

| 优先级 | 候选 | 与 OPC 的贴合度 | 最值得复制 | 主要缺口 |
|---|---|---:|---|---|
| P0 / 1 | [Nigh/show-me-the-story](https://github.com/Nigh/show-me-the-story) | 9/10 | 自动逐章生成、事实核查失败自动重写、叙事记忆、伏笔生命周期、全书优化、断点续作 | 默认仍暴露大纲/逐章审核；需改成隐藏运行并只交最终稿 |
| P0 / 2 | [mrigankad/Novel-OS](https://github.com/mrigankad/Novel-OS) | 8.5/10 | `StoryState`、结构化 agent 输出、确定性连续性检查、FAIL 阻断批准、context pack | 按章人工命令式；没有真正“一次提交→整本交付”控制器 |
| P1 / 3 | [abligail/narralume](https://github.com/abligail/narralume) | 8/10 | 长任务 steps/states/checkpoints、证据化审稿、候选变更与 canon 隔离、连续写作 | 产品哲学偏 human-in-the-loop；锁定事实冲突会暂停等人决定 |
| P1 / 4 | [john-paul-ruf/novel-engine](https://github.com/john-paul-ruf/novel-engine) | 7.5/10 | 15 步 pitch→publish、七角色编辑链、Voice Profile、真实整书/发布产物 | AGPL-3.0 不适合直接嵌入闭源 OPC；强人工协作倾向 |
| P2 / 5 | [Anshler/graphify-novel](https://github.com/Anshler/graphify-novel) | 6.5/10（作为模块 9/10） | 可直接移植的 `SKILL.md`、bible 文件布局、thread/timeline/character graph、跨章查询 | 不是生成器，没有 outline→draft、自动改稿循环或最终交付器 |

**建议落地顺序**：先复刻 P0-1 的单项目 headless 自动生产路径；第二步把 P0-2 的 `state_parser + story_state + continuity_engine` 嵌成每章硬门禁；第三步引入 P1-3 的 run/checkpoint/recovery 与 evidence finding；最后只吸收 P1-4 的角色职责和 P2-5 的轻量 bible schema。

---

## 二、候选详查

## 1. P0 — Show Me The Story

- **URL**：https://github.com/Nigh/show-me-the-story
- **License**：MIT；可复制、修改、再分发，保留版权和许可声明。[1]
- **维护状态**：高度活跃。GitHub API 在侦察时显示 154 commits、默认分支 `main`，最新 push 为 2026-08-30；发布页有 v3.0.3（2026-08-30），并提供 Windows/Linux/macOS 共 7 个构建资产。[1][2]
- **实际能力**：
  - 输入故事配置后生成全书大纲，再逐章写作；可开启自动确认一路写到底。
  - 结构化角色、世界观、组织、关系；每章 prompt 注入设定、全书大纲、近 5 章详细摘要、上一章结尾、活跃伏笔和叙事记忆。
  - 每章完成后自动摘要、事实核查；不通过最多自动重写 3 次，之后进入冲突处理。
  - 伏笔状态为 `planted → progressing → resolved/abandoned`，超期告警。
  - 完稿后执行全书诊断、一致性核查、生成工单、逐章最小化修订和 diff；最终导出单一 TXT/Markdown 全书。
  - 单 Go 二进制、Web UI、纯本地 JSON/Markdown、OpenAI-compatible API，支持中英文和断点恢复。[1][2]
- **运行 / 测试证据**：
  - v3.0.3 是可下载的跨平台 release；v3.0.1 发布说明专门修复事实核查冲突后的死锁，说明冲突路径不只是 README 设想。[2]
  - 154 commits、连续 v2.x/v3.x 发布以及 523 stars/59 forks（侦察时 GitHub API）显示已有真实使用反馈。
  - 本次未在本机完成 clone/build：并行 clone 时 GitHub 443 短暂不可达；因此**没有声称本地 E2E 通过**。当前证据等级是“源码、发布资产、release 修复记录可核验”，不是“本次实跑生成整本”。
- **可直接复制的模块**：
  1. `internal/story` 中 outline→chapter→summary→fact-check→retry 的领域流程。
  2. 叙事记忆的“章节确认后提取、修订时清除旧记忆并重提取、按 token 预算裁剪”。
  3. 伏笔生命周期、预计回收章和逾期检测。
  4. 全书优化的“诊断 → 一致性报告 → 可执行工单 → 按章最小修订”。
  5. 单任务锁、取消、SSE 进度、原子落盘和断点恢复。
  6. Go 标准库后端与 OpenAI-compatible client，适合作为独立 headless worker。
- **必须改造**：
  1. 把“审核大纲、逐章确认、事实冲突让用户处理”改为**内部自动决策/修订**；仅不可保守消解的锁定事实冲突才输出机器可读 blocked。
  2. UI 的大纲、草稿、工单、diff 都必须改为内部 artifact；OPC 第一次外显只允许一个 `novel`。
  3. 把事实核查从纯 LLM 判断升级为六门禁：故事事实、人物能动性、因果、节奏、可持续性、剧情连续性；每项需正文 evidence refs。
  4. 加入客户显式事实锁、推导/默认/决策 provenance，禁止模型在重写时“修掉”客户事实。
  5. 去掉或按输入选择“爽点/钩子”等网文倾向，保留多题材路由而非默认爽文化。
- **不可复制原因 / 边界**：
  - 可复制代码，但不能照搬其产品交互契约：它是作者工作台，不是一次提交、内部隐藏 QC、单一首交。
  - README 的模型质量/推荐章数属于作者估算，不应转成 OPC 的质量保证；仍须用固定回归夹具实测。

## 2. P0 — Novel OS

- **URL**：https://github.com/mrigankad/Novel-OS
- **License**：MIT。[3]
- **维护状态**：活跃但年轻。默认分支 `dev`，64 commits，GitHub API 显示最新 push 2026-08-09；侦察时 36 stars、12 forks，未归档。[3]
- **实际能力**：
  - 五角色：Architect（全书/章节规划）→ Scribe（正文）→ Editor（五种编辑模式）→ deterministic pre-check → Guardian（连续性）→ approve；另有 Curator 管风格。
  - agent 输出携带严格机器可解析更新块，经 `state_parser` 合并进 `story_state.json`。
  - 确定性连续性引擎检查 dormant/overdue threads、未回收伏笔、人物缺席/死亡状态、缺失章节文件、关系孤儿/矛盾/时间倒置、三章无推进的 stalled middle 等；`FAIL` 阻断 approve。
  - `context_pack` 做预算化上下文，`consequence` 预估修改波及，`compile_*` 产出 Markdown/DOCX/EPUB/HTML。[3]
- **运行 / 测试证据（本次实际执行）**：
  - 本机成功 clone `dev` 到临时目录，实测 commit：`1bd4b5725a8225462873571eb9f9d26f5496ae83`（2026-08-09，`feat(web): edit Codex entries from the studio`）。
  - 使用 `uv run --with-requirements requirements.txt --with-requirements requirements-dev.txt pytest -q`，**全部 386 项测试通过**（按 `pytest --collect-only -q` 逐文件计数求和；终端显示 100% 无失败）。测试覆盖 continuity exemptions、relationship continuity、context pack、state/API、compile、stall detector、consequence 等。
  - 这证明本地非 LLM 引擎与接口测试可跑；**没有调用付费/本地 LLM 生成整本小说**，所以不把 README 的“full-length”当成本次生成质量证据。
- **可直接复制的模块**：
  1. `core/state_manager.py` + `core/state_parser.py`：结构化状态落盘与 agent 输出合并。
  2. `core/continuity_engine.py`：低成本、可重复、无需 LLM 的硬检查。
  3. `core/stall_detector.py`：用剧情推进/人物发展/情绪/新信息/线程触达判断连续空转。
  4. `core/context_pack.py`：长篇上下文按关联度和预算打包。
  5. `agents/*/prompt.md` 的 OUTPUT CONTRACT、Guardian/Editor 分工。
  6. `core/compile_book.py`：批准章节只汇编为一个最终文稿。
- **必须改造**：
  1. 新增整书 orchestrator：从一次 customer idea 自动完成全书路径，而不是用户逐条 `plan/write/edit/validate/approve`。
  2. 失败门禁要自动生成定向 revision instruction，回到 Scribe/Editor 后重检，设最大轮次和 blocked 分支。
  3. 现有 deterministic checks 偏元数据完整性；补“客户事实锁、动机/知识/机会/代价、因果链、信息来源、章节衔接”的结构化证据。
  4. 禁止把 chapter draft、continuity report、候选路径外显；仅汇编过门章节。
  5. Architect 默认示例强调三幕/Deep POV/钩子，需改为输入驱动的结构、体裁、叙述距离，不可统一审美。
- **不可复制原因 / 边界**：
  - 可复制 MIT 代码；但仓库没有“一键整本、隐藏多轮 QC、唯一首交”的成品控制器。
  - 确定性检查只能发现已编码的不变量，无法证明文学质量或深层因果正确；必须与 LLM evidence review + 回归夹具合用。

## 3. P1 — NarraLume / 叙灯

- **URL**：https://github.com/abligail/narralume
- **License**：Apache-2.0；允许商用和修改，但分发修改文件需保留 notices，并注意专利条款。[4]
- **维护状态**：当前最活跃之一。2026-08-30 仍有提交；18 commits、104 stars/23 forks；v0.2.0 于 2026-08-21 发布，提供 5 个资产。Actions 页面有 17 次运行，最新 CI 与 release-readiness 均执行完成。[4][5]
- **实际能力**：
  - story bible 七区：author intent、outline、entities、canon、relationships、timeline、foreshadowing。
  - 章节/选区委托、连续写作、版本、评论、审稿 findings、revision candidates；AI 新事实/关系/时间线变化先作为候选，不静默进入 canon。
  - 长任务有 steps、states、checkpoints、run records，可离开页面再恢复；有 story-memory search、impact preview。
  - 可从 idea/import 到可交付 Markdown/TXT/DOCX/EPUB，并有项目 snapshot 和 SQLite backup。[4]
- **运行 / 测试证据**：
  - 官方提交信息明确记录 `npm run verify`（format、lint、typecheck、**640/649 tests**、evidence eval 5/5、licenses、build）和 Playwright E2E **9 passed / 3 skipped by design**；Actions 页面对应 CI 有运行记录。[4][5]
  - 有 hosted demo、跨平台 release 和两个版本标签。[4][5]
  - 本次未本地 npm install/跑测试；上述数字是可定位到 commit/CI 的上游证据，非本次复跑。
- **可直接复制的模块**：
  1. run center 的 step/state/checkpoint/error/recovery 数据模型。
  2. review finding 带 evidence、误报标记、revision candidate 的审稿闭环。
  3. canon change candidate 与 accepted canon 分离的双层状态。
  4. 长任务可暂停、重试、恢复而不损坏正文的事务边界。
  5. author intent + seven-section bible schema。
- **必须改造**：
  1. 当前“边界确认、逐章 review、冲突时等作者决定”要换成 OPC 的 no-question/no-wait conservative resolution。
  2. 自动驾驶要隐藏所有中间候选，仅在最终 pass 时提交一个 artifact；内部仍保留 run record 供审计。
  3. 接受/拒绝机制改为系统决策器：锁定事实不可改，推导与默认可回滚，无法消解则 blocked。
  4. 从“写作工具优先、AI 辅助”裁剪成 headless skill/runtime，避免带入整套 Web/SQLite 产品复杂度。
- **不可复制原因 / 边界**：
  - Apache-2.0 可复用，但 NOTICE/修改声明与依赖许可证必须保留。
  - 人机协作是其核心安全边界；直接照搬会违背 OPC 一次提交和不追问要求。

## 4. P1 — Novel Engine

- **URL**：https://github.com/john-paul-ruf/novel-engine
- **License**：AGPL-3.0-only。[6]
- **维护状态**：成熟度证据强。521 commits、17 tags；最新 release v0.9.4（2026-07-24），release 有 11 个资产；Actions 页面有 75 次 workflow runs。README 最新提交为 2026-07-29。[6][7]
- **实际能力**：
  - 15 步 pitch→publish，七个 AI 角色覆盖 story coach、ghostwriter、first reader、developmental editor、task master、copy editor、publisher。
  - 生成 story pitch、scaffold、scene outline、story bible、逐章 draft、编辑和 DOCX/EPUB 成品；支持 Claude/Codex/Ollama/OpenAI-compatible。
  - Voice Profile 约束文风；系列级 shared story bible 注入七角色上下文。[6][7]
- **运行 / 测试证据**：
  - 官方提供跨平台安装 release、演示视频、Build & Release workflows。
  - README 列出 10 本由该系统制作并上架 Amazon 的书和独立 evaluation 页面；这是目前候选中最强的“真实整书产物”证据，但**不等于独立文学质量认证**。[6][7]
  - 源码 `package.json` 有 Vitest/coverage 脚本；本次未本地 clone/build，未复跑测试。
- **可直接复制的模块**：
  1. 15 步阶段划分和七角色职责说明，可作为 OPC 内部 stage/agent spec 的参考。
  2. story scaffold / scene outline / story bible 模板与 Voice Profile 思路。
  3. 全书装配和出版格式交付路径。
  4. “first reader → developmental edit → task execution → copy edit”分层 QC 顺序。
- **必须改造**：
  1. 将 15 步中需要用户参与的采访、确认、手工编辑改成内部自主分支选择。
  2. 增加可机器判定的 continuity gates 和正文 evidence refs；不能只靠编辑角色自然语言评价。
  3. 将发布/查询信等非 OPC 小说节点职责全部剥离。
  4. 输出必须从工作台多版本改成单一最终正文 + 最小审计记录。
- **不可复制原因 / 边界**：
  - **AGPL-3.0-only 是硬风险**：若把其代码直接集成并通过网络提供服务，通常会触发向用户提供对应源码的义务。除非 OPC 整体兼容 AGPL，建议只借鉴思想/接口、不要复制实现；如要用，先做法律审查。
  - “10 本上架”只能证明跑通出版链路，不能证明跨题材稳定、无逻辑漏洞或首交可用。

## 5. P2 — graphify-novel

- **URL**：https://github.com/Anshler/graphify-novel
- **License**：MIT。[8]
- **维护状态**：小而清晰。41 commits，最新 push 2026-04-16；侦察时 65 stars/17 forks，未归档。仓库主体几乎就是 README + 可安装的 `SKILL.md`。[8][9]
- **实际能力**：
  - 从 premise 或既有章节批量初始化 bible。
  - bible 结构包括 `premise.md`、`timeline.md`、characters（YAML state + arc log）、threads（状态与 payoff）、world；知识图谱保存实体关系。
  - `review` 对章节查矛盾、连续性缺口、未解 setup；`update` 在 review 后更新 bible；`status/query/path/thread` 提供跨章检索。
  - `draft/` 与已接受 `chapters/` 隔离，review 不直接写 bible，符合“候选不污染 canon”。[8][9]
- **运行 / 测试证据**：
  - `SKILL.md` 是完整、可直接安装到 coding assistant 的命令工作流；仓库给出 premise 初始化、from-chapters batching、review/update/status/query 的实际命令契约。[9]
  - 没有应用测试套件、release、生成小说样本或 outline→draft 运行证据；因此只能评为**连续性/记忆插件**，不能算完整小说 agent。
- **可直接复制的模块**：
  1. `SKILL.md` 的 bible 文件 schema 和命令编排。
  2. `draft/` 排除、review 只提案、update 才进入事实源的写入边界。
  3. timeline event IDs、character arc log、thread payoff、open-thread status。
  4. 大量既有章节按 batch 子 agent 扫描，避免单上下文溢出。
- **必须改造**：
  1. 接入 OPC 的 outline→scene/chapter→draft 生成器和自动 revision loop。
  2. 把 `review` 结果变成结构化 gate（severity、evidence body refs、repair target），通过后自动 `update`。
  3. 移除依赖交互式 coding assistant 的“提示用户粘贴/确认”，改为无交互文件/对象 API。
  4. 增加唯一 final assembler 和 completed/blocked 分支。
- **不可复制原因 / 边界**：
  - MIT 许可无实质障碍；真正不可直接当成 OPC 节点的原因是它**不写小说**，也没有隐式 QC 后的单一最终交付。
  - 底层依赖另一个 `graphify` skill；若复制其图谱能力，需单独核查该依赖的许可证、安装链和稳定性。

---

## 三、能力矩阵（以源码/文档中可定位功能为准）

| 候选 | Story bible | Outline→draft | Continuity | 迭代隐藏 QC | Single final delivery | 证据强度 |
|---|---|---|---|---|---|---|
| Show Me The Story | 强：设定+关系+伏笔+叙事记忆 | 强：全书大纲→自动逐章 | 强：每章事实核查+全书一致性 | **接近**：自动重写≤3次、全书工单；但 UI 可见 | 有全书导出；默认过程非隐藏 | A-（release/源码；未本机 E2E） |
| Novel OS | 强：StoryState/Codex | 强：Architect→Scribe | 强：确定性+Guardian，FAIL gate | 中：有 edit/validate，但需外层自动回环 | compile approved chapters | **A（本机 386 tests pass）** |
| NarraLume | 强：七区 bible | 中强：quick/continuous creation | 强：evidence review+canon candidates | 中：任务可恢复，但重人审 | 有 export；默认候选可见 | A-（CI/E2E/release 上游证据） |
| Novel Engine | 强：book/series bible | 强：15-step pitch→publish | 中：多编辑角色，确定性门禁证据较弱 | 强但偏协作式 | 强：DOCX/EPUB/真实出版物 | A-（release/10 books；未复跑） |
| graphify-novel | 强：文件 bible+graph | **无** | 强：graph review/query | 弱：review→人工/update | **无** | B（可安装 skill；无测试/产物） |

> “隐藏 QC”按 OPC 口径严格判断：内部可多轮，但客户在第一次看到正文前不能看到候选稿、问题单或要求中途确认。五个候选没有一个原样完全满足；Show Me The Story 最接近自动闭环，Novel OS 最适合补硬门禁。

## 四、建议的复用架构

```text
CustomerIdea
  → InputLock / provenance（OPC 自建）
  → StoryBible + Outline
      - schema：graphify-novel / NarraLume
      - 自动 outline：Show Me The Story
  → for each chapter
      → ContextPack（Novel OS）
      → Draft（Show Me The Story / Novel OS Scribe）
      → Fact & State Extraction
      → Deterministic Continuity（Novel OS）
      → LLM Evidence Gates（OPC 六门禁）
      → targeted revision → re-check（隐藏；有最大轮次）
      → accept chapter state / memory / foreshadowing
  → Full-book diagnosis + work orders（Show Me The Story）
  → cross-book gate → targeted chapter revisions
  → assemble approved chapters（Novel OS compile）
  → exactly one external novel OR machine-readable blocked
  → run/checkpoint/provenance audit（NarraLume 思路；不对客户暴露中间稿）
```

### 最小可复制包

1. **从 Novel OS 复制（MIT）**：`state_manager.py`、`state_parser.py`、`continuity_engine.py`、`stall_detector.py`、`context_pack.py`、agent output contracts、compile pipeline。
2. **从 Show Me The Story 复制（MIT）**：chapter generation orchestration、fact-check retry、narrative memory、foreshadowing lifecycle、full-book postprocess tickets、atomic persistence。
3. **从 graphify-novel 复制（MIT）**：轻量 bible 目录/schema、timeline/thread/arc IDs、draft 与 canon 隔离。
4. **从 NarraLume 借鉴或按 Apache-2.0 合规复制**：task state/checkpoint/recovery、evidence findings、canon candidate acceptance model。
5. **Novel Engine 只借鉴设计，不复制代码**：七角色职责、Voice Profile、15-stage ordering；规避 AGPL 传染范围。

## 五、进入实现前必须做的验证

1. 固定五类题材回归：现实慢燃、温暖喜剧、推理悬疑、 speculative noir、群像/非线性；检查不会统一爽文化。
2. 对每个候选模块做 provenance 清点，保存原 LICENSE/NOTICE；Novel Engine 不进入复制清单。
3. 用故障注入测试六门禁：时间矛盾、主角靠外援、核心反转无铺垫、连续空转、重复扩写、章节跳接。
4. 验证失败稿从未进入 external artifact；只允许 `completed: one novel` 或 `blocked: zero novel`。
5. 至少跑三种模型（高端闭源、性价比 API、本地开源），记录首交通过率、平均修订轮次、token/章、误报率。
6. 长篇压力测试不只看“装得下”：30/50/80 章分别注入早期人物承诺、道具状态、伏笔回收和知识边界探针。

---

## Sources

1. [Nigh/show-me-the-story repository / README](https://github.com/Nigh/show-me-the-story)
2. [Show Me The Story releases](https://github.com/Nigh/show-me-the-story/releases)
3. [mrigankad/Novel-OS repository / README](https://github.com/mrigankad/Novel-OS)
4. [abligail/narralume repository / README](https://github.com/abligail/narralume)
5. [NarraLume Actions and releases](https://github.com/abligail/narralume/actions) · [releases](https://github.com/abligail/narralume/releases)
6. [john-paul-ruf/novel-engine repository / README](https://github.com/john-paul-ruf/novel-engine)
7. [Novel Engine Actions and releases](https://github.com/john-paul-ruf/novel-engine/actions) · [releases](https://github.com/john-paul-ruf/novel-engine/releases)
8. [Anshler/graphify-novel repository / README](https://github.com/Anshler/graphify-novel)
9. [graphify-novel SKILL.md](https://github.com/Anshler/graphify-novel/blob/master/SKILL.md)

## 证据说明

- 维护日期、commit/star/fork 数来自 2026-08-31 对 GitHub API/仓库页的侦察快照，之后会变化。
- “本次实跑”仅指 Novel OS 的本地 clone 与 386 项 pytest；其余项目均明确标为上游 CI/release/demo/样本证据，未把 README 自述冒充本机实测。
- GitHub API 后续请求遇到匿名 rate limit，且并行 clone 时出现短暂 443 连接失败；已改用 GitHub 仓库页、Actions、Releases 交叉核验，不影响已完成的 Novel OS 实跑证据。