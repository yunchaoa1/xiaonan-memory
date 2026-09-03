import json, time, urllib.request

PID = "e3779c7d-1ec9-47bf-bef2-0a9739ff0f9e"
BASE = "http://127.0.0.1:18188"

def get(path):
    try:
        with urllib.request.urlopen(BASE + path, timeout=10) as r:
            return json.load(r)
    except Exception:
        return None

t0 = time.time()
while time.time() - t0 < 1200:
    q = get("/queue")
    h = get(f"/history/{PID}")
    if h and PID in h:
        status = h[PID].get("status", {})
        if status.get("completed") or status.get("status_str") == "success":
            outs = h[PID].get("outputs", {})
            print("DONE", time.strftime("%H:%M:%S"))
            print(json.dumps(outs, ensure_ascii=False)[:2000])
            break
        if status.get("status_str") == "error":
            print("ERROR")
            print(json.dumps(status, ensure_ascii=False)[:1500])
            break
    time.sleep(15)
else:
    print("TIMEOUT")