# Agnes AI API 参考（2026-08-06 实测）

## 基本信息

- **Base URL**: `https://apihub.agnes-ai.com/v1`
- **格式**: OpenAI 兼容（Chat Completions、Images、Videos）
- **认证**: `Authorization: Bearer <API_KEY>`
- **Key 获取**: platform.agnes-ai.com 控制台 → API Key 管理

## 模型列表（实测可用）

### 文本模型

| 模型 | 类型 | max_tokens 建议 |
|------|------|----------------|
| `agnes-2.0-flash` | 标准对话 | 正常 |
| `agnes-2.5-flash` | 推理模型 | **≥200**（否则 content 为空）|
| `agnes-2.5-pro` | 推理旗舰 | **≥200** |
| `agnes-2.5-pro-alpha` | 推理实验 | 待测 |

**重要**：推理模型的 reasoning 和 content 是分开计 token 的。`max_tokens` 太小会导致全部 token 分给 reasoning，`content` 为空字符串。

### 图像模型

| 模型 | 端点 | 参数 |
|------|------|------|
| `agnes-image-2.1-flash` | `/v1/images/generations` | prompt, n=1, size（如 1024x1024）|

返回格式：`{"data": [{"url": "https://..."}]}`

### 视频模型

| 模型 | 端点 | 方式 |
|------|------|------|
| `agnes-video-v2.0` | `/v1/videos`（POST）| 异步提交 |
| | `/v1/videos/{task_id}`（GET）| 轮询状态 |

响应字段：`status: queued/processing/completed/failed`, `progress: 0-100`。
完成后视频 URL 在 `metadata.url`（mp4 格式）。
实测尺寸：1088×832（720p/4:3），生成约 70 秒。

## 本地脚本

`D:\Hermes\scripts\agnes_gen.py`

```bash
# 生图
python agnes_gen.py image "prompt" [--model agnes-image-2.1-flash] [--size 1024x1024]

# 生视频
python agnes_gen.py video "prompt" [--model agnes-video-v2.0]

# 查视频任务状态
python agnes_gen.py video-status <task_id>
```

图片自动下载到 `D:\Hermes\downloads\`。

## Hermes 视觉接入

`config.yaml` 配置：

```yaml
custom_providers:
  - name: agnes
    provider: openai-api
    base_url: https://apihub.agnes-ai.com/v1
    api_key: <KEY>
    models:
      - agnes-2.5-flash
      - agnes-2.0-flash
      - agnes-2.5-pro

auxiliary:
  vision:
    provider: custom:agnes
    model: agnes-2.5-flash
```

重启 Hermes 生效。当前主模型（如 deepseek-v4-pro）不支持视觉时自动回退到 Agnes 视觉模型。
