# 飞书接入复盘参考（2026-08）

## 已验证路径

1. Hermes 桌面版实际运行环境是 `D:\Hermes\hermes-agent\venv`，依赖必须检查/安装到该 venv，不要用系统 Python 代判。
2. bundled 插件名为 `feishu-platform`；插件初始可能是 bundled 但 disabled，需启用后才在新 Gateway 会话生效。
3. WebSocket 是 Windows 私机的优先模式：不需要公网 URL；`webhook` 只适合已有可达 HTTP 端点的部署。
4. 官方扫码自动创建失败时，向导会回退手动创建：飞书开放平台创建企业自建应用、开启机器人能力，在本机向导输入 App ID/App Secret。
5. 安装依赖或访问平台前，先检查代理环境。若仅是当前进程继承了失效的 `HTTP_PROXY/HTTPS_PROXY`，可以只对单条命令临时清空代理；不启动或修改用户的代理软件。

## 本次真实验收证据

- `lark-oapi==1.5.3` 在 Hermes venv 中可导入；`websockets` 已存在。
- `hermes plugins list` 显示 `feishu-platform enabled`。
- `.env` 中 App ID、App Secret、Domain 已存在；Secret 只做存在性检查，不读取、不回显。
- `hermes status --all` 显示 `Feishu configured`、`Gateway Status: running`。
- `FEISHU_CONNECTION_MODE=websocket`、`FEISHU_DOMAIN=feishu`；白名单未配置时，不得把配置完成说成端到端安全完成。

## 易错点

- pip 下载完成但命令收尾超时，不能凭下载进度宣布成功；必须用目标 venv 做 `import` 和版本回读验证。
- `hermes gateway setup` 在 Windows Terminal 中可能停在交互提示；后台注入按键不一定真正提交。重试前先截图/回读当前提示，避免重复输入凭证。
- “凭证已保存”“Gateway 正在运行”“Feishu 已配置”都不是“手机消息链路已接通”。最终门禁是：手机发真实消息 → Gateway 收到 → default 回复；随后再跑一次 Kanban 员工执行/质检闭环。
- 自动扫码接口失败不等于飞书官网不可访问；分别测试直连官网和向导注册接口，区分代理/自动注册服务问题与用户账号问题。
