import json, time, urllib.request

PID = "617202d2-99b9-4aeb-a3bd-f9928fb1e070"
BASE = "http://127.0.0.1:18189"

def get(path):
    try:
        with urllib.request.urlopen(BASE + path, timeout=10) as r:
            return json.load(r)
    except Exception as e:
        return {"error": str(e)}

start = time.time()
while time.time() - start < 3000:
    h = get("/history/" + PID)
    if h.get(PID):
        st = h[PID].get("status", {})
        if st.get("status_str") == "success":
            outs = h[PID].get("outputs", {})
            print("DONE", time.strftime("%H:%M:%S"))
            print("node7:", json.dumps(outs.get("7", {}), ensure_ascii=False)[:200])
            print("node8:", json.dumps(outs.get("8", {}), ensure_ascii=False)[:400])
            break
        if st.get("status_str") == "error":
            print("ERROR:", json.dumps(st, ensure_ascii=False)[:600])
            break
    print(time.strftime("%H:%M:%S"), "elapsed", int(time.time() - start), "s running...")
    time.sleep(30)
else:
    print("TIMEOUT 50min")