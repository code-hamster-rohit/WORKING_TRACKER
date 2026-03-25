from dotenv import load_dotenv
import os, datetime

load_dotenv()

import uvicorn
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, FileResponse
from db.rules import add, get, get_all, delete, update
from bson.objectid import ObjectId

app = FastAPI(title="Working Tracker", description="Track your working hours", version="1.0.0")

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    workings = get_all("WORKING_TRACKER", "WORKING_DETAILS", {})
    representative_details = get_all("WORKING_TRACKER", "HQ_DETAILS", {})
    if workings and workings[-1]["date"] == datetime.datetime.now().strftime("%Y-%m-%d"):
        return templates.TemplateResponse(request=request, name="previous_workings.html", context={"previous_workings": sorted(workings, key=lambda x: x["date"])[::-1]})
    else:
        representative_details[0].pop("_id")
        working_with = representative_details[0].keys()
        working_places = representative_details[0].values()
        return templates.TemplateResponse(request=request, name="add_working.html", context={"working_with": working_with, "working_places": working_places, "representative_details": representative_details})

@app.get("/health", response_class=HTMLResponse)
async def health_check():
    return HTMLResponse("OK")

@app.get("/sw.js")
async def service_worker():
    return FileResponse("static/sw.js", media_type="application/javascript")

@app.post("/add-working")
async def add_working(request: Request):
    data = await request.form()
    data = dict(data)
    data["date"] = datetime.datetime.now().strftime("%Y-%m-%d")
    data["doctor-calls"] = int(data["doctor-calls"])
    data["chemist-visits"] = int(data["chemist-visits"])
    data["working-with"] = data["working-with"].lower()
    data["working-place"] = data["working-place"].lower()
    data["note"] = data["note"].lower()
    data["remarks"] = data["remarks"].lower()
    add("WORKING_TRACKER", "WORKING_DETAILS", data)
    return templates.TemplateResponse(request=request, name="previous_workings.html", context={"previous_workings": sorted(get_all("WORKING_TRACKER", "WORKING_DETAILS", {}), key=lambda x: x["date"])[::-1]})

@app.get("/previous-workings", response_class=HTMLResponse)
async def previous_workings(request: Request):
    return templates.TemplateResponse(request=request, name="previous_workings.html", context={"previous_workings": sorted(get_all("WORKING_TRACKER", "WORKING_DETAILS", {}), key=lambda x: x["date"])[::-1]})

@app.post("/update-working")
async def update_working(request: Request):
    data = await request.form()
    data = dict(data)
    working_id = data.pop("id", None)
    
    if "doctor-calls" in data: data["doctor-calls"] = int(data["doctor-calls"])
    if "chemist-visits" in data: data["chemist-visits"] = int(data["chemist-visits"])
    if "working-with" in data: data["working-with"] = data["working-with"].lower()
    if "working-place" in data: data["working-place"] = data["working-place"].lower()
    if "note" in data: data["note"] = data["note"].lower()
    if "remarks" in data: data["remarks"] = data["remarks"].lower()

    if working_id:
        update("WORKING_TRACKER", "WORKING_DETAILS", {"_id": ObjectId(working_id)}, data)
        
    return templates.TemplateResponse(request=request, name="previous_workings.html", context={"previous_workings": get_all("WORKING_TRACKER", "WORKING_DETAILS", {})})

@app.get("/settings", response_class=HTMLResponse)
async def settings(request: Request):
    representative_details = get_all("WORKING_TRACKER", "HQ_DETAILS", {})
    representative_details[0].pop("_id")
    working_with = representative_details[0].keys()
    return templates.TemplateResponse(request=request, name="settings.html", context={"working_with": working_with, "representative_details": representative_details})

@app.post("/settings")
async def settings_post(request: Request):
    data = await request.form()
    action = data.get("action", "update")
    name = data.get("name", "").strip().lower()
    
    if not name:
        return await settings(request)
        
    representative_details = get_all("WORKING_TRACKER", "HQ_DETAILS", {})
    if not representative_details:
        add("WORKING_TRACKER", "HQ_DETAILS", {})
        representative_details = get_all("WORKING_TRACKER", "HQ_DETAILS", {})
        
    doc_id = representative_details[0]["_id"]

    if action == "delete":
        delete("WORKING_TRACKER", "HQ_DETAILS", {"_id": doc_id}, {name: ""})
    else:
        place_str = data.get("place", "")
        place_str = place_str.replace(",", ";").replace("|", ";")
        places = [p.strip().lower() for p in place_str.split(";") if p.strip()]
        
        update("WORKING_TRACKER", "HQ_DETAILS", {"_id": doc_id}, {name: places})

    representative_details = get_all("WORKING_TRACKER", "HQ_DETAILS", {})
    if representative_details:
        representative_details[0].pop("_id", None)
        working_with = list(representative_details[0].keys())
    else:
        working_with = []
        
    return templates.TemplateResponse(request=request, name="settings.html", context={"working_with": working_with, "representative_details": representative_details})