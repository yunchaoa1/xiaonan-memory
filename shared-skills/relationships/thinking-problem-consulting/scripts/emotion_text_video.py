"""
情感内容 · 纯文字短视频合成（2026-11-22 实测跑通）

管线: 台词表 + 配音mp3 → whisper large-v3 卡时间戳 → PIL 渲文字层 → ffmpeg overlay → 成片

为什么不用 ffmpeg drawtext:
  drawtext 的 alpha='if(lt(t,a),0,...)' 表达式里的逗号会和 filtergraph 的分隔符打架，
  中文 + 表达式 + 多层同时上必然 "Invalid argument"。PIL 渲透明 PNG 再 overlay 一次过。

用法:
    python emotion_text_video.py --lines 台词.txt --voice 配音.mp3 --out 成片.mp4

台词表格式（一行一个显示单元，竖线前是角色标记）:
    n|她跟我说「我妈偏心我弟」的时候
    s|她说：能理解啊
    i|我说：我没问你理解不理解
    k|你要东西这个动作本身，是错的

    n = 旁白（浅白）  s = 她说（浅灰）  i = 我说（纯白）  k = 关键句（暖金 + 字号加大）
    行内用「|」之后的文字；想换行就在同一显示单元里再分条，用 /// 分隔:
        i|我问她///你从小到大有没有一次///是理直气壮地跟家里要过东西

依赖: faster-whisper(large-v3)、PIL、ffmpeg
"""
import argparse, os, re, subprocess, sys

FFMPEG_DEFAULT = r"D:/tools/ffmpeg/ffmpeg"
WHISPER_DEFAULT = r"D:/Hermes/models/faster-whisper-large-v3"

W, H = 1080, 1920
FONT_R = r"C:/Windows/Fonts/msyh.ttc"
FONT_B = r"C:/Windows/Fonts/msyhbd.ttc"

COLORS = {
    "s": (188, 188, 196, 255),   # 她说：浅灰
    "i": (255, 255, 255, 255),   # 我说：纯白
    "k": (255, 236, 190, 255),   # 关键：暖金
    "n": (238, 238, 242, 255),   # 旁白：近白
}
SIZES = {"k": 84, "i": 72, "s": 72, "n": 72}


def parse_lines(path):
    """返回 [(role, [显示行...]), ...]"""
    out = []
    for raw in open(path, encoding="utf-8"):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        m = re.match(r"^([nsik])\s*\|(.*)$", line)
        if not m:
            raise SystemExit("台词格式错误（要 '标记|文字'）: " + line)
        role, body = m.group(1), m.group(2).strip()
        parts = [p.strip() for p in body.split("///") if p.strip()]
        out.append((role, parts))
    return out


def transcribe(voice, model_path, ffmpeg):
    """配音转 wav 并返回 whisper 分段 [(start, end, text), ...] + 总时长"""
    os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")
    from faster_whisper import WhisperModel

    wav = os.path.splitext(voice)[0] + "_16k.wav"
    subprocess.run([ffmpeg, "-y", "-v", "error", "-i", voice,
                    "-ac", "1", "-ar", "16000", "-acodec", "pcm_s16le", wav], check=True)
    model = WhisperModel(model_path, device="cuda", compute_type="float16")
    segs, info = model.transcribe(wav, language="zh", vad_filter=True)
    return [(s.start, s.end, s.text.strip()) for s in segs], info.duration


def align(display_lines, segs, duration):
    """把显示单元对齐到 whisper 分段：贪心向前匹配字符重合，失败则按字数比例兜底"""
    def norm(t):
        return re.sub(r"[^\u4e00-\u9fffA-Za-z0-9]", "", t)

    times, si = [], 0
    for role, parts in display_lines:
        target = norm("".join(parts))
        best_i, best_score = si, -1
        for j in range(si, min(si + 4, len(segs))):
            cand = norm(segs[j][2])
            score = sum(1 for ch in target if ch in cand)
            if score > best_score:
                best_score, best_i = score, j
        st = segs[best_i][0] if segs else 0.0
        times.append(st)
        si = max(si, best_i)

    # 兜底：一句都没匹配上（比如配音与文稿完全不符）→ 按字数比例铺
    if not any(t > 0 for t in times[1:]) and segs:
        total_chars = sum(len("".join(p)) for _, p in display_lines) or 1
        acc, cur = 0, 0.0
        for i, (_, parts) in enumerate(display_lines):
            times[i] = cur
            acc += len("".join(parts))
            cur = duration * acc / total_chars

    for i in range(1, len(times)):
        if times[i] <= times[i - 1]:
            times[i] = times[i - 1] + 1.2   # 防重叠 / 防倒序

    ends = times[1:] + [duration + 0.6]
    # 关键修正：每段结束不超过下一段开始（whisper 分段本身会前后交叠）
    fixed = []
    for i, (st, en) in enumerate(zip(times, ends)):
        if i + 1 < len(times):
            en = min(en, times[i + 1] - 0.05)
        fixed.append((st, max(st + 0.4, en)))
    return fixed


def render(role, parts, idx, outdir):
    from PIL import Image, ImageDraw, ImageFont
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    fs = SIZES.get(role, 72)
    ls = int(fs * 0.62)
    font = ImageFont.truetype(FONT_B if role in ("k", "i") else FONT_R, fs)
    total = len(parts) * fs + (len(parts) - 1) * ls
    y = int(H / 2 - total / 2)
    for ln in parts:
        bb = d.textbbox((0, 0), ln, font=font)
        x = (W - (bb[2] - bb[0])) // 2 - bb[0]
        d.text((x, y), ln, font=font, fill=COLORS.get(role, COLORS["n"]))
        y += fs + ls
    p = os.path.join(outdir, "l%02d.png" % idx)
    im.save(p)
    return p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lines", required=True, help="台词表 txt")
    ap.add_argument("--voice", required=True, help="配音 mp3/wav")
    ap.add_argument("--out", required=True, help="输出 mp4")
    ap.add_argument("--ffmpeg", default=FFMPEG_DEFAULT)
    ap.add_argument("--whisper", default=WHISPER_DEFAULT)
    ap.add_argument("--bg", default="0x0B0B10", help="背景色（默认近黑蓝）")
    ap.add_argument("--no-align", action="store_true", help="跳过 whisper，按字数比例铺时间")
    a = ap.parse_args()

    display = parse_lines(a.lines)
    outdir = os.path.join(os.path.dirname(os.path.abspath(a.out)), "txt_" + os.path.splitext(os.path.basename(a.out))[0])
    os.makedirs(outdir, exist_ok=True)

    if a.no_align:
        dur = float(subprocess.run([a.ffmpeg, "-i", a.voice], capture_output=True, text=True)
                    .stderr.split("Duration: ")[1].split(",")[0].strip().split(":")[1]) * 60
        segs = []
    else:
        segs, dur = transcribe(a.voice, a.whisper, a.ffmpeg)

    times = align(display, segs, dur)
    DUR = dur + 1.2

    paths = [render(r, parts, i, outdir) for i, (r, parts) in enumerate(display)]

    args = [a.ffmpeg, "-y", "-v", "error",
            "-f", "lavfi", "-i", "color=c=%s:s=%dx%d:d=%.2f:r=30" % (a.bg, W, H, DUR)]
    for p in paths:
        args += ["-loop", "1", "-i", p]
    args += ["-i", a.voice]

    fc, cur = [], "0:v"
    for i, (st, en) in enumerate(times):
        fc.append("[%s][%d:v]overlay=0:0:enable='between(t,%.2f,%.2f)'[o%d]" % (cur, i + 1, st, en, i))
        cur = "o%d" % i
    fc.append("[%s]fade=t=in:st=0:d=0.6,fade=t=out:st=%.2f:d=1.0,format=yuv420p[vout]" % (cur, DUR - 1.0))

    args += ["-filter_complex", ";".join(fc),
             "-map", "[vout]", "-map", "%d:a" % (len(paths) + 1),
             "-t", "%.2f" % DUR, "-c:v", "libx264", "-preset", "medium", "-crf", "19",
             "-c:a", "aac", "-b:a", "160k", "-r", "30", "-shortest", a.out]

    r = subprocess.run(args, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-2000:])
        sys.exit(1)
    print("OK", a.out, os.path.getsize(a.out), "bytes")
    print("文字层目录:", outdir)
    print("时间轴:", ["%.2f-%.2f" % t for t in times])


if __name__ == "__main__":
    main()
