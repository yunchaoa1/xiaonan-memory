# WhatDreamsCost 导演台热修复记录

## Widget值损坏Bug（2026-07 实测）

保存 WhatDreamsCost 工作流时，节点 Widget 值可能错位。典型症状：

| 节点 | Widget | 错误值 | 正确值 |
|------|------|------|------|
| LTXDirector | display_mode | `1280` | `frames` 或 `seconds` |
| LTXDirector | resize_method | `18` | `maintain aspect ratio` |
| LTXDirector | divisible_by | `0` | `32` 或 `8` |
| LTXDirectorGuide | ic_lora_name | `0.5` | `None` 或 `""` |
| LTXDirectorGuide | ic_lora_strength | `bicubic` | `1` 或 `0.5` |
| LTXVConditioning | frame_rate | MOTION_GUIDE_DATA | FLOAT（连线错到输出口5，应连输出口6） |

**修复方法**：从仓库下载热修复文件 `example_workflows/LTX_Director_2_Workflow_Hotfix.json`。

## 两段改单段

热修复默认两段采样。删第二段节点变单段：

删除节点ID：`#14 #28 #29 #31 #32 #33 #34 #55`

重新连线：
- `#22 video_latent → #1 VAEDecode (LATENT)`
- `#131 audio_latent → #18 audio_latent (LATENT)`（需新建link）
- 音频保留 `#22 audio_latent → #24 LTXVAudioVAEDecode` 不变

## ComfyUI-KJNodes 版本

热修复要求 KJNodes 最新版，否则 `LTX2SamplingPreviewOverride` 节点显示 UNKNOWN。

## 参考来源

- 仓库：https://github.com/WhatDreamsCost/WhatDreamsCost-ComfyUI
- README：v2.0.4 用 IC-LoRA 替代 MSR-V2，需同步更新 ComfyUI-LTXVideo + ComfyUI-KJNodes
