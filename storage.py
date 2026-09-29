from datetime import datetime, timezone
from itertools import count
from threading import Lock
from typing import Optional

from models import (
    Application,
    ApplicationCreate,
    ApplicationStatus,
    Complaint,
    ComplaintCreate,
    ComplaintStatus,
)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class ISPStore:
    """Thread-safe in-memory store for applications and complaints."""

    def __init__(self) -> None:
        self._applications: dict[int, Application] = {}
        self._complaints: dict[int, Complaint] = {}
        self._app_ids = count(1)
        self._cmp_ids = count(1)
        self._lock = Lock()

    # ----- Applications -----

    def add_application(self, data: ApplicationCreate) -> Application:
        with self._lock:
            app = Application(id=next(self._app_ids), created_at=_now(), **data.model_dump())
            self._applications[app.id] = app
            return app

    def get_application(self, app_id: int) -> Optional[Application]:
        return self._applications.get(app_id)

    def list_applications(
        self, status: Optional[ApplicationStatus] = None
    ) -> list[Application]:
        apps = list(self._applications.values())
        if status is not None:
            apps = [a for a in apps if a.status == status]
        return apps

    def set_application_status(
        self, app_id: int, status: ApplicationStatus
    ) -> Optional[Application]:
        app = self._applications.get(app_id)
        if app is None:
            return None
        updated = app.model_copy(update={"status": status})
        self._applications[app_id] = updated
        return updated

    # ----- Complaints -----

    def add_complaint(self, data: ComplaintCreate) -> Complaint:
        with self._lock:
            cmp = Complaint(id=next(self._cmp_ids), created_at=_now(), **data.model_dump())
            self._complaints[cmp.id] = cmp
            return cmp

    def get_complaint(self, cmp_id: int) -> Optional[Complaint]:
        return self._complaints.get(cmp_id)

    def list_complaints(
        self,
        status: Optional[ComplaintStatus] = None,
        application_id: Optional[int] = None,
    ) -> list[Complaint]:
        items = list(self._complaints.values())
        if status is not None:
            items = [c for c in items if c.status == status]
        if application_id is not None:
            items = [c for c in items if c.application_id == application_id]
        return items

    def resolve_complaint(
        self,
        cmp_id: int,
        note: str,
        status: ComplaintStatus = ComplaintStatus.resolved,
    ) -> Optional[Complaint]:
        cmp = self._complaints.get(cmp_id)
        if cmp is None:
            return None
        updated = cmp.model_copy(
            update={
                "status": status,
                "resolution_note": note,
                "resolved_at": _now(),
            }
        )
        self._complaints[cmp_id] = updated
        return updated

    def set_complaint_status(
        self, cmp_id: int, status: ComplaintStatus
    ) -> Optional[Complaint]:
        cmp = self._complaints.get(cmp_id)
        if cmp is None:
            return None
        updated = cmp.model_copy(update={"status": status})
        self._complaints[cmp_id] = updated
        return updated


store = ISPStore()
