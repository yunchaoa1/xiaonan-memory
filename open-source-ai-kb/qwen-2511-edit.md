# Qwen 2511 Edit — 首帧图生成

## ① 能帮我做什么
- 基于参考图生成风格一致的新图像（Image-to-Image Edit）
- 在保持角色/场景不变的前提下，生成不同构图和镜头
- 配合 Qwen Image 模型，支持中文提示词，理解力强

## ② 怎么用
**ComfyUI 工作流**：`05_工作流/Qwen2511_Edit_Workflow.json`

**核心参数**：
- 分辨率：928×1664（竖屏 9:16）
- Steps：4
- CFG：1.0
- Shift：3.1
- Sampler：euler + simple
- UNET：qwen_image_2512_fp8_e4m3fn
- VAE：qwen_image_vae（注意不是 z_image_vae！）
- 双 LoRA：3D皮克斯2512（strength=0）+ Lightning-4steps（strength=1）

**CLIPTextEncode**：用 `text` 字段，不是 `prompt`！

**三参考图机制**：
- 图1 = base_全景基准帧.png（场景参照）
- 图2 = host_ref.png（女主持参照）
- 图3 = doctor_ref.png（周教授参照）

## ③ 提示词技巧

✅ **好的写法**：
- 纯静态描述：双唇闭合、双手放扶手
- 中文写，Qwen 对中文理解很好
- 标注参考图来源（图1/图2/图3）

❌ **无效写法**：
- 动作描述：嘴唇微张、手势、点头 → 会导致画面不稳定
- 时间状态词：即将、刚刚、准备 → Qwen 不理解抽象时间
- 英文提示词 → 中文效果更好

**模板**：
```
[角色描述]，坐在黑色转椅上。[表情状态]，目光看向[方向]维持不动。
双唇[闭合/随说话自然开合]。双手放扶手。画面干净锐利。
固定机位无运动。[另一方描述]。
```
