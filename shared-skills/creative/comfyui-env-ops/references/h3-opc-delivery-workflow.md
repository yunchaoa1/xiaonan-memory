# 云端跑通版「H3 OPC 交付版」工作流（本机复现对照表）

> 凡哥 2026-09-14 指令：**『以我们在云电脑上跑通的那一版做最终版，不要改任何的』**
> 本表 = 该版的事实档案 + 本机缺件实测，用于「只装环境、不碰工作流」地把云端那版复现到本机。

## 一、版本身份

| 项 | 值 |
|---|---|
| 工作流文件 | ⚠️ **以「本地提示词优化版」为准** —— 凡哥 2026-09-14 二次确认：『**要本地提示词优化的那个版本**，然后缺什么补什么』→ `D:\数字资产\云电脑工作流\4-MiniMaxH3-V4-本地提示词优化版(对齐标准).json`（164 KB · 9-10 15:41）。同目录 `5-MiniMaxH3-OPC交付版-1088P.json`（101 KB · 9-10 17:34）是它之后的交付版，**两侧节点类型集合互差为空**，唯一实质差异 = 放大倍率 **1.5 → 2.0**；而**实测跑出过片的是 1.5×（1440×832）**，2.0×（1920×1088）在交接包的《待确认清单》里标着「未验证」→ 按凡哥指定取 **1.5× 那版** |
| 同目录关联件 | `H3-OPC交接包-2026-09-10/`（README / 接口规格 / 素材与提示词 / 待确认清单 / 运维与故障 / examples/opc_client.py）；UP 原版 `4-MiniMaxh-H3-全能生视频工作流-V4-2.json`（411 KB · 9-10 15:09） |
| 云端实例 | 智算云扉 · **RTX 5090 32GB** · ComfyUI **v0.35.0** |
| 交付规格 | **1920×1088 / 24fps / 5~15 秒** |
| 结构 | 顶层 **43 节点 / 30 类型** + 1 个打包子图「模型加载」（13 节点 / 7 类型，**子图内无缺件**） |
| 对外接口 | 3 个注入点：`MiniMaxH3MediaLoaderFantastic` / `MiniMaxH3ReferenceSplitter` / `MinimaxH3LatentUpscaler3D` |
| 启动参数 | **`--disable-cuda-malloc`** —— 不带则二采阶段崩在显存分配上（`Allocation on device`，**不是显存不够**，是 cudaMallocAsync 释放出错；依据 ComfyUI 官方 issue + `cuda_malloc.py` 源码） |

**本机运行实例（2026-09-14 实测）**：`D:\SDkecheng\ComfyUI`（`.venv`）· ComfyUI 0.35.0 · torch **2.13.0+cu130** · RTX 5080 **Laptop 16GB** · 端口 **18188**（不是默认 8188）。

## 一之二、多份相似工作流怎么分辨「哪一份是那一版」（判定法，2026-09-14 实测）

同一目录常有 3~5 份长得像的工作流（UP 原版 / 你改过的 / 交付版）。**别看文件名猜，做两步对比：①节点类型集合互差 ②关键节点 `widgets_values`。**

```python
import json
def load(p):
    w = json.load(open(p, encoding='utf-8')); ns = list(w.get('nodes', []))
    for sg in (w.get('definitions', {}) or {}).get('subgraphs', []) or []:
        ns += sg.get('nodes', [])          # 子图内节点要单独收集
    return w, ns
# ① 两份的 type 集合互差 → 谁「独有」什么节点
# ② 关键节点 widgets_values → 例：MinimaxH3LatentUpscaler3D 的第 3 个值 = 放大倍率
```

三份实测结论：

| | 文件 | 提示词优化 | 放大倍率 | 判定 |
|---|---|---|---|---|
| C | `4-MiniMaxh-H3-全能生视频工作流-V4-2.json`（UP 原版 · 411 KB） | ❌ **独有 `MiniMaxH3MultimodalChat`**（要云 API key 的那个，且 mode=4 bypass） | — | 被改的对象 |
| **B** | `4-MiniMaxH3-V4-本地提示词优化版(对齐标准).json`（164 KB） | ✅ `QwenTE_ModelLoader` + `QwenTE_ImageInfer` | **1.5** | **凡哥指定最终版**（实测出过片） |
| A | `5-MiniMaxH3-OPC交付版-1088P.json`（101 KB） | ✅ 同 B | **2.0** | B 的后续交付版；与 B 的类型集合互差为空 |

**凡哥凭记忆说「改过某个节点」时，用节点集差去证实，不要只回"对/不对"**：本例 C 独有的是 `MiniMaxH3MultimodalChat`，而 A/B 都换成了 `QwenTE_*` → **他记的那处「API 提示词优化 → 本地提示词优化」确认存在**，且能顺带定出哪几份是改后的。

⚠️ **同名 ≠ 同内容**：同一份工作流在**聊天附件**与 **ComfyUI `user/default/workflows/`** 里的体积会不同（本例 69,760B vs 88,010B，因为后者在 UI 里保存过）。**体检结论前后对不上时先比 size/hash，别怀疑脚本。**

## 二、本机缺件实测（对**这一版**，2026-09-14）

### 真缺节点：9 种 → 4 个插件

| 缺的节点 | 来源插件 | 星 / 最后推送 | 附加依赖 |
|---|---|---|---|
| `MiniMaxH3UnifiedToVideo`<br>`MiniMaxH3AudioLock`<br>`MiniMaxH3ReferenceSplitter`<br>`MiniMaxH3MediaLoaderFantastic`<br>`MiniMaxH3TiledSampler` | **`oufeixinxinren/ComfyUI-MiniMax-ContextIR`** | 33 · 9-12 | `av` ✅ 已装（18.0.0） |
| `MinimaxH3LatentUpscaler3D` | `LBH-123-AI/Comfyui_Minimax_h3_latent_Upscaler` | 595 · 8-28 | 配套 checkpoint → `models/latent_upscale_models/` |
| `QwenTE_ModelLoader` / `QwenTE_ImageInfer` | `tl2012tl/comfyUI-llama-TE` | 184 · 8-28 | ⚠️ `llama_cpp` **未装**（JamePeng fork wheel）+ `models/LLM/` **空的**（GGUF 未下，几 GB 起） |
| `LayerUtility: NumberCalculatorV2` | `chflame163/ComfyUI_LayerStyle` | 3160 · 9-03 | ⚠️ `blend_modes` 未装（`skimage` / `blind_watermark` / `wget` 已有） |

**ContextIR 一包提供 6 个**（含此前怀疑是「YCNodes 改名版」的 `MiniMaxH3TiledSampler` —— 它就是 ContextIR 的，不是改名版）。同包还提供本机已注册的 `MinimaxHailuo03ContextIRNode`（该名属 **ComfyUI 核心**，与 ContextIR 插件无关）。

`ComfyUI-MiniMax-ContextIR` 的节点全集（源码 grep 实证）：`MiniMaxH3UnifiedToVideo` / `MiniMaxH3UnifiedContextIR` / `MiniMaxH3ContextIR` / `MiniMaxH3AudioLock` / `MiniMaxH3ReferenceSplitter` / `MiniMaxH3MediaLoaderFantastic` / `MiniMaxH3TiledSampler` / `MiniMaxH3ConcatAVLatent` / `MiniMaxH3ConcatAVExtension` / `MiniMaxH3MultimodalChat` / `MiniMaxH3SigmaRefiner` / `MiniMaxH3ResolutionSelector` / `MiniMaxH3ResolutionExtension`。依赖只有 `av>=12.0.0`。

### 假阳性（**不要报缺**，3 类）

| 假阳性 | 判定依据 |
|---|---|
| `Fast Bypasser (rgthree)` ×1、`Fast Groups Bypasser (rgthree)` ×2 | 只在 rgthree 的 **JS/TS** 注册（`src_web/comfyui/fast_groups_bypasser.ts`），**永不出现**在 `/object_info`。本机 rgthree 正常（IMPORT FAILED = 0） |
| `d581531a-6a61-42b8-8f7d-8c6c8f913be1` ×1 | = 子图「模型加载」的 `id`，**子图实例**不是节点 |
| `default` / `minimax` | 是 `UNETLoader` 的 `weight_dtype` / `CLIPLoader` 的 `type`（`widgets_values[1]`），不是模型名 |

### 模型：真缺 **3** 个（不止标准加载器里那两个）

⚠️ **方法坑：只扫标准加载器（`UNETLoader` / `CLIPLoader` / `VAELoader` / `LoraLoaderModelOnly`）的 `widgets_values[0]` 会漏报。** 第三方插件把自己的模型藏在**自己的 widget** 里 —— 本例 `MinimaxH3LatentUpscaler3D` 的 `widgets_values[0]` 就是放大模型名。判「还缺几个模型」必须**遍历全部节点 widget 里一切像文件名的值**（`.safetensors` / `.gguf` / `.pth`），否则会向凡哥少报。本次就因此先说「只差放大模型」、随后又改成「差 3 个」，来回改口。

**第 3 个缺件模型 = `minimax_h3_bf16_CONSERVATIVE_v5.safetensors`**（`MinimaxH3LatentUpscaler3D` 引用，落 `models/latent_upscale_models/` **根目录**——该插件扫平铺目录、不放子目录）。
2026-09-14 已找到公开源：HF **`Asirus/Minimax-H3-Latent-Upscaler-BF16-MAXQUALITY`**，**690,593,160 字节**，文件名逐字一致 —— **推翻**更早「UP 独家、HF/ModelScope/Manager 全网查不到」的结论。教训：网盘件/自制件会随后被搬上 HF，**几天前的「查不到」不能当定论**；且**要进仓库文件列表看**（`api/models/<repo>?blobs=true`），按文件名搜搜不到 ≠ 不存在。

下面 2 个来自标准加载器：

| 工作流引用 | 本机现状 |
|---|---|
| `MiniMax-H3\minimax_h3_fl2va_pruned_**w4a8_mixed**.safetensors` | 本机是 `minimax_h3_fl2va_pruned_int8_convrot` —— **量化版本不同，算缺** |
| `minimax_h3_ref2v_turbo_4step_v0.1_comfyui_bf16.safetensors` | 本机是 `fl2v_lightx2v_turbo_4step_v0.1` / `fl2v_turbo_4step_v1.1_768p` —— **名字不同，算缺** |

**本机已有 4 个（只是目录前缀不同，不要误报）**：

| 工作流写法 | 本机实际路径 |
|---|---|
| `MiniMax-H3\qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors` | `text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors` |
| `MiniMax-H3\minimax_h3_video_vae_int8_convrot.safetensors` | `vae/minimax_h3_video_vae_int8_convrot.safetensors` |
| `MiniMax-H3\minimax_h3_audio_vae_fp32.safetensors` | `vae/minimax-h3/minimax_h3_audio_vae_fp32.safetensors` |
| `MiniMax-H3\minimax_h3_hybrid_fl2va_ref2va_b25-49-int8.safetensors` | `diffusion_models/minimax_h3/minimax_h3_hybrid_fl2va_ref2va_b25-49-int8.safetensors` |

## 三、本机目录名与工作流引用不一致 —— 按凡哥铁律「改环境不改工作流」

工作流引用 `MiniMax-H3\…`，本机实际子目录名是：

```
diffusion_models/minimax_h3/     text_encoders/nimimax-h3/     vae/minimax-h3/     loras/minimax_h3/
```

**正解**：在本机把 `MiniMax-H3/` 这个目录名造出来（**用 `ln` 硬链接现有文件 —— 不要用 `ln -s`**：Windows 上 MSYS 符号链接常需管理员/开发者模式，硬链接在同一 NTFS 盘普通权限即可且**零额外空间**；建完必验 `stat -c%h <文件>` 应 = **2**、`stat -c%s` 与源一致），让工作流引用原样命中 —— **不是**去改工作流里的路径。同理，此前在本机做过的 `AudioInfoNode`→`SWAN_AudioInfo`、LoRA 换名等适配**全部作废**（那是「工作流向本机靠」，凡哥明确否掉）。

## 四、复现顺序（全为「装环境」，不碰工作流）

1. 装 ContextIR + LatentUpscaler（缺件大头）
2. 装 llama-TE（JamePeng wheel + 下 GGUF 到 `models/LLM/`，**用 `-o` 直接存成工作流要的名字**）
3. 装 LayerStyle（一个 `NumberCalculatorV2` 换来 173 节点重依赖 —— 已向凡哥报代价，他未反对则照装）
4. 下 3 个缺模型 + 建 `MiniMax-H3/` 子目录**硬链接**（三处：`diffusion_models/` `text_encoders/` `vae/`；已存在的跳过）
5. 重启实例带上 `--disable-cuda-malloc`，重跑 `scripts/audit_workflow_missing_nodes.py` → 目标 **0 缺**

   **✅ 2026-09-14 本机已全部完成（实测记录，勿重复劳动）**
   - 4 插件全装；`llama_cpp 0.3.49`（JamePeng **cu130-cp312-win** wheel，`Qwen35ChatHandler` 已验）+ `diskcache` + `blend_modes`
   - **6 个模型全部逐字节校验通过**：w4a8_mixed `12,540,858,008`（HF `Kijai/MiniMax-H3-experimental`，官方 awesome 列表点名）/ ref2v_turbo LoRA `1,956,193,000`（HF `Comfy-Org/MiniMax-H3` 的 `loras/`，**工作流写裸文件名 → 必须放 `loras/` 根**，放子目录会「选不到」）/ CONSERVATIVE_v5 `690,593,160`（HF `Asirus/…MAXQUALITY`）/ QwenTE 主模型 `21,694,740,192` + mmproj `902,822,656`（HF `llmfan46/…`，**存盘用工作流里的短名**）
   - `MiniMax-H3/` 三处硬链接已建（`stat -c%h` = 2 验证）
   - 重跑体检：**节点 0 缺**（服务端已注册类 3015 → **3211**）；`start_comfyui.bat` 已加 `--disable-cuda-malloc`（备份 `.bak.20260914`）
   - **诚实边界：端到端出片尚未实测** —— 只验到「节点齐 + 模型齐 + `/prompt` 校验放行」；工作流一字未改。最后一步是凡哥自己开跑（首跑要加载 ~20GB GGUF，慢属正常）
6. 把工作流副本放进 `user/default/workflows/`（只加文件，不改内容）

## 五、云端运维要点（改自交接包 `运维与故障.md`）

- **每任务前 `POST /free`**（`{"unload_models":true,"free_memory":true}`）—— 任务失败/中断后模型不自动卸载
- 性能参考：15 秒全链约 **303 秒**（一采 60s / 二采 94s / 其他 149s）；倍率 1.5→2.0 后二采约 2~3 分钟
- 素材上限：图片 ≤9 / 视频 ≤3 / 音频 ≤3 / **合计 ≤12** —— **超限不报错，只出坏片**，必须在提交前拦
- 提交必须是 `{"prompt": <工作流>, "client_id": "..."}` 包一层，否则返 `no_prompt`
- ⚠️ **UI 格式 JSON 里参数存两份**：`widgets_values`（数组）+ `widgets_values_named`（字典），**实测可能不一致**（云端工作流有一处数组 15 / named 9，实际生效的是**数组**值）→ 改 UI JSON 两处都要改；走 API 格式不受影响
- 出片分辨率 = 一采尺寸 × 放大倍率；时长按 5s→124 帧（实 5.17s）/ 15s→362 帧（实 15.08s）对齐帧网格，**比设定值略长是正常的**

## 六、同目录其它候选工作流的缺件（2026-09-14 实测，供切换时参考）

| 工作流 | 缺节点 | 缺模型 |
|---|---|---|
| `4-MiniMaxh-H3-全能生视频工作流-V4-2.json`（411 KB） | 10 种（同上 9 种 + `MiniMaxH3MultimodalChat`） | `minimax_h3_ref2v_turbo_4step_v0.1_comfyui_bf16.safetensors` |
| `4-…-V4.json` | 12 种 | `minimax_h3_turbo_v4_step600_ema.safetensors` |
| `4-…-V3-本地提示词.json` | 10 种（含 `MiniMaxH3ConcatAVLatent` / `QwenTE_*`） | `MiniMax-H3\minimax_h3_ref_lora_rank_256_bf16.safetensors` |
| `H3长视频MV_context_lightx2v_长视频.json`（本机 9-11 已部署） | **0 种**（已做完本地适配，**但不符合「云电脑原样」要求**） | `MiniMax_H3_Combat_LoRA.safetensors`、`MiniMax-H3-Ref2VA-int8-convrot.safetensors` |

⚠️ **同名的两份内容不同**：`H3长视频MV_….json` 在 `D:\Hermes\attachments\` 是 **69,760B**（含 `AudioInfoNode`），在 ComfyUI `user/default/workflows/` 是 **88,010B**（已换成 `SWAN_AudioInfo`）。体检结论对不上时先比 size/hash。
