# GPT Image 主体资产节点：官方能力边界与输入输出规则核证备忘录

- 核证日期：2026-08-31（中国标准时间）
- 范围：仅核证 GPT Image 主体资产提示词/生成节点所需的模型与 API 能力边界；不设计产品架构，不生成图片。
- 证据等级：**A**＝OpenAI 官方文档、官方模型页、官方发布；**P**＝OPC 项目已锁定规则；**E**＝尚未完成固定样例实测的经验性判断。
- 运行时信息边界：外部资料仅用于本 Skill 制作与验证；不得转化为剧情、角色、场景或道具设定。

## 1. 执行结论

1. **模型 ID 不得写死。** 截至核证日，OpenAI 官方图像指南明确列出 `gpt-image-2`、`gpt-image-1.5`、`gpt-image-1`、`gpt-image-1-mini`；其中 `gpt-image-2` 是当前最新/默认的直接 GPT Image 模型，并存在快照 `gpt-image-2-2026-04-21`。[1][2] 但节点必须从受控运行配置取得并记录实际 `model_id`，启动或执行前按官方模型目录/账户可用性校验，不把“GPT Image 2”等用户称呼直接当运行时 ID。
2. **文本生图与图像编辑均为官方能力。** Image API 的 Generations 从文本生成；Edits 可用一张或多张输入图作为参考，进行部分或整体修改。[1]
3. **多图输入是明确能力，但未核实出通用固定最大张数。** 官方指南展示 4 张输入图，并明确称可用“一张或多张”参考图；因此 Skill 可表达有序多参考图，但不得凭空承诺最大张数、跨模型相同上限或每张图的语义自动绑定。[1]
4. **参数必须按实际模型校验。** `gpt-image-2` 支持满足约束的灵活分辨率；较早 GPT Image 型号的文档/返回结构常见尺寸为 `1024x1024`、`1024x1536`、`1536x1024`。不能把 `gpt-image-2` 的任意合法分辨率、透明背景预览等规则无条件下放到旧型号。[1][2][6]
5. **输出是图像字节，不是永久 URL。** Image API 对 GPT Image 返回 base64 图像数据；可请求 `png`、`jpeg`、`webp`，默认 `png`；`jpeg`/`webp` 可设 `output_compression`。[1][6]
6. **参考图不等于身份锁定保证。** 官方提供高保真输入/编辑能力，但没有承诺角色、服装、拓扑、文字、左右手或跨批次身份必然像素级一致。主体资产节点必须把这些作为验收项，而不是能力前提。

## 2. A 级：官方事实

### A-01 模型命名与调用面

- 官方图像指南当前列出四个 GPT Image API 模型：`gpt-image-2`、`gpt-image-1.5`、`gpt-image-1`、`gpt-image-1-mini`；部分组织可能需要先完成 API Organization Verification。[1]
- `gpt-image-2` 官方模型页称其为当前 state-of-the-art 图像生成模型，输入为文本和图像、输出为图像，支持 `/v1/images/generations` 与 `/v1/images/edits`；模型页列出别名 `gpt-image-2` 和快照 `gpt-image-2-2026-04-21`。[2]
- `gpt-image-1` 与 `gpt-image-1-mini` 官方模型页均明确为原生多模态，接受文本和图像输入并输出图像；mini 是成本优化版本。[4][5]
- `gpt-image-1.5` 官方模型页现称其为 previous image generation model；官方发布说明其相较 GPT Image 1 强化了指令遵循、编辑和保留细节能力。[3][9]
- Image API 直接选择 GPT Image `model`；Responses API 则选择支持 image-generation tool 的主线模型，由工具自行选择 GPT Image 模型。因此二者的 `model` 字段不是同一种模型身份，不能混写。[1]

**边界判断：** “GPT Image 2”现在有可核验的正式 API ID `gpt-image-2`，但这只证明核证日官方目录中的型号，不授权节点永远写死该值。模型别名可能滚动，快照用于锁定行为；账户权限与接口可用性仍须执行时校验。[2]

### A-02 文本生图

- Image API Generations 依据文本 prompt 从零生成图像；默认返回一张，也可用 `n` 请求一次返回多张。[1]
- API 参考对 GPT Image 的响应给出 base64 图像数据及 token usage 字段（文本输入 token、图像输入 token、图像输出 token等）。[6]

**边界判断：** `n` 是“同请求多输出”，不是“多参考图输入”，二者必须分字段记录；具体 `n` 上限应以所选模型当时的 API schema 为准，不由 Skill 猜测。

### A-03 参考图、多图与图像编辑

- Image API Edits 可以“部分或整体”修改已有图像，并允许一张或多张图作为参考生成新图；官方示例用 4 张商品参考图合成一张礼篮图。[1]
- Responses API 接受上下文中的图像输入/输出，支持多轮编辑和 File ID；`action` 可为 `auto`、`generate`、`edit`，强制 `edit` 却没有上下文图像会报错。[1]
- `gpt-image-2` 对每张图像输入自动按 high fidelity 处理；官方要求省略 `input_fidelity`，因为该型号不允许调整此参数，且参考图编辑可能产生更高图像输入 token 成本。[1]
- Mask 编辑是 prompt-based 引导，官方明确说不保证完全精确遵循遮罩形状；多输入时 mask 作用于第一张图。图与 mask 必须同格式同尺寸、均小于 50MB，mask 还必须含 alpha channel。[1]

**边界判断：**

- 多图能力成立，但“第一图自动是人物身份、第二图自动是服装、第三图自动是风格”不是官方规则；角色/用途与输入顺序必须由结构化任务显式声明。
- 高保真处理不等于无损复制、身份一致性担保或只改指定区域；mask 也不是硬像素约束。
- 未从本次官方资料核实出适用于所有 GPT Image 型号/接口的统一最大输入图数和统一单图大小上限，禁止写死。

### A-04 尺寸与质量

- `size`、`quality`、`background` 支持 `auto`；质量选项为 `low`、`medium`、`high`、`auto`。[1]
- `gpt-image-2` 接受满足以下约束的分辨率：每边是 16px 倍数；最长边不超过 3840px；长短边比不超过 3:1；总像素不少于 655,360 且不超过 8,294,400。官方列出的常用值包括 `1024x1024`、`1536x1024`、`1024x1536`、`2048x2048`、`2048x1152`、`3840x2160`、`2160x3840` 与 `auto`；超过 2,560×1,440 总像素的输出被标为 experimental。[1]
- API 参考/旧型号常见合法返回尺寸为 `1024x1024`、`1024x1536`、`1536x1024`。[6][7]

**边界判断：** 不得建立“GPT Image 全系列都支持 4K/任意比例”的硬规则。节点应把 `requested_size` 与 API 实际回传的 `size` 分开记录，并按执行时 `model_id` 的官方 schema 验证。

### A-05 背景、格式、压缩与返回

- `gpt-image-2` 的透明背景目前是 preview；请求 `background: "transparent"` 时应使用 `png` 或 `webp`，`jpeg` 不支持透明背景。[1]
- Image API 默认输出 `png`，也可请求 `jpeg` 或 `webp`；返回 base64 编码图像数据。`jpeg` 和 `webp` 可通过 `output_compression` 设 0–100% 压缩级别。[1][6]
- GPT Image 的 URL 返回不可作为通用假设；官方 API 参考明确 GPT Image 默认 base64，而 URL 语义主要属于 DALL·E 的 `response_format`。[6][7]

**边界判断：** 文件扩展名必须由实际 `output_format` 决定；不得把 base64 字符串当图片文件落盘，也不得把透明背景视为已实现，必须读取回传 metadata 并解码验收 alpha。

### A-06 安全、错误与可用性

- 所有 prompt 和生成图都受官方内容政策过滤；GPT Image 的 `moderation` 支持 `auto` 与 `low`。[1]
- 官方建议用 HTTP 状态/SDK 异常、request ID 与稳定的 `error.code` 处理错误；`429`/`5xx` 可按瞬时错误重试，`image_generation_user_error` 不应原样自动重试；`moderation_blocked` 可能附带 input/output stage 等粗粒度详情。[1]
- 官方提示部分组织在使用 GPT Image 前可能需要组织验证。[1]

## 3. P 级：OPC 项目锁定规则

以下规则来自 OPC 总类与当前断点，不冒充 OpenAI 能力：

1. **封闭运行时输入。** 运行时唯一合法信息源：原始小说明确版本、已验收上游 Skill 结构化产物、当前 Skill 已锁定规则/默认值/输出契约。禁止接受聊天补充、场外解释、网络资料、其他项目资料或未验收草稿；缺项时使用已验证默认值或输出机器可识别的阻断，不反问。
2. **节点唯一职责。** 只把已验收的人物、场景、道具主体及其状态版本编译成可执行图像任务并生成/QC 主体资产；不改剧情、不重新抽取资产、不拆分镜、不做视频运动设计、不把其他模型方言套入 GPT Image。
3. **模型配置规则。** 输入字段使用受控的 `runtime_model_id`；另外记录 `provider_display_name`、`official_model_id`、可选 `snapshot_id` 和核验时间。未知、不可用或与参数 schema 不匹配即 `MODEL_BLOCKED`，禁止静默降级。
4. **输入参考图规则。** 每张图必须来自已验收上游或本节点已批准资产，并携带 `reference_id`、版本、SHA-256、用途（identity/appearance/material/layout 等）、顺序和允许变化项；聊天上传不进入运行时。
5. **唯一成品。** 节点内部可以生成多个候选并自动 QC，但向下游只交付一个已锁定主体资产版本；不得把 `n>1` 的原始候选直接当多个正式版本。
6. **可追溯输出。** 至少记录 request ID、实际 `model_id`/snapshot（若 API 提供）、endpoint、prompt 版本、所有输入图哈希与顺序、请求参数、响应 metadata、输出格式/尺寸/背景、输出 SHA-256、usage、错误码、QC 与锁定状态。
7. **失败不补剧情。** 模型拒绝、编辑漂移、参考图冲突、参数非法或缺关键资产时，只能定向重试已声明变量或阻断；不得新造服装、道具、场景史或人物身份来“修图”。

## 4. E 级：必须通过固定样例验证后才能升级的经验

1. **参考图排序效应。** 第一张身份母版是否比后续图更强、不同用途图的最佳排序，目前只能视为待测；除 mask 明确作用于第一图外，官方未给通用权重规则。
2. **跨状态身份一致性。** 同一角色换服装/年龄/伤情时的脸型、体型、识别特征保持率需要固定资产样例量化，不能由“high fidelity”推导。
3. **只改声明变量。** 官方虽宣传更精确编辑与保留细节，但具体到 OPC 人物、场景拓扑、道具几何的保持率仍须测量。[9]
4. **最佳质量与尺寸。** `high` 并不自动等于 OPC 主体资产最优；应以身份保持、可见细节、成本、延迟和下游可用性共同实测。
5. **透明底清洁度。** 即便返回 alpha，也不能假设边缘无残色、半透明污染或阴影；需像素级 alpha/边缘 QC。
6. **文字、左右手、数量、细小配件。** 官方未给 100% 正确保证，应设为可机器/人工独立验收的风险项。
7. **多图容量与冲突退化。** 输入张数增加是否改善或稀释约束、不同参考图冲突时模型如何取舍，须按目标型号与接口实测。
8. **别名漂移。** `gpt-image-2` 别名与快照在一致性/质量上的实际差异需要回归，不能仅凭模型页推断。

## 5. 建议写入 Skill 的最小输入/输出契约（能力契约，不是产品架构）

### 5.1 必填输入

- `source_manifest`：原始小说版本与已验收上游产物版本/哈希；
- `asset_spec`：唯一资产 ID、类型（人物/场景/道具）、完整可见事实、状态版本、必须保持项、允许变化项、未知项；
- `runtime_model_id`：受控配置给出的官方 API ID，不从聊天解析；
- `endpoint_mode`：`images.generations` 或 `images.edits`（若用 Responses tool，必须单列并记录主线调用模型，不能与 GPT Image ID混淆）；
- `prompt` 与 prompt 版本；
- `reference_images[]`：若为 edit/reference 任务，含稳定 ID、版本、哈希、顺序、用途、来源；
- `output_request`：`size`、`quality`、`background`、`output_format`、可选 `output_compression`、`n`，且均需按实际型号 schema 校验。

### 5.2 必填输出

- `status`：`LOCKED | RETRYABLE_FAILED | ASSET_BLOCKED | MODEL_BLOCKED | POLICY_BLOCKED`；
- `request_provenance`：request ID、时间、endpoint、实际模型/快照（可取得时）、完整参数与输入清单；
- `image_artifact`：绝对路径/受控 URI、MIME、格式、字节数、宽高、alpha/背景检测、SHA-256；
- `usage`：API 返回的文本/图像输入与图像输出 usage（存在则原样记录）；
- `qc`：必须保持项逐条结果、允许变化项、未知/风险、失败原因、定向重试变更；
- `lock_record`：正式资产 ID、版本、来源哈希、批准输出哈希；只有 QC 通过才可进入 `LOCKED`。

## 6. 明确禁止的假设清单

- 不假设用户口语“GPT Image 2”永远等于某个可用 API ID；不把型号写死在 Skill 正文或调用模板。
- 不假设 Responses API 的主线 `model` 就是实际 GPT Image `model_id`。
- 不假设所有账户、地区、组织均已获权限，也不把 Organization Verification 当作已完成。
- 不假设所有 GPT Image 型号拥有相同尺寸、透明背景、`input_fidelity`、流式、压缩或多图上限。
- 不假设多图的顺序权重、角色绑定和冲突优先级；除官方 mask-first-image 规则外均须显式声明或实测。
- 不假设 mask 是精确像素边界。
- 不假设高保真编辑能保证人物身份、场景拓扑、道具结构、文字、手指、左右、数量或局部未改区完全一致。
- 不假设生成成功即资产合格；必须解码、检查实际格式/尺寸/alpha、计算哈希并完成资产 QC。
- 不假设 API 返回永久 URL；GPT Image 按 base64 图像处理。
- 不接受聊天补充作为运行时 prompt、参考图、模型选择、剧情设定或修复依据。

## 7. 核证状态与待测清单

**已由官方资料核证：** 当前模型目录；Image API 文本生成/编辑；多参考图能力；Responses 多轮图像上下文；`gpt-image-2` 高保真输入；mask 边界；尺寸/质量/背景/格式/压缩；base64 返回；安全过滤与错误处理。

**仍需真实 API 固定样例测试：** 当前账户实际可用模型列表与权限、各选定型号的精确参数 schema、最大多图数/单图限制、参考图排序与冲突、人物身份保持、状态版本编辑、透明底清洁度、文字/左右手/数量、别名对快照漂移、错误与重试策略。未测项保持 E 级，不能升级为硬门禁。

## Sources

[1] https://developers.openai.com/api/docs/guides/image-generation
[2] https://platform.openai.com/docs/models/gpt-image-2
[3] https://platform.openai.com/docs/models/gpt-image-1.5
[4] https://platform.openai.com/docs/models/gpt-image-1
[5] https://platform.openai.com/docs/models/gpt-image-1-mini
[6] https://platform.openai.com/docs/api-reference/images/create
[7] https://platform.openai.com/docs/api-reference/images/createEdit
[9] https://openai.com/index/new-chatgpt-images-is-here
