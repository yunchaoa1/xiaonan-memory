# YouTube 无字幕链路 · 完整实录（2026-10-27）

## 背景

凡哥丢来 `https://www.youtube.com/watch?v=-Go9VATddKE`（28 分钟 / 8.4 万播放）。
作者没开字幕 → 只能下音频转写。以下是**实测走通的完整命令链**，照抄可用。

---

## 一、环境

| 项 | 值 |
|---|---|
| yt-dlp | `D:/Hermes/hermes-agent/venv/Scripts/yt-dlp`（2026.08.19） |
| 代理 | `http://127.0.0.1:7897`（Clash 默认端口，`netstat -ano \| grep :7897` 确认） |
| 转写 | faster-whisper **medium**（本地完整 1.5G，`HF_HUB_OFFLINE=1`） |
| ffmpeg | 在 PATH |

⚠ `large-v3` 在本机是空壳缓存（1KB 空目录），**别用**。

---

## 二、四步命令

### ① 先试字幕（省时间的首选）

```bash
cd /d/Hermes/cache
YT="D:/Hermes/hermes-agent/venv/Scripts/yt-dlp"
$YT --proxy "http://127.0.0.1:7897" --skip-download --write-auto-sub --write-sub \
    --sub-lang "zh-Hans,zh-Hant,zh-TW,zh,en" --convert-subs srt -o "yt_%(id)s" "<URL>"
```

**本次结果**：`There are no subtitles for the requested languages` → 作者没开，走 ②

**忽略的警告**：
```
WARNING: [youtube] No supported JavaScript runtime could be found.
```
不影响下载，别去装 deno。

### ② 元信息（先判断值不值得转）

```bash
$YT --proxy "..." --skip-download --print "%(title)s|%(duration)s|%(uploader)s|%(view_count)s" "<URL>"
```

本次输出：
```
1個人+AI，每天4小時，輕鬆年入100萬，AI賺錢新思路...|1694|小船|84029
```
→ 1694 秒 = 28 分钟，值得转但必须后台跑。

### ③ 下音频 → 转写

```bash
$YT --proxy "..." -f "bestaudio" -o "ytgain.%(ext)s" "<URL>"
# → ytgain.webm 23.84 MiB（28 分钟）
ffmpeg -y -loglevel error -i ytgain.webm -ar 16000 -ac 1 ytgain.wav
# → 54,195,452 字节
python transcribe_file.py ytgain.wav ytgain.zh.txt
```

**务必 `background=true` + `notify=true`** —— 实测 2.5 分钟时还在跑，预计 20~30 分钟。

### ④ 下 360p 抽帧看画面（同时进行）

```bash
$YT --proxy "..." -f 134 -o "ytvid.%(ext)s" "<URL>"
# → ytvid.mp4 33.6 MiB (640x360)
ffmpeg -y -loglevel error -i ytvid.mp4 -vf "fps=16/1694,scale=440:-1,tile=4x4" -frames:v 1 "yt_sheet.jpg"
```

**坑**：`-f "worst[height<=480]/worst"` 报 `Requested format is not available`。
正解：`--list-formats` 看真实 ID —— 本次 360p mp4 = **134**。

---

## 三、transcribe_file.py（content-ingestion 没有这份时的备用）

`content-ingestion` 属于凡哥自有技能，自动流程改不动。若那边没有该脚本，把下面内容存成任意本地文件直接用。

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""通用本地音视频转写（faster-whisper medium）"""
import os, sys

os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("OMP_NUM_THREADS", "8")

from faster_whisper import WhisperModel

src = sys.argv[1]
out = sys.argv[2] if len(sys.argv) > 2 else os.path.splitext(src)[0] + ".zh.txt"

model = WhisperModel("medium", device="cpu", compute_type="int8")
segments, info = model.transcribe(src, language="zh", beam_size=5, vad_filter=True)

lines = [f"[{s.start:7.1f}s] {s.text.strip()}" for s in segments if s.text.strip()]
with open(out, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print(f"OK {len(lines)} 段 -> {out}")
```

**输出格式**：`[  765.8s] 對這這麼多年自媒體是關鍵` —— 带时间戳，回跳核对原片用。

---

## 四、抽帧首轮就读出的字幕线索（本次实例）

16 帧概览直接读到的关键句（省了大半转写等待）：

- 「只是有一個人來幫你」
- 「你有沒有發現這個故事」
- 「我之前的這個創業的項目」
- 「所以他就在想」
- 「他開始找設備了」
- 「也就是說有 **100 個新用戶試用**」
- 「他從哪來的一個可能」
- 「其實就是…（經驗）」
- 「才有可能變出一個所以然」
- 「你**首先要去做醫生**」
- 「**5000 美金的市調**」
- 「只是他們需要**一個確定**」
- 「你要什麼去跟他們談、利用它來打造你的…」

→ 结论：他讲的是**「先小成本验证需求再做产品」**（100 用户试用 / 5000 美金市调），是正经创业方法，不是纯忽悠。
**所以"抽帧先看 16 格"这一步，能在转写出稿前 20 分钟就定下内容方向。**

---

## 五、连带踩到的坑

| 问题 | 解法 |
|---|---|
| GitHub releases 下载连不通（`objects.githubusercontent.com` 被墙），但 `api.github.com` 通 | 用镜像前缀：`https://ghfast.top/<原 github.com URL>`（2026-10-27 实测 2.5MB APK 下载成功，SHA256 与官方一致）。备选 `ghproxy.net` / `gh-proxy.com` |
| 抖音长视频（>10 分钟）下下来没声音 | 见 `content-ingestion` 的 `dy_grab_audio.py` 与 SKILL.md 坑 ⑦：Camoufox 截 `media-audio-und-mp4a` 请求 |
| yt-dlp 抓抖音 403 | 导浏览器 cookie 也无效（抖音要它自家反爬标记）→ 抖音一律走 Camoufox 路线，别在 yt-dlp 上耗 |
