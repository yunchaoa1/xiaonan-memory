# cua-driver 稳定性问题

## 症状
- 长时间会话（100+ tool calls）后，`computer_use capture` 返回 `width: 0, height: 0, total_elements: 0`
- `session has ended` 错误
- vision 分析返回黑屏

## 诊断（2026-07-23）
- Hermes v0.17.0 + cua-driver 0.7.1
- `hermes computer-use doctor` 全部通过（UIA reachable, D3D11 OK, session active）
- 问题并非驱动本身的安装/权限/配置问题

## 根因
GitHub PR #69903 "fix(computer_use): disable cua-driver overlay by default" 正在修复。
cua-driver 的 cursor overlay 在空闲时可能导致 CPU 占用和会话超时。
该修复尚未合并到 v0.17.0。

## 已知修复方向
- `computer_use.no_overlay: true` 配置选项（等待 v0.18+）
- macOS/WSL/headless 环境自动禁 overlay

## 当前唯一恢复方式
重启 Hermes。终端 `taskkill` + 重启动 `cua-driver.exe` 无效——Hermes 与驱动会话在启动时建立绑定。
