import logging
from pydantic import ValidationError

from app.schemas import AnalysisResult
from app.services.ai_analyzer import analyze_with_ai, is_ai_configured, AIAnalysisError
from app.services.fallback_analyzer import analyze_fallback
from app.services.date_parser import parse_date_phrase

logger = logging.getLogger("followup.pipeline")


class PipelineResult:
    def __init__(self, result: AnalysisResult, mode: str, note: str = ""):
        self.result = result
        self.mode = mode  # "ai" or "local"
        self.note = note


def run_analysis(text: str) -> PipelineResult:
    if not text or not text.strip():
        raise ValueError("There is no text to analyze.")

    if is_ai_configured():
        try:
            raw = analyze_with_ai(text)
            validated = AnalysisResult.model_validate(raw)
            return PipelineResult(validated, "ai")
        except (AIAnalysisError, ValidationError) as e:
            logger.warning("AI analysis unavailable, using local fallback: %s", e)
            raw = analyze_fallback(text)
            validated = AnalysisResult.model_validate(raw)
            return PipelineResult(
                validated, "local",
                note="AI analysis is unavailable right now. We used local analysis instead.",
            )

    raw = analyze_fallback(text)
    validated = AnalysisResult.model_validate(raw)
    return PipelineResult(validated, "local")


def normalize_due_date(due_date_text: str, existing_due_date: str | None = None) -> str | None:
    parsed = parse_date_phrase(due_date_text)
    return parsed if parsed else existing_due_date
