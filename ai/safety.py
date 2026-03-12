"""Safety rails — confidence gates, content boundaries, response validation."""

from __future__ import annotations

import re
import logging

from ai.schemas import AIResult, RouteType
from ai.settings import TOKEN_BUDGETS

log = logging.getLogger(__name__)

# Content boundary patterns — refuse or hand off
_REFUSE_PATTERNS = [
    re.compile(r"\b(?:blizzard\s+tos|terms\s+of\s+service|eula)\b", re.IGNORECASE),
    re.compile(r"\b(?:piracy|pirate|torrent|crack|warez|keygen)\b", re.IGNORECASE),
    re.compile(r"\b(?:cheat|hack|exploit|bot|aimbot|speedhack)\b", re.IGNORECASE),
    re.compile(r"\b(?:suicide|self.?harm|kill\s+(?:my|your)self)\b", re.IGNORECASE),
    re.compile(r"\b(?:legal\s+advice|lawyer|sue|lawsuit)\b", re.IGNORECASE),
    re.compile(r"\b(?:medical\s+advice|doctor|diagnosis|symptom)\b", re.IGNORECASE),
    re.compile(r"\b(?:password|token|secret|api.?key|credential)\b.*\b(?:share|give|send|post)\b", re.IGNORECASE),
    re.compile(r"\b(?:share|give|send|post)\b.*\b(?:password|token|secret|api.?key|credential)\b", re.IGNORECASE),
]

# Handoff message for staff
HANDOFF_MESSAGE = "I'm not sure I can help with that one. A staff member should be able to assist you — try asking in the support channel!"

OUTAGE_MESSAGE = "I'm having trouble reaching my AI backend right now. In the meantime, try `/troubleshoot` for interactive help, or ask a staff member."


def check_content_boundaries(user_message: str) -> str | None:
    """Check if the user message hits content boundaries.

    Returns a safety flag string if blocked, None if OK.
    """
    for pattern in _REFUSE_PATTERNS:
        if pattern.search(user_message):
            return "content_boundary"
    return None


def validate_response(result: AIResult, route_type: RouteType) -> AIResult:
    """Validate an AI response against safety rules.

    May modify the result (e.g., replace answer with handoff).
    """
    # Safety flags = immediate handoff
    if result.safety_flags:
        log.warning("AI returned safety flags: %s", result.safety_flags)
        result.needs_staff = True
        result.answer_markdown = HANDOFF_MESSAGE
        result.confidence = 0.0
        return result

    # Confidence gates
    if result.confidence < 0.45:
        result.needs_staff = True
        if result.follow_up_question:
            # Low confidence but has a clarifying question — ask it
            result.answer_markdown = result.follow_up_question
            result.needs_staff = False
        else:
            result.answer_markdown = HANDOFF_MESSAGE
        return result

    if 0.45 <= result.confidence < 0.70:
        # Add uncertainty qualifier if not already present
        qualifiers = ["i think", "i believe", "likely", "probably", "not 100% sure", "might be"]
        has_qualifier = any(q in result.answer_markdown.lower() for q in qualifiers)
        if not has_qualifier:
            result.answer_markdown = f"*I'm fairly confident about this, but not 100% sure:*\n\n{result.answer_markdown}"

    # KB evidence check — warn but don't force handoff
    # The model often answers correctly from system prompt context without
    # explicitly listing used_kb_sections in its JSON output
    kb_routes = {RouteType.FAQ, RouteType.GM_KB, RouteType.TROUBLESHOOT}
    if route_type in kb_routes and not result.used_kb_sections:
        log.info("AI response for %s has no KB evidence — allowing (model may have used system prompt context)", route_type.value)

    # Output budget check (allow 20% overflow)
    budget = TOKEN_BUDGETS.get(route_type.value, {"max_output": 300})
    max_output = budget["max_output"]
    # Rough token estimate: 1 token ≈ 4 chars
    estimated_tokens = len(result.answer_markdown) / 4
    if estimated_tokens > max_output * 1.2:
        # Truncate to budget
        char_limit = int(max_output * 4 * 1.2)
        result.answer_markdown = result.answer_markdown[:char_limit].rsplit("\n", 1)[0]
        result.answer_markdown += "\n\n*[Response trimmed for brevity]*"

    # Multiple follow-up questions check
    question_marks = result.follow_up_question.count("?")
    if question_marks > 1:
        # Keep only the first question
        first_q = result.follow_up_question.split("?")[0] + "?"
        result.follow_up_question = first_q

    return result


def should_handoff(result: AIResult) -> bool:
    """Determine if this result requires a staff handoff."""
    return result.needs_staff or result.confidence < 0.45 or bool(result.safety_flags)
