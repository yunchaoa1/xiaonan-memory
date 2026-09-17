---
name: agnes-ai
description: Agnes AI 全模态免费API——视觉理解、图像生成、视频生成。凡哥说"用Agnes生图""用Agnes生视频""Agnes看图"时加载。
---

# Agnes AI —— 免费全模态 API

## API 信息

- Base URL: `https://apihub.agnes-ai.com/v1`（OpenAI 兼容）
- 认证: `Bearer <API_KEY>`（KEY 在 `D:\Hermes\.env` 的 `AGNES_API_KEY`）
- 官方文档: https://www.agnes-ai.com/zh-Hans/docs/overview

## 可用模型

| 类型 | 模型名 | 用途 |
|------|--------|------|
| 文本(标准) | `agnes-2.0-flash` | 通用对话 |
| 文本(推理) | `agnes-2.5-flash` | 推理增强，需 `max_tokens ≥ 200` |
| 文本(推理) | `agnes-2.5-pro` | 旗舰推理 |
| 图像生成 | `agnes-image-2.1-flash` | `/v1/images/generations` |
| 视频生成 | `agnes-video-v2.0` | `/v1/videos`（异步） |

⚠️ **视觉理解 vs 图像生成——不要混用（2026-08-06实测）**：
- `agnes-image-2.1-flash` 是**图像生成**模型，**不能**做视觉理解。`vision_analyze` 调用它报 400：`Model agnes-image-2.1-flash is an image model. Use /v1/images/generations`。
- 看图/视觉理解用 **`agnes-2.5-flash`**（文本模型支持图像输入，实测准确）。
- Hermes `auxiliary.vision` 必须指向 `agnes-2.5-flash`，不是 image 系列。

## Hermes 集成

### 视觉模型（当前配置）
```yaml
custom_providers:
  - name: agnes
    provider: openai-api
    base_url: https://apihub.agnes-ai.com/v1
    api_key: <KEY>
    models: [agnes-2.5-flash, agnes-2.0-flash, agnes-2.5-pro]

auxiliary:
  vision:
    provider: custom:agnes
    model: agnes-2.5-flash
```

### 图像/视频生成
Hermes 原生不支持 Agnes 作为 image_gen/video_gen provider。
使用脚本调用：`python D:\Hermes\scripts\agnes_gen.py`

## 脚本用法

```
# 生图
python D:\Hermes\scripts\agnes_gen.py image "一只猫坐在窗台上"

# 生视频（异步，自动轮询）
python D:\Hermes\scripts\agnes_gen.py video "海浪拍打岩石"

# 查视频任务状态
python D:\Hermes\scripts\agnes_gen.py video-status <task_id>
```

## 视频生成特性

- 分辨率：默认 1088×832（720p/4:3）
- 帧数：`num_frames` 必须 `8n+1`（默认 121 = 5秒@24fps）
- 支持 `image_url`（单图生视频）
- 支持 `reference_images` 数组（多参考图）
- 支持 `keyframes` 数组（关键帧过渡）
- 异步：提交后轮询 `/v1/videos/{task_id}`，结果在 `metadata.url`

## 与 Seedance 对比

| 能力 | Agnes | Seedance |
|------|-------|----------|
| 全能参考多维度控制 | ❌ | ✅ |
| 运动画笔 | ❌ | ✅ |
| 故事板 | 基础(keyframes) | ✅ 完整 |
| 关键帧过渡 | ✅ | ✅ |
| 图生视频 | ✅ | ✅ |
| 适合场景 | 简单生成 | 导演级制作 |

凡哥的业务场景推荐 Seedance，Agnes 做辅助。
