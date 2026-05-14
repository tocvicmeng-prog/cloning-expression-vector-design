"""
module_id: tests.engine.session.test_replay_determinism
file: tests/engine/session/test_replay_determinism.py
task_id: T-309
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import TypedDict

import pytest

from domain.events import (
    DesignCompiled,
    DesignEvent,
    DomainEvent,
    GatePredicateVersionBumped,
    LLMTranslationConfirmed,
    OperationalProtocolAuthorised,
    ReviewerSignedOff,
    ScreeningCompleted,
    SessionStarted,
    SopRendered,
)
from engine.session import ReplayIntegrityFailure, replay_canonical_json, replay_design_events

BASE_TIME = datetime(2026, 5, 14, tzinfo=UTC)


class _DesignBase(TypedDict):
    event_id: str
    occurred_at_utc: datetime
    actor_id: str
    session_id: str


class _GovernanceBase(TypedDict):
    event_id: str
    occurred_at_utc: datetime
    actor_id: str
    institution_id: str


def _design_base(session_id: str, index: int) -> _DesignBase:
    return {
        "event_id": f"{session_id}-event-{index}",
        "occurred_at_utc": BASE_TIME + timedelta(seconds=index),
        "actor_id": "user-1",
        "session_id": session_id,
    }


def _governance_base(index: int) -> _GovernanceBase:
    return {
        "event_id": f"governance-event-{index}",
        "occurred_at_utc": BASE_TIME + timedelta(seconds=index),
        "actor_id": "reviewer-1",
        "institution_id": "institution-1",
    }


def _session_events(session_id: str, index: int) -> tuple[DesignEvent, ...]:
    return (
        SessionStarted(**_design_base(session_id, 1), project_name=f"demo-{index}"),
        LLMTranslationConfirmed(
            **_design_base(session_id, 2),
            structured=(("objective", f"construct-{index}"),),
        ),
        DesignCompiled(
            **_design_base(session_id, 3),
            construct_id=f"construct-{index}",
            construct_checksum=f"checksum-{index}",
            design_plan_hash=f"plan-{index}",
        ),
        ScreeningCompleted(
            **_design_base(session_id, 4),
            batch_id=f"batch-{index}",
            verdict_payload=(("verdict", "clear"),),
        ),
        OperationalProtocolAuthorised(
            **_design_base(session_id, 5),
            profile_id="profile-1",
            decision_record_hash=f"decision-{index}",
        ),
        SopRendered(**_design_base(session_id, 6), sop_bundle_hash=f"sop-{index}"),
    )


def _reviewer_event(index: int) -> ReviewerSignedOff:
    return ReviewerSignedOff(
        **_governance_base(index),
        decision_record_payload=(("decision", "approved"), ("index", str(index))),
        decision_record_hash=f"decision-{index}",
    )


def test_replay_is_byte_identical_for_100_synthetic_sessions() -> None:
    for index in range(100):
        events = _session_events(f"session-{index}", index)
        governance = (_reviewer_event(index),)

        first = replay_canonical_json(events, governance_events=governance)
        second = replay_canonical_json(
            tuple(reversed(tuple(reversed(events)))), governance_events=governance
        )

        assert first == second


def test_cross_stream_invariant_requires_embedded_signed_governance_payload() -> None:
    events = _session_events("session-cross-stream", 200)

    with pytest.raises(ReplayIntegrityFailure, match="ReviewerSignedOff"):
        replay_design_events(events, governance_events=())

    state = replay_design_events(events, governance_events=(_reviewer_event(200),))
    assert state.state.value == "READY_TO_EXPORT"


def test_design_stream_owns_screening_authorisation_and_sop_events() -> None:
    events = _session_events("session-stream-owner", 300)

    assert {event.stream.value for event in events[-3:]} == {"design"}


def test_gate_predicate_version_bumped_governance_event_round_trips() -> None:
    event = GatePredicateVersionBumped(
        **_governance_base(500),
        gate_name="BlockCompile",
        old_predicate_version="1.0.0",
        new_predicate_version="1.1.0",
        predicate_content_hash="hash-v1-1",
        decision_record_payload=(("decision", "approved"),),
        decision_record_hash="decision-hash",
    )

    restored = DomainEvent.from_dict(event.to_dict())

    assert isinstance(restored, GatePredicateVersionBumped)
    assert restored.decision_record_payload == (("decision", "approved"),)
