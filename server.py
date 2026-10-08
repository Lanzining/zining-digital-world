"""
L · ZINING V5 backend skeleton
Install: pip install fastapi uvicorn
Run: uvicorn server:app --reload
This is intentionally a starter backend, not production security.
"""
from fastapi import FastAPI
from pydantic import BaseModel
from pathlib import Path
import json

app=FastAPI(title="L ZINING API")
DATA=Path(__file__).parent.parent/"data"/"site.json"
DATA.parent.mkdir(exist_ok=True)
if not DATA.exists():
    DATA.write_text(json.dumps({"title":"在世界之外，留一方属于我的世界。","sub":"Beyond the world, I keep a world of my own.","mood":"calm","settings":{"sound":True,"daynight":True,"motion":True}},ensure_ascii=False),encoding="utf-8")

class Home(BaseModel):
    title:str
    sub:str

def read():
    return json.loads(DATA.read_text(encoding="utf-8"))
def write(d):
    DATA.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding="utf-8")

@app.get("/api/public")
def public():
    d=read()
    return {"title":d["title"],"sub":d["sub"],"mood":d.get("mood","calm"),"settings":d.get("settings",{})}

@app.post("/api/admin/home")
def update_home(home:Home):
    d=read();d["title"]=home.title;d["sub"]=home.sub;write(d)
    return {"ok":True,"data":d}
