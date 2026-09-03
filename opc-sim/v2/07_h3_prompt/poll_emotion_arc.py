import json, time, urllib.request

PID = "c3930f04-d66e-4051-807b-ceb2de98b2f1"
BASE = "http://127.0.0.1:18188"

def get(path):
    try:
        with urllib.request.urlopen(BASE + path, timeout=10) as r:
            return json.load(r)
    except Exception as e:
        return None

t0 = time.time()
last_status = ""
while time.time() - t0 < 3600:  # 1h cap
    q = get("/queue")
    if q is not None:
        running = q.get("queue_running", [])
        pending = q.get("queue_pending", [])
        status = f"running={len(running)} pending={len(pending)}"
        if status != last_status:
            print(time.strftime("%H:%M:%S"), status, flush=True)
            last_status = status
    h = get(f"/history/{PID}")
    if h and PID in h:
        entry = h[PID]
        status = entry.get("status", {})
        if status.get("completed") or status.get("status_str") == "success":
            outs = entry.get("outputs", {})
            print("DONE", time.strftime("%H:%M:%S"))
            print(json.dumps(outs, ensure_ascii=False)[:3000])
            break
        if status.get("status_str") == "error":
            print("ERROR", time.strftime("%H:%M:%S"))
            print(json.dumps(status, ensure_ascii=False)[:2000])
            break
    time.sleep(30)
else:
    print("TIMEOUT after 1h")
