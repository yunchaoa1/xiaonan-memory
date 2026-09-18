# -*- coding: utf-8 -*-
"""漫剧拉片 ASR：faster-whisper medium(int8/CPU) 转写 + VAD 分段。
输出每样本的 segments（带时间戳）→ JSON，供台词密度/静默段占比分析。
"""
import json, sys, time
from faster_whisper import WhisperModel

files = sys.argv[1:]
print(f"[init] loading medium int8 cpu_threads=20 ...", flush=True)
model = WhisperModel("medium", device="cpu", compute_type="int8", cpu_threads=20)
print("[init] ok", flush=True)

for f in files:
    t0 = time.time()
    try:
        segs, info = model.transcribe(
            f, language="zh", beam_size=5,
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=250, speech_pad_ms=100),
        )
        out = [{"s": round(s.start, 2), "e": round(s.end, 2), "t": s.text.strip()} for s in segs]
        rec = {"file": f, "dur": round(info.duration, 2), "n_seg": len(out), "segments": out}
        with open(f + ".asr.json", "w", encoding="utf-8") as fh:
            json.dump(rec, fh, ensure_ascii=False, indent=1)
        speech = sum(o["e"] - o["s"] for o in out)
        print(f"[done] {f} dur={info.duration:.0f}s segs={len(out)} "
              f"speech={speech:.0f}s ({speech/info.duration*100:.1f}%) "
              f"took={time.time()-t0:.0f}s", flush=True)
    except Exception as e:
        print(f"[FAIL] {f}: {e}", flush=True)
