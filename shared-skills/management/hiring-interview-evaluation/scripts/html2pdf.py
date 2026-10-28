# -*- coding: utf-8 -*-
"""HTML → A4 PDF（Edge/Chrome headless），并校验页数与页面尺寸。

用法:
    python html2pdf.py 输入.html 输出.pdf [png输出目录]

要点（踩过的）：
- 原生程序必须收 D:/... 正斜杠路径，MSYS 的 /d/... 不转换，会报 No such file
- 必须加 --no-pdf-header-footer，否则页眉页脚会带上文件路径和日期
- @page margin + 内容高度是页数的主因；装不下就把 h2 上加 class="pb" 做强制分页
- 中文路径没问题，不用绕到临时英文目录
"""
import os
import subprocess
import sys

BROWSERS = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
]

VERIFY_PY = r"D:\Hermes\venvs\media\Scripts\python.exe"

VERIFY_CODE = """
import os, sys
import pypdfium2 as pdfium
path = sys.argv[1]
out = sys.argv[2] if len(sys.argv) > 2 else ""
doc = pdfium.PdfDocument(path)
w, h = doc[0].get_size()
print("页数", len(doc))
print("尺寸", round(w / 72 * 25.4, 1), "x", round(h / 72 * 25.4, 1), "mm  (A4 = 210 x 297)")
if out:
    os.makedirs(out, exist_ok=True)
    for i in range(len(doc)):
        f = os.path.join(out, "p%d.png" % (i + 1))
        doc[i].render(scale=110 / 72).to_pil().save(f)
        print("  PNG", f)
"""


def find_browser():
    for p in BROWSERS:
        if os.path.exists(p):
            return p
    raise SystemExit("找不到 Edge 或 Chrome，先确认装了哪一个")


def to_pdf(src, out):
    src = os.path.abspath(src)
    out = os.path.abspath(out)
    if not os.path.exists(src):
        raise SystemExit("源文件不存在: %s" % src)
    url = "file:///" + src.replace("\\", "/")
    cmd = [
        find_browser(),
        "--headless=new",
        "--disable-gpu",
        "--no-pdf-header-footer",
        "--print-to-pdf=" + out.replace("\\", "/"),
        url,
    ]
    subprocess.run(cmd, timeout=180, check=False)
    if not os.path.exists(out):
        raise SystemExit("转换失败，没生成 PDF（看上面 Edge 的输出）")
    return out


def verify(pdf_path, png_dir=None):
    py = VERIFY_PY if os.path.exists(VERIFY_PY) else sys.executable
    args = [py, "-c", VERIFY_CODE, pdf_path]
    if png_dir:
        args.append(os.path.abspath(png_dir))
    r = subprocess.run(args, capture_output=True, text=True)
    print(r.stdout.strip() or r.stderr.strip())
    if png_dir and r.returncode == 0:
        print("→ 打开 PNG 用眼睛核一次：中文有没有乱码、题号连不连续、有没有截断")


def main():
    if len(sys.argv) < 3:
        raise SystemExit(__doc__)
    out = to_pdf(sys.argv[1], sys.argv[2])
    print("OK", out, os.path.getsize(out), "bytes")
    verify(out, sys.argv[3] if len(sys.argv) > 3 else None)


if __name__ == "__main__":
    main()
