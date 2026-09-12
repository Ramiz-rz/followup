"""
Statuses are never decided by the AI. A commitment is only ever
"completed" or "waiting" because a person set it that way (or the
extractor flagged it as waiting). Everything else, open, due soon,
or overdue, is computed here from the due date and today's date.
"""
from datetime import date, datetime
from app.services.date_parser import days_between

DUE_SOON_WINDOW_DAYS = 2


def effective_commitment_status(raw_status: str, due_date: str | None, reference: date = None) -> str:
    if raw_status in ("completed", "waiting"):
        return raw_status

    if not due_date:
        return "open"

    delta = days_between(due_date, reference)
    if delta is None:
        return "open"
    if delta < 0:
        return "overdue"
    if delta <= DUE_SOON_WINDOW_DAYS:
        return "due_soon"
    return "open"


def days_waiting(waiting_since: str | None, created_at: datetime, reference: date = None) -> int:
    ref = reference or date.today()
    if waiting_since:
        delta = days_between(waiting_since, ref)
        if delta is not None:
            return max(0, -delta)
    if created_at:
        return max(0, (ref - created_at.date()).days)
    return 0
