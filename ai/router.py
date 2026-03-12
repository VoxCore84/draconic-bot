"""AI router — decides whether to use AI, which route, and which model tier."""

from __future__ import annotations

import logging
import re
import time

import discord

from ai.kb import KnowledgeBase
from ai.metrics import MetricsTracker
from ai.prompts import build_system_prompt
from ai.provider import GeminiProvider, LLMProvider
from ai.safety import (
    HANDOFF_MESSAGE,
    OUTAGE_MESSAGE,
    check_content_boundaries,
    should_handoff,
    validate_response,
)
from ai.schemas import AIResult, ModelTier, RouteType
from ai.sessions import SessionManager
from ai.settings import (
    AI_ALLOWED_CHANNEL_IDS,
    AI_DAILY_HARD_CAP_USD,
    AI_ENABLED,
    AI_PRO_ESCALATION_DAILY_MAX,
    AI_PRO_ESCALATION_ENABLED,
    AI_RATE_CHANNEL_INTERVAL,
    AI_RATE_FRUSTRATION_USER,
    AI_RATE_PRO_HOURLY_MAX,
    AI_RATE_USER_MAX,
    AI_RATE_USER_WINDOW,
    AI_TEST_CHANNEL_IDS,
    TOKEN_BUDGETS,
)

log = logging.getLogger(__name__)

# --- Question detection heuristics ---

_QUESTION_WORDS = re.compile(
    r"(?:^|\b)(?:how|why|what|where|can't|cannot|stuck|error|issue|problem|won't|doesn't)\b",
    re.IGNORECASE,
)

_SETUP_KEYWORDS = re.compile(
    r"\b(?:server|mysql|database|arctium|config|worldserver|bnetserver|extract|maps?|vmaps?|mmaps?|"
    r"repack|compile|cmake|openssl|port|forward|connect|login|account|gm|admin|flying|mount|"
    r"dragonrid|skyrid|transmog|crash|quest|npc|spell|build|version|update|sql|heidi|uniserver)\b",
    re.IGNORECASE,
)

_FRUSTRATION_PATTERN = re.compile(
    r"(?:i.?m so|i.?m really|very|super)\s*(?:confused|frustrated|lost|giving up|give up|about to quit)|"
    r"(?:this is|it.?s)\s*(?:too hard|too difficult|impossible|make no sense)|"
    r"(?:i don.?t|i cannot|i can.?t)\s*(?:understand|figure this out|get this to work)|"
    r"i.?ve been trying for (?:hours|days|a long time)|"
    r"can someone (?:just )?(?:please )?(?:help|explain|hold my hand)",
    re.IGNORECASE,
)


def _looks_like_question(content: str) -> int:
    """Score how question-like a message is. Returns 0-5."""
    score = 0
    if "?" in content:
        score += 1
    if _QUESTION_WORDS.search(content):
        score += 1
    if _SETUP_KEYWORDS.search(content):
        score += 1
    if len(content.split()) >= 5 and len(content) >= 15:
        score += 1
    if any(content.lower().startswith(w) for w in ("how ", "why ", "what ", "where ", "can ")):
        score += 1
    return score


def _detect_route_type(content: str) -> RouteType:
    """Classify the message into a route type based on content."""
    content_lower = content.lower()

    if _FRUSTRATION_PATTERN.search(content):
        return RouteType.FRUSTRATION

    # GM command questions
    gm_keywords = [".additem", ".tele", ".learn", ".npc", ".lookup", ".modify",
                    ".go creature", ".go object", ".levelup", ".cast", "gm command",
                    "game master", "admin command"]
    if any(kw in content_lower for kw in gm_keywords):
        return RouteType.GM_KB

    # Troubleshooting (more complex, multi-step issues)
    troubleshoot_signals = ["tried", "already", "still ", "nothing work", "doesn't work",
                           "keeps ", "every time", "after i ", "when i try"]
    troubleshoot_count = sum(1 for s in troubleshoot_signals if s in content_lower)
    if troubleshoot_count >= 2:
        return RouteType.TROUBLESHOOT

    return RouteType.FAQ


def _select_model_tier(route_type: RouteType) -> ModelTier:
    """Pick the model tier based on route type."""
    if route_type in (RouteType.FAQ, RouteType.GM_KB):
        return ModelTier.FLASH_LITE
    if route_type in (RouteType.TROUBLESHOOT, RouteType.FRUSTRATION, RouteType.LOG_SUMMARY):
        return ModelTier.FLASH
    return ModelTier.FLASH_LITE


class AIRouter:
    """Central AI routing and orchestration layer.

    All cogs call this instead of Gemini directly.
    """

    def __init__(self):
        self.enabled = AI_ENABLED
        self.provider: LLMProvider = GeminiProvider()
        self.kb = KnowledgeBase()
        self.sessions = SessionManager()
        self.metrics = MetricsTracker()
        self._budget_exhausted = False

        # Rate limiting state
        self._channel_last_response: dict[int, float] = {}
        self._user_timestamps: dict[int, list[float]] = {}
        self._frustration_user_last: dict[int, float] = {}
        self._pro_hourly_timestamps: list[float] = []

    # --- Public API ---

    async def handle_message(
        self,
        message: discord.Message,
        force_route: RouteType | None = None,
        extra_context: str = "",
    ) -> AIResult | None:
        """Main entry point for AI-powered responses.

        Returns an AIResult if the AI should respond, or None if the message
        should be ignored (not eligible, rate limited, budget exhausted, etc.).
        """
        if not self.enabled:
            return None

        # Budget check
        if self._check_budget_exhausted():
            return None

        # Channel eligibility
        channel_id = message.channel.id
        all_allowed = AI_ALLOWED_CHANNEL_IDS | AI_TEST_CHANNEL_IDS
        if all_allowed and channel_id not in all_allowed:
            return None

        content = message.content
        if len(content) < 10:
            return None

        # Determine if this is a mention/reply vs organic question
        is_mention = message.mentions and any(
            m.id == message.guild.me.id for m in message.mentions
        ) if message.guild else False
        is_reply_to_bot = (
            message.reference
            and message.reference.resolved
            and isinstance(message.reference.resolved, discord.Message)
            and message.reference.resolved.author.bot
        )
        is_in_bot_thread = isinstance(message.channel, discord.Thread)

        # For organic (non-mention, non-reply) messages, need question heuristics
        if not is_mention and not is_reply_to_bot:
            # Don't interrupt threads unless it's a bot thread
            if is_in_bot_thread:
                pass  # OK to respond in threads the bot started
            elif isinstance(message.channel, discord.Thread):
                return None

            # Don't interrupt replies between humans
            if message.reference and not is_reply_to_bot:
                return None

            # Question score must be >= 2
            score = _looks_like_question(content)
            if score < 2:
                return None

        # Content boundary check
        boundary_flag = check_content_boundaries(content)
        if boundary_flag:
            return AIResult(
                route=RouteType.HANDOFF,
                confidence=0.0,
                needs_staff=False,
                answer_markdown="I can't help with that topic. If you have a server setup or gameplay question, I'm happy to assist!",
                safety_flags=[boundary_flag],
            )

        # Rate limiting
        now = time.time()
        route_type = force_route or _detect_route_type(content)

        if not self._check_rate_limits(message.author.id, channel_id, route_type, now):
            return None

        # Select model tier
        model_tier = _select_model_tier(route_type)

        # Pro escalation check
        if model_tier == ModelTier.PRO:
            if not AI_PRO_ESCALATION_ENABLED or not self._check_pro_rate(now):
                model_tier = ModelTier.FLASH  # downgrade

        # KB retrieval
        keywords = self.kb.extract_keywords(content)
        if extra_context:
            keywords.extend(self.kb.extract_keywords(extra_context))

        budget = TOKEN_BUDGETS.get(route_type.value, {"max_input": 2500, "max_output": 220})
        kb_snippets = self.kb.select_snippets(keywords, max_tokens=budget["max_input"] // 2)

        # Conversation context
        thread_id = message.channel.id if isinstance(message.channel, discord.Thread) else None
        session_key = self.sessions.make_key(channel_id, message.author.id, thread_id)

        session = None
        conversation_context_text = "No prior conversation."
        conversation_context_list = None

        if is_reply_to_bot or is_in_bot_thread:
            session = self.sessions.get_or_create(session_key)
            if len(session) > 0:
                conversation_context_list = session.get_context()
                conversation_context_text = "\n".join(
                    f"{t['role']}: {t['content'][:200]}" for t in conversation_context_list[-4:]
                )

        # Build prompt
        system_prompt = build_system_prompt(
            route_type=route_type,
            kb_snippets=kb_snippets,
            conversation_context=conversation_context_text,
        )

        user_prompt = content
        if extra_context:
            user_prompt = f"{content}\n\n[Additional context: {extra_context}]"

        # Call provider
        result = await self.provider.generate(
            route_type=route_type,
            model_tier=model_tier,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            conversation_context=conversation_context_list,
            max_output_tokens=budget["max_output"],
        )

        # Validate response
        result = validate_response(result, route_type)

        # Update session
        if session is not None:
            session.add_turn("user", content[:500])
            if result.answer_markdown and not should_handoff(result):
                session.add_turn("assistant", result.answer_markdown[:500])

        # Log metrics
        self.metrics.log_request(
            result=result,
            channel_id=channel_id,
            user_id=message.author.id,
            message_id=message.id,
        )

        # Track rate limits
        self._channel_last_response[channel_id] = now
        self._user_timestamps.setdefault(message.author.id, []).append(now)

        return result

    async def handle_admin_test(
        self,
        route_type: RouteType,
        text: str,
    ) -> AIResult:
        """Admin-only test endpoint — bypasses rate limits and channel checks."""
        model_tier = _select_model_tier(route_type)
        keywords = self.kb.extract_keywords(text)
        budget = TOKEN_BUDGETS.get(route_type.value, {"max_input": 2500, "max_output": 220})
        kb_snippets = self.kb.select_snippets(keywords, max_tokens=budget["max_input"] // 2)

        system_prompt = build_system_prompt(
            route_type=route_type,
            kb_snippets=kb_snippets,
        )

        result = await self.provider.generate(
            route_type=route_type,
            model_tier=model_tier,
            system_prompt=system_prompt,
            user_prompt=text,
            max_output_tokens=budget["max_output"],
        )
        return validate_response(result, route_type)

    def toggle(self, enabled: bool):
        self.enabled = enabled
        log.info("AI router %s", "enabled" if enabled else "disabled")

    def reload_kb(self):
        self.kb.load()
        log.info("Knowledge base reloaded")

    # --- Rate limiting ---

    def _check_rate_limits(self, user_id: int, channel_id: int, route: RouteType, now: float) -> bool:
        # Channel cooldown
        last = self._channel_last_response.get(channel_id, 0)
        if now - last < AI_RATE_CHANNEL_INTERVAL:
            return False

        # User rate limit
        timestamps = self._user_timestamps.get(user_id, [])
        timestamps = [t for t in timestamps if now - t < AI_RATE_USER_WINDOW]
        self._user_timestamps[user_id] = timestamps
        if len(timestamps) >= AI_RATE_USER_MAX:
            return False

        # Frustration cooldown
        if route == RouteType.FRUSTRATION:
            last_frust = self._frustration_user_last.get(user_id, 0)
            if now - last_frust < AI_RATE_FRUSTRATION_USER:
                return False
            self._frustration_user_last[user_id] = now

        return True

    def _check_pro_rate(self, now: float) -> bool:
        self._pro_hourly_timestamps = [t for t in self._pro_hourly_timestamps if now - t < 3600]
        if len(self._pro_hourly_timestamps) >= AI_RATE_PRO_HOURLY_MAX:
            return False
        self._pro_hourly_timestamps.append(now)
        return True

    def _check_budget_exhausted(self) -> bool:
        daily_spend = self.metrics.get_daily_spend()
        if daily_spend >= AI_DAILY_HARD_CAP_USD:
            if not self._budget_exhausted:
                log.warning("Daily AI budget exhausted: $%.4f >= $%.2f", daily_spend, AI_DAILY_HARD_CAP_USD)
                self._budget_exhausted = True
            return True
        self._budget_exhausted = False
        return False
