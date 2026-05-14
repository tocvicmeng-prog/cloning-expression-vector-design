"""
module_id: app.design_service
file: src/app/design_service.py
task_id: T-606

Top-level design-session application use cases.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum
from typing import Protocol, TypedDict

from domain.events import (
    CanonicalPayload,
    DesignCompiled,
    DesignEvent,
    DomainEvent,
    FreeTextEntered,
    GovernanceEvent,
    HostSelected,
    LLMTranslationConfirmed,
    LLMTranslationProposed,
    OverrideJustified,
    PartAdded,
    RuleAcknowledged,
    SessionId,
    SessionStarted,
)
from domain.security import Principal
from domain.sequence import Sha256, sha256_text
from engine.session import (
    BLOCK_COMPILE,
    BLOCK_EXPORT,
    BLOCK_OPERATIONAL_PROTOCOL,
    BLOCK_VENDOR_SUBMISSION,
    DesignSession,
    GatePredicateRegistry,
    GateState,
    GateVerdict,
    ReplayIntegrityFailure,
    SessionSnapshot,
    SessionState,
    empty_session,
    replay_design_events,
)

MODULE_ID = "app.design_service"
OWNING_TASKS = ("T-606",)

DEFAULT_DERIVATION_ENVIRONMENT_HASH = sha256_text("app.design_service:T-606:phase-local")


class DesignEventLog(Protocol):
    def append_event(self, stream_id: str, event: DomainEvent) -> str: ...

    def read_events(self, stream_id: str) -> tuple[DomainEvent, ...]: ...


class ProjectSessionStore(Protocol):
    def save_session(self, session: DesignSession) -> str: ...


class SessionSnapshotStore(Protocol):
    def save(self, snapshot: SessionSnapshot) -> None: ...

    def latest_matching(
        self,
        session_id: SessionId,
        derivation_environment_hash: Sha256,
    ) -> SessionSnapshot | None: ...


class SessionAlreadyExistsError(ValueError):
    """Raised when create is called for a session with an existing design stream."""


class SessionNotFoundError(KeyError):
    """Raised when a session use case cannot find a design stream."""


class DesignGateBlockedError(PermissionError):
    """Raised when an activated safety gate blocks a design-service use case."""


class PendingState(Enum):
    AWAITING_SCREENING = "AwaitingScreening"
    AWAITING_AUTHORISATION = "AwaitingAuthorisation"
    AWAITING_SOP_RENDER = "AwaitingSopRender"
    AWAITING_EXPORT = "AwaitingExport"


@dataclass(frozen=True)
class PendingStep:
    state: PendingState
    session_state: SessionState
    gate_verdict: GateVerdict
    downstream_owner: str


@dataclass(frozen=True)
class DesignOperationResult:
    session: DesignSession
    event_id: str
    event: DesignEvent


@dataclass(frozen=True)
class AddPart:
    part_id: str
    part_payload_hash: str


@dataclass(frozen=True)
class SelectHost:
    host_id: str
    host_role: str


@dataclass(frozen=True)
class EnterFreeText:
    text: str


@dataclass(frozen=True)
class ProposeTranslation:
    structured: CanonicalPayload


@dataclass(frozen=True)
class ConfirmTranslation:
    structured: CanonicalPayload


@dataclass(frozen=True)
class AcknowledgeRule:
    rule_id: str
    justification: str


@dataclass(frozen=True)
class JustifyOverride:
    override_id: str
    justification: str


DesignAmendment = (
    AddPart
    | SelectHost
    | EnterFreeText
    | ProposeTranslation
    | ConfirmTranslation
    | AcknowledgeRule
    | JustifyOverride
)


PENDING_STATE_GATES = {
    PendingState.AWAITING_SCREENING: BLOCK_VENDOR_SUBMISSION,
    PendingState.AWAITING_AUTHORISATION: BLOCK_OPERATIONAL_PROTOCOL,
    PendingState.AWAITING_SOP_RENDER: BLOCK_OPERATIONAL_PROTOCOL,
    PendingState.AWAITING_EXPORT: BLOCK_EXPORT,
}

PENDING_STATE_OWNERS = {
    PendingState.AWAITING_SCREENING: "app.screening_orchestrator",
    PendingState.AWAITING_AUTHORISATION: "app.authorisation_decision",
    PendingState.AWAITING_SOP_RENDER: "app.sop_protocol_orchestrator",
    PendingState.AWAITING_EXPORT: "app.export_orchestrator",
}


class _DesignEventBase(TypedDict):
    event_id: str
    occurred_at_utc: datetime
    actor_id: str
    session_id: SessionId


class DesignService:
    def __init__(
        self,
        *,
        design_event_log: DesignEventLog,
        project_store: ProjectSessionStore | None = None,
        snapshot_store: SessionSnapshotStore | None = None,
        gate_registry: GatePredicateRegistry | None = None,
        derivation_environment_hash: Sha256 = DEFAULT_DERIVATION_ENVIRONMENT_HASH,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._design_event_log = design_event_log
        self._project_store = project_store
        self._snapshot_store = snapshot_store
        self._gate_registry = gate_registry or GatePredicateRegistry.with_pending_defaults()
        self._derivation_environment_hash = derivation_environment_hash
        self._clock = clock or (lambda: datetime.now(UTC))
        self._event_sequence = 0

    def create_session(
        self,
        principal: Principal,
        session_id: SessionId,
        *,
        project_name: str,
    ) -> DesignOperationResult:
        _require_non_empty(session_id, "session_id")
        _require_non_empty(project_name, "project_name")
        if self._read_design_events(session_id):
            raise SessionAlreadyExistsError(session_id)

        event = SessionStarted(
            **self._event_base(principal, session_id, "SessionStarted"),
            project_name=project_name,
        )
        session = empty_session(session_id).apply(event)
        return self._persist_result(session_id, session, event)

    def open_session(
        self,
        principal: Principal,
        session_id: SessionId,
        *,
        governance_events: Iterable[GovernanceEvent] = (),
    ) -> DesignSession:
        del principal
        return self.replay_session(session_id, governance_events=governance_events)

    def amend_session(
        self,
        principal: Principal,
        session_id: SessionId,
        amendment: DesignAmendment,
        *,
        governance_events: Iterable[GovernanceEvent] = (),
    ) -> DesignOperationResult:
        session = self.replay_session(session_id, governance_events=governance_events)
        event = self._event_from_amendment(principal, session_id, amendment)
        updated = session.apply(event)
        return self._persist_result(session_id, updated, event)

    def compile_session(
        self,
        principal: Principal,
        session_id: SessionId,
        *,
        construct_id: str,
        construct_checksum: str,
        design_plan_hash: str,
        governance_events: Iterable[GovernanceEvent] = (),
    ) -> DesignOperationResult:
        _require_non_empty(construct_id, "construct_id")
        _require_non_empty(construct_checksum, "construct_checksum")
        _require_non_empty(design_plan_hash, "design_plan_hash")

        session = self.replay_session(session_id, governance_events=governance_events)
        verdict = self._gate_registry.verdict(BLOCK_COMPILE, session, allow_pending=True)
        if verdict.state is GateState.BLOCKED:
            raise DesignGateBlockedError(verdict.reason)

        event = DesignCompiled(
            **self._event_base(principal, session_id, "DesignCompiled"),
            construct_id=construct_id,
            construct_checksum=construct_checksum,
            design_plan_hash=design_plan_hash,
        )
        updated = session.apply(event)
        return self._persist_result(session_id, updated, event)

    def replay_session(
        self,
        session_id: SessionId,
        *,
        governance_events: Iterable[GovernanceEvent] = (),
    ) -> DesignSession:
        _require_non_empty(session_id, "session_id")
        events = self._read_design_events(session_id)
        if not events:
            raise SessionNotFoundError(session_id)

        snapshot = None
        if self._snapshot_store is not None:
            snapshot = self._snapshot_store.latest_matching(
                session_id,
                self._derivation_environment_hash,
            )
        if snapshot is not None and snapshot.event_sequence <= len(events):
            events_to_replay = events[snapshot.event_sequence :]
            session = replay_design_events(
                events_to_replay,
                governance_events=governance_events,
                initial_snapshot=snapshot.session,
                derivation_environment_hash=self._derivation_environment_hash,
            )
        else:
            session = replay_design_events(
                events,
                governance_events=governance_events,
                derivation_environment_hash=self._derivation_environment_hash,
            )
        self._save_session(session)
        return session

    def current_pending_state(
        self,
        session_id: SessionId,
        *,
        governance_events: Iterable[GovernanceEvent] = (),
    ) -> PendingStep | None:
        session = self.replay_session(session_id, governance_events=governance_events)
        session_state = session.state
        pending_state = _pending_state_for_session_state(session_state)
        if pending_state is None:
            return None
        gate = PENDING_STATE_GATES[pending_state]
        verdict = self._gate_registry.verdict(gate, session, allow_pending=True)
        return PendingStep(
            state=pending_state,
            session_state=session_state,
            gate_verdict=verdict,
            downstream_owner=PENDING_STATE_OWNERS[pending_state],
        )

    def add_part(
        self,
        principal: Principal,
        session_id: SessionId,
        *,
        part_id: str,
        part_payload_hash: str,
    ) -> DesignOperationResult:
        return self.amend_session(
            principal,
            session_id,
            AddPart(part_id=part_id, part_payload_hash=part_payload_hash),
        )

    def select_host(
        self,
        principal: Principal,
        session_id: SessionId,
        *,
        host_id: str,
        host_role: str,
    ) -> DesignOperationResult:
        return self.amend_session(
            principal,
            session_id,
            SelectHost(host_id=host_id, host_role=host_role),
        )

    def enter_free_text(
        self,
        principal: Principal,
        session_id: SessionId,
        *,
        text: str,
    ) -> DesignOperationResult:
        return self.amend_session(principal, session_id, EnterFreeText(text=text))

    def confirm_translation(
        self,
        principal: Principal,
        session_id: SessionId,
        *,
        structured: Mapping[str, str] | CanonicalPayload,
    ) -> DesignOperationResult:
        return self.amend_session(
            principal,
            session_id,
            ConfirmTranslation(structured=_canonical_payload(structured)),
        )

    def _persist_result(
        self,
        session_id: SessionId,
        session: DesignSession,
        event: DesignEvent,
    ) -> DesignOperationResult:
        event_id = self._design_event_log.append_event(session_id, event)
        self._save_session(session)
        return DesignOperationResult(session=session, event_id=event_id, event=event)

    def _save_session(self, session: DesignSession) -> None:
        if self._project_store is not None:
            self._project_store.save_session(session)
        if self._snapshot_store is not None:
            self._snapshot_store.save(
                SessionSnapshot(
                    session_id=session.session_id,
                    event_sequence=len(session.applied_event_ids),
                    derivation_environment_hash=self._derivation_environment_hash,
                    session=session,
                )
            )

    def _read_design_events(self, session_id: SessionId) -> tuple[DesignEvent, ...]:
        raw_events = self._design_event_log.read_events(session_id)
        events: list[DesignEvent] = []
        for event in raw_events:
            if not isinstance(event, DesignEvent):
                raise ReplayIntegrityFailure(f"{event.event_type} is not a design event")
            if event.session_id != session_id:
                raise ReplayIntegrityFailure("design event stream contains a mismatched session_id")
            events.append(event)
        return tuple(events)

    def _event_from_amendment(
        self,
        principal: Principal,
        session_id: SessionId,
        amendment: DesignAmendment,
    ) -> DesignEvent:
        if isinstance(amendment, AddPart):
            _require_non_empty(amendment.part_id, "part_id")
            _require_non_empty(amendment.part_payload_hash, "part_payload_hash")
            return PartAdded(
                **self._event_base(principal, session_id, "PartAdded"),
                part_id=amendment.part_id,
                part_payload_hash=amendment.part_payload_hash,
            )
        if isinstance(amendment, SelectHost):
            _require_non_empty(amendment.host_id, "host_id")
            _require_non_empty(amendment.host_role, "host_role")
            return HostSelected(
                **self._event_base(principal, session_id, "HostSelected"),
                host_id=amendment.host_id,
                host_role=amendment.host_role,
            )
        if isinstance(amendment, EnterFreeText):
            _require_non_empty(amendment.text, "text")
            return FreeTextEntered(
                **self._event_base(principal, session_id, "FreeTextEntered"),
                text=amendment.text,
            )
        if isinstance(amendment, ProposeTranslation):
            return LLMTranslationProposed(
                **self._event_base(principal, session_id, "LLMTranslationProposed"),
                structured=amendment.structured,
            )
        if isinstance(amendment, ConfirmTranslation):
            return LLMTranslationConfirmed(
                **self._event_base(principal, session_id, "LLMTranslationConfirmed"),
                structured=amendment.structured,
            )
        if isinstance(amendment, AcknowledgeRule):
            _require_non_empty(amendment.rule_id, "rule_id")
            _require_non_empty(amendment.justification, "justification")
            return RuleAcknowledged(
                **self._event_base(principal, session_id, "RuleAcknowledged"),
                rule_id=amendment.rule_id,
                justification=amendment.justification,
            )
        _require_non_empty(amendment.override_id, "override_id")
        _require_non_empty(amendment.justification, "justification")
        return OverrideJustified(
            **self._event_base(principal, session_id, "OverrideJustified"),
            override_id=amendment.override_id,
            justification=amendment.justification,
        )

    def _event_base(
        self,
        principal: Principal,
        session_id: SessionId,
        event_type: str,
    ) -> _DesignEventBase:
        self._event_sequence += 1
        return {
            "event_id": f"design-service:{session_id}:{self._event_sequence:06d}:{event_type}",
            "occurred_at_utc": self._clock(),
            "actor_id": str(principal.id),
            "session_id": session_id,
        }


def _pending_state_for_session_state(session_state: SessionState) -> PendingState | None:
    if session_state is SessionState.AWAITING_SCREENING:
        return PendingState.AWAITING_SCREENING
    if session_state in {
        SessionState.AWAITING_AUTHORISATION,
        SessionState.AWAITING_REVIEWER_SIGNOFF,
    }:
        return PendingState.AWAITING_AUTHORISATION
    if session_state is SessionState.AWAITING_SOP_RENDER:
        return PendingState.AWAITING_SOP_RENDER
    if session_state is SessionState.READY_TO_EXPORT:
        return PendingState.AWAITING_EXPORT
    return None


def _canonical_payload(payload: Mapping[str, str] | CanonicalPayload) -> CanonicalPayload:
    if isinstance(payload, Mapping):
        return tuple((str(key), str(value)) for key, value in sorted(payload.items()))
    return tuple(payload)


def _require_non_empty(value: str, field_name: str) -> None:
    if not value:
        raise ValueError(f"{field_name} cannot be empty")


__all__ = [
    "DEFAULT_DERIVATION_ENVIRONMENT_HASH",
    "PENDING_STATE_GATES",
    "PENDING_STATE_OWNERS",
    "AcknowledgeRule",
    "AddPart",
    "ConfirmTranslation",
    "DesignAmendment",
    "DesignEventLog",
    "DesignGateBlockedError",
    "DesignOperationResult",
    "DesignService",
    "EnterFreeText",
    "JustifyOverride",
    "PendingState",
    "PendingStep",
    "ProjectSessionStore",
    "ProposeTranslation",
    "SelectHost",
    "SessionAlreadyExistsError",
    "SessionNotFoundError",
    "SessionSnapshotStore",
]
