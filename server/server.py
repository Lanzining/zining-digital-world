from fastapi import FastAPI, HTTPException, Request, UploadFile, File, Form
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pathlib import Path
from datetime import datetime, timezone
import hashlib,hmac,json,os,secrets,uuid

ROOT=Path(__file__).resolve().parent.parent
DATA=ROOT/"data"/"site.json"; MEDIA=ROOT/"media"; INDEX=ROOT/"index.html"; CONTROL=ROOT/"control.html"
MEDIA.mkdir(parents=True,exist_ok=True); DATA.parent.mkdir(parents=True,exist_ok=True)
DEFAULT={"title":"在世界之外，留一方属于我的世界。","sub":"A private world by L · ZINING.","intro":"这里不用于介绍我。这里保存我在数字世界里留下的痕迹。","mood":"calm","settings":{"sound":True,"daynight":True,"motion":True},"memories":[],"thoughts":[],"journey":[],"music":[],"collection":[],"future":[]}
if not DATA.exists(): DATA.write_text(json.dumps(DEFAULT,ensure_ascii=False,indent=2),encoding="utf-8")
app=FastAPI(title="L · ZINING")
app.mount("/media",StaticFiles(directory=str(MEDIA)),name="media")
ADMIN_PASSWORD=os.getenv("ADMIN_PASSWORD") or secrets.token_urlsafe(24)
SESSION_SECRET=os.getenv("SESSION_SECRET") or secrets.token_urlsafe(32)
COOKIE="lz_admin"

class Home(BaseModel):
    title:str; sub:str; intro:str=""
class MemoryEdit(BaseModel):
    title:str=""; caption:str=""; date:str=""; visibility:str="public"
class TextItem(BaseModel):
    title:str=""; body:str=""; date:str=""; tag:str=""

def read_data():
    try:d=json.loads(DATA.read_text(encoding="utf-8"))
    except:d=dict(DEFAULT)
    for k,v in DEFAULT.items(): d.setdefault(k,v)
    return d
def write_data(d): DATA.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding="utf-8")
def token(): return hmac.new(SESSION_SECRET.encode(),b"admin",hashlib.sha256).hexdigest()
def is_admin(r): return hmac.compare_digest(r.cookies.get(COOKIE,""),token())
def auth(r):
    if not is_admin(r): raise HTTPException(401,"未授权")

@app.get("/")
def home(): return FileResponse(INDEX)
@app.get("/control")
def control(): return FileResponse(CONTROL)

@app.get("/api/public")
def public():
    d=read_data()
    out=dict(d)
    out["memories"]=[m for m in d["memories"] if m.get("visibility","public")=="public"]
    out["private_count"]=sum(1 for m in d["memories"] if m.get("visibility")=="private")
    return out

@app.post("/api/admin/login")
def login(payload:dict):
    if not hmac.compare_digest(str(payload.get("password","")),ADMIN_PASSWORD): raise HTTPException(401,"密码不正确")
    r=JSONResponse({"ok":True}); r.set_cookie(COOKIE,token(),httponly=True,secure=True,samesite="lax",max_age=43200); return r
@app.post("/api/admin/logout")
def logout():
    r=JSONResponse({"ok":True}); r.delete_cookie(COOKIE); return r
@app.get("/api/admin/me")
def me(r:Request): return {"authenticated":is_admin(r)}
@app.get("/api/admin/data")
def admin_data(r:Request): auth(r); return read_data()

@app.post("/api/admin/home")
def home_update(x:Home,r:Request):
    auth(r); d=read_data(); d["title"]=x.title; d["sub"]=x.sub; d["intro"]=x.intro; write_data(d); return {"ok":True,"data":d}
@app.post("/api/admin/settings")
def settings(payload:dict,r:Request):
    auth(r); d=read_data(); s=d["settings"]
    for k in ("sound","daynight","motion"):
        if k in payload:s[k]=bool(payload[k])
    write_data(d); return {"ok":True,"settings":s}
@app.post("/api/admin/mood")
def mood(payload:dict,r:Request):
    auth(r); d=read_data(); d["mood"]=payload.get("mood","calm"); write_data(d); return {"ok":True,"mood":d["mood"]}

@app.post("/api/admin/text/{kind}")
def add_text(kind:str,x:TextItem,r:Request):
    auth(r)
    if kind not in ("thoughts","journey","music","collection","future"): raise HTTPException(400,"内容类型无效")
    d=read_data(); item={"id":uuid.uuid4().hex,"title":x.title.strip(),"body":x.body.strip(),"date":x.date.strip(),"tag":x.tag.strip(),"created_at":datetime.now(timezone.utc).isoformat()}
    d[kind].insert(0,item); write_data(d); return {"ok":True,"item":item}
@app.delete("/api/admin/text/{kind}/{item_id}")
def delete_text(kind:str,item_id:str,r:Request):
    auth(r)
    if kind not in ("thoughts","journey","music","collection","future"): raise HTTPException(400,"内容类型无效")
    d=read_data(); before=len(d[kind]); d[kind]=[x for x in d[kind] if x.get("id")!=item_id]
    if len(d[kind])==before: raise HTTPException(404,"内容不存在")
    write_data(d); return {"ok":True}

@app.get("/api/admin/memories")
def memories(r:Request): auth(r); return {"memories":read_data()["memories"]}
@app.post("/api/admin/memories")
async def upload_memory(request:Request,image:UploadFile=File(...),title:str=Form(""),caption:str=Form(""),date:str=Form(""),visibility:str=Form("public")):
    auth(request)
    allowed={"image/jpeg":".jpg","image/png":".png","image/webp":".webp","image/gif":".gif"}
    if image.content_type not in allowed: raise HTTPException(400,"只支持 JPG、PNG、WEBP、GIF")
    raw=await image.read()
    if len(raw)>8*1024*1024: raise HTTPException(413,"单张图片不能超过 8MB")
    fn=uuid.uuid4().hex+allowed[image.content_type]; (MEDIA/fn).write_bytes(raw)
    item={"id":uuid.uuid4().hex,"file":f"/media/{fn}","title":title.strip() or "未命名记忆","caption":caption.strip(),"date":date.strip() or datetime.now().strftime("%Y-%m-%d"),"visibility":"private" if visibility=="private" else "public","created_at":datetime.now(timezone.utc).isoformat()}
    d=read_data(); d["memories"].insert(0,item); write_data(d); return {"ok":True,"memory":item}
@app.put("/api/admin/memories/{mid}")
def edit_memory(mid:str,x:MemoryEdit,r:Request):
    auth(r); d=read_data()
    for m in d["memories"]:
        if m.get("id")==mid:
            m.update({"title":x.title.strip() or "未命名记忆","caption":x.caption.strip(),"date":x.date.strip(),"visibility":"private" if x.visibility=="private" else "public"}); write_data(d); return {"ok":True,"memory":m}
    raise HTTPException(404,"记忆不存在")
@app.delete("/api/admin/memories/{mid}")
def delete_memory(mid:str,r:Request):
    auth(r); d=read_data(); target=next((m for m in d["memories"] if m.get("id")==mid),None)
    if not target: raise HTTPException(404,"记忆不存在")
    fn=Path(target.get("file","")).name
    if (MEDIA/fn).exists(): (MEDIA/fn).unlink()
    d["memories"]=[m for m in d["memories"] if m.get("id")!=mid]; write_data(d); return {"ok":True}
