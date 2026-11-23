# -*- coding: utf-8 -*-
"""成片台词审计：转写整片，揪出重复句 / 漏句 / 非中文。

逐段 ASR 全绿也不代表拼起来没问题 —— 跨段重复、模型自发重复、手捂嘴吞音，
都只在整片上才看得见。

用法：
    python audit_final_film.py 成片.mp4 台词原稿.md
    python audit_final_film.py 成片.mp4 台词原稿.md --write asr.txt

输出四块：
  1) 逐行时间轴（人工扫这个，别只看总数）
  2) 重复句（同一句出现 >1 次 —— 硬伤，必须改）
  3) 原稿里在成片找不到的句子（同音字会造成误报，人工复核）
  4) 语言判定（非 zh 说明台词没写进 <d>[Chinese]）

依赖：ffmpeg（D:/tools/ffmpeg/ffmpeg.exe）、faster-whisper 本地模型。
⚠️ ffmpeg 不认 /d/ 前缀路径，脚本内统一转成 D:/。
"""
import io
import os
import re
import subprocess
import sys
import warnings

warnings.filterwarnings("ignore")

FF = r"D:/tools/ffmpeg/ffmpeg.exe"
MODEL = r"D:/Hermes/models/faster-whisper-large-v3"  # 不要从 HF 下，连不上
TMP_WAV = os.path.join(os.environ.get("TEMP", "."), "audit_film.wav")

# 归一化：去标点空白，只留汉字数字字母。同音字不处理（会误判，留给人工）
PUNCT = "，。？！、；：\"'“”‘’（）《》…—　 .,?!;:\"'()<>-\n\r\t"


def norm(s: str) -> str:
    return "".join(ch for ch in s if ch not in PUNCT)


def to_native(p: str) -> str:
    """ffmpeg 需要 D:/ 风格路径，MSYS 的 /d/ 会被拒。"""
    p = p.replace("\\", "/")
    if re.match(r"^/[a-zA-Z]/", p):
        p = p[1].upper() + ":" + p[2:]
    return p


def transcribe(video: str):
    video = to_native(video)
    subprocess.run(
        [FF, "-y", "-i", video, "-vn", "-ac", "1", "-ar", "16000",
         to_native(TMP_WAV), "-loglevel", "error"],
        check=True,
    )
    from faster_whisper import WhisperModel

    m = WhisperModel(MODEL, device="cpu", compute_type="int8")
    segs, info = m.transcribe(to_native(TMP_WAV), language="zh", vad_filter=True)
    rows = [(s.start, s.end, s.text.strip()) for s in segs]
    return rows, getattr(info, "language_probability", None)


def load_screenplay(path: str):
    """从台词稿抽引号内台词；跳过 # / > 开头的说明行（历史误报源）。"""
    lines = []
    for raw in io.open(path, encoding="utf-8"):
        if raw.lstrip().startswith(("#", ">")):
            continue
        for q in re.findall(r'[“"]([^”"]+)[”"]', raw):
            q = q.strip()
            if len(norm(q)) >= 2:
                lines.append(q)
    return lines


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 1
    video, script = sys.argv[1], sys.argv[2]
    rows, langp = transcribe(video)

    print(f"=== 语言判定：zh，置信度 {langp:.2f} ===")
    if langp is not None and langp < 0.5:
        print("!! 不是中文 —— 台词没写进 <d>[Chinese]，H3 在自己编。全片作废重来。\n")

    print(f"\n=== 逐行时间轴（{len(rows)} 个断句，逐行扫，别只看总数）===")
    for st, en, tx in rows:
        print(f"{st:7.1f}-{en:7.1f}  {tx}")

    # ---- 重复句 ----
    print("\n=== 重复句（同一句出现 >1 次 = 硬伤）===")
    seen = {}
    for st, en, tx in rows:
        k = norm(tx)
        if len(k) >= 3:
            seen.setdefault(k, []).append(st)
    dup = {k: v for k, v in seen.items() if len(v) > 1}
    if not dup:
        print("无")
    else:
        for k, ts in dup.items():
            print(f"  「{k}」 出现在 {', '.join(f'{t:.1f}s' for t in ts)}  ← 检查是否段06尾/段07头各写了一遍")

    # ---- 漏句 ----
    if os.path.exists(script):
        src = load_screenplay(script)
        joined = "".join(norm(t) for _, _, t in rows)
        print(f"\n=== 原稿 {len(src)} 句，成片比对 ===")
        missing = [q for q in src if norm(q) not in joined]
        if not missing:
            print("无漏句")
        else:
            print("疑似漏句（同音字会误报，逐条人工复核）：")
            for q in missing:
                print(f"  {q}")
    else:
        print(f"\n（跳过漏句比对：找不到 {script}）")

    if "--write" in sys.argv:
        i = sys.argv.index("--write")
        if i + 1 < len(sys.argv):
            out = sys.argv[i + 1]
            io.open(out, "w", encoding="utf-8").write(
                "\n".join(f"{s:7.1f}-{e:7.1f}  {t}" for s, e, t in rows)
            )
            print(f"\n时间轴已写入 {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
