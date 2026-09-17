# H3 生态模型来源总表（2026-09-10 实测，云端智算实例）

用途：凡哥拿 UP（小黄瓜）工作流来配模型时，先查本表 → 三步定位（公模库 find → 本地 models find → HF 搜源）。**绝不只回一句"没有"。**

## 查询三步（每次都要走全）

```bash
# ① 公模库（共享模型空间，软链零下载）
find /datasets -iname "*<关键词>*" 2>/dev/null | head -10
# ② 本地实例目录
find /home/waas/ComfyUI/models -iname "*<关键词>*" 2>/dev/null | head -15
# ③ HF 搜发布源
curl -s "https://hf-mirror.com/api/models?search=<关键词>" | python -c "import sys,json;[print(m['modelId']) for m in json.load(sys.stdin)[:20]]"
# ③b 看仓库文件+真实大小
curl -s "https://hf-mirror.com/api/models/<repo>?blobs=true" | python -c "import sys,json;[print(f['rfilename'], f.get('size',0)//1048576,'MB') for f in json.load(sys.stdin)['siblings']]"
```

## 主模型 diffusion_models

| 文件 | 大小 | 来源 | 公模库 |
|---|---|---|---|
| **`Minimax-h3_Singularity_ref2va_Pruned_v1.3_int8.safetensors`** | **20,967,647,456**（19.53 GiB） | HF `WarmBloodAban/Minimax-h3_Singularity`（14.1 万下载，9-12 更新） | ✅ 云端 `/datasets/.../diffusion_models/`；**本机 2026-09-14 经 hf-mirror 直连下载** |
| `Minimax-h3_Singularity_ref2va_v1.3_int8.safetensors`（完整版） | 34,004,507,622（31.67 GiB） | 同上 | ❌ |
| `minimax_h3_ref2va_int8_convrot.safetensors` / `_pruned_int8_convrot` | — | 官方 repackaged | 实例已软链 |

Singularity = 融合版，UP 主称可**有限缓解人物油腻 / 快速动作变形**。用法：**替换工作流 UNET / diffusion_models 加载项**（是主模型不是 LoRA），放 `models/diffusion_models/`。

**同系列仓库（2026-09-14 核实）**：主仓库里还带一份提示词规范 `MiniMax_H3_Singularity_Prompt_Writing_Specification_Enhanced_EN.md`（19,775 字节，值得一并取）；`TenStrip/Minimax-h3_Singularity-Lora` = 两个 LoRA（`..._128spect-fro95_lora.safetensors` 1,277,206,240 / `..._64-fro95_lora.safetensors` 655,311,872）；`WarmBloodAban/Singularity-LTX-2.3_OmniCine_V1` = LTX-2.3 融合 LoRA（`Singularity-LTX-2.3_OmniCine_V1.safetensors` 2,695,584,680 等 3 个）。

⚠️ **「融合模型」有两个，别混**：工作流原生 + 云端实际在用的是 **`minimax_h3_hybrid_fl2va_ref2va_b25-49-int8`**（下节，fl2va 基底 + ref2va 参考通路）；**Singularity 是「替换 UNET 加载项」的可选件，云端与工作流都没用它**。凡哥提"融合模型"时**先问清是哪一个**，两者定位不能互相替代。

### H3 Hybrid 融合主模型（fl2va 基底 + ref2va 参考通路，2026-09-11 核实）

HF `smhfacct/Minimax-H3-fl2va-ref2va-hybrid-models`（226★，仓库 83.9GB，4 个变体**各 19.53GB**）：

| 文件（注意仓库已 rename，实际名带 `-int8`） | 取 ref2va 的块 | 取向 |
|---|---|---|
| `minimax_h3_hybrid_fl2va_ref2va_b30-49-int8.safetensors` | 30–49（后20/50） | 最接近 fl2va，画质最好、参考力最弱 |
| **`minimax_h3_hybrid_fl2va_ref2va_b25-49-int8.safetensors`** | 25–49（后25/50） | **作者推荐首选**，画质略高、参考略降 |
| `minimax_h3_hybrid_fl2va_ref2va_b20-49-int8.safetensors` | 20–49（后30/50） | 偏 ref2va，参考更准、画质略降 |
| `minimax_h3_hybrid_fl2va_ref2va_b15-49-int8.safetensors` | 15–49（后35/50） | 最接近 ref2va，参考最强、画质最低 |

- **原理**：两版 H3 绝大多数权重逐张量比对 cos ≥0.9997（QKV/MLP/RMSNorm/patch proj/RoPE/token refiner 几乎 bit-identical），差异几乎全在**每块 `adaln_proj`**（把文本/音频/视频/**参考**模态信号注入残差流的调制投影）。所以做法 = 全部用 **fl2va** 做基底，只把后面若干块的 `adaln_proj` 换成 **ref2va** 的 → 保留参考通路、保住 fl2va 画质。纯权重选择合并，**无训练/无微调**。
- **基底 = pruned int8-convrot 官方版**（README 明写）→ 与官方 `*_pruned_int8_convrot.safetensors` **同架构同张量布局**，是 ref2va 的 **drop-in 替换**（换 UNET/diffusion_models 加载项即可，工作流其余不动）。
- 定位：**参考条件生成**（图/视频/音频参考）用；非参考任务不会超过 fl2va（权重本就大半相同）。实验性主观调参产物，作者自述未经系统验证。
- ⚠️ 报文件名必须逐字：仓库做过 `..._b25-49.safetensors` → `..._b25-49-int8.safetensors` 的 rename；写漏 `-int8` 或把 `fl2va` 打成 `f12va` → 节点里选不到（"缺模型"）。

## VAE（注意 int8 版只有第三方发）

| 文件 | 大小 | 来源 | 本地实例 |
|---|---|---|---|
| `minimax_h3_audio_vae_fp32.safetensors` | 577MB | HF `Comfy-Org/MiniMax-H3` `vae/` | ✅ 已有 |
| `minimax_h3_video_vae_fp16.safetensors` | 4967MB | HF `Comfy-Org/MiniMax-H3` `vae/` | ✅ 已有 |
| **`minimax_h3_video_vae_int8_convrot.safetensors`** | **3025MB** | HF `GuangyuanSD/minimax_h3_video_vae_int8_convrot` | ❌ 需下载 |
| `taeh3.safetensors`（TAE 轻量预览 VAE） | **9,791,388 字节**（9.34 MiB） | **HF `GuangyuanSD/minimax_h3_video_vae_int8_convrot`**（2026-09-15 本机实测下载成功，hf-mirror 直连）→ 放 `models/vae_approx/` | ✅ 云端公模库有 |
| `minimax_h3_fl2v_lightx2v_turbo_4step_v0.1_comfy_resized_avg_rank_21_bf16.safetensors` | 300MB | 同 GuangyuanSD 仓库 | — |

⚠️ **官方 Comfy-Org 仓库不发 int8_convrot 版**——工作流引用 `minimax_h3_video_vae_int8_convrot.safetensors` 时，只有 fp16 会"选不到模型"。fp16 可临时顶（功能等价，显存略多）。

## text_encoders（Qwen3-VL 32B，三个量化版）

| 文件 | 公模库 /datasets/ComfyUI/models/text_encoders/ | 本地实例 |
|---|---|---|
| `qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors` | ✅ | ✅ 已有（工作流常用这个） |
| `qwen3vl_32b_minimax_h3_bf16.safetensors` | ✅ | — |
| `qwen3vl_32b_minimax_h3_int8_convrot.safetensors` | ✅ | ✅ 已有 |

## latent_upscale_models

| 文件 | 大小 | 来源 |
|---|---|---|
| `minimax_h3_latent_upscaler_3d_fp16.safetensors` | 690MB | 公模库 ✅（HF `LBH-123-AI/Minimax_h3_latent_Upscaler` 同名） |
| `minimax_h3_latent_upscaler_3d_fp32.pth` | 1381MB | 公模库 ✅ |
| `minimax_h3_latent_upscaler_3d_bf16.safetensors` | — | 仅 HF `LBH-123-AI/Minimax_h3_latent_Upscaler`（公模库无） |
| LTX-2.5 spatial / temporal upscaler x2 bf16 | 995MB / 262MB | 公模库 ✅ |

## loras

| 文件 | 来源 / 公模库 |
|---|---|
| `minimax_h3_turbo_v4_step600_ema.safetensors` | HF `larryvrh/MiniMax-H3-Turbo-Lora`；公模库 ✅ |
| `Singularity LTX-2.3  OmniCine Preview v0.1.safetensors` | 公模库 `/datasets/ComfyUI/models/loras/` ✅（注意文件名含双空格，软链要加引号） |
| `minimax_h3_fl2v_turbo_8step_v1.0_768p_comfyui_bf16` / `fl2v_lightx2v_turbo_4step` / `ref2v_turbo_4step_v0.1` | 公模库 ✅ |

## 其他相关公模库目录（LayerStyle 及后期处理节点用）

`layerstyle`（整目录软链）、`rmbg`、`BiRefNet`、`birefnet`、`segformer_b2/b3_clothes`、`segformer_b3_fashion`、`face_parsing`、`sam2`、`sam3`、`onnx`、`upscale_models`、`depth`、`detection`、`frame_interpolation`、`text_encoders`、`vae_approx`。

## 已装插件 ↔ 需要模型对照

| 插件 | 需要模型 | 放置目录 |
|---|---|---|
| `LBH-123-AI/Comfyui_Minimax_h3_latent_Upscaler` | upscaler checkpoint（bf16/fp16/pth） | `models/latent_upscale_models/` |
| `oufeixinxinren/ComfyUI-MiniMax-ContextIR` | 无（复用官方 H3 全家桶）；媒体加载需 PyAV 或 ffmpeg | — |
| `larryvrh/ComfyUI-MiniMax-H3-Turbo` | turbo LoRA v4 | `models/loras/` |
| `chflame163/ComfyUI_LayerStyle` | layerstyle 模型库 | `models/layerstyle/`（整目录软链） |
| `crystian/ComfyUI-Crystools` | 无 | — |
| `tl2012tl/comfyUI-llama-TE`（本地提示词/图片反推，替代要 API key 的 `MiniMaxH3MultimodalChat`） | GGUF 主模型 + mmproj（Qwen3.6-35B-A3B heretic 等） | `models/LLM/<子目录>/`；核心依赖 `llama_cpp` |

## 本地 LLM（`comfyUI-llama-TE` 用，放在 `models/LLM/<子目录>/`）

工作流节点里写 `Qwen\xxx.gguf` = 子目录 `models/LLM/Qwen/`。

| 文件 | 精确字节 | 来源 | 公模库 |
|---|---|---|---|
| `Qwen3.6-35B-A3B-uncensored-heretic-NVFP4-Experts-Only-Q8_0.gguf`（UP 工作流要的） | **21,694,740,192**（20.20 GiB） | HF `llmfan46/Qwen3.6-35B-A3B-uncensored-heretic-Native-MTP-Preserved-NVFP4-Experts-Only-GGUF` | ❌ 需下载 |
| `Qwen3.6-35B-A3B-mmproj-BF16.gguf` | **902,822,656** | 同仓库 | ❌ 需下载 |
| 同上主模型（镜像，略小） | 19.37 GB | HF `WeilPesi/Qwen3.6-35B-A3B-uncensored-heretic-NVFP4-Experts-Only-GGUF` | ❌ |
| `Qwen3.5-9B-Q5_K_M.gguf` + `mmproj-BF16.gguf` | 6.1 GB / 0.86 GB | 公模库 `/datasets/ComfyUI/models/LLM/` ✅ | ✅（可临时顶，但工作流指定 35B-A3B） |

要点：HF 搜 `Qwen3.6-35B-A3B` / `NVFP4-Experts-Only` 能搜到一批同名系列（`SC117` 的 APEX-I 版 13~24GB、`LuffyTheFox` Genesis-Hermes 等）——**功能等价可直接换用，但节点里要手选文件**；要"打开即匹配"就按工作流原名存盘（`curl -o <工作流里的短名>`，URL 用 HF 长名）。20GB 下载挂 `nohup`，判完成用字节对比（见 SKILL.md）。

## ⚠️ 更正（2026-09-14）：「查不到」的三个模型其实都有公开源

**本节旧文曾断言 `minimax_h3_bf16_CONSERVATIVE_v5.safetensors` 全网查不到 —— 那是错的，已作废。** 2026-09-14 复核把三件全找到了，**文件名逐字一致**（下完 `stat -c%s` 对字节即可确认）：

| 工作流引用的文件 | 精确字节 | 来源仓库 | 落位 |
|---|---|---|---|
| `minimax_h3_bf16_CONSERVATIVE_v5.safetensors` | **690,593,160**（658.6 MiB） | HF **`Asirus/Minimax-H3-Latent-Upscaler-BF16-MAXQUALITY`** | `models/latent_upscale_models/` |
| `minimax_h3_fl2va_pruned_w4a8_mixed.safetensors` | **12,540,858,008**（11.68 GiB） | HF **`Kijai/MiniMax-H3-experimental`**（官方 awesome 列表点名的 W4A8 源；镜像 `starsfriday/MiniMax-H3-w4a8` 同字节） | `models/diffusion_models/MiniMax-H3/` |
| `minimax_h3_ref2v_turbo_4step_v0.1_comfyui_bf16.safetensors` | **1,956,193,000**（1.82 GiB） | HF **`Comfy-Org/MiniMax-H3` 的 `loras/`**（官方就有，别去翻第三方） | `models/loras/`（工作流里无子目录前缀 → 必须放 loras 根，放子目录会"选不到"） |

W4A8 家族背景（免再摸黑）：`Kijai/MiniMax-H3-experimental` 同时发 `fl2va` / `ref2va` 两个 `_pruned_w4a8_mixed`；同类还有 `AX1Y2JP/MiniMax-H3-W4A8-ConvRot`、`Winnougan/MiniMax-H3-INT4_Convrot_ComfyUI`、`starsfriday/MiniMax-H3-w4a8`、`koongrizzly/MiniMax_H3_int4_W4A8_ConvRot_Pruned`（后者含 `ref2va_hybrid_b20-49_pruned_w4a8_mixed`）。**官方多源对照索引：`github.com/MiniMax-AI/awesome-minimax-h3-integration`（每个量化档列出 2~3 个 HF 源）——先查它再搜。** 出处：ComfyUI Wiki「2026-08-05 Kijai MiniMax H3 w4a8」。

### 方法论教训（比这三个文件更值钱）：报「公开源没有」前必须做**精确文件名**检索

本次三件全被"仓库名关键词搜索"漏掉，是**检索姿势**的错，不是模型不存在：

- `api/models?search=<关键词>` **只搜仓库名/ID**，搜不到 ≠ 文件不存在
- 正解两条并用：
  - **HF 全文搜**：`curl -s "https://huggingface.co/search/full-text?q=<文件名不含扩展名>&type=model" | grep -oE "[A-Za-z0-9._/-]*<文件名>[A-Za-z0-9._/-]*" | sort -u`
  - **web 精确引号搜**：`"<完整文件名>.safetensors"`（本次正是这一招一击命中 Kijai 仓库 + comfyui-wiki 报道 + 官方 awesome 列表）
- **结论口径**：「仓库名搜 + 文件名全文搜 + Manager 注册表」三路都空，才可以说"公开源没有"，**且必须注明检索日期**（模型站每天在变 —— 本次隔 4 天就翻案）
- 翻案后**立刻回改本条**（凡哥要的就是这个：错了就说错了并改掉记录）

**替代路径（万一真有自制件查不到）**：①三路查全 + 注明日期，如实说"公开源没有"；②指出最可能来源（夸克分享搜文件名 / UP 视频说明）；③给替代（官方 bf16 主模型 / Singularity 融合版顶上，手选文件）。**不要提供臆测的下载链接。**

## 关键教训

1. **模型名必须与工作流引用逐字一致**——差一个 `_fp16` / `_int8_convrot` 就是"缺模型"。回答"有没有"时按三步查全再答。
2. **公模库（/datasets）是第一顺位**——2026-09 实测 Singularity 主模型、turbo v4、H3 全系 VAE/text encoder/upscaler 大多已有，软链零下载。
3. **软链前先 `rm -f` 半截文件**（curl 中断残留会占位导致假成功）。
4. **下载完验大小**（`ls -la` + `du -h`），150B / 几十字节 = 假成功；**GB 级文件用官方精确字节对比**（`?blobs=true` 的 `size` vs `stat -c%s`），du 的进位会让"差 1GB"看起来像下完了。
5. **回答"有没有"要先走完三步再开口**：凡哥常在下载中途就问"是不是没进展/下完了吗"——用字节百分比 + "串行下载时后一个文件未出现=前一个没完"两条信号给确定答案，别让他自己盯着看。
