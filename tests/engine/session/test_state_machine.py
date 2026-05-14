"""
module_id: tests.engine.session.test_state_machine
file: tests/engine/session/test_state_machine.py
task_id: T-309
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import TypedDict

import pytest

from domain.events import (
    DesignCompiled,
    DesignEvent,
    FreeTextEntered,
    HostSelected,
    LLMTranslationConfirmed,
    OperationalProtocolAuthorised,
    PartAdded,
    ScreeningCompleted,
    SessionStarted,
    SopRendered,
)
from engine.session import SessionState, SessionTransitionError, empty_session

BASE_TIME = datetime(2026, 5, 14, tzinfo=UTC)


class _DesignBase(TypedDict):
    event_id: str
    occurred_at_utc: datetime
    actor_id: str
    session_id: str


def _event_base(index: int) -> _DesignBase:
    return {
        "event_id": f"event-{index}",
        "occurred_at_utc": BASE_TIME + timedelta(seconds=index),
        "actor_id": "actor-1",
        "session_id": "session-1",
    }


def _happy_path_events() -> tuple[DesignEvent, ...]:
    return (
        SessionStarted(**_event_base(1), project_name="demo"),
        PartAdded(**_event_base(2), part_id="part-a", part_payload_hash="hash-part"),
        HostSelected(**_event_base(3), host_id="ecoli", host_role="expression"),
        FreeTextEntered(**_event_base(4), text="express egfp"),
        LLMTranslationConfirmed(**_event_base(5), structured=(("objective", "egfp"),)),
        DesignCompiled(
            **_event_base(6),
            construct_id="construct-1",
            construct_checksum="checksum-1",
            design_plan_hash="plan-1",
        ),
        ScreeningCompleted(
            **_event_base(7),
            batch_id="batch-1",
            verdict_payload=(("verdict", "clear"),),
        ),
        OperationalProtocolAuthorised(
            **_event_base(8),
            profile_id="profile-1",
            decision_record_hash="decision-1",
        ),
        SopRendered(**_event_base(9), sop_bundle_hash="sop-1"),
    )


def test_happy_path_state_transitions() -> None:
    session = empty_session("session-1")
    expected_states = (
        SessionState.COLLECTING,
        SessionState.COLLECTING,
        SessionState.COLLECTING,
        SessionState.COLLECTING,
        SessionState.DRAFT,
        SessionState.AWAITING_SCREENING,
        SessionState.AWAITING_AUTHORISATION,
        SessionState.AWAITING_SOP_RENDER,
        SessionState.READY_TO_EXPORT,
    )

    for event, expected_state in zip(_happy_path_events(), expected_states, strict=True):
        session = session.apply(event)
        assert session.state is expected_state

    assert session.construct_id == "construct-1"
    assert session.screening_verdict == "CLEAR"
    assert session.sop_bundle_hash == "sop-1"


@pytest.mark.parametrize(
    ("verdict", "expected_state"),
    [
        ("hit", SessionState.BLOCKED_BY_HIT),
        ("watchlist", SessionState.AWAITING_REVIEWER_SIGNOFF),
        ("manual_review_required", SessionState.AWAITING_REVIEWER_SIGNOFF),
        ("unavailable", SessionState.BLOCKED_BY_POLICY),
        ("not_applicable", SessionState.AWAITING_AUTHORISATION),
    ],
)
def test_screening_verdict_branches(verdict: str, expected_state: SessionState) -> None:
    session = empty_session("session-1")
    for event in _happy_path_events()[:6]:
        session = session.apply(event)

    session = session.apply(
        ScreeningCompleted(
            **_event_base(17),
            batch_id="batch-2",
            verdict_payload=(("verdict", verdict),),
        )
    )

    assert session.state is expected_state
    assert session.screening_verdict == verdict.upper()


def test_invalid_transition_is_rejected() -> None:
    session = empty_session("session-1")

    with pytest.raises(SessionTransitionError, match="DesignCompiled cannot be applied"):
        session.apply(
            DesignCompiled(
                **_event_base(1),
                construct_id="construct-1",
                construct_checksum="checksum",
                design_plan_hash="plan",
            )
        )


def test_duplicate_identical_event_is_idempotent_but_conflicting_duplicate_is_rejected() -> None:
    event = SessionStarted(**_event_base(1), project_name="demo")
    session = empty_session("session-1").apply(event)

    assert session.apply(event) == session

    conflicting = SessionStarted(**_event_base(1), project_name="different")
    with pytest.raises(SessionTransitionError, match="conflicting duplicate"):
        session.apply(conflicting)
