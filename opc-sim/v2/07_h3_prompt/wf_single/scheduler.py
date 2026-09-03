import json, time, urllib.request, os, sys

BASE = "http://127.0.0.1:18189"
WFDIR = r"D:\Hermes\xiaonan-memory\opc-sim\v2\07_h3_prompt\wf_single"
LOG = os.path.join(WFDIR, "run_log.txt")

def get(path, timeout=10):
    try:
        with urllib.request.urlopen(BASE + path, timeout=timeout) as r:
            return json.load(r)
    except Exception as e:
        return {"error": str(e)}

def log(msg):
    line = f"{time.strftime('%H:%M:%S')} {msg}"
    print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def submit(wf, client_id):
    payload = {"prompt": wf, "client_id": client_id}
    req = urllib.request.Request(BASE + "/prompt", data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=30))

def wait_done(prompt_id, timeout_s=3600):
    start = time.time()
    while time.time() - start < timeout_s:
        h = get(f"/history/{prompt_id}")
        if h.get(prompt_id):
            st = h[prompt_id].get("status", {})
            if st.get("status_str") == "success":
                return "success", h[prompt_id].get("outputs", {})
            if st.get("status_str") == "error":
                msgs = st.get("messages", [])
                return "error", str(msgs[-1:])[:300]
        time.sleep(30)
    return "timeout", ""

def main():
    manifest = json.load(open(os.path.join(WFDIR, "manifest.json"), encoding="utf-8"))
    log(f"=== 23镜一采调度启动，共 {len(manifest)} 镜 ===")
    results = []
    t0 = time.time()
    for i, m in enumerate(manifest):
        sid = m["shot_id"]
        wf = json.load(open(os.path.join(WFDIR, m["file"]), encoding="utf-8"))
        log(f"[{i+1}/23] {sid} 提交 (frames={m['frames']}, node={m['node_id']})")
        try:
            r = submit(wf, f"full-{sid}")
            if "prompt_id" not in r:
                log(f"  {sid} 提交失败: {r}")
                results.append({"shot_id": sid, "status": "submit_fail", "err": str(r)[:200]})
                continue
            pid = r["prompt_id"]
            if r.get("node_errors"):
                log(f"  {sid} 节点错误: {json.dumps(r['node_errors'], ensure_ascii=False)[:300]}")
            st, out = wait_done(pid)
            if st == "success":
                log(f"  {sid} 一采完成 (用时 {int((time.time()-t0)/60)}min 累计)")
                results.append({"shot_id": sid, "status": "ok", "prompt_id": pid})
            else:
                log(f"  {sid} {st}: {out}")
                results.append({"shot_id": sid, "status": st, "err": out})
        except Exception as e:
            log(f"  {sid} 异常: {str(e)[:300]}")
            results.append({"shot_id": sid, "status": "exception", "err": str(e)[:200]})
    ok = sum(1 for r in results if r["status"] == "ok")
    log(f"=== 一采调度结束: {ok}/{len(manifest)} 成功, 总用时 {int((time.time()-t0)/60)}min ===")
    json.dump(results, open(os.path.join(WFDIR, "run_results.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"ALL_DONE {ok}/{len(manifest)}", flush=True)

if __name__ == "__main__":
    main()
