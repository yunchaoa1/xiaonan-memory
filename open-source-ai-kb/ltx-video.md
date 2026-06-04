# LTX-Video — AI 视频生成

> 基于官方 Model Card、论文 (arxiv:2601.03233)、官方提示词指南
> 官方：https://huggingface.co/Lightricks/LTX-2.3

## ① 能帮我做什么
- 首帧图 + 音频 → 口型同步视频（Image-to-Video + Audio）
- **画音一体**：视频和音频在同一个 DiT 模型里生成
- 多镜头硬切（Cut to），适合访谈类视频
- 双通道模式：粗生成 → 超分
- 官方还提供 API（ltx.video），有 Fast/Pro 两档

## ② 怎么用

**模型架构（理解原理有助于调参）：**
- DiT（Diffusion Transformer），非对称双流：14B 视频 + 5B 音频
- 双向音视频交叉注意力，实现画音同步
- Modality-CFG：视频和音频引导分开控制
- 多语言文本编码器，英文为主

**我们用的版本：**
`ltx-2.3-22b-distilled-1.1` — 8步蒸馏版，CFG=1，v1.1 改进了音频和视觉质量

**ComfyUI 参数：**
- UNET：ltx-2.3-22b-distilled-1.1_transformer_only_fp8_scaled
- 分辨率：736×1280（竖屏，满足 32 整除约束）
- 帧率：24fps | Seed：42 | CFG：1.0 | Epsilon：0.001
- 双通道：通道1 8步（scale×0.5）+ 通道2 4步超分（denoise 0.42）

**⚠️ 尺寸约束（官方硬要求）：**
- 宽高必须能被 32 整除
- 帧数 = N × 8 + 1（减1后能被8整除）
- ComfyUI 节点会自动 padding 处理

**镜头切换**：硬切（Cut to），不用 LTX transition LoRA
**⚠️ 文件禁放 /tmp**，必须放 D:\SDkecheng\
**⚠️ 音频段间 1 秒静音间隙**，合并用 `-c:a pcm_s16le`

## ③ 提示词技巧

### 官方指南核心规则

**提示词 6 要素（官方）：**
1. 定镜头（Establish the Shot）— 用电影术语描述景别
2. 设场景（Set the Scene）— 光线、色调、材质、氛围
3. 写动作（Describe the Action）— 从头到尾自然流动
4. 定义角色（Define the Character(s)）— 年龄、发型、服装、特征
5. 摄像机运动（Camera Movement）— 明确如何运动
6. 描述音频（Describe the Audio）— 对白用引号括起来

**✅ 官方推荐写法：**
- 写成一整段流畅的段落（single flowing paragraph）
- 用现在时态动词
- 细节程度匹配景别（特写 > 全景）
- 4-8 句描述性句子
- 大胆迭代——LTX 为快速实验设计

**✅ 什么效果好：**
电影级构图、情感人物瞬间、氛围/光线、清晰的摄影机语言、风格化美学、角色可以说话唱歌

**❌ 官方明确不要写：**
- **内心情绪标签**（不要写 sad/confused，用视觉线索替代！）
- 文字和 Logo（不可靠）
- 复杂物理（会出伪影，跳舞可以）
- 场景过载（太多角色或动作）
- 矛盾的光线逻辑
- 过度复杂的提示词（从简单开始逐层加）

### 我们的实战验证

❌ **额外发现的禁止词**（激活文字渲染）：
text, subtitle, watermark, letters, words, typography
✅ **替代**：Clean visual presentation with sharp edges

**我们验证有效的模板：**
```
[角色描述], seated on a black swivel chair. [动作/情绪的身体线索].
[His/Her] gaze is fixed steadily to the [left/right] side without moving.
[Lips closed / Lips move naturally with speech]. Hands resting on armrests.
Clean visual presentation with sharp edges. Fixed camera, no movement.
[另一方] is off-screen and [silent/speaking].
Cut to next shot.
```

**Modality-CFG 实战：**
视频 scale×0.5 = 给音频更多自由度让口型自然。画面不稳可提高 scale，口型不准可降低。

### 官方 LipDub 功能
视频配音替换工具，提示词格式：
`[说话人] is speaking [语言], saying: "[完整对白]"`
目前验证的语言：英/法/西/德/俄
