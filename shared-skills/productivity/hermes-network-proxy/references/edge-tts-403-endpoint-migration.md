# edge-tts 语音播报故障全链：403 →（误入）新域名 429 → v2 令牌正解

> 最后订正：2026-10-27。**结论以本文件为准**，10-12/10-13 的"换新域名"判断已被推翻。

## 症状

```
TTS chunk 1 failed (edge): 403, Invalid response status,
url='wss://speech.platform.bing.com/consumer/speech/synthesize/readaloud/edge/v1?TrustedClientToken=...'
```

之后（手改新域名后）变成：

```
TTS chunk 1 failed (edge): 429, Invalid response status,
url='wss://api.msedgeservices.com/tts/cognitiveservices/websocket/v1?Ocp-Apim-Subscription-Key=...'
```

## 时间线（按发布时间排，这是关键）

| 日期 | 事件 |
|---|---|
| 2026-10-10 | issue #490 报 403 潮 |
| 2026-10-12 | PR #491「改用 `api.msedgeservices.com`」+ 修 locale 日期解析 |
| 2026-10-13 15:34 | **release 7.3.0**：合入 PR #492「Sec-MS-GEC v2 令牌」、#488 进度条、#493 |
| 2026-10-13 15:57 | **release 7.3.1**：修 locale 相关 `parse_rfc2616_date` |
| 2026-10-13 之后 | PR #491 被 close，理由 **`Superseded by #492`** |

**教训**：`pip index versions` 只能看到版本号，看不到"上游是否刚发了修法"。
本次卡点就在这 —— 10-12 那天 7.3.x 还没发（7.2.8 是 3 月的），所以只能手改；
但 10-13 官方就发了正解，手改就成了债。

## 正解

```bash
D:/Hermes/hermes-agent/venv/Scripts/python.exe -m pip install --no-deps -U "edge-tts==7.3.1"
```

装完 `constants.py` 应是**干净原版**：

```python
BASE_URL = "speech.platform.bing.com/consumer/speech/synthesize/readaloud"
WSS_URL  = f"wss://{BASE_URL}/edge/v1?TrustedClientToken={TRUSTED_CLIENT_TOKEN}"
SEC_MS_GEC_VERSION = f"2-{CHROMIUM_FULL_VERSION}"   # ← v2 令牌，这才是 403 的解
```

实测：一次成功 1.1s / 23,760 字节；连发两次 1.2s、1.3s，各 ~21KB，无 429。

## 弯路实录：新域名为什么不能当修法

`WSS_URL` 手改成 `api.msedgeservices.com/tts/cognitiveservices/websocket/v1` +
`?Ocp-Apim-Subscription-Key=<TRUSTED_CLIENT_TOKEN>` 后：

- ✅ 能出音频（10-12 实测 19,152 / 30,528 / 18,144 字节都成功过）
- ❌ **频繁 429**。那个网关把公共 `TRUSTED_CLIENT_TOKEN` 当**订阅键**用 → 限流窗口极短
- ❌ 越测越挂：5s → 15s → 40s 退避全部 429；10-27 连打后连续三个真实请求全 429
- 429 响应头（无 `Retry-After`，等于让你自己猜）：
  ```
  x-ceto-ref: <hash>|2026-10-27T08:47:17.390Z
  X-CDN-TraceID: 0.18d854b8.1793090837.50090cb
  Content-Length: 0
  ```
- 另有间歇 `NoAudioReceived`（握手 200 但音频流空）——同一限流压力下的副产物

## 排除矩阵（都真跑过，别重复）

| 探针 | 结果 | 结论 |
|---|---|---|
| `voices/list` HTTPS | ✅ 200 / 170KB | 音色列表没坏，别误判"网断了" |
| 版本号 140/141/142/143/144、或不带 | ❌ 全 403 | 不是版本号过期 |
| 带 / 不带 `Sec-MS-GEC` | ❌ 全 403 | 不是 DRM 算错（是**令牌代次**旧了） |
| 走代理 7897 换出口 IP | ❌ 仍 403 | 不是地区墙 / 不是 IP 封 |
| 本机时钟 vs 服务端 `Date` | 偏差 2.5s | 不是时钟 |
| 7.2.7 / 7.2.8 | ❌ | 那时还没 v2 |
| 手改新域名 | ⚠️ 能出但 429 | 弯路 |
| **7.3.0 / 7.3.1** | ✅ 稳定 | **正解** |

## app 侧配合（必做）

`tools/tts_tool.py` 的 `_import_edge_tts()` 是懒加载，模块进了 `sys.modules` 就不再读盘：

- 装/改完 **必须真重启 Hermes 桌面 App**
- **桌面板"假重启"**：有托盘 + `requestSingleInstanceLock`（`app.asar` 里可查到），点 X 只收托盘，
  再点图标是把老实例叫回来 → 进程 CreationDate 不变就是没重启
- 校验脚本：`D:/Hermes/scripts/restart_hermes_app.ps1`（杀干净 → 等单实例锁释放 → 重新拉起，写日志到 `logs/restart_app.log`）
- 判断生效：报错 URL 里的域名/status 变了 = 新代码进内存了

## 附：`tts_tool.py` 的 429 退避补丁（2026-10-27 加，保留）

`_generate_edge_tts()` 里加了 5s / 15s / 40s 三段退避，只在 **429、5xx、连接级错误、
`NoAudioReceived`** 时重试；**403 不重试**（真故障要露出，不能被重试吞掉）。
升到 7.3.1 后正常情况不会触发，留着当保险。验证脚本：`D:/Hermes/scripts/test_tts_retry.py`。
