# 抖音视频抓取（CDP 方案 · 2026-09-21 实测全链跑通）

**什么时候用**：凡哥发来抖音链接要你学习／拉片，而 yt-dlp 拿不到。
**结论先行**：抖音不是"cookie 不够"，是**接口签名**问题——绕开的办法不是补 cookie，而是**借一个真浏览器会话，从网络层取带签名的 CDN 直链**。

---

## 为什么 yt-dlp 在抖音上走不通

| 尝试 | 实际报错 | 说明 |
|---|---|---|
| `web_extract <链接>` | `Failed to fetch url` | 页面正文 JS 渲染，抓不到静态文本——别在这上面耗时间 |
| `yt-dlp <精选页 URL>` | `Unsupported URL`（generic 兜底） | `douyin.com/jingxuan?modal_id=<id>` 是精选页形态，先换算成 `douyin.com/video/<id>` |
| `yt-dlp douyin.com/video/<id>` | `HTTP Error 403: Forbidden` → `Fresh cookies (not necessarily logged in) are needed` | 接口带 a_bogus / X-Bogus 签名 + ttwid |
| `--cookies-from-browser chrome` | `Could not copy Chrome cookie database` | Chrome 正在运行时 cookie 库被独占（Windows），关浏览器才能复制 |
| `--cookies-from-browser edge` | cookie 读到了，**仍 403** | 证明死结在签名，别继续在 cookie 上耗时间 |

---

## 全链（Windows + git-bash；路径一律 `C:/...` 形式给原生程序）

### 1. 起一个独立 Chrome 实例（带远程调试端口，不碰用户正在用的浏览器）

```bash
mkdir -p "$LOCALAPPDATA/Temp/vid/profile"
# terminal(background=true)：
"/c/Program Files/Google/Chrome/Application/chrome.exe" \
  --remote-debugging-port=9222 \
  --user-data-dir="C:/Users/<user>/AppData/Local/Temp/vid/profile" \
  --no-first-run --no-default-browser-check about:blank
```

健康检查（必须打印出 `Chrome/xxx` 才算起来了）：

```bash
curl -s http://localhost:9222/json/version
curl -s http://localhost:9222/json/list   # 拿 page 的 webSocketDebuggerUrl
```

> 不要用 `&` 后台化（会被拦），用 `terminal(background=true)`。任务完成后 kill 掉这个进程。

### 2. playwright `connect_over_cdp` 驱动它 + 记录网络

```python
import json
from playwright.sync_api import sync_playwright

url = "https://www.douyin.com/video/<id>"
with sync_playwright() as p:
    b = p.chromium.connect_over_cdp("http://localhost:9222")
    ctx = b.contexts[0]
    page = ctx.pages[0]
    reqs = []
    page.on("request", lambda r: reqs.append((r.method, r.resource_type, r.url)))
    page.goto(url, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(12000)          # 等 MSE 把音/视频分片请求发出来
    print("TITLE:", page.title())
    print(page.inner_text("body")[:3000])  # 简介 + 章节列表常在这里
    json.dump(reqs, open("network.json", "w", encoding="utf-8"), ensure_ascii=False)
```

`page.inner_text("body")` 往往已经给出**视频简介 + 章节时间轴**（"章节要点 00:30 冲突驱动型开场…"），先读它就能拿到分段结构，省一轮抽帧。

### 3. 从 network.json 里取媒体直链

找这两类（都是 `206` + `fetch`/`media`，域名 `v26-web.douyinvod.com`）：

- 视频：`.../media-video-avc1/?a=6383&br=482&...`
- 音频：`.../media-audio-und-mp4a/?a=6383&br=189&...`

**整条 URL（含 query 签名）原样使用，不要截断**。签名有时效（分钟级），抓到即刻下载。

**格式覆盖要全（2026-09-24 补）**：视频流有两种编码变体——`media-video-avc1`（H.264）与 **`media-video-hvc1`（H.265）**；音频为 `media-audio-und-mp4a`。**自家过滤脚本只匹配 avc1 时会漏掉 hvc1**（实测报 `video_url_ok: False` 而音频正常）→ 别放弃，从 network.json 手动正则提取即可：

```python
import json, re
d = json.load(open('network.json', encoding='utf-8'))   # 顶层是 list，元素形如 [200, "xhr", "url"]
s = json.dumps(d, ensure_ascii=False)
urls = re.findall(r'https?://[^"\\ ]+', s)
vid = next(u for u in urls if 'media-video' in u)   # avc1 / hvc1 都能命中
aud = next(u for u in urls if 'media-audio' in u)
# 再 curl -L 下载（URL 含完整签名参数，原样使用）
```

另：页面里 `<video>` 的 `src` 显示为 `blob:`（MSE 流式播放）属正常——直链不在 DOM 里，只在 network 记录里，不要去页面里找。

### 4. 下载 + 合流

```bash
curl -sSL -H "User-Agent: <页面同款 UA>" -H "Referer: https://www.douyin.com/" \
     -o dy_video.mp4 "<video_url>"
curl -sSL -H "User-Agent: <页面同款 UA>" -H "Referer: https://www.douyin.com/" \
     -o dy_audio.mp4 "<audio_url>"
ffmpeg -loglevel error -i dy_video.mp4 -i dy_audio.mp4 -c copy dy_full.mp4 -y
```

抖音的音轨和视频轨是**两个独立流**——只下 video 拿到的文件没有声音。

### 5. 之后照常走本 skill 主流程

ASR 转写（`Method A`）→ 抽帧 / 要点页 vision（`Method B`）。
本 skill 下 `scripts/mangju_asr.py`（漫剧拉片同款）输出段的字段是 **`{s, e, t}`**，不是 `{start, end, text}`；JSON 顶层为 `{file, dur, n_seg, segments}`。

**同音错字要当心**：口播转写会有同音误字（实测「冲突驱动型」→「一度驱动性」、「盗梦空间」→「逗梦空间」、「延迟揭示」→「延迟街市」）。这类教学视频常带中英双语硬字幕——**关键术语的写法用抽帧读字幕交叉校验**，别直接采信 ASR 的错字再转述给人。

### 6. 顺手挖作者/团队/元数据（2026-09-24 增补：拉片/调研一体）

抓视频时把"这个人是谁、数据多少"一起带走：

- **作者**：监听里的 `aweme/v1/web/aweme/detail/` 响应 → `aweme_detail.author`：`nickname` 昵称 / `unique_id` 抖音号 / `signature` 简介 / `follower_count` 粉丝 / `total_favorited` 获赞。页面文本还会带"作者声明：内容由 AI 生成"（接口对应 `risk_infos`）。
- **主页作品列表**：`douyin.com/user/<sec_uid>`（sec_uid 从视频页 `a[href*="/user/"]` 拿）→ 打开后 `mouse.wheel` 滚动 3–5 次 → `inner_text` 抓作品标题（含 `#` 的行）+ "共创"标记。
- **元数据速查表**（`aweme_detail` 常用字段）：

  | 字段 | 用途 |
  |---|---|
  | `mix_info` | 合集名 + `current_episode`/`updated_to_episode`（确认系列集数） |
  | `statistics` | digg / comment / collect / share（`play_count` 常为 0 不给） |
  | `risk_infos` | "内容由 AI 生成"声明 |
  | `suggest_words` | 观众搜索词（= 真实观众认知线索，如"XX短剧演员表"） |
  | `author.ip_location` | 属地（接口可能为 None，页面文本有） |

- **评论**：`aweme/v1/web/comment/list/` 响应里拿前几条（完整翻页需签名，别硬啃）。
- **已知边界**：搜索页（`/search/`）未登录弹扫码框，不能无登录搜站内；找到的线索用 web_search 到站外补。

---

## 抽帧与接触表（这次踩过的两个坑）

- **要点页要按段落口播时间点定位再去抽**：先转写拿时间戳，再在"公式/提示词讲到的那一秒"抽帧，比等间隔狂抽省一大半 vision 调用。本次 7 分钟视频只抽 5 张要点页就覆盖了五种开场。
- **多帧拼一张接触表**：

```bash
ffmpeg -loglevel error \
  -i f1.jpg -i f2.jpg -i f3.jpg -i f4.jpg \
  -filter_complex "[0][1][2][3]xstack=inputs=4:layout=0_0|w0_0|0_h0|w0_h0[o];[o]scale=1600:-1[o2]" \
  -map "[o2]" sheet.jpg -y
```

  **PITFALL**：`xstack` 和独立的 `-vf scale` 不能同时用，会报
  `Filtergraph 'scale=...' was specified for a stream fed from a complex filtergraph. Simple and complex filtering cannot be used together`。
  把 `scale` 写进**同一个** `filter_complex`（接在 xstack 后面，用 `[o]…[o2]` 链接）即可。

- **更省事的替代（2026-09-24）：`tile` 一步拼宫格**——连续帧/关键段直接出拼图，免 xstack：

```bash
ffmpeg -ss <起始秒> -i in.mp4 -t 3 -vf "fps=6,scale=480:-1,tile=6x3" -frames:v 1 sheet.jpg -y
```

- **场景切换统计（剪辑节奏）**：`scdet` 的阈值选项实测不触发，改用 select+showinfo：

```bash
ffmpeg -loglevel info -i in.mp4 -vf "select=gt(scene\,0.2),showinfo" -vsync 0 -f null - 2>&1 \
  | grep -o "pts_time:[0-9.]*" | sed 's/pts_time://'
```

  计数 = 镜头切换数；均值镜头时长 = 总时长 ÷ （切换数 + 1）。

---

## 已知局限（写清边界，别当成"抖音不能抓"）

- 无登录态也能拿到公开视频的音/视频流；仅登录可见的内容不在本方案覆盖内。
- 签名 URL 会过期，隔天再用同一份 network.json 会 403——重新走一遍步骤 2 取新链接。
- 本方案依赖 Chrome + playwright（同机都已具备）；换机器若有缺失，先装 playwright 再用。
