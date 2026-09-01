# 主体资产复用侦察 v0.1

- **范围**：角色／场景／道具主体资产生成、角色一致性、多 reference image、asset registry／locking
- **核查日期**：2026-08-31（维护状态以 GitHub API 的 `pushed_at` 与仓库自述交叉判断）
- **目标**：给 OPC 一键漫剧的 `GPT Image Subject Assets` 节点挑选可复用模块，而不是寻找一个可原样替代的端到端产品。
- **运行限制**：本机 GPT Image runtime 当前为 `MODEL_BLOCKED`；因此 OpenAI 项只完成了官方文档、SDK／示例代码与真实示例核验，**没有伪造本机生成结果**。

## 结论先行

建议采用**组合式复用**，而非押注单一项目：

1. **首选生成后端：OpenAI GPT Image Image API**——直接复用多图 `images.edit`、输出参数、流式事件和官方“Character Anchor → continuation”范式。
2. **首选锁定层：DVC + OPC 自有 manifest/QC schema**——DVC 管二进制内容寻址、远端与 Git 历史；OPC 管 `asset_id/state_id/reference role/allowed changes/QC/status`，两者职责不要混在一起。
3. **离线研究基线：PuLID（脸部真人 ID）+ IPAdapter Plus（主体／风格／构图控制）**——可用于回归对照或敏感素材本地处理，但不应冒充 GPT Image 等价后端。
4. **InstantCharacter 只做研究基准，不进入商业生产**——许可证明确禁止任何商业或 production 用途。[7]

| 候选 | 类型 | OPC 推荐级别 | 最适合复用的部分 | 主要硬伤 |
|---|---|---:|---|---|
| OpenAI GPT Image 官方 API/Cookbook/Demo | 官方 SDK／示例 | **A：主后端** | 多参考图编辑、角色锚定、流式输出、参数适配 | 云端、费用／策略／可用性；没有资产注册与确定性锁定 |
| InstantCharacter + ComfyUI wrapper | 开源角色一致性 | **C：研究基准** | 单图主体编码、`subject_scale`、本地推理结构 | 明确非商用／非生产；高显存；非场景／道具锁定 |
| PuLID (SDXL/FLUX) | 开源 ID 一致性 | **B：离线脸部基线** | tuning-free ID encoder、fidelity/editability 参数 | 偏人脸身份，不是通用角色资产；FLUX.1-dev 商用受限 |
| ComfyUI IPAdapter Plus | ComfyUI 工作流 | **B：离线控制模块** | 多 reference embedding、区域／风格／构图节点与 JSON 工作流 | maintenance-only；GPL；依赖模型许可证碎片化 |
| DVC Data Registry | 资产管理／locking | **A：锁定基础层** | 内容哈希、`.dvc` pointer、remote、Git 审批历史 | 不理解 OPC 语义、审批、QC、reference 顺序 |

---

## 候选 1：OpenAI GPT Image 官方 API + Cookbook + ImageGen Demo

### URL / license / 维护状态

- 官方指南与 Python API 分别是 [Image generation][1] 和 [Create image edit][2]。
- 官方生产提示范式见 [GPT Image Prompting Guide][3]；可运行 Demo 为 [openai-imagegen-demo][4]。
- **代码许可**：`openai-imagegen-demo` 为 MIT，可商用、修改、分发；OpenAI Cookbook 同为 MIT。服务本身另受 OpenAI API 条款、使用政策与计费约束，不能把示例代码许可误认为模型服务许可。[4]
- **维护状态：活跃**。官方指南当前覆盖 `gpt-image-2`，Demo 是 GPT Image 2 的 Next.js photobooth；本次 GitHub API 核查中 `openai/openai-cookbook` 与 `openai/openai-python` 均在 2026-08 有提交。

### 已核实的真实示例

- API Reference 给出**四张产品参考图合成一个礼篮**的 Python `client.images.edit(image=[...])` 完整示例，证明“一次请求、多有序 reference”不是概念稿；当前参考上限为 16 张，每张 PNG/WebP/JPG、低于 50 MB。[2]
- 官方 Prompting Guide 给出完整的 **Character Anchor → Story continuation**：先生成儿童绘本角色锚图，再将该锚图送入 `images.edit`，显式重复脸、比例、服装、色板和“不重设计角色”等不变量，并展示两张输出图。[3]
- 官方 Demo 实际实现上传／相机输入、风格预设、`/images/edits`、partial-image streaming、结果下载；路由、SSE parser、API service、preset catalog 都有明确文件边界。[4]

### 可复用模块

1. **`GptImageBackendAdapter`**：映射 OPC `runtime_model_id / endpoint_mode / ordered references / size / quality / background / format / compression` 到官方 SDK；不要硬编码显示名。
2. **Reference packer**：按 manifest 的有序角色组装 multipart 数组；强制记录每张输入的 `asset_id/version/SHA-256/role/allowed_changes`。
3. **Character-anchor prompt compiler**：复用官方“change vs preserve”“每轮重述不变量”“Character Anchor → continuation”结构，而非照搬其故事内容。[3]
4. **Streaming/cost telemetry**：复用 Demo 的 SSE 分层和 API 的 partial events；记录 request ID、usage、requested/actual output metadata。[2][4]
5. **输出解码器**：GPT Image 始终返回 base64 图像；OPC 立即落盘、验 MIME／尺寸／alpha 并计算 SHA-256，不能依赖临时 URL。[2]

### 与 GPT Image / OPC 的差距

- 这是最接近 GPT Image 的候选，但官方示例仍是**生成体验**而不是**可审计资产流水线**：没有 source approval hash、fact-to-source map、typed blocking statuses、独立 QC、candidate retry ledger、formal lock record。
- `images.edit` 的 high fidelity／mask 是生成控制，不是像素锁或身份保证；官方建议每轮重申 preserve list，本身就说明会漂移。[3]
- 多图数组只提供输入顺序，不自动提供 OPC 所需的“哪张是身份、服装、道具、场景拓扑”语义；需 OPC manifest 自己绑定。
- Responses API 适合多轮编辑，Image API 适合单请求生成／编辑；OPC 应将两者做成显式 endpoint adapter，禁止自动切换。[1]

### 数据隐私 / 商用限制

- API business data 默认不用于训练；API 输入／输出通常可能保留最多 30 天用于服务与滥用识别，符合条件的端点／客户可申请 ZDR；输入输出权利在法律允许范围内归客户，但仍要遵守政策并确保上传 reference 的肖像权、版权和授权。[5]
- 云端处理意味着未公开角色设定、演员脸、客户商品图会离开本机；资产 manifest 应标 `sensitivity`，对敏感主体要求 ZDR 资格或转本地后端。
- API 输出“归用户”不等同于任何司法辖区都必然产生可执行版权，也不保证不近似第三方作品；商用发布仍需法务／相似性检查。

---

## 候选 2：Tencent InstantCharacter（含 ComfyUI wrapper）

### URL / license / 维护状态

- 官方仓库：[Tencent-Hunyuan/InstantCharacter][6]；项目页／论文图例：[instantcharacter.github.io][8]；第三方 ComfyUI wrapper 在官方 README 中有链接。[6]
- **许可：自定义、严格非商用**。许可证只允许 academic/research/education，并明确禁止“任何商业或 production 用途”；代码和模型权重都在该定义内。[7]
- **维护状态：低频／近停滞**。未 archived，但官方仓库最近 push 为 2025-05-14；公开更新包括 22 GB 以下 offload、ComfyUI wrapper 和首次发布。[6]

### 已核实的真实示例

- 官方 README 给出可执行的 FLUX pipeline：单张白底女孩 reference，经 SigLIP + DINOv2 encoder、InstantCharacter adapter、`subject_scale=0.9`，生成“街头弹吉他”，并给出 Ghibli／新海诚 LoRA 变体。[6]
- 项目页公开多角色、跨姿态／风格定性图和对比图；论文方法声明训练数据为千万级 paired multi-view + unpaired text-image 样本。[8]
- 官方自己注明动物角色“relatively unstable”，这是 OPC 非人类 IP 角色的重要风险信号。[6]

### 可复用模块

- **主体编码接口**：`subject_image + subject_scale + seed + prompt` 的清晰后端契约。
- **双视觉编码器思路**：细节与背景鲁棒特征分开提取，再由 adapter 注入 DiT；可借鉴为 OPC QC 的“身份细节／整体轮廓”双指标，而不复制受限权重。
- **ComfyUI node boundary**：reference loader、adapter loader、offload、sampler、save 节点可作为本地实验工作流结构参考。
- **白底 reference 预处理约束**：适合 OPC 主体资产的规范化输入检查。

### 与 GPT Image / OPC 的差距

- 核心是**单 reference 的 character-driven generation**，不覆盖 GPT Image 的多图语义组合、mask edit、文字渲染、透明背景、Responses 多轮上下文。
- 角色一致性来自 embedding 注入，不提供像素级资产 lock；场景拓扑、道具结构、状态链都没有 registry 或版本语义。
- 基于 FLUX.1-dev，显存需求高；官方原始路径约 22 GB offload，第三方 wrapper 自述普通路径约 45 GB、offload 约 24 GB。[6]
- OPC 需要 source provenance、explicit unknown preservation、QC／typed blocking；此仓库都没有。

### 数据隐私 / 商用限制

- 本地运行时 reference 可不上传第三方，隐私优于云 API；但在线 HF Space／ComfyOnline 会把图片交给对应服务，须另审其 retention／logs。
- **不可用于 OPC 商业生产**，也不应把 wrapper 的 AGPL 许可当作能够覆盖／消除上游 InstantCharacter 非商用限制；上游限制继续生效。[7]
- 另有 FLUX.1-dev 基座许可限制，形成双重许可门槛。建议仅保留作研究 benchmark 和一致性评估样本。

---

## 候选 3：PuLID（SDXL / FLUX）

### URL / license / 维护状态

- 仓库：[ToTheBeginning/PuLID][9]；FLUX 实现与调参说明：[pulid_for_flux.md][10]。
- **代码许可：Apache-2.0**。[9] 但最终可商用性取决于所选基座／checkpoint；尤其 FLUX.1-dev 是非商业、非生产许可，商业使用需另行取得授权。[11]
- **维护状态：低频活跃**。未 archived，最近 push 2025-07-31，新增 FLUX.1-Krea-dev 支持；主模型发布集中在 2024，issue 较多。[9][10]

### 已核实的真实示例

- README 有 PuLID SDXL／FLUX 输出图、在线 HF demos、Replicate demos、model zoo；v0.9.1 自报相对 v0.9.0 ID similarity 提升约 5 个百分点，同时保持 editability。[9]
- 文档给出 12 GB、16 GB、24 GB 消费显卡运行路径和 bf16/fp8 对比图；也明确说明部分男性输入 ID fidelity 不够。[10]
- 参数示例真实揭示 trade-off：越早注入 ID，保真越高、可编辑性越低；写实建议 start timestep 4，风格化建议 0–1。[10]

### 可复用模块

- **Face-ID encoder + cross-attention injection**：作为真人／近真人角色的本地一致性后端。
- **显式 fidelity/editability knob**：把 `start_id_step / id_weight / CFG mode` 映射为 OPC 声明式 retry variables，避免靠改故事事实修图。
- **本地 Gradio／consumer GPU profiles**：可拆为 `pulid-sdxl` 与 `pulid-flux` runtime adapters。
- **回归指标**：ArcFace/InsightFace 类 identity similarity 可作为软诊断，不能替代人工 invariant QC。

### 与 GPT Image / OPC 的差距

- PuLID 是 **ID（主要为脸）customization**，不是通用角色全身、服装、场景、道具的 reference editor；儿童、动物、蒙面角色、非写实 IP 未必有可靠 face embedding。
- 不具备 GPT Image 多 reference compositing、文本／版式、透明资产、mask surgical edit 或语言推理能力。
- 没有 asset manifest、source hash、approval、reference role/order、state version、QC lock。
- 官方自己暴露 fidelity 与 editability 的冲突；因此只能成为 OPC 多后端之一，不能让 similarity score 自动触发 `LOCKED`。[10]

### 数据隐私 / 商用限制

- 完全本地推理可保留生物特征 reference 在本机；但脸 embedding 本身仍属高敏感派生数据，应加密、最小保存并绑定被摄者授权。
- Apache-2.0 只覆盖 PuLID 代码；模型权重、InsightFace、基座 checkpoint 各自许可必须逐项做 SBOM。使用 FLUX.1-dev 的路径不能直接商业化。[10][11]
- 输出涉及真人肖像时还需防冒用／深伪与属地人格权风险。

---

## 候选 4：ComfyUI IPAdapter Plus

### URL / license / 维护状态

- 仓库：[cubiq/ComfyUI_IPAdapter_plus][12]；真实工作流目录：[examples][13]；核心 IP-Adapter 模型卡：[h94/IP-Adapter][14]。
- **节点代码许可：GPL-3.0**。[12] 核心 h94 IP-Adapter 模型卡标 Apache-2.0，但 FaceID、Kolors、LoRA、基座模型等必须分别核对，不能以节点仓库 GPL 代替模型许可证。[12][14]
- **维护状态：maintenance-only**。作者在 2025-04-14 明确说不再以 ComfyUI 为主要生成工具，只会考虑关键更新／PR，不做持续开发；仓库未 archived，最近 push 同日。[12]

### 已核实的真实示例

- `examples/` 不是截图集合，而是大量可导入 JSON：simple、advanced、FaceID、FaceID batch、combine embeds、weighted embeds、regional conditioning、style+composition、precise composition、negative image、tiled 等。[13]
- README 将 IPAdapter 描述为“1-image LoRA”，并给出统一模型加载器、精确命名、FaceID+LoRA 配对、权重建议和视频教程。[12]

### 可复用模块

1. **Reference conditioning graph**：主体、脸、风格、构图、负参考分成不同 embedding／weight／region；这很适合映射 OPC 的 ordered reference roles。
2. **`combine_embeds` / `weighted_embeds` / batch FaceID**：可用于多视图角色 master 的本地融合实验。
3. **regional conditioning**：多角色同镜时把 reference 限定到区域，降低身份串脸。
4. **ComfyUI JSON 工作流封装**：节点 ID、模型依赖、seed、sampler、输出都可固定并纳入 run manifest；先导出 API format，再由 REST `/prompt` 执行。
5. **Unified loader contract**：严格模型文件名可进一步升级为“模型文件 SHA-256 + license manifest”，避免同名漂移。

### 与 GPT Image / OPC 的差距

- IPAdapter 是视觉条件注入，不具备 GPT Image 对复杂自然语言、不变量列表、多对象关系、精确文字的统一推理。
- 多 reference embedding 融合不等于语义角色绑定；“身份脸 + 服装 + 道具 + 场景”仍可能互相污染，必须用区域、mask、分阶段生成和 QC。
- ComfyUI workflow JSON 通常锁了图结构和参数，但**不自动锁模型字节、custom-node commit、Python/CUDA 环境或输出**；需额外 manifest/DVC。
- maintenance-only 且 ComfyUI API／节点接口会演进，OPC 应 vendoring 固定 commit 或加兼容测试，不能盲目自动更新。[12]

### 数据隐私 / 商用限制

- 本地 ComfyUI 可让 references、embeddings、outputs 留在本机；Comfy Cloud／第三方节点可能上传遥测或素材，需逐节点审计。
- 未知 workflow／custom node 本质上可执行 Python，应视同代码执行，入库前 code review 和 hash lock。
- GPL-3.0 对分发修改版／组合的义务需法务判断；若只把本地 ComfyUI 当独立进程，通过文件／HTTP 边界调用，通常比把其代码嵌入闭源 OPC 更容易隔离，但不能当法律结论。
- 商用必须生成**逐组件许可清单**：节点、IPAdapter 权重、CLIP vision、InsightFace、LoRA、SDXL/Kolors/其他 base checkpoint 缺一不可。[12][14]

---

## 候选 5：DVC Data Registry（资产 registry / locking 基础层）

### URL / license / 维护状态

- 仓库：[treeverse/dvc][15]；Data Registry 方案：[官方文档][16]；`.dvc` 文件规范：[官方文档][17]。
- **许可：Apache-2.0**；成熟项目，GitHub API 本次核查显示 2026-08 仍有 push，仓库未 archived。[15]
- **维护状态：活跃／成熟**，相比图像生成研究仓库更适合做长期基础设施。

### 已核实的真实示例

- `.dvc` 是可进 Git 的 YAML pointer，示例包含输出 `md5`、`path`、描述和 remote；规范还支持目录、size/nfiles 以及不同 remote 的 checksum／version metadata。[17]
- 官方 Data Registry 明确支持跨项目 `dvc get`／`dvc import`，将 metadata/history 放 Git、数据放远端，并可用只读 endpoint 防删除／篡改。[16]

### 可复用模块

- **内容寻址资产存储**：每个 reference、candidate、locked output 由 DVC 管二进制和 remote；OPC 同时另算 SHA-256 作为安全／供应链标识（DVC 当前本地内容追踪常用 MD5，不能直接替代 OPC 要求的 SHA-256）。[17]
- **Git 审批轨迹**：manifest、QC report、lock record 走 branch/PR/review；大图不塞 Git。
- **跨项目只读 registry**：下游 storyboard／video skill 通过 tag／Git commit pin 取已锁资产，不读取“latest”。
- **版本回滚／复现**：锁定 `git_commit + dvc pointer + sha256 + storage URI`，使角色 master 与 state versions 可追溯。

### 与 GPT Image / OPC 的差距

- DVC 不生成图，也不理解角色／场景／道具、identity master、state delta、reference role/order、approval、explicit unknown 或 `LOCKED/QC_FAILED/MODEL_BLOCKED`。
- `.dvc` 的内容哈希证明“字节相同”，不证明“画对了”“授权有效”或“这个候选已批准”。
- 并发锁、审批状态机、候选唯一性和下游权限需要 OPC 自己实现；DVC remote ACL 只解决存储访问的一部分。

### 数据隐私 / 商用限制

- DVC 本身可完全本地或接自管 S3／Azure／SSH；数据是否出域取决于 remote 配置，不由 DVC SaaS 强制决定。[16]
- Apache-2.0 商用友好；真正风险在 remote 凭据、bucket ACL、reference 生物特征／客户 IP 的加密和删除策略。
- Git 中只存 pointer／manifest，**不得**把人脸原图、API key、signed URL 或可逆 embedding 放公开仓库。

---

## 推荐的 OPC 复用架构

```text
approved upstream asset_spec
        │
        ▼
[OPC preflight compiler]
  provenance / explicit unknowns / sufficiency gates
        │
        ├── cloud: OpenAI images.edit (primary)
        ├── local-face: PuLID (optional benchmark)
        └── local-general: ComfyUI IPAdapter graph (optional benchmark)
        │
        ▼
[candidate store: DVC remote]
  raw bytes + SHA-256 + backend/model/workflow commit + ordered refs
        │
        ▼
[OPC independent QC]
  per-invariant result + retry variables + policy/provenance checks
        │
        ▼
[lock transaction]
  exactly one formal final
  asset.json + qc.json + lock.json + .dvc pointer + Git commit/tag
```

### 最小可实施的 lock record（建议新增，不来自任一候选的现成 schema）

```yaml
asset_id: character.niuman.identity-master
state_version: v0.1
status: LOCKED
source_manifest_sha256: "..."
backend:
  kind: openai-images-edit
  model_id: "<runtime verified exact id>"
  endpoint: /v1/images/edits
  request_id: "..."
references:
  - order: 0
    ref_id: "..."
    role: identity
    version: v0.1
    sha256: "..."
    allowed_changes: [pose, background]
artifact:
  dvc_path: assets/character.niuman.identity-master/v0.1.png.dvc
  sha256: "..."
  mime: image/png
  width: 1024
  height: 1536
qc_report_sha256: "..."
workflow_lock:
  prompt_schema_version: "..."
  code_git_commit: "..."
  comfy_workflow_sha256: null
  model_weights_sha256: null
approved_by: "independent-verifier-id"
locked_at: "RFC3339 timestamp"
```

## 采用／排除建议

- **立即复用**：OpenAI 官方 SDK 的 `images.edit` 请求／stream 结构、官方 Character Anchor 提示结构、DVC 的内容存储与跨项目 registry。
- **小规模 PoC 后复用**：IPAdapter Plus 的 `combine_embeds + regional conditioning`，PuLID 的 ID fidelity 软评分；都必须放在独立 backend adapter 后。
- **明确排除生产**：InstantCharacter 的代码／权重／ComfyUI wrapper，因为上游许可证直接禁止 commercial 与 production。[7]
- **绝不复用为真相机制**：任何单一 CLIP／FaceID 相似度、seed、workflow JSON 或文件名。它们都不能替代 provenance、人工／独立 QC 和 SHA-256 lock。

## 验证边界与后续实验

由于当前 runtime 为 `MODEL_BLOCKED`，本报告没有声称 GPT Image 在本机成功运行。解除权限后，最小实测应固定同一角色资产，分别执行：

1. OpenAI：1 张 identity ref；4 张按 `identity/front/side/costume` 排序的 refs；交换顺序做 A/B；每组至少 4 个内部 candidates。
2. ComfyUI：IPAdapter single、combine embeds、regional；锁定 custom-node commit 和全部模型 SHA-256。
3. PuLID：写实人脸与风格化角色各一组，扫描 ID insertion timestep；记录 similarity 与人工 invariant QC 的相关／冲突案例。
4. 所有后端统一落入 DVC，验证“改一个字节 → hash／pointer 改变”“旧 Git tag 可复现拉取”“只有一个 `LOCKED` final”。
5. InstantCharacter 只允许在隔离研究环境跑非商业 benchmark，不把产物进入 OPC 商业资产库。

## Sources

[1] https://developers.openai.com/api/docs/guides/image-generation
[2] https://developers.openai.com/api/reference/python/resources/images/methods/edit
[3] https://developers.openai.com/cookbook/examples/multimodal/image-gen-models-prompting-guide
[4] https://github.com/openai/openai-imagegen-demo
[5] https://openai.com/enterprise-privacy
[6] https://github.com/Tencent-Hunyuan/InstantCharacter
[7] https://github.com/Tencent-Hunyuan/InstantCharacter/blob/main/License.txt
[8] https://instantcharacter.github.io
[9] https://github.com/ToTheBeginning/PuLID
[10] https://github.com/ToTheBeginning/PuLID/blob/main/docs/pulid_for_flux.md
[11] https://huggingface.co/black-forest-labs/FLUX.1-dev/blob/main/LICENSE.md
[12] https://github.com/cubiq/ComfyUI_IPAdapter_plus
[13] https://github.com/cubiq/ComfyUI_IPAdapter_plus/tree/main/examples
[14] https://huggingface.co/h94/IP-Adapter
[15] https://github.com/treeverse/dvc
[16] https://doc.dvc.org/example-scenarios/data-registry
[17] https://doc.dvc.org/user-guide/project-structure/dvc-files
