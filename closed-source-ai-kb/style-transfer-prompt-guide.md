# 画风迁移提示词指南

> 目标：同一个角色，输出三种不同画风，保持角色特征一致
> 适用：Qwen Image、通义万相、Midjourney、DALL-E 等主流模型

---

## 核心原理

画风迁移 = 角色描述（锁定身份）+ 画风关键词（转换风格）+ 负向提示词（排除干扰）

模型看到"人物特征"就知道是谁，看到"风格关键词"就改变画法，看到"负向词"就避免跑偏。

---

## 画风关键词参考

### 二次元平面风格

中文：二次元动漫风格，平面赛璐璐上色，日系动漫，干净线稿，高饱和色彩，平涂，动画截图风格

英文：2D anime style, cel-shaded, flat coloring, clean lineart, Japanese animation style, anime screencap, vibrant flat colors

### 新中式3D风格

中文：新中式3D渲染，皮克斯风格，三维卡通渲染，柔和光影，次表面散射，精致材质，C4D渲染质感，国风3D角色

英文：3D Pixar style render, C4D render, soft subsurface scattering, stylized 3D character, toon shader, Chinese aesthetic 3D, Blender cycles render

### 真人写实风格

中文：真人写实摄影，超写实，电影级质感，自然光线，皮肤纹理真实，专业人像摄影，85mm镜头，浅景深

英文：photorealistic, hyperrealistic, cinematic lighting, natural skin texture, professional portrait photography, 85mm lens, shallow depth of field

---

## 提示词模板

### 通用模板

```
[角色外貌描述]，[服装描述]，[标志性特征]。
[画风关键词]。
[画面质量词]。
```

### 实战示例

**角色：海口骑楼少年**
```
一名16岁海南少年，小麦色皮肤，清爽短发，白色棉麻短衫，
戴一串贝壳项链，眼神明亮带着海边少年的自由气息。

转换为二次元动漫风格，平面赛璐璐上色，干净线稿，
日系少年漫画主角既视感，高饱和色彩。
高品质，精美细节。
```

**负向提示词（通用）：**
```
改变角色长相，特征丢失，风格混杂，写实与动漫混合，
低质量，模糊，比例失调，畸形
```

---

## 各平台特性

### Qwen Image / 通义万相

- 支持中文提示词，效果优于英文
- 图生图模式：上传参考图 + 风格描述 → 保持角色特征
- 可直接用"转换为XX风格"这种自然语言指令

### Midjourney

- `--cref [图片URL]` 锁定角色参考
- `--sref [图片URL]` 锁定风格参考（MJ V6+）
- 英文提示词为主
- 艺术家风格关键词效果好：`by Hayao Miyazaki`, `Pixar style`

### DALL-E / GPT-Image

- 自然语言理解最强，直接说人话
- "把这个角色画成二次元动漫风格，保持长相不变"
- 对指令遵循度高

---

## 实操要点

1. 角色描述先写具体、再写抽象——"黑色短发、丹凤眼、高鼻梁"比"帅气少年"有效
2. 标志物不变——项链、发型、服装颜色，跨画风也保持一致
3. 先出真人版再转换——真人版五官最清晰，以此为锚点转换更准
4. 一次不行就多轮——AI 没见过你的角色，第一次可能走形，微调提示词再试
