from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


# ---------- Enums ----------

class PlanType(str, Enum):
    basic = "basic"          # 50 Mbps
    standard = "standard"    # 100 Mbps
    premium = "premium"      # 300 Mbps
    gigabit = "gigabit"      # 1 Gbps


class ApplicationStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    installed = "installed"
    rejected = "rejected"


class ComplaintStatus(str, Enum):
    open = "open"
    in_progress = "in_progress"
    resolved = "resolved"
    closed = "closed"


class ComplaintCategory(str, Enum):
    no_internet = "no_internet"
    slow_speed = "slow_speed"
    billing = "billing"
    router_issue = "router_issue"
    other = "other"


# ---------- Application (new connection request) ----------

class ApplicationCreate(BaseModel):
    customer_name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., min_length=3, max_length=120)
    phone: str = Field(..., min_length=5, max_length=20)
    address: str = Field(..., min_length=3, max_length=200)
    region: str = Field(..., min_length=1, max_length=100)
    plan: PlanType = PlanType.basic


class Application(ApplicationCreate):
    id: int
    status: ApplicationStatus = ApplicationStatus.pending
    created_at: datetime


# ---------- Complaint ----------

class ComplaintCreate(BaseModel):
    application_id: int
    subject: str = Field(..., min_length=3, max_length=150)
    description: str = Field(..., min_length=3, max_length=1000)
    category: ComplaintCategory = ComplaintCategory.other


class Resolution(BaseModel):
    """Admin resolution attached to a complaint."""
    note: str = Field(..., min_length=3, max_length=1000)


class Complaint(ComplaintCreate):
    id: int
    status: ComplaintStatus = ComplaintStatus.open
    resolution_note: Optional[str] = None
    resolved_at: Optional[datetime] = None
    created_at: datetime
