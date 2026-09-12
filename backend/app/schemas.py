from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, field_validator

ALLOWED_PRIORITIES = {"high", "medium", "low"}
ALLOWED_COMMITMENT_STATUSES = {"open", "due_soon", "overdue", "completed", "waiting"}
ALLOWED_WAITING_STATUSES = {"waiting", "resolved"}


# ---------- Raw extraction schemas (what the AI or fallback produces) ----------

class RawCommitment(BaseModel):
    action: str
    person: str = "Unclear"
    due_date_text: str = "Unclear"
    due_date: Optional[str] = None
    priority: str = "medium"
    confidence: float = 0.5
    evidence: str = ""

    @field_validator("priority")
    @classmethod
    def check_priority(cls, v):
        if v not in ALLOWED_PRIORITIES:
            return "medium"
        return v

    @field_validator("confidence")
    @classmethod
    def check_confidence(cls, v):
        try:
            v = float(v)
        except (TypeError, ValueError):
            return 0.5
        return max(0.0, min(1.0, v))

    @field_validator("action")
    @classmethod
    def check_action(cls, v):
        if not v or not v.strip():
            raise ValueError("action cannot be empty")
        return v.strip()


class RawWaitingItem(BaseModel):
    item: str
    person: str = "Unclear"
    waiting_since_text: str = "Unclear"
    confidence: float = 0.5
    evidence: str = ""

    @field_validator("confidence")
    @classmethod
    def check_confidence(cls, v):
        try:
            v = float(v)
        except (TypeError, ValueError):
            return 0.5
        return max(0.0, min(1.0, v))

    @field_validator("item")
    @classmethod
    def check_item(cls, v):
        if not v or not v.strip():
            raise ValueError("item cannot be empty")
        return v.strip()


class AnalysisResult(BaseModel):
    summary: str = ""
    commitments: List[RawCommitment] = Field(default_factory=list)
    waiting_items: List[RawWaitingItem] = Field(default_factory=list)


# ---------- API request/response schemas ----------

class ProjectCreate(BaseModel):
    name: str


class ProjectOut(BaseModel):
    id: str
    name: str
    summary: str
    source_name: str
    analysis_mode: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CommitmentOut(BaseModel):
    id: str
    project_id: str
    action: str
    person: str
    due_date: Optional[str]
    due_date_text: str
    priority: str
    status: str
    confidence: float
    evidence: str
    source: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WaitingItemOut(BaseModel):
    id: str
    project_id: str
    item: str
    person: str
    waiting_since: Optional[str]
    waiting_since_text: str
    status: str
    confidence: float
    evidence: str
    source: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CommitmentUpdate(BaseModel):
    action: Optional[str] = None
    person: Optional[str] = None
    due_date: Optional[str] = None
    due_date_text: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None

    @field_validator("priority")
    @classmethod
    def check_priority(cls, v):
        if v is not None and v not in ALLOWED_PRIORITIES:
            raise ValueError(f"priority must be one of {ALLOWED_PRIORITIES}")
        return v

    @field_validator("status")
    @classmethod
    def check_status(cls, v):
        if v is not None and v not in ALLOWED_COMMITMENT_STATUSES:
            raise ValueError(f"status must be one of {ALLOWED_COMMITMENT_STATUSES}")
        return v


class WaitingItemUpdate(BaseModel):
    item: Optional[str] = None
    person: Optional[str] = None
    waiting_since: Optional[str] = None
    waiting_since_text: Optional[str] = None
    status: Optional[str] = None

    @field_validator("status")
    @classmethod
    def check_status(cls, v):
        if v is not None and v not in ALLOWED_WAITING_STATUSES:
            raise ValueError(f"status must be one of {ALLOWED_WAITING_STATUSES}")
        return v


class AnalyzeTextRequest(BaseModel):
    text: str
    project_name: Optional[str] = None


class StatsOut(BaseModel):
    open: int
    due_soon: int
    overdue: int
    waiting: int
    completed: int
    risk_score: int
    risk_level: str
    risk_reasons: List[str]


class ForgottenItem(BaseModel):
    id: str
    kind: str  # "commitment" or "waiting"
    action: str
    person: str
    evidence: str
    reason: str
    status: str
