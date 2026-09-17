# MiniMax H3 全能参考工作流 —— 加速与分辨率铁律

来源：2026-08-06 凡哥 H3 全能参考生视频工作流实测（`D:\下载\minimax_h3_全能参考生视频.json` → `minimax_h3_turbo_加速版.json`）

## 工作流结构速览（API 格式）

| 节点ID | class_type | 作用 |
|--------|-----------|------|
| 127 | UNETLoader | `minimax_h3_ref2va_pruned_int8_convrot.safetensors` |
| 128 | CLIPLoader | `qwen3vl_32b_minimax_h3_int8_convrot.safetensors` type=minimax |
| 119/120 | VAELoader | video VAE(fp16) + audio VAE(fp32) |
| 136 | MiniMaxH3ReferenceToVideo | 全能参考主节点（5图+2音频） |
| 124 | BasicScheduler | steps=25（原版）/ 4（Turbo） scheduler=simple |
| 123 | KSamplerSelect | sampler=res_multistep（原版）/ euler（Turbo） |
| 126 | BasicGuider | 无显式 CFG（Turbo 用 1.0） |
| 125 | SamplerCustomAdvanced | 潜空间采样 |
| 131 | ComfyMathExpression | 时长→帧数：`max(5, round(a*24)) + (5 - (max(5, round(a*24)) % 17)) % 17` |
| 122/121 | VAEDecode / VAEDecodeAudio | 解码 |
| 130/92 | CreateVideo / SaveVideo | 输出 |

## ⚡ H3 加速 = Turbo LoRA（~5-6倍）

- LoRA：`larryvrh/MiniMax-H3-Turbo-Lora`（HuggingFace，Apache 2.0，2026-08-05发布，744MB）
- 文件：`minimax_h3_turbo_4step.safetensors`（非 EMA 版，DualClockSampler 用）
- 放置：`ComfyUI/models/loras/`

### 🚨 2026-08-07 实测修正：直接 LoadLora 会失败，必须三步

**第一步：转换 LoRA 键名（必做）**
- 作者原文件键名**缺 `diffusion_model.` 前缀** → 普通 `LoadLora` 加载无效
- 用 `convert_h3_lora_for_comfyui.py`（DualClockSampler 仓库自带）：
  `python convert_h3_lora_for_comfyui.py <原文件> <models/loras/minimax_h3_turbo_4step_comfyui.safetensors>`
- 转换只改键名前缀，不改数值/dtype/强度

**第二步：换非 pruned 完整版主模型（必做）**
- ❌ `minimax_h3_ref2va_pruned_int8_convrot.safetensors`（缺 AdaLN 层，LoRA 不生效）
- ✅ `minimax_h3_ref2va_int8_convrot.safetensors`（完整版，约15GB，从 Comfy-Org/MiniMax-H3 下）

**第三步：用对的加载器 + 修音频**
- 加载器：**`Load LoRA (Bypass, Model Only)`**（加载LoRA（旁路，仅模型）），强度 1.0——不是普通合并式 LoadLora
- 音频：ComfyUI 有 `ModelSamplingAV`（≥commit bdcb886）→ 官方 euler 已修；没有 → 装 DualClockSampler 插件，`MiniMax H3 Dual-Clock Euler` 接 `SamplerCustomAdvanced.sampler`

### 症状诊断表
| 症状 | 根因 |
|------|------|
| 画面模糊 + 重影变形 | LoRA 键名没转 + pruned 主模型 |
| 完全没声音/爆音 | ComfyUI 旧版无 ModelSamplingAV |

### 工作流改动（4 处，其他不动）
1. 新增 LoadLora 节点（转换后的 `minimax_h3_turbo_4step_comfyui.safetensors`，strength 1.0）
2. 节点124 steps: 25 → 4
3. 节点123 sampler: `res_multistep` → `euler`
4. BasicGuider + BasicScheduler 的 model 输入从 UNETLoader 改接到 LoadLora 输出
- ⚠️ 官方标注 "early prototype, not production quality"——画质需实测对比

## 📏 分辨率铁律（H3 硬性约束）

**宽高必须同时是 32 的倍数**，否则 H3 报错/失败：

```
1280×720  ❌ (720÷32=22.5)
1280×704  ✅ (704÷32=22)
1280×736  ✅ (736÷32=23)
1312×736  ✅ (ResolutionSelector 自动算出，≈720P)
```

- 工作流里的 ResolutionSelector（节点115）`multiple: 32` 自动对齐
- 节点162 megapixels = `a*b/1000000`，要 720P 就设 **0.92**（≈1280×720 的像素量）→ 自动输出 1312×736
- 帧数走 17 对齐（H3 时间网格）：表达式 `max(5, round(a*24)) + (5 - (max(5, round(a*24)) % 17)) % 17`
- 16:9 默认 864×480（0.4MP）是 32 对齐下的最稳分辨率

## ⚠️ 分组/画布元素教训

- 凡哥给的 H3 JSON 是 **API 格式**（只有 `inputs`/`class_type`），**不支持** `groups`/`pos`
- 给 API 格式强加 groups → ComfyUI 加载节点全部消失
- 要画布分组：让凡哥从 ComfyUI 菜单 **Export→Workflow** 导出（Workflow 格式），再改
- 改工作流**必须从原文件改**（`search_files` 找路径），不要 Python 重新生成——会丢完整提示词文本
