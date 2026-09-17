# OpenAI Codex 动态模型烟雾测试

## 目的

把“模型库里看得到”“OAuth 账号能调用”“工具/视觉能力可用”分开验证。不要凭旧订阅经验判断新模型。

## 1. 确认准确模型 ID

```bash
hermes model --refresh
hermes config show
```

无交互环境可查看 Hermes home 下：

- `provider_models_cache.json`：provider 当前模型快照。
- `context_length_cache.yaml`：具体 model + endpoint 的上下文长度缓存。

缓存是时间点快照，不是永久白名单。2026-08-03 的 `openai-codex` 快照包含 `gpt-5.6-sol/terra/luna`、`gpt-5.5`、`gpt-5.4`、`gpt-5.4-mini`；以后必须重新核对。

## 2. 最小文字调用

```bash
hermes chat -q "只回答 ok" \
  --provider openai-codex \
  -m gpt-5.6-sol \
  -Q --source tool
```

判定：进程 exit 0 且正文为 `ok`。模型出现在列表但这里 403/404/`model_not_found`，仍不能视为可用。

## 3. 工具调用探针

项目 SOUL 可能要求“执行前先列计划等待确认”，导致嵌套测试停在确认而非调用工具。要测模型原始工具能力，可对**无副作用命令**使用隔离规则：

```bash
hermes chat -q "调用 terminal 执行 echo TOOL_OK，最后只回答工具输出" \
  --provider openai-codex \
  -m gpt-5.6-sol \
  -t terminal \
  --ignore-rules \
  -Q --source tool
```

`--ignore-rules` 仅用于 `echo`、只读查询等能力探针；真实任务仍遵守用户确认流程。

判定：必须看到实际工具输出 `TOOL_OK`，不能把模型直接复述字符串算成功。

## 4. 视觉探针

```bash
hermes chat -q "只根据像素识别图中文字" \
  --image "D:/path/known-ocr-fixture.png" \
  --provider openai-codex \
  -m gpt-5.6-sol \
  -Q --source tool
```

使用带已知答案的图片，并列出逐项评分：标题、状态、数字、按钮、小字。模糊区域裁切放大后复测，临时裁切文件用完删除。

## 5. 视觉路由快路径

当 `auxiliary.vision=auto` 且主模型支持原生视觉时，`vision_analyze` 应把原始图片作为 multimodal tool-result envelope 交回主模型；典型提示是：

```text
Image loaded into your context — you can see it natively now.
```

如果返回的是完整文字描述，说明走了辅助描述路径。两条路径都可能“成功”，但准确率和延迟不同，必须用同一基准图比较。

## 6. 记录与切换决策

至少记录：

- provider / model ID
- Hermes 版本
- 文字、工具、视觉三项是否通过
- 是否使用 native image envelope
- 响应是否超时
- 当前默认模型、视觉 override、cron model 是否分别变化

只有需要全局稳定时才改默认；新模型可先用于当前会话，cron 保持旧稳定模型并不矛盾。
