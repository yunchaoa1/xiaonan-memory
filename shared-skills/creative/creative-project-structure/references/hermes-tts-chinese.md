# Hermes TTS Chinese Voice Fix

## Problem
朗读 (read aloud) replies in English even after setting `tts.voice: zh-CN-XiaoxiaoNeural`.

## Root cause
Edge TTS reads its voice config from the **nested** path `tts.edge.voice`, NOT from the top-level `tts.voice`.

## Fix
```bash
hermes config set tts.edge.voice zh-CN-XiaoxiaoNeural
```

Not:
```bash
hermes config set tts.voice zh-CN-XiaoxiaoNeural   # ❌ ignored by Edge TTS
hermes config set voice.voice zh-CN-XiaoxiaoNeural  # ❌ wrong section
```

## Verification
```bash
grep -A3 "tts:" config.yaml
# Should show:
# tts:
#   provider: edge
#   edge:
#     voice: zh-CN-XiaoxiaoNeural
```

## Restart required
Hermes must be restarted after TTS config changes. `/reset` is NOT sufficient.

## Common Chinese Edge TTS voices
- `zh-CN-XiaoxiaoNeural` — 晓晓 (female, warm)
- `zh-CN-YunxiNeural` — 云希 (male)
- `zh-CN-XiaoyiNeural` — 晓伊 (female)
