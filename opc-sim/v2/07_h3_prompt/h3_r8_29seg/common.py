# -*- coding: utf-8 -*-
"""H3 r8 29-seg director payload builder — shared templates & renderers.
Official six-section English prompts (per minimax-h3-shot-prompt), Chinese only in <d>.
Subject slot order: 人物图 -> 场景图 -> 故事板图 -> 道具图; Picture N = slot index+1.
"""
import json, os, copy

OUTDIR = r"D:\Hermes\xiaonan-memory\opc-sim\v2\07_h3_prompt\h3_r8_29seg"

ZY = "openai_gpt-image-2-medium_20260904_162321_2c587b34.png"
MO = "openai_gpt-image-2-medium_20260904_162330_6145ca5c.png"
CAP = "openai_gpt-image-2-medium_20260904_162523_5e369c06.png"
HOME = "openai_gpt-image-2-medium_20260904_162443_a1a292ea.png"
CORR = "openai_gpt-image-2-medium_20260904_162627_e598bae0.png"

SB = {
 "S01":"openai_gpt-image-2-medium_20260904_184316_0313d74b.png","S02":"openai_gpt-image-2-medium_20260904_184357_5b8ae3f2.png",
 "S03":"openai_gpt-image-2-medium_20260904_184305_b8acdea8.png","S04":"openai_gpt-image-2-medium_20260904_184549_fc74044f.png",
 "S05a1":"openai_gpt-image-2-medium_20260904_184526_ee510de3.png","S05a2":"openai_gpt-image-2-medium_20260904_184544_cc685e3d.png",
 "S05b1":"openai_gpt-image-2-medium_20260904_184726_f4fc500a.png","S05b2":"openai_gpt-image-2-medium_20260904_184708_72ffb2aa.png",
 "S05b3":"openai_gpt-image-2-medium_20260904_184709_6a13ea80.png","S06":"openai_gpt-image-2-medium_20260904_184902_0e4e146a.png",
 "S07":"openai_gpt-image-2-medium_20260904_184844_ec6e0932.png","S08a":"openai_gpt-image-2-medium_20260904_184846_e1a0fa21.png",
 "S08b":"openai_gpt-image-2-medium_20260904_185023_cfade1fe.png","S09a":"openai_gpt-image-2-medium_20260904_185044_5d5d5a24.png",
 "S09b":"openai_gpt-image-2-medium_20260904_185025_7585d5a8.png","S10a":"openai_gpt-image-2-medium_20260904_185211_53f1d682.png",
 "S10b":"openai_gpt-image-2-medium_20260904_185308_69fb5b43.png","S11a1":"openai_gpt-image-2-medium_20260904_185209_26e76ce4.png",
 "S11a2":"openai_gpt-image-2-medium_20260904_185430_558db00e.png","S11b1":"openai_gpt-image-2-medium_20260904_185426_40d42420.png",
 "S11b2":"openai_gpt-image-2-medium_20260904_185638_eea7e8cf.png","S11c1":"openai_gpt-image-2-medium_20260904_185805_f4bccab0.png",
 "S11c2":"openai_gpt-image-2-medium_20260904_185805_bf914365.png","S12":"openai_gpt-image-2-medium_20260904_185810_80bf4361.png",
 "S13":"openai_gpt-image-2-medium_20260904_190002_8e670aaf.png","S14":"openai_gpt-image-2-medium_20260904_185957_aa016ad5.png",
 "S15":"openai_gpt-image-2-medium_20260904_190002_b6948391.png","S16":"openai_gpt-image-2-medium_20260904_190117_812306e1.png",
 "S17":"openai_gpt-image-2-medium_20260904_190119_24713a9f.png",
}
DUR = {"S01":10,"S02":10,"S03":13,"S04":12,"S05a1":6,"S05a2":6,"S05b1":4,"S05b2":6,"S05b3":4,
 "S06":10,"S07":10,"S08a":10,"S08b":14,"S09a":12,"S09b":12,"S10a":10,"S10b":9,
 "S11a1":6,"S11a2":6,"S11b1":7,"S11b2":7,"S11c1":5,"S11c2":7,"S12":8,
 "S13":14,"S14":14,"S15":12,"S16":12,"S17":10}
def frames_for(dur_s):
    return 17*round((dur_s*24 - 5)/17.0) + 5
FRAMES = {s: frames_for(d) for s, d in DUR.items()}

def tfmt(sec):
    mm = int(sec//60); ss = sec - mm*60
    return f"{mm:02d}:{ss:06.3f}"

# ---- canonical lines ----
def zy_def(p, indoor, sid=None):
    shoes = "dark indoor slippers" if indoor else "dark shoes"
    return (f"<Subject {p}> is Zhou Ye, the about-26-year-old Chinese man in <Picture {p}>: an upright, "
            f"slightly lean build, a clear-cut face with a defined jaw, straight fairly thick eyebrows and calm dark "
            f"eyes, his hair in a neat short crop; he wears a deep-navy zip jacket over a dark round-neck top, dark "
            f"trousers and {shoes}. His appearance follows the sheet throughout.")

def mo_def(p, apron=True, sid=None):
    apr = " with a light-beige bib apron tied over it at her waist" if apron else ""
    return (f"<Subject {p}> is the mother, the about-52-year-old Chinese woman in <Picture {p}>: a slender, "
            f"slightly thin figure with soft gentle features, gentle dark eyes and a few fine grey strands at her "
            f"temples, her black hair gathered in a low bun at the nape; she wears a loose light-warm-grey knitted "
            f"top over dark charcoal-grey trousers{apr}. Her appearance follows the sheet throughout.")

def cap_def(p):
    return (f"<Subject {p}> is the deep-navy plain six-panel cotton cap with a curved brim and no markings, shown in "
            f"<Picture {p}>; it is Zhou Ye's cap, worn on his head, later taken off and held in his hand or set onto "
            f"the shoe cabinet, always the same object.")

def board_def(p, n_shots):
    if n_shots > 1:
        tgt = ", ".join(f"[Shot {i}]" for i in range(1, n_shots)) + f" and [Shot {n_shots}]"
    else:
        tgt = "[Shot 1]"
    return (f"<Picture {p}> is a storyboard reference for {tgt}, defining their viewpoint, subject placement and "
            f"shot order.")

def space_def(p, zone_text):
    return (f"<Subject {p}> is the single space of this shot: {zone_text}. The space follows <Picture {p}>; the "
            f"sheet panels, grids and labels never enter the frames.")

def zy_kept(): return ("his neat short crop, clear-cut face and calm dark eyes, the deep-navy zip jacket over the "
    "dark round-neck top, and his restrained manner are kept throughout")
def mo_kept(apron=True):
    s = ("her low bun with the grey temple strands, the loose light-warm-grey knitted top over the charcoal-grey trousers")
    if apron: s += ", the light-beige bib apron"
    return s + ", and her careful held-back manner are kept throughout"
def space_kept(zl): return f"the {zl} is the only space of the shot and is kept throughout"
def cap_kept(): return ("the deep-navy plain cap with its curved brim is the same object whether worn, held in his "
    "hand, or set onto the shoe cabinet, kept throughout")
def pic_kept(): return ("partially_preserved - its viewpoint, subject placement and shot order are realized in the "
    "take; the sheet layout, panels and labels never enter the frames")

def appear_str(appears):
    return ", ".join(f"[Shot {i}]" for i in sorted(appears))

def render(shot):
    """shot: dict with sid, subjects(list of def dicts), n_cuts, summary, shots(list of
    {t:None or sec, body}), sound, style; def dict fields:
    role zy/mo/cap/board/space, pic, sid, indoor, apron, zone_text, appears(list of shot idx)
    returns (global_text, seg_text, refs)"""
    subjs = shot["subjects"]; n = len(subjs); ncuts = shot.get("n_cuts") or len(shot["shots"])
    defs = []
    for s in subjs:
        r = s["role"]; p = s["pic"]
        if r=="zy": defs.append(zy_def(p, s.get("indoor", False), s.get("sid")))
        elif r=="mo": defs.append(mo_def(p, s.get("apron", True), s.get("sid")))
        elif r=="cap": defs.append(cap_def(p))
        elif r=="board": defs.append(board_def(p, ncuts))
        elif r=="space": defs.append(space_def(p, s["zone_text"]))
    sd = "\n".join(defs)
    ret = []
    for s in subjs:
        r = s["role"]; p = s["pic"]; ap = appear_str(s["appears"])
        if r=="zy": ret.append(f"<Subject {p}> (appears in {ap}): fully_preserved - {zy_kept()}")
        elif r=="mo": ret.append(f"<Subject {p}> (appears in {ap}): fully_preserved - {mo_kept(s.get('apron', True))}")
        elif r=="cap": ret.append(f"<Subject {p}> (appears in {ap}): fully_preserved - {cap_kept()}")
        elif r=="space": ret.append(f"<Subject {p}> (appears in {ap}): fully_preserved - {space_kept(s['zone_label'])}")
        elif r=="board": ret.append(f"<Picture {p}> ({ap} planning anchor): {pic_kept()}")
    ra = "\n".join(ret)
    glob_text = f"subject_definitions:\n{sd}\n\nsummary:\n[reference generation] {shot['summary']}\nretention_analysis:\n{ra}"
    dd = [shot["style"]]
    for i, sh in enumerate(shot["shots"]):
        if i == 0:
            dd.append("[Shot 1] " + sh["body"])
        else:
            dd.append(f"[Shot {i+1}] At {tfmt(sh['t'])}, the shot cuts to " + sh["body"])
    seg_text = "\n".join(dd)
    seg_text += f"\n\noverall_soundscape:\n{shot['sound']}\n\nnon_diegetic_music:\nN/A"
    refs = []
    for s in subjs:
        if s["role"] in ("zy", "mo", "cap", "space") and s.get("img"):
            refs.append({"index": s["pic"]-1, "imageFile": s["img"], "imageB64": ""})
    return glob_text, seg_text, refs
