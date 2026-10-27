---
name: hermes-network-proxy
description: Hermes 网络、Provider 与语音/视觉路由——v2rayN/Clash 代理、OpenAI Codex OAuth、动态模型目录、TTS 语音播报失败排障、主模型原生视觉和辅助视觉排障。
---

# Hermes 网络、Provider 与视觉路由

## 触发条件

- 凡哥说“连不上”“超时”“API call failed”“Connection error”
- 切换 OpenAI Codex 或其他 provider/model
- 模型库出现新模型，需要判断是否真能调用
- 图片能上传但 OCR 错、`vision_analyze` 失败、视觉走错供应商
- 主模型、辅助视觉、cron 的模型状态互相不一致
- 语音播报失败、`TTS chunk N failed (edge)`、`WSServerHandshakeError: 403`
- **改了 `venv/Lib/site-packages/**` 或升级依赖后，App 里行为照旧没变化**（十有八九是桌面 App 没真重启）

## 先拆成四层，禁止混查

1. **网络层**：HTTP(S)/ALL_PROXY、v2rayN 端口、连通性。
2. **主模型层**：`model.provider` + `model.default`，以及当前会话实际 runtime。
3. **视觉层**：图片是主模型原生像素路径，还是 `auxiliary.vision` 文本描述回退。
4. **自动化层**：cron 可能有自己的 model/provider override 或旧 snapshot。

某一层成功不代表其他层同步成功。手动 `/model` 后，必须分别核对主配置、视觉覆盖和 cron；不要根据当前聊天能回答就宣布迁移完成。

---

## 代理原理

Hermes 源码确认（`utils.py`、`process_bootstrap.py`）读取：

```text
HTTPS_PROXY → HTTP_PROXY → ALL_PROXY
https_proxy → http_proxy → all_proxy
```

**TUN 模式不等于环境变量。** TUN 通过虚拟网卡接管流量，不保证 Hermes 子进程拿到代理环境变量。优先先查源码/官方文档，再按真实机制配置，禁止连续猜端口。

### v2rayN 配置

1. 从 `D:\Program Files\v2rayN\guiConfigs\guiNConfig.json` 或 v2rayN UI 确认 mixed 端口。
2. 必要时在启动 Hermes 的同一环境设置：

```cmd
set HTTPS_PROXY=http://127.0.0.1:10808
set HTTP_PROXY=http://127.0.0.1:10808
hermes desktop
```

3. 连通性验证：

```bash
curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 --proxy http://127.0.0.1:10808 https://api.openai.com
```

OAuth provider 使用的 endpoint 可能不同；公共 API 的 curl 只能验证网络，不能单独证明 OAuth 模型可调用。

---

## OpenAI Codex OAuth 与动态模型目录

### 认证

1. ChatGPT 安全设置中开启 Codex 设备代码授权。
2. `hermes auth add openai-codex`
3. 浏览器完成 OAuth。
4. 用 `hermes auth list openai-codex` 核对 credential，而不是读取/打印 token。

### 模型列表不能写死

OpenAI Codex OAuth 的允许模型由服务端动态下发。旧经验“某模型只限 API、Plus 不能用”可能随时过期，**不能凭印象否定用户在模型库里看到的新模型**。

优先核对：

```bash
hermes model --refresh
hermes config show
```

无交互环境可查看 Hermes home 下的 `provider_models_cache.json`，但必须把它标注为“当前缓存快照”，不能当永久白名单。`context_length_cache.yaml` 可核对具体 endpoint 下的上下文长度。

2026-08-03 实测的 `openai-codex` 缓存快照包含：

- `gpt-5.6-sol`
- `gpt-5.6-terra`
- `gpt-5.6-luna`
- `gpt-5.5`
- `gpt-5.4`
- `gpt-5.4-mini`

其中 `gpt-5.6-sol` 已通过真实 OAuth 文字调用；该事实只说明当时账号可用，未来仍以实时目录和烟雾测试为准。

### 最小文字烟雾测试

```bash
hermes chat -q "只回答 ok" --provider openai-codex -m gpt-5.6-sol -Q --source tool
```

测试模型能力而不是用户工作流时，可在**无副作用的隔离探针**上增加 `--ignore-rules`，避免 SOUL 的“先列计划再执行”让工具调用测试停在二次确认。不得用它绕过真实任务的用户确认。

详见 `references/openai-codex-model-smoke-tests.md`。

---

## 视觉路由：优先让主模型看原始像素

Hermes 官方路由规则：

- 主模型支持视觉，并且 provider 支持图片内容 → 图片作为原始像素直接交给主模型。
- 主模型为文本模型或通道不支持图片 → 才调用 `auxiliary.vision` 生成文字描述。
- `auxiliary.vision.provider: auto` 的首选是当前主 provider + 当前主模型；显式 provider/model 覆盖会阻止跟随。

### 让视觉动态跟随主模型

```bash
hermes config set auxiliary.vision.provider auto
hermes config set auxiliary.vision.model ""
hermes config set auxiliary.vision.base_url ""
hermes config set auxiliary.vision.api_key ""
```

然后重启需要长期读取配置的组件：

```bash
hermes gateway restart
hermes config show
```

验证标准：`hermes config show` 不再列出显式 `Vision provider=... model=...` override。对 vision-capable 主模型调用 `vision_analyze` 时，原生快路径会返回“Image loaded into your context”，下一轮由主模型直接读像素，而不是拿到辅助模型生成的文字摘要。

### 显式锁定辅助视觉

只有当主模型视觉不稳定或用户明确要求固定回退模型时，才锁定：

```bash
hermes config set auxiliary.vision.provider openai-codex
hermes config set auxiliary.vision.model gpt-5.5
hermes config set auxiliary.vision.base_url ""
hermes config set auxiliary.vision.api_key ""
```

### 旧 endpoint 残留

从 Agnes、自建网关等迁移时，只改 provider/model 不够；显式 `base_url` / `api_key` 可能继续把请求送往旧 endpoint。症状包括供应商名与当前配置不符、`No available channel`、图片 analysis failed。修复后必须重启并用真实图片验证。

详见 `references/openai-codex-vision-routing.md`。

## Codex 国内中转站

cdxai.cn 提供 OpenAI 兼容 API 中转，支持 GPT-5.6 Sol/Terra/Luna。定价和对比见 `references/cdxai-gateway.md`。接入方式同自定义 provider。

**实测可用性（2026-08-06）**：`gpt-5.6-sol` ✅、`gpt-5.6-terra` ✅、`gpt-5.5` ✅、`gpt-5.4-mini` ✅；`gpt-5.6-luna` ❌（502 Upstream access forbidden，需找 cdxai 客服 woslii 开通）。分组 0.95x 官方直连最便宜。

## DeepSeek V4 Flash vs Pro（2026-08-06 查证）

⚠️ **模型名以官方 `/v1/models` 为准（2026-09-15 实测）**：DeepSeek 直连**只有两个名字** —— `deepseek-flash`（日常）与 `deepseek-v4-pro`（重活）。**不存在 `deepseek-v4-flash`** —— 这个错名曾被同时写进记忆、`delegation.model` 和 cron 任务里，凡哥问\"怎么又变成 V4 了\"才查出来。凡哥日常主模型＝ `deepseek-flash`（OpenAI 兼容通道 `https://api.deepseek.com/v1`，就是官方直连，Hermes 内部叫 `openai-api` 只是格式名）。**官方更新日志 2026-07-31 确认**：V4-Flash 正式版（DeepSeek-V4-Flash-0731）Agent 能力大幅增强，基准测试远超 V4-Pro-Preview，且**原生支持 Responses API 并针对性适配 Codex**（Pro 暂不支持）。V4-Pro 未同步升级，正式版"尽快发布"。

| 基准测试 | V4-Flash 得分 | 测什么 |
|---------|-------------|-------|
| Terminal Bench 2.1 | 82.7 | 命令行/终端智能体 |
| Cybergym | 76.7 | 网络安全智能体 |
| DSBench-FullStack | 68.7 | 全栈开发 |
| Toolathlon verified | 70.3 | 工具调用 |
| NL2Repo | 54.2 | 自然语言→代码仓库 |
| DeepSWE | 54.4 | 软件工程 |
| DSBench-Hard | 59.6 | Coding Agent 难题 |
| Agent Last Exam | 25.2 | 综合智能体考试 |
| Automation Bench | 25.1 | 自动化任务 |

**一句话**：Flash 强在动手（操作电脑/用工具/改文件/跑工作流），弱在开放知识问答。凡哥的用法（操作文件+跑工作流+读文档）正好是 Flash 强项。

**价格**（每百万 token，官方）：Flash 输入¥1/缓存命中¥0.02/输出¥2；Pro 输入¥3/缓存¥0.025/输出¥6。**DeepSeek 是付费 API，不是免费**——凡哥有官方 API key，走 `https://api.deepseek.com/v1` 直连。

**切换命令**：`hermes config set model '{"default": "deepseek-flash", "provider": "deepseek"}'`，重启生效；会话内 `/model <模型名>` 即时切。

**改主模型/provider 的完整流程（2026-09-23 本机实操：中转站 → 官方直连）**：凡哥的配置一度是 `provider: "Yue88 中转站"` + `base_url: https://api-yue88.xyz/v1` + 该站自己的 `api_key`（**自定义 provider 名可以是中文**）。换成官方 provider 时**只改 default/provider 不够 —— 旧 base_url + api_key 会继续把请求送去中转站**（与上文「旧 endpoint 残留」同一条坑，只是这次发生在**主模型层**）：

```bash
cd D:/Hermes
cp config.yaml "config.yaml.bak-$(date +%Y%m%d_%H%M%S)"   # 先备份，可回滚
hermes config set model.default deepseek-flash
hermes config set model.provider deepseek
hermes config unset model.base_url        # ← 必须清，否则仍走旧 endpoint
hermes config unset model.api_key         # ← key 改用 .env 里的 DEEPSEEK_API_KEY
hermes config                             # 复核：Model: {'default': 'deepseek-flash', 'provider': 'deepseek', ...}
```

- `hermes config` 子命令 = `show / edit / get / set / unset / path / env-path / check / migrate`。**清字段用 `unset`，不要用 `set ""`**；`hermes config get model.base_url` 回 `Config key not set: model.base_url` = 真清干净了。
- 改完**新会话生效**；要让网关里立刻生效需 `hermes gateway restart`（会话内 `/restart`）。
- 顺手核 `delegation.model` 与 cron 的 `model_snapshot`（同下文「填模型名前的核验纪律」），避免只改了主模型、子代理和定时任务还在用旧 provider。

**填模型名前的核验纪律（2026-09-15 教训：从记忆里抄名字 → 写出无效名）**：任何地方要写模型名（`model.default` / `delegation.model` / cron `--model` / 给外部 AI 的稿子），先核一次官方目录：

```bash
set -a; . D:/Hermes/.env; set +a
curl -s "${DEEPSEEK_BASE_URL:-https://api.deepseek.com}/v1/models" -H "Authorization: Bearer $DEEPSEEK_API_KEY"
```

连带要查的三处：① `model.default` ② **`delegation.model`（子代理）**——本次这里写的就是无效名，意味着派子代理时会失败或被兜底 ③ cron 任务的 `model_snapshot` / `provider_snapshot`（`hermes cron list`，出现 `error: … (N failures in a row)` 就是坏任务）。修子代理名：`hermes config set delegation.model deepseek-flash`。

## 第三方免费 API 平台：Agnes AI

Agnes AI 提供免费的 OpenAI 兼容全模态 API（文本/图像/视频）。

- **Base URL**：`https://apihub.agnes-ai.com/v1`
- **认证**：`Authorization: Bearer <API_KEY>`（key 从 platform.agnes-ai.com 控制台获取）

**可用模型**（2026-08-06 实测全通）：

| 模型 | 类型 | 实测 |
|------|------|------|
| `agnes-2.0-flash` | 文本标准 | ✅ chat OK |
| `agnes-2.5-flash` | 文本推理 | ✅ chat OK（max_tokens≥200否则content空） |
| `agnes-2.5-pro` | 文本推理旗舰 | 📋 |
| `agnes-2.5-pro-alpha` | 文本推理实验 | 📋 |
| `agnes-image-2.1-flash` | 图像生成 | ✅ /v1/images/generations |
| `agnes-video-v2.0` | 视频生成 | ✅ /v1/videos 异步，~70s，1088×832 |

**推理模型坑**：`agnes-2.5-*` 的 reasoning 和 content 分开计数，`max_tokens` 必须 ≥200。

**Hermes 接入**：
- 视觉：`custom_providers` 加 agnes → `auxiliary.vision.provider: custom:agnes` + `model: agnes-2.5-flash`，重启生效
- 生图/生视频：脚本 `D:\Hermes\scripts\agnes_gen.py image/video "提示词"`（绕过 Hermes image_generate 原生只支持 FAL 的限制）

---

## 视觉测试方法

不要只问“能不能看图”。选一张有可核验答案的 OCR 图，列出判定项：标题、状态、段位、星数、奖励、按钮、局部小字。

1. 主模型直接图片测试：

```bash
hermes chat -q "只根据像素识别图中文字" --image "D:/path/test.png" --provider openai-codex -m gpt-5.6-sol -Q --source tool
```

2. 当前会话调用 `vision_analyze`，观察是原始图片 envelope 还是纯文字描述。
3. 对模糊小字裁切放大后再分析；临时裁切图验证完立即删除。
4. 把结果与已知答案逐项比对，不能以“返回了内容”当成功。

---

## 常见诊断

### 语音播报全挂：`TTS chunk N failed (edge)`（403 → 429 → 正解是升 edge-tts 7.3.x）

**症状**：播报报 `TTS chunk N failed (edge): 403 / 429, Invalid response status, url='wss://...'`。
本机 TTS 通道 = `config.yaml` 的 `tts.provider: edge` / `tts.edge.voice: zh-CN-XiaoxiaoNeural`。

**★ 2026-10-27 定论（推翻 10-12 的判断，别再走老路）**：
正解只有一个 —— **把 edge-tts 升到 7.3.0+（现 7.3.1）**。
7.3.0 合的是 PR **#492「Sec-MS-GEC v2 令牌」**：`SEC_MS_GEC_VERSION = f"2-{CHROMIUM_FULL_VERSION}"`。
**老域名 + v2 令牌就是通的**：实测一次成功 1.1s / 23KB，连发两次 1.2~1.3s 都成功，不限流。

**先按这个矩阵排除，别重复乱试**（每一项都真跑过）：

| 探针 | 结果 | 结论 |
|---|---|---|
| `voices/list` HTTPS（同 headers） | ✅ 200 / 170KB | **音色列表还好 → 别误判成"网断了"** |
| 老地址枚举 140/141/142/143/144 版本号、或不带 | ❌ 全 403 | 不是 `Sec-MS-GEC-Version` 过期 |
| 带 / 不带 `Sec-MS-GEC` | ❌ 全 403 | 不是 DRM 令牌算错 |
| 走本机代理（换出口 IP） | ❌ 仍 403 | 不是地区墙 / 不是 IP 被封 |
| 本机时钟 vs 服务端 `Date` 头 | 偏差 2.5s | 不是时钟偏移 |
| edge-tts 7.2.7 / 7.2.8 | ❌ 都挂 | 当年还没 v2 令牌，升小版本没用 |
| **新地址 `api.msedgeservices.com`**（手改 constants） | ⚠️ 能出音频但**频繁 429** | ← **弯路，已废弃**，见下 |
| **edge-tts 7.3.0 / 7.3.1**（官方 v2 令牌） | ✅ 出音频、不限流 | ← **真正的修法** |

**为什么"新地址"是弯路（2026-10-27 血泪）**：
PR #491「改用 `api.msedgeservices.com`」看着最像正解，**已被作者 closed，理由 `Superseded by #492`**。
新域名虽然能出音频，但那个网关把公共 `TRUSTED_CLIENT_TOKEN` 当订阅键 → **经常 429 限流**；
短时间连打会把额度彻底打满，5s/15s/40s 退避都救不回来（越测越挂）。
判断"有没有官方修法"要看 **release 时间线**，不是看装的是什么版本：
`pip index versions edge-tts` 里 7.2.8 是 3 月的，**7.3.0 / 7.3.1 是 2026-10-13 才发的**。

**修法（跑脚本，别手改 site-packages）**：
```bash
python D:/Hermes/skills/productivity/hermes-network-proxy/scripts/patch_edge_tts.py          # 确保 >=7.3 + 真实合成自检
python D:/Hermes/skills/productivity/hermes-network-proxy/scripts/patch_edge_tts.py --verify # 只查 + 试合成
python D:/Hermes/skills/productivity/hermes-network-proxy/scripts/patch_edge_tts.py --revert # 重装官方 wheel，冲掉任何手改
```
手工等价命令（**必须 `--no-deps`**，别让它顺带改 Hermes 的依赖树）：
```bash
D:/Hermes/hermes-agent/venv/Scripts/python.exe -m pip install --no-deps -U "edge-tts==7.3.1"
```
装完 `constants.py` 应该是干净原版：`WSS_URL` 指向 `speech.platform.bing.com`、
`SEC_MS_GEC_VERSION = f"2-{CHROMIUM_FULL_VERSION}"`。**不要再往新域名打补丁。**

**★★ 最坑的一条：Hermes 会把你的升级偷偷降级回去（2026-10-27 血泪，先看这条再看别的）**
`tools/lazy_deps.py` 里是**硬钉版本**：`"tts.edge": ("edge-tts==7.2.7",)`。
`_import_edge_tts()` 每次调用都先跑 `lazy_deps.ensure("tts.edge")`，发现不满足 `==7.2.7`
就 **pip 降级**。所以升到 7.3.1 后**第一次调 TTS 就被打回 7.2.7**（令牌变回 `1-` → 403 复现），
外在表现就是「**每次重启都还是失败 / 刚装好的版本一转身就没了**」。
必须同时改两处：

| 文件 | 改法 |
|---|---|
| `hermes-agent/tools/lazy_deps.py` | `"tts.edge": ("edge-tts==7.3.1",)` |
| `hermes-agent/pyproject.toml` | `edge-tts = ["edge-tts==7.3.1"]` |

改完自检（跑一次 `ensure()` 后版本必须**还是** 7.3.1）：
`D:/Hermes/scripts/verify_lazydeps_pin.py`
**判断"有没有被降级"**：看报错 URL 里的 `Sec-MS-GEC-Version=`，`1-` 就是旧的 7.2.7，
`2-` 才是 7.3.x。

**⚠️ 三个坑（第 3 条最容易误判；10-13 / 10-27 两次实测都踩到）**
1. 临时验证改常量时：`communicate.py` 是 `from .constants import WSS_URL` 直接导入的 —— **必须同时改
   `edge_tts.constants` 和 `edge_tts.communicate` 两个模块属性**，只改前者不生效（报错 URL 还是老的，会误判成"新办法也不行"）。
2. 装包一定加 `--no-deps`：venv 里依赖已齐，否则 pip 会顺带动 `aiohttp`/`tabulate`，撞 Hermes 其它依赖。
3. ★ **改完必须重启 Hermes 桌面 App**（**且"重启"极可能是假的** —— 详见下一节，务必先看）。
   `tools/tts_tool.py` 的 `_import_edge_tts()` 是懒加载，模块一旦进了 `sys.modules` 就再也不读盘 ——
   磁盘改了、App 进程里还是老地址。**在 `terminal` 里测能过是因为每次都是新进程，极易误判成"已经修好了"**。
   判断有没有重启成功：让 Hermes 播报一次，报错 URL 里还有 `speech.platform.bing.com` = 没重启。

**验证标准 = 真出一段非 0 字节音频**（只看"没报错"不够）：
```bash
python -c "
import asyncio, edge_tts
async def m(): await edge_tts.Communicate('语音测试','zh-CN-XiaoxiaoNeural').save('t.mp3')
asyncio.run(m())"
ls -l t.mp3    # 应 10~20KB
```

完整证据链（探针脚本、403 响应头、上游 issue/PR 时间线、locale 相关的附带小修）见
`references/edge-tts-403-endpoint-migration.md`。

### ★ 桌面 App 的「重启」是假的 → 改 site-packages 后必须「真重启」（2026-10-14 实测）

**通用教训（不限 TTS）**：凡是改 `venv/Lib/site-packages/**`、或任何**在 import 期加载**的文件，
`hermes_cli.main serve` 后端进程**必须真重启**才生效。**在 `terminal` 里另起进程测通 ≠ App 内生效。**

**坑**：桌面板点窗口右上角 X **只是收进托盘，进程根本没退**。桌面板带 **`Tray` + `requestSingleInstanceLock`**
（在 `apps/desktop/release/win-unpacked/resources/app.asar` 里 grep 得到），关窗后再点图标 = 把**老实例唤回来**。
所以用户说"我重启过了"可能压根没重启 —— 2026-10-14 实测：5 个 `Hermes.exe` + 后端 `serve` 的
`CreationDate` **全是 `2026/10/12 14:30:38-39`，20 小时没变**，而"重启"是当天上午做的。

**判定唯一标准 = 进程启动时间**（窗口开关、日志里出现 `[boot] Finalizing desktop startup` 都不算证据）：

```bash
powershell -NoProfile -Command "Get-CimInstance Win32_Process | Where-Object { \$_.Name -eq 'Hermes.exe' -or (\$_.Name -eq 'python.exe' -and \$_.CommandLine -match 'hermes_cli\.main\s+serve') } | Select-Object ProcessId,Name,CreationDate | Format-Table -AutoSize"
```

比对规则：`CreationDate` 必须**晚于**改动文件的 mtime，才算真重启。

**两种真重启方式**：

1. 让用户手动退：**托盘图标右键 → 退出**（不是点 X）。App 自己的文案也这么说：
   `当前运行的应用在此功能加入前启动。请退出并重新打开 Hermes，然后回到此处。`
2. 跑现成脚本（推荐，可替用户远程做）：

```bash
powershell -NoProfile -Command "Start-Process powershell -ArgumentList @('-NoProfile','-ExecutionPolicy','Bypass','-File','D:\Hermes\scripts\restart_hermes_app.ps1','-DelaySeconds','90') -WindowStyle Hidden"
```

`scripts/restart_hermes_app.ps1`（本技能自带，换电脑不丢）：等 N 秒（留给 Agent 把话说说完）→
杀全部 `Hermes.exe` + 后端 `serve` + `scrapling-mcp` → 等进程真退干净（单实例锁释放，最多 30s）→
重新拉起 `Hermes.exe` → 把重启前后进程 `CreationDate` 写进日志。自带刹车：`D:\Hermes\logs\restart_cancel.flag`
存在则放弃；exe 不存在则**一个进程都不杀**。日志 `D:\Hermes\logs\restart_app.log`。

**⚠️ 替用户重启前必须先讲清代价**：脚本会杀掉宿主进程 → **当前窗口会自己关掉再开**，且会打断**其它会话**
正在跑的轮次。先发一条消息说明执行时间与取消方式，再用 `-DelaySeconds`（≥60s）兜住；**禁止静默执行**。

### 上游服务端改动 → 直接查 issue/PR 时间线（通用手法）

多个用户/地区**同一时间**一起挂、且本地换参数怎么试都不动 → 大概率上游改了服务端。
别继续在本地瞎试，去问上游仓库 —— **当天的 open PR 常常就是现成答案**：

```bash
curl -s "https://api.github.com/repos/<owner>/<repo>/issues?state=all&sort=created&direction=desc&per_page=10" \
 | python -c "import sys,json;[print(i['created_at'][:10],'|',i['state'],'|',i['title']) for i in json.load(sys.stdin)]"
curl -s "https://api.github.com/repos/<owner>/<repo>/pulls?state=all&sort=created&direction=desc&per_page=5" \
 | python -c "import sys,json;[print(i['number'],i['state'],i['title'],'\n',(i.get('body') or '')[:800]) for i in json.load(sys.stdin)]"
curl -sL "https://patch-diff.githubusercontent.com/raw/<owner>/<repo>/pull/<N>.diff"
```
流程：**先本地 monkeypatch 验证通过 → 再决定是否落到安装目录 / 是否等官方发版**。
⚠️ 注意 issue 列表里**同名旧 issue 可能是上一轮的、已被关闭的**（本次 #458 是 1 月的旧 403，
其"升级到 7.2.7"的结论对 10 月这轮完全无效）—— 看 `created_at` 挑当天/本周的那条。

**⚠️ 更贵的坑：正解可能是「新版已经发了」，而你还在手改**（2026-10-27 二次踩，代价是白走两天弯路）：

- **只看 `pip index versions` 或已装版本 = 会误判"上游没修法"**。必须看 release 的 `published_at`：
  本次 7.3.0 / 7.3.1 是 **2026-10-13** 才发的 —— 10-12 那天确实还没有，两天后就有了，手改随即变成债。
  ```bash
  curl -s "https://api.github.com/repos/<owner>/<repo>/releases?per_page=5" \
   | python -c "import sys,json;[print(r['tag_name'],r['published_at']) for r in json.load(sys.stdin)]"
  ```
- **PR/issue 被 `closed` ≠ 被拒**，必须读关闭理由。本次 #491 的 closing comment 是
  `Superseded by #492` —— 我当时把"未合并"直接读成"没修好"，于是手动改了一行 constants 走
  另一条路：能出音频、但**频繁 429**，比原故障更难查。
- 判据顺序：`merged_at` → closing comment 里的 `Superseded by #N` / `Duplicate of #N` →
  顺着那个 PR 找它落在哪个 release → `pip download` 那个版本**解包读源码**核对常量（别只看 changelog 标题）。
- **手改 site-packages 是临时手段，不是修法**：必须同时留下 ①幂等脚本 ②自动备份 ③
  "官方发版后如何回滚重装"的一句话，否则下一个会话会把弯路当正解继续维护。

### GitHub 直连被墙 → 装软件走另一条路（2026-09-23 实测）

本机实测**只挡主域**：`github.com` 超时（000），但 `api.github.com` 200、`apps.microsoft.com` 302、`objects.githubusercontent.com` 可连、`www.yworks.com` 200 → **换通道即可，不必先折腾代理**。先分域探测再下结论：

```bash
for h in github.com api.github.com apps.microsoft.com; do printf "%s -> " "$h"; \
  curl -s -o /dev/null -w "%{http_code} (%{time_total}s)\n" --max-time 8 "https://$h"; done
```

- ⚠️ `winget install <包>` 的**默认源清单 URL 常常就是 GitHub 直链** → 被墙时报 `InternetOpenUrl() failed. 0x80072efd`（本次 `JGraph.Draw` 即此坑）→ 改走 **`--source msstore`**（微软商店源、Store CDN）实测成功。
- 镜像前缀 `https://gh-proxy.com/<原 GitHub 直链>` 可下（HTTP 206）；**第三方通道下载件必须核验**：`size` + `sha256`（对比 GitHub API `assets[].digest`）+ `Get-AuthenticodeSignature`。
- 代理只读排查：**`clash-verge-service.exe` 在跑 ≠ 代理可用**（服务≠内核监听）→ 查 `%APPDATA%\io.github.clash-verge-rev.clash-verge-rev\*.yaml` 的 `mixed-port`，再用 `netstat | grep LISTENING` 确认；**凡哥的代理不擅自改、不擅自起**。
- 装完要**实测一次真实用途**再宣布成功；随后删掉下载包（清理铁律）。

完整配方（分域探测 / 四条通道 / 核验三连 / 代理只读排查）见 `references/blocked-github-downloads.md`。

### web_search / 搜索工具老是说"受限"

**根因**：Hermes 的 `web_search` 是本地工具直接向海外搜索引擎发 HTTP 请求。国内网络下必须走代理，否则全被墙。GPT 不卡是因为 OpenAI 服务端调 Bing，不经过用户本地网络。

**修复**：在 `D:\Hermes\.env` 追加代理环境变量（重启或 `/reload`）：

```
HTTP_PROXY=http://127.0.0.1:10808
HTTPS_PROXY=http://127.0.0.1:10808
```

验证：`curl -s -o /dev/null -w "%{http_code}" --proxy http://127.0.0.1:10808 "https://lite.duckduckgo.com/lite/?q=test"` 应返回 200-202。

搜索提供商（内置 braive-free/ddgs/searxng/exa/tavily/firecrawl）配好代理后默认链就能用，无需改后端。

### 视觉图片请求过慢或反复超时

视觉工具不能把本地4K PNG原图直接转成大Base64发送。应先使用本地临时副本按最长边1568px、Base64约5MB预算压缩后再发送；原始图片必须保持不变，用户提供`region`时先裁剪再缩放，以保留局部细节。当前实现已在`tools/vision_tools.py::vision_analyze_tool`中固定执行该传输预处理。

### `model_not_found` / 模型库有但调用失败

模型显示、账号授权、具体通道可调用是三件事。用最小真实调用确认；失败时刷新目录并保留真实错误，不要编造订阅范围。

### 工具测试停在“请确认执行”

这可能是项目/SOUL 规则生效，不是模型不会调用工具。对安全的能力探针使用隔离会话和 `--ignore-rules`；对真实任务继续遵守用户确认规则。

### 视觉返回内容但 OCR 错

这不是“视觉链路成功”的充分证据。用已知答案逐项计分；对关键小字裁切放大复核。
