# V4 全能工作流 OPC/API 交接（2026-09-10 云上）

## 背景与目标
- 云上（智算云扉 waas，RTX 5090 32GB）跑通的 `4-MiniMaxH3-V4-本地提示词优化版(对齐标准).json` 要交接给小何做 OPC 平台集成。
- 模式：OPC 平台发指令 → agent（小何自己写）→ 调云上 ComfyUI API → 出片回 OPC。通信方式与产物回传由小何定。
- 规格（凡哥定）：默认单一直出 **1920×1088**、无其他选项；视频 **5~15 秒**；素材=人物/场景/道具/分镜图 + 提示词；**提示词唯一输入口 = `221.string_1`**。**保留"本地 Qwen 提示词优化"步骤**（凡哥拍板）。
- 交付包三件：① API 格式工作流 JSON（官方界面导出）② 接口说明文档 ③ Python 示例（上传→提交→轮询→取片）。

## 官方素材上限（三源一致：MiniMax 官方 GitHub README / HuggingFace 模型卡 / ComfyUI 官方文档）
| 类型 | 上限 | 附加约束 |
|---|---|---|
| 图片 | **≤9** | 宽高比 0.4~2.5，≥256×256；自动降采样到 2048 短边（只降不升）|
| 视频 | **≤3** | 每段 2–15s；总长 ≤15s；24fps |
| 音频 | **≤3** | 每段 2–15s；总长 ≤15s；**不能单独提交**（须搭配图或视频）|
| 合计 | **≤12 文件** | 最易忽略的一条 |

- 输出侧：时长 4–15s、24fps、帧数 107–362 按 17 递增（17k+5 网格）。
- 官方 `duration` 参数说明（FLOAT 秒）：`max(5, round(duration*fps))` snapped up to the 17k+5 grid → **5s→124帧(5.17s)、15s→362帧(15.08s)**，节点自动算帧数，接口只给秒。
- `ref_images`/`ref_videos`/`ref_video_audios`/`ref_audios` 都是 `COMFY_AUTOGROW_V3`（自动增长口，**节点本身不卡数量**）→ **数量约束必须做在接口层**（超限拒绝），否则模型端会崩坏/不听指令。

## 工作流结构图谱（对齐标准版）
- **220 MiniMaxH3MediaLoaderFantastic**（素材面板）：唯一输入 `media_state`（STRING，JSON 列表）。条目形如 `{"kind":"picture","file":"minimax_h3/png_xxxx [input]","name":"齐白兰四视图.png","duration":null,"width":1309,"height":736,"has_audio":false,"audio_mode":"off"}` 与 `{"kind":"string","text":"<风格串>"}`。输出 references(H3_REFS) → 221。
- **221 MiniMaxH3ReferenceSplitter**：输入 references；widgets：`aspect_ratio="16:9 (Widescreen)"` / `size1=960×544` / `size2=1920×1088` / `duration=15.0` / `short_edge_max=0` / `align_to=16`。
  - 22 个输出槽位（截图实证）：`picture_1~9`、`video_1~3`、`video_audio_1~3`、`audio_1~3`、`string_1~3`、`width_1`、`height_1`、`width_2`、`height_2`、`duration`。
  - 已接线：picture_1/2→201.ref_image_0/1（&1379 图片口）；audio_1→201.ref_audio_0（&1379）；string_1→1301.any_03（&1379.提示词）；width_1/height_1→201.width/height；duration→201.duration（&1311）。**width_2/height_2/size2 悬空**（标准版原样，`links=[]`）。
- **201 MiniMaxH3UnifiedToVideo**：clip/video_vae/audio_vae←1297 子图；prompt←1301；`ref_images.ref_image_N`（AUTOGROW）；ref_image_size、first_frame/last_frame、ref_videos/ref_audios 可选；width/height/duration←221；mode=auto（按接线自动判任务）。
- **1301 Any Switch (rgthree)**：any_01←1379.Qwen 输出、any_03←221.string_1 → 取第一个非空 → 201.prompt。**云端 object_info 证实有后端实现 → API 格式可保留**（不必手改接线）。
- **1379 QwenTE_ImageInfer**（本地提示词优化）：图片口 8 个；提示词入←221.string_1；系统提示词←1386(Any Switch)←1387/1385/1384/1383/1382（5 套，前端 Fast Bypasser 1381 控单选；JSON 里当前 1387 启用）。
- **1297 子图**（type=UUID `d581531a-…`，名"模型加载"）：内部 13 节点（UNETLoader fl2va_int8 + UNETLoader hybrid_ref2va + CLIPLoader qwen3vl_nvfp4_awq + VAELoader video_int8/audio_fp32 + SigmaShift×2 + ModelAttentionBackend×2 + SageAttentionPatch×2 + BlockSparseAttention×2）。输出 MODEL/MODEL_1/CLIP/VAE/VAE_1。**API 格式需铺平展开**。
- **二采链**：201.av_latent →（226 AudioLock bypass 透传）→1367 VRAM_Debug→1313 LTXVSeparateAVLatent→**1317 MinimaxH3LatentUpscaler3D（scale）**→1316 LTXVConcatAVLatent→1330 MiniMaxH3TiledSampler→244 VAEDecode→245 VHS_VideoCombine（最终输出，prefix "Minimax"）。
- bypass(mode=4)：226 MiniMaxH3AudioLock（av_latent 透传到下游 1367）；1335 LoraLoaderModelOnly（无下游）。
- 纯前端节点（API 导出时消失，不影响出片）：MarkdownNote(142)、Fast Groups Bypasser(1228/1229)、Fast Bypasser(1381)、ShowText|pysssss(1300/1378)。

## 分辨率实测与倍率决策（2026-09-10）
- 成品实测（`Minimax_00003-audio.mp4`）：**1440×832** / 24fps / 362 帧 / 15.084s = 960×544 × `1317.scale`(1.5)，832 = 816 对齐 32。
- 与标准版逐项 diff：**size2 悬空 + scale=1.5 都是标准版原样**（凡哥版唯一差异 = duration 15 vs 9）。**UP 原版同样出 1440×832**——"1920×1088"只是分隔器留的备选档位，从未接线。
- **要 1920×1088 → `1317.scale` 改 2.0**（960×2=1920、544×2=1088 严丝合缝）。凡哥拍板 A（代价：二采像素 +74%，预计 1:34→~2:45）。
- 改法（JSON 双写，见下"双参数存储"）：`widgets_values[2]` 和 `widgets_values_named['mode.scale']` **两处都改**。凡哥也可自行在界面改（Ctrl+F 搜 "Upscaler" 定位节点）。
- 该改动 = 交付版第 2 处偏离标准版（第 1 处=本地提示词优化）——**凡哥已明示批准**，勿再当"擅自改动"。

## 核心坑：ComfyUI 新版 JSON 双参数存储（必背）
- 节点 widget 值存两份：`widgets_values`（数组，按顺序）；`widgets_values_named`（dict，按名称，**key 含点号**如 `mode.scale`、`aspect_ratio.size1`）。
- **手改 JSON 必须两处同改**。⚠️ **2026-09-10 实测更正（推翻旧结论）**：同一工作流里 221 节点 `widgets_values` 的 duration=**15** 而 `widgets_values_named['duration']`=**9**（不一致），实际出片 **15.084s** → **真正生效的是数组 `widgets_values`**（此前"以 named 为准"是错的，named 只是元数据/缓存，可能残留旧值）。→ 两处同改仍是保险做法；**API 格式只有一套参数，无此坑**（AGENT 走 API 不受影响）。
- 附带收益：`widgets_values_named` 的 key ≈ API 格式 inputs 的 key（对动态口/子参数尤其有用），是验证官方导出格式的参照。

## 排查与操作技巧
- **节点权威定义**：`curl -s http://127.0.0.1:8188/object_info/<NodeName>`（实例自答，比翻源码准）。可见新类型模板：AUTOGROW_V3 的 template/prefix/min、DYNAMICCOMBO 的 options 与 inputs。
- **节点 ID 显示**：设置（⚙️ 或 Ctrl+,）→ 搜 `ID` → 「Node ID Badge Mode」→ `Show all`。
  - ⚠️ **徽标位置 = 节点【右上角】**（官方前端源码 `BadgePosition.TopRight`），别往左上角找。
  - ⚠️ 该选项**只有 `None` / `Show all` 两个值**（无 hover 中间态）。
  - ⚠️ **不需要重启 ComfyUI**：设置改动会自动触发画布重绘（源码 `setDirty(true,true)`）；不生效先 `Ctrl+Shift+R` 强刷 + 手点进 **LiteGraph → Node → Node ID badge mode**（搜索框有搜不全的已知 bug）。
  - ⚠️ 已知冲突：**ComfyUI-Manager** 等插件自带徽标实现会打架（官方 issue #9959）。
  - **更省事：直接按节点类型名定位**（同类唯一，Ctrl+F 搜类型名）——给凡哥指路优先报类型名，不报数字 ID。
- **判定输出口是否接线**：UI JSON 里看 `outputs[].links` 是否空数组。
- **改工作流前先 diff 标准版**：`D:\Hermes\attachments\4-MiniMaxh-H3-全能生视频工作流-V4-2.json`（411KB）——防止把"标准版原样"误判为"被改错"。
- **UI→API 转换必走官方**：ComfyUI 界面「工作流(Workflow) → 导出（API）」一次导出 → 之后纯 API 调用。理由：subgraph 铺平 / 动态口点号 key（`ref_images.ref_image_0`、`aspect_ratio.size1`）/ bypass 消解**只有官方导出才准**；手写转换器=绕开官方（凡哥铁律禁止）。打开云端界面：平台端口映射，或 SSH 隧道 `ssh -N -L 8188:127.0.0.1:8188 waas`。
- 耗时参考：15s 视频全链 303s（一采 6步 60s + 二采 4步 94s + 其他 149s）。

## 调用格式要点（给小何的接口）
- 提交：`POST /prompt`，body `{"prompt": <API格式工作流>, "client_id": "..."}`；轮询 `GET /history/{id}`；取片 `GET /view?filename=…&subfolder=…&type=output`；上传图 `POST /upload/image`。
- 提示词语法：模型用 `<Picture N>` / `<Audio N>` 引用素材槽位（标准版模板原文即如此）。
- 参数注入点（API 格式）：`220.media_state`（素材 JSON）、`221.duration`（5~15）、尺寸由 `1317.scale=2.0` 锁死；其余固定。
- 输入约束（接口层硬编码）：图≤9 / 视频≤3(2-15s，总≤15s) / 音频≤3(2-15s，总≤15s，须陪图或视频) / 合计≤12 / 提示词 1 条。

## 未决/待办（2026-09-10 更新）
- ✅ **交接包已产出**：`D:\数字资产\云电脑工作流\H3-OPC交接包-2026-09-10\`（+ 同名 `.zip`，20.6KB / 6 文件）。凡哥明示**不含工作流文件**（小何有云端操作权限，自行界面「导出(API)」）。内容：`README.md` / `接口规格.md` / `素材与提示词.md` / `运维与故障.md` / `待确认清单.md` / `examples/opc_client.py`。
- `examples/opc_client.py` **已实测**：`--help` 正常；输入校验 + 注入逻辑 13 项单测全过。设计要点：**按 `class_type` 查节点、不硬编码数字 ID**（规避 API 导出 subgraph 铺平后 ID 变化）；`inject()` 只动 `media_state`/`duration`/`mode.scale` 三处，实测不污染其他参数。
- **待云上确认**（已写入交接包《待确认清单.md》，含验证方法）：① ⭐`media_state.file` 的 `"minimax_h3/png_9122 [input]"` 格式在 API 注入时怎么写（面板私有格式、无官方文档，给的是实测反推法而非结论）② `kind=video/audio` 条目字段结构（无样本）③ API 导出后节点 ID 是否变化 ④ 倍率 2.0 出片实测（应 1920×1088）⑤ Qwen 优化在纯 API 下是否触发 ⑥ 提示词注入路径唯一性 ⑦ 云端对外访问地址。
- 官方界面「导出(API)」由小何侧执行。
