# -*- coding: utf-8 -*-
"""工作流缺件体检：以运行实例的 /object_info 为权威源，排掉 3 类假阳性。

为什么需要它（2026-09-14 本机实测的教训）：
  · grep 源码查缺件会误判（0.3x 核心节点用 IO.Schema(node_id="X") 写法）
  · 直接拿 /object_info 求差集又会**误报 3 类假缺件**：前端节点、子图实例 uuid、
    加载器第 1 个 widget 不是文件名；模型名还会因目录前缀不同被误报
  · 手工跑一次要拼 5 条命令，且极易漏掉归一化步骤 → 固化成脚本

用法:
    python audit_workflow_missing_nodes.py <工作流.json> [更多.json ...]
    python audit_workflow_missing_nodes.py <工作流.json> --port 18188
    python audit_workflow_missing_nodes.py <工作流.json> --models D:/SDkecheng/ComfyUI/models
    python audit_workflow_missing_nodes.py <工作流.json> --object-info ./object_info.json

默认自动探测端口（8188 / 18188）；取不到运行实例时回退读脚本同目录的 object_info.json。
"""
import argparse, json, os, re, sys, urllib.request

# 只在**前端 JS/TS** 里注册、永远不出现在 /object_info 的节点 → 不许报缺
FRONTEND_ONLY = {
    'Note', 'MarkdownNote', 'Reroute', 'PrimitiveNode', 'Bookmark', 'Label',
    'Fast Bypasser (rgthree)', 'Fast Muter (rgthree)',
    'Fast Groups Bypasser (rgthree)', 'Fast Groups Muter (rgthree)',
    'SetNode', 'GetNode', 'Anything Everywhere',
}

LOADER_TYPES = ('UNETLoader', 'CLIPLoader', 'VAELoader', 'LoraLoader',
                'LoraLoaderModelOnly', 'UpscaleModelLoader',
                'LatentUpscaleModelLoader', 'DiffusionModelLoader',
                'CheckpointLoaderSimple', 'ControlNetLoader')
# 这些 loader 的 widgets_values[1] 是枚举（type/dtype），不是文件名 → 只取 [0]
ENUM_WIDGET0_SKIP = {'default', 'minimax', 'ltxv', 'wan', 'sdxl', 'sd1.5', 'flux',
                     'stable_diffusion', 'auto', 'none', 'fp8_e4m3fn', 'fp16', 'bf16'}

DEFAULT_PORTS = (8188, 18188)


def fetch_object_info(port=None, cache_path='object_info.json'):
    """返回 (object_info_dict, 来源说明)。port=None 时逐个探测默认端口。"""
    ports = [port] if port else list(DEFAULT_PORTS)
    for p in ports:
        try:
            with urllib.request.urlopen(
                    f'http://127.0.0.1:{p}/object_info', timeout=10) as r:
                data = json.loads(r.read().decode('utf-8'))
            try:
                with open(cache_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f)
            except OSError:
                pass
            return data, f'运行实例 127.0.0.1:{p}'
        except Exception:
            continue
    if os.path.exists(cache_path):
        with open(cache_path, encoding='utf-8') as f:
            return json.load(f), f'本地缓存 {cache_path}（实例没连上，可能不是最新！）'
    sys.exit('取不到 /object_info：把 ComfyUI 跑起来，或 --object-info 指一个已存的文件')


def collect(wf):
    """收集节点类型；子图定义单独返回，用于识别子图实例 uuid。"""
    import collections
    types = collections.Counter()
    for n in wf.get('nodes', []) or []:
        types[n.get('type')] += 1
    sub_ids, sub_types = set(), collections.Counter()
    for sg in (wf.get('definitions', {}) or {}).get('subgraphs', []) or []:
        for key in ('id', 'uuid', 'name'):
            if sg.get(key):
                sub_ids.add(sg[key])
        for n in sg.get('nodes', []) or []:
            sub_types[n.get('type')] += 1
    return types, sub_ids, sub_types


def models_in(nodes):
    """抽加载器的模型引用；跳过枚举值（CLIPLoader 的 type / UNETLoader 的 dtype）。"""
    out = []
    for n in nodes:
        if n.get('type') not in LOADER_TYPES:
            continue
        wv = n.get('widgets_values') or []
        if not wv:
            continue
        name = wv[0]
        if not isinstance(name, str) or not name or name.lower() in ENUM_WIDGET0_SKIP:
            continue
        if not re.search(r'\.(safetensors|sft|ckpt|pt|pth|gguf|bin)$', name, re.I):
            continue
        out.append((n.get('type'), name))
    return out


def index_models(models_dir):
    """basename 小写 → 相对路径列表。忽略目录前缀是必须的：
    工作流写 MiniMax-H3\\x.safetensors，本机可能在 diffusion_models/minimax_h3/x.safetensors"""
    idx = {}
    if not models_dir or not os.path.isdir(models_dir):
        return idx
    for dp, _dns, fns in os.walk(models_dir):
        for fn in fns:
            rel = os.path.relpath(os.path.join(dp, fn), models_dir).replace(os.sep, '/')
            idx.setdefault(fn.lower(), []).append(rel)
    return idx


def audit(path, registered, models_dir):
    wf = json.load(open(path, encoding='utf-8'))
    fmt = 'UI' if 'nodes' in wf else 'API'
    types, sub_ids, sub_types = collect(wf)
    all_types = types + sub_types

    missing, frontend, subgraph_inst = [], [], []
    for t, c in sorted(all_types.items()):
        if t is None:
            continue
        if t in sub_ids:
            subgraph_inst.append((t, c))          # 子图实例，不是缺件
        elif t in registered:
            continue
        elif t in FRONTEND_ONLY:
            frontend.append((t, c))
        else:
            missing.append((t, c))

    print('=' * 72)
    print(f'### {os.path.basename(path)}   [{fmt} 格式]')
    print(f'    顶层节点 {sum(types.values())} 个 / {len(types)} 类型'
          f' · 子图 {len(sub_ids)} 个 / 子图内 {sum(sub_types.values())} 节点')
    print(f'    ❌ 真缺件 {len(missing)} 种：')
    for t, c in missing:
        print(f'         {t}   (x{c})')
    if not missing:
        print('         （无 —— 节点全齐 ✅）')
    if frontend:
        print(f'    ⏭  前端节点（正常，不算缺）：{[t for t, _ in frontend]}')
    if subgraph_inst:
        print(f'    ⏭  子图实例 uuid（正常，不算缺）：{[t for t, _ in subgraph_inst]}')

    if models_dir:
        idx = index_models(models_dir)
        if not idx:
            print(f'    ⚠️  模型目录不可读，跳过模型核对：{models_dir}')
            return
        nodes = list(wf.get('nodes', []) or [])
        for sg in (wf.get('definitions', {}) or {}).get('subgraphs', []) or []:
            nodes += sg.get('nodes', []) or []
        seen, hits, misses = set(), 0, 0
        print(f'    模型引用（本机 {len(idx)} 个文件，按 basename 归一比对）：')
        for ltype, name in models_in(nodes):
            if name in seen:
                continue
            seen.add(name)
            hit = idx.get(name.replace('\\', '/').split('/')[-1].lower())
            if hit:
                hits += 1
                print(f'       ✅ [{ltype}] {name}  → {hit[0]}')
            else:
                misses += 1
                print(f'       ❌ [{ltype}] {name}   （本机真缺）')
        print(f'    小结：模型 {hits} 有 / {misses} 缺')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('workflows', nargs='+')
    ap.add_argument('--port', type=int, default=None,
                    help='实例端口；不给则探测 8188 / 18188')
    ap.add_argument('--models', default=None,
                    help='ComfyUI/models 目录；给了才做模型核对（强烈建议给）')
    ap.add_argument('--object-info', dest='oi', default='object_info.json')
    a = ap.parse_args()

    obj, src = fetch_object_info(a.port, a.oi)
    print(f'权威节点源：{src} —— 已注册节点类 {len(obj)} 个')
    for w in a.workflows:
        try:
            audit(w, obj, a.models)
        except Exception as e:
            print(f'  !! {w} 体检失败：{type(e).__name__}: {e}')
    print()
    print('提醒：结论必须排掉 前端节点 / 子图 uuid / 加载器枚举值 三类假阳性；')
    print('      模型比对必须忽略目录前缀（工作流 MiniMax-H3\\x vs 本机 minimax_h3/x）。')
    print('      「同名工作流」可能内容不同 —— 附件版与 ComfyUI 存过的版本先比 size/hash。')


if __name__ == '__main__':
    main()
