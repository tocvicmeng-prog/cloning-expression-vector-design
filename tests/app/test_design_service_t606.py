"""
module_id: tests.app.test_design_service_t606
file: tests/app/test_design_service_t606.py
task_id: T-606
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import TypedDict

import pytest

from app.design_service import (
    PENDING_STATE_GATES,
    DesignGateBlockedError,
    DesignService,
    PendingState,
)
from domain.events import (
    DesignCompiled,
    DomainEvent,
    OperationalProtocolAuthorised,
    ReviewerSignedOff,
    ScreeningCompleted,
    SessionId,
    SopRendered,
)
from domain.security import InstitutionId, PrincipalId, SecurityRole, UserPrincipal
from domain.sequence import sha256_text
from domain.types.derivation import PredicateVersion
from engine.session import (
    BLOCK_COMPILE,
    DesignSession,
    GatePredicateRegistry,
    GateState,
    GateVerdict,
    InMemorySnapshotStore,
    SessionState,
    blocked_verdict,
)

NOW = datetime(2026, 5, 14, tzinfo=UTC)


class _DesignBase(TypedDict):
    event_id: str
    occurred_at_utc: datetime
    actor_id: str
    session_id: SessionId


class _GovernanceBase(TypedDict):
    event_id: str
    occurred_at_utc: datetime
    actor_id: str
    institution_id: str


@dataclass
class InMemoryDesignEventLog:
    events: dict[str, list[DomainEvent]] = field(default_factory=dict)

    def append_event(self, stream_id: str, event: DomainEvent) -> str:
        self.events.setdefault(stream_id, []).append(event)
        return event.event_id

    def read_events(self, stream_id: str) -> tuple[DomainEvent, ...]:
        return tuple(self.events.get(stream_id, ()))


@dataclass
class InMemoryProjectStore:
    sessions: dict[str, DesignSession] = field(default_factory=dict)

    def save_session(self, session: DesignSession) -> str:
        self.sessions[session.session_id] = session
        return session.session_id


def test_create_open_amend_compile_and_replay_round_trip() -> None:
    service, log, store = _service()
    principal = _user()

    created = service.create_session(principal, "session-1", project_name="demo")
    service.add_part(
        principal,
        "session-1",
        part_id="part-egfp",
        part_payload_hash="part-hash",
    )
    service.select_host(principal, "session-1", host_id="ecoli-k12", host_role="expression")
    service.enter_free_text(principal, "session-1", text="express egfp in ecoli")
    service.confirm_translation(
        principal,
        "session-1",
        structured={"host": "ecoli-k12", "objective": "egfp-expression"},
    )
    compiled = service.compile_session(
        principal,
        "session-1",
        construct_id="construct-1",
        construct_checksum="checksum-1",
        design_plan_hash="plan-1",
    )

    opened = service.open_session(principal, "session-1")
    replayed = service.replay_session("session-1")

    assert created.event_id.endswith(":SessionStarted")
    assert compiled.session.state is SessionState.AWAITING_SCREENING
    assert opened.canonical_json() == replayed.canonical_json()
    assert store.sessions["session-1"].canonical_json() == replayed.canonical_json()
    assert [event.event_type for event in log.read_events("session-1")] == [
        "SessionStarted",
        "PartAdded",
        "HostSelected",
        "FreeTextEntered",
        "LLMTranslationConfirmed",
        "DesignCompiled",
    ]


@pytest.mark.parametrize(
    ("pending_state", "expected_gate", "expected_owner"),
    [
        (PendingState.AWAITING_SCREENING, "BlockVendorSubmission", "app.screening_orchestrator"),
        (
            PendingState.AWAITING_AUTHORISATION,
            "BlockOperationalProtocol",
            "app.authorisation_decision",
        ),
        (
            PendingState.AWAITING_SOP_RENDER,
            "BlockOperationalProtocol",
            "app.sop_protocol_orchestrator",
        ),
        (PendingState.AWAITING_EXPORT, "BlockExport", "app.export_orchestrator"),
    ],
)
def test_pending_state_taxonomy_uses_registered_t309_gates(
    pending_state: PendingState,
    expected_gate: str,
    expected_owner: str,
) -> None:
    registry = GatePredicateRegistry.with_pending_defaults()

    assert PENDING_STATE_GATES[pending_state] in registry.registrations
    assert str(PENDING_STATE_GATES[pending_state]) == expected_gate

    service, log, _store = _compiled_service(registry=registry)
    governance_events: tuple[ReviewerSignedOff, ...] = ()
    if pending_state is PendingState.AWAITING_AUTHORISATION:
        log.append_event("session-1", _screening_clear(7))
    elif pending_state is PendingState.AWAITING_SOP_RENDER:
        log.append_event("session-1", _screening_clear(7))
        log.append_event("session-1", _authorised(8))
        governance_events = (_reviewer_signed_off(8),)
    elif pending_state is PendingState.AWAITING_EXPORT:
        log.append_event("session-1", _screening_clear(7))
        log.append_event("session-1", _authorised(8))
        log.append_event("session-1", _sop_rendered(9))
        governance_events = (_reviewer_signed_off(8),)

    current = service.current_pending_state("session-1", governance_events=governance_events)

    assert current is not None
    assert current.state is pending_state
    assert current.gate_verdict.state is GateState.PENDING_NOT_YET_ACTIVATED
    assert current.downstream_owner == expected_owner


def test_compile_honours_activated_block_compile_gate_without_appending_event() -> None:
    version = PredicateVersion("1.0.0")
    content_hash = sha256_text("block compile in T-606 test")

    def predicate(_session: DesignSession) -> GateVerdict:
        return blocked_verdict(
            BLOCK_COMPILE,
            version,
            content_hash,
            reason="validation hard failure",
        )

    registry = GatePredicateRegistry.with_pending_defaults().activate(
        BLOCK_COMPILE,
        predicate,
        version=version,
        content_hash=content_hash,
    )
    service, log, _store = _draft_service(registry=registry)

    with pytest.raises(DesignGateBlockedError, match="validation hard failure"):
        service.compile_session(
            _user(),
            "session-1",
            construct_id="construct-1",
            construct_checksum="checksum-1",
            design_plan_hash="plan-1",
        )

    assert not any(isinstance(event, DesignCompiled) for event in log.read_events("session-1"))


def _service(
    *,
    registry: GatePredicateRegistry | None = None,
) -> tuple[DesignService, InMemoryDesignEventLog, InMemoryProjectStore]:
    log = InMemoryDesignEventLog()
    store = InMemoryProjectStore()
    service = DesignService(
        design_event_log=log,
        project_store=store,
        snapshot_store=InMemorySnapshotStore(),
        gate_registry=registry,
        clock=_clock(),
    )
    return service, log, store


def _draft_service(
    *,
    registry: GatePredicateRegistry | None = None,
) -> tuple[DesignService, InMemoryDesignEventLog, InMemoryProjectStore]:
    service, log, store = _service(registry=registry)
    principal = _user()
    service.create_session(principal, "session-1", project_name="demo")
    service.confirm_translation(principal, "session-1", structured={"objective": "egfp"})
    return service, log, store


def _compiled_service(
    *,
    registry: GatePredicateRegistry | None = None,
) -> tuple[DesignService, InMemoryDesignEventLog, InMemoryProjectStore]:
    service, log, store = _draft_service(registry=registry)
    service.compile_session(
        _user(),
        "session-1",
        construct_id="construct-1",
        construct_checksum="checksum-1",
        design_plan_hash="plan-1",
    )
    return service, log, store


def _user() -> UserPrincipal:
    return UserPrincipal(
        id=PrincipalId("user-1"),
        role=SecurityRole.USER,
        institution=InstitutionId("institution-1"),
        credentials_verified_at=NOW,
    )


def _clock() -> Callable[[], datetime]:
    counter = 0

    def next_time() -> datetime:
        nonlocal counter
        counter += 1
        return NOW + timedelta(seconds=counter)

    return next_time


def _design_base(index: int) -> _DesignBase:
    return {
        "event_id": f"external-design-{index}",
        "occurred_at_utc": NOW + timedelta(seconds=index),
        "actor_id": "external-service",
        "session_id": "session-1",
    }


def _governance_base(index: int) -> _GovernanceBase:
    return {
        "event_id": f"external-governance-{index}",
        "occurred_at_utc": NOW + timedelta(seconds=index),
        "actor_id": "reviewer-1",
        "institution_id": "institution-1",
    }


def _screening_clear(index: int) -> ScreeningCompleted:
    return ScreeningCompleted(
        **_design_base(index),
        batch_id="batch-1",
        verdict_payload=(("verdict", "clear"),),
    )


def _authorised(index: int) -> OperationalProtocolAuthorised:
    return OperationalProtocolAuthorised(
        **_design_base(index),
        profile_id="profile-1",
        decision_record_hash="decision-1",
    )


def _sop_rendered(index: int) -> SopRendered:
    return SopRendered(**_design_base(index), sop_bundle_hash="sop-1")


def _reviewer_signed_off(index: int) -> ReviewerSignedOff:
    return ReviewerSignedOff(
        **_governance_base(index),
        decision_record_payload=(("decision", "approved"),),
        decision_record_hash="decision-1",
    )
