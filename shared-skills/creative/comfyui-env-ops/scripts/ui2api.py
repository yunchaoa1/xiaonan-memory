# -*- coding: utf-8 -*-
"""
ComfyUI UI格式工作流 → API格式 转换器（可无头提交）

为什么需要它：ComfyUI 的 POST /prompt 只收 API 格式；UI 格式（带 nodes/links/definitions/groups）
直接提交会 500。而「导出(API)」只在浏览器前端里有 —— GUI 不可用时（预览面板无响应、
桌面窗口枚举不可用），这是唯一能自主跑工作流的路。

它干四件事：
  1. 子图拍平（definitions.subgraphs → 顶层节点，id 加 sg 前缀）
  2. bypass/静音节点（mode=2/4）做**同类型直通重连** ← 不做会断链、不出片
  3. 可达性剪枝（只保留输出类节点能回溯到的分支）
  4. 下拉值归一化（工作流里的大小写/斜杠写法与实际磁盘目录名对齐）

用法:
  python ui2api.py <ui.json> <out_api.json>            # 只转换 + 打印诊断
  python ui2api.py <ui.json> <out_api.json> --submit   # 转换后直接提交（含 /free 收尾）

依赖: 仅标准库（urllib），需 ComfyUI 实例在跑（默认 18188，用 --srv 改）。
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
import uuid

DEFAULT_SRV = 'http://127.0.0.1:18188'
WIDGET_TYPES = ('INT', 'FLOAT', 'STRING', 'BOOLEAN', 'COMBO')
# 输出类节点：可达性剪枝的起点（按需补充你自己的保存/预览类节点）
TERMINALS = ('VHS_VideoCombine', 'SaveVideo', 'SaveImage', 'SaveAudio',
             'PreviewAudio', 'PreviewImage', 'SaveAnimatedWEBP')

# ---------------------------------------------------------------------------
# 手工覆盖：位置映射不可靠 / 本机节点版本与原文件不同代时，在这里定死取值。
# 常见两类（本机 2026-09-15 实测）：
#   a) widget 值损坏 —— 取出来的是参数名本身（'frame_rate','loop_count',…），
#      即已知的「widget 值被写成名字」形态 → 整节点手工定死
#   b) 节点代次不同 —— 云版旧节点少了必需参数（如 MiniMaxH3ReferenceSplitter 的
#      short_edge_max / align_to），必须从另一份新一点的工作流里抄值补齐
# ---------------------------------------------------------------------------
OVERRIDES: dict[str, dict] = {}


def fetch_oi(srv: str) -> dict:
    with urllib.request.urlopen(srv + '/object_info', timeout=180) as r:
        return json.loads(r.read().decode('utf-8'))


def declared_widgets(spec: dict) -> list[str]:
    """按 object_info 声明顺序取 widget 型输入名（组合框 list / 基础类型 / DynamicCombo dict）"""
    names = []
    for sec in ('required', 'optional'):
        for n, d in (spec.get('input', {}).get(sec) or {}).items():
            t = d[0] if isinstance(d, (list, tuple)) and d else d
            if isinstance(t, list) or t in WIDGET_TYPES or isinstance(t, dict):
                names.append(n)
    return names


def norm_combo(cls: str, inputs: dict, oi: dict) -> list[str]:
    """下拉值归一化：文件里的大小写/正反斜杠与磁盘实际目录名不一致时自动纠正。

    实例：工作流写 'MiniMax-H3\\minimax_h3_audio_vae_fp32.safetensors'，
    实际下拉列表是 'minimax-h3\\minimax_h3_audio_vae_fp32.safetensors'
    → 提交报 value_not_in_list。别指望「Windows 不区分大小写」能救校验层。
    """
    spec = oi.get(cls) or {}
    opts = {}
    for sec in ('required', 'optional'):
        for n, d in (spec.get('input', {}).get(sec) or {}).items():
            t = d[0] if isinstance(d, (list, tuple)) and d else d
            if isinstance(t, list):
                opts[n] = t

    def canon(s):
        return str(s).replace('/', '\\').strip().lower()

    fixed = []
    for k, v in list(inputs.items()):
        if k in opts and isinstance(v, str) and v not in opts[k]:
            for c in opts[k]:
                if isinstance(c, str) and canon(c) == canon(v):
                    inputs[k] = c
                    fixed.append(f'{k}: {v!r} -> {c!r}')
                    break
    return fixed


def to_api(wf: dict, oi: dict, overrides: dict):
    top = list(wf.get('nodes', []))
    sgs = {sg['id']: sg for sg in (wf.get('definitions') or {}).get('subgraphs', []) or []}
    notes, warns = [], []

    # ---------- 1. 节点表 + id 别名（子图内节点用 sg 前缀，避免与顶层撞号） ----------
    nodes, id_alias = {}, {}
    for n in top:
        nodes[str(n['id'])] = n
    for iid, sg in sgs.items():
        for n in sg.get('nodes', []):
            aid = f'sg{n["id"]}'
            nodes[aid] = n
            id_alias[('inner', n['id'], iid)] = aid

    # ---------- 2. 链接表：src[(目标, 目标槽)] = (源, 源槽) ----------
    # ⚠ 顶层 links 是数组 [id, o, o_slot, t, t_slot, type]，
    #   子图 links 是字典 {id, origin_id, origin_slot, target_id, target_slot, type} —— 两种都要吃
    src: dict[tuple, tuple] = {}

    def add_links(links, inner=None):
        for L in links or []:
            if isinstance(L, dict):
                lid, o, os_ = L.get('id'), L.get('origin_id'), L.get('origin_slot')
                t, ts = L.get('target_id'), L.get('target_slot')
            elif len(L) >= 5:
                lid, o, os_, t, ts = L[0], L[1], L[2], L[3], L[4]
            else:
                continue
            if lid is None:
                continue
            if inner is not None:
                # 子图内部：origin 可能是虚拟的「子图输入槽」（负 id）→ 丢弃链接，
                # 让下游回落到节点自己的 widget 值（那才是界面里显示的值）
                if ('inner', o, inner) not in id_alias:
                    continue
                oid = id_alias[('inner', o, inner)]
                tid = id_alias.get(('inner', t, inner), f'sg{t}')
            else:
                oid, tid = str(o), str(t)
            src[(tid, ts)] = (oid, os_)

    add_links(wf.get('links'))
    for iid, sg in sgs.items():
        add_links(sg.get('links'), inner=iid)

    # ---------- 3. 子图输出槽 → 内部产出节点，并把顶层引用改指到内节点 ----------
    for iid, sg in sgs.items():
        inn = {}
        for L in (sg.get('links') or []):
            if isinstance(L, dict):
                inn[L.get('id')] = (L.get('origin_id'), L.get('origin_slot'))
            elif len(L) >= 5:
                inn[L[0]] = (L[1], L[2])
        inst = next((str(n['id']) for n in top if n.get('type') == iid), None)
        if not inst:
            continue
        for k, o in enumerate(sg.get('outputs') or []):
            lids = o.get('linkIds') or []
            pair = inn.get(lids[0]) if lids else None
            if not pair or ('inner', pair[0], iid) not in id_alias:
                continue
            new = (id_alias[('inner', pair[0], iid)], pair[1])
            for key in list(src):
                if src[key] == (inst, k):
                    src[key] = new
            notes.append(f'子图槽{k} {o.get("name")} -> {new[0]}[{new[1]}]')

    # ---------- 4. 分类 ----------
    skip_front = {a: n['type'] for a, n in nodes.items()
                  if n.get('type') not in oi and n.get('type') not in sgs}      # 前端 JS 节点
    skip_inst = {a for a, n in nodes.items() if n.get('type') in sgs}           # 子图实例本身
    skip_bypass = {a: n for a, n in nodes.items()
                   if n.get('mode') in (2, 4) and n.get('type') not in sgs}     # bypass / 静音

    # ---------- 5. bypass = 同类型直通重连（关键步骤，不做会断链） ----------
    # ComfyUI 的 bypass 语义 = 删掉该节点并把「同类型的输入」接到原输出下游。
    # 实例：MiniMaxH3AudioLock(mode=4) 的 av_latent 输出直接喂一采采样器的 latent_image，
    #       原样删掉 → 采样器缺 latent → 整条链不出片。
    for aid, n in skip_bypass.items():
        repl = {}
        for oi_idx, o in enumerate(n.get('outputs') or []):
            m = None
            for i_idx, i in enumerate(n.get('inputs') or []):
                if i.get('type') == o.get('type') and i.get('link') is not None:
                    m = src.get((aid, i_idx))
                    if m:
                        break
            repl[oi_idx] = m
        for key in list(src):
            if src[key][0] == aid:
                m = repl.get(src[key][1])
                if m:
                    src[key] = m
                else:
                    del src[key]
                    warns.append(f'bypass移除链接 {key[0]}[{key[1]}] <- {aid}（无同类型输入可直通）')

    # ---------- 6. 可达性剪枝：只保留输出类节点能回溯到的分支 ----------
    keep, stack = set(), [a for a, n in nodes.items()
                          if n.get('type') in TERMINALS
                          and a not in skip_bypass and a not in skip_front]
    while stack:
        a = stack.pop()
        if a in keep:
            continue
        keep.add(a)
        for (t_id, _ts), (o_id, _os) in src.items():
            if t_id == a and o_id not in keep:
                stack.append(o_id)
    dropped = sorted(set(nodes) - keep - set(skip_front) - set(skip_inst) - set(skip_bypass))
    if dropped:
        notes.append(f'不可达剪枝（本次不需要）：{dropped}')

    # ---------- 7. 生成 API ----------
    api = {}
    for aid in sorted(keep, key=lambda x: (x.startswith('sg'), x)):
        n = nodes[aid]
        cls = n['type']
        inputs = {}
        ui_in = list(n.get('inputs') or [])
        vals = list(n.get('widgets_values') or [])
        ui_w = [i['name'] for i in ui_in if 'widget' in i]
        oi_w = declared_widgets(oi[cls])

        # widget 名↔值按顺序配对：优先用文件自己的 inputs 顺序（能带出 dotted 名，
        # 如 'aspect_ratio.size1' / 'mode.scale' / 'ref_images.ref_image_0'），
        # 数量对不上才回落到 object_info 的声明顺序
        if ui_w and len(ui_w) == len(vals):
            names = ui_w
        elif len(oi_w) == len(vals):
            names = oi_w
        else:
            names = (oi_w[:len(vals)] if oi_w else ui_w[:len(vals)])
            warns.append(f'⚠ {aid} {cls}: 参数名无法确定 → 用 {names}（值 {len(vals)} 个）')

        for i, nm in enumerate(names):
            if i < len(vals):
                inputs[nm] = vals[i]
        for i, u in enumerate(ui_in):          # 连线覆盖 widget 默认值
            if u.get('link') is not None:
                got = src.get((aid, i))
                if got:
                    inputs[u['name']] = [got[0], got[1]]
        if aid in overrides:
            inputs.update(overrides[aid])
            notes.append(f'手工覆盖 #{aid}: {list(overrides[aid].keys())}')
        fx = norm_combo(cls, inputs, oi)
        if fx:
            notes.append(f'下拉归一化 #{aid}: ' + '; '.join(fx))

        api[aid] = {'class_type': cls, 'inputs': inputs,
                    '_meta': {'title': n.get('title') or cls}}

    return api, skip_front, skip_bypass, dropped, notes, warns


def submit(srv: str, api: dict) -> str | None:
    """POST /free → POST /prompt；校验失败会精确报出 node_errors（含节点号与参数名）"""
    try:
        req = urllib.request.Request(
            srv + '/free',
            data=json.dumps({"unload_models": True, "free_memory": True}).encode(),
            headers={'Content-Type': 'application/json'})
        urllib.request.urlopen(req, timeout=30)
        print('已 POST /free 释放显存')
    except Exception as e:                                  # 不致命
        print('free 失败(不致命):', e)

    cid = str(uuid.uuid4())
    req = urllib.request.Request(
        srv + '/prompt',
        data=json.dumps({"prompt": api, "client_id": cid}).encode('utf-8'),
        headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            body = json.loads(r.read().decode('utf-8'))
        print('✅ 已入队  prompt_id =', body.get('prompt_id'), ' number =', body.get('number'))
        return body.get('prompt_id')
    except urllib.error.HTTPError as e:
        raw = e.read().decode('utf-8', 'replace')
        print('❌ HTTP', e.code)
        try:
            d = json.loads(raw)
            print('error:', json.dumps(d.get('error'), ensure_ascii=False)[:400])
            for k, v in (d.get('node_errors') or {}).items():
                cls = (api.get(k) or {}).get('class_type', '?')
                print(f'  #{k} {cls}: {json.dumps(v, ensure_ascii=False)[:400]}')
        except Exception:
            print(raw[:1500])
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('ui')
    ap.add_argument('out')
    ap.add_argument('--srv', default=DEFAULT_SRV)
    ap.add_argument('--submit', action='store_true')
    a = ap.parse_args()

    wf = json.load(open(a.ui, encoding='utf-8'))
    oi = fetch_oi(a.srv)
    api, sf, sb, dropped, notes, warns = to_api(wf, oi, OVERRIDES)

    print('=== 丢弃：前端专用节点（不在 /object_info）===')
    for k, v in sf.items():
        print(f'  {k}: {v}')
    print('=== 丢弃：bypass/静音节点（已做同类型直通）===')
    for k, n in sb.items():
        print(f'  {k}: {n["type"]} (mode={n.get("mode")})')
    print(f'=== 不可达剪枝 {len(dropped)} 个：{dropped} ===')
    print('=== 提示 ===')
    for x in notes:
        print('  ' + x)
    print('=== 警告（需要人看）===')
    for x in warns:
        print('  ' + x)
    json.dump(api, open(a.out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'\n✅ API 写出: {a.out}  节点数 {len(api)}')

    if a.submit:
        print()
        submit(a.srv, api)


if __name__ == '__main__':
    main()
