"""
星火智画本地版 · AI短剧生产管线
FastAPI 后端 + ComfyUI API + SQLite 持久化
"""
import json, os, asyncio, uuid, time, shutil, io, re, hashlib, base64
from pathlib import Path
from datetime import datetime
from typing import Optional
import sqlite3
import aiosqlite
import aiohttp
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Request
from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ─── 路径配置 ──────────────────────────────
WORKSPACE = Path(os.environ.get("PIPELINE_WORKSPACE", str(Path(__file__).parent / "projects")))
WORKSPACE.mkdir(exist_ok=True)
DB_PATH = WORKSPACE / "spark_ai.db"
UPLOAD_DIR = WORKSPACE / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR = WORKSPACE / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

COMFYUI_URL = os.environ.get("COMFYUI_URL", "http://172.26.112.1:18188")

# ─── 数据库 ────────────────────────────────
def get_db():
    db = sqlite3.connect(str(DB_PATH))
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA journal_mode=WAL")
    return db

def init_db():
    db = get_db()
    db.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        display_name TEXT DEFAULT '',
        created_at TEXT DEFAULT (datetime('now'))
    );
    CREATE TABLE IF NOT EXISTS sessions (
        token TEXT PRIMARY KEY,
        user_id INTEGER NOT NULL,
        created_at TEXT DEFAULT (datetime('now')),
        FOREIGN KEY (user_id) REFERENCES users(id)
    );
    CREATE TABLE IF NOT EXISTS adaptations (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL DEFAULT '未命名项目',
        script TEXT DEFAULT '',
        scenes TEXT DEFAULT '[]',
        status TEXT DEFAULT 'draft',
        source_type TEXT DEFAULT 'manual',
        source_url TEXT DEFAULT '',
        created_at TEXT DEFAULT (datetime('now')),
        updated_at TEXT DEFAULT (datetime('now'))
    );
    CREATE TABLE IF NOT EXISTS image_projects (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL DEFAULT '未命名项目',
        created_at TEXT DEFAULT (datetime('now')),
        updated_at TEXT DEFAULT (datetime('now'))
    );
    CREATE TABLE IF NOT EXISTS image_generations (
        id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        prompt TEXT DEFAULT '',
        negative_prompt TEXT DEFAULT '',
        model TEXT DEFAULT 'qwen-2511-edit',
        width INTEGER DEFAULT 1024,
        height INTEGER DEFAULT 1024,
        aspect_ratio TEXT DEFAULT '1:1',
        num_images INTEGER DEFAULT 1,
        seed INTEGER DEFAULT -1,
        image_url TEXT DEFAULT '',
        status TEXT DEFAULT 'pending',
        created_at TEXT DEFAULT (datetime('now')),
        FOREIGN KEY (project_id) REFERENCES image_projects(id)
    );
    CREATE TABLE IF NOT EXISTS video_projects (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL DEFAULT '未命名项目',
        created_at TEXT DEFAULT (datetime('now')),
        updated_at TEXT DEFAULT (datetime('now'))
    );
    CREATE TABLE IF NOT EXISTS video_generations (
        id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        prompt TEXT DEFAULT '',
        model TEXT DEFAULT 'ltx-director',
        width INTEGER DEFAULT 1920,
        height INTEGER DEFAULT 1080,
        duration REAL DEFAULT 3.0,
        video_url TEXT DEFAULT '',
        status TEXT DEFAULT 'pending',
        created_at TEXT DEFAULT (datetime('now')),
        FOREIGN KEY (project_id) REFERENCES video_projects(id)
    );
    CREATE TABLE IF NOT EXISTS asset_collections (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL DEFAULT '默认集合',
        type TEXT DEFAULT 'image',
        created_at TEXT DEFAULT (datetime('now'))
    );
    CREATE TABLE IF NOT EXISTS assets (
        id TEXT PRIMARY KEY,
        collection_id TEXT NOT NULL,
        name TEXT DEFAULT '',
        file_path TEXT NOT NULL,
        file_type TEXT DEFAULT 'image',
        file_size INTEGER DEFAULT 0,
        created_at TEXT DEFAULT (datetime('now')),
        FOREIGN KEY (collection_id) REFERENCES asset_collections(id)
    );
    """)
    db.commit()
    db.close()

init_db()

# ─── FastAPI App ───────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(title="星火智画 · 本地版", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# ─── 工具函数 ──────────────────────────────
def hash_password(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

def now_str() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M")

def row_to_dict(row) -> dict:
    if row is None: return {}
    return dict(row)

def generate_id() -> str:
    return uuid.uuid4().hex[:12]

# ─── 用户系统 ──────────────────────────────

class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    password: str
    display_name: str = ""

@app.post("/api/auth/register")
def api_register(data: RegisterRequest):
    db = get_db()
    try:
        db.execute("INSERT INTO users (username, password_hash, display_name) VALUES (?, ?, ?)",
                   [data.username, hash_password(data.password), data.display_name or data.username])
        db.commit()
        return {"ok": True, "message": "注册成功"}
    except sqlite3.IntegrityError:
        raise HTTPException(400, "用户名已存在")
    finally:
        db.close()

@app.post("/api/auth/login")
def api_login(data: LoginRequest):
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE username = ?", [data.username]).fetchone()
    if not user or user["password_hash"] != hash_password(data.password):
        raise HTTPException(401, "用户名或密码错误")
    token = uuid.uuid4().hex
    db.execute("INSERT OR REPLACE INTO sessions (token, user_id) VALUES (?, ?)", [token, user["id"]])
    db.commit()
    db.close()
    return {"ok": True, "token": token, "user": {"id": user["id"], "username": user["username"], "display_name": user["display_name"]}}

@app.post("/api/auth/logout")
def api_logout(request: Request):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if token:
        db = get_db()
        db.execute("DELETE FROM sessions WHERE token = ?", [token])
        db.commit()
        db.close()
    return {"ok": True}

def get_user_from_token(token: str) -> Optional[dict]:
    if not token: return None
    db = get_db()
    row = db.execute("SELECT u.* FROM users u JOIN sessions s ON u.id = s.user_id WHERE s.token = ?", [token]).fetchone()
    db.close()
    return row_to_dict(row) if row else None

# ─── 剧本项目 (Adaptations) ────────────────

@app.get("/api/adaptations")
def list_adaptations():
    db = get_db()
    rows = db.execute("SELECT * FROM adaptations ORDER BY updated_at DESC").fetchall()
    db.close()
    return [row_to_dict(r) for r in rows]

@app.post("/api/adaptations")
def create_adaptation(data: dict):
    pid = generate_id()
    db = get_db()
    db.execute("INSERT INTO adaptations (id, name, created_at, updated_at) VALUES (?, ?, ?, ?)",
               [pid, data.get("name", "未命名项目"), now_str(), now_str()])
    db.commit()
    row = db.execute("SELECT * FROM adaptations WHERE id = ?", [pid]).fetchone()
    db.close()
    return row_to_dict(row)

@app.get("/api/adaptations/{pid}")
def get_adaptation(pid: str):
    db = get_db()
    row = db.execute("SELECT * FROM adaptations WHERE id = ?", [pid]).fetchone()
    db.close()
    if not row: raise HTTPException(404, "项目不存在")
    d = row_to_dict(row)
    d["scenes"] = json.loads(d.get("scenes", "[]"))
    return d

@app.put("/api/adaptations/{pid}")
def update_adaptation(pid: str, data: dict):
    db = get_db()
    fields = []
    values = []
    for k in ["name", "script", "scenes", "status", "source_type", "source_url"]:
        if k in data:
            fields.append(f"{k} = ?")
            val = json.dumps(data[k], ensure_ascii=False) if k == "scenes" else data[k]
            values.append(val)
    if fields:
        db.execute(f"UPDATE adaptations SET {', '.join(fields)}, updated_at = ? WHERE id = ?",
                   values + [now_str(), pid])
        db.commit()
    row = db.execute("SELECT * FROM adaptations WHERE id = ?", [pid]).fetchone()
    db.close()
    if not row: raise HTTPException(404)
    d = row_to_dict(row)
    d["scenes"] = json.loads(d.get("scenes", "[]"))
    return d

@app.delete("/api/adaptations/{pid}")
def delete_adaptation(pid: str):
    db = get_db()
    db.execute("DELETE FROM adaptations WHERE id = ?", [pid])
    db.commit()
    db.close()
    return {"ok": True}

@app.post("/api/adaptations/{pid}/scenes/auto-split")
def auto_split_scenes(pid: str, data: dict):
    """自动将剧本拆分为分镜"""
    db = get_db()
    row = db.execute("SELECT * FROM adaptations WHERE id = ?", [pid]).fetchone()
    if not row: raise HTTPException(404)
    script = row["script"] or ""
    if not script: raise HTTPException(400, "请先输入剧本内容")
    
    num = data.get("num_scenes", 5)
    # 按段落/句号拆分
    parts = re.split(r'[。！？\n]+', script)
    parts = [p.strip() for p in parts if len(p.strip()) > 5]
    
    if len(parts) < num:
        # 如果段落不够，按更小的粒度拆分
        parts = re.split(r'[。！？，,；;\n]+', script)
        parts = [p.strip() for p in parts if len(p.strip()) > 3]
    
    scenes = []
    step = max(1, len(parts) // num)
    for i in range(min(num, len(parts))):
        idx = min(i * step + i % step, len(parts) - 1)
        chunk = parts[idx]
        scenes.append({
            "id": f"s{i+1}",
            "number": i + 1,
            "summary": chunk[:100] + ("..." if len(chunk) > 100 else ""),
            "full_text": chunk,
            "prompt_cn": "",
            "prompt_en": "",
            "image_url": "",
            "video_url": "",
            "status": "pending"
        })
    
    scenes_json = json.dumps(scenes, ensure_ascii=False)
    db.execute("UPDATE adaptations SET scenes = ?, updated_at = ? WHERE id = ?", [scenes_json, now_str(), pid])
    db.commit()
    db.close()
    return {"scenes": scenes, "count": len(scenes)}

@app.put("/api/adaptations/{pid}/scenes/{sid}")
def update_scene(pid: str, sid: str, data: dict):
    db = get_db()
    row = db.execute("SELECT * FROM adaptations WHERE id = ?", [pid]).fetchone()
    if not row: raise HTTPException(404)
    scenes = json.loads(row["scenes"] or "[]")
    for s in scenes:
        if s["id"] == sid:
            for k in ["prompt_cn", "prompt_en", "summary", "full_text", "status"]:
                if k in data:
                    s[k] = data[k]
            break
    db.execute("UPDATE adaptations SET scenes = ?, updated_at = ? WHERE id = ?",
               [json.dumps(scenes, ensure_ascii=False), now_str(), pid])
    db.commit()
    db.close()
    return {"ok": True, "scene": next((s for s in scenes if s["id"] == sid), {})}

# ─── 图片设计 (Image Projects) ─────────────

@app.get("/api/image-projects")
def list_image_projects():
    db = get_db()
    rows = db.execute("""
        SELECT ip.*, 
               (SELECT COUNT(*) FROM image_generations WHERE project_id = ip.id) as image_count
        FROM image_projects ip ORDER BY updated_at DESC
    """).fetchall()
    db.close()
    return [row_to_dict(r) for r in rows]

@app.post("/api/image-projects")
def create_image_project(data: dict):
    pid = generate_id()
    db = get_db()
    db.execute("INSERT INTO image_projects (id, name, created_at, updated_at) VALUES (?, ?, ?, ?)",
               [pid, data.get("name", "未命名项目"), now_str(), now_str()])
    db.commit()
    row = db.execute("SELECT * FROM image_projects WHERE id = ?", [pid]).fetchone()
    db.close()
    return row_to_dict(row)

@app.get("/api/image-projects/{pid}")
def get_image_project(pid: str):
    db = get_db()
    row = db.execute("SELECT * FROM image_projects WHERE id = ?", [pid]).fetchone()
    gens = db.execute("SELECT * FROM image_generations WHERE project_id = ? ORDER BY created_at DESC", [pid]).fetchall()
    db.close()
    if not row: raise HTTPException(404)
    d = row_to_dict(row)
    d["generations"] = [row_to_dict(g) for g in gens]
    return d

@app.put("/api/image-projects/{pid}")
def update_image_project(pid: str, data: dict):
    db = get_db()
    if "name" in data:
        db.execute("UPDATE image_projects SET name = ?, updated_at = ? WHERE id = ?", [data["name"], now_str(), pid])
        db.commit()
    db.close()
    return {"ok": True}

@app.delete("/api/image-projects/{pid}")
def delete_image_project(pid: str):
    db = get_db()
    db.execute("DELETE FROM image_generations WHERE project_id = ?", [pid])
    db.execute("DELETE FROM image_projects WHERE id = ?", [pid])
    db.commit()
    db.close()
    return {"ok": True}

# ─── 图片生成 API ──────────────────────────
class ImageGenRequest(BaseModel):
    project_id: str
    prompt: str
    negative_prompt: str = ""
    model: str = "qwen-2511-edit"
    width: int = 1024
    height: int = 1024
    aspect_ratio: str = "1:1"
    num_images: int = 1
    seed: int = -1

@app.post("/api/generate-image")
async def generate_image(data: ImageGenRequest):
    """调用 ComfyUI Qwen 2511 Edit 工作流生成图片"""
    gen_id = generate_id()
    
    # 保存到数据库
    db = get_db()
    db.execute("""INSERT INTO image_generations (id, project_id, prompt, negative_prompt, model, width, height, aspect_ratio, num_images, seed, status)
                  VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'generating')""",
               [gen_id, data.project_id, data.prompt, data.negative_prompt, data.model, 
                data.width, data.height, data.aspect_ratio, data.num_images, data.seed])
    db.execute("UPDATE image_projects SET updated_at = ? WHERE id = ?", [now_str(), data.project_id])
    db.commit()
    db.close()
    
    try:
        # 调用 ComfyUI API
        image_url = await call_comfyui_image(data.prompt, data.width, data.height, data.seed)
        
        db = get_db()
        db.execute("UPDATE image_generations SET status = 'done', image_url = ? WHERE id = ?", [image_url, gen_id])
        db.commit()
        db.close()
        return {"ok": True, "id": gen_id, "image_url": image_url, "status": "done"}
    except Exception as e:
        db = get_db()
        db.execute("UPDATE image_generations SET status = 'failed' WHERE id = ?", [gen_id])
        db.commit()
        db.close()
        raise HTTPException(500, f"ComfyUI 生成失败: {str(e)}")

async def call_comfyui_image(prompt: str, width: int = 1024, height: int = 1024, seed: int = -1) -> str:
    """调用 ComfyUI 生成图片 - Qwen 2511 Edit 工作流"""
    if seed < 0:
        seed = int(time.time() * 1000) % 2147483647
    
    workflow = {
        "3": {"class_type": "KSampler", "inputs": {"seed": seed, "steps": 20, "cfg": 7, "sampler_name": "euler", "scheduler": "normal", "denoise": 1, "model": ["4", 0], "positive": ["6", 0], "negative": ["7", 0], "latent_image": ["5", 0]}},
        "4": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": "qwen2511_edit.safetensors"}},
        "5": {"class_type": "EmptyLatentImage", "inputs": {"width": width, "height": height, "batch_size": 1}},
        "6": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip": ["4", 1]}},
        "7": {"class_type": "CLIPTextEncode", "inputs": {"text": "", "clip": ["4", 1]}},
        "8": {"class_type": "VAEDecode", "inputs": {"samples": ["3", 0], "vae": ["4", 2]}},
        "9": {"class_type": "SaveImage", "inputs": {"filename_prefix": "spark_ai", "images": ["8", 0]}},
    }
    
    async with aiohttp.ClientSession() as session:
        # Queue prompt
        payload = {"prompt": workflow, "client_id": "spark_ai_local"}
        async with session.post(f"{COMFYUI_URL}/prompt", json=payload) as resp:
            if resp.status != 200:
                raise Exception(f"ComfyUI prompt 错误: {resp.status}")
            result = await resp.json()
            prompt_id = result.get("prompt_id")
        
        if not prompt_id:
            raise Exception("未获取到 prompt_id")
        
        # 等待生成完成
        for _ in range(120):  # 最多等 2 分钟
            await asyncio.sleep(1)
            async with session.get(f"{COMFYUI_URL}/history/{prompt_id}") as hist_resp:
                if hist_resp.status != 200:
                    continue
                history = await hist_resp.json()
                if prompt_id in history:
                    outputs = history[prompt_id].get("outputs", {})
                    for node_id, node_output in outputs.items():
                        images = node_output.get("images", [])
                        if images:
                            img = images[0]
                            filename = img["filename"]
                            subfolder = img.get("subfolder", "")
                            # 复制到本地 outputs 目录
                            img_url = f"{COMFYUI_URL}/view?filename={filename}&subfolder={subfolder}&type=output"
                            # 尝试下载到本地
                            try:
                                async with session.get(img_url) as img_resp:
                                    if img_resp.status == 200:
                                        content = await img_resp.read()
                                        local_path = OUTPUT_DIR / filename
                                        local_path.write_bytes(content)
                                        return f"/api/outputs/{filename}"
                            except:
                                pass
                            return img_url
        raise Exception("生成超时")

# ─── 视频项目 (Video Projects) ─────────────

@app.get("/api/video-projects")
def list_video_projects():
    db = get_db()
    rows = db.execute("""
        SELECT vp.*, 
               (SELECT COUNT(*) FROM video_generations WHERE project_id = vp.id) as video_count
        FROM video_projects vp ORDER BY updated_at DESC
    """).fetchall()
    db.close()
    return [row_to_dict(r) for r in rows]

@app.post("/api/video-projects")
def create_video_project(data: dict):
    pid = generate_id()
    db = get_db()
    db.execute("INSERT INTO video_projects (id, name, created_at, updated_at) VALUES (?, ?, ?, ?)",
               [pid, data.get("name", "未命名项目"), now_str(), now_str()])
    db.commit()
    row = db.execute("SELECT * FROM video_projects WHERE id = ?", [pid]).fetchone()
    db.close()
    return row_to_dict(row)

@app.get("/api/video-projects/{pid}")
def get_video_project(pid: str):
    db = get_db()
    row = db.execute("SELECT * FROM video_projects WHERE id = ?", [pid]).fetchone()
    gens = db.execute("SELECT * FROM video_generations WHERE project_id = ? ORDER BY created_at DESC", [pid]).fetchall()
    db.close()
    if not row: raise HTTPException(404)
    d = row_to_dict(row)
    d["generations"] = [row_to_dict(g) for g in gens]
    return d

@app.put("/api/video-projects/{pid}")
def update_video_project(pid: str, data: dict):
    db = get_db()
    if "name" in data:
        db.execute("UPDATE video_projects SET name = ?, updated_at = ? WHERE id = ?", [data["name"], now_str(), pid])
        db.commit()
    db.close()
    return {"ok": True}

@app.delete("/api/video-projects/{pid}")
def delete_video_project(pid: str):
    db = get_db()
    db.execute("DELETE FROM video_generations WHERE project_id = ?", [pid])
    db.execute("DELETE FROM video_projects WHERE id = ?", [pid])
    db.commit()
    db.close()
    return {"ok": True}

# ─── 视频生成 API ──────────────────────────
class VideoGenRequest(BaseModel):
    project_id: str
    prompt: str
    model: str = "ltx-director"
    width: int = 1920
    height: int = 1080
    duration: float = 3.0
    seed: int = -1

@app.post("/api/generate-video")
async def generate_video(data: VideoGenRequest):
    """调用 ComfyUI LTX Director 工作流生成视频"""
    gen_id = generate_id()
    
    db = get_db()
    db.execute("""INSERT INTO video_generations (id, project_id, prompt, model, width, height, duration, status)
                  VALUES (?, ?, ?, ?, ?, ?, ?, 'generating')""",
               [gen_id, data.project_id, data.prompt, data.model, data.width, data.height, data.duration])
    db.execute("UPDATE video_projects SET updated_at = ? WHERE id = ?", [now_str(), data.project_id])
    db.commit()
    db.close()
    
    try:
        video_url = await call_comfyui_video(data.prompt, data.width, data.height, data.duration, data.seed)
        db = get_db()
        db.execute("UPDATE video_generations SET status = 'done', video_url = ? WHERE id = ?", [video_url, gen_id])
        db.commit()
        db.close()
        return {"ok": True, "id": gen_id, "video_url": video_url, "status": "done"}
    except Exception as e:
        db = get_db()
        db.execute("UPDATE video_generations SET status = 'failed' WHERE id = ?", [gen_id])
        db.commit()
        db.close()
        raise HTTPException(500, f"ComfyUI 视频生成失败: {str(e)}")

async def call_comfyui_video(prompt: str, width: int = 1920, height: int = 1080, duration: float = 3.0, seed: int = -1) -> str:
    """调用 ComfyUI LTX Director 生成视频"""
    if seed < 0:
        seed = int(time.time() * 1000) % 2147483647
    
    num_frames = int(duration * 24)  # 24fps
    
    workflow = {
        "3": {"class_type": "KSampler", "inputs": {"seed": seed, "steps": 20, "cfg": 7, "sampler_name": "euler", "scheduler": "normal", "denoise": 1, "model": ["4", 0], "positive": ["6", 0], "negative": ["7", 0], "latent_image": ["5", 0]}},
        "4": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": "ltx_director.safetensors"}},
        "5": {"class_type": "EmptyLatentImage", "inputs": {"width": width, "height": height, "batch_size": num_frames}},
        "6": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip": ["4", 1]}},
        "7": {"class_type": "CLIPTextEncode", "inputs": {"text": "", "clip": ["4", 1]}},
        "8": {"class_type": "VAEDecode", "inputs": {"samples": ["3", 0], "vae": ["4", 2]}},
        "9": {"class_type": "VHS_VideoCombine", "inputs": {"frame_rate": 24, "format": "video/h264-mp4", "images": ["8", 0], "filename_prefix": "spark_video"}},
    }
    
    async with aiohttp.ClientSession() as session:
        payload = {"prompt": workflow, "client_id": "spark_ai_video"}
        async with session.post(f"{COMFYUI_URL}/prompt", json=payload) as resp:
            if resp.status != 200:
                raise Exception(f"ComfyUI prompt 错误: {resp.status}")
            result = await resp.json()
            prompt_id = result.get("prompt_id")
        
        if not prompt_id:
            raise Exception("未获取到 prompt_id")
        
        # 等待生成完成（视频需要更长时间）
        for _ in range(300):  # 最多等 5 分钟
            await asyncio.sleep(2)
            async with session.get(f"{COMFYUI_URL}/history/{prompt_id}") as hist_resp:
                if hist_resp.status != 200:
                    continue
                history = await hist_resp.json()
                if prompt_id in history:
                    outputs = history[prompt_id].get("outputs", {})
                    for node_id, node_output in outputs.items():
                        gifs = node_output.get("gifs", [])
                        if gifs:
                            gif = gifs[0]
                            filename = gif["filename"]
                            subfolder = gif.get("subfolder", "")
                            video_url = f"{COMFYUI_URL}/view?filename={filename}&subfolder={subfolder}&type=output"
                            try:
                                async with session.get(video_url) as vid_resp:
                                    if vid_resp.status == 200:
                                        content = await vid_resp.read()
                                        local_path = OUTPUT_DIR / filename
                                        local_path.write_bytes(content)
                                        return f"/api/outputs/{filename}"
                            except:
                                pass
                            return video_url
        raise Exception("视频生成超时")

# ─── 资产库 (Asset Library) ────────────────

@app.get("/api/asset-collections")
def list_asset_collections():
    db = get_db()
    rows = db.execute("SELECT * FROM asset_collections ORDER BY created_at DESC").fetchall()
    db.close()
    return [row_to_dict(r) for r in rows]

@app.post("/api/asset-collections")
def create_asset_collection(data: dict):
    cid = generate_id()
    db = get_db()
    db.execute("INSERT INTO asset_collections (id, name, type, created_at) VALUES (?, ?, ?, ?)",
               [cid, data.get("name", "新建集合"), data.get("type", "image"), now_str()])
    db.commit()
    row = db.execute("SELECT * FROM asset_collections WHERE id = ?", [cid]).fetchone()
    db.close()
    return row_to_dict(row)

@app.delete("/api/asset-collections/{cid}")
def delete_asset_collection(cid: str):
    db = get_db()
    db.execute("DELETE FROM assets WHERE collection_id = ?", [cid])
    db.execute("DELETE FROM asset_collections WHERE id = ?", [cid])
    db.commit()
    db.close()
    return {"ok": True}

@app.get("/api/asset-collections/{cid}/assets")
def list_assets(cid: str):
    db = get_db()
    rows = db.execute("SELECT * FROM assets WHERE collection_id = ? ORDER BY created_at DESC", [cid]).fetchall()
    db.close()
    return [row_to_dict(r) for r in rows]

@app.post("/api/asset-collections/{cid}/upload")
async def upload_asset(cid: str, file: UploadFile = File(...), name: str = Form("")):
    db = get_db()
    col = db.execute("SELECT * FROM asset_collections WHERE id = ?", [cid]).fetchone()
    if not col:
        db.close()
        raise HTTPException(404, "集合不存在")
    
    ext = Path(file.filename).suffix if file.filename else ".png"
    asset_id = generate_id()
    save_name = f"{asset_id}{ext}"
    save_path = UPLOAD_DIR / save_name
    
    content = await file.read()
    save_path.write_bytes(content)
    
    file_type = "image"
    if ext.lower() in [".mp4", ".webm", ".mov"]:
        file_type = "video"
    
    db.execute("INSERT INTO assets (id, collection_id, name, file_path, file_type, file_size) VALUES (?, ?, ?, ?, ?, ?)",
               [asset_id, cid, name or file.filename or "未命名", str(save_path), file_type, len(content)])
    db.commit()
    row = db.execute("SELECT * FROM assets WHERE id = ?", [asset_id]).fetchone()
    db.close()
    return row_to_dict(row)

@app.delete("/api/assets/{aid}")
def delete_asset(aid: str):
    db = get_db()
    asset = db.execute("SELECT * FROM assets WHERE id = ?", [aid]).fetchone()
    if asset:
        path = Path(asset["file_path"])
        if path.exists():
            path.unlink()
    db.execute("DELETE FROM assets WHERE id = ?", [aid])
    db.commit()
    db.close()
    return {"ok": True}

# ─── 静态文件服务 ──────────────────────────

@app.get("/api/outputs/{filename}")
def serve_output(filename: str):
    path = OUTPUT_DIR / filename
    if path.exists():
        media_type = "video/mp4" if filename.endswith(".mp4") else "image/png"
        return FileResponse(path, media_type=media_type)
    raise HTTPException(404)

@app.get("/api/uploads/{filename}")
def serve_upload(filename: str):
    path = UPLOAD_DIR / filename
    if path.exists():
        return FileResponse(path)
    raise HTTPException(404)

# ─── 状态 ──────────────────────────────────

@app.get("/api/status")
def status():
    db = get_db()
    adapt_count = db.execute("SELECT COUNT(*) FROM adaptations").fetchone()[0]
    img_count = db.execute("SELECT COUNT(*) FROM image_projects").fetchone()[0]
    vid_count = db.execute("SELECT COUNT(*) FROM video_projects").fetchone()[0]
    asset_count = db.execute("SELECT COUNT(*) FROM assets").fetchone()[0]
    db.close()
    return {
        "comfyui_url": COMFYUI_URL,
        "comfyui_status": "unknown",
        "adaptations": adapt_count,
        "image_projects": img_count,
        "video_projects": vid_count,
        "assets": asset_count
    }

# ─── 首页 ──────────────────────────────────

@app.get("/")
def index():
    return HTMLResponse(open(Path(__file__).parent / "index.html", encoding="utf-8").read())

# ─── 启动 ──────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    print(f"✨ 星火智画本地版 启动在 http://localhost:18888")
    print(f"📁 工作目录: {WORKSPACE}")
    print(f"🎨 ComfyUI: {COMFYUI_URL}")
    uvicorn.run("pipeline_server:app", host="0.0.0.0", port=18888, reload=True)
