# LTX官方提示词指南

来源：https://ltx.io/blog/ltx-2-3-prompt-guide

## 核心原则

| 官方说 | 含义 |
|------|------|
| 越详细越好 | 长提示词效果优于短提示词 |
| 提示词长度匹配视频长度 | 长视频配长提示词，否则模型会自己乱填 |
| 用电影语言 | tracking shot, shallow depth of field, macro lens, low angle 都有效 |
| 台词拆成小段 | 每段台词之间插入表演指导（停顿、表情、动作） |
| 用物理动作代替情绪标签 | 不说"sad"，说"he looks to the side with a cracking voice" |
| 2.3的面部表情和节奏控制更精准 | 可以写"pauses, looks to the side, then continues" |

## 官方示例（台词拆段法）

```
A middle-aged man with greying hair speaks in a sad, slow-paced voice,
"I remember after you kids came along..."
He pauses and looks to the side, then continues,
"your mom..."
His eyes widen momentarily. He finishes with a cracking voice,
"said something to me I never quite understood."
The camera slowly zooms into his face.
The audio is crisp with faint room tone.
```

每句话之间插入动作，模型就能精准控制节奏。

## 对我们的影响

- LTX能理解电影术语（tracking shot、shallow depth of field）——之前我们都避开了
- 台词拆段+中间插动作是我们已经在做的（镜1镜2定稿就是这格式）
- 场景可以写更详细——之前怕幻觉做减法，但官方说模型需要足够的方向来填充时长
