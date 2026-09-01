# OPC 视频/H3 复用侦察 v0.1

> 核验日：2026-08-31。范围仅限 MiniMax H3 官方资料、AIMixer Director、ComfyUI 官方/Partner Nodes H3 工作流；未运行模型、未改本机配置。判定：**A=可直接复用，B=经薄适配可用，C=仅作参考，D=不采用**。

## 结论

| 候选 | 判定 | 最小接入建议 |
|---|---:|---|
| MiniMax 官方 H3 资料、官方仓库与 API | **B** | 固化官方 prompt guide/输入约束为 OPC H3 schema；仅封装 API/本地 Base 调用，不复制未开源 Context-IR、Regenerate-2K 服务。上线前单独做 Community License/商用地域审查。 |
| AIMixer/ComfyUI_MiniMaxH3_Director | **B** | 只借其 `external_groups → Director → report` 边界做适配器；OPC 继续持有 shot/asset/task/QC 主状态，先做 1 个 t2v + 1 个 r2v JSON 契约回归，不直接把导演台 UI 当业务数据库。 |
| ComfyUI 官方/Partner Nodes H3 工作流 | **A（模板与图结构）/C（云端实现）** | 版本锁定官方 T2V/FLF2V/R2V JSON，抽成三个受控子图；在提交前后加 OPC manifest、任务状态持久化和 QC gate。Partner 云端节点只调用，不复制服务端。 |

## 1. MiniMax 官方 H3 资料、GitHub 与 API

- **URL / 维护**：官方仓库 `MiniMax-AI/MiniMax-H3`；官方 API 为 `video-generation-v2-create`。[1][3] GitHub API 核验：仓库未归档，最近提交 `d21241f0a4b3`（2026-08-15）。
- **License**：权重及整体材料是 **MiniMax H3 Community License Agreement**，不是 MIT/Apache；含地域、商用及衍生使用条件，必须按原文法务审查。[2] 仓库代码文件中虽有个别 Apache-2.0 SPDX，不能据此把整套模型/权重视为 Apache。**不可直接复制/再许可模型材料。**
- **节点/工作流**：H3-Base 分 `FL2VA`（T2V/I2V/首尾帧）与 `Ref2VA`（图/视频/音频参考）；官方仓库给出本地 768p、Context-IR→Base→Regenerate-2K 混合链路及 API 脚本。[1]
- **示例/测试证据**：仓库含 3 个可复现 768p 请求脚本、T2VA/FL2VA/Ref2VA MP4，以及 2K 各阶段脚本和参考输出；这是可复现实例证据，但未发现覆盖 OPC 业务契约的自动化测试。[1]
- **可复用模块**：两套官方提示词指南/`h3-prompt-writing` skill、reference 数量与时长约束、`conditions[].uri` 素材描述、T2V/FL2VA/Ref2VA 路由、异步任务 ID/结果拉取模式。[1][3]
- **闭源依赖**：`H3-Context-IR` 依赖多阶段托管模型/服务，未开源；`H3-Regenerate-2K` 尚未开源，完整 2K 复现依赖 MiniMax API。[1] **服务端实现许可证不可见，标记“不可复制”，只能按 API 条款调用。**
- **与 OPC 的差距**：官方 prompt guide 不等于 OPC 的 shot-level 提示词版本/审核记录；URI/顺序引用不含素材 ID、角色/镜头绑定和血缘；API task_id 不提供 OPC 的排队—重试—取消—结算状态机；示例没有画面/音频同步、身份一致性、字幕/品牌、安全与技术参数 QC gate。[1][3]

## 2. AIMixer / ComfyUI_MiniMaxH3_Director

- **URL / 维护**：`https://github.com/AIMixer/ComfyUI_MiniMaxH3_Director`。[4] GitHub API 核验：Apache-2.0、未归档，最近提交 `9007d9aec584`（2026-08-31，恢复高级采样参数）；活跃维护，但当日仍有 51 个 open issues。
- **License**：仓库根 LICENSE 被 GitHub 识别为 **Apache-2.0**；可按许可证复用其代码，仍须保留 notice。模型权重及第三方节点不因该许可证而被覆盖。
- **节点/工作流**：单 Director 整合多段时间轴、t2v/i2v/fl2v/r2v/v2v/rv2v、选择运行、缓存/源画面补位、外部 `Director Group`/`Groups Combine`、Refine 二采及 `report` 输出；底层调用 ComfyUI 原生 H3 conditioning/sampling/AV decode。[4]
- **示例/测试证据**：仓库有 9 个示例 JSON（含 T2V、FL2V、R2V、V2V、RV2V、外部 groups、二采），README 声称可直接 Queue；树中未见 `tests/` 或 GitHub Actions，故证据级别是“示例覆盖”，**不是自动回归/生成质量证明**。
- **可复用模块**：外部 groups 数据边界、分段 plan、素材组与公共参数拼接、选择运行、segment cache、连续性处理、导出及机器可读 report；这些比整块复制 UI 更适合作 OPC adapter。[4]
- **闭源依赖**：本地生成依赖 H3 权重（Community License）及 ComfyUI 原生节点；README 另链第三方 `comfyit.cn` 模型/工作流包。该站打包物的再分发许可证未在本次核验中明确，**不可复制进 OPC 制品**；只接受用户按官方来源自备模型。
- **与 OPC 的差距**：提示词主要保存在节点/JSON，缺 prompt template ID、版本、审批与镜头语义校验；素材依赖槽位和 `@/<Picture N>` 顺序，缺稳定 asset UUID、hash、授权和 lineage；“选择运行/缓存/report”不是持久化任务状态机；未见自动测试、失败重试幂等、逐镜 QC 指标、人工验收/驳回闭环。[4]

## 3. ComfyUI 官方/Partner Nodes H3 工作流

- **URL / 维护**：ComfyUI Core（GPL-3.0）与官方 `workflow_templates`（MIT）。[5][6] GitHub API 核验：两仓均未归档；Core 最近提交 2026-08-31，templates 最近提交 `d3b4a9e89573`（2026-08-29，修复 MiniMax-H3 demo 404）。官方文档同时提供 API Partner 与本地 open-weight 教程。[7][8]
- **License**：Core 可按 **GPL-3.0** 使用；官方模板仓库为 **MIT**，所以 JSON 图结构可复用并保留许可声明。[5][6] Partner Nodes 调用 MiniMax 托管 API；服务端源码/许可证未公开，**不可复制云端实现**。
- **节点/工作流**：Partner 模板覆盖 T2V、FLF2V、R2V，输出含原生立体声；本地模板覆盖 T2V、I2V（可首/尾帧）与 R2V，使用 `MiniMaxH3ImageToVideo` / `MiniMaxH3ReferenceToVideo` 等原生节点。[7][8]
- **示例/测试证据**：官方 gallery 发布可下载 JSON/代码调用说明；templates 仓库存在 API T2V/FLF2V/R2V 与本地 T2V/I2V/R2V JSON、对应 webp/MP4 输出，且仓库有模板校验、节点兼容、站点 E2E/单测工作流。[6][9] 这证明“模板可装载/有示例输出”，不证明每次生成达到 OPC 内容 QC。
- **可复用模块**：三类基准子图、分辨率/时长/seed 参数面、SaveVideo 音视频落盘、官方模板 schema/validator、API-format JSON 与 Comfy SDK 调用边界。[6][7][8]
- **闭源依赖**：Partner 路径按秒计费并依赖 Comfy 登录、额度、网络与 MiniMax 服务；云端认证/队列/推理实现不可复制。Local 路径仍受 H3 Community License 与大模型文件约束。[7][8]
- **与 OPC 的差距**：模板只表达执行图，不保存 OPC prompt 版本/镜头归属；Load/Reference 节点没有 asset manifest、hash、权利状态；Comfy queue/job 不是跨会话业务状态与成本账本；仅有结构校验，无角色一致性、镜头连贯、音画同步、黑帧/静帧、字幕品牌、安全与人工签核 QC。[6][7][8]

## 最小接入顺序

1. **先 A**：vendor 固化官方 templates 的 T2V/FLF2V/R2V API-format JSON、commit SHA 与 license notice。
2. **再 B**：定义 `OpcH3Job{shot_id,prompt_version,asset_refs,mode,params}` → Comfy inputs；返回 `provider_task_id,output_hash,report,status`，素材引用必须由 asset UUID 映射，禁止业务层直接依赖 `<Picture N>` 顺序。
3. **可选 B**：仅在多段/多素材需求出现时接 Director external groups；Director report 作为执行遥测，不作为 OPC 状态真源。
4. **补 QC**：提交前做 schema/素材存在性/许可检查；完成后做文件可解码、时长/分辨率/fps/音轨、黑帧/静帧、音画同步和人工镜头验收。不通过则状态进入 `qc_failed`，不得只凭 Comfy `success` 放行。

## Sources

[1] https://github.com/MiniMax-AI/MiniMax-H3  
[2] https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/LICENSE  
[3] https://platform.minimax.io/docs/api-reference/video-generation-v2-create  
[4] https://github.com/AIMixer/ComfyUI_MiniMaxH3_Director  
[5] https://github.com/Comfy-Org/ComfyUI  
[6] https://github.com/Comfy-Org/workflow_templates  
[7] https://docs.comfy.org/tutorials/partner-nodes/minimax/minimax-h3  
[8] https://docs.comfy.org/tutorials/video/minimax/minimax-h3  
[9] https://comfy.org/workflows/b34841f6789c-b34841f6789c
