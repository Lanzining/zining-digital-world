from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from pathlib import Path
import hashlib
import hmac
import json
import os
import secrets

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "site.json"
INDEX = ROOT / "index.html"
CONTROL = ROOT / "control.html"

DEFAULT = {
    "title": "在世界之外，留一方属于我的世界。",
    "sub": "Beyond the world, I keep a world of my own.",
    "mood": "calm",
    "settings": {"sound": True, "daynight": True, "motion": True},
}

DATA.parent.mkdir(parents=True, exist_ok=True)
if not DATA.exists():
    DATA.write_text(json.dumps(DEFAULT, ensure_ascii=False, indent=2), encoding="utf-8")

app = FastAPI(title="L · ZINING")

# For the free/prototype deployment, set ADMIN_PASSWORD in Render.
# A random fallback prevents the old V5 password from being usable.
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
if not ADMIN_PASSWORD:
    ADMIN_PASSWORD = secrets.token_urlsafe(24)

SESSION_COOKIE = "lz_admin"
SESSION_SECRET = os.getenv("SESSION_SECRET") or secrets.token_urlsafe(32)

class Home(BaseModel):
    title: str
    sub: str

def read_data():
    return json.loads(DATA.read_text(encoding="utf-8"))

def write_data(d):
    DATA.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")

def make_token():
    msg = "admin".encode()
    sig = hmac.new(SESSION_SECRET.encode(), msg, hashlib.sha256).hexdigest()
    return sig

def is_admin(request: Request):
    return hmac.compare_digest(request.cookies.get(SESSION_COOKIE, ""), make_token())

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
    if not is_admin(request):
        raise HTTPException(status_code=401, detail="未授权")
    d = read_data()
    d["title"] = home.title
    d["sub"] = home.sub
    write_data(d)
    return {"ok": True, "data": d}
