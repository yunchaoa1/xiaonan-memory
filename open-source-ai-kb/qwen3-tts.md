# Qwen3 TTS — 语音克隆

## ① 能帮我做什么
- 用几秒参考音频克隆任意角色的声音
- 支持中文、英文等多语言
- 通过 VoiceClone 模式保持角色声音一致性

## ② 怎么用
**工作流节点**：
- Qwen3Loader → Qwen3VoiceClone → PreviewAudio
- 参考音频加载：VHS_LoadAudioUpload

**核心参数**：
- 模型：Qwen/Qwen3-TTS-12Hz-1.7B-Base（VoiceClone 用 Base，不用 CustomVoice！）
- 来源：ModelScope（HuggingFace 国内可能慢）
- 精度：bf16
- max_new_tokens：长文本设 4096，短文本 2048
- ref_audio_max_seconds：默认 30 秒足够

**关键规则**：
- ⚠️ ref_text 必须精确匹配参考音频的实际内容——不匹配 = 23秒噪音！
- ✅ 先用 Whisper 转录参考音频，确认 ref_text 后再传参
- seed 影响发音细节，不满意换 seed 重出（42→123→2222→...）

**输出处理**：
- ComfyUI 生成 FLAC（24000Hz），需转 MP3
- ffmpeg: `ffmpeg -i input.flac -ar 44100 -b:a 192k output.mp3`

## ③ 提示词技巧

**末尾防截断公式**：
疑问句末尾加「呢」+「谢谢」→ 防止吞掉最后一个字，多出约 0.8 秒可裁剪

例：
- 原：普通人能不能负担得起？
- 改：普通人能不能负担得起呢？谢谢

**语调调优**：
- VoiceClone 语调偏冷/高冷时，换 seed 效果有限
- 根源在参考音频本身——换个更自然的参考音频比调 seed 有效
- 周教授参考音频：vfinal_seg2_00001_.flac（打招呼语气自然）
