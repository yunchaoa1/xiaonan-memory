# Cangjie Skill Pipeline · 苍捷蒸馏工作流

> Source: `kangarooking/cangjie-skill` (1881⭐ MIT license)
> Verified: 2026-07-07 via actual video distillation test

## What It Does

Takes long-form content (books, videos, podcasts, courses) and distills extractable methodology into Agent-callable SKILL.md files. Not summarization — structured methodology extraction.

## Local Toolchain (Verified)

```
Local mp4 → ffmpeg (audio extract) → whisper (STT) → cangjie-skill (distill) → SKILL.md
```

### Step 1: Extract Audio
```bash
ffmpeg -i input.mp4 -vn -acodec pcm_s16le -ar 16000 -ac 1 output.wav -y
```

### Step 2: Transcribe
```bash
uv pip install openai-whisper  # one-time
python -c "
import whisper
model = whisper.load_model('medium')  # medium for Chinese, small/tiny for English
result = model.transcribe('output.wav', language='zh')
print(result['text'])
"
```
- CPU only (FP32), ~2-3x realtime for medium model
- 41MB mp4 → 6MB WAV → transcript in ~60s

### Step 3: Distill via Cangjie RIA-TV++
Feed transcript text to cangjie-skill's 7-stage pipeline:
1. Adler analysis → BOOK_OVERVIEW.md
2. Parallel extraction (frameworks/principles/cases/counterexamples/terminology)
3. Triple verification (cross-domain evidence ×2, predictive power, uniqueness)
4. RIA++ construction (R=quote, I=restate, A1=case, A2=trigger, E=execution, B=boundaries)
5. Zettelkasten linking → INDEX.md + dependency graph
6. Stress testing (decoy questions + cross-skill confusion tests)
7. Delivery → SKILL.md + DIGEST.md + GLOSSARY.md

## Verified Results (from video author's tests)

| Source | Duration | Skills Output | Time |
|--------|----------|:---:|------|
| Andrew Ng AI Course | 26 videos, 4h+ | 25 skills | ~1 hour |
| YouTube Loom Engineering | 4 videos, 80min | 8 skills | — |

## Known Limitations

- Chinese transcription quality: whisper medium model works but has errors with accented speech. Review transcript before distillation.
- Video-downloader companion tool only supports YouTube/Bilibili links, not local files. Use our own ffmpeg+whisper pipeline for local files.
- Output SKILL.md format may need manual frontmatter adjustment for Hermes compatibility.
- Best for METHODOLOGY content (frameworks, steps, criteria). Not suitable for narrative/emotional content.
