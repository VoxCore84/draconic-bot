"""AI usage metrics — JSONL logging + SQLite rollups."""

from __future__ import annotations

import hashlib
import json
import logging
import sqlite3
import time
from datetime import datetime, timezone
from pathlib import Path

from ai.schemas import AIResult, MetricsEntry
from ai.settings import AI_LOG_FILE, AI_METRICS_DB

log = logging.getLogger(__name__)


def _ensure_dirs():
    AI_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    AI_METRICS_DB.parent.mkdir(parents=True, exist_ok=True)


def _hash_user_id(user_id: int) -> str:
    return hashlib.sha256(str(user_id).encode()).hexdigest()[:16]


def _init_db(conn: sqlite3.Connection):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS ai_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT NOT NULL,
            date TEXT NOT NULL,
            route TEXT NOT NULL,
            model TEXT NOT NULL,
            input_tokens INTEGER DEFAULT 0,
            output_tokens INTEGER DEFAULT 0,
            latency_ms INTEGER DEFAULT 0,
            estimated_cost_usd REAL DEFAULT 0.0,
            confidence REAL DEFAULT 0.0,
            needs_staff INTEGER DEFAULT 0,
            fallback_used INTEGER DEFAULT 0,
            error TEXT
        )
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_ai_requests_date ON ai_requests(date)
    """)
    conn.commit()


class MetricsTracker:
    """Logs AI calls to JSONL and SQLite for monitoring."""

    def __init__(self):
        _ensure_dirs()
        self._db = sqlite3.connect(str(AI_METRICS_DB))
        _init_db(self._db)

    def log_request(self, result: AIResult, channel_id: int, user_id: int, message_id: int):
        now = datetime.now(timezone.utc)
        ts_str = now.isoformat()
        date_str = now.strftime("%Y-%m-%d")

        entry = MetricsEntry(
            ts=ts_str,
            route=result.route.value,
            model=result.model_used,
            channel_id=channel_id,
            user_id_hash=_hash_user_id(user_id),
            message_id=message_id,
            input_tokens=result.input_tokens,
            output_tokens=result.output_tokens,
            latency_ms=result.latency_ms,
            estimated_cost_usd=self._estimate_cost(result),
            confidence=result.confidence,
            needs_staff=result.needs_staff,
            used_kb_sections=result.used_kb_sections,
            fallback_used=result.fallback_used,
            error=result.error,
        )

        # JSONL log
        try:
            with open(AI_LOG_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry.__dict__, default=str) + "\n")
        except Exception:
            log.exception("Failed to write JSONL log")

        # SQLite
        try:
            self._db.execute(
                """INSERT INTO ai_requests
                   (ts, date, route, model, input_tokens, output_tokens, latency_ms,
                    estimated_cost_usd, confidence, needs_staff, fallback_used, error)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (ts_str, date_str, entry.route, entry.model,
                 entry.input_tokens, entry.output_tokens, entry.latency_ms,
                 entry.estimated_cost_usd, entry.confidence,
                 int(entry.needs_staff), int(entry.fallback_used), entry.error),
            )
            self._db.commit()
        except Exception:
            log.exception("Failed to write SQLite metrics")

    def get_daily_spend(self, date_str: str | None = None) -> float:
        if date_str is None:
            date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        row = self._db.execute(
            "SELECT COALESCE(SUM(estimated_cost_usd), 0) FROM ai_requests WHERE date = ?",
            (date_str,),
        ).fetchone()
        return row[0] if row else 0.0

    def get_monthly_spend(self) -> float:
        now = datetime.now(timezone.utc)
        month_prefix = now.strftime("%Y-%m")
        row = self._db.execute(
            "SELECT COALESCE(SUM(estimated_cost_usd), 0) FROM ai_requests WHERE date LIKE ?",
            (f"{month_prefix}%",),
        ).fetchone()
        return row[0] if row else 0.0

    def get_daily_pro_count(self, date_str: str | None = None) -> int:
        if date_str is None:
            date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        row = self._db.execute(
            "SELECT COUNT(*) FROM ai_requests WHERE date = ? AND model LIKE '%pro%'",
            (date_str,),
        ).fetchone()
        return row[0] if row else 0

    def get_stats_24h(self) -> dict:
        """Get usage stats for the last 24 hours."""
        cutoff = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
        # Simplify: just use today's date
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        rows = self._db.execute(
            """SELECT COUNT(*) as total,
                      COALESCE(SUM(estimated_cost_usd), 0) as spend,
                      COALESCE(AVG(latency_ms), 0) as avg_latency,
                      COALESCE(SUM(CASE WHEN error IS NOT NULL THEN 1 ELSE 0 END), 0) as errors,
                      COALESCE(SUM(fallback_used), 0) as fallbacks,
                      COALESCE(SUM(needs_staff), 0) as handoffs
               FROM ai_requests WHERE date = ?""",
            (date_str,),
        ).fetchone()
        return {
            "requests": rows[0],
            "spend_usd": round(rows[1], 4),
            "avg_latency_ms": int(rows[2]),
            "errors": rows[3],
            "fallbacks": rows[4],
            "handoffs": rows[5],
        }

    def get_stats_30d(self) -> dict:
        """Get usage stats for the last 30 days."""
        rows = self._db.execute(
            """SELECT COUNT(*) as total,
                      COALESCE(SUM(estimated_cost_usd), 0) as spend,
                      COALESCE(AVG(latency_ms), 0) as avg_latency,
                      COALESCE(SUM(CASE WHEN error IS NOT NULL THEN 1 ELSE 0 END), 0) as errors
               FROM ai_requests
               WHERE date >= date('now', '-30 days')""",
        ).fetchone()
        return {
            "requests": rows[0],
            "spend_usd": round(rows[1], 4),
            "avg_latency_ms": int(rows[2]),
            "errors": rows[3],
        }

    def get_route_breakdown(self) -> dict[str, int]:
        """Get request counts by route for today."""
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        rows = self._db.execute(
            "SELECT route, COUNT(*) FROM ai_requests WHERE date = ? GROUP BY route",
            (date_str,),
        ).fetchall()
        return {row[0]: row[1] for row in rows}

    @staticmethod
    def _estimate_cost(result: AIResult) -> float:
        from ai.provider import _PRICING
        pricing = _PRICING.get(result.model_used, {"input": 0.15, "output": 0.60})
        return (
            (result.input_tokens / 1_000_000 * pricing["input"])
            + (result.output_tokens / 1_000_000 * pricing["output"])
        )

    def close(self):
        self._db.close()
