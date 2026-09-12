"""
Follow-Up Risk is a plain scoring formula over the actual records in
the database. Nothing here comes from a model. See README.md for the
documented formula, this is the implementation of it.
"""
from app.services.status_engine import effective_commitment_status, days_waiting

WAITING_STALE_DAYS = 3


def compute_risk(commitments, waiting_items) -> dict:
    """
    commitments: list of Commitment ORM objects
    waiting_items: list of WaitingItem ORM objects
    """
    score = 0
    reasons = []

    overdue = [c for c in commitments if effective_commitment_status(c.status, c.due_date) == "overdue"]
    if overdue:
        points = min(60, len(overdue) * 15)
        score += points
        reasons.append(f"{len(overdue)} overdue commitment{'s' if len(overdue) != 1 else ''}")

    unresolved = [c for c in commitments if c.status not in ("completed",)]

    high_priority_unresolved = [
        c for c in unresolved
        if c.priority == "high" and effective_commitment_status(c.status, c.due_date) != "overdue"
    ]
    if high_priority_unresolved:
        points = min(30, len(high_priority_unresolved) * 10)
        score += points
        reasons.append(
            f"{len(high_priority_unresolved)} high-priority item"
            f"{'s' if len(high_priority_unresolved) != 1 else ''} without completion"
        )

    unassigned_unresolved = [
        c for c in unresolved if not c.person or c.person.strip().lower() == "unclear"
    ]
    if unassigned_unresolved:
        points = min(20, len(unassigned_unresolved) * 5)
        score += points
        reasons.append(
            f"{len(unassigned_unresolved)} unresolved commitment"
            f"{'s have' if len(unassigned_unresolved) != 1 else ' has'} no clear owner"
        )

    missing_date_unresolved = [c for c in unresolved if not c.due_date]
    if missing_date_unresolved:
        points = min(20, len(missing_date_unresolved) * 5)
        score += points
        reasons.append(
            f"{len(missing_date_unresolved)} unresolved commitment"
            f"{'s have' if len(missing_date_unresolved) != 1 else ' has'} no due date"
        )

    stale_waiting = []
    for w in waiting_items:
        if w.status != "waiting":
            continue
        wd = days_waiting(w.waiting_since, w.created_at)
        if wd >= WAITING_STALE_DAYS:
            stale_waiting.append((w, wd))
    if stale_waiting:
        points = min(30, len(stale_waiting) * 8)
        score += points
        longest = max(wd for _, wd in stale_waiting)
        if len(stale_waiting) == 1:
            reasons.append(f"1 waiting item has been unresolved for {longest} day{'s' if longest != 1 else ''}")
        else:
            reasons.append(
                f"{len(stale_waiting)} waiting items have been unresolved, "
                f"the longest for {longest} day{'s' if longest != 1 else ''}"
            )

    score = max(0, min(100, score))

    if score >= 75:
        level = "Critical"
    elif score >= 50:
        level = "High"
    elif score >= 25:
        level = "Medium"
    else:
        level = "Low"

    if not reasons:
        reasons.append("No overdue items, unclear owners, or stale waiting items right now.")

    return {"score": score, "level": level, "reasons": reasons}
