# ComfyUI UI 格式工作流编辑（改连线 / 加节点 / 分组布局）

2026-09-10 实做记录（V4 H3 工作流：换本地提示词组 + 修三处漏连 + 6 区分组）。

## 0. 先判格式

```python
d = json.load(open(path, encoding='utf-8'))
is_ui = 'nodes' in d and isinstance(d.get('nodes'), list)      # → UI：可改坐标/建组/改线
is_api = all(isinstance(v, dict) and 'class_type' in v for v in d.values())  # → API：只能体检连线
```
API 格式**没有坐标也没有 groups**，做不了节点组。凡哥要"分组/摆整齐"时直接请他
ComfyUI 里 `Workflow → Export` 导出 UI 格式（或从云端 `user/default/workflows/` 用 FileZilla 取），
**不要手工从 API 格式造 UI 文件**：`widgets_values` 顺序错 = 参数丢失 = 工作流行为被悄悄改掉。

UI 顶层键：`id / revision / last_node_id / last_link_id / nodes / links / groups / definitions / config / extra / version`。

## 1. 结构要点（改之前必读）

- 连线元组：`[link_id, 源节点id, 源输出槽, 目标节点id, 目标输入槽, 类型]`
- 节点 `inputs[]`：`{"name","type","link", ...}`；`outputs[]`：`{"name","type","links":[...]}`（**可能是 `None` 而不是 `[]`**）
- **改一根线要动三处**：`links` 数组 + 源 `outputs[槽].links` + 目标 `inputs[项].link`
- 目标输入槽 = `inputs` 数组**下标**：`next(i for i,it in enumerate(node['inputs']) if it['name']==NAME)`
- 输出槽下标 = `outputs` 数组下标（如子图节点的 out0/out1 = 两条链）
- 新增节点：**deepcopy 一个同类节点**当模板（保留 `properties` 里的 `cnr_id`/`aux_id`/`ver`），改 `id`/`pos`/`size`/`title`/`order`，inputs/outputs 重建，`last_node_id = max+1`
- 新 link id 从 `last_link_id+1` 递增，最后回写 `last_link_id`
- 旧文件常残留**坏链接**（指向已删节点，如 `[8833, 253, 0, 1209, 2, 'AUDIO']` 而 1209 不存在）→ 清 links 时同步从源 `outputs[].links` 摘掉
- 子图：`definitions.subgraphs[]`（带 name/nodes），主画布上是**一个** type=子图 uuid 的节点；子图内部节点改动风险高，非必要不动

## 2. 可复用代码骨架

```python
def link_of(dst_id, name):
    for it in nodes[dst_id].get('inputs', []):
        if it.get('name') == name: return it.get('link')
def remove_link(lid):
    l = lobj(lid)
    for o in nodes[l[1]].get('outputs', []) or []:
        if isinstance(o.get('links'), list) and lid in o['links']: o['links'].remove(lid)
    for it in nodes[l[3]].get('inputs', []) or []:
        if it.get('link') == lid: it['link'] = None
    links.remove(l)
def add_link(src_id, src_slot, dst_id, dst_name, ltype):
    global next_link
    dst_slot = next(i for i, it in enumerate(nodes[dst_id]['inputs']) if it.get('name') == dst_name)
    lid = next_link; next_link += 1
    links.append([lid, src_id, src_slot, dst_id, dst_slot, ltype])
    outs = nodes[src_id].setdefault('outputs', [])
    while len(outs) <= src_slot: outs.append({'name': ltype, 'type': ltype, 'links': []})
    if not isinstance(outs[src_slot].get('links'), list): outs[src_slot]['links'] = []   # ← None 坑
    outs[src_slot]['links'].append(lid)
    nodes[dst_id]['inputs'][dst_slot]['link'] = lid
    return lid
```

## 3. 分组 + 布局配方

```python
GROUPS = [("① 素材输入", [142,220,221], '#3f789e'), ...]   # 按数据流从左到右，一组一列
PAD_X, PAD_TOP, GAP_Y, GAP_X, TOP_Y = 60, 90, 45, 150, 3600
x = -4800
for title, ids, color in GROUPS:
    ids = [i for i in ids if i in nodes]                 # 未入组节点要单独报出来
    sz  = [(nodes[i].get('size') or [280,120]) for i in ids]
    cw  = max(s[0] for s in sz); y = TOP_Y + PAD_TOP; mb = y
    for i, s in zip(ids, sz):
        nodes[i]['pos'] = [x + PAD_X, y]; y += s[1] + GAP_Y; mb = y - GAP_Y
    new_groups.append({"title": title, "bounding": [x, TOP_Y, cw + 2*PAD_X, (mb-(TOP_Y+PAD_TOP))+2*PAD_TOP],
                       "color": color, "font_size": 28, "flags": {}})
    x += cw + 2*PAD_X + GAP_X
```
- **组内顺序 = 数据流顺序**（上游在上），连线才不会在组内回头
- 布局**只改 `pos`**，不碰 `links` / `widgets_values`
- **交付前生成 HTML 预览**（组框 + 节点按同比例画 div，新节点高亮）→ 聊天里 `::preview{file="..."}` 给凡哥看效果，他确认后再导入，省一轮往返

## 4. 改完必跑自检

```bash
<venv>/bin/python scripts/audit_workflow_ui_json.py <输出>.json
```
输出应全为 ✅：坏链接 0 / 悬空输入 0 / inputs↔outputs 不同步 0 / 未入组节点 0。

## 5. 本次实例（V4）

1. `1329`/`1341`.model：`1299`(链A LoRA) → **`1335`**(链B LoRA) —— 恢复"一采/二采各一套加速"
2. `201`.prompt：`1378` → **`1300`** —— 接回"润色开关链"（Any Switch：本地润色优先 / 原始文本兜底）
3. 新增 `1389` `Any Switch`「音频来源切换(二采优先)」：`any_01`←二采音频、`any_02`←一采音频 → `1210.on_false`
4. 清理坏链接 `8833`（指向不存在节点 1209）
5. 6 区分组 + 重排坐标（原 50 节点散乱 → 43 节点 6 组，悬空链接 0）

**教训**：这 4 个节点一开始被我按"无人引用"判成可删——**全错**。判死必须以参考版本（V3）的对应结构为依据，详见 SKILL.md 的"判没用的铁律"。
