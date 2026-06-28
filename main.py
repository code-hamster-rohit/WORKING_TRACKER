from dotenv import load_dotenv
import os, datetime

load_dotenv()

import uvicorn
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from db.rules import add, get, get_all, delete, update, delete_document
from bson.objectid import ObjectId
import json, zipfile, shutil
from gdrive_service import upload_file, download_file, get_available_backup_months

def get_grouped_workings(selected_month: str = None):
    workings = sorted(get_all("WORKING_TRACKER", "WORKING_DETAILS", {}), key=lambda x: x["date"])[::-1]
    
    if not selected_month:
        selected_month = datetime.datetime.now().strftime("%Y-%m")
        
    local_months = [w["date"][:7] for w in workings]
    backup_months = get_available_backup_months()
    available_months = sorted(list(set(local_months + backup_months)))
    
    # Try fetching from GDrive if selected month is in the past but not locally available
    if selected_month and selected_month < datetime.datetime.now().strftime("%Y-%m") and selected_month not in local_months:
        zip_filename = f"backup_{selected_month}.zip"
        json_filename = f"workings_{selected_month}.json"
        
        tmp_zip = os.path.join("/tmp" if os.environ.get("VERCEL") else ".", zip_filename)
        tmp_json = os.path.join("/tmp" if os.environ.get("VERCEL") else ".", json_filename)
        
        try:
            if download_file(zip_filename, tmp_zip):
                with zipfile.ZipFile(tmp_zip, 'r') as zipf:
                    # extractall is safer for changing output dir
                    zipf.extractall(path="/tmp" if os.environ.get("VERCEL") else ".")
                    
                with open(tmp_json, 'r') as f:
                    backup_data = json.load(f)
                
                for w in backup_data:
                    w["is_backup"] = True
                
                workings.extend(backup_data)
                workings = sorted(workings, key=lambda x: x["date"])[::-1]
                
                if os.path.exists(tmp_zip): os.remove(tmp_zip)
                if os.path.exists(tmp_json): os.remove(tmp_json)
                
                local_months = [w["date"][:7] for w in workings]
                available_months = sorted(list(set(local_months + backup_months)))
        except Exception as e:
            print("Could not fetch backup from GDrive:", e)

    min_month = available_months[0] if available_months else selected_month
    max_month = available_months[-1] if available_months else selected_month
        
    grouped = {}
    for w in workings:
        if w["date"].startswith(selected_month):
            d = datetime.datetime.strptime(w["date"], "%Y-%m-%d")
            year = d.strftime("%Y")
            month = d.strftime("%B")
            if year not in grouped:
                grouped[year] = {}
            if month not in grouped[year]:
                grouped[year][month] = []
            grouped[year][month].append(w)
    return grouped, selected_month, min_month, max_month

app = FastAPI(title="Working Tracker", description="Track your working hours", version="1.0.0")

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

@app.get("/backup")
async def backup_data(request: Request):
    expected_secret = os.environ.get("CRON_SECRET")
    if expected_secret:
        auth_header = request.headers.get("Authorization")
        if not auth_header or auth_header != f"Bearer {expected_secret}":
            return JSONResponse({"status": "error", "message": "Unauthorized"}, status_code=401)
            
    workings = get_all("WORKING_TRACKER", "WORKING_DETAILS", {})
    if not workings:
        return JSONResponse({"status": "success", "message": "No data to backup."})
        
    current_month = datetime.datetime.now().strftime("%Y-%m")
    to_backup = [w for w in workings if w["date"][:7] < current_month]
    
    if not to_backup:
        return JSONResponse({"status": "success", "message": "No past data to backup."})
        
    grouped = {}
    for w in to_backup:
        month_key = w["date"][:7]
        if month_key not in grouped:
            grouped[month_key] = []
        w_copy = w.copy()
        w_copy["_id"] = str(w_copy["_id"])
        grouped[month_key].append(w_copy)
        
    tmp_dir = "/tmp/backups" if os.environ.get("VERCEL") else "backups"
    os.makedirs(tmp_dir, exist_ok=True)
    
    backup_months = get_available_backup_months()
    
    for month_key, month_workings in grouped.items():
        json_filename = f"workings_{month_key}.json"
        zip_filename = f"backup_{month_key}.zip"
        json_path = os.path.join(tmp_dir, json_filename)
        zip_path = os.path.join(tmp_dir, zip_filename)
        
        combined_data = month_workings
        if month_key in backup_months:
            tmp_download = os.path.join(tmp_dir, f"temp_{zip_filename}")
            try:
                if download_file(zip_filename, tmp_download):
                    with zipfile.ZipFile(tmp_download, 'r') as zipf:
                        zipf.extractall(path=tmp_dir)
                        
                    with open(json_path, 'r') as f:
                        existing_data = json.load(f)
                        
                    existing_dates = {w["date"] for w in existing_data}
                    for w in month_workings:
                        if w["date"] not in existing_dates:
                            existing_data.append(w)
                            
                    combined_data = sorted(existing_data, key=lambda x: x["date"])
            except Exception as e:
                print(f"Error merging existing backup for {month_key}:", e)
        
        with open(json_path, 'w') as f:
            json.dump(combined_data, f, indent=4)
            
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(json_path, json_filename)
            
        try:
            upload_file(zip_path, zip_filename)
            for w in month_workings:
                if "_id" in w and w["_id"]:
                    delete_document("WORKING_TRACKER", "WORKING_DETAILS", {"_id": ObjectId(w["_id"])})
        except Exception as e:
            return JSONResponse({"status": "error", "message": str(e)})
            
    shutil.rmtree(tmp_dir, ignore_errors=True)
    return JSONResponse({"status": "success", "message": "Backup completed successfully!"})

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, month: str = None):
    workings = get_all("WORKING_TRACKER", "WORKING_DETAILS", {})
    if workings and workings[-1]["date"] == datetime.datetime.now().strftime("%Y-%m-%d"):
        grouped_workings, selected_month, min_month, max_month = get_grouped_workings(month)
        return templates.TemplateResponse(request=request, name="previous_workings.html", context={"grouped_workings": grouped_workings, "selected_month": selected_month, "min_month": min_month, "max_month": max_month})
    else: return templates.TemplateResponse(request=request, name="add_working.html")

@app.get("/health", response_class=HTMLResponse)
async def health_check():
    return HTMLResponse("OK")

@app.get("/sw.js")
async def service_worker():
    return FileResponse("static/sw.js", media_type="application/javascript")

@app.get("/add-working", response_class=HTMLResponse)
async def add_working_page(request: Request):
    return templates.TemplateResponse(request=request, name="add_working.html")

@app.post("/add-working")
async def add_working(request: Request):
    data = await request.form()
    data = dict(data)
    data["date"] = datetime.datetime.strptime(data["date"], "%Y-%m-%d").strftime("%Y-%m-%d")
    data["doctor-calls"] = int(data["doctor-calls"])
    data["chemist-visits"] = int(data["chemist-visits"])
    data["working-with"] = data["working-with"].lower()
    data["working-place"] = data["working-place"].lower()
    data["note"] = data["note"].lower()
    data["remarks"] = data["remarks"].lower()
    
    workings = get_all("WORKING_TRACKER", "WORKING_DETAILS", {})
    if workings and data["date"] in [working["date"] for working in workings]:
        print(workings, data["date"])
        return templates.TemplateResponse(request=request, name="add_working.html", context={"error": "Working for today is already present"})
    
    current_month = datetime.datetime.now().strftime("%Y-%m")
    month_key = data["date"][:7]
    
    if month_key < current_month:
        backup_months = get_available_backup_months()
        if month_key in backup_months:
            zip_filename = f"backup_{month_key}.zip"
            json_filename = f"workings_{month_key}.json"
            tmp_zip = os.path.join("/tmp" if os.environ.get("VERCEL") else ".", zip_filename)
            tmp_json = os.path.join("/tmp" if os.environ.get("VERCEL") else ".", json_filename)
            
            try:
                if download_file(zip_filename, tmp_zip):
                    with zipfile.ZipFile(tmp_zip, 'r') as zipf:
                        zipf.extractall(path="/tmp" if os.environ.get("VERCEL") else ".")
                        
                    with open(tmp_json, 'r') as f:
                        backup_data = json.load(f)
                        
                    if any(w["date"] == data["date"] for w in backup_data):
                        return templates.TemplateResponse(request=request, name="add_working.html", context={"error": "Working for this date is already present in backups"})
                        
                    data["_id"] = str(ObjectId())
                    backup_data.append(data)
                    backup_data = sorted(backup_data, key=lambda x: x["date"])
                    
                    with open(tmp_json, 'w') as f:
                        json.dump(backup_data, f, indent=4)
                        
                    with zipfile.ZipFile(tmp_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
                        zipf.write(tmp_json, json_filename)
                        
                    upload_file(tmp_zip, zip_filename)
                    
                    if os.path.exists(tmp_zip): os.remove(tmp_zip)
                    if os.path.exists(tmp_json): os.remove(tmp_json)
                    
                    grouped_workings, selected_month, min_month, max_month = get_grouped_workings()
                    return templates.TemplateResponse(request=request, name="previous_workings.html", context={"grouped_workings": grouped_workings, "selected_month": selected_month, "min_month": min_month, "max_month": max_month})
            except Exception as e:
                print("Error directly updating backup:", e)
    
    add("WORKING_TRACKER", "WORKING_DETAILS", data)
    grouped_workings, selected_month, min_month, max_month = get_grouped_workings()
    return templates.TemplateResponse(request=request, name="previous_workings.html", context={"grouped_workings": grouped_workings, "selected_month": selected_month, "min_month": min_month, "max_month": max_month})

@app.get("/previous-workings", response_class=HTMLResponse)
async def previous_workings(request: Request, month: str = None):
    grouped_workings, selected_month, min_month, max_month = get_grouped_workings(month)
    return templates.TemplateResponse(request=request, name="previous_workings.html", context={"grouped_workings": grouped_workings, "selected_month": selected_month, "min_month": min_month, "max_month": max_month})

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
        
    grouped_workings, selected_month, min_month, max_month = get_grouped_workings(data.get("date", "")[:7] if data.get("date") else None)
    return templates.TemplateResponse(request=request, name="previous_workings.html", context={"grouped_workings": grouped_workings, "selected_month": selected_month, "min_month": min_month, "max_month": max_month})

@app.get("/debug-gdrive")
def debug_gdrive():
    debug_info = {
        "env_var_present": False,
        "service_created": False,
        "folders_found": [],
        "chosen_folder_id": None,
        "files_found": [],
        "errors": []
    }
    
    import os, json
    from gdrive_service import get_gdrive_service
    creds_json_str = os.environ.get("GCP_SERVICE_ACCOUNT_JSON")
    debug_info["env_var_present"] = bool(creds_json_str)
    
    try:
        service = get_gdrive_service()
        debug_info["service_created"] = True
        
        # Test folder finding
        query = "mimeType='application/vnd.google-apps.folder' and name='WorkingTrackerBackups' and trashed=false"
        folder_results = service.files().list(q=query, spaces='drive', fields='nextPageToken, files(id, name, shared)').execute()
        items = folder_results.get('files', [])
        debug_info["folders_found"] = items
        
        folder_id = None
        if items:
            for item in items:
                if item.get('shared', False):
                    folder_id = item['id']
                    break
            if not folder_id:
                folder_id = items[0]['id']
        debug_info["chosen_folder_id"] = folder_id
        
        if folder_id:
            # Test file finding
            q = f"name contains 'backup_' and name contains '.zip' and '{folder_id}' in parents and trashed=false"
            file_results = service.files().list(q=q, spaces='drive', fields='files(id, name)').execute()
            debug_info["files_found"] = file_results.get('files', [])
            
    except Exception as e:
        debug_info["errors"].append(str(e))
        
    return JSONResponse(content=debug_info)