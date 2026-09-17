# LTX CFG参数官方指南

来源：https://ltx.io/blog/comfyui-workflow-guide

## 核心规则

| 参数 | 推荐值 | 禁止 |
|------|:---:|------|
| CFG Scale | **2.0 - 5.0**（默认3.0-3.5） | 不要超过7.0 |
| 理由 | 模型已有参考图做ground truth，不需要高引导 | CFG>7→动作僵硬、画面失真、像机器人 |

## 官方原文

> "CFG Scale (Guidance): This controls how strictly the model follows your prompt. 3.0-3.5 is the default. Stick to 2.0-5.0 for video."

> "Start at 3.0, not 7.0. The model already has the image as ground truth. It doesn't need as much guidance. High CFG can distort the image into something unrecognizable."

> "You set CFG scale to 15 because you want the model to 'really follow your prompt.' The video becomes stilted, over-constrained, and motion looks robotic."

## 三大质量杀手（按优先级）

1. 比例不对（wrong aspect ratio）
2. **CFG太高**（CFG scale too high）
3. 提示词堆砌（overstuffed prompts）
