# -*- coding: utf-8 -*-
"""HTML → A4 PDF（Edge 无头）+ 页数校验 + 渲图自查

用法：
    python build_interview_pdf.py "D:/Documents/我的文档/招聘/xxx.html"
    python build_interview_pdf.py "D:/.../xxx.html" --no-render   # 只出 PDF + 数页

想批量出两份（初面/复试），在下面 BATCH 里列路径，或自己写循环调 to_pdf()。

依赖（装在独立 venv，别往 Hermes 主 venv 塞带依赖树的包）：
    D:\\Hermes\\venvs\\media\\Scripts\\python.exe -m pip install pypdf pypdfium2 pillow
    ⚠ pypdfium2 的 render().to_pil() 需要 pillow，缺了会报错（2026-10-28 实测）。

实测（2026-10-28，25.5 分钟面试录音同批次的面试清单）：
    10 页内容压成 2 页 A4，Edge 出片 ~1.5 秒，文件 260-271 KB。
"""
import os
import subprocess
import sys

EDGE_CANDIDATES = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
]

# ── 打印 CSS 要点（写进 HTML 的 <style>，别靠浏览器默认）────────────────
# @page { size: A4; margin: 14mm 15mm 12mm 15mm; }
# body  { font-family: "Microsoft YaHei","微软雅黑",sans-serif; font-size: 10.5pt; line-height: 1.62; }
# .q    { page-break-inside: avoid; break-inside: avoid; }   /* 一题不被劈开 */
# h2.pb { page-break-before: always; break-before: page; }   /* 想从某处分页就挂这个类 */
# 一页装不下时：宁可「故意分两页」，也别让第 2 页只剩两行。


def find_edge():
    for p in EDGE_CANDIDATES:
        if os.path.exists(p):
            return p
    raise SystemExit("找不到 Edge/Chrome，改 EDGE_CANDIDATES")


def to_pdf(html_path):
    """HTML → 同名 PDF。native 程序吃原生路径：一律 D:/ 正斜杠，不能写 /d/。"""
    html_path = os.path.abspath(html_path)
    pdf_path = os.path.splitext(html_path)[0] + ".pdf"
    subprocess.run(
        [
            find_edge(),
            "--headless=new",
            "--disable-gpu",
            "--no-pdf-header-footer",          # 去掉页眉页脚（日期/URL）
            "--print-to-pdf=" + pdf_path.replace("\\", "/"),
            "file:///" + html_path.replace("\\", "/"),
        ],
        check=True,
        capture_output=True,
    )
    return pdf_path


def verify(pdf_path, do_render=True):
    """数页 + 逐页渲 PNG。渲图后用 vision 自查：乱码 / 截断 / 压边 / 留白。"""
    from pypdf import PdfReader

    r = PdfReader(pdf_path)
    n = len(r.pages)
    b = r.pages[0].mediabox
    w_mm = round(float(b.width) / 72 * 25.4, 1)
    h_mm = round(float(b.height) / 72 * 25.4, 1)
    print(f"页数 {n} · 页面 {w_mm}x{h_mm}mm（A4=210x297）· {os.path.getsize(pdf_path)} bytes")
    if not do_render:
        return n
    try:
        import pypdfium2 as pdfium
    except ImportError:
        print("（跳过渲图：没装 pypdfium2）")
        return n
    pdf = pdfium.PdfDocument(pdf_path)
    base = os.path.splitext(pdf_path)[0]
    for i in range(len(pdf)):
        img = pdf[i].render(scale=110 / 72).to_pil()   # 110dpi 够看清中文
        out = f"{base}_p{i + 1}.png"
        img.save(out)
        print("  渲图", out)
    return n


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    do_render = "--no-render" not in sys.argv
    if not args:
        raise SystemExit(__doc__)
    for h in args:
        pdf = to_pdf(h)
        verify(pdf, do_render)
