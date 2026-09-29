---
name: video-analysis
description: Analyze video content by downloading, extracting keyframes with ffmpeg, and reading frames via vision — useful for learning from tutorials, reference footage, and AI video technique videos.（中文触发：分析视频内容（下载、ffmpeg抽关键帧、逐帧读取）时加载）
platforms: [windows, linux, macos]
---

# Video Analysis

Download a video, extract keyframes at regular intervals, and use vision analysis to read the content frame by frame. Designed for learning from tutorial/reference videos without needing to watch them manually.

## When to Use

- User shares a video link and wants you to learn its content
- User has a local video file and wants you to analyze it
- Tutorial/reference video for AI video production techniques

## Workflow

### Step 1: Get the video

**If the user provides a URL:**
```bash
# Install if needed
uv pip install yt-dlp

# Download
yt-dlp -o "/path/to/output/%(title)s.%(ext)s" "<video_url>"
```

**Pitfall:** B站 and some Chinese platforms may return 412/SSL errors. If yt-dlp fails, try `--force-ipv4` first. If still failing, the user may need to download the video themselves (e.g., via B站 app) and share the local file.

**If the link is a JS-rendered platform page (抖音 / 小红书 / 快手 / 微信视频号) — capture the media stream with Playwright instead of asking the user to download.** `web_extract` on a Douyin `/video/<id>` page returns only an obfuscated JS blob (`_$jsvmprt…`, no content), and the page's login modal dims any screenshot — but a real headless Chromium renders it fine with **no login and no cookies**:

```bash
python D:\Hermes\skills\media\video-analysis\scripts\douyin_video_fetch.py 7690214971057147177 D:/Hermes/cache/douyin
```

Runbook (same pattern works for other SPA platforms — swap the URL and the stream-host filter):
1. `playwright` chromium, `headless=True`, desktop UA, `locale="zh-CN"`; open `https://www.douyin.com/video/<id>`.
2. `page.on("response", …)` and keep URLs containing `media-video` / `media-audio` (host `*.douyinvod.com`). These arrive only once playback starts — call `document.querySelector('video')?.play()` to trigger them.
3. `page.title()` **and** `meta[name=description]` carry the real payload: the full caption text **plus the publisher and post date** (e.g. "… #韩束防脱洗发水（广告） - 央视网于20260928发布在抖音"). The publisher line is what tells you whose account actually posted it.
4. Download with the page's own context so the Referer/signature checks pass: `ctx.request.get(media_url, headers={"Referer": "https://www.douyin.com/"}).body()` → write bytes. Signed media URLs expire, so download immediately after capture.
5. Post time without any API: Douyin snowflake id's high 32 bits are Unix seconds — `datetime.fromtimestamp(vid >> 32)`, render in UTC+8.

### Step 2: Extract keyframes

Use ffmpeg to grab frames at regular intervals (e.g., every 15 seconds for a 5-minute video = ~22 frames):

```bash
mkdir -p "/path/to/frames"
ffmpeg -i "/path/to/video.mp4" -vf "fps=1/15" -q:v 2 "/path/to/frames/frame_%03d.jpg" -y
```

- `fps=1/15` = one frame every 15 seconds. Adjust for video length.
- `-q:v 2` = high quality JPEG output

### Step 3: Read frames

Use `vision_analyze` to read each frame. **Always use full Windows paths** (e.g., `D:\SDkecheng\...`) — relative or MSYS paths will fail.

Batch-read multiple frames at once to save turns. Focus on frames likely to contain key content (titles, step indicators, summary screens).

### Step 4: Compile knowledge

After reading all key frames, compile the extracted information into a structured document. Use the frame timestamps to reconstruct the video's logical structure (intro → steps → examples → summary).

## Reading on-screen text in a dense, text-heavy video (ad / 口播 / 科普)

For a short vertical video whose payload is *text* (burned-in 字幕, 大字宣传语, 免责小字), the goal is not keyframes but **complete text coverage** — read it in two passes:

1. **Pass 1 — coverage.** `fps=1` (one frame per second) to a `frames/` dir; nothing at 1 fps gets missed. Then build contact sheets so a single vision call covers many seconds: ffmpeg `-vf "fps=1/N,scale=576:-1,tile=2x3"`, or with PIL paste frames into a grid and **draw the second number in each cell** (`ImageDraw.text((x+8,y+8), f"{n}s", fill="red")`) so you can attribute every claim to a timestamp. Keep cells at the source frame's native width (e.g. 576) — 大字幕/旁白字幕 stay legible; shrinking cells to fit more of them destroys the text.
2. **Pass 2 — fine print.** Small text (免责声明, 注册证号, 报告编号, 数据来源) is *never* legible in a sheet. Crop the specific region from the single frame and upscale before reading: PIL `im.crop(box).resize((w*3, h*3), Image.LANCZOS)`. The片尾免责声明 and 瓶身小字 are usually the most decision-relevant text in the whole video — always read them, never summarize them away.

Quote what you read verbatim in your answer, with the timestamp. Keep `frames/` as the evidence artifact and report its absolute path.

## Audio track analysis (transcript / dialogue density)

For judging 节奏/dialogue density of 短剧·漫剧 (how much of the runtime is speech vs pure visuals), analyze the AUDIO, not frames:

1. Download audio only: `yt-dlp -f worstaudio -o "name.%(ext)s" "<url>"` (or `-f "30016+30216"` when you also want a low-res video strip for subtitle-shape checks).
2. Transcribe with faster-whisper (model `medium`, `device=cpu`, `compute_type=int8`; `vad_filter=True` → each returned segment is a speech window; gaps between segments = pure-visual/silent stretches).
3. Metrics: speech coverage = Σsegment duration / total duration; density = chars per minute; line frequency = segments per minute; sentence length = split segment text on 。！？.
4. Form check: ffmpeg `-vf "fps=1/14,scale=560:-1,tile=2x2"` → vision — one frame every ~14s as a 2x2 grid, read the subtitle text style (1st-person dialogue vs 3rd-person narration).

Benchmark numbers (红果爆款漫剧实测): 93.2% speech coverage, 177 chars/min, ~1 line per 3.2s. Runnable scripts live at `D:\Hermes\xiaonan-memory\scripts\` (mangju_asr.py / mangju_analyze.py).
（注：本文早前指向的 `references/competitor-drama-lapian.md` 文件已不存在，方法学数字以上面这句为准。）

**Pitfall:** native python does NOT translate MSYS paths — pass `D:/...` style paths to scripts (`/d/Hermes/...` becomes `D:\d\Hermes\...`).

## Pitfalls

1. **B站/Douyin blocking** — search/listing endpoints may return 412, but direct downloads of public single videos (by av/BV id) usually work **without cookies or proxy**: use `--no-check-certificates`, and `--force-ipv4` if SSL issues persist. Only after direct download also fails, ask the user to download locally. (Verified 2026-09: B站 direct download of public 短剧/漫剧 audio+video OK.)
2. **Vision paths** — must use full absolute paths like `D:\SDkecheng\...`, not `/d/...` MSYS paths or relative paths.
3. **Frame rate** — `fps=1/N` means one frame every N seconds. For a 5-minute video, `fps=1/15` gives ~22 frames. For longer videos, increase N to avoid hundreds of frames.
4. **Don't read every frame** — read the first few to understand structure, then skip to frames at logical breakpoints (where steps change, where examples are shown).
5. **Use the SYSTEM ffmpeg, not Playwright's bundled one.** Playwright ships a stripped `ms-playwright/ffmpeg-*/ffmpeg-win64.exe` that rejects a perfectly valid captured mp4 with `Invalid data found when processing input`. On this machine the working binary is `D:/tools/ffmpeg/ffmpeg.exe` (check `command -v ffmpeg` → `/d/tools/ffmpeg/ffmpeg`, then pass it the native `D:/…` form). Verify a download is real media before blaming the tool: read the first bytes — a valid mp4 starts with `…ftypisom…moov`.
6. **A "captured" stream can be a valid file that ffmpeg still can't open in a *different* build** — when probing fails, re-probe with a second binary rather than re-downloading; the capture is rarely the problem.
