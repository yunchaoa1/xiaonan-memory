# edge-tts 403 / 微软换合成端点（2026-10）· 完整证据链

> 场景：Hermes 语音播报报 `TTS chunk 1 failed (edge): 403, message='Invalid response status',
> url='wss://speech.platform.bing.com/consumer/speech/synthesize/readaloud/edge/v1?...Sec-MS-GEC=...'`
> 本机配置：`D:\Hermes\config.yaml` → `tts.provider: edge` / `tts.edge.voice: zh-CN-XiaoxiaoNeural`
> 排查日期：2026-10-12（Windows / Hermes 桌面版）

---

## 1. 结论（一句话）

微软把 Edge「大声朗读」的**合成 WebSocket** 从 `speech.platform.bing.com` 迁到了
**`api.msedgeservices.com`**（Edge 155 走的新地址）。老地址从 2026-10 初开始对大量地区返回 403，
到 2026-10-12 连美国也开始了。**与本地网络、代理、IP、令牌、包版本、系统时钟全部无关。**

## 2. 排除矩阵（每一项都真跑过，别重复试）

| # | 探针 | 实际结果 | 能排除什么 |
|:-:|---|---|---|
| 1 | 老地址 WSS 握手 | ❌ `WSServerHandshakeError 403` | 复现主症状 |
| 2 | `voices/list` HTTPS（同 headers） | ✅ **200 / 170,998 字节** | **不是"net 断了"** —— 只有合成那根线被掐 |
| 3 | 枚举版本号 140 / 141 / 142 / 143 / 144 / 不带 | ❌ 全 403 | 不是 `Sec-MS-GEC-Version` 过期 |
| 4 | 带 `Sec-MS-GEC` / 完全不带 | ❌ 全 403 | 不是 DRM 令牌算错 |
| 5 | 走本机代理（出口 IP 换成 103.151.173.208） | ❌ 仍 403 | 不是地区墙 / 不是 IP 被封 |
| 6 | 本机时钟 vs 服务端 `Date` 响应头 | 偏差 **2.5 秒** | 不是时钟偏移（GEC 是时间函数） |
| 7 | edge-tts **7.2.7** 与 **7.2.8** | ❌ 都挂 | 不是包版本旧（7.2.7 是当时最新已发布版） |
| 8 | TCP/TLS/DNS 到 `speech.platform.bing.com` | ✅ 0.07s / TLSv1.3 | 不是链路问题 |
| 9 | **新地址 `api.msedgeservices.com`** | ✅ **出声，19,152 字节 MP3** | **就是修法** |

DNS/TLS 探针：
```bash
python -c "
import socket,ssl,time
h='api.msedgeservices.com'
print('DNS->', socket.gethostbyname(h))
s=socket.socket(); s.settimeout(8); t=time.time(); s.connect((h,443))
print('TCP OK', round(time.time()-t,2),'s')
c=ssl.create_default_context().wrap_socket(s, server_hostname=h); print('TLS', c.version())
"
```

403 响应头（老地址，注意 `Content-Length: 0`、无响应体、`X-MSEdge-Ref` 里的边缘节点编号）：
```
strict-transport-security: max-age=31536000; includeSubDomains
X-Cache: CONFIG_NOCACHE
Accept-CH: Sec-CH-UA-Arch, Sec-CH-UA-Bitness, ...
X-MSEdge-Ref: Ref A: E44817C9F44C4D2097DD0C92F35E352E Ref B: SG2AA1070305031 Ref C: 2026-10-12T10:20:35Z
Date: Mon, 12 Oct 2026 10:20:35 GMT
Content-Length: 0
```
> `Ref B` 那个值是边缘节点 ID（`SG2` = 新加坡 PoP）。**它不是错误码，别拿它当线索。**

## 3. 上游时间线（就是从这里找到答案的）

```
curl -s "https://api.github.com/repos/rany2/edge-tts/issues?state=all&sort=created&direction=desc&per_page=10"
curl -s "https://api.github.com/repos/rany2/edge-tts/pulls?state=all&sort=created&direction=desc&per_page=5"
```

- **#458**（2026-01-20 开、2026-03-22 关为 not planned）标题就是
  `WSServerHandshakeError: 403, message='Invalid response status'` —— **那是上一轮，当时的解法是升到 7.2.7**。
  所以"403 就升级"这条旧经验在 2026-10 **已经失效**（本机 7.2.7/7.2.8 同样 403）。
- **#490**（2026-10-10 开）本轮的首个报告，帖子里的报错文本与本机**逐字一致**
  （含 `Sec-MS-GEC-Version=1-143.0.3650.75`）。
- **PR #491**（2026-10-12 开，当天）＝答案。正文关键句：
  > "Since October 2026 `speech.platform.bing.com` answers the synthesis WebSocket with 403 in many
  > countries, and since 12 October in the US too. Microsoft Edge 155 synthesizes through
  > `api.msedgeservices.com/tts/cognitiveservices/websocket/v1`. That host also accepts the legacy
  > token given as `Ocp-Apim-Subscription-Key`, with the legacy `Sec-MS-GEC` and `Sec-MS-GEC-Version`."
  > "The voice list still answers on the legacy host, so `VOICE_LIST` is unchanged."

取 diff：
```bash
curl -sL "https://patch-diff.githubusercontent.com/raw/rany2/edge-tts/pull/491.diff"
```

## 4. 补丁内容（PR #491 的核心，上游截至 2026-10-12 未合并）

文件：`D:\Hermes\hermes-agent\venv\Lib\site-packages\edge_tts\constants.py`

```python
# 改前
WSS_URL = f"wss://{BASE_URL}/edge/v1?TrustedClientToken={TRUSTED_CLIENT_TOKEN}"

# 改后
WSS_URL = (
    "wss://api.msedgeservices.com/tts/cognitiveservices/websocket/v1"
    f"?Ocp-Apim-Subscription-Key={TRUSTED_CLIENT_TOKEN}"
)
```

- `TRUSTED_CLIENT_TOKEN` 本身**不变**（`6A5AA1D4EAFF4E9FB37E23D68491D6F4`），只是换了个 query 名传给新主机。
- `VOICE_LIST`（音色列表）**不用改** —— 老主机仍在服务它。
- `Sec-MS-GEC` / `Sec-MS-GEC-Version` / `ConnectionId` 由 `communicate.py` 照旧往 URL 上追加，不用动。
- 音频格式不变：MP3 / 24kHz / 单声道。

PR 里同时附带的第二个小修（locale 无关地解析服务端 `Date`）：`drm.py` 的
`parse_rfc2616_date` 用 `strptime("%a, %d %b %Y %H:%M:%S %Z")`，`%a`/`%b` 跟随进程 locale，
非英文 locale 下解析失败会抛 `SkewAdjustmentError: Failed to parse server date`。
**只在 locale 不是英文的系统上才会碰到**；简体中文 Windows 下的 Python 默认 `C` locale，本机没复现。
若要一并修：`from email.utils import parsedate_to_datetime` 替换掉 `strptime` 分支。

## 5. 验证脚本

```bash
cd "$LOCALAPPDATA/Temp"
# 1) 先验"能用"：monkeypatch 到新端点跑一次（注意要同时改两个模块，见坑 1）
python - <<'EOF'
import asyncio, edge_tts, edge_tts.constants as C, edge_tts.communicate as CM
NEW = ("wss://api.msedgeservices.com/tts/cognitiveservices/websocket/v1"
       f"?Ocp-Apim-Subscription-Key={C.TRUSTED_CLIENT_TOKEN}")
C.WSS_URL = NEW; CM.WSS_URL = NEW
async def m():
    c = edge_tts.Communicate("语音测试", "zh-CN-XiaoxiaoNeural")
    await c.save("t.mp3")
asyncio.run(m())
EOF
ls -l t.mp3          # 必须 10~20KB；0 字节 = 仍失败（edge-tts 空文本也会写 0 字节文件，见上游 #487）
```

判定标准：**文件非 0 字节**才算通过。只看"没报错"不够（上游有"空文本退出码 0 但写 0 字节坏文件"的已知 bug）。

## 6. 两个坑（踩过）

1. **monkeypatch 必须改两处**。`communicate.py` 是 `from .constants import WSS_URL`，
   绑定发生在 import 时。只设 `edge_tts.constants.WSS_URL` **不生效** —— 报错 URL 里仍会出现
   `speech.platform.bing.com`，会误判成"新地址也不行"。要同时 `import edge_tts.communicate as CM; CM.WSS_URL = NEW`。
2. **补丁会被升级覆盖**。`pip install -U edge-tts` 会把 `constants.py` 换回上游版本 →
   403 复发。升级后必须重打；等上游发版合并 PR #491 后才能撤掉。

## 7. 与相邻问题的区分（别混）

- **不是** `local-web-capabilities` 那类"抓网页 403/反爬"—— 那是 HTTP 抓取层。
- **不是** `hermes-network-proxy` 里"旧 base_url 残留"—— 那个是主模型/视觉 provider 层的配置残留。
  本条是**第三方包硬编码的服务端地址**过期，本地没配置可改，只能改包常量或等发版。
- 若不想打补丁，替代路径 = 换 Hermes `tts.provider`（edge 是免费通道；换其他 provider 有成本）。**未实测，仅备选。**
