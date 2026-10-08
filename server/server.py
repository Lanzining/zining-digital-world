from fastapi import FastAPI, HTTPException, Request, UploadFile, File, Form
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pathlib import Path
import hashlib
import hmac
import json
import os
import secrets
import uuid
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "site.json"
MEDIA = ROOT / "media"
INDEX = ROOT / "index.html"
CONTROL = ROOT / "control.html"
MEDIA.mkdir(parents=True, exist_ok=True)

DEFAULT = {
    "title": "在世界之外，留一方属于我的世界。",
    "sub": "Beyond the world, I keep a world of my own.",
    "mood": "calm",
    "settings": {"sound": True, "daynight": True, "motion": True},
    "memories": []
}

DATA.parent.mkdir(parents=True, exist_ok=True)
if not DATA.exists():
    DATA.write_text(json.dumps(DEFAULT, ensure_ascii=False, indent=2), encoding="utf-8")

app = FastAPI(title="L · ZINING")
app.mount("/media", StaticFiles(directory=str(MEDIA)), name="media")

ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
if not ADMIN_PASSWORD:
    ADMIN_PASSWORD = secrets.token_urlsafe(24)

SESSION_COOKIE = "lz_admin"
SESSION_SECRET = os.getenv("SESSION_SECRET") or secrets.token_urlsafe(32)

class Home(BaseModel):
    title: str
    sub: str

class WorldSettings(BaseModel):
    sound: bool = True
    daynight: bool = True
    motion: bool = True

class MemoryEdit(BaseModel):
    title: str = ""
    caption: str = ""
    date: str = ""
    visibility: str = "public"

def read_data():
    try:
        d = json.loads(DATA.read_text(encoding="utf-8"))
    except Exception:
        d = dict(DEFAULT)
    d.setdefault("memories", [])
    return d

def write_data(d):
    DATA.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")

def make_token():
    return hmac.new(SESSION_SECRET.encode(), b"admin", hashlib.sha256).hexdigest()

def is_admin(request: Request):
    return hmac.compare_digest(request.cookies.get(SESSION_COOKIE, ""), make_token())

def require_admin(request: Request):
    if not is_admin(request):
        raise HTTPException(status_code=401, detail="未授权")

@app.get("/")
def home():
    return FileResponse(INDEX)

@app.get("/control")
def control():
    return FileResponse(CONTROL)

@app.get("/api/public")
def public():
    d = read_data()
    return {
        "title": d.get("title", DEFAULT["title"]),
        "sub": d.get("sub", DEFAULT["sub"]),
        "mood": d.get("mood", "calm"),
        "settings": d.get("settings", {}),
        "memories": [
            m for m in d.get("memories", [])
            if m.get("visibility", "public") == "public"
        ],
    }

@app.post("/api/admin/login")
def login(payload: dict):
    password = str(payload.get("password", ""))
    if not hmac.compare_digest(password, ADMIN_PASSWORD):
        raise HTTPException(status_code=401, detail="密码不正确")
    response = JSONResponse({"ok": True})
    response.set_cookie(
        SESSION_COOKIE,
        make_token(),
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=60 * 60 * 12,
    )
    return response

@app.post("/api/admin/logout")
def logout():
    response = JSONResponse({"ok": True})
    response.delete_cookie(SESSION_COOKIE)
    return response

@app.get("/api/admin/me")
def me(request: Request):
    return {"authenticated": is_admin(request)}

@app.post("/api/admin/home")
def update_home(home: Home, request: Request):
    require_admin(request)
    d = read_data()
    d["title"] = home.title
    d["sub"] = home.sub
    write_data(d)
    return {"ok": True, "data": d}

@app.get("/api/admin/settings")
def admin_settings(request: Request):
    require_admin(request)
    d = read_data()
    settings = d.get("settings", {})
    return {"settings": {"sound": bool(settings.get("sound", True)), "daynight": bool(settings.get("daynight", True)), "motion": bool(settings.get("motion", True))}}

@app.post("/api/admin/settings")
def update_settings(settings: WorldSettings, request: Request):
    require_admin(request)
    d = read_data()
    d["settings"] = settings.model_dump()
    write_data(d)
    return {"ok": True, "settings": d["settings"]}

@app.get("/api/admin/memories")
def admin_memories(request: Request):
    require_admin(request)
    return {"memories": read_data().get("memories", [])}

@app.post("/api/admin/memories")
async def upload_memory(
    request: Request,
    image: UploadFile = File(...),
    title: str = Form(""),
    caption: str = Form(""),
    date: str = Form(""),
    visibility: str = Form("public"),
):
    require_admin(request)

    allowed = {"image/jpeg", "image/png", "image/webp", "image/gif"}
    if image.content_type not in allowed:
        raise HTTPException(status_code=400, detail="只支持 JPG、PNG、WEBP、GIF 图片")

    data = await image.read()
    if len(data) > 8 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="单张图片不能超过 8MB")

    ext_map = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
        "image/gif": ".gif",
    }
    filename = f"{uuid.uuid4().hex}{ext_map[image.content_type]}"
    (MEDIA / filename).write_bytes(data)

    item = {
        "id": uuid.uuid4().hex,
        "file": f"/media/{filename}",
        "title": title.strip() or "Untitled Memory",
        "caption": caption.strip(),
        "date": date.strip() or datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "visibility": "private" if visibility == "private" else "public",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    d = read_data()
    d.setdefault("memories", [])
    d["memories"].insert(0, item)
    write_data(d)
    return {"ok": True, "memory": item}

@app.put("/api/admin/memories/{memory_id}")
def edit_memory(memory_id: str, payload: MemoryEdit, request: Request):
    require_admin(request)
    d = read_data()
    for m in d.get("memories", []):
        if m.get("id") == memory_id:
            m["title"] = payload.title.strip() or "Untitled Memory"
            m["caption"] = payload.caption.strip()
            m["date"] = payload.date.strip()
            m["visibility"] = "private" if payload.visibility == "private" else "public"
            write_data(d)
            return {"ok": True, "memory": m}
    raise HTTPException(status_code=404, detail="记忆不存在")

@app.delete("/api/admin/memories/{memory_id}")
def delete_memory(memory_id: str, request: Request):
    require_admin(request)
    d = read_data()
    memories = d.get("memories", [])
    target = next((m for m in memories if m.get("id") == memory_id), None)
    if not target:
        raise HTTPException(status_code=404, detail="记忆不存在")

    filename = Path(target.get("file", "")).name
    path = MEDIA / filename
    if path.exists():
        path.unlink()

    d["memories"] = [m for m in memories if m.get("id") != memory_id]
    write_data(d)
    return {"ok": True}
