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

## Pitfalls

1. **B站/Douyin blocking** — yt-dlp may fail with 412 or SSL errors. Don't spend too long fighting it — ask the user to download locally.
2. **Vision paths** — must use full absolute paths like `D:\SDkecheng\...`, not `/d/...` MSYS paths or relative paths.
3. **Frame rate** — `fps=1/N` means one frame every N seconds. For a 5-minute video, `fps=1/15` gives ~22 frames. For longer videos, increase N to avoid hundreds of frames.
4. **Don't read every frame** — read the first few to understand structure, then skip to frames at logical breakpoints (where steps change, where examples are shown).
