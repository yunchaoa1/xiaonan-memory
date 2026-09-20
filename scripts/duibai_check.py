# -*- coding: utf-8 -*-
"""对白型剧本自检 v2。正文范围 §3→§4 前；台词行含带/不带（神态）两种形态。
用法: python duibai_check.py <剧本.md>"""
import re, sys

p = sys.argv[1]
t = open(p, encoding="utf-8").read()
body = t.split("## §3")[1].split("## §4")[0]
parts = re.split(r"###\s*第(\d+)集", body)[1:]
eps = [(int(parts[i]), parts[i+1]) for i in range(0, len(parts), 2)]
print(f"file={p.split(chr(92))[-1]}  episodes={len(eps)}")
print(f"{'ep':<6}{'台词字':>7}{'台词句':>7}{'△字':>7}{'△段':>5}{'T/△':>7}{'OS':>4}{'VO':>4}{'三要素':>6}{'场景':>5}")
stats = []
for n, seg in eps:
    title = seg.strip().split("\n")[0][:14]
    lines = [l.rstrip() for l in seg.split("\n")]
    dlg_c = dlg_n = act_c = act_n = os_n = vo_n = scene_n = 0
    tri = 0; run = 0; maxrun = 0; last_sp = None
    for l in lines:
        s = re.sub(r"^[-*\s]+", "", l).strip()
        if not s or s.startswith("#"): continue
        if re.match(r"^\d+\s*[-－]\s*\d+", s): scene_n += 1; continue
        if s.startswith("【"): tri += 1; continue
        if s.startswith("△"): act_n += 1; act_c += len(re.sub(r"[^\u4e00-\u9fa5]", "", s)); continue
        if s.startswith("人物："): continue
        if s.startswith("20-") or re.match(r"^\d+-\d+", s): scene_n += 1; continue
        m = re.match(r"^([\u4e00-\u9fa5A-Za-z·]{1,10})(（[^）]*）)?：(.+)$", s)
        if m:
            txt = m.group(3); sp = m.group(1)
            dlg_n += 1; dlg_c += len(re.sub(r"[^\u4e00-\u9fa5]", "", txt))
            if "OS" in m.group(0): os_n += 1
            if "VO" in m.group(0): vo_n += 1
            if sp == last_sp: run += 1
            else: run = 1; last_sp = sp
            maxrun = max(maxrun, run)
            continue
        if "OS" in s: os_n += 1
        if "VO" in s: vo_n += 1
    ratio = round(dlg_c / act_c, 2) if act_c else 0
    stats.append((n, dlg_c, dlg_n, act_c, act_n, ratio, os_n, vo_n, tri, scene_n, maxrun))
    print(f"E{n:<5}{dlg_c:>7}{dlg_n:>7}{act_c:>7}{act_n:>5}{ratio:>7}{os_n:>4}{vo_n:>4}{tri:>6}{scene_n:>5}  {title}")
d = [s[1] for s in stats]
print("\n=== 汇总 ===")
print(f"集数 {len(stats)} | 台词字/集 均值 {sum(d)//len(d)} 中位 {sorted(d)[len(d)//2]} 区间 {min(d)}-{max(d)}")
print(f"台词 300-350 区间集数 {sum(1 for x in d if 300 <= x <= 350)}/{len(d)}")
print(f"△字/集 均值 {sum(s[3] for s in stats)//len(stats)} | OS 总 {sum(s[6] for s in stats)} | VO 总 {sum(s[7] for s in stats)}")
print(f"三要素齐全集 {sum(1 for s in stats if s[8] >= 3)}/{len(stats)} | 场景行总 {sum(s[9] for s in stats)}")
print(f"单次发言>2句(连续同角色)总 {sum(1 for s in stats if s[10] > 2)} 集 | 最大连续发言 {max(s[10] for s in stats)} 句")
