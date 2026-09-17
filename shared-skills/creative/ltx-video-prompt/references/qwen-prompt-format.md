# Qwen 2511 提示词写法

> 来源：HuggingFace Qwen/Qwen-Image 官方README
> 日期：2026-07-10

## 官方格式

Qwen不吃特殊语法——**自然语言描述**即可。中英文均可。

⚠️ **"生成真实人物照片"触发词实测效果差**——Qwen-Image不识别此触发词。替代方法：用细节拆出写实感。——哑光自然肤质+皮肤纹理+自然瑕疵+手机抓拍质感+不摆拍不磨皮。

## 防多余肢体铁律

Qwen容易生成第三只手/多余肢体。每条提示词必须精确指定每只手的位置：
- "左手在X，右手在Y。只有两只手。"
- 手的位置必须在同一个自然动作逻辑里——不自然的手势=模型自己补

## 中英文品质标签

```
en: ", Ultra HD, 4K, cinematic composition."
zh: ", 超清，4K，电影级构图."
```

## 支持画幅比例

| 比例 | 分辨率 |
|------|------|
| 1:1 | 1328×1328 |
| 16:9 | 1664×928 |
| 9:16 | 928×1664 |
| 4:3 | 1472×1140 |
| 3:4 | 1140×1472 |
| 3:2 | 1584×1056 |
| 2:3 | 1056×1584 |

## 官方示例提示词

```
A coffee shop entrance features a chalkboard sign reading "Qwen Coffee $2 per cup," with a neon light beside it displaying "通义千问". Next to it hangs a poster showing a beautiful Chinese woman, and beneath the poster is written "π≈3.1415926-53589793-23846264-33832795-02384197". Ultra HD, 4K, cinematic composition.
```

## 凡哥分类法（冒号分隔）

凡哥偏好分类法便于排错，Qwen兼容此格式：

```
类别名：描述内容。类别名：描述内容。超清，4K，电影级构图。
```

关键：每个类别一行，句号结尾，全正面描述不写否定句。
