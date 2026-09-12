from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/api/waiting", tags=["waiting"])


def _get_waiting_or_404(waiting_id: str, db: Session) -> models.WaitingItem:
    item = db.query(models.WaitingItem).filter(models.WaitingItem.id == waiting_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Waiting item not found.")
    return item


@router.patch("/{waiting_id}", response_model=schemas.WaitingItemOut)
def update_waiting(waiting_id: str, payload: schemas.WaitingItemUpdate, db: Session = Depends(get_db)):
    item = _get_waiting_or_404(waiting_id, db)
    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{waiting_id}")
def delete_waiting(waiting_id: str, db: Session = Depends(get_db)):
    item = _get_waiting_or_404(waiting_id, db)
    db.delete(item)
    db.commit()
    return {"deleted": True}
