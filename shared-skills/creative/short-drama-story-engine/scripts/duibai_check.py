# -*- coding: utf-8 -*-
"""红果集剧本量化自检（对白型）。

用法:
    python duibai_check.py <剧本.md> [--json out.json]

检查项（对白型铁律口径）:
    - 集数 / 每集集首三要素
    - 每集台词中文字数（目标 300–350；收束集同样不得缩水）
    - 每集 △ 字数与段数、台词/△ 比（>1 才说明台词为主）
    - VO 计数（应 0）/ OS 计数（每集 ≤2）
    - 单次发言连续句数（>2 需抽样人工判定是否长独白）
    - 场次行数

两个已知坑（本脚本已处理，勿改回去）:
    1) 正文范围必须截到 §4 工艺段之前——否则最后一集会把钩子链/时长表/自证/自评
       全部吞进来（历史事故: 末集 141 字被误报成 859 字）。
    2) 自证段落会写 "VO＝0"、"全文无镜头左/画面右" 这类声明——按关键词扫会把
       声明误判成违规。故本脚本只在正文区间内统计，并对命中行做"声明句"过滤。
"""
import re
import sys
import json

CJK = re.compile(r"[\u4e00-\u9fff]")

# 台词行：角色 或 角色（神态）：内容   —— 带/不带神态括号两种形态都要收
LINE_DIALOGUE = re.compile(r"^([\u4e00-\u9fffA-Za-z·]{1,12})(?:（[^）]*）)?\s*[：:]\s*(.+)$")
LINE_SCENE = re.compile(r"^\d+\s*[-－]\s*\d+\s+\S")
LINE_PEOPLE = re.compile(r"^人物\s*[：:]")
LINE_EP = re.compile(r"^###\s*第\s*(\d+)\s*集")
# 声明句过滤：整行在声明"没有某违规"的，不算违规命中
DECLARATIVE = re.compile(r"(＝|=)\s*0|零(解说|旁白|命中)|全文无|无(解说|旁白|『)|应为\s*0")


def strip_md(line):
    return re.sub(r"^[-*•\s]+", "", line).strip()


def cjk_len(s):
    return len(CJK.findall(s or ""))


def body_of(text):
    """正文 = §3 集剧本正文 → §4 之前。缺失标题时回退到全文。"""
    if "## §3" in text:
        t = text.split("## §3", 1)[1]
    elif "集剧本正文" in text:
        t = text.split("集剧本正文", 1)[1]
    else:
        return text
    for marker in ("## §4", "## §5", "## 4.", "## 四"):
        if marker in t:
            t = t.split(marker, 1)[0]
            break
    return t


def main():
    path = sys.argv[1]
    text = open(path, encoding="utf-8").read()
    body = body_of(text)

    blocks = re.split(r"(?m)^###\s*第\s*\d+\s*集", body)
    parts = re.findall(r"(?m)^###\s*第\s*(\d+)\s*集[^\n]*", body)
    eps = list(zip(parts, blocks[1:])) if len(blocks) > 1 else []

    rows = []
    for ep, blk in eps:
        dlg_chars = 0
        dlg_lines = 0
        tri_chars = 0
        tri_lines = 0
        os_n = vo_n = scene_n = 0
        max_run = run = 0
        last_sp = None

        for raw in blk.split("\n"):
            line = strip_md(raw)
            if not line:
                continue
            if LINE_SCENE.match(line) and "△" not in line:
                scene_n += 1
                continue
            if LINE_PEOPLE.match(line):
                continue
            if "VO" in line.upper() and not DECLARATIVE.search(line):
                vo_n += 1
            is_os = bool(re.search(r"(OS|O\.S\.|内心)", line, re.I))

            if line.startswith("△"):
                tri_lines += 1
                tri_chars += cjk_len(line[1:])
                last_sp = None          # △ 打断连续发言
                continue

            m = LINE_DIALOGUE.match(line)
            if m:
                spk, content = m.group(1), m.group(2)
                if spk in ("人物", "△", "OS", "VO", "字幕"):
                    continue
                dlg_lines += 1
                dlg_chars += cjk_len(content)
                if is_os:
                    os_n += 1
                if spk == last_sp:
                    run += 1
                else:
                    run = 1
                    last_sp = spk
                max_run = max(max_run, run)

        rows.append(dict(ep=int(ep), dlg_chars=dlg_chars, dlg_lines=dlg_lines,
                         tri_chars=tri_chars, tri_lines=tri_lines,
                         ratio=round(dlg_chars / tri_chars, 2) if tri_chars else None,
                         vo=vo_n, os=os_n, max_run=max_run, scenes=scene_n))

    print(f"剧本: {path}")
    print(f"正文区间字符: {len(body)}  |  集数: {len(rows)}")
    print(f"{'集':>4} {'台词字':>6} {'台词句':>6} {'△字':>6} {'△段':>4} {'台词/△':>7} {'VO':>3} {'OS':>3} {'最长连句':>8}")
    for r in rows:
        flag = ""
        if r["dlg_chars"] == 0 or not (200 <= r["dlg_chars"] <= 400):
            flag += "  ← 台词量离群"
        if r["vo"]:
            flag += "  ← VO 违规"
        if r["os"] > 2:
            flag += "  ← OS 超限"
        if r["max_run"] > 2:
            flag += "  ← 连续发言>2(抽样判独白)"
        print(f"{r['ep']:>4} {r['dlg_chars']:>6} {r['dlg_lines']:>6} {r['tri_chars']:>6} "
              f"{r['tri_lines']:>4} {str(r['ratio']):>7} {r['vo']:>3} {r['os']:>3} {r['max_run']:>8}{flag}")

    if rows:
        n = len(rows)
        mean = sum(r["dlg_chars"] for r in rows) / n
        inband = sum(1 for r in rows if 300 <= r["dlg_chars"] <= 350)
        trips = sum(r["tri_chars"] for r in rows)
        dlgs = sum(r["dlg_chars"] for r in rows)
        print(f"\n台词字/集 均值 {mean:.0f} | 落在 300–350 的集: {inband}/{n}")
        print(f"全剧 台词 {dlgs} 字 / △ {trips} 字 = 台词/△ {dlgs / trips:.2f}" if trips else "")
        print(f"VO 合计 {sum(r['vo'] for r in rows)}（应 0） | OS 合计 {sum(r['os'] for r in rows)}")
        for r in rows:
            if r["max_run"] > 2:
                print(f"  提示: 第 {r['ep']} 集最长连续同角色发言 {r['max_run']} 句——"
                      f"关键信息段应拆成多角色一问一答（禁一人连说 3 句以上）")

    if "--json" in sys.argv:
        out = sys.argv[sys.argv.index("--json") + 1]
        json.dump(rows, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(f"\n已写出 {out}")


if __name__ == "__main__":
    main()
