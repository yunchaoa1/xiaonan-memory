# -*- coding: utf-8 -*-
"""API-格式 ComfyUI 工作流 JSON 连线体检。

用法:
    python audit_workflow_json.py 工作流1.json [工作流2.json ...]

输出每个工作流:
  - 节点数 / 类名清单
  - 无效引用: inputs 里 [node_id, out_idx] 指向文件里不存在的节点
  - 悬空节点: 没有任何下游引用的节点(已排除输出/显示类,这些悬空是正常的)
  - 两个工作流的同名结构差异不在此脚本范围(自行 diff)

判读要点(见 SKILL.md「工作流 JSON 连线体检」):
  - 悬空 = 可疑, 不必然错; 判错前先看该节点类型是否有\"输出给人看\"的正当理由
  - 无效引用 = 一定错(节点被删/工作流被手工改断)
"""
import json
import sys

# 这些类型天然没有下游(它们是终点), 悬空不算问题
TERMINAL = (
    "VHS_VideoCombine", "SaveImage", "SaveVideo", "PreviewImage",
    "ShowText", "PreviewAny", "VRAM_Debug",
)
# 这些类型一旦悬空, 基本就是连线错误(加载器/采样器/开关/编码器)
SUSPECT = (
    "Loader", "Lora", "Primitive", "Switch", "ImageInfer", "Sampler",
    "VAEDecode", "VAEEncode", "Concat", "Scheduler", "Guider", "Noise",
    "Calculator", "Upscaler", "Resize", "cleanGpu", "ModelPreview",
)


def audit(path):
    d = json.load(open(path, encoding="utf-8"))
    # API 格式: 顶层键 = 节点 id
    classmap = {k: v.get("class_type", "?") for k, v in d.items() if isinstance(v, dict)}
    ids = set(classmap)
    used = {}
    for k, v in d.items():
        if not isinstance(v, dict):
            continue
        for ik, iv in v.get("inputs", {}).items():
            if isinstance(iv, list) and len(iv) == 2 and isinstance(iv[0], str):
                used.setdefault(iv[0], []).append("%s.%s" % (k, ik))

    print("########## %s ##########" % path)
    print("节点数: %d" % len(classmap))
    sub = [k for k in classmap if ":" in k]
    if sub:
        print("子图节点: %d 个 (形如 1297:123, 顶层引用正常)" % len(sub))

    bad = [(u, ws) for u, ws in used.items() if u not in ids]
    print("无效引用(指向不存在的节点): %s" % (bad if bad else "无 [OK]"))

    dangling = []
    for k, ct in sorted(classmap.items(), key=lambda x: str(x[0])):
        if k in used:
            continue
        if any(t in ct for t in TERMINAL):
            continue
        if any(t in ct for t in SUSPECT):
            dangling.append("[%s] %s" % (k, ct))
    print("可疑悬空节点(输出无人使用): %s" % ("\n    " + "\n    ".join(dangling) if dangling else "无 [OK]"))
    print()
    return bad, dangling


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 1
    rc = 0
    for p in argv[1:]:
        try:
            bad, dangling = audit(p)
            if bad or dangling:
                rc = 2
        except Exception as exc:  # noqa: BLE001
            print("[ERROR] %s: %s" % (p, exc))
            rc = 3
    print("提示: 悬空多为可删的残留(如换掉 API 节点后遗留的 Switch->ShowText 支线);"
          "若那条支线本意是喂给 sampler, 说明漏连了。")
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv))
