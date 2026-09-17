#!/usr/bin/env python3
"""探针：某个节点输入的「值」会不会被 ComfyUI 拦掉。

用途：判断「工作流里的值（大小写不同 / 正反斜杠不同 / 疑似不在下拉列表）」到底要不要改。
不要凭「字符串不在下拉列表里」就动工作流 —— 先实测（见 SKILL.md「提交 /prompt 成功 ≠ 输入值合法」）。

用法：
    python probe_combo_value.py VAELoader vae_name "MiniMax-H3/minimax_h3_audio_vae_fp32.safetensors"
    python probe_combo_value.py VAELoader vae_name "A.safetensors" "B.safetensors" --port 18188

坑（都踩过）：
  * 探针必须带一个输出节点，否则 ComfyUI 提前返回 prompt_no_outputs，
    node_errors 是空的 → 什么也验不到（第一版探针就是这么白跑的）。
  * 输出节点选最省的：EmptyImage -> SaveImage（64x64，不碰任何模型）。
  * 被测节点不接任何输出时会被 ComfyUI 剪枝：只校验不执行 —— 正合纯校验探针的需求；
    探完仍建议 POST /interrupt + POST /free 收尾。
  * 校验放行 != 值合法：实测不存在的模型名也会被放行。文件不存在只会在执行期炸。
  * 200 + 无 node_errors 只说明「没被拦」，不等于「能出片」；说结论时别把它升级成「已跑通」。
"""
import argparse
import json
import urllib.error
import urllib.request


def post(base, path, payload):
    req = urllib.request.Request(
        base + path,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", "replace")
        try:
            return e.code, json.loads(raw)
        except Exception:
            return e.code, {"_raw": raw[:300]}


def probe(base, class_type, input_name, value, client_id="probe"):
    graph = {
        "1": {"class_type": class_type, "inputs": {input_name: value}},
        "2": {"class_type": "EmptyImage",
              "inputs": {"width": 64, "height": 64, "batch_size": 1, "color": 0}},
        "3": {"class_type": "SaveImage",
              "inputs": {"images": ["2", 0], "filename_prefix": "probe_combo"}},
    }
    status, body = post(base, "/prompt", {"prompt": graph, "client_id": client_id})
    errs = body.get("node_errors") or {}
    if errs:
        print("  \u274c 被拦  value=%r" % value)
        for nid, err in errs.items():
            for e in err.get("errors", []):
                print("       -> %s: %s %s" % (e.get("type"), e.get("message"), e.get("details", "")))
        return False
    if status == 200:
        print("  \u2705 放行（未拦；注意这 ≠ 值合法、更 ≠ 能出片）  value=%r" % value)
        return True
    print("  \u26d4 HTTP %s  value=%r  %s" % (status, value, json.dumps(body, ensure_ascii=False)[:200]))
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("class_type", help="节点类名，如 VAELoader")
    ap.add_argument("input_name", help="输入名，如 vae_name")
    ap.add_argument("values", nargs="+", help="一个或多个待测值")
    ap.add_argument("--port", default="18188", help="ComfyUI 端口（本机是 18188，不是 8188）")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--no-cleanup", action="store_true", help="跳过 interrupt/free 收尾")
    a = ap.parse_args()

    base = "http://%s:%s" % (a.host, a.port)
    try:
        with urllib.request.urlopen(base + "/system_stats", timeout=8) as r:
            st = json.loads(r.read())
        print("实例: ComfyUI %s | torch %s" % (
            st.get("system", {}).get("comfyui_version"),
            st.get("system", {}).get("pytorch_version")))
    except Exception as e:
        print("连不上 %s（%s）—— 确认端口/实例是否在跑" % (base, type(e).__name__))
        return 2

    print("探针: %s.%s" % (a.class_type, a.input_name))
    for v in a.values:
        probe(base, a.class_type, a.input_name, v)

    if not a.no_cleanup:
        post(base, "/interrupt", {})
        post(base, "/free", {"unload_models": True, "free_memory": True})
        try:
            with urllib.request.urlopen(base + "/queue", timeout=8) as r:
                q = json.loads(r.read())
            print("收尾: 已 interrupt + free | 队列 运行中 %d / 等待 %d" % (
                len(q.get("queue_running", [])), len(q.get("queue_pending", []))))
        except Exception:
            print("收尾: 已 interrupt + free")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
