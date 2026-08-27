"""In-process pending low-confidence tutor-handoff, keyed by session.

The next-turn "Yes" used to be reconstructed by scanning ``st_turns`` through
``MemoryTool.recent_pairs``. That method did not exist on ``MemoryTool``, the
lookup was wrapped in a bare ``except`` that returned ``None``, and even a
working ST scan read the *oldest* turns — so a student who said Yes after
"send this to your tutor?" was greeted instead of escalated.

This store is written the moment the agent asks the question, so the following
turn does not depend on persistence catching up (inbound "Yes" is logged
*before* the next recall) or on a method the memory facade may not expose.
``st_turns`` remains the durable fallback across process restarts.
"""

from __future__ import annotations

_pending: dict[str, str] = {}


def remember_pending_question(*, session_id: str, question: str) -> None:
    if session_id and question.strip():
        _pending[session_id] = question.strip()


def peek_pending_question(session_id: str) -> str | None:
    return _pending.get(session_id)


def clear_pending_question(session_id: str) -> None:
    _pending.pop(session_id, None)


def reset_pending_questions() -> None:
    _pending.clear()
