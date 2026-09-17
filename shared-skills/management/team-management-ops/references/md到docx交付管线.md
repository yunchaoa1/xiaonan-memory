# md → docx 交付管线（本会话实测可用）

给凡哥/HR 交 Word 时的固定做法。**Markdown 先写**（好改、好 diff、可 git），要交人时再转 docx。

## 管线

```
① 写 .md（正文）
② md2docx 转换器：md → docx_create.py 的 JSON spec
③ python D:/Hermes/skills/productivity/docx/scripts/docx_create.py spec.json out.docx
④ 验证：python …/docx_read.py out.docx --structure   （打印结构，确认标题/表格/段落都在）
```

转换器（`md2docx.py`）自己写十来行就够：逐行分段 → 识别 `#`~`######` 标题 / 表格（连续 `|` 行，跳过分隔行、按表头列数补齐或截断）/ `-` `*` 无序 / `1.` 有序 / `>` 引用 / ``` 围栏 / `---` 横线 / 普通段落，`**粗体**` 拆成 runs。**spec 里的表头/单元格是纯字符串，先去掉 `**` 等 markdown 标记。**

⚠️ 转换器写在临时目录（`$LOCALAPPDATA/Temp/md2docx.py`）**会被清掉**——下次要重新生成；别把它当永久资产，也**不要**把未验证的版本塞进技能目录当脚本。

## spec 关键字段（docx_create.py）

- 页级：`page`（页边距等）
- 块级：`blocks` —— `heading`（含 level）/ `paragraph`（`text` 或 `runs`）/ `bullet_list` / `numbered_list` / `table`（表头行 + 数据行）/ `image` / `toc` / `page_break`
- 本会话实测：一份 ~330 行的 md → `{"ok": true, "blocks": 162}`、5 张表、大纲正确。

## 同族：xlsx 的 spec（`xlsx_create.py`）

`sheets[]` 下每条：`name` / `column_widths` / `row_heights`（按行号字符串）/ `freeze_panes` / `merges`（`"A1:C1": "标题"`）/ `rows`（二维数组，单元格对象 `{value, bold, fill, align, wrap, border, format}`）/ `validations`。
**数字格式的键是 `format`（不是 `fmt`）**；百分比存小数 + `format: "0%"`（存 20 会显示成 2000%）。公式直接写在 `value` 里（`"=SUM(B4:B7)"`）。

## 交付纪律

- 交付目录 `D:\Documents\我的文档\CTO攻略\`，**文件名带 v 号与月份**；**换版即删旧版**（凡哥最怕发错版本）。
- 交付时在聊天里**同时列清：改了哪几处 / 哪几处是建议 / 保留了什么**。
- 用 `MEDIA:<绝对路径>` 让人能直接点开；**说过的文件必须先真的生成**（本会话犯过：嘴上说"已重做一版"但文件没写出来，被凡哥追问路径时才发现——**先写文件，再发链接**）。
