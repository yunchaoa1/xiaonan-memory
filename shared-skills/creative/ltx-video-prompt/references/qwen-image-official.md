# Qwen-Image 官方提示词格式

> 来源：https://huggingface.co/Qwen/Qwen-Image README（2026-07-10访问）

## 核心发现

Qwen-Image **没有特殊提示词格式**。就两件事：

1. **提示词本体**：自然语言描述，中英文均可
2. **结尾加质量标签**：`，超清，4K，电影级构图。`（中文）或 `, Ultra HD, 4K, cinematic composition.`（英文）

官方示例提示词就是一段自然描述加这个尾巴。

## positive_magic 参数

```python
positive_magic = {
    "en": ", Ultra HD, 4K, cinematic composition.",
    "zh": "，超清，4K，电影级构图."
}
```

## 支持的画幅比例

1:1, 16:9, 9:16, 4:3, 3:4, 3:2, 2:3

## 结论

凡哥用的分类法（类别名：内容）对Qwen**不必要**，但可以继续用——方便排错。更简单的写法就是一段自然语言+质量尾巴。
