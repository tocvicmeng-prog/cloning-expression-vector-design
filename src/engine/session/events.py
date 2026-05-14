"""
module_id: engine.session.events
file: src/engine/session/events.py
task_id: T-309

Event replay and cross-stream replay invariants.
"""

from __future__ import annotations

from collections.abc import Iterable

from domain.events import (
    AdvisoryWarningPresented,
    DesignEvent,
    DomainEvent,
    GovernanceEvent,
    OperationalProtocolAuthorised,
    ReviewerSignedOff,
    RiskAdvisoryAcknowledged,
    RiskAdvisoryDeclined,
    RiskAdvisoryEscalated,
    ScreeningCompleted,
    SessionStarted,
    SopRendered,
)
from domain.sequence import Sha256
from engine.session.state_machine import DesignSession, SessionTransitionError, empty_session

DESIGN_STREAM_ONLY_EVENT_TYPES = frozenset(
    {
        ScreeningCompleted.event_type,
        OperationalProtocolAuthorised.event_type,
        SopRendered.event_type,
    }
)


class ReplayIntegrityFailure(ValueError):
    """Raised when persisted event streams cannot replay into a trustworthy state."""


def replay_design_events(
    design_events: Iterable[DesignEvent],
    *,
    governance_events: Iterable[GovernanceEvent] = (),
    initial_snapshot: DesignSession | None = None,
    derivation_environment_hash: Sha256 | None = None,
) -> DesignSession:
    events = tuple(design_events)
    if not events and initial_snapshot is None:
        raise ReplayIntegrityFailure("cannot replay an empty design stream without a snapshot")

    governance = tuple(governance_events)
    ensure_cross_stream_invariants(events, governance)

    session = (
        initial_snapshot if initial_snapshot is not None else _session_from_first_event(events[0])
    )
    if derivation_environment_hash is not None:
        session = _with_environment_hash(session, derivation_environment_hash)
    for event in events:
        try:
            session = session.apply(event)
        except SessionTransitionError as exc:
            raise ReplayIntegrityFailure(str(exc)) from exc
    return session


def replay_canonical_json(
    design_events: Iterable[DesignEvent],
    *,
    governance_events: Iterable[GovernanceEvent] = (),
    initial_snapshot: DesignSession | None = None,
    derivation_environment_hash: Sha256 | None = None,
) -> str:
    return replay_design_events(
        design_events,
        governance_events=governance_events,
        initial_snapshot=initial_snapshot,
        derivation_environment_hash=derivation_environment_hash,
    ).canonical_json()


def ensure_cross_stream_invariants(
    design_events: Iterable[DesignEvent],
    governance_events: Iterable[GovernanceEvent],
) -> None:
    design = tuple(design_events)
    governance = tuple(governance_events)
    _assert_design_stream_owns_design_only_events((*design, *governance))

    session_ids = frozenset(event.session_id for event in design)
    reviewer_hashes = _reviewer_decision_hashes(governance)
    for event in design:
        if (
            isinstance(event, OperationalProtocolAuthorised)
            and event.decision_record_hash not in reviewer_hashes
        ):
            raise ReplayIntegrityFailure(
                "OperationalProtocolAuthorised references no embedded ReviewerSignedOff payload"
            )

    for governance_event in governance:
        if (
            isinstance(governance_event, AdvisoryWarningPresented)
            and governance_event.design_session_id not in session_ids
        ):
            raise ReplayIntegrityFailure(
                "advisory presentation references an unknown design session"
            )
        if isinstance(
            governance_event,
            RiskAdvisoryAcknowledged | RiskAdvisoryDeclined | RiskAdvisoryEscalated,
        ):
            _require_embedded_payload(governance_event)


def _session_from_first_event(event: DesignEvent) -> DesignSession:
    if not isinstance(event, SessionStarted):
        raise ReplayIntegrityFailure("design replay must start with SessionStarted or a snapshot")
    return empty_session(event.session_id)


def _with_environment_hash(
    session: DesignSession,
    derivation_environment_hash: Sha256,
) -> DesignSession:
    from dataclasses import replace

    return replace(session, derivation_environment_hash=derivation_environment_hash)


def _assert_design_stream_owns_design_only_events(events: Iterable[DomainEvent]) -> None:
    for event in events:
        if event.event_type in DESIGN_STREAM_ONLY_EVENT_TYPES and not isinstance(
            event, DesignEvent
        ):
            raise ReplayIntegrityFailure(f"{event.event_type} must be in the design stream")


def _reviewer_decision_hashes(events: Iterable[GovernanceEvent]) -> frozenset[str]:
    hashes: set[str] = set()
    for event in events:
        if isinstance(event, ReviewerSignedOff):
            if not event.decision_record_payload:
                raise ReplayIntegrityFailure(
                    "ReviewerSignedOff must embed its signed decision payload"
                )
            hashes.add(event.decision_record_hash)
    return frozenset(hashes)


def _require_embedded_payload(
    event: RiskAdvisoryAcknowledged | RiskAdvisoryDeclined | RiskAdvisoryEscalated,
) -> None:
    payload = (
        event.acknowledgement_payload
        if isinstance(event, RiskAdvisoryAcknowledged)
        else event.decline_payload
        if isinstance(event, RiskAdvisoryDeclined)
        else event.escalation_payload
    )
    if not payload:
        raise ReplayIntegrityFailure(f"{event.event_type} must embed its signed payload")
