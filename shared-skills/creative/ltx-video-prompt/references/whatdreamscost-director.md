# WhatDreamsCost LTX Director 导演台完整知识

> 最后更新：2026-07-24

## 仓库信息

- **GitHub**: https://github.com/WhatDreamsCost/WhatDreamsCost-ComfyUI
- **最新版本**: v2.0.4（2026-07-13）
- **作者YouTube**: WhatDreamsCost

## 教程视频

| 视频 | 链接 |
|------|------|
| LTX Director 2.0 预告（IC-LoRA用法） | https://www.youtube.com/watch?v=o0l6Ikvn5Q0 |
| LTX Director 1.0 完整教程（基础操作） | https://www.youtube.com/watch?v=vM60pJJqqEI |
| 第三篇教程 | https://www.youtube.com/watch?v=aXDIr8eNovI |

## V3工作流（当前最新）

文件：`LTX I2V FFLF Custom Audio Workflow - SUPPORTS LATEST COMFYUI VERSION - V3.json`

**核心变化（v2.0起）**：IC-LoRA 替代 MSR-V2。作者测过MSR和BFS后认为IC-LoRA最稳定。老工作流（MSR版）和新节点不兼容。

## 模型要求

| 组件 | 文件 | 大小 | 来源 |
|------|------|------|------|
| 主模型 | `ltx-2.3-22b-distilled-1.1.safetensors` | 46GB | models/checkpoints/LTX2.3/ |
| LoRA（质量补丁） | `ltx-2.3-22b-distilled-lora-384.safetensors` | 7.6GB | HuggingFace: Lightricks/LTX-2.3 |
| LoRA强度 | 0.5（工作流默认） | — | LoraLoaderModelOnly节点 |

### 备选模型

`szwagros/ltx-2.3-22b-dev-bf16-fp8`（HuggingFace）
- FP8版transformer: 21.4GB
- 包含独立audio_vae（107MB）和vocoder（258MB）
- 适合音频驱动视频场景

## IC-LoRA参考图

- 在LTX Director节点的IC-LoRA轨道上拖入参考图
- 图生视频：拖图片到IC-LoRA轨道
- 不需要额外的IC-LoRA模型下载——Director节点内置处理

## 节点更新命令

```bash
cd custom_nodes/WhatDreamsCost-ComfyUI && git pull
# 同步更新依赖
cd custom_nodes/ComfyUI-LTXVideo && git pull
```

注意：ComfyUI-LTXVideo必须同步更新，否则Director不兼容。

## V3工作流节点一览

| 节点 | 作用 |
|------|------|
| LowVRAMCheckpointLoader | 加载主模型 |
| LoraLoaderModelOnly | 加载蒸馏LoRA（强度0.5） |
| LTX Director | 总控台：时间线+IC-LoRA+提示词+音频 |
| Load Audio UI | 导入/裁剪音频 |
| Load Video UI | 导入/裁剪视频 |
| MultiImageLoader | 加载参考图 |
| Speech Length Calculator | 根据台词算时长 |

## v2.0新功能

- 完整视频支持（扩展/裁剪/拼接）
- IC-LoRA支持（拖放参考图）
- 音频修补（Audio Inpainting）
- Retake模式（重新生成视频片段，Beta）
- 时间线保存/加载（导出为JSON）
- 模型缓存（1.5-3x加速）
- UI全面改版

## 已知问题

- Retake模式"不够有力"，作者在重写中
- 没有完整的文档——README说"Tutorial videos and documentation coming soon"
