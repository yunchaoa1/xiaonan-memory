# LTX-Video — AI 视频生成

> 基于官方 Model Card (LTX-2.3) 和论文 (arxiv:2601.03233)
> 官方：https://huggingface.co/Lightricks/LTX-2.3

## ① 能帮我做什么
- 从首帧图 + 音频生成口型同步视频
- **画音一体生成**：视频和音频在同一个模型里同步产出
- 支持多镜头硬切（Cut to），适合访谈类视频
- 双通道模式：先粗生成再超分，兼顾速度和质量

## ② 怎么用

**模型架构（理解原理有助于高效使用）：**
- 类型：DiT（Diffusion Transformer）音视频基础模型
- 结构：非对称双流 Transformer — 14B 参数视频流 + 5B 参数音频流
- 双向音视频交叉注意力（Cross-Attention），实现画音同步
- 多语言文本编码器，英文为主
- **Modality-CFG**：视频和音频可以分开控制引导强度，我们视频通道 scale×0.5 就是这个原理

**我们用的版本：**
`ltx-2.3-22b-distilled-1.1` — 8步蒸馏版，CFG=1，相比 v1.0 改进了音频和视觉质量
- 全量版 `ltx-2.3-22b-dev` 可训练但更慢，目前不需要
- LoRA 版 `ltx-2.3-22b-distilled-lora-384-1.1` 可微调风格

**ComfyUI 参数：**
- UNET：ltx-2.3-22b-distilled-1.1_transformer_only_fp8_scaled
- 分辨率：736×1280（竖屏，736/32=23 ✅，1280/32=40 ✅）
- 帧率：24fps
- Seed：42（固定，保证一致性）
- CFG：1.0（蒸馏版标准）
- Epsilon：0.001

**⚠️ 尺寸约束（官方要求）：**
- 宽高必须能被 32 整除
- 帧数必须满足 `帧数 = N × 8 + 1`（即减1后能被8整除）
- 不满足时需 padding 后裁剪，ComfyUI 节点会自动处理

**双通道生成：**
- 通道1：8步主生成（scale×0.5）
- 通道2：4步超分（denoise 0.42, ×2 latent upscaler）

**镜头切换**：硬切（Cut to），不用 LTX transition LoRA

**⚠️ 文件禁放 /tmp**，必须放 D:\SDkecheng\
**⚠️ 音频段间 1 秒静音间隙**，合并用 `-c:a pcm_s16le`

## ③ 提示词技巧

**模型如何理解语言：**
LTX-2.3 使用多语言文本编码器，但训练数据以英文为主。英文提示词效果远好于中文。

**官方提示词指南**（ltx.video/blog/how-to-prompt-for-ltx-2，国内被墙）

**我们验证过的规则：**

❌ **禁止词**（模型看到就激活文字渲染导致画面出字）：
text, subtitle, watermark, letters, words, typography

✅ **替代写法**：Clean visual presentation with sharp edges

**核心原则：**
- 提示词只写角色动作/表情/语气，不写具体台词——让 LTX 跟音频自然驱动
- 单段单说话人，末尾标注另一方状态
- 固定机位描述，段末写 Cut to next shot
- 描述角色外观特征帮助模型保持一致性

**典型模板：**
```
[角色描述], seated on a black swivel chair. [动作/情绪].
[His/Her] gaze is fixed steadily to the [left/right] side without moving.
[Lips closed / Lips move naturally with speech]. Hands resting on armrests.
Clean visual presentation with sharp edges. Fixed camera, no movement.
[另一方] is off-screen and [silent/speaking].
Cut to next shot.
```

**Modality-CFG 原理（知道后用得更准）：**
视频和音频引导是分开控制的。我们视频 scale×0.5 意味着给音频更多自由度，让口型更自然地跟随配音。如果画面不稳定可以适当提高视频 scale，如果口型不准可以降低。
