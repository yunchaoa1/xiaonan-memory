# -*- coding: utf-8 -*-
"""对白型剧本自检：量化红果集剧本是否符合《对白型铁律》。
指标：集数 / 每集台词字数(300-350) / △字数与非空段数 / 台词△比 / VO(应0) / OS(≤2/集) / 三要素 / 单次发言≤2句 / 场景行
用法: python duibai_check.py <剧本.md>
"""
import re, sys, os, json

def analyze(path):
    t = open(path, encoding="utf-8").read()
    i = t.find("集剧本正文")
    body = t[i:] if i > 0 else t
    # 切集
    eps = re.split(r"\n(?=#{2,4}\s*第\s*\d+\s*集)", body)
    eps = [e for e in eps if re.match(r"#{2,4}\s*第\s*\d+\s*集", e.strip())]
    rows = []
    for e in eps:
        title = e.strip().split("\n")[0].strip("# ").strip()
        lines = [l.strip() for l in e.split("\n")]
        dlg_chars = 0; dlg_lines = 0; act_chars = 0; act_lines = 0
        os_n = 0; vo_n = 0; scene_n = 0
        elem = sum(1 for k in ("人物线", "转折", "卡点") if k in e)
        speakers = {}
        for l in lines:
            if not l or l.startswith("#"): continue
            # 去 markdown 前缀（- / * / ** / - **）
            raw = l
            l = re.sub(r"^[-*•]+\s*", "", l).strip()
            l = re.sub(r"^\*\*|\*\*$", "", l).strip()
            if re.match(r"^\d+\s*[-－]\s*\d+", l): scene_n += 1; continue
            if l.startswith("△") or raw.lstrip().startswith("△"):
                act_lines += 1; act_chars += len(re.sub(r"[^\u4e00-\u9fa5]", "", l))
                continue
            if "VO" in l: vo_n += 1
            if "OS" in l: os_n += 1
            # 台词行：角色（神态）：内容  或  角色：内容
            m = re.match(r"^[-*]?\s*([^：:（(]{1,12})[（(]?[^）)：:]*[）)]?\s*[：:]\s*(.+)$", l)
            if m:
                dlg_lines += 1
                txt = m.group(2)
                dlg_chars += len(re.sub(r"[^\u4e00-\u9fa5]", "", txt))
                sp = m.group(1).strip()
                speakers[sp] = speakers.get(sp, 0) + 1
        rows.append(dict(ep=title, dlg_chars=dlg_chars, dlg_lines=dlg_lines,
                         act_chars=act_chars, act_lines=act_lines, os=os_n, vo=vo_n,
                         scenes=scene_n, elem=elem, speakers=len(speakers)))
    return rows

if __name__ == "__main__":
    p = sys.argv[1]
    rows = analyze(p)
    print(f"file={os.path.basename(p)}  episodes={len(rows)}")
    print(f"{'ep':<28}{'台词字':>7}{'台词句':>7}{'△字':>7}{'△段':>6}{'比T/△':>8}{'OS':>4}{'VO':>4}{'三要素':>7}{'场景':>5}")
    for r in rows:
        ratio = round(r['dlg_chars'] / r['act_chars'], 2) if r['act_chars'] else 0
        print(f"{r['ep'][:26]:<28}{r['dlg_chars']:>7}{r['dlg_lines']:>7}{r['act_chars']:>7}{r['act_lines']:>6}{ratio:>8}{r['os']:>4}{r['vo']:>4}{r['elem']:>7}{r['scenes']:>5}")
    n = len(rows)
    if n:
        import statistics as st
        dc = [r['dlg_chars'] for r in rows]; ac = [r['act_chars'] for r in rows]
        print("\n=== 汇总 ===")
        print(f"集数 {n} | 台词字/集 平均 {st.mean(dc):.0f} 中位 {st.median(dc):.0f} 区间 {min(dc)}-{max(dc)}")
        print(f"△字/集 平均 {st.mean(ac):.0f} | 台词/△ 总比 {sum(dc)/max(sum(ac),1):.2f}")
        print(f"VO 总 {sum(r['vo'] for r in rows)}（应 0） | OS 总 {sum(r['os'] for r in rows)}（每集应 ≤2）")
        print(f"三要素齐全集 {sum(1 for r in rows if r['elem']==3)}/{n} | 场景行总 {sum(r['scenes'] for r in rows)}")
        inband = sum(1 for r in rows if 300 <= r['dlg_chars'] <= 350)
        print(f"台词落在 300-350 字的集 {inband}/{n}")
