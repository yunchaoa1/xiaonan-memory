# -*- coding: utf-8 -*-
"""H3 r8 29-seg director first-pass builder.
Loads storyboard package + shot data modules, renders official six-section
self-contained prompts, QAs them, splits into RAM-safe batches, and writes
API payloads (skeleton = wf_single/workflow_single_S01.json, node 1201,
timeline_data content swapped only)."""
import json, os, re, sys, math, random, string, uuid

BASE = r"D:\Hermes\xiaonan-memory\opc-sim\v2\07_h3_prompt\h3_r8_29seg"
sys.path.insert(0, BASE)
PKG = r"D:\Hermes\xiaonan-memory\opc-sim\v2\06_storyboard\storyboard_package.json"
SKEL = r"D:\Hermes\xiaonan-memory\opc-sim\v2\07_h3_prompt\wf_single\workflow_single_S01.json"
INPUT_DIR = r"D:\SDkecheng\ComfyUI\input"
OUT = os.path.join(BASE, "payloads")
os.makedirs(OUT, exist_ok=True)

import common
from common import ZY, MO, CAP, HOME, CORR, SB

ROLE_IMG = {"zy": ZY, "mo": MO, "cap": CAP}

# ---- frame counts: 17k+5 snap with ceil so frames/24 >= card duration_s ----
def frames_for(dur_s):
    k = math.ceil((dur_s * 24 - 5) / 17.0)
    return 17 * k + 5

pkg = json.load(open(PKG, encoding="utf-8"))
cards = {c["shot_id"]: c for c in pkg["shot_cards"]}

shots = []
for part in ("data_p1", "data_p2", "data_p3"):
    m = __import__(part)
    shots += m.P1 if part == "data_p1" else m.P2 if part == "data_p2" else m.P3
assert len(shots) == 29 and len({s["sid"] for s in shots}) == 29

FRAMES = {s["sid"]: frames_for(cards[s["sid"]]["duration_s"]) for s in shots}
# override common for tfmt consistency (tfmt is seconds-based, unchanged)

def purify_dlg(text):
    # inside <d> only: …… -> ， (official punctuation rule); no other change
    def rep(m):
        return m.group(0).replace("……", "，")
    return re.sub(r"<d>.*?</d>", rep, text, flags=re.S)

issues = []

def dlg_of(body):
    # <d>[Chinese] ...</d> -> inner text without the language tag
    return [re.sub(r"^\[[A-Za-z]+\]\s*", "", m) for m in re.findall(r"<d>(.*?)</d>", body, re.S)]

for sh in shots:
    sid = sh["sid"]; card = cards[sid]
    fr = FRAMES[sid]
    if fr / 24.0 < card["duration_s"] - 1e-9:
        issues.append(f"{sid}: frames {fr} -> {fr/24.0:.3f}s < card {card['duration_s']}s")
    if (fr - 5) % 17 != 0:
        issues.append(f"{sid}: NOT 17k+5")
    joined_pkg = "".join(x["line"].replace("……", "，").strip() for x in (card.get("dialogue") or []))
    lines = [d for shx in sh["shots"] for d in dlg_of(shx["body"])]
    joined_data = "".join(x.replace("……", "，").strip() for x in lines)
    if joined_pkg != joined_data:
        issues.append(f"{sid}: DIALOGUE MISMATCH\n  pkg : {joined_pkg}\n  data: {joined_data}")
    # forbidden in <d> (raw): tildes, repeated marks, emoji, ellipsis, decorative
    for d in lines:
        bad = []
        if "…" in d: bad.append("ellipsis(will-be-purified)")
        if "~" in d or "～" in d: bad.append("tilde")
        if re.search(r"[!！]{2,}|[?？]{2,}|[。]{2,}", d): bad.append("repeated-mark")
        if d and not re.search(r"[。？！，]$", d): bad.append(f"no-ending-punct({d!r})")
        if bad: issues.append(f"{sid}: <d> {bad}: {d!r}")
    for shx in sh["shots"]:
        t = shx.get("t")
        if t is not None and t >= card["duration_s"]:
            issues.append(f"{sid}: cut t={t} >= card dur {card['duration_s']}")
    # refs/pic integrity
    pics = [s["pic"] for s in sh["subjects"]]
    if sorted(pics) != list(range(1, max(pics) + 1)):
        issues.append(f"{sid}: pic numbers not contiguous 1..{max(pics)}: {pics}")
    if not any(s["role"] == "board" for s in sh["subjects"]):
        issues.append(f"{sid}: no board subject")

print(f"frames per shot: {json.dumps(FRAMES)}")
print(f"total frames: {sum(FRAMES.values())} = {sum(FRAMES.values())/24.0:.2f}s")

# ---- render six-section prompts ----
rendered = []
for sh in shots:
    sid = sh["sid"]
    glob_text, seg_text, refs_auto = common.render(sh)
    full = glob_text + "\n\ndetailed_description:\n" + seg_text
    full = purify_dlg(full)
    # build segment refs: subject order by pic
    subj = sorted(sh["subjects"], key=lambda s: s["pic"])
    refs = []
    for s in subj:
        pic = s["pic"]
        if s["role"] == "board":
            f = SB[sid]
        elif s["role"] == "space":
            f = s["img"]
        else:
            f = ROLE_IMG[s["role"]]
        if not f:
            issues.append(f"{sid}: no image for {s}")
        if not os.path.exists(os.path.join(INPUT_DIR, f)):
            issues.append(f"{sid}: MISSING input file {f}")
        refs.append({"index": pic - 1, "imageFile": f, "imageB64": ""})
    # QA on the full prompt
    if len(full) > 7000:
        issues.append(f"{sid}: prompt {len(full)} chars > 7000")
    if "…" in full or "~" in full or "～" in full:
        issues.append(f"{sid}: stray ellipsis/tilde survived purification")
    order = [full.find(x) for x in ("subject_definitions:", "\nsummary:\n", "retention_analysis:", "detailed_description:", "overall_soundscape:", "non_diegetic_music:")]
    if any(x < 0 for x in order) or order != sorted(order):
        issues.append(f"{sid}: six-section order broken: {order}")
    if "\nsummary:\n[reference generation]" not in full:
        issues.append(f"{sid}: summary missing [reference generation] prefix")
    # storyboard Picture official phrasing exists (subject_definitions)
    board_pic = [s["pic"] for s in sh["subjects"] if s["role"] == "board"][0]
    if f"<Picture {board_pic}> is a storyboard reference" not in full:
        issues.append(f"{sid}: storyboard <Picture {board_pic}> official line missing")
    # board pic appears in summary + retention
    summ = full.split("summary:")[1].split("retention_analysis:")[0]
    ret = full.split("retention_analysis:")[1].split("detailed_description:")[0]
    if f"<Picture {board_pic}>" not in summ:
        issues.append(f"{sid}: board not referenced in summary")
    if f"<Picture {board_pic}>" not in ret or "partially_preserved" not in ret:
        issues.append(f"{sid}: retention line for board pic missing/not partially_preserved")
    # no forbidden frame-anchored orientation wording
    if re.search(r"left of the frame|right of the screen|left edge of the|right edge of the|screen-left|screen-right", full, re.I):
        issues.append(f"{sid}: frame-anchored orientation wording")
    # subject definitions for every non-board pic
    for s in sh["subjects"]:
        if s["role"] == "board":
            continue
        p = s["pic"]
        sd_block = full.split("summary:")[0]
        if f"<Subject {p}>" not in sd_block:
            issues.append(f"{sid}: no subject_definitions line for pic {p}")
    rendered.append({"sid": sid, "duration_s": FRAMES[sid] / 24.0, "frames": FRAMES[sid],
                     "prompt": full, "refs": refs, "n_cuts": len(sh["shots"]),
                     "board_pic": board_pic})

hard = [i for i in issues if "will-be-purified" not in i]
print("--- ISSUES ---")
for i in issues: print(i)
print("issues:", len(issues), "hard:", len(hard))
if hard:
    sys.exit(2)

# ---- batch split: <=5 segs and <=1120 frames per batch (RAM guard) ----
MAX_FRAMES = 1120
MAX_SEGS = 5
batches, cur, curf = [], [], 0
for r in rendered:
    if cur and (len(cur) >= MAX_SEGS or curf + r["frames"] > MAX_FRAMES):
        batches.append(cur); cur, curf = [], 0
    cur.append(r); curf += r["frames"]
if cur: batches.append(cur)
print("batches:", [(len(b), sum(x["frames"] for x in b)) for b in batches])

# ---- assemble payloads from skeleton ----
skel = json.load(open(SKEL, encoding="utf-8"))
dir_node = [k for k, n in skel.items() if n.get("class_type") == "MiniMaxH3Director"][0]
tl_tpl = json.loads(skel[dir_node]["inputs"]["timeline_data"])
print("director node:", dir_node, "| total_frames widget:", skel[dir_node]["inputs"]["total_frames"])

def seg_id():
    return uuid.uuid4().hex[:12]

manifest = {}
for bi, batch in enumerate(batches, 1):
    tl = json.loads(json.dumps(tl_tpl))  # deep copy
    tl["totalFrames"] = sum(x["frames"] for x in batch)
    tl["frameRate"] = 24
    tl["durationSec"] = tl["totalFrames"] / 24.0
    g = tl["global"]
    g["prompt"] = ""          # per-segment self-contained prompts (content-only swap)
    g["refs"] = []
    segs = []
    start = 0
    for r in batch:
        s = {"id": seg_id(), "start": start, "length": r["frames"], "frameCount": r["frames"],
             "durationSec": round(r["frames"] / 24.0, 6), "prompt": r["prompt"],
             "negativePrompt": "bad video", "taskType": "", "refs": r["refs"],
             "refAudios": [], "refVideos": [],
             "genImage": {"imageFile": "", "fileName": ""}}
        segs.append(s)
        manifest[f"batch{bi}"] = manifest.get(f"batch{bi}", []) + [r["sid"]]
        start += r["frames"]
    tl["segments"] = segs
    wf = json.loads(json.dumps(skel))
    wf[dir_node]["inputs"]["timeline_data"] = json.dumps(tl, ensure_ascii=False)
    wf[dir_node]["inputs"]["total_frames"] = tl["totalFrames"]
    outp = os.path.join(OUT, f"batch_{bi}.json")
    with open(outp, "w", encoding="utf-8") as f:
        json.dump(wf, f, ensure_ascii=False)
    print(f"batch_{bi}.json saved: {len(segs)} segs, {tl['totalFrames']} frames -> {tl['totalFrames']/24.0:.2f}s")
with open(os.path.join(OUT, "manifest.json"), "w", encoding="utf-8") as f:
    json.dump(manifest, f, ensure_ascii=False, indent=1)
with open(os.path.join(OUT, "segments.json"), "w", encoding="utf-8") as f:
    json.dump(rendered, f, ensure_ascii=False, indent=1)
print("manifest:", json.dumps(manifest, ensure_ascii=False))
print("OK")
