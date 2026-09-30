# -*- coding: utf-8 -*-
"""会议录音 → 中文转写（faster-whisper large-v3 · GPU · 本地不出网）

用法：改下面 CONFIG 的音频路径 → python transcribe_meeting.py
要点：
  · 逐段 flush 写 txt（可边跑边读，别等跑完）；同时输出结构化 json
  · initial_prompt＝人物/项目术语表 —— 中文会议准确率提升最大的一招
  · 实测基准：RTX 5080 Laptop 16G，73 分钟音频 ≈ 18 分钟（≈4× 实时），1871 段
前置：ffmpeg 先转 16k 单声道 wav（native 路径用 D:/... 正斜杠）
   ffmpeg -y -v error -i "会议.m4a" -ac 1 -ar 16000 -c:a pcm_s16le "D:/Hermes/cache/audio/meeting_16k.wav"
"""
import json, os, time

# ── CONFIG ──────────────────────────────────────────────────────────
WAV      = r"D:\Hermes\cache\audio\meeting_16k.wav"
MODEL    = r"D:\Hermes\models\faster-whisper-large-v3"   # 没下过见 SKILL.md §③（hf-mirror）
OUT_DIR  = r"D:\Documents\我的文档\会议记录"
OUT_TXT  = os.path.join(OUT_DIR, "会议_转写.txt")
OUT_JSON = os.path.join(OUT_DIR, "会议_转写.json")

# 术语表：人物 + 项目 + 工具名（写进 initial_prompt，显著压同音错字）
GLOSSARY = ("以下是我们技术部的项目会议记录。参会人：谢泽凡、何锦波、吴伟俊、李林、唐光辉。"
            "涉及项目与工具：OPC 数字社区平台、影剧工坊、Novin AI、智提分教育学习机、"
            "公司级 Agent、漫剧发布平台、浪浪椰 APP、台账、考核、归档、日报、"
            "ComfyUI、LangGraph、RAGFlow、DeepSeek、向量数据库。")
# ────────────────────────────────────────────────────────────────────

from faster_whisper import WhisperModel

assert os.path.exists(WAV), f"找不到音频：{WAV}（先用 ffmpeg 转 16k 单声道）"
os.makedirs(OUT_DIR, exist_ok=True)

t0 = time.time()
model = WhisperModel(MODEL, device="cuda", compute_type="float16")
segments, info = model.transcribe(
    WAV,
    language="zh",
    beam_size=5,
    vad_filter=True,
    vad_parameters=dict(min_silence_duration_ms=500),
    initial_prompt=GLOSSARY,
    condition_on_previous_text=False,   # 防上一段幻觉扩散
)
print(f"[开始] 音频 {info.duration/60:.1f} 分钟 → 输出 {OUT_TXT}", flush=True)

rows, n = [], 0
with open(OUT_TXT, "w", encoding="utf-8") as f:
    for s in segments:
        n += 1
        text = s.text.strip()
        f.write(f"[{s.start:8.1f}-{s.end:8.1f}] {text}\n")
        rows.append({"start": round(s.start, 2), "end": round(s.end, 2), "text": text})
        if n % 20 == 0:                     # 每 20 段 flush 一次 → 边跑边读
            f.flush()
            print(f"  … {n} 段 · {s.end/60:.0f} 分钟 / {info.duration/60:.0f} 分钟", flush=True)

with open(OUT_JSON, "w", encoding="utf-8") as f:
    json.dump({"duration": info.duration, "segments": rows}, f, ensure_ascii=False, indent=1)

print(f"[完成] 共 {n} 段 · 用时 {time.time()-t0:.0f}s · 输出 {OUT_TXT}", flush=True)
