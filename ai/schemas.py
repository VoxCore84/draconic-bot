"""Data schemas for the AI support pipeline."""

from __future__ import annotations

import enum
import time
from dataclasses import dataclass, field


class RouteType(enum.Enum):
    FAQ = "faq"
    TROUBLESHOOT = "troubleshoot"
    FRUSTRATION = "frustration"
    GM_KB = "gm_kb"
    LOG_SUMMARY = "log_summary"
    HANDOFF = "handoff"


class ModelTier(enum.Enum):
    FLASH_LITE = "flash_lite"
    FLASH = "flash"
    PRO = "pro"


@dataclass
class AIResult:
    route: RouteType
    confidence: float
    needs_staff: bool
    answer_markdown: str
    follow_up_question: str = ""
    used_kb_sections: list[str] = field(default_factory=list)
    safety_flags: list[str] = field(default_factory=list)
    model_used: str = ""
    input_tokens: int = 0
    output_tokens: int = 0
    latency_ms: int = 0
    fallback_used: bool = False
    error: str | None = None


@dataclass
class CostEstimate:
    input_tokens: int
    output_tokens: int
    model: str
    estimated_usd: float


@dataclass
class ProviderHealth:
    available: bool
    latency_ms: int = 0
    error: str | None = None


@dataclass
class KBSnippet:
    """A selected knowledge base section."""
    file_key: str  # e.g. "30_setup_and_connection"
    title: str
    content: str
    tags: list[str] = field(default_factory=list)


@dataclass
class ConversationTurn:
    role: str  # "user" or "assistant"
    content: str
    timestamp: float = field(default_factory=time.time)


@dataclass
class MetricsEntry:
    ts: str
    route: str
    model: str
    channel_id: int
    user_id_hash: str
    message_id: int
    input_tokens: int
    output_tokens: int
    latency_ms: int
    estimated_cost_usd: float
    confidence: float
    needs_staff: bool
    used_kb_sections: list[str]
    fallback_used: bool
    error: str | None
