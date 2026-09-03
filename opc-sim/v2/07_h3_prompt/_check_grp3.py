# -*- coding: utf-8 -*-
"""A-Q programmatic self-check v2 for h3_prompt_v9_grp3.json vs storyboard_package_v6.json."""
import json, io, re

PROMPTS = r"D:\Hermes\xiaonan-memory\opc-sim\v2\07_h3_prompt\h3_prompt_v9_grp3.json"
CARDS   = r"D:\Hermes\xiaonan-memory\opc-sim\v2\06_storyboard\storyboard_package_v6.json"

data = json.load(io.open(PROMPTS, encoding="utf-8"))
pkg  = json.load(io.open(CARDS, encoding="utf-8"))
cards = {c["shot_id"]: c for c in pkg["shot_cards"]}

IDS = ["S11b2", "S11c1", "S11c2", "S12", "S13", "S14", "S15", "S16", "S17"]
prompts = {s["shot_id"]: s["prompt"] for s in data["shots"]}

def t2s(t):
    mm, rest = t.split(":")
    ss, ms = rest.split(".")
    return int(mm) * 60 + int(ss) + int(ms) / 1000.0

lines = []
def res(rule, sid, ok, msg=""):
    print(f"{rule} {sid} {'PASS' if ok else 'FAIL'} {msg}")
    lines.append((rule, sid, ok, msg))

SECS = ["subject_definitions:", "summary:", "retention_analysis:", "detailed_description:",
        "overall_soundscape:", "non_diegetic_music:"]
for sid in IDS:
    p = prompts[sid]
    card = cards[sid]
    dur = float(card["duration_s"])
    dlg = [("zhou-ye" if "zhou-ye" in d["speaker"] else "mother", d["line"]) for d in card["dialogue"]]
    # A order & count
    idx = [p.find(s) for s in SECS]
    okA = all(i >= 0 for i in idx) and idx == sorted(idx) and all(p.count(s) == 1 for s in SECS)
    res("A", sid, okA, "" if okA else f"idx={idx}")
    # B CJK only inside <d>; <d> content uses only ，。？！+ CJK + spaces
    outside = re.sub(r"<d>\[Chinese\] [^<]*</d>", "", p)
    cjk_out = re.findall(r"[\u4e00-\u9fff\u3001\u3002\uff01\uff1f\uff0c\u201c\u201d\u2026\u300a\u300b\uff1b\uff1a\uff08\uff09]", outside)
    badp = []
    for m in re.finditer(r"<d>\[Chinese\] ([^<]*)</d>", p):
        if re.search(r"[^\u4e00-\u9fff，。？！ ]", m.group(1)):
            badp.append(m.group(1))
    res("B", sid, not cjk_out and not badp, f"cjk_out={cjk_out[:2]} badp={badp[:1]}")
    # C single take marker in detailed_description; official no-cuts sentence; zero cut-language
    dd = p[p.find("detailed_description:"):]
    n1 = len(re.findall(r"\[Shot 1\] A |\[Shot 1\] The |\[Shot 1\] A |\[Shot 1\]\n", dd))
    n2 = len(re.findall(r"\[Shot [2-9]\]", p))
    nocut = "The camera stays locked in this single continuous shot throughout, no cuts." in p
    cutlang = re.findall(r"\bcuts? to\b|\bcuts? away\b|\bcut to\b|reverse shot|new shot|second shot|insert shot", dd)
    res("C", sid, n1 == 1 and n2 == 0 and nocut and not cutlang, f"marker={n1} shotN={n2} nocut={nocut} cutlang={cutlang[:2]}")
    # D official storyboard sentence per slot; zero grid words
    expect_pic = 3 if sid in ("S11b2", "S11c1") else 4
    sent = f"<Picture {expect_pic}> is a storyboard reference for [Shot 1], defining its viewpoint, subject placement, and shot order."
    gridwords = re.findall(r"(grid|panel|border|layout|第.{1,2}格|构图对应)", p, re.I)
    res("D", sid, p.count(sent) == 1 and not gridwords, f"sent={p.count(sent)} gridwords={gridwords[:3]}")
    # E retention only positive statements
    ret = p[p.find("retention_analysis:"):p.find("detailed_description:")]
    badE = re.findall(r"never| no |not |won't|isn't|can't|doesn't|don't|without", ret)
    pos = len(re.findall(r"fully_preserved|partially_preserved", ret))
    res("E", sid, not badE and pos >= 3, f"bad={badE[:2]} pos={pos}")
    # F speaker id per <d> + nearest preceding tag matches card speaker
    ds = list(re.finditer(r"<d>\[Chinese\] ([^<]*)</d>", p))
    spok, spmatch = True, True
    if not dlg:
        res("F", sid, not ds, f"d={len(ds)} card_lines=0 (no dialogue shot)")
    else:
        for m in ds:
            pre = p[max(0, m.start() - 400):m.start()]
            i1 = pre.rfind("(S1)")
            i2 = pre.rfind("(S2)")
            if i1 < 0 and i2 < 0:
                spok = False
                continue
            got = "S1" if i1 > i2 else "S2"
            # find card line owning this chunk via cumulative offsets over the concatenation
            pre_text = "".join(x.group(1) for x in ds if x.start() < m.start())
            pos = len(pre_text)
            acc = 0
            expect = None
            for spk, ln in dlg:
                if acc <= pos < acc + len(ln):
                    expect = "S1" if spk == "zhou-ye" else "S2"
                    break
                acc += len(ln)
            if expect and got != expect:
                spmatch = False
        res("F", sid, spok and spmatch and len(ds) >= 1, f"d={len(ds)} card={len(dlg)} spok={spok} spmatch={spmatch}")
    # G single-space subject definition
    res("G", sid, "is the single space of this shot:" in p, "")
    # H style opening sentence of detailed_description
    ddbody = p[p.find("detailed_description:") + len("detailed_description:"):].lstrip()
    res("H", sid, ddbody.startswith("The target video uses a 3D animated film style"), "")
    # I negation scan (official no-cuts sentence + N/A exempt)
    body = p.replace("The camera stays locked in this single continuous shot throughout, no cuts.", "").replace("N/A", "")
    negs = re.findall(r"\b(no|not|never|without|none|nothing|nor|nowhere|won't|isn't|aren't|can't|don't|doesn't|didn't|wasn't|weren't|hasn't|haven't|hadn't|couldn't|shouldn't|wouldn't)\b", body, re.I)
    res("I", sid, not negs, f"negs={negs[:5]}")
    # J timestamps parse + within card duration
    ts = [t2s(m.group(1)) for m in re.finditer(r"\b(\d{2}:\d{2}\.\d{3})\b", p)]
    okJ = len(ts) >= 3 and all(t <= dur for t in ts)
    res("J", sid, okJ, f"ts={len(ts)} max={max(ts) if ts else None} dur={dur}")
    # K length cap
    res("K", sid, len(p) <= 7000, f"len={len(p)}")
    # L <d> concatenation == card dialogue verbatim (order preserved)
    dtexts = [m.group(1) for m in ds]
    okL = "".join(dtexts) == "".join(l for _, l in dlg)
    res("L", sid, okL, "" if okL else f"got={''.join(dtexts)} want={''.join(l for _, l in dlg)}")
    # M zero left/right / frame-anchor terms
    banned = re.findall(r"\bleft\b|\bright\b|\bcorner of the frame\b|\boff.?screen\b|\bon.?screen\b|\bcenter of frame\b|\btop of frame\b|\bbottom of frame\b", p, re.I)
    res("M", sid, not banned, f"banned={banned[:3]}")
    # N <d>[Chinese] + single space (or zero <d> when card has no dialogue)
    if dlg:
        okN = (not re.search(r"<d>\[Chinese\][^ ]", p)) and "<d>[Chinese] " in p and not re.search(r"<d>\[Chinese\] [^<]*[^\u4e00-\u9fff，。？！ ]</d>", p)
    else:
        okN = "<d>" not in p
    res("N", sid, okN, "")
    # O storyboard <Picture N> label line non-empty and once
    res("O", sid, sent in p and len(re.findall(r"<Picture \d+> is a storyboard reference", p)) == 1, "")
    # P no bag; only the on-camera characters tracked
    bag = re.findall(r"\bbag\b", p, re.I)
    defs = p[:p.find("summary:")]
    if sid == "S11b2":
        badP = "is Mother," in defs
    elif sid == "S11c1":
        badP = "is Zhou Ye," in defs
    else:
        badP = ("is Zhou Ye," not in defs) or ("is Mother," not in defs)
    res("P", sid, not bag and not badP, f"bag={len(bag)} defs_ok={not badP}")
    # Q contiguous numbering: Subject n <- Picture n; storyboard picture = last slot
    subj = sorted(set(int(x) for x in re.findall(r"<Subject (\d)> is", defs)))
    picrefs = sorted(set(int(x) for x in re.findall(r"in <Picture (\d)>", defs)))
    okQ = subj == list(range(1, len(subj) + 1)) and picrefs == subj and expect_pic == len(subj) + 1
    res("Q", sid, okQ, f"subj={subj} picrefs={picrefs} board={expect_pic}")

fails = [l for l in lines if not l[2]]
print("=" * 60)
print("TOTAL FAILS:", len(fails))
for r, s, ok, msg in fails:
    print("FAIL", r, s, msg)
