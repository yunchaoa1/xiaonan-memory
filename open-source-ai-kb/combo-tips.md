# AI 组合使用技巧

## Qwen 2511 Edit → LTX-Video 完整管线
当前访谈视频的标准流程：
1. Qwen 2511 Edit 出首帧图（给 LTX 做起始帧）
2. Qwen3 TTS 出音频（给 LTX 做口型驱动）
3. LTX Director 用首帧+音频生成视频
4. ffmpeg 合并多段视频

关键衔接点：
- 首帧图分辨率 928×1664，LTX 输入 736×1280，LTX 会自动适配
- 音频用 pcm_s16le 格式合并，加 1 秒静音间隙防止爆音
- 帧首尾衔接原则：帧 N 尾帧 ≈ 帧 N+1 首帧

## 其他已验证组合
- ffmpeg 合并 FLAC 片段 → -c:a pcm_s16le（不能用 -c copy）
- ComfyUI 输出 FLAC（24000Hz）→ ffmpeg 转 MP3（44100Hz/192kbps）才能被某些节点兼容
