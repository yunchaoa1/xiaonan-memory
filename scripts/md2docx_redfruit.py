# -*- coding: utf-8 -*-
"""红果版剧本包 md → 领导版 Word 转换。
只取正文（## 3. 集剧本正文 起），跳过工艺头部；
红果格式排版：集标题=Heading1、三要素=正文加粗前缀、
场景行=加粗、人物行=斜体、△动作=正文、台词=正文。
用法: python md2docx_redfruit.py <in.md> <out.docx> <卷标题>
"""
import re, sys
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn

def main():
    in_md, out_docx, vol_title = sys.argv[1], sys.argv[2], sys.argv[3]
    text = open(in_md, encoding="utf-8").read()
    # 只保留正文：从 "## 3. 集剧本正文" 起，到下一个 "## N." 工艺章节前
    m = re.search(r"^#{2,3}\s*[3三][\.、]\s*集剧本正文", text, re.M)
    if not m:
        m = re.search(r"^#{3}\s*第\s*\d+\s*集", text, re.M)
    if not m:
        print("ERROR: 找不到正文起点"); sys.exit(1)
    body = text[m.start():]
    # 截到下一个 "## N."（工艺尾部：人物表/道具流/自评等）
    m2 = re.search(r"^##\s*[456789]\s*[\.、]", body, re.M)
    if m2:
        body = body[:m2.start()]

    doc = Document()
    # 全局字体：中文正文用宋体/雅黑 12pt
    style = doc.styles["Normal"]
    style.font.name = "Times New Roman"
    style.font.size = Pt(12)
    style.element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")

    # 封面
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(vol_title); r.bold = True; r.font.size = Pt(26)
    p2 = doc.add_paragraph(); p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r2 = p2.add_run("红果短剧集规格剧本（改编自《十二时辰》小说）")
    r2.font.size = Pt(14); r2.font.color.rgb = RGBColor(0x66, 0x66, 0x66)
    doc.add_paragraph()

    lines = body.split("\n")
    i = 0
    while i < len(lines):
        ln = lines[i].rstrip()
        if not ln.strip():
            i += 1; continue
        # 集标题 ### 第 N 集 ...
        if ln.startswith("###") or re.match(r"^第\s*\d+\s*集", ln.strip()):
            t = ln.lstrip("#").strip()
            h = doc.add_heading(t, level=1)
            for rn in h.runs: rn.font.name = "Times New Roman"; rn.font.size = Pt(16)
            i += 1; continue
        # 分隔线/正文起点标题
        if ln.strip() in ("---", "--"):
            i += 1; continue
        if re.match(r"^#{2,3}\s*[3三][\.、]\s*集剧本正文", ln):
            i += 1; continue
        # 其他标题
        if ln.startswith("#"):
            t = ln.lstrip("#").strip()
            pp = doc.add_paragraph(); rr = pp.add_run(t); rr.bold = True
            rr.font.size = Pt(14)
            i += 1; continue
        # 三要素行 【人物线】...
        if ln.startswith("【"):
            pp = doc.add_paragraph()
            segs = re.split(r"(【[^】]+】)", ln)
            for s2 in segs:
                if not s2: continue
                rr = pp.add_run(s2)
                if s2.startswith("【"): rr.bold = True
                rr.font.size = Pt(11)
                rr.font.color.rgb = RGBColor(0x40, 0x40, 0x40)
            pp.paragraph_format.space_after = Pt(4)
            i += 1; continue
        # 表格行（集编排登记等，正文后一般无）跳过
        if ln.startswith("|"):
            i += 1; continue
        # 场景行 1-1 日/外/...
        if re.match(r"^-\s*\d+\s*-\s*\d+", ln) or re.match(r"^\d+\s*-\s*\d+", ln):
            t = ln.lstrip("-").strip()
            pp = doc.add_paragraph(); rr = pp.add_run(t)
            rr.bold = True; rr.font.size = Pt(12)
            pp.paragraph_format.space_before = Pt(10)
            i += 1; continue
        # 人物行
        if re.match(r"^-?\s*人物[:：]", ln):
            t = ln.lstrip("-").strip()
            pp = doc.add_paragraph(); rr = pp.add_run(t)
            rr.italic = True; rr.font.size = Pt(11)
            i += 1; continue
        # 字幕/音效等括号行
        if re.match(r"^-?\s*[【（(]", ln) or "字幕" in ln[:6] or ln.strip().startswith("字幕"):
            t = ln.lstrip("-").strip()
            pp = doc.add_paragraph()
            rr = pp.add_run(t); rr.font.size = Pt(11)
            rr.font.color.rgb = RGBColor(0x50, 0x50, 0x50)
            pp.alignment = WD_ALIGN_PARAGRAPH.CENTER
            i += 1; continue
        # 普通行：△动作 / 台词
        if ln == "---" or ln == "--":
            i += 1; continue
        if ln.startswith("-"):
            ln = ln[1:].strip()
        if ln in ("---", "--") or ln == "":
            if ln: i += 1
            continue
        pp = doc.add_paragraph()
        rr = pp.add_run(ln)
        rr.font.size = Pt(12)
        pp.paragraph_format.line_spacing = 1.4
        i += 1

    doc.save(out_docx)
    print(f"OK -> {out_docx}")

if __name__ == "__main__":
    main()
