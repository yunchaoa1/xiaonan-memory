# -*- coding: utf-8 -*-
r"""把一批 mp4 转成中文文稿（本地 faster-whisper large-v3，GPU）

用法:
  python transcribe_mp4s.py <目录或mp4...>

输出: 每个 mp4 同名 .txt（带时间戳）和 .json（分段）

来源说明：改写自 2026-10-20 在 RTX 5080 上实际跑通的脚本（xhs_transcribe.py），
逻辑一致（ffmpeg 用 subprocess 传列表、large-v3、language=zh、vad_filter），
但这份抄本没有单独再跑一遍 —— 首次用请先拿一个短文件试。

依赖: D:\Hermes\hermes-agent\venv（faster-whisper 1.2.1）、D:\tools\ffmpeg\ffmpeg.exe
模型: D:\Hermes\models\faster-whisper-large-v3（2026-10-20 实测加载 2.9s，≈2.2× 实时）
"""
import glob
import json
import os
import subprocess
import sys
import time

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

FFMPEG = r"D:\tools\ffmpeg\ffmpeg.exe"
MODEL_DIR = r"D:\Hermes\models\faster-whisper-large-v3"

# 领域术语塞进 initial_prompt，能明显压住同音错词
DOMAIN_HINT = "以下是中文口播，涉及穿搭术语：正肩、落肩、版型、克重、珠地棉、微胖、阔腿裤、工装裤、配色。"


def collect(args):
    out = []
    for a in args:
        if os.path.isdir(a):
            out += sorted(glob.glob(os.path.join(a, "*.mp4")))
        elif os.path.isfile(a):
            out.append(a)
    return out


def to_wav(mp4):
    wav = os.path.splitext(mp4)[0] + "_16k.wav"
    if os.path.exists(wav):
        return wav
    # ⚠️ 必须 subprocess.run + 列表参数：os.system 带引号的 Windows 路径会报
    #    "filename, directory name, or volume label syntax is incorrect"
    r = subprocess.run(
        [FFMPEG, "-y", "-v", "error", "-i", mp4, "-vn",
         "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", wav],
        capture_output=True, text=True)
    if r.returncode != 0 or not os.path.exists(wav):
        print("[失败] 转音频", mp4, "|", (r.stderr or "")[:200])
        return None
    return wav


def main():
    files = collect(sys.argv[1:])
    if not files:
        print("没找到 mp4")
        return
    print("[任务] %d 个文件" % len(files))

    from faster_whisper import WhisperModel
    print("[加载模型]", MODEL_DIR)
    t0 = time.time()
    model = WhisperModel(MODEL_DIR, device="cuda", compute_type="float16")
    print("[模型就绪] %.1fs" % (time.time() - t0))

    for mp4 in files:
        base = os.path.splitext(mp4)[0]
        if os.path.exists(base + ".txt"):
            print("[跳过]", os.path.basename(mp4), "(已有稿)")
            continue
        wav = to_wav(mp4)
        if not wav:
            continue
        t = time.time()
        segs, info = model.transcribe(
            wav, language="zh", beam_size=5, vad_filter=True,
            initial_prompt=DOMAIN_HINT)
        rows = [{"start": round(s.start, 1), "end": round(s.end, 1), "text": s.text.strip()}
                for s in segs]
        with open(base + ".txt", "w", encoding="utf-8") as f:
            for r in rows:
                f.write("[%05.1f-%05.1f] %s\n" % (r["start"], r["end"], r["text"]))
        with open(base + ".json", "w", encoding="utf-8") as f:
            json.dump({"audio": info.duration, "segments": rows}, f,
                      ensure_ascii=False, indent=1)
        print("[完成] %s | %ds 音频 | %d 段 | 耗时 %.1fs"
              % (os.path.basename(mp4), int(info.duration), len(rows), time.time() - t))

    print("\nALL DONE")


if __name__ == "__main__":
    main()
