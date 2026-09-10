# -*- coding: utf-8 -*-
"""H3 r8 29-seg first-pass runner: serial batches, /free between, poll /history,
verify minimax_seg_cache fingerprints, archive per-shot, write progress."""
import json, os, sys, time, shutil, urllib.request, urllib.error

BASE = r"D:\Hermes\xiaonan-memory\opc-sim\v2\07_h3_prompt\h3_r8_29seg"
URL = "http://127.0.0.1:18188"
CLIENT = "h3-r8-29seg-run"
DIR_NODE = "1201"
CACHE = r"D:\SDkecheng\ComfyUI\output\minimax_seg_cache\1201"
ARCH = os.path.join(BASE, "firstpass_cache")
PROG = os.path.join(BASE, "firstpass_progress.json")
LOG = os.path.join(BASE, "run_log.txt")

def log(msg):
    line = f"[{time.strftime('%H:%M:%S')}] {msg}"
    print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def http_json(method, path, body=None, timeout=30):
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(URL + path, data=data, method=method)
    if data is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode("utf-8"))
        except Exception:
            return e.code, {"error": "non-json"}
    except Exception as e:
        return -1, {"error": str(e)}

def free_and_stats(tag):
    st, d = http_json("POST", "/free", {"unload_models": True, "free_memory": True})
    log(f"{tag} POST /free -> {st}")
    st2, s = http_json("GET", "/system_stats")
    if st2 == 200 and "system" in s:
        sysd = s["system"]
        log(f"{tag} ram_free={sysd.get('ram_free', '?')/1e6:.0f}MB of {sysd.get('ram_total','?')/1e6:.0f}MB")
        dv = s.get("devices") or []
        if dv:
            v = dv[0]
            log(f"{tag} vram_free={v.get('vram_free','?')/1e6:.0f}MB of {v.get('vram_total','?')/1e6:.0f}MB")
    time.sleep(3)

manifest = json.load(open(os.path.join(BASE, "payloads", "manifest.json"), encoding="utf-8"))
nb = len(manifest)
progress = {"done": [], "failures": [], "done_batches": []}
if os.path.exists(PROG):
    progress = json.load(open(PROG, encoding="utf-8"))
    progress.setdefault("done", [])
    progress.setdefault("done_batches", [])
    progress.setdefault("failures", [])

def verify_batch(bi, seg_prompts):
    """seg_prompts: list of prompt strings in segment order. Returns list of per-seg (ok, cachefiles)."""
    out = []
    for j, prompt in enumerate(seg_prompts):
        pre = [f"seg_{j:04d}.pre.pt", f"seg_{j:04d}.pre.av.pt",
               f"seg_{j:04d}.pre.meta.json", f"seg_{j:04d}.pre.handoff.json"]
        ok = True
        sizes = {}
        for fn in pre:
            p = os.path.join(CACHE, fn)
            if not os.path.isfile(p) or os.path.getsize(p) <= 0:
                ok = False; sizes[fn] = "MISSING"
            else:
                sizes[fn] = os.path.getsize(p)
        meta_ok = None
        mp = os.path.join(CACHE, f"seg_{j:04d}.pre.meta.json")
        if os.path.isfile(mp):
            try:
                meta = json.load(open(mp, encoding="utf-8"))
                meta_ok = (meta.get("prompt") == prompt)
            except Exception:
                meta_ok = False
        out.append({"index": j, "files_ok": ok, "sizes": sizes, "fingerprint_match": meta_ok})
        log(f"  seg_{j:04d}: files_ok={ok} fingerprint_match={meta_ok} sizes={ {k: v for k, v in sizes.items()} }")
    return out

def archive_batch(bi, sids):
    dst_dir = os.path.join(ARCH, f"batch{bi}")
    os.makedirs(dst_dir, exist_ok=True)
    paths = []
    for j, sid in enumerate(sids):
        d = os.path.join(dst_dir, sid)
        os.makedirs(d, exist_ok=True)
        for fn in (f"seg_{j:04d}.pre.pt", f"seg_{j:04d}.pre.av.pt",
                   f"seg_{j:04d}.pre.meta.json", f"seg_{j:04d}.pre.handoff.json"):
            src = os.path.join(CACHE, fn)
            if os.path.isfile(src):
                shutil.copy2(src, os.path.join(d, fn))
        paths.append(os.path.join(d, "seg_%04d.pre.pt" % j))
    log(f"batch{bi} archived -> {dst_dir}")
    return paths

def run_batch(bi):
    sids = manifest[f"batch{bi}"]
    payload = json.load(open(os.path.join(BASE, "payloads", f"batch_{bi}.json"), encoding="utf-8"))
    tl = json.loads(payload[DIR_NODE]["inputs"]["timeline_data"])
    seg_prompts = [s["prompt"] for s in tl["segments"]]
    nframes = tl["totalFrames"]
    log(f"=== batch{bi}: {len(sids)} segs {sids} frames={nframes} ===")
    free_and_stats(f"batch{bi} pre-free")
    t0 = time.time()
    st, resp = http_json("POST", "/prompt", {"prompt": payload, "client_id": CLIENT}, timeout=60)
    if st != 200 or "prompt_id" not in resp:
        log(f"batch{bi} SUBMIT FAILED st={st} resp={json.dumps(resp, ensure_ascii=False)[:800]}")
        raise RuntimeError(f"submit failed: {resp}")
    pid = resp["prompt_id"]
    log(f"batch{bi} submitted prompt_id={pid}")
    # poll
    while True:
        time.sleep(15)
        st, h = http_json("GET", f"/history/{pid}")
        if st == 200 and h and pid in h:
            entry = h[pid]
            status = (entry.get("status") or {}).get("status_str")
            if status == "completed":
                break
            if status == "error":
                msgs = [m.get("message", "") for m in (entry.get("status") or {}).get("messages", [])]
                log(f"batch{bi} ERROR: {json.dumps(msgs, ensure_ascii=False)[:1200]}")
                raise RuntimeError(f"batch error: {msgs}")
        if time.time() - t0 > 6 * 3600:
            raise RuntimeError("batch timeout 6h")
    el = time.time() - t0
    log(f"batch{bi} completed in {el/60:.1f} min")
    free_and_stats(f"batch{bi} post-free")
    # verify per-seg cache + fingerprint, then archive
    ver = verify_batch(bi, seg_prompts)
    arch = archive_batch(bi, sids)
    good = all(v["files_ok"] and v["fingerprint_match"] for v in ver)
    if not good:
        raise RuntimeError(f"batch{bi} cache verify failed: {ver}")
    per = [{"sid": sid, "frames": seg["frameCount"], "duration_s": seg["durationSec"],
            "prompt_id": pid, "seg_index": j, "cache_path": arch[j],
            "batch_elapsed_s": round(el, 1)} for j, (sid, seg) in enumerate(zip(sids, tl["segments"]))]
    progress["done"].extend(per)
    json.dump(progress, open(PROG, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    log(f"batch{bi} DONE archived {len(arch)} segs")

if __name__ == "__main__":
    done_bi = {p["prompt_id"] for p in progress["done"]}
    try:
        for bi in range(1, nb + 1):
            if f"batch{bi}" in [p.get("batch_tag", "") for p in progress["done"]]:
                continue
            # tag done entries
            for p in progress["done"]:
                p["batch_tag"] = p.get("batch_tag")
            run_batch(bi)
        log("ALL BATCHES DONE")
        print(json.dumps(progress, ensure_ascii=False, indent=1))
    except Exception as e:
        progress["failures"].append(str(e))
        json.dump(progress, open(PROG, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        log(f"RUN STOPPED: {e}")
        sys.exit(1)
