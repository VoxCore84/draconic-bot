"""Ephemeral conversation memory — short-lived session context with TTL."""

from __future__ import annotations

import time
import logging

from ai.schemas import ConversationTurn
from ai.settings import AI_SESSION_TTL_MINUTES

log = logging.getLogger(__name__)

_TTL_SECONDS = AI_SESSION_TTL_MINUTES * 60
_MAX_TURNS = 6


class ConversationSession:
    """A short-lived conversation context for one user/thread."""

    def __init__(self):
        self.turns: list[ConversationTurn] = []
        self.last_activity: float = time.time()

    def add_turn(self, role: str, content: str):
        self.turns.append(ConversationTurn(role=role, content=content))
        self.last_activity = time.time()
        # Keep only the last N turns
        if len(self.turns) > _MAX_TURNS:
            self.turns = self.turns[-_MAX_TURNS:]

    def is_expired(self) -> bool:
        return (time.time() - self.last_activity) > _TTL_SECONDS

    def get_context(self) -> list[dict]:
        """Return turns as a list of dicts for the provider."""
        return [{"role": t.role, "content": t.content} for t in self.turns]

    def __len__(self):
        return len(self.turns)


class SessionManager:
    """Manages ephemeral conversation sessions keyed by scope."""

    def __init__(self):
        # Key: session_key (thread_id or "channel_id:user_id")
        self._sessions: dict[str, ConversationSession] = {}

    def get_or_create(self, session_key: str) -> ConversationSession:
        self._prune_expired()
        if session_key not in self._sessions or self._sessions[session_key].is_expired():
            self._sessions[session_key] = ConversationSession()
        return self._sessions[session_key]

    def get(self, session_key: str) -> ConversationSession | None:
        session = self._sessions.get(session_key)
        if session and not session.is_expired():
            return session
        return None

    def make_key(self, channel_id: int, user_id: int, thread_id: int | None = None) -> str:
        """Build a session key. Thread ID takes priority if present."""
        if thread_id:
            return str(thread_id)
        return f"{channel_id}:{user_id}"

    def _prune_expired(self):
        """Remove expired sessions."""
        expired = [k for k, v in self._sessions.items() if v.is_expired()]
        for k in expired:
            del self._sessions[k]
        if expired:
            log.debug("Pruned %d expired sessions", len(expired))

    @property
    def active_count(self) -> int:
        self._prune_expired()
        return len(self._sessions)
