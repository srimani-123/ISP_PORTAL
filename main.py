from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from models import (
    Application,
    ApplicationCreate,
    ApplicationStatus,
    Complaint,
    ComplaintCategory,
    ComplaintCreate,
    ComplaintStatus,
    PlanType,
    Resolution,
)
from storage import store

app = FastAPI(title="ISP Portal", version="1.0.0")
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")


# ==================================================================
# JSON API — Applications
# ==================================================================

@app.post("/api/applications", response_model=Application, status_code=201)
def api_create_application(payload: ApplicationCreate) -> Application:
    return store.add_application(payload)


@app.get("/api/applications", response_model=list[Application])
def api_list_applications(status: Optional[ApplicationStatus] = None) -> list[Application]:
    return store.list_applications(status)


@app.get("/api/applications/{app_id}", response_model=Application)
def api_get_application(app_id: int) -> Application:
    app_obj = store.get_application(app_id)
    if app_obj is None:
        raise HTTPException(404, "Application not found")
    return app_obj


@app.patch("/api/applications/{app_id}/status", response_model=Application)
def api_set_application_status(app_id: int, new_status: ApplicationStatus):
    updated = store.set_application_status(app_id, new_status)
    if updated is None:
        raise HTTPException(404, "Application not found")
    return updated


# ==================================================================
# JSON API — Complaints
# ==================================================================

@app.post("/api/complaints", response_model=Complaint, status_code=201)
def api_create_complaint(payload: ComplaintCreate) -> Complaint:
    if store.get_application(payload.application_id) is None:
        raise HTTPException(400, "Application not found for this complaint")
    return store.add_complaint(payload)


@app.get("/api/complaints", response_model=list[Complaint])
def api_list_complaints(
    status: Optional[ComplaintStatus] = None,
    application_id: Optional[int] = None,
) -> list[Complaint]:
    return store.list_complaints(status, application_id)


@app.post("/api/complaints/{cmp_id}/resolve", response_model=Complaint)
def api_resolve_complaint(cmp_id: int, payload: Resolution) -> Complaint:
    updated = store.resolve_complaint(cmp_id, payload.note)
    if updated is None:
        raise HTTPException(404, "Complaint not found")
    return updated


# ==================================================================
# Customer Web UI
# ==================================================================

@app.get("/", response_class=HTMLResponse)
def customer_home(request: Request, application_id: Optional[int] = None):
    apps = store.list_applications()
    my_app = store.get_application(application_id) if application_id else None
    my_complaints = (
        store.list_complaints(application_id=application_id) if application_id else []
    )
    return templates.TemplateResponse(
        "customer.html",
        {
            "request": request,
            "plans": [p.value for p in PlanType],
            "categories": [c.value for c in ComplaintCategory],
            "my_application": my_app,
            "my_complaints": my_complaints,
        },
    )


@app.post("/apply")
def customer_apply(
    customer_name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    address: str = Form(...),
    region: str = Form(...),
    plan: PlanType = Form(PlanType.basic),
):
    app_obj = store.add_application(
        ApplicationCreate(
            customer_name=customer_name,
            email=email,
            phone=phone,
            address=address,
            region=region,
            plan=plan,
        )
    )
    return RedirectResponse(url=f"/?application_id={app_obj.id}", status_code=303)


@app.post("/complaints")
def customer_complaint(
    application_id: int = Form(...),
    subject: str = Form(...),
    description: str = Form(...),
    category: ComplaintCategory = Form(ComplaintCategory.other),
):
    if store.get_application(application_id) is None:
        raise HTTPException(400, "Invalid application ID")
    store.add_complaint(
        ComplaintCreate(
            application_id=application_id,
            subject=subject,
            description=description,
            category=category,
        )
    )
    return RedirectResponse(url=f"/?application_id={application_id}", status_code=303)


# ==================================================================
# Admin Web UI
# ==================================================================

@app.get("/admin", response_class=HTMLResponse)
def admin_home(
    request: Request,
    app_status: Optional[ApplicationStatus] = None,
    cmp_status: Optional[ComplaintStatus] = None,
):
    apps = store.list_applications(app_status)
    complaints = store.list_complaints(cmp_status)
    return templates.TemplateResponse(
        "admin.html",
        {
            "request": request,
            "applications": apps,
            "complaints": complaints,
            "app_statuses": [s.value for s in ApplicationStatus],
            "cmp_statuses": [s.value for s in ComplaintStatus],
            "app_status": app_status.value if app_status else "",
            "cmp_status": cmp_status.value if cmp_status else "",
            "app_lookup": {a.id: a for a in store.list_applications()},
        },
    )


@app.post("/admin/applications/{app_id}/status")
def admin_set_app_status(app_id: int, new_status: ApplicationStatus = Form(...)):
    if store.set_application_status(app_id, new_status) is None:
        raise HTTPException(404, "Application not found")
    return RedirectResponse(url="/admin", status_code=303)


@app.post("/admin/complaints/{cmp_id}/resolve")
def admin_resolve_complaint(
    cmp_id: int,
    note: str = Form(...),
    new_status: ComplaintStatus = Form(ComplaintStatus.resolved),
):
    if store.resolve_complaint(cmp_id, note, new_status) is None:
        raise HTTPException(404, "Complaint not found")
    return RedirectResponse(url="/admin", status_code=303)
