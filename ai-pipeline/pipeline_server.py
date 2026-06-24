"""
星火智画本地版 · AI短剧生产管线
FastAPI 后端 + ComfyUI API
"""
import json, os, asyncio, uuid, time
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="星火智画 · 本地版")

WORKSPACE = Path(os.environ.get("PIPELINE_WORKSPACE", str(Path(__file__).parent / "projects")))
WORKSPACE.mkdir(exist_ok=True)

COMFYUI_URL = "http://172.26.112.1:18188"

# ─── 数据模型 ──────────────────────────────

class Project(BaseModel):
    id: str
    name: str
    script: str = ""
    scenes: list = []
    created_at: str = ""

class ScriptInput(BaseModel):
    project_id: str
    content: str

class SceneGenerate(BaseModel):
    project_id: str
    num_scenes: int = 5

# ─── 内存存储 ──────────────────────────────

projects: dict[str, Project] = {}

def auto_split_scenes(script: str, num: int = 5) -> list[dict]:
    """简易剧本→分镜（后面接 AI）"""
    chunks = [s.strip() for s in script.replace("。", "。\n").split("\n") if s.strip()]
    scenes = []
    for i, chunk in enumerate(chunks[:num]):
        scenes.append({
            "id": f"s{i+1}",
            "number": i+1,
            "summary": chunk[:80] + ("..." if len(chunk)>80 else ""),
            "full_text": chunk,
            "prompt_cn": "",
            "prompt_en": "",
            "image_url": "",
            "video_url": "",
            "status": "pending"
        })
    return scenes

# ─── API ────────────────────────────────────

@app.post("/api/projects")
def create_project(data: dict):
    pid = uuid.uuid4().hex[:8]
    proj = Project(
        id=pid,
        name=data.get("name", "未命名"),
        created_at=time.strftime("%Y-%m-%d %H:%M")
    )
    projects[pid] = proj
    (WORKSPACE / pid).mkdir(exist_ok=True)
    return proj.model_dump()

@app.get("/api/projects")
def list_projects():
    return [p.model_dump() for p in projects.values()]

@app.get("/api/projects/{pid}")
def get_project(pid: str):
    if pid not in projects:
        raise HTTPException(404)
    return projects[pid].model_dump()

@app.post("/api/projects/{pid}/script")
def save_script(pid: str, data: ScriptInput):
    if pid not in projects:
        raise HTTPException(404)
    projects[pid].script = data.content
    return {"ok": True}

@app.post("/api/projects/{pid}/scenes/generate")
def generate_scenes(pid: str, data: SceneGenerate):
    if pid not in projects:
        raise HTTPException(404)
    script = projects[pid].script
    if not script:
        raise HTTPException(400, detail="请先输入剧本")
    scenes = auto_split_scenes(script, data.num_scenes)
    projects[pid].scenes = scenes
    return {"scenes": scenes, "count": len(scenes)}

@app.get("/api/projects/{pid}/scenes")
def get_scenes(pid: str):
    if pid not in projects:
        raise HTTPException(404)
    return projects[pid].scenes

@app.get("/api/status")
def status():
    return {"comfyui": COMFYUI_URL, "projects": len(projects)}

# 首页
@app.get("/")
def index():
    return HTMLResponse(open(Path(__file__).parent / "index.html").read())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("pipeline_server:app", host="0.0.0.0", port=18888, reload=True)
