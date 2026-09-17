# MiniMax H3 加速方案：Turbo LoRA

## 核心发现

MiniMax-H3 官方视频生成加速的唯一无损方案是 **Turbo LoRA**（`larryvrh/MiniMax-H3-Turbo-Lora`，HuggingFace，Apache 2.0）。

## 原理

- 原版 H3：~20 步采样
- Turbo LoRA：**4 步**蒸馏生成 → ~**5 倍加速**
- 同时生成视频 + 同步立体声音频
- 画质：比 base model 在 4 步时"sharper detail"，但标注为 early preview（非量产质量）

## 工作流修改（3 处 + 1 个新节点）

| 节点 | 字段 | 原值 | 新值 |
|------|------|------|------|
| 124 BasicScheduler | `steps` | 25 | **4** |
| 123 KSamplerSelect | `sampler_name` | `res_multistep` | **`euler`** |
| 126 BasicGuider | `model` → 127 | → 127 | → **168** |
| **新增 168** | `LoadLora` | — | `minimax_h3_turbo_4step.safetensors`，strength=1.0，model ← 127 |

## 前提

1. 从 HuggingFace 下载 LoRA → `ComfyUI/models/loras/minimax_h3_turbo_4step.safetensors`
2. LoRA 文件接在 UNETLoader（127）后面，输出给 BasicGuider 和 BasicScheduler

## 已知问题

- ⚠️ 音频：4 步生成可能产生爆音/削波。修复方案：DualClockSampler 节点（`shuaixn/ComfyUI-MiniMaxH3DualClockSampler`）替换 KSamplerSelect
- CFG：用 `BasicGuider` 路径，等价起点 1.0（不设额外 CFG）
- 这是早期预览版，稳定性和兼容性不保证

## 示例工作流

加速版工作流模板：`D:\Hermes\workflows\minimax_h3_turbo.json`（已含 Turbo LoRA 节点，prompt 需从原工作流粘贴）
