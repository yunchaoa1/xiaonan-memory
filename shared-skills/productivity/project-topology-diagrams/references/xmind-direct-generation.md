# .xmind 直出模块与校验配方（2026-10-07 打通 · 2026-10-10 抽成公共模块）

## 一、公共模块（任何新脑图都走它，别再复制粘贴写法）

`D:\Hermes\scripts\xmind_writer.py`

| 函数 | 作用 |
|---|---|
| `write_xmind(tree, out_path)` | 直出 `.xmind`（zip：content.json / metadata.json / manifest.json），返回主题数 |
| `read_xmind_titles(path)` | 回读校验：`(主题数, 全部标题列表, 中心标题)` |
| `tree_to_md(tree)` | 同一棵树 → 人可读 Markdown（给凡哥看的镜像版） |

- 节点格式 = **`(标题, [子节点…])` 二元组**
  ⚠ 与 `project_tree_data.py` 的 **`(标签, 类型, 子节点)`** 三元组**不是一个格式**——混用就会出现 "done / prog" 当标题的废图（已踩两次）。
- 新专题做法：新建 `gen_mindmap_<主题>.py`，自带 `TREE`，`import xmind_writer` 即可（实例：`gen_mindmap_yuanqi.py` → 元气森林平台脑图 60 主题）。
- 主树（技术部项目思维导图）用 `gen_xmind.py`（它读 `project_tree_data.py`，自带一份等效写法）。

## 二、格式（照 XMind 26.x 实测样例）

```json
// content.json
[{"id": "<sheet_id>", "revisionId": "<uuid>", "class": "sheet",
  "rootTopic": {"id": "<uuid>", "class": "topic", "title": "中心主题",
    "titleUnedited": false, "structureClass": "org.xmind.ui.map.clockwise",
    "children": {"attached": [
      {"id": "<uuid>", "class": "topic", "title": "分支",
       "titleUnedited": false, "children": {"attached": [ ... ]}}
    ]}}}]
```

- `metadata.json`：`{"dataStructureVersion": "3", "creator": {"name": "Vana", "version": "26.05.01107"}, "activeSheetId": "<sheet_id>", "layoutEngineVersion": "5"}`
- `manifest.json`：`{"file-entries": {"content.json": {}, "metadata.json": {}}}`
- 节点只需 `id` + `title`；**样式/配色/布局由 XMind 打开时自动套**（7–8 KB 文件渲染正常）。

## 三、校验配方（每次生成后必跑，3 条）

1. **回读主题数 = 预期节点数**（`read_xmind_titles`）。
2. **所有 title 都是 str** —— 踩过：`_topic(label, kids)` 与 `_topic(node)` 签名不匹配、推导式又把节点元组当标题 → **52/60 个标题变成 JSON 数组**，XMind 里显示异常。校验片段：
   ```python
   n, ts, c = read_xmind_titles(path)
   bad = [t for t in ts if not isinstance(t, str)]
   assert not bad, bad[:5]
   ```
3. **.md 里不得出现整行的 `- done` / `- prog` / `- none` / `- block`**（出现 = label/kind 写反了）。

## 四、实测记录

- 2026-10-10 元气森林平台脑图（60 主题 / 7 分支）由本模块直出；同日晚「技术部项目思维导图」按更新后的树重出 **109 主题**（98/102 主题的前几版已在 XMind 里打开验证渲染正常 ✓）。
- ⚠ 让 XMind 用文件参数打开 **.xmind** 时，若实例中已开着别的文档，实测**可能不弹新窗口**（.md 导入则正常）→ 直出文件的验收**以回读 content.json 为准**；要目视确认就请凡哥双击一次。

## 五、其他注意

- 生成器里的日期/口径算标签：**写日期前先跑 `date` 核实**（本会话踩过：中心里写「2026-10-08 口径」，实际是 10-10，只能重生成）。
- 免费版 XMind 的「升级」内嵌面板会挡 Ctrl+S —— 直出路线完全不受影响（这正是主推直出的原因之一）。
