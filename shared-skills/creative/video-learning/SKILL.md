---
name: video-learning
description: Learn from video content — download, extract frames, analyze visually, synthesize into documentation. Use when the user shares a video link or asks you to study a video for pipeline/knowledge integration.（中文触发：从视频学习内容（下载、抽帧、分析、总结）时加载）
platforms: [windows]
---

# Video Learning Workflow

Use this skill when the user wants you to learn from a video (tutorial, lecture, demo) and integrate the knowledge into existing pipelines or documentation.

## Trigger conditions

- User shares a Douyin/Bilibili/YouTube link and asks you to study it
- User downloads a video for you to learn from
- User mentions "学习这个视频" / "看这个视频" / "固化到管线"

## Workflow (ordered)

### 1. DOWNLOAD (if not provided as local file)

**PITFALL: Do NOT blindly try random CLI tools.** Search first or ask the user what tool they prefer.

- Preferred: IDM (Internet Download Manager) — browser extension, one-click
- CLI fallback: `yt-dlp` if installed
- **B站 412 先升级 yt-dlp，别急着换工具**（2026-09-09 实测）：旧版 yt-dlp（2026.6.9）抓 B 站报 `HTTP Error 412: Precondition Failed`，`uv pip install -U yt-dlp` 到 2026.8.19+ 即直接下载成功（官方已修 B 站 412）。cookie 导出（`--cookies-from-browser edge/chrome`）在浏览器运行时锁库会失败，是绕路不是正解。
- **PITFALL (Windows/MSYS 路径坑，2026-09-09 实测)**：yt-dlp 是 Windows 原生程序，`-o "/d/数字资产/..."` 这类 MSYS 路径会被当成相对路径解析（`\d\...`）→ 文件写错位到 `C:\d\...`。给原生程序传路径一律用 `C:/...` 形式，或先 `cd` 到目标目录再用相对文件名。
- B站-specific: `bilix` may work when yt-dlp is blocked
- **IF multiple tools fail**: suggest the user install IDM (internetdownloadmanager.com) or download via app → transfer to PC
- **PITFALL: Do NOT spend excessive time on download attempts.** If 2-3 tools fail, report the blocker and suggest alternatives.

Save to: `D:\SDkecheng\小南学习课堂\` or user-specified path.

### 2. EXTRACT FRAMES

Use ffmpeg to extract frames at regular intervals:

```bash
mkdir -p "<output_dir>/frames"
ffmpeg -i "<video_path>" -vf "fps=1/15" -q:v 2 "<output_dir>/frames/frame_%03d.jpg" -y
```

- `fps=1/15` = one frame every 15 seconds. **按视频长度调密度**（2026-09-11 实测）：
  | 视频长度 | 采样密度 | 说明 |
  |---|---|---|
  | ≤ 2 分钟（短视频/竖屏教程） | **`fps=1/1.8`**（≈1.8 秒/帧） | 默认 1/15 只会出 3–4 帧，**整段过程全部漏掉**。51 秒的视频用 1.8s/帧 出 28 帧刚好覆盖全过程 |
  | 2–15 分钟 | `fps=1/5` ~ `fps=1/8` | 步骤型教程 |
  | > 15 分钟 | `fps=1/15` ~ `fps=1/30` | 讲座/长课，靠转写兜底 |
- Use Windows absolute paths for vision_analyze compatibility

**⚠️ 短教程必须"画面 + 口播"一起读，缺一必漏**：本例 51 秒视频里，**方法只在口播里**（"减去一笔 → 这就是特斯拉的 logo"），**成品形态只在画面里**（方框内建筑式图形 + 锁标 + 发光字实景）。只转写会不知道长什么样，只看帧会不知道思路。两个都要。

### 3. ANALYZE CONTENT (choose method)

**Method A: Audio Transcription (PREFERRED for tutorials/lectures)**
For videos where the primary content is spoken — tutorials, lectures, courses — extract audio and transcribe:

```bash
# Step 1: Extract audio to WAV
ffmpeg -i "<video>" -vn -acodec pcm_s16le -ar 16000 -ac 1 "temp_audio.wav" -y

# Step 2: Install faster-whisper (2026-09-09 实测推荐：比 openai-whisper 快数倍，CPU int8 medium 转中文 15.8 分钟视频 ≈12 分钟)
uv pip install faster-whisper

# Step 3: Transcribe (medium for Chinese; 模型从 HF 下载——直连被墙就加 HF_ENDPOINT 走国内镜像 hf-mirror.com)
export HF_ENDPOINT=https://hf-mirror.com
python -c "
from faster_whisper import WhisperModel
model = WhisperModel('medium', device='cpu', compute_type='int8')
segments, info = model.transcribe('temp_audio.wav', language='zh', vad_filter=True)
for s in segments:
    print(f'[{s.start:.1f}-{s.end:.1f}]', s.text)
"
```

- **模型下载被墙**：`huggingface_hub` 读 `HF_ENDPOINT=https://hf-mirror.com` 环境变量（国内镜像，直连可用）——whisper 等一切 HF 模型同理。
- **不要浪费时间抓 B 站字幕接口**：UP 无 CC 字幕时 `x/player/v2` 返回 `subtitle 数为 0`；音频转写是完整内容的正解。
- 转写结果要带时间戳分段（`[s.start-s.end]`），便于对齐帧号定位关键画面。

**Method B: Frame Analysis (fallback for visual-heavy content)**
Use when the video is primarily visual (UI demos, ComfyUI workflows, drawing tutorials).

**PITFALL: Do NOT try to extract subtitles/transcripts from Chinese video platforms.** B站 API is frequently blocked, and subtitle extraction rarely works. Use vision_analyze on extracted frames instead.

- Load key frames with `vision_analyze` using **full Windows paths** (e.g., `D:\SDkecheng\...\frame_001.jpg`)
- Ask for "完整文字" (complete text) on each frame
- Batch multiple frames in parallel (up to 6 per turn)
- Focus on frames likely to contain key content (title slides, step overviews, examples, tool interfaces)

**Note:** `vision_analyze` needs absolute Windows paths (`D:\...`), NOT MSYS paths (`/d/...`).

### 4. SYNTHESIZE

- Identify structure: problem → steps → examples → summary
- Extract actionable rules, checklists, templates
- Map to existing pipeline stages

### 5. DOCUMENT & UPDATE

- Write structured documentation to the appropriate pipeline directory
- Update DASHBOARD.md to reflect completion
- Update memory log for the day

## Common pitfalls

1. **"瞎猜脑补" trap**: When a tool fails, search for alternatives rather than guessing. The user values efficiency over exhaustive exploration.
2. **Subtitle tunnel vision**: Don't waste time trying to extract CC/subtitles. Vision_analyze on frames is more reliable.
3. **Path formats**: vision_analyze requires Windows absolute paths. MSYS `/d/...` paths will fail with "Invalid image source".
4. **B站 anti-bot**: B站 frequently blocks CLI downloaders and API calls. Browser-based IDM is more reliable.
