# Director Refine Upscale 2K OOM 案例（2026-09-09 云上实测链）

> 症状/日志判读见 SKILL.md「二采放大异常诊断」。本文件=OOM 物理根因证据、失败路径记录、正路部署。
> 状态：正路（换小模型）已部署交付，**凡哥实测确认前不算闭环**——下方"正路"是有官方依据的方向，不是已验证成功流程。

## 症状与日志铁证

二采（upscale h3_latent 1920×1088）"没进度条 / 直接出片 / 比一采还糊"= **refine 采样失败回退**：
```
[H3 latent upscale: 864×480 → 1920×1088 / latent 54x30 → 120x68 (scale=2.27)]  ← 放大成功
[Director refine pass 1/1 (sigmas wired euler 3-step, custom model)]          ← 二采开跑
[WARNING] Segment 1 refine failed (Allocation on device); keeping last successful pass.
大量 aimdo VBAR "ABOVE watermark" 警告 = 显存管理极限挣扎（OOM 前兆）
```

## OOM 物理根因：模型文件大小 vs 32GB 显存（不是参数）

- `ref2va_int8_convrot.safetensors`（full 版）dynamic VRAM **Staged 32.4GB**；`qwen3vl_int8_convrot` Staged 25.8GB → 两模型换页下 2K latent 激活峰值爆 32GB
- 一采 25 步要 364s（≈14.5s/it）= 系统已在极限换页；2K 放大 5 倍 latent 面积直接 Allocation 失败
- **latent upscaler 官方 README 原文（LBH-123-AI/Comfyui_Minimax_h3_latent_Upscaler）**：⚠️ "This saves **time, not VRAM** — the refinement pass still runs at the target resolution, so peak memory is comparable to generating high-res directly." → h3_latent upscale 不省显存，别指望它解决 OOM
- **官网 example 能跑 2K 的差异 = 用小模型**：官方 json 用 `ref2va_pruned_w4a8_mixed` / `qwen3vl_nvfp4_awq` / `fl2va_pruned_int8_convrot`（剪枝量化小文件），显存占用比 full int8 小一半

## 失败路径记录（别再走）

1. **sage 2.x 装不上**：KJ 的 sage 节点要 `sageattention>=2.x`（模块级 `from sageattention.core import get_cuda_arch_versions`）；**PyPI/tuna 最高只有 1.0.6**（旧 API 无 `sageattention.core`）→ 报 "not new enough or could not determine CUDA architecture"。2.x 只在 GitHub/源码发，云 HF 不通 → sage 链在云端不可用。本地 Win 当年同因转 SolAttn。
2. **SolAttn 替代 sage 无效（OOM 依旧）**：SolAttn 稀疏窗口 start_percent=0.2~end_percent=0.9，而 refine 只有 **3 步** → 稀疏区几乎不生效，不省显存。SolAttn 对长采样（25 步一采）有效，对 3 步 refine 无效。
3. **调 steps/denoise 不解决**：官方 example 就是 beta 3 步/denoise 0.2 + 2MP——参数没毛病，先查官方 example json 佐证再怀疑执行。

## 正路：换 pruned/awq 小模型（/datasets 平台公模库软链）

**/datasets 只读公模库有全套 H3 ComfyUI 单文件**（免下载/免复制部署）：
- `diffusion_models/`：`minimax_h3_ref2va_pruned_int8_convrot.safetensors`（=本地 r2v json 官方模型名）、`minimax_h3_fl2va_pruned_int8_convrot.safetensors`、fl2va_bf16/fp8/int8、hybrid 系列、`minimax_h3_fused_refdelta_r1024_turbo8_mystic07`
- `text_encoders/`：`qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors`（官方 example 同款）、bf16、int8
- `loras/`：turbo 全套（fl2v 8step v1.0 / 4step v1.0+v1.1 / lightx2v / ref2v turbo / training adapter）
- `latent_upscale_models/`：3d fp16/fp32
- 另有 HF 原始权重镜像 `/datasets/studio/huggingface/models/MiniMax-H3/`（**原始 split 格式，ComfyUI 不可直接用**）

**部署命令（软链到共享盘，ComfyUI 即可见）**：
```bash
ln -s /datasets/ComfyUI/models/diffusion_models/minimax_h3_ref2va_pruned_int8_convrot.safetensors /home/waas/ComfyUI/models/diffusion_models/
ln -s /datasets/ComfyUI/models/text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors /home/waas/ComfyUI/models/text_encoders/
# 重启 ComfyUI 后模型下拉出现；软链后再跑 2K 二采看 OOM 消没消
```
注意：/datasets 只读（可读可软链、不可写）；共享盘 /home/waas 才是环境盘。

**模型替换对照表**（官方 example 同款）：
| 用途 | full 大文件（OOM） | 小模型（正路） |
|---|---|---|
| 主模型 UNET | ref2va_int8_convrot (32.4GB staged) | `ref2va_pruned_int8_convrot` |
| 文本编码器 | qwen3vl_int8_convrot (25.8GB) | `qwen3vl_32b_minimax_h3_nvfp4_awq` |

交付 json：`D:\数字资产\云电脑工作流\minimax_h3_director_r2v_480p_to_2k_turbo_小模型_云版.json`（turbo 版结构 + 模型名改 pruned/awq）。

## 官方 issue 地图（upscale 二采）

- **#96**（8/21，Open）：I2V/FL2V + upscale 二采 shape mismatch（1032 vs 1508 token）→ "keeping first-pass latent" 回退；R2V 在 main 新版正常。原因：upscale 后 conditioning 未按目标画布重建。
- **#122**（9/5，Open）：竖构图也复现（768×1376→832×1504）。
- **#98**（9/2，Open）：请求 Director 集成 MMH3 分割放大（Spatial/Temporal Split Upscale，低显存平铺放大）——**未集成**；独立节点在 LBH 仓库（README_zh 提 8/28 发布 Split Upscale 三节点，英文 README 未收录，落地前先核实仓库实际文件）。
- 处理原则：遇到 a148812（8/28）上 upscale 相关怪象，先查 main 分支是否已修（issue 未关=可能未修完），版本决策交凡哥拍板。
