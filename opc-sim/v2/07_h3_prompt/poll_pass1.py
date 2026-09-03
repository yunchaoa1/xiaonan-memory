import json, time, urllib.request, sys

PID = "9640ae19-c250-494d-bcf2-508308e17af5"
BASE = "http://127.0.0.1:18188"

def get(path):
    try:
        with urllib.request.urlopen(BASE + path, timeout=10) as r:
            return json.loads(r.read().decode('utf-8'))
    except Exception as e:
        return {"_err": str(e)}

deadline = time.time() + 40 * 60  # 40 min max
last_status = ""
while time.time() < deadline:
    h = get("/history/" + PID)
    if PID in h:
        entry = h[PID]
        st = entry.get("status", {})
        if st.get("completed") or st.get("status_str") == "success":
            outs = entry.get("outputs", {})
            print("DONE. outputs:", json.dumps(outs, ensure_ascii=False)[:2000])
            sys.exit(0)
        if st.get("status_str") == "error":
            msgs = st.get("messages", [])
            print("ERROR:", json.dumps(msgs, ensure_ascii=False)[:1500])
            sys.exit(1)
    q = get("/queue")
    qr = q.get("queue_running", [])
    running = any(x[1] == PID for x in qr) if qr else False
    status = "running" if running else ("waiting" if any(x[1]==PID for x in q.get("queue_pending",[])) else "?")
    if status != last_status:
        print(time.strftime("%H:%M:%S"), "status:", status, flush=True)
        last_status = status
    time.sleep(20)

print("TIMEOUT after 40min")
sys.exit(2)
