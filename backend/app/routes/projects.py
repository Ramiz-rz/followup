from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app import models, schemas
from app.services.status_engine import effective_commitment_status
from app.services.risk_engine import compute_risk
from app.utils.forgotten import get_forgotten_items

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.get("", response_model=List[schemas.ProjectOut])
def list_projects(db: Session = Depends(get_db)):
    return db.query(models.Project).order_by(models.Project.created_at.desc()).all()


@router.post("", response_model=schemas.ProjectOut)
def create_project(payload: schemas.ProjectCreate, db: Session = Depends(get_db)):
    project = models.Project(name=payload.name.strip() or "Untitled project")
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def _get_project_or_404(project_id: str, db: Session) -> models.Project:
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")
    return project


@router.get("/{project_id}", response_model=schemas.ProjectOut)
def get_project(project_id: str, db: Session = Depends(get_db)):
    return _get_project_or_404(project_id, db)


@router.delete("/{project_id}")
def delete_project(project_id: str, db: Session = Depends(get_db)):
    project = _get_project_or_404(project_id, db)
    db.query(models.Commitment).filter(models.Commitment.project_id == project_id).delete()
    db.query(models.WaitingItem).filter(models.WaitingItem.project_id == project_id).delete()
    db.delete(project)
    db.commit()
    return {"deleted": True}


@router.get("/{project_id}/commitments", response_model=List[schemas.CommitmentOut])
def get_commitments(project_id: str, db: Session = Depends(get_db)):
    _get_project_or_404(project_id, db)
    items = db.query(models.Commitment).filter(models.Commitment.project_id == project_id).all()
    for item in items:
        item.status = effective_commitment_status(item.status, item.due_date) if item.status not in (
            "completed", "waiting") else item.status
    return items


@router.get("/{project_id}/waiting", response_model=List[schemas.WaitingItemOut])
def get_waiting(project_id: str, db: Session = Depends(get_db)):
    _get_project_or_404(project_id, db)
    return db.query(models.WaitingItem).filter(models.WaitingItem.project_id == project_id).all()


@router.get("/{project_id}/stats", response_model=schemas.StatsOut)
def get_stats(project_id: str, db: Session = Depends(get_db)):
    _get_project_or_404(project_id, db)
    commitments = db.query(models.Commitment).filter(models.Commitment.project_id == project_id).all()
    waiting_items = db.query(models.WaitingItem).filter(models.WaitingItem.project_id == project_id).all()

    counts = {"open": 0, "due_soon": 0, "overdue": 0, "completed": 0}
    for c in commitments:
        effective = effective_commitment_status(c.status, c.due_date)
        if effective in counts:
            counts[effective] += 1

    waiting_open = sum(1 for w in waiting_items if w.status == "waiting")

    risk = compute_risk(commitments, waiting_items)

    return schemas.StatsOut(
        open=counts["open"],
        due_soon=counts["due_soon"],
        overdue=counts["overdue"],
        waiting=waiting_open,
        completed=counts["completed"],
        risk_score=risk["score"],
        risk_level=risk["level"],
        risk_reasons=risk["reasons"],
    )


@router.get("/{project_id}/forgotten", response_model=List[schemas.ForgottenItem])
def get_forgotten(project_id: str, db: Session = Depends(get_db)):
    _get_project_or_404(project_id, db)
    commitments = db.query(models.Commitment).filter(models.Commitment.project_id == project_id).all()
    waiting_items = db.query(models.WaitingItem).filter(models.WaitingItem.project_id == project_id).all()
    return get_forgotten_items(commitments, waiting_items)
