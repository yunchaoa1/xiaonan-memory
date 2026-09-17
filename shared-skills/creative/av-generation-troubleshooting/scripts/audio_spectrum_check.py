#!/usr/bin/env python
"""Audio spectrum diagnosis for generated videos (hum vs human voice check).

Usage:
    python audio_spectrum_check.py video1.mp4 [video2.mp4 ...]

For each input: extracts audio via ffmpeg, then reports per-file and per-5s-window
band energy (low/mid/voice/high) + dominant frequency peak.

Judgement rules:
  - HUM: speechless segments also carry >60% energy below 500 Hz AND voice band
    (0.5-6 kHz) is ~0 -> constant low-frequency hum (e.g. VAE bug artifacts).
  - NORMAL: speechless segments carry energy in mid band (sobs/water/cloth);
    dialogue segments' low-frequency share is the voice fundamental
    (female 165-255 Hz, male 85-180 Hz) and is NOT hum.

Requires: ffmpeg on PATH, numpy, wave (stdlib).
"""
import subprocess
import sys
import tempfile
import wave
from pathlib import Path

import numpy as np


def extract_audio(video: str, wav_path: str) -> bool:
    r = subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-i", video, "-vn", "-acodec", "pcm_s16le", wav_path],
        capture_output=True, text=True,
    )
    return r.returncode == 0 and Path(wav_path).exists()


def analyze(wav_path: str, window_s: int = 5) -> dict:
    with wave.open(wav_path) as w:
        sr = w.getframerate()
        ch = w.getnchannels()
        n = w.getnframes()
        raw = w.readframes(n)
    a = np.frombuffer(raw, dtype=np.int16).reshape(-1, ch).mean(axis=1) / 32768.0
    if len(a) < sr:
        return {"error": "audio too short"}
    f = np.fft.rfftfreq(len(a), 1 / sr)
    spec = np.abs(np.fft.rfft(a)) ** 2
    tot = spec.sum() + 1e-12
    bands = {
        "low<200Hz": float(spec[f < 200].sum() / tot),
        "200-500Hz": float(spec[(f >= 200) & (f < 500)].sum() / tot),
        "voice0.5-6k": float(spec[(f >= 500) & (f < 6000)].sum() / tot),
        "high>6k": float(spec[f >= 6000].sum() / tot),
    }
    peaks = []
    for t in range(0, max(1, len(a) // sr - window_s + 1), window_s):
        seg = a[t * sr:(t + window_s) * sr]
        if len(seg) < sr:
            break
        fs = np.fft.rfftfreq(len(seg), 1 / sr)
        ss = np.abs(np.fft.rfft(seg)) ** 2
        peaks.append(int(fs[np.argmax(ss)]))
    return {"dur_s": round(len(a) / sr, 1), "rms": float(np.sqrt((a ** 2).mean())), "bands": bands, "peaks_hz": peaks}


def verdict(bands: dict) -> str:
    lo = bands["low<200Hz"] + bands["200-500Hz"]
    vc = bands["voice0.5-6k"]
    if lo > 0.8 and vc < 0.1:
        return "HUM (constant low-frequency, almost no voice band)"
    if lo > 0.6 and vc < 0.1:
        return "suspected hum (check per-window peaks on speechless segments)"
    return "looks normal (low share may be voice fundamental; check peaks)"


def main(argv):
    if not argv:
        print(__doc__)
        return 1
    tmp = Path(tempfile.mkdtemp())
    for i, video in enumerate(argv):
        wav = tmp / f"seg{i}.wav"
        if not extract_audio(video, str(wav)):
            print(f"[{video}] audio extraction FAILED")
            continue
        res = analyze(str(wav))
        if "error" in res:
            print(f"[{video}] {res['error']}")
            continue
        b = res["bands"]
        print(f"[{video}] dur={res['dur_s']}s rms={res['rms']:.3f}")
        print(f"  bands: <200Hz {b['low<200Hz']*100:.1f}% | 200-500Hz {b['200-500Hz']*100:.1f}% | "
              f"voice 0.5-6k {b['voice0.5-6k']*100:.1f}% | >6k {b['high>6k']*100:.1f}%")
        print(f"  per-{5}s peaks (Hz): {res['peaks_hz']}")
        print(f"  => {verdict(b)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
