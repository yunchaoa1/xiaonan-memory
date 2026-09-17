# AI Video Tools & Prompt Conventions

## LTX 2.3 Multi-Reference Video Generation
- **Skill**: `ltx-video-prompt` (loads automatically on trigger words "多图参考生视频" / "LTX视频提示词")
- **Prompt storage**: `D:\Hermes\xiaonan-memory\prompts\` directory
  - Naming: `角色名_场景_内容.md` — searchable by character, scene, or date
  - Example: `齐白兰_卧室自拍_面试练习生.md`
- **Key rules**: All English description, Chinese dialogue inline, no subtitle/text/caption words, face shape from reference images via vision_analyze only

## ACE Studio
- Official: https://acestudio.ai (JS-rendered, Hermes browser can't access, user can)
- Used for: Voice Cloning, Voice Changer, Video Composer (BGM + sound effects)
- When debugging: user may need to share screenshots of documentation pages

## Cangjie Skill (苍捷Skill)
- GitHub: https://github.com/kangarooking/cangjie-skill (1881⭐, MIT)
- Distills videos/books/podcasts into executable Agent Skills
- Workflow: video → ffmpeg audio → Whisper transcription → Cangjie → SKILL.md
- See: `video-learning` skill references
