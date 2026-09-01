# OPC GPT Image 运行就绪只读核验 v0.1

- 核验时间：2026-08-31 14:14:01 +08:00
- 核验对象：`D:\Hermes\skills\creative\gpt-image-subject-assets-opc-test\SKILL.md`
- 核验性质：本机只读运行前置检查；**未发起任何 API 请求，未生成图片，未显示或复制任何密钥值**
- 结论：**MODEL_BLOCKED / 不可安全进入真实生成**

## 1. 总结论

本机存在 OpenAI 兼容凭证记录、OpenAI Python SDK、Hermes `image_generate` 实现及 OpenAI 图像 provider 源码；CLI 的 `image_gen` toolset 也处于 enabled。可是目标 OPC 节点要求的关键运行门禁并未闭合：

1. 没有发现目标节点可消费的、受控且显式的 `runtime_model_id` 配置；
2. 没有 `image_gen:` 配置段，未显式选择 `image_gen.provider=openai`，也未锁定质量层级；
3. 当前 `OPENAI_API_KEY` 凭证记录关联的是第三方 OpenAI-compatible endpoint `https://api-yue88.xyz/v1`，不是已核验的 OpenAI 官方 endpoint；
4. 未经 API 请求无法证明该凭证对 `gpt-image-2`、`/v1/images/generations` 或 `/v1/images/edits` 有权限；本次按要求不得请求，因此权限必须记为 `UNKNOWN/UNVERIFIED`；
5. 通用 Hermes 图像工具的输入/输出契约不足以直接满足 OPC Skill 所需的 provenance、实际模型/endpoint/request ID、输出 MIME/尺寸/alpha/SHA-256、分层 QC 与唯一 lock record；
6. OPC 专用、可审计的执行脚本和专用输出目录均未发现。

因此，凭证“存在”不等于 OpenAI GPT Image“可用”。当前不得把任何 eligible fixture 送入真实生成，也不得宣称运行时就绪。

## 2. 可用 / 缺失矩阵

| 检查项 | 状态 | 只读证据 | 判定 |
|---|---|---|---|
| 模型 ID 来源 | **缺失（受控值）** | 目标 Skill 要求 `runtime_model_id`；`D:\Hermes\config.yaml` 无 `image_gen:` 段，也未发现 OPC runtime 配置或执行清单。OpenAI provider 源码内部写有 API 模型 `gpt-image-2`，并有虚拟层级 `gpt-image-2-low/medium/high`，但这是 Hermes provider 默认/实现常量，不是目标节点已批准的受控 `runtime_model_id`。 | **BLOCKED**；不得把源码默认值静默提升为 OPC 运行配置。 |
| Endpoint | **存在配置，但未核验为目标能力** | `D:\Hermes\.env` 中 `OPENAI_BASE_URL` 为非空；凭证池把 `OPENAI_API_KEY` 记录关联到 `https://api-yue88.xyz/v1`。Hermes OpenAI 图像 provider 调用 SDK 的 `images.generate` / `images.edit`；其源码未显式传 `base_url`，运行时可能由 SDK 环境配置解析。 | **BLOCKED**；endpoint 是第三方兼容站，未证明实现 GPT Image Images API，也未证明模型映射/返回 schema。 |
| 官方 OpenAI endpoint | **未配置/未证实** | 未发现受控值明确锁定 `https://api.openai.com/v1`。 | **缺失**。不得把第三方 endpoint 当作官方 OpenAI。 |
| API 凭证存在性 | **存在（仅存在性）** | `D:\Hermes\.env` 有非空 `OPENAI_API_KEY`；`D:\Hermes\auth.json` 有 `openai-api` API-key 凭证池条目及指纹记录。本报告未读取或输出密钥值。 | **AVAILABLE-PRESENCE-ONLY**。 |
| GPT Image 权限 | **未知/未验证** | 凭证池该条目无成功/失败状态和图像请求记录；`request_count=0`。按任务约束未请求模型目录或 Images API。 | **BLOCKED**；不能推断模型、组织验证、额度、地区或 endpoint 权限。 |
| Codex OAuth | **不可作为替代** | `openai-codex` 凭证池状态为 `exhausted`，并记录需重新登录；其 endpoint 为 ChatGPT Codex backend，不是已批准的 Images API 凭证。 | **UNAVAILABLE / OUT OF SCOPE**。 |
| 调用工具 | **部分可用** | CLI toolset 中 `image_gen` enabled；源码存在 `D:\Hermes\hermes-agent\tools\image_generation_tool.py`、OpenAI backend `plugins\image_gen\openai\__init__.py`；已安装 `openai==2.24.0`。 | 基础执行件存在，但当前会话未暴露 `image_generate` 工具，且 provider 未受控选定。 |
| 已配置 image provider | **缺失** | `config.yaml` 无 `image_gen:` 段，故无显式 `image_gen.provider`、`image_gen.model` 或 `image_gen.openai.model`。脱离完整 Hermes 插件启动流程的只读 registry 检查得到 active provider 为 `None`，不能证明运行时已路由到 OpenAI。 | **BLOCKED**；启用 toolset 不等于 provider 已配置。 |
| OpenAI provider 能力代码 | **存在** | provider 声明 text/image 两种 modality、最多 16 张参考图；generation 调用 `client.images.generate`，edit 调用 `client.images.edit`，结果保存至缓存。 | 代码能力存在，不等于账户/endpoint 能力已验证。 |
| 输出目录 | **通用缓存可用；OPC 专用目录缺失** | 通用目录 `D:\Hermes\cache\images\` 已存在；provider 默认保存于该目录。候选 OPC 专用目录 `D:\Hermes\xiaonan-memory\outputs\opc-gpt-image-subject-assets\` 不存在，且目标 Skill 未锁定唯一输出根目录、命名/版本/不可覆盖规则。 | **BLOCKED for OPC lock**；通用缓存不能替代受控资产仓。 |
| OPC 专用执行脚本 | **未发现** | 对 `D:\Hermes` 的文件名与内容检索仅定位到通用工具/provider、Skill 和静态报告；未发现把 approved manifest 编译为请求、落 provenance/audit JSON、做解码元数据/SHA/QC/lock 的专用 runner。 | **缺失**。 |
| 最小请求 schema | **可从官方备忘录/源码整理，但尚未固化成机器 schema** | 见第 3 节。当前通用工具只接受统一 prompt/aspect/reference 输入；provider 固定 `n=1`，内部把层级映射为 `gpt-image-2` + quality。 | **BLOCKED**；需要目标节点可验证的 JSON Schema/运行清单。 |
| 可安全进入真实生成 | **否** | 受控模型、provider、endpoint 能力、权限、专用审计闭环均未闭合。 | **MODEL_BLOCKED**。 |

## 3. 最小请求 schema（运行前应固化；本次未发送）

### 3.1 OPC 运行清单最小结构

```json
{
  "node_run_id": "<required-controlled-id>",
  "prompt_schema_version": "<required-version>",
  "source_manifest": [
    {
      "path_or_uri": "<approved-source>",
      "version": "<required>",
      "approval_status": "approved",
      "sha256": "<64-hex>"
    }
  ],
  "asset_spec": {
    "asset_id": "<required>",
    "asset_type": "character|scene|prop",
    "state_version": "<required>",
    "visible_facts": [],
    "required_invariants": [],
    "allowed_changes": [],
    "explicit_unknowns": []
  },
  "runtime": {
    "provider": "openai",
    "runtime_model_id": "<required-controlled-official-api-id>",
    "snapshot_id": null,
    "base_url": "<required-controlled-endpoint>",
    "endpoint_mode": "images.generations|images.edits",
    "credential_ref": "<secret-reference-only; never inline>"
  },
  "request": {
    "prompt": "<compiled-only-from-approved-facts>",
    "size": "<validated-for-runtime-model>",
    "quality": "<validated-for-runtime-model>",
    "background": "<optional-if-supported>",
    "output_format": "png|jpeg|webp",
    "output_compression": null,
    "n": 1
  },
  "reference_images": []
}
```

### 3.2 对官方 Image API 的最小 generation payload

只有在第 4 节门禁全部关闭后，generation 的最小网络 payload 才可形如：

```json
{
  "model": "<runtime_model_id>",
  "prompt": "<compiled_prompt>",
  "size": "<validated_size>",
  "quality": "<validated_quality>",
  "n": 1
}
```

目标 endpoint 语义：`POST <controlled-base-url>/images/generations`。若为 edit，则必须切换到 multipart `images/edits`，并携带已批准且逐张带 ID/version/SHA/role/order 的图像文件；不得把通用 URL 列表直接当作 OPC reference manifest。

**注意：** 本机 Hermes OpenAI provider 当前实际发送的 API 模型在源码中固定为 `gpt-image-2`，质量由虚拟层级映射；这与 Skill 要求“从受控配置取得实际 `runtime_model_id`、禁止写死/静默默认”的规则冲突。真实运行前必须解决该冲突并记录“受控值 → 实际发送值”的一致性校验。

## 4. 进入真实生成前必须关闭的阻断

1. **RUNTIME_MODEL_ID_BLOCKED**：建立受控、版本化配置，明确官方 API ID；不得仅依赖 provider 默认 `gpt-image-2-medium` 或源码常量。
2. **PROVIDER_SELECTION_BLOCKED**：显式配置并读回 `image_gen.provider=openai` 及受控模型/质量选择；确认完整 Hermes 启动后 active provider 与配置一致。
3. **ENDPOINT_BLOCKED**：明确本次测试是官方 OpenAI endpoint 还是经批准的第三方兼容 endpoint；若是第三方，必须有其 Images API、模型映射、数据处理和返回 schema 的批准证据。当前 `api-yue88.xyz` 不能被默认为 OpenAI 官方能力。
4. **PERMISSION_BLOCKED**：在获得允许发起网络检查/付费请求后，先以非生成方式核验模型可见性和组织/项目权限；若供应商无法提供无费用能力探针，则在明确成本批准后只做 1 个 eligible 资产的最小请求。当前权限保持 UNKNOWN。
5. **SCHEMA_BLOCKED**：固化 request/response/audit JSON Schema，包括条件必填、typed status、request ID、实际模型/endpoint、usage/error、reference manifest、输出 metadata、SHA-256、machine/human QC 和 lock record。
6. **RUNNER_BLOCKED**：实现或批准 OPC 专用 runner；runner 必须拒绝缺失 hash/approval/runtime_model_id 的输入，禁止静默改模型/参数，且只能返回一个正式候选。
7. **OUTPUT_BLOCKED**：锁定 OPC 输出根目录、资产 ID/版本命名、临时与正式目录隔离、不可覆盖和唯一 lock record 规则。`D:\Hermes\cache\images\` 只能作临时缓存。
8. **QC_BLOCKED**：真实产物必须完成 base64/字节解码、MIME/格式/宽高/alpha/bytes/SHA-256 读回，以及独立人工可见事实 QC；未完成时不得 `LOCKED`。

## 5. 安全判定

```text
credential_present = true
controlled_runtime_model_id_present = false
explicit_openai_image_provider_selected = false
endpoint_is_official_openai = false_or_unproven
images_api_permission_verified = false
opc_runner_present = false
opc_output_contract_ready = false
api_calls_made = 0
generated_images = 0
safe_to_generate = false
blocking_status = MODEL_BLOCKED
```

## 6. 本次只读证据来源

- `D:\Hermes\skills\creative\gpt-image-subject-assets-opc-test\SKILL.md`
- `D:\Hermes\xiaonan-memory\references\opc-gpt-image-subject-assets-verification-v0.1.md`
- `D:\Hermes\xiaonan-memory\references\opc-gpt-image-subject-assets-preflight-v0.1.md`
- `D:\Hermes\xiaonan-memory\references\opc-gpt-image-capability-research-2026-08-31.md`
- `D:\Hermes\config.yaml`（仅非密钥字段）
- `D:\Hermes\.env`（仅变量名与值是否非空）
- `D:\Hermes\auth.json`（仅凭证类型、来源、状态、endpoint；密钥/token/指纹值不输出）
- `D:\Hermes\hermes-agent\plugins\image_gen\openai\__init__.py`
- `D:\Hermes\hermes-agent\plugins\image_gen\openai\plugin.yaml`
- `D:\Hermes\hermes-agent\tools\image_generation_tool.py`
- `D:\Hermes\hermes-agent\agent\image_gen_provider.py`

最终结论：**本机有“可组装的基础件”，但没有完成目标 OPC 节点所需的受控运行配置与权限证据。现在进入真实生成不安全，必须保持 `MODEL_BLOCKED`，不得猜测可用性。**
