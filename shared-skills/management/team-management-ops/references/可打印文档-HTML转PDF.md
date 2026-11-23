# 可打印文档：HTML → A4 PDF（中文 / 给凡哥打印用）

> 场景：凡哥说「帮我生成 PDF，我要打印」。本次产物＝面试题单（12 题、两页 A4）。
> 适用：清单 / 题单 / 一页纸 / 检查表 / 表格式方案 —— 要**排版好看且能打印**的中文文档。

**不要用 PDF 工具库直接画（reportlab 那类）做这种带层级的表格式文档** —— 排版成本高、中文要手配字体。**用 HTML + 无头浏览器打印**，CSS 控制一切，改内容只改 HTML。

---

## 一、写 HTML（要点）

```css
@page { size: A4; margin: 14mm 15mm 12mm 15mm; }   /* 页边距写这里，别用 body padding */
body { font-family: "Microsoft YaHei", "SimSun", sans-serif; font-size: 10.5pt; line-height: 1.6; color:#111; }
```

- **中文字体**：`Microsoft YaHei`（微软雅黑）本机一定有；正文字号 **10～10.5pt** 是打印可读下限，再小就不适合拿在手上看。
- **层次靠左边色条 + 缩进**，不靠字号堆叠：每条内容一个 `border-left: 3px solid <色>`，答法行 `margin-left: 20px`。
- **三档判断用 ○ / △ / ×**，不用 emoji —— emoji 在无头打印里可能掉字或变彩色方块。
- **别让小块被切到下一页**：条目容器加 `break-inside: avoid;`。

## 二、转 PDF（Windows · Edge 或 Chrome 都行）

```bash
"/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe" \
  --headless=new --disable-gpu --no-pdf-header-footer \
  --print-to-pdf="D:/Documents/我的文档/02_团队/招聘/xxx.pdf" \
  "file:///D:/Documents/我的文档/02_团队/招聘/xxx.html"
```

- **路径一律用 `C:/…`、`D:/…` 正斜杠原生路径**；HTML 用 `file:///` 前缀。**中文路径实测可用**，不用挪到临时英文目录。
- `--no-pdf-header-footer` 去掉页眉页脚（否则会印上日期和文件地址）。
- 控制台会刷一堆无关报错（QQBrowser importer / EDGE_IDENTITY / task_provider）—— **只看 `NNNNN bytes written to file …` 这一行就算成功**。
- 别把命令接在 `| tail` 后面判 exit code，那是管道的返回码，会误判。

## 三、验证（三件套，必须做）

```bash
# 1) 页数 + 尺寸
"/d/Hermes/venvs/media/Scripts/python.exe" -c "
from pypdf import PdfReader
r=PdfReader('xxx.pdf'); b=r.pages[0].mediabox
print('页数',len(r.pages),'尺寸',round(float(b.width)/72*25.4,1),'x',round(float(b.height)/72*25.4,1),'mm')
"
# 2) 渲染成图看排版
"/d/Hermes/venvs/media/Scripts/python.exe" -c "
import pypdfium2 as pdfium
pdf=pdfium.PdfDocument('xxx.pdf')
for i in range(len(pdf)):
    pdf[i].render(scale=115/72).to_pil().save(f'_pv{i+1}.png')
"
# 3) vision_analyze 逐页看：中文有没有方块/乱码、层级、色条缩进、有没有截断压边
```

- 依赖装在 **`D:\Hermes\venvs\media`** 这个独立 venv（`pypdf` / `pypdfium2` / `pillow`），**不要往 Hermes 主 venv 装**。
- 验完把 `_pv*.png` 删掉，别留中间产物在交付目录。

## 四、页面溢出怎么办（本次实测）

- 症状：A4 页数比预期多一页，最后几行被挤到第 2 页。
- **不要一味缩字号**（缩到 9pt 以下，凡哥拿在手上看着累 → 会被要求重排）。
- **正解：按大节强制分页**，让第 2 页从一个干净的位置开始：

  ```css
  h2.pb { page-break-before: always; break-before: page; margin-top: 0; }
  ```
  `<h2 class="pb">三、…</h2>`

- 本次的分页结果是：**第 1 页＝验真假 + 制衡能力（前半场用），第 2 页＝深度追问 + 收尾（后半程用）** —— 分页逻辑和服务于「他面试时怎么翻」对齐，不只是为了凑页数。
- 页面尺寸核对：A4 = 210 × 297 mm（PDF 里约 595 × 842 pt）。

## 五、交付话术

报**完整绝对路径**（凡哥铁律），并交代三件事：
1. 几页、每页放什么（他能预判怎么翻）
2. 打印设置：**A4 / 缩放 100% /「实际大小」**，别选「适应页面」
3. 源文件路径也留下（「要改直接说，我改完重导」）

---

## 六、路线 B：Playwright 渲染（2026-11-23 实测 · 采购计划书 8 页 ＋ 周会要点单 1 页）

本机没 Edge 路径依赖、也没 pypdf 时走这条，控制更细（`@page` 全部生效）：

```python
from playwright.sync_api import sync_playwright
import pathlib, pymupdf
src = pathlib.Path("xxx.html").resolve()
out = pathlib.Path("xxx.pdf").resolve()
with sync_playwright() as pw:
    b = pw.chromium.launch(); pg = b.new_page()
    pg.goto(src.as_uri())            # 用 as_uri()，别手拼 file:///
    pg.wait_for_timeout(800)
    pg.pdf(path=str(out), format="A4", print_background=True,
           margin={"top":"14mm","bottom":"12mm","left":"15mm","right":"15mm"})
    b.close()
d = pymupdf.open(str(out)); print("页数", d.page_count)
```

**逐页目检（比 pypdfium2 更省事，主 venv 装了 pymupdf 就够）**：

```python
for i, page in enumerate(d):
    page.get_pixmap(dpi=85).save(rf"D:\Hermes\cache\pdf_pv\p{i+1}.png")
```
→ 再 `vision_analyze` 一张张看：**中文有没有方块／文字有没有压边／表格有没有折行／有没有孤立标题**。
（中间图放 cache，别丢在交付目录。）

### 调到「正好 N 页」的实操循环（本次 8 页定稿用了 5 轮）

**一次只动两个变量**，每轮重渲染 + 数页数，别整段重排：

| 想要的效果 | 动哪里 |
|---|---|
| 少 1 页（末页只溢出 1–2 行） | 先动 `.foot`/末段的 `margin`、`padding`；再动正文 `font-size` **0.2pt**（10.6 → 10.4）、`line-height` 0.08（1.7 → 1.62） |
| 多填空、字更好读 | 优先放大 `.say`/要点块的字号与 `padding`，正文少动 |
| 页数还是一样 | **看第 2 页到底溢出了什么**（`pymupdf` 取 `d[1].get_text()`），往往只是一行页脚 —— 别去动正文 |

### 四个排版坑（本机实测，逐条踩过）

1. **孤立标题**：「六、采购方案」只剩标题在页底，内容全翻到下一页 → `h3{page-break-after:avoid}` ＋ 内容块 `page-break-inside:avoid`；章节开头要换页就显式 `class="pb"`。
2. **表格数值列折行**：`450 W` 被拆成两行、`CUDA 核心` 表头被拆字 → 给该列**显式列宽 + `white-space:nowrap`**；长文本列保持 `normal`。列宽总和别超 100%。
3. **页底大片空白**：某个大块 `page-break-inside:avoid` 被整体推到下一页 → 要么接受（章节结束的留白），要么把该块前面的小节拆出来填空；**别用缩字号去硬塞**。
4. **错字要逐页看才发现**：本次封面「报价以洽当日为准」漏了「谈」字——**只有渲染成图看出来**，纯 `pdftotext` 抽查容易漏。
