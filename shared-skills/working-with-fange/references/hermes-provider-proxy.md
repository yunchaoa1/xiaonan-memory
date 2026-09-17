# Hermes Provider & Proxy 配置备忘（2026-08-03）

## openai-codex OAuth 模型限制

**openai-codex provider 只提供 "Codex models"，不是 OpenAI 完整 API 目录。**

Codex OAuth（ChatGPT Plus/Pro 订阅）可用的模型：
- gpt-5.5
- gpt-5.4-mini
- gpt-5.4
- gpt-5.3-codex
- gpt-5.3-codex-spark

**不可用**：GPT-5.6 Sol 等完整 API 模型——这些需要 OpenAI API Key（openai-api provider）。

来源：Hermes 文档明确写 "OpenAI Codex — uses Codex models"。

## 代理配置

### Hermes 读取的环境变量

查源码 `utils.py:_PROXY_ENV_KEYS` 和 `agent/process_bootstrap.py`：
- `HTTPS_PROXY`, `HTTP_PROXY`, `ALL_PROXY`
- `https_proxy`, `http_proxy`, `all_proxy`
- 排除：`NO_PROXY`/`no_proxy`

### v2rayN 注意事项

| 模式 | 原理 | Hermes 能否走 |
|------|------|---------------|
| TUN 模式 | 虚拟网卡劫持系统流量 | ❌ Hermes 不自动走 |
| 系统代理 | 设置 Windows 系统代理 | ✅ 如果设了环境变量 |
| 手动设置 env | `set HTTPS_PROXY=...` | ✅ |

**解法**：v2rayN 开启系统代理 + 在启动 Hermes 前 `set HTTPS_PROXY=http://127.0.0.1:<端口>`

注意：只在设置了 env var 的同一个 cmd 窗口里启动的 Hermes 进程才能读到代理变量。

### Windows WinHTTP 代理

`netsh winhttp show proxy` 查看系统级代理——Hermes 不直接读这个，只读环境变量。

## 辅助模型配置

视觉模型等 auxiliary 配置：
```bash
hermes config set auxiliary.vision.provider openai-codex
hermes config set auxiliary.vision.model gpt-5.4-mini
```

注意：视觉模型走 openai-codex 也受代理影响——如果 openai-codex 直连超时，视觉也超时。

## hermes proxy 命令

当前（2026-08-03）只支持两个上游：
- `nous` — Nous Portal
- `xai` — xAI Grok OAuth
不支持 OpenAI/ChatGPT 代理。

## hermes auth add openai-codex

```bash
hermes auth add openai-codex --type oauth
```
会弹出浏览器让用户登录 ChatGPT → 设备码授权 → 需要在 ChatGPT 安全设置中开启 "Codex 设备代码授权"。
