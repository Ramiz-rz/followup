"""
Real LLM analysis. Only used when OPENAI_API_KEY is set. If the call
fails for any reason (no key, network error, bad JSON back), the
caller falls back to the local analyzer and the project is clearly
labeled "local", never presented as AI output.
"""
import json
import os
import logging

logger = logging.getLogger("followup.ai_analyzer")

SYSTEM_PROMPT = """You are part of FollowUp, a tool that finds commitments and waiting \
items hidden inside real conversations.

Read the conversation text and extract only what is actually there. Do not invent \
names, dates, or commitments that are not supported by the text.

A commitment is something a person explicitly agreed to do (e.g. "I'll send it \
tomorrow", "I'll take care of the API"), or an explicit assigned action \
("Can you remind me to check this Friday?"). A vague opinion or suggestion \
("I think we should update the dashboard") is NOT a commitment unless the \
speaker actually commits to doing it.

A waiting item is something the speaker or team is blocked on, waiting for \
someone else to do (e.g. "We are still waiting for the client to approve the \
design", "I haven't received the credentials yet").

Return ONLY valid JSON, no prose, no markdown code fences, matching exactly \
this shape:

{
  "summary": "one or two sentence plain-language summary of what's going on",
  "commitments": [
    {
      "action": "what will be done, in a short clear phrase",
      "person": "who committed to it, or 'Unclear' if not stated",
      "due_date_text": "the date phrase as written, e.g. 'tomorrow', or 'Unclear'",
      "priority": "high | medium | low",
      "confidence": 0.0,
      "evidence": "the exact sentence from the source text this came from"
    }
  ],
  "waiting_items": [
    {
      "item": "what is being waited on",
      "person": "who it's being waited on, or 'Unclear'",
      "waiting_since_text": "date phrase if mentioned, or 'Unclear'",
      "confidence": 0.0,
      "evidence": "the exact sentence from the source text this came from"
    }
  ]
}

confidence must be a number between 0 and 1 reflecting how clearly the text \
supports the extraction. evidence must be copied from the source text, not \
paraphrased."""


class AIAnalysisError(Exception):
    pass


def is_ai_configured() -> bool:
    return bool(os.getenv("OPENAI_API_KEY"))


def _strip_code_fence(raw: str) -> str:
    text = raw.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[-1]
        if text.endswith("```"):
            text = text[: -3]
        text = text.strip()
        if text.lower().startswith("json"):
            text = text[4:].strip()
    return text


def analyze_with_ai(text: str) -> dict:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise AIAnalysisError("No OpenAI API key is configured.")

    try:
        from openai import OpenAI
    except ImportError as e:
        raise AIAnalysisError("The OpenAI client library is not installed.") from e

    client = OpenAI(api_key=api_key)
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    try:
        response = client.chat.completions.create(
            model=model,
            temperature=0.1,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text[:20000]},
            ],
        )
    except Exception as e:
        logger.warning("OpenAI request failed: %s", e)
        raise AIAnalysisError(f"The OpenAI request failed: {e}") from e

    raw = response.choices[0].message.content or ""
    raw = _strip_code_fence(raw)

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        logger.warning("OpenAI returned malformed JSON: %s", raw[:500])
        raise AIAnalysisError("The AI response could not be parsed as JSON.") from e

    if not isinstance(data, dict):
        raise AIAnalysisError("The AI response was not a JSON object.")

    return data
