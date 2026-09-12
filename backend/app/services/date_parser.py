"""
Turns loose date phrases like "tomorrow", "next Friday", "in two days"
into an actual ISO date, relative to a reference date (normally "today"
on the backend). If a phrase cannot be confidently resolved, this
returns None and the caller should store "Unclear" instead of guessing.
"""
import re
from datetime import date, timedelta

WEEKDAYS = {
    "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
    "friday": 4, "saturday": 5, "sunday": 6,
}

MONTHS = {
    "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
    "july": 7, "august": 8, "september": 9, "october": 10, "november": 11,
    "december": 12,
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "jun": 6, "jul": 7, "aug": 8,
    "sep": 9, "sept": 9, "oct": 10, "nov": 11, "dec": 12,
}

WORD_NUMBERS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
}


def _next_weekday(ref: date, weekday: int, force_next_week: bool = False) -> date:
    days_ahead = weekday - ref.weekday()
    if days_ahead < 0 or (days_ahead == 0 and force_next_week) or (force_next_week and days_ahead == 0):
        days_ahead += 7
    if days_ahead <= 0:
        days_ahead += 7
    return ref + timedelta(days=days_ahead)


def parse_date_phrase(phrase: str, reference: date = None) -> str | None:
    """Returns an ISO date string (YYYY-MM-DD) or None if unclear."""
    if not phrase:
        return None
    ref = reference or date.today()
    text = phrase.strip().lower()
    text = re.sub(r"[.,!?]$", "", text)

    if text in ("today", "tonight", "this afternoon", "this morning", "end of day", "eod"):
        return ref.isoformat()

    if text == "tomorrow":
        return (ref + timedelta(days=1)).isoformat()

    if text in ("yesterday",):
        return (ref - timedelta(days=1)).isoformat()

    # "next week" -> 7 days out
    if "next week" in text:
        return (ref + timedelta(days=7)).isoformat()

    # "in N days" / "in two days"
    m = re.search(r"in (\d+|" + "|".join(WORD_NUMBERS.keys()) + r")\s+days?", text)
    if m:
        raw = m.group(1)
        n = int(raw) if raw.isdigit() else WORD_NUMBERS.get(raw)
        if n:
            return (ref + timedelta(days=n)).isoformat()

    # "by <month> <day>" or "<month> <day>"
    m = re.search(
        r"(" + "|".join(MONTHS.keys()) + r")\s+(\d{1,2})(st|nd|rd|th)?",
        text,
    )
    if m:
        month = MONTHS[m.group(1)]
        day = int(m.group(2))
        year = ref.year
        try:
            candidate = date(year, month, day)
        except ValueError:
            return None
        if candidate < ref:
            try:
                candidate = date(year + 1, month, day)
            except ValueError:
                return None
        return candidate.isoformat()

    # weekday references: "friday", "next friday", "this friday", "by friday"
    force_next = "next" in text
    for name, idx in WEEKDAYS.items():
        if name in text:
            return _next_weekday(ref, idx, force_next_week=force_next).isoformat()

    # explicit ISO-ish date already, e.g. 2026-09-20 or 09/20/2026
    m = re.search(r"(\d{4})-(\d{2})-(\d{2})", text)
    if m:
        try:
            return date(int(m.group(1)), int(m.group(2)), int(m.group(3))).isoformat()
        except ValueError:
            return None

    m = re.search(r"(\d{1,2})/(\d{1,2})/(\d{4})", text)
    if m:
        try:
            return date(int(m.group(3)), int(m.group(1)), int(m.group(2))).isoformat()
        except ValueError:
            return None

    return None


def days_between(iso_date: str, reference: date = None) -> int | None:
    """Positive if iso_date is in the future, negative if in the past."""
    if not iso_date:
        return None
    ref = reference or date.today()
    try:
        y, m, d = [int(x) for x in iso_date.split("-")]
        target = date(y, m, d)
    except (ValueError, TypeError):
        return None
    return (target - ref).days
