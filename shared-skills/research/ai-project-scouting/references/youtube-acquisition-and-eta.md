# YouTube 取料通路 + 转写 ETA 纪律（2026-10-29 实测）

> 抖音那套在 `content-ingestion`（用户自有技能）。这里只记 **YouTube 专属**的通路和等待纪律。

## 一、YouTube 取料三段（本机实测可用）

```bash
YT="https://www.youtube.com/watch?v=<id>"
PROXY="http://127.0.0.1:7897"          # 本机 Clash 端口；不加 --proxy 直连会超时
YTDLP="D:/Hermes/hermes-agent/venv/Scripts/yt-dlp"

# ⓪ 判这个号靠不靠谱（最省：不下载、不转写，只拉标题）
"$YTDLP" --proxy "$PROXY" --flat-playlist --print "%(title)s" \
  "https://www.youtube.com/@<channel>/videos" | head -30

# ① 先试字幕（有字幕就别折腾音频）
"$YTDLP" --proxy "$PROXY" --skip-download --write-auto-sub --write-sub \
  --sub-lang "zh-Hans,zh-Hant,zh-TW,zh,en" --convert-subs srt -o "yt_%(id)s" "$YT"
#   实测：不少中文频道没开字幕 → "There are no subtitles for the requested languages"

# ② 没字幕 → 只下音轨（28 分钟约 23MB，比下视频快得多）
"$YTDLP" --proxy "$PROXY" -f "bestaudio" -o "ytgain.%(ext)s" "$YT"
ffmpeg -y -loglevel error -i ytgain.webm -ar 16000 -ac 1 ytgain.wav
"D:/Hermes/hermes-agent/venv/Scripts/python.exe" transcribe_file.py ytgain.wav out.zh.txt

# ③ 要抽帧看画面 → 用 360p（-f 134），别用 worst
"$YTDLP" --proxy "$PROXY" -f 134 -o "ytvid.%(ext)s" "$YT"
ffmpeg -y -loglevel error -i ytvid.mp4 -vf "fps=16/<总秒数>,scale=440:-1,tile=4x4" \
  -frames:v 1 "sheet.jpg"
```

**踩过的坑**：
- `-f "worst[height<=480]/worst"` 可能报 `Requested format is not available` → 先 `--list-formats`，直接用具体 ID（360p = `134`）
- `WARNING: No supported JavaScript runtime` 可忽略，字幕/音频下载不受影响
- 抖音的 `dy_transcribe.py` **不适用 YouTube**；YouTube 走 yt-dlp 这条

## 二、转写 ETA 纪律（凡哥会问「还需要多久？」）

**速度参照（本机 CPU int8 / medium，实测两次）**：≈ **0.85 倍实时**
- 15 分钟音频 → 约 12 分钟
- 28 分钟音频 → 约 24 分钟

**规则**：

1. **开口就把 ETA 说出去**（"这段 28 分钟，大概 20-25 分钟出字"），别等他问
2. 他问了 → **给准确剩余时间**（已跑多久 + 总估 + 依据），不要说"还要一会"
3. **主动给替代**：「要不要我先把已经确定的讲给你？」／「可以改成边转边写，10 分钟先给前半段」
4. 长音频**优先边转边写**（faster-whisper 是 generator，逐段落盘），别最后一次性写文件 —— 本次 28 分钟音频因为最后才写盘，中途无法给部分结果
5. **等待期间别干等**：并行做抽帧 / 拉频道标题 / 查项目真身；`notify=true` 会通知，**别反复 poll**
6. 转写完**先读全文再下结论**（550～880 段这种长度，只看末段会误判主题）

## 三、GPU 加速（未实测，先别承诺）

- 本机：RTX 5080 **Laptop** / 16G 显存 / 驱动 596.36 / CUDA 13.2
- 但当前 venv 的 torch 是 **`2.12.1+cpu`，`CUDA 可用: False`**
- 要提速必须**另建独立 venv** 装 CUDA 版（CUDA torch 好几个 G，**别污染 Hermes venv**）。理论可快 20 倍量级（28 分钟音频 → 1-2 分钟）
- ⚠ 5080 是 Blackwell 新架构，加速库可能不认 → **未跑通前只能跟凡哥说"要试，可能得挑版本"，不许承诺"显卡能跑"**
