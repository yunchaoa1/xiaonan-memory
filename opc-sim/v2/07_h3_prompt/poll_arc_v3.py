import json, time, urllib.request

PID = "b2be72e1-e84f-41b9-86c9-d06290210f0b"
BASE = "http://127.0.0.1:18188"

def get(path):
    try:
        with urllib.request.urlopen(BASE + path, timeout=10) as r:
            return json.load(r)
    except Exception as e:
        return {"error": str(e)}

start = time.time()
while time.time() - start < 3600:
    h = get(f"/history/{PID}")
    if h.get(PID):
        e = h[PID]
        status = e.get("status", {})
        if status.get("completed") or status.get("status_str") == "success":
            outs = e.get("outputs", {})
            files = []
            for nid, o in outs.items():
                if "images" in o and o["images"]:
                    files.append(o["images"][0].get("filename"))
                if "audio" in o:
                    pass
            print(f"DONE at {time.strftime('%H:%M:%S')} files: {files}")
            print(json.dumps(outs.get("8", {}), ensure_ascii=False)[:800])
            break
        if status.get("status_str") == "error":
            print("ERROR:", json.dumps(status, ensure_ascii=False)[:500])
            break
    q = get("/queue")
    if not q.get("queue_running"):
        print("queue empty but no history - checking...")
    print(f"{time.strftime('%H:%M:%S')} elapsed {int(time.time()-start)}s running...")
    time.sleep(45)
else:
    print("TIMEOUT after 3600s")
