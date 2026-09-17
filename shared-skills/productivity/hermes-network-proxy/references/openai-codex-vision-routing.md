# OpenAI Codex 视觉路由：原生主模型与辅助回退

## 适用场景

- 主模型已切换，但图片仍由旧辅助模型处理。
- `vision_analyze` 返回供应商错误、OCR 明显降级或文字摘要。
- 希望视觉动态跟随主模型，而不是固定一个辅助模型。

## 核心判定

Hermes 有两条路径：

1. **主模型原生视觉**：vision-capable 主模型和 provider 支持图片内容时，原始像素直接进入主模型。
2. **辅助描述回退**：主模型不能接收图片时，`auxiliary.vision` 先把图片转成文字描述。

`auxiliary.vision.provider: auto` 会优先选择当前主 provider/model；显式 provider/model 则覆盖跟随关系。

## 跟随主模型的配置

```bash
hermes config set auxiliary.vision.provider auto
hermes config set auxiliary.vision.model ""
hermes config set auxiliary.vision.base_url ""
hermes config set auxiliary.vision.api_key ""
hermes gateway restart
hermes config show
```

验证：`hermes config show` 不应再出现显式 Vision override。若 `vision_analyze` 返回 “Image loaded into your context — you can see it natively now”，说明走原始像素快路径；不要把这条 envelope 当最终识别文本，下一轮由主模型回答。

## 旧 endpoint 残留

从 Agnes、自建 OpenAI-compatible endpoint 等迁移时，必须同时清空 `base_url` 和 `api_key`。否则表面显示新 provider/model，实际请求仍可能命中旧端点。

典型信号：

- 错误里出现旧供应商名称。
- `No available channel for model ...`
- 图片上传成功但 analysis failed。

## 2026-08-03 验证记录

环境：Hermes Agent v0.17.0，主 provider `openai-codex`，主模型 `gpt-5.6-sol`。

操作：从显式 `openai-codex/gpt-5.5` 视觉 override 改为 `auto + 空 model`，清空 endpoint 字段，重启 gateway。

结果：

- `hermes config show` 不再显示 Vision override。
- `vision_analyze` 返回原始图片 envelope，确认由 5.6 Sol 主模型读取像素。
- OCR 基准图《赵云与阿斗》正确识别：`失败`、`霸主·四`、3亮2暗、`刀×5`、`双倍金币`、`领取`。
- 中央小字经裁切放大确认共有5个“贼”，上方两个做了镜像/倾倒式绘制。
- 先前辅助文字摘要把“霸主”读成“霸王”、把“贼”读成“败”；因此“工具返回成功”不能代替逐项准确率验证。

## 回滚

若主模型原生视觉超时或准确率更差，可显式锁回已验证模型：

```bash
hermes config set auxiliary.vision.provider openai-codex
hermes config set auxiliary.vision.model gpt-5.5
hermes config set auxiliary.vision.base_url ""
hermes config set auxiliary.vision.api_key ""
hermes gateway restart
```

回滚后再用同一基准图复测，避免换图导致不可比。
