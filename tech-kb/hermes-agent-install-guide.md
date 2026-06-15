# Hermes Agent 安装完整教程（Windows WSL2 + DeepSeek）

> 适用：Windows 10/11 家庭电脑 | 日期：2026-06-16  
> 目标：在家里电脑上搭建可聊天的 Hermes Agent（终端版）

---

## 一、前置条件

- Windows 10（2004版以上）或 Windows 11
- 至少 8GB 内存，2GB 空闲硬盘
- 有 DeepSeek API Key（`platform.deepseek.com` 获取）

---

## 二、安装 WSL2

**1.** 右键开始菜单 → Windows PowerShell（管理员）

**2.** 输入：`wsl --install`

**3.** 重启电脑

**4.** 重启后，开始菜单搜 "Ubuntu"，打开

**5.** 首次打开会提示设置用户名和密码（记住密码！）

**6.** 设置完成后看到绿色提示符 `用户名@xxxxx:~$` 即成功

---

## 三、下载 Hermes Agent 代码

> ⚠️ 国内 GitHub 被墙，不能用官网的 curl 命令。需手动下载。

**1.** 打开浏览器，访问：
```
https://codeload.github.com/NousResearch/hermes-agent/zip/refs/heads/main
```
会自动下载一个 zip 文件（约 50MB）

**2.** 把下载的压缩包解压到：
```
C:\Users\你的用户名\hermes-agent\
```
（注意：解压后会有嵌套两层 `hermes-agent-main` 文件夹）

---

## 四、安装 Hermes Agent

> ⚠️ 不能在 `/mnt/c/`（Windows文件系统）下安装！会报权限错误。

**1.** 打开 Ubuntu 终端，把代码复制到 Linux 地盘：
```bash
cp -r "/mnt/c/Users/你的用户名/hermes-agent/hermes-agent-main/hermes-agent-main" ~/hermes-agent
```

**2.** 进入目录并安装：
```bash
cd ~/hermes-agent
bash setup-hermes.sh
```

**3.** 等待安装完成（约5-10分钟），看到类似 "Dependencies installed" 即可。

---

## 五、配置 DeepSeek API

**1.** 创建配置文件：
```bash
echo "OPENAI_API_KEY=sk-你的DeepSeek密钥" > ~/hermes-agent/.env
echo "OPENAI_BASE_URL=https://api.deepseek.com/v1" >> ~/hermes-agent/.env
```

> 替换 `sk-你的DeepSeek密钥` 为实际的 API Key

**2.** 启动 Hermes：
```bash
cd ~/hermes-agent && uv run python3 cli.py
```

**3.** 首次启动会自动安装浏览器引擎（Chromium），提示时按 `Y` 回车

**4.** 看到 "HERMES-AGENT" 大字和命令列表即成功

**5.** 输入 `/model` 选择模型，在列表中找到 `deepseek-chat` 或 `deepseek-v4-pro`

**6.** 直接输入文字开始聊天

---

## 六、常用命令

| 命令 | 作用 |
|------|------|
| `/quit` | 退出 Hermes |
| `/model` | 切换模型 |
| `/help` | 查看所有命令 |
| `/clear` | 清屏 |
| `/save` | 保存当前对话 |

---

## 七、以后每次启动

打开 Ubuntu，输入两行：
```bash
cd ~/hermes-agent && uv run python3 cli.py
```

---

## 八、已知限制

### Gateway/Dashboard/Web 界面
Hermes 的 Telegram 连接、Dashboard、Web 聊天界面目前硬编码了 OpenRouter 作为 AI 提供商入口，不认自定义 API（DeepSeek 直连）。如需这些功能，需要：
- 去 `openrouter.ai` 注册并充值（$5起）
- 配置 `OPENROUTER_API_KEY`

### 终端聊天
不受影响，DeepSeek 直连完全正常。

---

## 九、文件位置速查

| 什么 | 在哪里 |
|------|--------|
| Hermes 代码 | `~/hermes-agent/` |
| 配置文件 | `~/hermes-agent/.env` |
| Hermes 数据 | `~/.hermes/` |
| 会话记录 | `~/.hermes/sessions/` |

---

## 十、试错经验

| 错误 | 原因 | 解决 |
|------|------|------|
| curl 连不上 GitHub | 国内被墙 | 手动下载 zip |
| PermissionError 安装失败 | 在 /mnt/c/ 下安装 | 复制到 ~/ 再装 |
| command not found: hermes | 未注册全局命令 | 用 `uv run python3 cli.py` 直接启动 |
| ModuleNotFoundError: dotenv | 依赖不完整 | 用 `uv run` 而不是 `python3` |
| gateway setup 报 401 | 网关硬编码 OpenRouter | 只用终端聊天，或充值 OpenRouter |
