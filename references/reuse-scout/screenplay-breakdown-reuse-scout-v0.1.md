# 小说改剧本与剧本资产拆解复用侦察 v0.1

- 侦察日期：2026-08-31（UTC+08）
- 目标节点：`novel-to-screenplay`、`screenplay-breakdown / asset-extraction`
- OPC硬需求：人物/场景/道具的稳定身份与故事状态、来源追溯、连续性、有版本的结构化输出、可被AI漫剧后续节点直接消费。
- 核验口径：仓库/官网正文、GitHub API 元数据与文件树；“tests/examples”仅在确有文件或本机实际执行时记为有。GitHub `updated_at` 会被收藏等活动刷新，因此维护状态以 `pushed_at`/最新 commit 为主。

## 一页结论

**建议不是选一个项目整套搬入，而是组合复用：**

1. **输入标准与人工可读母稿：Fountain 1.1**；中文人名必须支持 `@角色名` 强制角色元素，场次使用 `#scene-id#`。[1][2]
2. **格式解析/互转内核：`wildwinter/screenplay-tools`**；优先复用其 Python `Script/Element` 中间模型、Fountain/FDX parser/writer。本机在正确工作目录实跑 **28/28 tests PASS**，是本次最强“可运行证据”。[3][4]
3. **production breakdown 词表、场景资产聚合与交互参考：`ScriptBreak`**；可借其 Fountain/FDX/PDF 场景切分、19类 production elements、bibles、timeline、stripboard/Day Out of Days 思路，但不要直接把其单文件前端当OPC核心库。[5][6]
4. **机器交换基线：OSF 2.1 的 production tag categories + scene dictionaries**；只借 schema 概念，不把停更 XML 直接定为OPC主格式。[7][8]
5. **小说→剧本生成策略：Dramatron 的层级生成（logline→characters/locations→beats→dialogue）**；只复用分层思想和提示编排，不复用其 notebook 作为生产服务。[9][10]
6. **CLI/JSON辅助：Meander**；可借 Fountain→JSON AST、FDX→Fountain、角色别名/台词统计，但 GPL-3.0 对闭源或非GPL分发有传染性风险，建议仅做进程边界工具或参考重写。[11][12]

**没有任何候选原生满足 OPC 的关键要求：**`identity base + story-state version`、道具持有人/状态有向链、能力 trigger/effect/cost、逐场来源跨度、改编操作追溯、跨镜头连续性断言、中文网文长上下文与AI漫剧资产绑定。可复用的是“解析与生产分类”，连续性与溯源仍必须由 OPC 自建。

## 候选总表（6个）

| 候选 | 定位 | URL / License | 维护状态（截至侦察日） | Tests / examples 核验 | 复用优先级 |
|---|---|---|---|---|---|
| Fountain 1.1 + 官方 Objective-C parser | 开放纯文本剧本语法、参考 parser/data model | https://fountain.io/syntax/；https://github.com/nyousefi/Fountain；MIT | 规范稳定但参考仓库陈旧；最新 commit 2015-03-31 | 官网有完整示例与下载样稿；Xcode unit tests/sample files；本机 Windows 未跑 Xcode tests | **A：输入/交换语法** |
| wildwinter/screenplay-tools | Fountain/FDX 多语言 parser、writer、格式无关 AST | https://github.com/wildwinter/screenplay-tools；MIT | 活跃；最新 commit 2026-01-05，未 archived | Python/C++/JS 多套 tests + 大量 fixtures；本机 Python `unittest` **28/28 PASS** | **A：解析内核** |
| wassermanproductions/scriptbreak | 本地 screenplay production breakdown、bibles、timeline、stripboard/MCP | https://github.com/wassermanproductions/scriptbreak；Apache-2.0 | 很活跃；最新 commit 2026-08-05，未 archived | 有 screenshots、release workflow、安装包/源码构建说明；仓库未发现自动化 test 文件 | **A-/B+：资产分类与产品参考** |
| severdia/Open-Screenplay-Format (OSF 2.1) | XML结构化剧本/前期制作交换格式 | https://github.com/severdia/Open-Screenplay-Format；MIT | **停滞**；最新 commit 2016-11-08；仓库未标 archived 但事实性 dormant | `OSF-2.1.xml` 本身是完整示例；无 tests/parser | **B：schema概念参考** |
| google-deepmind/dramatron | LLM层级式剧本共创 | https://github.com/google-deepmind/dramatron；软件 Apache-2.0、其他材料 CC-BY 4.0 | 低活跃；最新 commit 2024-07-16，未 archived | 可运行 Colab notebook 是唯一代码主体；无 test suite；LLM接口故意留空，需自行实现 `sample` | **B：改编编排思想** |
| lichendust/meander | Fountain生产文档 CLI、FDX转换、JSON data | https://github.com/lichendust/meander；GPL-3.0 | 活跃；最新 commit/tag 0.2.6 于 2026-02-21，未 archived | README/内置 help 有JSON示例；仓库未发现 `*_test.go` | **B-/C：CLI/AST参考，license慎用** |

> **排除项记录：`slow2342/n2s`。** 搜索索引曾显示“小说→结构化YAML剧本”、Apache-2.0、v0.1.0 与测试小说示例，但核验时 GitHub API 与 clone 均返回不存在/404，因此不能作为可复用依赖或可靠证据；仅可作为“市场上有人采用 YAML chapter→scene”弱信号，不列入候选。

## 逐项核验与可复用模块

### 1. Fountain 1.1 + 官方 parser：剧本输入标准层

**证据。** Fountain 规范明确 Scene Heading、Character、Dialogue、Action、Parenthetical、Transition、Section、Synopsis、Notes、scene numbers 等元素；强制角色语法 `@McCLANE` 特别适合非罗马文字；强制 Action `!` 能避免全大写误判。[1] 开发者页说明官方实现以 `FNScript`、`FNElement`、`FountainParser`、`FountainWriter` 构成通用数据模型，MIT，并包含 unit tests/sample files。[2] 官方仓库最新 commit 停在 2015-03-31，故应把它视为稳定参考实现，而非活跃依赖。[13]

**可复用。** 

- 将 Scene Heading/Action/Character/Dialogue/Parenthetical/Section/Synopsis/Note 映射为 OPC `scene/beat/dialogue/source_note` 基元。
- `#1A#` 场号可承载稳定 `scene_id` 的人类可读表示。
- Fountain Notes/Sections 可作为编辑层的非打印结构提示；但机器真值应另存 JSON/YAML sidecar。
- 强制语法 `@中文名`、`.场景标题`、`!动作` 可规避中文没有大小写导致的启发式失效。

**差距。** Fountain 只表达排版结构，不表达 production assets、人物状态、prop ownership、连续性或来源范围；不能把“动作文本里提到一个词”自动等同于“需建模资产”。中文剧本若不强制标记，角色识别规则基本不可用。

### 2. wildwinter/screenplay-tools：解析与格式归一化内核

**证据。** 项目用同一格式无关 `Script`/`Element` 模型支持 Fountain 和 Final Draft FDX 的读写，覆盖 Python、JavaScript、C#、C++，声明 UTF-8 支持；仓库有独立 `python/tests/fdx`、`python/tests/fountain` 及共享 fixtures。[3][4] GitHub API 显示 MIT、未 archived、最新 commit 2026-01-05。[14] 本机下载 `main` zip 后，从 `python/` 执行：

```text
python -m unittest discover -s tests -v
Ran 28 tests in 0.215s
OK
```

覆盖 FDX parse/write/round-trip、Fountain scene heading/action/character/dialogue/notes/sections/tags/UTF-8/writer 等。首次从仓库根目录执行时 23 项因测试写死相对路径 `../tests/...` 失败；切到其预期的 `python/` 目录后 28/28 通过。这是测试运行方式陷阱，不是 parser 逻辑失败。

**可复用。**

- `Fountain.Parser` 与 `FDX.Parser` 做输入适配器；统一到 `Script(titleEntries, elements)`。
- `Element` type/text/attributes/tags 作为 OPC ingest AST 的第一层，不直接当最终资产 schema。
- FDX round-trip tests 可转为 OPC 导入回归基线；UTF-8 fixture 可再扩展简中姓名、全角标点和无大小写角色标记。
- 可将 Python 实现 vendoring/依赖化，避免 ScriptBreak 1.6MB 单HTML的耦合。

**差距。** 它只解析剧本元素，不理解角色别名、intro description、prop状态、场景地理、能力规则、来源溯源。现有 test 也没有中文 Fountain、中文 slugline、跨场状态链测试，OPC 必须补。

### 3. ScriptBreak：production breakdown 与资产清单最接近的成功实现

**证据。** README 声明导入 `.fountain/.fdx/.pdf/.txt`，产生 scenes、characters、locations、props、shot lists、timeline、bibles、CSV/breakdown/prompt-pack exports，并以纯 JSON `.scriptbreak` 保存项目。[5] 源码可直接定位 `parseFountain`、`parseFDX`、slugline parser、场景 `characters/elements/shots`、元素聚合、bibles 与 project-look。自动标签同时使用分类词表和动作行中的大写 featured items；内置 production 类别包括 props、wardrobe、vehicles、VFX 等。[6] GitHub API 显示 Apache-2.0、未 archived、最新 commit 2026-08-05；该 commit 新增 shooting schedule、stripboard 与 cast Day Out of Days。[15]

**可复用。**

- **场景拆解 UI/数据形态：** `scene -> characters + location + elements[category] + shots`。
- **资产清单分类：** Cast、Extras、Props、Wardrobe、Vehicles、VFX/SFX、Animals、Sound、Set Dressing 等，可作为 OPC `asset_category` 初始受控词表。
- **bible思路：** characters/locations/hero props 的 canonical description；可迁移为 OPC identity base，但必须加版本、证据、状态引用。
- **跨场聚合：** element→scene indexes、人物出场 lanes、location/day-night/int-ext timeline、stripboard、Day Out of Days，可用于连续性可视化和拍摄/生成批次规划。
- **导出边界：** JSON 项目文件与 MCP 层可参考为 OPC node I/O，而不是复制 prompt-pack 内容。

**差距与风险。** 

- 主要业务逻辑集中在约 1.6MB 的 `src/index.html`，模块化和单元测试不足；仓库未发现自动化 tests。
- `bibles` 是可编辑描述，不是 `identity + state`；同一角色换装/受伤/年龄变化没有明确 state ID/transition cause/source。
- “大写名词+英语词表”对中文失效；中文没有大小写，分词、量词、别名、省略主语、古装称谓都需专门模型。
- 连续性主要是 presence/timeline，不是可验证 ledger；没有 prop holder/condition 链、能力成本、原文 span provenance。
- prompt packs 面向通用图片/视频生成，未锁定 15 秒漫剧容量、资产先生成后绑定、首尾帧/镜组一致性。

### 4. Open Screenplay Format 2.1：结构化剧本/production标签词典

**证据。** 仓库声明 OSF 2.1 是 application-independent、platform-agnostic 的 XML screenplay format，并面向 screenwriting/preproduction software。[7] 完整 `OSF-2.1.xml` 样例含 document info、段落/文本、locked scene/page numbers、characters、locations、sceneIntros、sceneTimes、revisions，以及 21 个 production `tagCategories`：Cast、Extras、Stunts、Vehicles、Props、Special Effects、Costumes、Makeup、Animals、Music、Sound、Set Dressing、Visual FX 等。[8] MIT；最新 commit 2016-11-08，无 tests/parser，事实性停滞。[16]

**可复用。**

- characters/locations/scene intro/time 受控字典；revision、locked scene/page numbers 的版本语义。
- production tag categories 可作为 OPC 资产分类的行业基线，并与 ScriptBreak 类别对齐。
- XML示例可用来反推 legacy import adapter 与 schema migration 测试。

**差距。** OSF 是文档格式而非知识图谱：tag类别不等于稳定资产实例，没有状态有向边、证据、scene binding的严格完整性约束。规范/仓库十年无维护，不能作为新系统唯一真值；建议只借概念并转成 OPC JSON Schema。

### 5. Dramatron：小说/故事到剧本的层级生成参考

**证据。** README 描述从 log line 出发，层级生成 character descriptions、plot points、location descriptions、dialogue，以 top-down hierarchy 保持长文本一致性；项目定位是人机共写，不是自治成片。[9] README 明示 Colab “unplugged”，调用方需自行实现 LLM `__init__`/`sample`；仓库树仅一个主要 notebook，无 tests；Apache-2.0 软件、其他材料 CC-BY 4.0，最新 commit 2024-07-16。[9][10][17]

**可复用。**

- `premise/logline → character/location bible → scene beats → dialogue` 的分层生成顺序。
- 每层先冻结高层约束再扩写低层文本，适合作为 OPC novel→screenplay 的 staged generation skeleton。
- 人工可编辑中间层与“不是自治全剧”的风险声明，适合转成自动质量闸门而非盲信单次LLM。

**差距。** 它从概念生成原创故事，不是忠实改编；没有 chapter/source spans、retain/compress/merge/reorder 操作、事实锁定、版权/provenance，也没有 production breakdown 或状态连续性。研究中专业编剧也评价输出可能 formulaic，更适合 world-building/alternatives；因此不能直接承担 OPC 小说改编主节点。[9]

### 6. Meander：Fountain→JSON 数据交换与生产统计

**证据。** Meander 是 Go 单二进制，提供 render/merge/gender/data/convert；`data` 生成包含 metadata、title、characters、content elements 的 JSON，character 结构含 name/gender/other_names/lines_spoken，section 含 type/text/scene_number/revision；`convert` 含 FDX XML→Fountain 解析。[11][12] GPL-3.0、未 archived、最新 commit/version 0.2.6 于 2026-02-21。[18] 仓库未发现 `*_test.go`，故“示例充分但自动化测试证据弱”。

**可复用。**

- JSON AST 的最小字段：`meta/title/characters/content[]`。
- 角色别名、台词数、scene number、revision；多文件 merge 可参考长篇/分集编译。
- CLI进程边界可作为格式转换辅助，降低与OPC服务代码的耦合。

**差距与license。** JSON仍是剧本元素树，不含 production assets/state/provenance；gender统计不适合作为人物身份真值。GPL-3.0 若链接/派生进入非GPL产品会造成分发义务，采用前需法律确认；安全路线是只调用独立CLI，或仅参考数据形态后自行实现。

## 可复用 schema / parser / continuity / asset 模块映射

| OPC所需模块 | 首选来源 | 能直接拿到什么 | OPC必须新增什么 |
|---|---|---|---|
| Fountain/FDX ingest | screenplay-tools | UTF-8 parser/writer、格式无关 Script/Element、FDX round-trip | 中文强制标记规范、PDF仅作为低可信输入、source span/byte offsets |
| 人类可读剧本标准 | Fountain 1.1 | scene/action/character/dialogue/note/section/scene number | sidecar manifest、稳定ID、事实/推断/未知分层 |
| production分类词典 | OSF 2.1 + ScriptBreak | Cast/Extras/Props/Costume/Makeup/Vehicles/VFX/SFX/Set Dressing等 | 中文同义词/本体、是否需制作判定、置信度与证据 |
| 场景级资产表 | ScriptBreak | scene→cast/location/elements/shots；全局聚合 | `asset_id/version_id`、required/optional、source binding、依赖图 |
| canonical bible | ScriptBreak + Dramatron | 角色/地点/hero prop描述，高层先行生成 | identity与appearance state分离；immutable anchors；版本和审批状态 |
| 连续性可视化 | ScriptBreak | timeline、character lanes、stripboard、Day Out of Days | 状态机与断言：holder/condition/wardrobe/injury/time/weather/orientation；transition cause |
| 机器交换 schema | OSF/Meander | XML dictionaries/tags；JSON AST | OPC JSON Schema、严格required/enum/$ref、schema version/migrations |
| 小说→剧本编排 | Dramatron | 层级生成与可编辑中间层 | 源文事实锁、逐scene provenance、改编操作日志、因果/信息权限/容量门 |

## 建议的 OPC 最小结构（基于候选补齐缺口）

```yaml
schema_version: opc.screenplay-assets/0.1
source_manifest:
  package_id: string
  source_documents:
    - id: string
      uri: string
      sha256: string
      rights_status: verified|unknown|blocked
scenes:
  - id: scene.xxx.v1
    screenplay_elements: []        # screenplay-tools AST映射
    source_spans: [{doc_id, start, end, quote_hash}]
    adaptation_ops: [retain|compress|merge|reorder|externalize|add|delete]
    bindings:
      characters: [{identity_id, state_id}]
      location: {asset_id, state_id}
      props: [{asset_id, state_id}]
assets:
  identities:
    - id: identity.xxx.v1
      kind: character|location|prop|ability
      canonical_name: string
      aliases: []
      invariant_anchors: []
      evidence: []
  states:
    - id: state.xxx.yyy.v1
      identity_id: identity.xxx.v1
      valid_scenes: []
      attributes: {}
      evidence: []
continuity:
  transitions:
    - from_state: string
      to_state: string
      cause_scene: string
      cause_element: string
      assertions: []
qc:
  orphan_assets: 0
  unresolved_transitions: 0
  source_coverage: 0.0
```

这不是某候选已有 schema，而是把 **screenplay-tools 的 AST、OSF/ScriptBreak 的 production categories、ScriptBreak 的场景绑定、OPC所需状态与溯源**拼成的建议契约。关键设计规则：

- 稳定实体与出现状态分开；禁止每次出现新建人物。
- 每场角色必须绑定 `identity_id + state_id`；外部道具/能力/地点分开绑定。
- 状态变化必须有 `from/to/cause/source`；同一静态画面不能同时绑定互斥状态。
- 来源必须到原文 span/hash，不只记“第几章”。
- asset category 与 asset instance 分开；“名词被提到”不自动等于“需要制作”。

## 与中文 AI 漫剧的系统性差距

1. **中文解析。** 英文工具依赖 uppercase character/featured prop、`INT./EXT.`、英文词表；中文必须采用强制 Fountain 标记或结构化编辑器输出，并增加中文场景头（内/外、日/夜）、NER、别名与代词消解。
2. **长网文改编而非原创。** 需要 chapter→scene 双向来源、锁定事实、删并挪外化记录、信息权限、因果与代价；Dramatron没有这些。
3. **资产“状态”而非静态 bible。** 漫剧生成最怕换脸、换装、伤势/道具跳变；所有候选至多有 canonical bible/presence timeline，没有严格版本状态图。
4. **能力与拟态表达。** 玄幻能力要有 owner/trigger/target/observable effect/cost/unknown boundary；古代叙述或比喻不能被LLM升级成新科学/超自然定律。候选无对应模型。
5. **生成媒介约束。** OPC还需15秒单元容量、角色同屏上限、先主体资产后分镜绑定、首/尾帧与参考图ID；production tools只面向真人拍摄或通用提示包。
6. **可追溯质量门。** 现成工具没有“无孤儿资产、无无因状态跳变、每场绑定有效ID、来源覆盖率”的自动 gate。
7. **中文文化与审查风险。** 服饰、朝代、民族、宗教、敏感历史与平台合规需独立证据/规则层，不能靠英文 breakdown 词典。

## 推荐落地顺序

### P0：两周内可做

1. 以 **screenplay-tools Python** 建 `Fountain/FDX -> normalized screenplay AST` adapter，并固定其 28 项 upstream tests；新增至少 20 项中文 fixtures。
2. 定义 `opc.screenplay/0.1` 与 `opc.screenplay-assets/0.1` JSON Schema；Fountain 只做人类可读镜像，不做唯一数据库。
3. 合并 **OSF + ScriptBreak** production categories，形成中英双语受控词表；每个提取项保留 source span/confidence/required_for_generation。
4. 实现 `identity/state/transition/scene_binding` 四张核心表及 orphan/transition/source-coverage gate。

### P1：随后

5. 参考 **Dramatron** 把小说改编拆成 fact freeze→character/location base→scene beats→action/dialogue；每层输出版本化中间物。
6. 参考 **ScriptBreak** 做 timeline/state lanes/prop ownership views，而不是先做 prompt pack。
7. 用固定中文小说与已批准剧本做端到端回归：原文→剧本→资产→连续性报告→下游分镜绑定，全程不需重读散文猜资产。

### 暂不建议

- 不以 OSF 2.1 XML 作为新系统主存储。
- 不把 ScriptBreak 单文件 UI 直接嵌入核心服务；抽取算法/词表思想并重写为可测试模块。
- 不将 Dramatron notebook 当自治小说改编器。
- 不在未确认 GPL 分发边界前链接 Meander 代码。
- 不依赖已404的 n2s。

## Sources

[1] Fountain 1.1 Syntax — https://fountain.io/syntax/

[2] Fountain Developer Resources — https://fountain.io/developers/

[3] wildwinter/screenplay-tools — https://github.com/wildwinter/screenplay-tools

[4] screenplay-tools tests tree — https://github.com/wildwinter/screenplay-tools/tree/main/python/tests

[5] wassermanproductions/scriptbreak — https://github.com/wassermanproductions/scriptbreak

[6] ScriptBreak source (parser/categories/bibles) — https://github.com/wassermanproductions/scriptbreak/blob/master/src/index.html

[7] severdia/Open-Screenplay-Format — https://github.com/severdia/Open-Screenplay-Format

[8] OSF 2.1 complete XML example — https://github.com/severdia/Open-Screenplay-Format/blob/master/OSF-2.1.xml

[9] google-deepmind/dramatron README — https://github.com/google-deepmind/dramatron

[10] Dramatron Colab — https://github.com/google-deepmind/dramatron/blob/main/colab/dramatron.ipynb

[11] lichendust/meander — https://github.com/lichendust/meander

[12] Meander JSON data structs/parser — https://github.com/lichendust/meander/blob/main/source/fountain.go

[13] Fountain latest commit API — https://api.github.com/repos/nyousefi/Fountain/commits?per_page=1

[14] screenplay-tools repository metadata API — https://api.github.com/repos/wildwinter/screenplay-tools

[15] ScriptBreak latest commit API — https://api.github.com/repos/wassermanproductions/scriptbreak/commits?per_page=1

[16] OSF latest commit API — https://api.github.com/repos/severdia/Open-Screenplay-Format/commits?per_page=1

[17] Dramatron latest commit API — https://api.github.com/repos/google-deepmind/dramatron/commits?per_page=1

[18] Meander latest commit API — https://api.github.com/repos/lichendust/meander/commits?per_page=1
