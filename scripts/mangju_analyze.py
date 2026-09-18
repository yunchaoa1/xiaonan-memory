# -*- coding: utf-8 -*-
"""漫剧拉片分析：从 *.asr.json 算台词密度 / 静默占比 / 单句长度 / 交锋频率。
输出对照表 + 按 2 分钟/集折算的每集指标。
用法: python mangju_analyze.py file1.asr.json file2.asr.json ...
"""
import json, re, sys, os

def load(p):
    return json.load(open(p, encoding="utf-8"))

def analyze(rec):
    dur = rec["dur"]
    segs = rec["segments"]
    speech = sum(s["e"] - s["s"] for s in segs)
    # 单句：段内按标点切
    sents = []
    for s in segs:
        for x in re.split(r"[。！？!?…]+", s["t"]):
            x = x.strip("，、；;：: 　\"'“”‘’")
            if len(x) >= 2:
                sents.append(x)
    allchars = sum(len(re.sub(r"[，。、！？：；\s]", "", s["t"])) for s in segs)
    # 空档
    gaps = []
    for a, b in zip(segs, segs[1:]):
        g = b["s"] - a["e"]
        if g > 0: gaps.append(round(g, 2))
    big = [g for g in gaps if g >= 3.0]
    mins = dur / 60
    return {
        "file": os.path.basename(rec["file"]),
        "dur_s": dur, "dur_min": round(mins, 1),
        "speech_s": round(speech, 1),
        "speech_pct": round(speech / dur * 100, 1),
        "silent_pct": round((1 - speech / dur) * 100, 1),
        "chars": allchars,
        "chars_per_min": round(allchars / mins, 0),
        "segs": len(segs),
        "segs_per_min": round(len(segs) / mins, 1),
        "sents": len(sents),
        "sent_avg": round(sum(len(x) for x in sents) / max(len(sents), 1), 1),
        "sent_over15_pct": round(sum(1 for x in sents if len(x) > 15) / max(len(sents), 1) * 100, 1),
        "sent_max": max((len(x) for x in sents), default=0),
        "gap_big_n": len(big), "gap_big_s": round(sum(big), 1),
        "gap_max": max(gaps, default=0),
        # 按 2 分钟/集折算
        "per_ep_chars_2min": round(allchars / mins * 2, 0),
        "per_ep_sents_2min": round(len(sents) / mins * 2, 1),
        "per_ep_segs_2min": round(len(segs) / mins * 2, 1),
    }

if __name__ == "__main__":
    rows = [analyze(load(p)) for p in sys.argv[1:]]
    keys = ["file", "dur_min", "speech_pct", "silent_pct", "chars", "chars_per_min",
            "segs_per_min", "sent_avg", "sent_over15_pct", "sent_max",
            "gap_big_n", "gap_big_s", "gap_max",
            "per_ep_chars_2min", "per_ep_sents_2min", "per_ep_segs_2min"]
    hdr = {k: k for k in keys}
    out = [hdr] + rows
    w = {k: max(len(str(r.get(k, ""))) for r in out) for k in keys}
    for i, r in enumerate(out):
        print(" | ".join(str(r.get(k, "")).ljust(w[k]) for k in keys))
        if i == 0:
            print("-+-".join("-" * w[k] for k in keys))
    # 汇总
    if rows:
        print("\n=== 汇总（4 样本平均）===")
        for k in ["speech_pct", "silent_pct", "chars_per_min", "segs_per_min",
                  "sent_avg", "sent_over15_pct", "per_ep_chars_2min", "gap_max"]:
            print(f"{k}: {sum(r[k] for r in rows)/len(rows):.1f}")
        json.dump(rows, open("lapian_analysis.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("saved -> lapian_analysis.json")
