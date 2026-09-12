from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.services.status_engine import effective_commitment_status

router = APIRouter(prefix="/api/commitments", tags=["commitments"])


def _get_commitment_or_404(commitment_id: str, db: Session) -> models.Commitment:
    item = db.query(models.Commitment).filter(models.Commitment.id == commitment_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Follow-up not found.")
    return item


@router.patch("/{commitment_id}", response_model=schemas.CommitmentOut)
def update_commitment(commitment_id: str, payload: schemas.CommitmentUpdate, db: Session = Depends(get_db)):
    item = _get_commitment_or_404(commitment_id, db)
    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    item.status = effective_commitment_status(item.status, item.due_date) if item.status not in (
        "completed", "waiting") else item.status
    return item


@router.delete("/{commitment_id}")
def delete_commitment(commitment_id: str, db: Session = Depends(get_db)):
    item = _get_commitment_or_404(commitment_id, db)
    db.delete(item)
    db.commit()
    return {"deleted": True}
