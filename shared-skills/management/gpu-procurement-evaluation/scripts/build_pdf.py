# -*- coding: utf-8 -*-
"""HTML → A4 中文 PDF（Playwright chromium），并导出逐页 PNG 供目检。

为什么用这条路：本机没有 Word/LibreOffice，reportlab 未装且中文字体麻烦；
Playwright + chromium 直接吃系统字体（微软雅黑），表格/分页/页码都好控。

用法：
    python build_pdf.py 计划书.html                       # 输出同名 .pdf
    python build_pdf.py 计划书.html 计划书_2026-11-20.pdf  # 指定输出
    python build_pdf.py 计划书.html --png D:\\tmp\\pv       # 同时导出每页 PNG（目检用）
    python build_pdf.py 计划书.html --png D:\\tmp\\pv --dpi 85

依赖：playwright（pip 装过一次即可）、pymupdf（仅 --png 时需要）
"""
import os
import pathlib
import sys


FOOTER = (
    "<div style='font-size:8pt;color:#888;width:100%;"
    "font-family:Microsoft YaHei;text-align:center;'>"
    "第 <span class='pageNumber'></span> 页 / 共 <span class='totalPages'></span> 页</div>"
)


def build(src_html: str, out_pdf: str = None, png_dir: str = None, dpi: int = 85) -> str:
    from playwright.sync_api import sync_playwright

    src = pathlib.Path(src_html).resolve()
    if not src.exists():
        raise SystemExit(f"找不到 HTML：{src}")
    out = pathlib.Path(out_pdf).resolve() if out_pdf else src.with_suffix(".pdf")

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(src.as_uri())
        page.emulate_media(media="print")      # 关键：走 @media print 的 CSS
        page.wait_for_timeout(1000)            # 等字体/图片就位
        page.pdf(
            path=str(out),
            format="A4",
            print_background=True,
            margin={"top": "18mm", "bottom": "16mm", "left": "16mm", "right": "16mm"},
            display_header_footer=True,
            header_template="<div></div>",
            footer_template=FOOTER,
        )
        browser.close()

    print(f"PDF OK {out} {os.path.getsize(out)} bytes")

    if png_dir:
        import pymupdf  # pip install pymupdf

        pathlib.Path(png_dir).mkdir(parents=True, exist_ok=True)
        doc = pymupdf.open(str(out))
        for i, pg in enumerate(doc, 1):
            fp = os.path.join(png_dir, f"p{i}.png")
            pg.get_pixmap(dpi=dpi).save(fp)
            print("png", fp)
        print(f"共 {doc.page_count} 页")

    return str(out)


def main(argv):
    if len(argv) < 2:
        raise SystemExit(__doc__)
    src = None
    out = None
    png = None
    dpi = 85
    i = 1
    while i < len(argv):
        a = argv[i]
        if a == "--png":
            i += 1
            png = argv[i]
        elif a == "--dpi":
            i += 1
            dpi = int(argv[i])
        elif src is None:
            src = a
        elif out is None:
            out = a
        i += 1
    build(src, out, png, dpi)


if __name__ == "__main__":
    main(sys.argv)
