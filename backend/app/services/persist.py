from sqlalchemy.orm import Session

from app import models
from app.schemas import AnalysisResult
from app.services.pipeline import normalize_due_date


def persist_analysis(db: Session, project: models.Project, result: AnalysisResult, source_name: str):
    for c in result.commitments:
        due_date = normalize_due_date(c.due_date_text, c.due_date)
        db.add(models.Commitment(
            project_id=project.id,
            action=c.action,
            person=c.person or "Unclear",
            due_date=due_date,
            due_date_text=c.due_date_text or "Unclear",
            priority=c.priority,
            status="open",
            confidence=c.confidence,
            evidence=c.evidence,
            source=source_name,
        ))

    for w in result.waiting_items:
        waiting_since = normalize_due_date(w.waiting_since_text, None)
        db.add(models.WaitingItem(
            project_id=project.id,
            item=w.item,
            person=w.person or "Unclear",
            waiting_since=waiting_since,
            waiting_since_text=w.waiting_since_text or "Unclear",
            status="waiting",
            confidence=w.confidence,
            evidence=w.evidence,
            source=source_name,
        ))

    db.commit()
