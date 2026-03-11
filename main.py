import os
import shutil
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from tools.db import create_request, get_all_requests, get_dashboard_data, init_db, update_request
from tools.export import generate_export
from tools.excel_reader import get_staff

load_dotenv(override=True)

app = FastAPI(title="Engineering Request System")

app.mount("/static", StaticFiles(directory="static"), name="static")

UPLOADS_DIR = Path("uploads")
UPLOADS_DIR.mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


@app.on_event("startup")
def startup():
    init_db()
    UPLOADS_DIR.mkdir(exist_ok=True)


@app.get("/")
def root():
    return FileResponse("static/index.html")


@app.get("/submit")
def submit_page():
    return FileResponse("static/submit.html")


@app.get("/review")
def review_page():
    return FileResponse("static/review.html")


@app.get("/dashboard")
def dashboard_page():
    return FileResponse("static/dashboard.html")


@app.get("/api/staff")
def api_staff():
    return get_staff()


@app.post("/api/requests")
async def api_create_request(
    secteur: str = Form(...),
    requester: str = Form(...),
    description: str = Form(...),
    type: str = Form(None),
    file: UploadFile = File(None),
):
    attachment_path = None
    if file and file.filename:
        UPLOADS_DIR.mkdir(exist_ok=True)
        safe_name = f"{os.urandom(4).hex()}_{file.filename}"
        dest = UPLOADS_DIR / safe_name
        with open(dest, "wb") as f:
            shutil.copyfileobj(file.file, f)
        attachment_path = f"uploads/{safe_name}"

    request_id = create_request(secteur, requester, description, type=type, attachment_path=attachment_path)
    return {"id": request_id, "message": "Request submitted successfully"}


@app.get("/api/requests")
def api_list_requests(requester: str = None, status: str = None, assignee: str = None, type: str = None):
    return get_all_requests(requester=requester, status=status, assignee=assignee, type=type)


class RequestUpdate(BaseModel):
    assignee: str | None = None
    status: str | None = None
    description: str | None = None
    type: str | None = None


@app.patch("/api/requests/{request_id}")
def api_update_request(request_id: int, data: RequestUpdate):
    update_request(request_id, assignee=data.assignee, status=data.status, description=data.description, type=data.type)
    return {"message": "Updated successfully"}


@app.get("/api/export")
def api_export():
    path = generate_export()
    return FileResponse(
        path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename="demandes_ingenierie.xlsx",
    )


@app.get("/api/dashboard")
def api_dashboard():
    return get_dashboard_data()
