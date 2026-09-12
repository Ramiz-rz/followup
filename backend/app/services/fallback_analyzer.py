"""
Local fallback analyzer.

This does not call any LLM. It looks for known ways people phrase
commitments and waiting states in everyday conversation, and pulls
out an action, a likely owner, and a date phrase if one is present.

It is intentionally simpler than an LLM. It will miss subtle or
indirect commitments, and it says so in the UI (labeled "Local
analysis", never "AI analysis").
"""
import re
from dataclasses import dataclass, field
from typing import Optional

SPEAKER_LINE = re.compile(r"^\s*([A-Za-z][A-Za-z .'\-]{1,30}):\s*(.+)$")

HEDGE_WORDS = ["i think", "maybe", "perhaps", "might", "could consider", "not sure", "possibly"]

WAITING_PATTERNS = [
    r"\bstill waiting\b",
    r"\bwaiting for\b",
    r"\bawaiting\b",
    r"\bhaven't received\b",
    r"\bhave not received\b",
    r"\bhasn't (?:sent|approved|confirmed)\b",
    r"\bneeds? approval\b",
    r"\bpending (?:approval|confirmation|review)\b",
    r"\bno word (?:back|yet)\b",
]

FIRST_PERSON_COMMITMENT = [
    r"\bi'll\b",
    r"\bi will\b",
    r"\bi'm going to\b",
    r"\bi am going to\b",
    r"\bi need to\b",
    r"\bi've got to\b",
    r"\bi have got to\b",
    r"\bi plan to\b",
    r"\blet me\b",
]

REQUEST_COMMITMENT = [
    r"\bcan you\b",
    r"\bcould you\b",
    r"\bplease remember to\b",
    r"\bplease send\b",
    r"\bremind me to\b",
    r"\bsomeone needs to\b",
    r"\byou need to\b",
]

GROUP_COMMITMENT = [
    r"\blet's\b",
    r"\bwe need to\b",
    r"\bwe'll\b",
    r"\bwe will\b",
    r"\bwe are going to\b",
]

DATE_PHRASE_PATTERNS = [
    r"\btoday\b", r"\btonight\b", r"\btomorrow\b", r"\byesterday\b",
    r"\bnext week\b", r"\bthis week\b",
    r"\bin \d+ days?\b", r"\bin (?:one|two|three|four|five|six|seven|eight|nine|ten) days?\b",
    r"\bby (?:end of day|eod)\b",
    r"\b(?:next |this )?(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b",
    r"\bby [a-z]+ \d{1,2}(?:st|nd|rd|th)?\b",
    r"\b(?:january|february|march|april|may|june|july|august|september|october|november|december) \d{1,2}(?:st|nd|rd|th)?\b",
    r"\b\d{4}-\d{2}-\d{2}\b",
]

COMMON_WORDS = {
    "the", "this", "that", "these", "those", "we", "they", "it", "client",
    "team", "everyone", "someone", "please", "before", "after", "next",
}


@dataclass
class RawItem:
    kind: str  # "commitment" | "waiting"
    action: str
    person: str
    due_date_text: str = "Unclear"
    priority: str = "medium"
    confidence: float = 0.5
    evidence: str = ""


def _split_speaker(line: str):
    m = SPEAKER_LINE.match(line)
    if m:
        return m.group(1).strip(), m.group(2).strip()
    return None, line.strip()


def _split_sentences(message: str):
    parts = re.split(r"(?<=[.!?])\s+", message)
    return [p.strip() for p in parts if p.strip()]


def _extract_date_phrase(sentence: str) -> str:
    low = sentence.lower()
    for pattern in DATE_PHRASE_PATTERNS:
        m = re.search(pattern, low)
        if m:
            return m.group(0)
    return "Unclear"


def _extract_named_person(sentence: str) -> Optional[str]:
    for pattern in (r"\bwith ([A-Z][a-z]+)\b", r"\bfrom ([A-Z][a-z]+)\b", r"\bfor ([A-Z][a-z]+) to\b"):
        m = re.search(pattern, sentence)
        if m and m.group(1).lower() not in COMMON_WORDS:
            return m.group(1)
    return None


def _has_hedge(low_sentence: str) -> bool:
    return any(h in low_sentence for h in HEDGE_WORDS)


def _match_any(patterns, low_sentence: str) -> bool:
    return any(re.search(p, low_sentence) for p in patterns)


def _clean_evidence(sentence: str) -> str:
    s = sentence.strip()
    s = s.strip('"').strip()
    return s


def _priority_for(low_sentence: str, has_date: bool) -> str:
    if any(w in low_sentence for w in ("urgent", "asap", "critical", "important", "must")):
        return "high"
    if has_date:
        return "medium"
    return "low"


def extract_raw_items(text: str) -> list[RawItem]:
    items: list[RawItem] = []
    lines = [l for l in text.split("\n") if l.strip()]

    for line in lines:
        speaker, message = _split_speaker(line)
        for sentence in _split_sentences(message):
            if len(sentence) < 6:
                continue
            low = sentence.lower()
            hedge = _has_hedge(low)

            date_phrase = _extract_date_phrase(sentence)
            has_date = date_phrase != "Unclear"
            named_person = _extract_named_person(sentence)

            if _match_any(WAITING_PATTERNS, low):
                person = named_person or speaker or "Unclear"
                confidence = 0.75 if not hedge else 0.5
                if has_date:
                    confidence = min(0.95, confidence + 0.1)
                items.append(RawItem(
                    kind="waiting",
                    action=sentence,
                    person=person,
                    due_date_text=date_phrase,
                    confidence=round(confidence, 2),
                    evidence=_clean_evidence(sentence),
                ))
                continue

            if _match_any(FIRST_PERSON_COMMITMENT, low):
                if hedge:
                    continue  # e.g. "I think I'll maybe..." too weak to log
                person = speaker or "Unclear"
                confidence = 0.85 if has_date else 0.7
                items.append(RawItem(
                    kind="commitment",
                    action=sentence,
                    person=person,
                    due_date_text=date_phrase,
                    priority=_priority_for(low, has_date),
                    confidence=round(confidence, 2),
                    evidence=_clean_evidence(sentence),
                ))
                continue

            if _match_any(REQUEST_COMMITMENT, low):
                if hedge:
                    continue
                person = "remind me" in low and (speaker or "Unclear") or (named_person or "Unclear")
                confidence = 0.65 if has_date else 0.55
                items.append(RawItem(
                    kind="commitment",
                    action=sentence,
                    person=person or "Unclear",
                    due_date_text=date_phrase,
                    priority=_priority_for(low, has_date),
                    confidence=round(confidence, 2),
                    evidence=_clean_evidence(sentence),
                ))
                continue

            if _match_any(GROUP_COMMITMENT, low):
                if hedge:
                    continue
                person = named_person or speaker or "Unclear"
                confidence = 0.6 if has_date else 0.5
                items.append(RawItem(
                    kind="commitment",
                    action=sentence,
                    person=person,
                    due_date_text=date_phrase,
                    priority=_priority_for(low, has_date),
                    confidence=round(confidence, 2),
                    evidence=_clean_evidence(sentence),
                ))
                continue

    return items


def analyze_fallback(text: str) -> dict:
    raw_items = extract_raw_items(text)
    commitments = [
        {
            "action": item.action,
            "person": item.person,
            "due_date_text": item.due_date_text,
            "due_date": None,
            "priority": item.priority,
            "confidence": item.confidence,
            "evidence": item.evidence,
        }
        for item in raw_items if item.kind == "commitment"
    ]
    waiting_items = [
        {
            "item": item.action,
            "person": item.person,
            "waiting_since_text": item.due_date_text,
            "confidence": item.confidence,
            "evidence": item.evidence,
        }
        for item in raw_items if item.kind == "waiting"
    ]

    if not commitments and not waiting_items:
        summary = "Local analysis did not find any clear commitments or waiting items in this text."
    else:
        summary = (
            f"Local analysis found {len(commitments)} commitment(s) and "
            f"{len(waiting_items)} waiting item(s) based on common phrasing patterns."
        )

    return {
        "summary": summary,
        "commitments": commitments,
        "waiting_items": waiting_items,
    }
