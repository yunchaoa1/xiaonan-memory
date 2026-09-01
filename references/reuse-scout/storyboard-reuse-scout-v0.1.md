# 分镜 / Shot Planning / Storyboard / 连续性复用侦察 v0.1

- 侦察时间：2026-08-31（UTC+08:00）
- 目标：为 OPC 一键漫剧 Skill 的“剧本 → 镜头 / 分镜 / 故事板 / 连续性”节点寻找可复用实现
- 结论先行：**用 OTIO 做时间线交换骨架；用自有 `OPCShot` schema 承载导演字段与连续性台账；借鉴 Kitsu 的 sequence/shot/casting 实体关系；Blender Storytools 只作为可选 3D blocking 适配器；Story2Board 只做可替换的视觉一致性后端。Wonder Unit Storyboarder 与 Adobe Firefly 只能当产品/交互参照，不能复制实现。**

## 1. 候选总表

| 候选 | 类型与 URL | License（已核实） | 维护状态（截至侦察日） | 可运行 / 成功证据 | 复用判定 |
|---|---|---|---|---|---|
| **OpenTimelineIO (OTIO)** | 开放标准 + Python/C++ SDK；<https://github.com/AcademySoftwareFoundation/OpenTimelineIO> | Apache-2.0[1] | 活跃；GitHub API 显示非 archived，最新提交 `bc5fe2d7`（2026-08-07）；PyPI 有 Windows cp311 wheel[3] | 仓库含 examples/tests/CI；本机新 venv 安装 `opentimelineio==0.18.1`，成功写入并回读含 1 个 4 秒 Clip 与自定义 camera/axis/character_versions metadata 的 `.otio` 文件 | **A：立即采用**。直接用核心 schema、时间数学、序列化和 adapter 机制 |
| **Blender Storytools** | Blender 5+ 故事板/Grease Pencil 插件；<https://github.com/Pullusb/storytools> | GPL-3.0[4] | 活跃；非 archived；release `3.1.0`（2026-02-28），最新提交 `a159808d`（2026-08-07）；Blender 官方扩展平台可安装[5] | README 给出 Blender 内直接安装路径，并展示 camera gizmo、相机前建绘制对象、自动关键帧等可执行功能；但本机未安装 Blender 5，未做运行烟测 | **B：做边界适配器**。复用 camera/blocking/Grease Pencil 工作流；不要把 GPL 代码并入宽松许可核心 |
| **Wonder Unit Storyboarder / Shot Generator** | Electron 故事板应用 + 3D Shot Generator；<https://github.com/wonderunit/storyboarder> | **无 LICENSE 文件，package.json 也无 license 字段**；不能因公开仓库推定可复制 | 偏停滞；非 archived，但 release `v2.1.0` 为 2020-09-03，默认分支最后提交为 2022-06-30；仓库 `pushed_at` 2024-03-17 | README 展示 Fountain 导入、绘板、animatic、导出；package scripts 含 `start:shot-generator` 与 Mocha/Electron 测试入口；官网仍提供下载与 Shot Generator 产品演示[6][7] | **C：只借鉴交互/schema 思路，不拷代码**。许可证缺失是硬阻断 |
| **Kitsu + kitsu-cli/Gazu** | 动画制作管理平台与 API/CLI；<https://github.com/cgwire/kitsu>、<https://github.com/cgwire/kitsu-cli> | Kitsu AGPL-3.0[8]；CLI 仓库当前未发现 LICENSE 文件，须在采用前补做法律确认 | Kitsu 活跃；release `v1.0.58`（2026-08-28），最新提交 `f398fec6`（2026-08-28） | CLI 文档给出 `pip install kitsu-cli`、创建 sequence/shot、asset casting、task/preview 的完整命令，并默认输出 JSON，明确面向脚本和 AI agents[9] | **A-/B：优先照搬实体关系，谨慎复用代码**。可直接采用 sequence→shot→casting→task→preview 的数据模型；若集成 AGPL 服务需隔离部署并履行许可证 |
| **Story2Board** | 训练免调的一致性故事板生成；<https://github.com/DavidDinkevich/Story2Board> | MIT（仓库 LICENSE 已核实）[10]；但底模 FLUX.1-dev 权重另受其模型许可约束 | 研究原型；非 archived；最后提交 `92ef1107`（2025-08-22），无 release | README 提供 Linux/Python 3.12/CUDA 12 安装与 `main.py` 具体样例；输出图片和逐 panel prompt；2025-08-21 修复过遗漏的 LPA 行。论文/项目展示 LPA + RAVM 和 Rich Storyboard Benchmark[10][11] | **B：模型层可插拔改造**。复用 LPA/RAVM 算法与 benchmark 思路，不让其成为核心 schema 依赖 |
| **Adobe Firefly Boards** | 商业闭源在线产品；<https://www.adobe.com/products/firefly/features/storyboard.html> | 商业条款，非开源 | Adobe 在线产品，持续运营（具体版本/提交不可审计） | 官方页面展示脚本/提示词→panel、参考图、remix、跨 panel 连贯、协作、JPEG/PNG/MP4 导出[12] | **D：不可复制**。仅作为功能验收基线；若接入只能走官方产品/API与商业条款 |

> 证据等级说明：OTIO 为“本机实际执行”；其余为“官方仓库命令、测试入口、release/提交或官方产品演示”。Blender/GPU/Kitsu 服务依赖较重，本轮未把“文档可运行”冒充“本机已跑通”。

## 2. 每个候选真正可移植的模块

### 2.1 OTIO：时间线骨架，不是导演分镜数据库

**可直接照搬**

1. `Timeline → Stack/Tracks → Track → Clip/Gap/Transition` 组合模型。
2. `RationalTime` / `TimeRange` 的帧率安全时间计算，避免 float 秒数漂移。
3. `ExternalReference` / `ImageSequenceReference` 关联故事板帧、音频、预览视频；`source_range` 表示实际使用区间。[2]
4. `Marker` 表达对白点、动作触发点、转折点、QC 警告；`metadata` 承载 OPC 扩展。
5. JSON 序列化、schema 版本与 adapter 插件模式；可导向 NLE，而不把 OPC 锁死在某个剪辑软件。[1][2]

**不能只靠 OTIO 的部分**

OTIO 是 editorial timeline，不原生定义镜头高度、焦距、180°轴线、人物站位、视线、服装版本、道具归属或连续性状态。应把这些定义为稳定的 `metadata.opc`，同时在独立 `OPCShot` JSON 中保留规范化字段；OTIO 是交换/播放视图，不应成为唯一真源。

**本机烟测结果**

```text
安装：opentimelineio==0.18.1（Windows / Python 3.11 wheel）
写入：Timeline(name=OPC) / Track(kind=Video) / Clip(name=SH001)
时长：96 frames @ 24fps = 4.0s
metadata：camera=CU, axis=A, character_versions=[hero-v3]
回读：成功，字段完整
文件：D:\Temp\opc-smoke.otio
```

### 2.2 Blender Storytools：把二维 board 与三维 blocking 连接起来

**可移植模块**

- “相机前创建 Grease Pencil drawing”与 drawing-to-camera parenting。
- camera/object 的平移、纵深、旋转、缩放 gizmo；所有变换尊重 autokey，天然可形成 blocking 关键帧。[4]
- camera view 内构图、镜头切换、可视化相机运动；适合把 `OPCShot.camera` 与 `blocking` 转成 `.blend` previs。
- 适配器可输出：人物占位 primitive、摄影机、焦距/传感器、起止站位、运动轨迹、Grease Pencil panel。

**改造边界**

- 核心 Skill 只生成中立 JSON；单独 GPL 插件/脚本读取 JSON 并构建 Blender scene。
- 不要让 `.blend` 成为连续性唯一真源；回写 camera transform、actor transform、rendered board URL 即可。
- Storypencil 是 Blender VSE/scene 同步思路的知名先例，但官方旧文档明确提到 scene synchronization 可能失败；因此此处优先选维护更活跃、模块更清楚的 Storytools，而不是只列 Storypencil 名字。

### 2.3 Storyboarder：可借鉴的 UX 和数据语义，不可复制代码

**值得 clean-room 重做的模块**

- Fountain screenplay → scene/board 的入口。
- board 顺序、时长、对白/动作文本与 animatic playback。
- 3D Shot Generator 的最小场景：camera + actors + props + lights；参数化改机位而非每次重画。
- board revision / change tracking、导出 PDF/GIF/视频/图像序列的产品路径。[6][7]

**硬限制**

仓库没有 LICENSE，npm manifest 也没有 license；默认版权保留。可以观察公开行为、定义兼容导入器或 clean-room schema，但**不能复制源码、素材或私有 `.storyboarder` 实现细节**。项目维护也不足以作为 OPC 核心依赖。

### 2.4 Kitsu：连续性台账最有价值的是实体图

**可直接照搬的 schema/算法思想**

```text
Project
  └─ Episode
      └─ Sequence
          └─ Shot
              ├─ Casting(Character/Prop/Set + version)
              ├─ Tasks(Storyboard/Layout/Animation/QC)
              ├─ Preview/Thumbnail
              └─ Status/Review/Comment
```

Kitsu 明确要求 shot 隶属 sequence，并支持 shot/sequence 的 casting、任务状态和 preview；CLI 又把这些暴露成 JSON 命令，适合 agent 自动化。[8][9]

**OPC 应增加的连续性扩展**

- `continuity_in` / `continuity_out`：人物位置、朝向、视线、服装、伤妆、手持物、场景状态。
- `asset_binding`：角色/场景/道具的 immutable version id，禁止“同上一镜”。
- `actual_tail_frame_ref`：生成完成后用真实尾帧覆盖计划尾帧，下一镜只读已批准版本。
- `axis_id`、`screen_direction`、`eyeline_target` 与校验器。
- `revision`、`approval_status`、`supersedes`，防止旧 panel 混入新 animatic。

**许可证策略**

实体关系和接口思想可以自行实现；若直接修改/网络部署 Kitsu，应按 AGPL 评估源代码提供义务。CLI 仓库许可证信息不完整，未确认前不 vendoring。

### 2.5 Story2Board：视觉一致性算法后端

**可移植算法**

- **Latent Panel Anchoring (LPA)**：多个 panel 共享参考 latent，稳定主体身份。
- **Reciprocal Attention Value Mixing (RAVM)**：寻找参考/目标 panel 之间双向强注意 token 对，软混合 value，在保持身份时允许背景、动作和构图变化。[10][11]
- 自由故事先由 LLM 拆为 grounded panel prompts，再进入图像模型；其 benchmark 不只测人脸相似，还测 layout diversity、background-grounded storytelling、consistency。

**必须改造**

- 当前入口围绕“单一 main subject + reference top panel + 若干 bottom panels”，而 OPC 需要多角色、服装/道具状态、正反打、轴线与首尾帧接口。
- 把 renderer 定义为 `StoryboardRenderer` 插件：输入 `OPCShot[] + AssetBindings + ReferencePanels`，输出 panel、seed、模型版本、prompt log、identity/continuity metrics。
- LPA/RAVM 只属于图像模型层；不要把 FLUX latent 或 attention token 泄漏进通用 shot schema。
- Windows 未官方测试，CUDA 12 / Python 3.12 / 大模型权重成本高；应保留云模型或其他本地扩散模型替换口。

### 2.6 Adobe Firefly Boards：商业基准而非代码来源

可把其公开功能转成 OPC 的验收项：脚本/文本生成 panel、上传参考图、remix 单镜、跨 panel 维持角色/环境/灯光、协作评论、重排、导出单帧或整段 MP4。[12] 但实现、模型、连续性算法与内部 schema 均不可审计和复制；没有官方稳定 API 证据时，不应把 GUI 自动化当生产依赖。

## 3. 推荐的 OPC 最小 schema（v0.1）

```yaml
project_id: opc-demo
fps: 24
aspect_ratio: "9:16"
shots:
  - shot_id: EP01-SQ010-SH0010
    sequence_id: EP01-SQ010
    narrative_function: reveal
    duration_frames: 192
    core_end_frame: 168
    dialogue: [{speaker_asset_id: char.hero.v3, text: "……", in: 32, out: 120}]
    assets:
      characters: [{id: char.hero.v3, costume: costume.hero.school.v2}]
      props: [{id: prop.letter.v1, owner: char.hero.v3, hand: right}]
      set: set.classroom.day.v4
    camera:
      shot_size: CU
      lens_mm: 50
      height_m: 1.55
      yaw_pitch_roll: [0, -3, 0]
      movement: {type: push_in, start: [0,-3,1.55], end: [0,-2.4,1.55]}
    blocking:
      axis_id: axis-A
      actors: [{id: char.hero.v3, start: [0,0], end: [0.2,0], facing: 180}]
      eyelines: [{from: char.hero.v3, to: prop.letter.v1}]
    continuity_in:  {prop.letter.v1: closed_in_right_hand}
    continuity_out: {prop.letter.v1: open_on_desk}
    board:
      panel_mode: 4
      panels: [{beat: start}, {beat: trigger}, {beat: core}, {beat: end_hold}]
      reference_panel_ids: [hero-approved-front-v3]
    edit:
      in_transition: cut
      out_transition: match_action
      actual_tail_frame_ref: null
    provenance:
      generator: story2board-adapter
      model: flux1-dev
      seed: 12345
      revision: 1
      approval_status: draft
```

### 映射到 OTIO

- 每个 `shot` → 一个 `Clip`；`duration_frames` → `source_range.duration`。
- panel 图片 / animatic / 真实尾帧 → `ExternalReference` 或 `ImageSequenceReference`。
- 对白、动作点、QC → `Marker`。
- `camera`、`blocking`、`continuity_*`、`assets`、`provenance` → `Clip.metadata.opc` 的稳定子对象。
- 多音轨对白/环境音 → 独立 `Track(kind=Audio)`，以 shot id 关联；不要把所有音频塞进 Clip metadata。

## 4. 可执行的复用路线

### Phase 1：两周内可落地

1. 定义 `OPCShot` JSON Schema + Pydantic/dataclass 模型。
2. 实现校验器：镜号唯一、帧率时间、≤15 秒、core≤14 秒、asset version 完整、轴线/屏幕方向、道具 ownership in/out、对白覆盖、尾帧引用。
3. 实现 `opcshot ↔ OTIO` adapter，并用 golden `.otio` + round-trip tests 固化行为。
4. 借 Kitsu 实体图实现本地 `Project/Episode/Sequence/Shot/Casting/Task/Preview`，先不依赖 Kitsu 服务。

### Phase 2：可选工具适配

5. Blender adapter：从 `camera/blocking/assets` 生成 camera、占位 actor/prop、Grease Pencil panel 与 keyframes；输出 preview 和 transform 回写。
6. Story2Board adapter：先支持单主体 4-panel；记录 prompt/seed/model/license；后续再加多角色与上一镜真实尾帧条件。
7. 导出：OTIO + contact sheet PDF + 独立 panel PNG + animatic MP4。

### Phase 3：连续性闭环

8. 每次生成后提取真实尾帧，更新 `actual_tail_frame_ref` 与 `continuity_out_actual`。
9. 下一镜生成前执行 continuity diff；不一致时阻断或自动生成修订任务。
10. 视觉 QC 分开打分：identity、costume/prop、screen direction、background/set、composition diversity；结构校验通过不等于导演审阅通过。

## 5. 最终取舍

- **马上采用**：OTIO 时间线/时间数学/adapter；自建 OPCShot/continuity schema；Kitsu 的实体图。
- **隔离适配**：GPL Storytools（Blender previs）；AGPL Kitsu 服务；MIT Story2Board（GPU 模型后端）。
- **仅作 clean-room 参考**：Wonder Unit Storyboarder（无许可证且维护偏停）。
- **仅作商业能力基准**：Adobe Firefly Boards；不可复制内部实现，不把网页 GUI 当稳定 API。
- **不建议**：把 OTIO 当完整分镜 schema、把 Blender 文件当连续性主数据库、把任一扩散模型的 latent/token 结构写死进 OPC 核心。

## Sources

[1] https://github.com/AcademySoftwareFoundation/OpenTimelineIO
[2] https://opentimelineio.readthedocs.io/en/latest/tutorials/otio-serialized-schema.html
[3] https://pypi.org/project/OpenTimelineIO
[4] https://github.com/Pullusb/storytools
[5] https://extensions.blender.org/add-ons/storytools
[6] https://github.com/wonderunit/storyboarder
[7] https://wonderunit.com/storyboarder
[8] https://github.com/cgwire/kitsu
[9] https://github.com/cgwire/kitsu-cli
[10] https://github.com/DavidDinkevich/Story2Board
[11] https://arxiv.org/abs/2508.09983
[12] https://www.adobe.com/products/firefly/features/storyboard.html
