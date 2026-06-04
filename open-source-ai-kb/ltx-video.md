# LTX-Video Director — AI 视频生成

## ① 能帮我做什么
- 从首帧图 + 音频生成口型同步视频
- 支持多镜头硬切（Cut to），适合访谈类视频
- 双通道模式：先粗生成再超分，兼顾速度和质量

## ② 怎么用
**ComfyUI 节点**：LTX Director 剪辑节点

**核心参数**：
- UNET：ltx-2.3-22b-distilled-1.1_transformer_only_fp8_scaled
- 分辨率：736×1280（竖屏）
- 帧率：24fps
- Seed：42（固定，保证一致性）
- CFG：1.0
- Epsilon：0.001

**双通道生成**：
- 通道1：8步主生成（scale×0.5）
- 通道2：4步超分（denoise 0.42, ×2 latent upscaler）

**镜头切换**：硬切（Cut to），不用 LTX transition LoRA

**⚠️ 文件禁放 /tmp**，必须放 D:\SDkecheng\
**⚠️ 音频段间 1 秒静音间隙**，合并用 `-c:a pcm_s16le`

## ③ 提示词技巧

❌ **禁止词**（LTX 看到就激活导致画面出字）：
text, subtitle, watermark, letters, words, typography

✅ **替代写法**：Clean visual presentation with sharp edges

**模板规律**：
- LTX-2.3 是英文模型，提示词必须英文
- 只写角色动作/表情/语气，不写具体台词——让 LTX 跟音频自然驱动
- 单段单说话人，末标注另一方不发言
- 固定机位模板，段末写 Cut to next shot

**典型模板**：
```
[A character description], seated on a black swivel chair. [Action/emotion].
[His/Her] gaze is fixed steadily to the [left/right] side of the frame without moving.
[Lips closed / Lips move naturally with speech]. [Hands resting on armrests].
Clean visual presentation with sharp edges. Fixed camera, no movement.
[Other character] is off-screen and [silent/speaking].
Cut to next shot.
```
