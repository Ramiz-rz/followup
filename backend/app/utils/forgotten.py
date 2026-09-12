from app.services.status_engine import effective_commitment_status, days_waiting
from app.services.date_parser import days_between

WAITING_FORGOTTEN_DAYS = 5
MIN_CONFIDENCE_FOR_NO_DATE = 0.6


def get_forgotten_items(commitments, waiting_items) -> list[dict]:
    forgotten = []

    for c in commitments:
        if c.status in ("completed",):
            continue
        effective = effective_commitment_status(c.status, c.due_date)

        if effective == "overdue":
            delta = days_between(c.due_date)
            days_late = abs(delta) if delta is not None else None
            reason = f"Overdue by {days_late} day{'s' if days_late != 1 else ''}." if days_late else "Overdue."
            forgotten.append({
                "id": c.id, "kind": "commitment", "action": c.action, "person": c.person,
                "evidence": c.evidence, "reason": reason, "status": effective,
            })
        elif not c.due_date and c.status == "open" and c.confidence >= MIN_CONFIDENCE_FOR_NO_DATE:
            forgotten.append({
                "id": c.id, "kind": "commitment", "action": c.action, "person": c.person,
                "evidence": c.evidence,
                "reason": "No due date was found, but the message contains an explicit commitment.",
                "status": effective,
            })

    for w in waiting_items:
        if w.status != "waiting":
            continue
        wd = days_waiting(w.waiting_since, w.created_at)
        if wd >= WAITING_FORGOTTEN_DAYS:
            forgotten.append({
                "id": w.id, "kind": "waiting", "action": w.item, "person": w.person,
                "evidence": w.evidence,
                "reason": f"Waiting for {wd} days with no resolution.",
                "status": "waiting",
            })

    return forgotten
