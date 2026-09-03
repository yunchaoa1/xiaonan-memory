import json, time, urllib.request

PID = "057c89d0-339a-4b32-8b46-19142a58a72d"
BASE = "http://127.0.0.1:18189"

def get(path):
    try:
        with urllib.request.urlopen(BASE + path, timeout=10) as r:
            return json.load(r)
    except Exception as e:
        return {"error": str(e)}

start = time.time()
while time.time() - start < 3300:
    h = get("/history/" + PID)
    if h.get(PID):
        st = h[PID].get("status", {})
        if st.get("status_str") == "success":
            outs = h[PID].get("outputs", {})
            print("DONE", time.strftime("%H:%M:%S"))
            print("node7:", json.dumps(outs.get("7", {}), ensure_ascii=False)[:300])
            print("node8:", json.dumps(outs.get("8", {}), ensure_ascii=False)[:700])
            break
        if st.get("status_str") == "error":
            msgs = st.get("messages", [])
            err = [m for m in msgs if m[0] == "execution_error"]
            print("ERROR:", json.dumps(err, ensure_ascii=False)[:500])
            break
    print(time.strftime("%H:%M:%S"), "elapsed", int(time.time() - start), "s running...")
    time.sleep(40)
else:
    print("TIMEOUT 55min")
