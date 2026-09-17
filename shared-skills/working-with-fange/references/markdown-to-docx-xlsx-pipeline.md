# 交付件生产线：Markdown → Word / Excel（本机实测 2026-09-13）

凡哥的文本类交付默认落 `D:\Documents\我的文档\<项目>\`，且**同时给 Word 版**（他要能打开、能转发给同事/领导）。

## 环境事实（本机实测）

- **没有 pandoc**（`which pandoc` → 空）。不要指望 `pandoc md -o docx`。
- **有 python-docx 1.2.0**（`python -c "import docx"` 正常）。
- bundled `docx` / `xlsx` 技能自带脚本（**技能本身受保护，不要改；直接调用即可**）：
  - `D:\Hermes\skills\productivity\docx\scripts\docx_create.py spec.json out.docx`（JSON spec 生成 docx）
  - `D:\Hermes\skills\productivity\docx\scripts\docx_read.py out.docx --structure`（校验大纲/块数）
  - `D:\Hermes\skills\productivity\docx\scripts\docx_validate.py out.docx`（返回 `{"ok":true,"issues":[]}`）
  - `D:\Hermes\skills\productivity\xlsx\scripts\xlsx_create.py spec.json out.xlsx`
  - `D:\Hermes\skills\productivity\xlsx\scripts\xlsx_read.py out.xlsx --sheets | --json --sheet <名>`

## 套路（一步一次，稳）

1. **先写 Markdown**（人话版正文，可以用表格/标题/列表/引用）——Markdown 是源，Word 是派生物。
2. **写一个小解析器**把 Markdown 转成 docx_create.py 的 JSON spec，然后调脚本。解析器覆盖子集即可：
   `#~###### 标题`、段落、`-/*` 列表、`1.` 编号、`| 表格 |`、`> 引用`、``` 围栏、`---` 分隔线；行内 `**加粗**` 拆成 runs。
   （本机现成脚本：`%LOCALAPPDATA%\Temp\md2docx.py`，2026-09-13 实测产出 162 块/5 表正常。若已丢失，按上面子集重写，约 60 行。）
3. **调 docx_create.py**，再用 `docx_read.py --structure` + `docx_validate.py` 校验（块数与大纲对得上才算成）。
4. **Excel 直接写 spec JSON**（不必经过 Markdown）。常用键：`sheets[].rows`（标量或 cell 对象）、`column_widths`、`freeze_panes`、`merges`、`validations`（`{"range":"B2:B20","type":"list","formula1":"\"小何,小吴\""}` 做下拉）、`tables`。多页签一次生成（本例 4 页签：项目进展/考核表×2/日志）。
5. **回报路径 + 用 `MEDIA:` 交付**——⚠️ **贴路径前必须真实写盘**（见 `working-with-fange`「声称产出前，文件必须真的存在」）。

## 踩过的坑

- **中文文件名**在 spec/路径里直接写没问题，但 shell 里要整体加引号：`python md2docx.py "D:/Documents/我的文档/x.md" ...`。
- **本机 MSYS 不转换路径**：给原生 python 传 `D:/...` 正斜杠写法（不要 `/d/...`）。
- spec 里表格每行**列数要一致**（不足要补空串），否则生成的表会错位。
- `patch` 工具在 CRLF 文件里匹配多行 `old_string` 会失败——**DASHBOARD.md 之类 CRLF 文件做多行替换时，用单行唯一锚点**，或用 `execute_code` 里连续调用 `patch()`。
