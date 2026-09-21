# UP Astral星芒 H3「全能生视频」工作流结构解剖（2026-09-10，源码+文件双证据）

> ⚠️ **作者归因（凡哥 2026-09-18 纠正：『**不是小黄瓜的**，我们的这个工作流的特点是有提示词优化功能的，你忘记了？』）**
> 这套工作流（`MiniMaxh-H3-全能生视频工作流 V3/V4` / `4-MiniMaxH3-V4-本地提示词优化版(对齐标准).json`）的作者是 **Astral星芒**（B站 space **176339505**），**不是「啦啦啦的小黄瓜」**——后者是**另一套 LTX2.5 放大方案**的作者，那套已被凡哥否掉，两套不可混记。
> **辨识特征（一眼区分）= 带本地提示词优化**（`QwenTE_*` / `comfyUI-llama-TE` 反推提示词，替代 MiniMaxH3MultimodalChat 云 API 节点）。
> **归因方法（别凭印象）**：读工作流 json 的 **MarkdownNote** 节点——里面写死了作者、教程链接、网盘地址。本例原话：`【AI视频】MiniMax-H3 全能生视频V4 工作流 latent分块二采版 (可直出2K)`／`【特点】文生、图生、参考生三合一；官方skill自动提示词；音频锁定；低显存二次采样；远景不崩脸`／`【作者】Astral星芒`／`【工作流使用讲解】https://space.bilibili.com/176339505`。

用于凡哥的 `MiniMaxh-H3-全能生视频工作流 V3/V4`。V3 = 本地提示词版（UP 原版参考），V4 = 新版（turbo + 潜空间放大 + 3 参考图）。

**权威基准 = 凡哥指定的那份"标准版"**（本例 `...-V4-2.json`：API 提示词节点 `1304`，且它 mode=4 bypass）。核对顺序：① 先看标准版怎么接 → ② 改法只允许"凡哥点名的那一处差异" → ③ **以标准版为底稿重建**，不在自己改过的版本上打补丁。
标准版 V4-2 关键事实（与本文件旧推断冲突时**以本节为准**）：`ref_image_0/1`（**2 张**）、Splitter `duration=9s`、`1329/1341.model ← 1299`、`1335` = **bypass 备用链**、`1318` 悬空、组开关 `1228`(matchTitle「二次采样」) + `1229`(matchTitle「提示词优化」，靠组名子串匹配)。
**V3 只用来理解"每根线的意图"**（槽位索引、开关语义、双链来源），**不作为接线判据**——V3 的接线在 V4 里已被重写。

## 1. 输入端：Media Loader → Reference Splitter

`MiniMaxH3MediaLoaderFantastic`(Media Loader) 的 `media_state` = 面板拖拽写入的 JSON 条目数组，
每条 `{"kind": "picture|video|audio|string", "enabled": bool, ...}`；`string` 条目就是**喂给 Qwen 的反推指令/风格文本**。

`MiniMaxH3ReferenceSplitter` 输出是**固定槽位**（源码 `h3_fant_nodes.py`，空槽填 None）：

| 输出索引 | 0–8 | 9–11 | 12–14 | 15–17 | 18–20 | 21 | 22 | 23 | 24 | 25 |
|---|---|---|---|---|---|---|---|---|---|---|
| 含义 | picture_1..9 | video_1..3 | video_audio_1..3 | audio_1..3 | string_1..3 | width_1 | height_1 | width_2 | height_2 | duration |

- `string_1` = 索引 18 → 接 QwenTE 图像推理的「提示词」输入（**反推指令模板**，不是最终提示词）
- `picture_1..3` = 索引 0/1/2 → 接「图片/图片2/图片3」
- `audio_1` = 索引 15 → 兼作参考音频（接 UnifiedToVideo 的 `ref_audios.ref_audio_0` 与音频锁）
- `width_1/height_1`(21/22) = 一采尺寸；`width_2/height_2`(23/24) = 二采/放大后尺寸
- **`short_edge_max`（★ 放大/二采的显存命门）**：源码 tooltip 原文 `Short edge max pixels; 0 = no scaling`——**`0` = 参考图完全不缩放**（只缩不放）。本项目那份工作流取的就是 **0**，喂 1440×2560（3.7MP）参考图 → 二采时**32GB 也暴显存**（症状 `cuMemFreeAsync CUDA_ERROR_INVALID_VALUE` + `Fatal Python error: Aborted`）。
  UP 官方教程原话：「你传入的图片如果是 2K 的，参考的图片就是 2K 的，这个时候就很容易暴显存」→ 解法：按目标短边设上限（**544 ≈ 一采短边最省 / 816 / 1088 按显存微调**），或喂之前先缩放参考图文件。→ 完整因果链见 `av-generation-troubleshooting/references/h3-refimage-scaling-vram-crash-2026-09.md`
- `align_to`(16) = 缩放后像素对齐，一般不动

## 2. 本地提示词组（QwenTE / comfyUI-llama-TE）

```
QwenTE_ModelLoader ──→ QwenTE_ImageInfer ──文本──→ ShowText ──→ UnifiedToVideo.prompt
        (主模型+mmproj)      ↑  提示词 ← 221[18]
                             ↑  系统提示词 ← Any Switch（5 个 PrimitiveStringMultiline：T2VA/I2VA/L2VA/FL2VA/REF2VA）
                             ↑  图片 ← 221[0]（V4 另接 图片2/图片3 ← 221[1]/[2]）
```
关键参数（V3/V4 逐项一致）：输入模式=图片、最大边长 1024、最大生成 token 512、温度 0.7 / top_p 0.59 / top_k 61 / 重复惩罚 0.99、seed 固定、不输出 think 块、**生成后自动卸载模型=True**（给 H3 腾显存）。

- `Any Switch (rgthree)` = **取第一个非空**，无 index 旋钮 → 五路系统提示词同时有内容时永远走 any_01(T2VA)，**模式切换靠 Ctrl+M 静音**其余节点。
- `Fast Bypasser (rgthree)`（"忽略节点"）= 一把子 bypass 指定节点；**bypass 掉图像推理 = 关闭"润色"**（其输出为空后由 Any Switch 落到兜底路）。

## 3. 「提示词润色开关」的真实接线（易被误判为死链）

```
1379 本地润色输出 ─┐
                   ├→ 1301 Any Switch(润色优先) → 1300 ShowText → 201 UnifiedToVideo.prompt
221[18] 原始文本 ──┘
```
润色开 → 走本地；润色关（bypass 1379）→ 自动落到原始文本。**201.prompt 必须接这条链的输出（1300），接到"只显示不传递"的节点上 = 开关失效。**

## 4. 一采 / 二采：两套独立模型链 + 各自 LoRA（V3 铁证，V4 最易错处）

V3 子图里有**两条结构完全相同**的链，各带一个 `LoraLoaderModelOnly`（turbo v4）：

| | 链 | 末端 LoRA | 喂给 |
|---|---|---|---|
| V3 | 1297:127 → SigmaShift → AttnBackend → … | `224` | `124`/`126` = **一采** |
| V3 | 1297:1221 → SigmaShift → AttnBackend → … | `1223` | `240`/`242` = **二采** |

**⚠️ 以参考版本定案，不要按"成对结构"推断**（2026-09-10 凡哥纠正）：
- V3（旧结构）确实是"一采一套、二采一套"
- **标准版 V4-2（权威）是"一套共用 + 备用链"**：`1329`/`1341`.model ← `1299`（一采二采**共用同一个 LoRA**）；`1335` = **mode=4(bypass) 的第二条链、无下游**——这是设计如此，**不是漏接**
- 我曾按 V3 的对称性把 `1329`/`1341` 改接 `1335`，被标准版推翻 → **同一现象在不同参考版下结论相反，判据永远是"凡哥指定的那份标准版"**
- 凡哥纪律：对齐参考版时**不要增加不要减少**，唯一允许差异＝他点名的那一处；对齐方式是**以标准版为底稿重建**，不是在自己改过的版本上打补丁

## 5. 音频链与"二采音频"

```
253 VAEDecodeAudio(一采 latent) ─┐
                                 ├→ 1210 ComfySwitchNode(是否锁定音频) → 227/245 VHS_VideoCombine.audio
226 MiniMaxH3AudioLock ← 221[15] ─┘ (on_true = 锁参考音频)
```
H3 是**音视频联合 DiT**，二采（tiled sampler）会**重新细化音频 latent** → 理论上只输出一采音频会与二采画面产生**口型/语速错位**。
**但标准版里二采 `VAEDecodeAudio`(`1318`) 本来就是悬空的**（音频一律走 `1210`）——"把二采音频接进音频链"属于**超越标准版的新设计**：必须先问凡哥，他确认后才新增节点。本次新增过一个 `Any Switch`（二采优先/一采兜底）方案，随后因"完全对齐标准版"被要求全部回退。**不要自行加节点。**

## 6. V4 相对 V3 的结构差异

| 项 | V3 | V4 |
|---|---|---|
| 参考图 | 1 张 | 3 张（`ref_image_0/1/2`）|
| 一采 | beta 8 步 denoise 1 | simple 6 步 + turbo v4 LoRA |
| 放大 | 解码 → RTX VSR 图像放大 → 重编码 → **第二个 UnifiedToVideo 重算高清条件** → 2 步 denoise 0.3 | **潜空间放大 1.5×（`MinimaxH3LatentUpscaler3D`）→ TiledSampler 分块细化 4 步**（无第二个 UnifiedToVideo）|
| 注意力 | comfy kitchen | 省显存 Sage 补丁 + BlockSparse(Sol-Attn) |
| 间隔 | — | ModelPreviewOverrideKJ + taeh3 预览 |

`TiledSampler` 源码明确带 **R2V 参考条件同步裁切**（分块采样时按 tile 裁切条件里的参考图），所以 V4 才不需要第二个 `UnifiedToVideo`。

## 7. 推荐分组（凡哥工作流的 6 区）

① 素材输入（说明/MediaLoader/Splitter）→ ② 本地提示词(QwenTE) → ③ 模型加载(子图/1采LoRA/2采LoRA/预览覆盖) → ④ 一次采样 → ⑤ 放大链(二采) → ⑥ 解码与输出（含音频开关与二采音频切换）。
**开关/兜底类节点归入它服务的功能区，不要单独隔离成"待删区"。**
