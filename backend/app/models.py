import uuid
from datetime import datetime

from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Text
from app.database import Base


def gen_id():
    return uuid.uuid4().hex[:12]


class Project(Base):
    __tablename__ = "projects"

    id = Column(String, primary_key=True, default=gen_id)
    name = Column(String, nullable=False)
    summary = Column(Text, default="")
    source_text = Column(Text, default="")
    source_name = Column(String, default="")
    analysis_mode = Column(String, default="local")  # "local" or "ai"
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Commitment(Base):
    __tablename__ = "commitments"

    id = Column(String, primary_key=True, default=gen_id)
    project_id = Column(String, ForeignKey("projects.id"))
    action = Column(Text, nullable=False)
    person = Column(String, default="Unclear")
    due_date = Column(String, nullable=True)  # ISO date string, nullable
    due_date_text = Column(String, default="Unclear")
    priority = Column(String, default="medium")  # high | medium | low
    status = Column(String, default="open")  # open | due_soon | overdue | completed | waiting
    confidence = Column(Float, default=0.5)
    evidence = Column(Text, default="")
    source = Column(String, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class WaitingItem(Base):
    __tablename__ = "waiting_items"

    id = Column(String, primary_key=True, default=gen_id)
    project_id = Column(String, ForeignKey("projects.id"))
    item = Column(Text, nullable=False)
    person = Column(String, default="Unclear")
    waiting_since = Column(String, nullable=True)  # ISO date string
    waiting_since_text = Column(String, default="Unclear")
    status = Column(String, default="waiting")  # waiting | resolved
    confidence = Column(Float, default=0.5)
    evidence = Column(Text, default="")
    source = Column(String, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
