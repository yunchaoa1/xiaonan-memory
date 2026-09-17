# Codex 中转站：cdxai.cn

国内 OpenAI API 中转站（2026-08-06 发现），提供标准 OpenAI 兼容接口。

- **网站**：https://cdxai.cn
- **Base URL**：`https://cdxai.cn/v1`
- **认证**：`Authorization: Bearer <API_KEY>`（从网站 keys 页面获取）
- **联系**：微信 woslii

## 定价（PHP 结算，约 CNY ¥0.05/PHP）

每百万 token 的学分（1学分≈¥0.113，1000学分=PHP 2260）：

| 模型 | 输入 | 缓存输入 | 输出 |
|------|------|---------|------|
| GPT-5.6 Sol | 125 | 12.50 | 750 |
| GPT-5.6 Terra | 50 | 5 | 300 |
| GPT-5.6 Luna | 5 | 0.50 | 30 |

## Hermes 接入

同 DeepSeek/Agnes，配进 `custom_providers`：

```yaml
custom_providers:
  - name: cdxai
    provider: openai-api
    base_url: https://cdxai.cn/v1
    api_key: <从网站获取>
    models:
      - gpt-5.6-sol
      - gpt-5.6-terra
      - gpt-5.6-luna
```

## 对比 DeepSeek v4-pro（CNY/百万token）

| 模型 | 输入 | 输出 |
|------|------|------|
| GPT-5.6 Luna | ¥0.57 | ¥3.4 |
| DeepSeek v4-flash | ¥1 | ¥2 |
| DeepSeek v4-pro | ¥3 | ¥6 |
| GPT-5.6 Sol | ¥14 | ¥85 |
