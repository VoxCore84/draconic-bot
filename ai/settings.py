"""AI configuration — loads AI-specific settings from environment."""

import os
from pathlib import Path
from config import _int_env


def _float_env(key: str, default: float = 0.0) -> float:
    val = os.getenv(key, "")
    return float(val) if val.strip() else default


def _bool_env(key: str, default: bool = False) -> bool:
    val = os.getenv(key, "").strip().lower()
    if not val:
        return default
    return val in ("true", "1", "yes", "on")


def _list_env(key: str) -> list[int]:
    """Parse a comma-separated list of ints from env."""
    val = os.getenv(key, "").strip()
    if not val:
        return []
    return [int(x.strip()) for x in val.split(",") if x.strip().isdigit()]


# --- Feature flags ---
AI_ENABLED = _bool_env("AI_ENABLED", False)

# --- Model names ---
AI_ROUTE_DEFAULT_MODEL = os.getenv("AI_ROUTE_DEFAULT_MODEL", "gemini-2.5-flash-lite")
AI_ROUTE_COMPLEX_MODEL = os.getenv("AI_ROUTE_COMPLEX_MODEL", "gemini-2.5-flash")
AI_ROUTE_PRO_MODEL = os.getenv("AI_ROUTE_PRO_MODEL", "gemini-2.5-pro")

# --- Channel lists ---
AI_ALLOWED_CHANNEL_IDS = set(_list_env("AI_ALLOWED_CHANNEL_IDS"))
AI_TEST_CHANNEL_IDS = set(_list_env("AI_TEST_CHANNEL_IDS"))

# --- Cost caps ---
AI_DAILY_HARD_CAP_USD = _float_env("AI_DAILY_HARD_CAP_USD", 1.50)
AI_MONTHLY_SOFT_CAP_USD = _float_env("AI_MONTHLY_SOFT_CAP_USD", 20.00)

# --- Timeouts ---
AI_RESPONSE_TIMEOUT_SECONDS = int(os.getenv("AI_RESPONSE_TIMEOUT_SECONDS", "20"))

# --- Session memory ---
AI_SESSION_TTL_MINUTES = int(os.getenv("AI_SESSION_TTL_MINUTES", "30"))

# --- Logging ---
AI_LOG_PREVIEW_ENABLED = _bool_env("AI_LOG_PREVIEW_ENABLED", True)

# --- Pro escalation ---
AI_PRO_ESCALATION_ENABLED = _bool_env("AI_PRO_ESCALATION_ENABLED", True)
AI_PRO_ESCALATION_DAILY_MAX = int(os.getenv("AI_PRO_ESCALATION_DAILY_MAX", "25"))

# --- Paths ---
_BOT_DIR = Path(__file__).parent.parent
AI_KB_DIR = _BOT_DIR / "knowledge"
AI_LOG_DIR = _BOT_DIR / "logs"
AI_DATA_DIR = _BOT_DIR / "data"
AI_METRICS_DB = AI_DATA_DIR / "ai_metrics.db"
AI_LOG_FILE = AI_LOG_DIR / "gemini_calls.jsonl"

# --- Rate limits ---
AI_RATE_CHANNEL_INTERVAL = 90       # seconds between AI responses per channel
AI_RATE_USER_MAX = 2                # max AI responses per user
AI_RATE_USER_WINDOW = 300           # per 5 minutes
AI_RATE_CHANNEL_PROACTIVE_MAX = 3   # proactive answers per channel
AI_RATE_CHANNEL_PROACTIVE_WINDOW = 600  # per 10 minutes
AI_RATE_FRUSTRATION_USER = 1800     # 30 min per user
AI_RATE_PRO_HOURLY_MAX = 5          # pro escalations per hour

# --- Token budgets per route ---
TOKEN_BUDGETS = {
    "faq":           {"max_input": 2500, "max_output": 220},
    "gm_kb":         {"max_input": 2500, "max_output": 220},
    "frustration":   {"max_input": 2500, "max_output": 250},
    "troubleshoot":  {"max_input": 4000, "max_output": 380},
    "log_summary":   {"max_input": 5000, "max_output": 450},
    "pro_escalation": {"max_input": 8000, "max_output": 500},
}
