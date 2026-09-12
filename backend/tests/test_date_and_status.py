from datetime import date, timedelta
from app.services.date_parser import parse_date_phrase, days_between
from app.services.status_engine import effective_commitment_status


def test_parse_tomorrow():
    ref = date(2026, 9, 12)
    assert parse_date_phrase("tomorrow", ref) == "2026-09-13"


def test_parse_today():
    ref = date(2026, 9, 12)
    assert parse_date_phrase("today", ref) == "2026-09-12"


def test_parse_unclear_phrase():
    assert parse_date_phrase("whenever we get a chance") is None


def test_parse_weekday():
    ref = date(2026, 9, 12)  # a Saturday
    result = parse_date_phrase("friday", ref)
    assert result == "2026-09-18"


def test_overdue_status():
    ref = date(2026, 9, 12)
    yesterday = (ref - timedelta(days=1)).isoformat()
    assert effective_commitment_status("open", yesterday, reference=ref) == "overdue"


def test_due_soon_status():
    ref = date(2026, 9, 12)
    tomorrow = (ref + timedelta(days=1)).isoformat()
    assert effective_commitment_status("open", tomorrow, reference=ref) == "due_soon"


def test_open_status_no_date():
    assert effective_commitment_status("open", None) == "open"


def test_completed_stays_completed_even_if_overdue():
    ref = date(2026, 9, 12)
    yesterday = (ref - timedelta(days=1)).isoformat()
    assert effective_commitment_status("completed", yesterday, reference=ref) == "completed"
