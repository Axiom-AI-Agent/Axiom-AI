"""In-memory onboarding session store — Week 13 SessionStore pattern.

Onboarding slots live here until the student confirms enrollment.
No student or enrollment rows are written to the database during collection.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from services.admissions.onboarding_flow import OnboardingSlots, OnboardingState


@dataclass
class OnboardingSession:
    """Ephemeral multi-turn onboarding progress for one tenant+phone pair."""

    slots: OnboardingSlots = field(default_factory=OnboardingSlots)
    active: bool = False
    awaiting_confirmation: bool = False
    next_step: str | None = None
    ambiguous_classes: list[dict] = field(default_factory=list)

    def to_state(self) -> OnboardingState:
        state = OnboardingState(
            slots=self.slots,
            next_step=self.next_step,
            awaiting_confirmation=self.awaiting_confirmation,
            ambiguous_classes=list(self.ambiguous_classes),
        )
        state.complete = self.slots.confirmed and bool(self.slots.class_id)
        return state

    @classmethod
    def from_state(cls, state: OnboardingState, *, active: bool = True) -> OnboardingSession:
        return cls(
            slots=state.slots,
            active=active,
            awaiting_confirmation=state.awaiting_confirmation,
            next_step=state.next_step,
            ambiguous_classes=list(state.ambiguous_classes),
        )


class OnboardingSessionStore:
    """Process-local store keyed by ``tenant_id:phone``."""

    def __init__(self) -> None:
        self._sessions: dict[str, OnboardingSession] = {}

    @staticmethod
    def session_key(*, tenant_id: str, phone: str) -> str:
        return f"{tenant_id}:{phone}"

    def get(self, *, tenant_id: str, phone: str) -> OnboardingSession | None:
        return self._sessions.get(self.session_key(tenant_id=tenant_id, phone=phone))

    def save(self, *, tenant_id: str, phone: str, session: OnboardingSession) -> None:
        self._sessions[self.session_key(tenant_id=tenant_id, phone=phone)] = session

    def clear(self, *, tenant_id: str, phone: str) -> None:
        self._sessions.pop(self.session_key(tenant_id=tenant_id, phone=phone), None)

    def start(self, *, tenant_id: str, phone: str) -> OnboardingSession:
        session = OnboardingSession(active=True, next_step="name")
        self.save(tenant_id=tenant_id, phone=phone, session=session)
        return session

    def is_active(self, *, tenant_id: str, phone: str) -> bool:
        session = self.get(tenant_id=tenant_id, phone=phone)
        return session is not None and session.active


_default_store: OnboardingSessionStore | None = None


def get_onboarding_session_store() -> OnboardingSessionStore:
    global _default_store
    if _default_store is None:
        _default_store = OnboardingSessionStore()
    return _default_store
