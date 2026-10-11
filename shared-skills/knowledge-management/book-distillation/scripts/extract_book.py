#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
extract_book.py —— 图书提取器（book-distillation 技能配套）

把 PDF / EPUB / DOCX / HTML / RTF / TXT / MD 提取成「干净全文 + 元数据」，
交给 agent 按章蒸馏。设计原则：**零重依赖** —— 优先用本机已有工具，
缺的走降级链，绝不因为少一个包就整条流程停摆。

用法:
  python extract_book.py <path...> [--mode technical|text] [--out DIR]
  python extract_book.py --check              # 只打印每种格式可用的提取器，不处理文件

  <path...>  文件 / 目录 / glob（可混写、可多个）
  --mode     technical = 保留表格版式（pdftotext -layout）；text = 最快路径（默认 text）
  --out      工作目录；默认 %TEMP%/book_distill_work-<pid>

输出:
  <out>/full_text.txt   各源合并全文（每源前有 SOURCE 分隔标记）
  <out>/metadata.json   workdir + 汇总统计 + 每源 sha256/字符/词数/估算tokens/提取器/告警

退出码: 0 = 成功（允许有被跳过的坏源）  1 = 一个源都没提取出来
"""
import argparse
import glob as _glob
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path

# Windows 控制台默认 GBK，中文/符号会炸 —— 强制 UTF-8
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

SUPPORTED = {".pdf", ".epub", ".docx", ".txt", ".md", ".markdown",
             ".rst", ".adoc", ".html", ".htm", ".rtf"}

# 扫描版判定：页数够多但抽出文本极少
SCAN_MIN_CHARS = 200
SCAN_MIN_PAGES = 3


# ---------------------------------------------------------------- 能力探测
def _have(mod):
    try:
        __import__(mod)
        return True
    except Exception:
        return False


def capability_table():
    """返回 [(格式, 提取器, 是否可用, 补装命令/备注, 档位)]，从优到劣。"""
    pdftotext = shutil.which("pdftotext")
    return [
        ("pdf", "pdftotext (poppler)", bool(pdftotext), "choco install poppler", "★最好"),
        ("pdf", "pymupdf/fitz", _have("fitz"), "pip install pymupdf", "★好"),
        ("pdf", "pypdf", _have("pypdf"), "pip install pypdf", "☆兜底"),
        ("pdf", "docling (表格/公式→markdown)", _have("docling"), "pip install docling", "☆最全(慢,~1.5s/页)"),
        ("epub", "ebooklib + beautifulsoup4", _have("ebooklib") and _have("bs4"),
         "pip install ebooklib beautifulsoup4", "★好"),
        ("epub", "stdlib zipfile + bs4（内置降级）", _have("bs4"), "pip install beautifulsoup4", "☆兜底"),
        ("docx", "python-docx", _have("docx"), "pip install python-docx", "★好"),
        ("html", "beautifulsoup4", _have("bs4"), "pip install beautifulsoup4", "★好"),
        ("rtf", "stdlib 正则", True, "-", "☆兜底"),
        ("txt/md/rst/adoc", "内置直读", True, "-", "★好"),
        ("mobi/azw3", "Calibre (ebook-convert)", bool(shutil.which("ebook-convert")),
         "装 Calibre 并加入 PATH", "需外部工具"),
        ("扫描版PDF", "OCR（本工具不做，先 OCR 再喂进来）", bool(shutil.which("ocrmypdf")),
         "pip install ocrmypdf + tesseract", "前置步骤"),
    ]


def print_check():
    print("格式".ljust(16), "提取器".ljust(38), "状态".ljust(6), "补装/备注")
    print("-" * 100)
    for fmt, eng, ok, hint, tier in capability_table():
        print(f"{fmt.ljust(16)}{eng.ljust(38)}{('✅可用' if ok else '❌缺失').ljust(6)}{tier}  {hint}")
    print("\n提示：本工具只读文本层。扫描版 PDF / 图表内文字提取不出来 —— 先跑 `ocrmypdf in.pdf out.pdf` 再喂进来。")


# ---------------------------------------------------------------- 各格式提取
def _epub_via_ebooklib(path):
    import ebooklib
    from ebooklib import epub
    from bs4 import BeautifulSoup
    book = epub.read_epub(str(path))
    parts = []
    for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
        soup = BeautifulSoup(item.get_content(), "html.parser")
        t = soup.get_text("\n")
        t = re.sub(r"\n{3,}", "\n\n", t).strip()
        if t:
            parts.append(t)
    return "\n\n".join(parts), "ebooklib"


def _epub_via_zip(path):
    from bs4 import BeautifulSoup
    with zipfile.ZipFile(str(path)) as z:
        names = sorted(n for n in z.namelist()
                       if n.lower().endswith((".xhtml", ".html", ".htm")))
        parts = []
        for n in names:
            soup = BeautifulSoup(z.read(n), "html.parser")
            t = re.sub(r"\n{3,}", "\n\n", soup.get_text("\n")).strip()
            if t:
                parts.append(t)
    return "\n\n".join(parts), "zipfile+bs4"


def extract_pdf(path, mode):
    pt = shutil.which("pdftotext")
    if pt:
        cmd = [pt]
        if mode == "technical":
            cmd.append("-layout")
        cmd += ["-enc", "UTF-8", str(path), "-"]
        r = subprocess.run(cmd, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=900)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout, "pdftotext"
    if _have("fitz"):
        import fitz
        doc = fitz.open(str(path))
        txt = "\n".join(page.get_text() for page in doc)
        if txt.strip():
            return txt, "pymupdf"
    if _have("pypdf"):
        from pypdf import PdfReader
        reader = PdfReader(str(path))
        txt = "\n".join((pg.extract_text() or "") for pg in reader.pages)
        if txt.strip():
            return txt, "pypdf"
    raise RuntimeError("没有可用的 PDF 提取器（装 poppler 或 pypdf）")


def extract_epub(path):
    if _have("ebooklib") and _have("bs4"):
        try:
            return _epub_via_ebooklib(path)
        except Exception:
            pass
    if _have("bs4"):
        return _epub_via_zip(path)
    raise RuntimeError("EPUB 提取需要 beautifulsoup4（pip install beautifulsoup4）")


def extract_docx(path):
    import docx
    d = docx.Document(str(path))
    parts = [p.text for p in d.paragraphs]
    for t in d.tables:                     # 表格常是干货所在，逐行保留
        for row in t.rows:
            cells = [c.text.strip() for c in row.cells]
            if any(cells):
                parts.append(" | ".join(cells))
    return "\n".join(parts), "python-docx"


def extract_html(path):
    from bs4 import BeautifulSoup
    raw = Path(path).read_text(encoding="utf-8", errors="replace")
    soup = BeautifulSoup(raw, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()
    return soup.get_text("\n"), "beautifulsoup4"


def extract_rtf(path):
    raw = Path(path).read_text(encoding="utf-8", errors="replace")
    raw = re.sub(r"\\'([0-9a-fA-F]{2})", lambda m: chr(int(m.group(1), 16)), raw)
    raw = re.sub(r"\\[a-zA-Z]+-?\d* ?", " ", raw)     # 控制字
    raw = raw.replace("{", " ").replace("}", " ")
    return re.sub(r"\n{3,}", "\n\n", raw), "stdlib-regex"


def extract_text(path):
    return Path(path).read_text(encoding="utf-8", errors="replace"), "builtin"


EXTRACTORS = {
    ".pdf": extract_pdf, ".epub": extract_epub, ".docx": extract_docx,
    ".html": extract_html, ".htm": extract_html, ".rtf": extract_rtf,
    ".txt": extract_text, ".md": extract_text, ".markdown": extract_text,
    ".rst": extract_text, ".adoc": extract_text,
}


# ---------------------------------------------------------------- 工具函数
def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def count_tokens_est(text):
    """有 tiktoken 就精确算；没有就按 词数/0.75 估（与 book-to-skill 同常数）。"""
    try:
        import tiktoken
        enc = tiktoken.get_encoding("cl100k_base")
        return len(enc.encode(text)), "tiktoken/cl100k_base"
    except Exception:
        words = len(re.findall(r"\S+", text))
        return int(words / 0.75), "words/0.75-est"


def expand_inputs(paths):
    """文件 / 目录 / glob 展开成实际文件列表（去重、按名排序）。"""
    out = []
    for p in paths:
        cand = Path(p)
        if cand.is_dir():
            out += [f for f in sorted(cand.rglob("*")) if f.is_file()]
        elif cand.is_file():
            out.append(cand)
        else:
            hits = [Path(x) for x in _glob.glob(p, recursive=True)]
            out += [h for h in hits if h.is_file()]
    seen, uniq = set(), []
    for f in out:
        key = str(f.resolve())
        if key not in seen:
            seen.add(key)
            uniq.append(f)
    return uniq


# ---------------------------------------------------------------- 主流程
def main():
    ap = argparse.ArgumentParser(description="图书提取器（book-distillation 配套）")
    ap.add_argument("paths", nargs="*", help="文件/目录/glob，可多个")
    ap.add_argument("--mode", choices=["technical", "text"], default="text")
    ap.add_argument("--out", default=None)
    ap.add_argument("--check", action="store_true", help="只打印提取器可用性")
    args = ap.parse_args()

    if args.check:
        print_check()
        return 0
    if not args.paths:
        ap.error("至少给一个文件/目录/glob（或用 --check 看环境）")

    files = expand_inputs(args.paths)
    if not files:
        print("❌ 没有匹配到任何文件", file=sys.stderr)
        return 1

    workdir = Path(args.out) if args.out else Path(tempfile.gettempdir()) / f"book_distill_work-{os.getpid()}"
    workdir.mkdir(parents=True, exist_ok=True)

    chunks, sources, skipped = [], [], []
    for f in files:
        ext = f.suffix.lower()
        if ext not in SUPPORTED:
            skipped.append((str(f), f"不支持的格式 {ext}"))
            print(f"⚠️  跳过（格式不支持）: {f.name}")
            continue
        try:
            text, engine = EXTRACTORS[ext](f, args.mode) if ext == ".pdf" else EXTRACTORS[ext](f)
        except Exception as e:
            skipped.append((str(f), str(e)))
            print(f"⚠️  跳过（提取失败）: {f.name} —— {e}")
            continue

        chars = len(text)
        words = len(re.findall(r"\S+", text))
        tokens, method = count_tokens_est(text)
        pages = text.count("\f") + 1 if ext == ".pdf" else None
        warn = None
        if ext == ".pdf" and pages and pages >= SCAN_MIN_PAGES and chars < SCAN_MIN_CHARS:
            warn = ("疑似扫描版/图片型 PDF（文本层几乎为空）——先跑 "
                    "`ocrmypdf in.pdf out.pdf` 再喂进来")
            print(f"⚠️  {f.name}: {warn}")

        chunks.append(f"===== SOURCE: {f.name} =====\n{text.strip()}\n")
        sources.append({
            "file": f.name, "path": str(f), "format": ext.lstrip("."),
            "extractor": engine, "sha256": sha256_of(f),
            "chars": chars, "words": words, "tokens_est": tokens,
            "pages": pages, "warning": warn,
        })
        print(f"✅ {f.name}: {chars} 字符 / ~{tokens} tokens / {engine}"
              + (f" / {pages} 页" if pages else ""))

    if not chunks:
        print("❌ 一个源都没提取成功", file=sys.stderr)
        return 1

    full = "\n\n".join(chunks)
    text_path = workdir / "full_text.txt"
    text_path.write_text(full, encoding="utf-8")

    total_tokens, method = count_tokens_est(full)
    meta = {
        "created": datetime.now().isoformat(timespec="seconds"),
        "mode": args.mode,
        "workdir": str(workdir),
        "total_sources": len(sources),
        "total_chars": len(full),
        "total_words": len(re.findall(r"\S+", full)),
        "total_tokens_est": total_tokens,
        "token_method": method,
        "sources": sources,
        "skipped": skipped,
    }
    meta_path = workdir / "metadata.json"
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    print("\n" + "=" * 60)
    print(f"Workdir -> {workdir}")
    print(f"Text    -> {text_path}")
    print(f"Meta    -> {meta_path}")
    print(f"合计: {len(sources)} 源 / {meta['total_words']} 词 / ~{total_tokens} tokens ({method})")
    if skipped:
        print(f"跳过 {len(skipped)} 个源（见 metadata.json 的 skipped）")
    if total_tokens > 50_000:
        print("💡 本书 >50k tokens：蒸馏时别整本读入 —— 用 grep -n 找章标题行号 + "
              "sed -n 'a,bp' / read_file(offset,limit) 只切要用的章。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
