"""
module_id: app.screening_orchestrator
file: src/app/screening_orchestrator.py
task_id: T-1002

Screening adapter orchestration and screening event emission.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from adapter.screening import (
    BatchScreeningOutcome,
    ScreeningError,
    ScreeningRequest,
    ScreeningResult,
)
from domain.types.screening import ScreeningVerdict
from domain.canonicalisation import canonical_json, canonical_sha256
from domain.events import DomainEvent, ReviewerSignedOff, ScreeningCompleted
from domain.ports.audit_append import AuditAppendPort, AuditEntry, AuditEntryId
from domain.ports.decision_record_signing import DecisionRecordVerifier, SignedDecisionRecord
from domain.security import ServiceName, ServicePrincipal

MODULE_ID = "app.screening_orchestrator"
OWNING_TASKS = ("T-1002",)

REVIEW_SIGNOFF_VERDICTS = frozenset(
    {
        ScreeningVerdict.WATCHLIST,
        ScreeningVerdict.MANUAL_REVIEW_REQUIRED,
        ScreeningVerdict.UNAVAILABLE,
    }
)
BLOCKING_VERDICT_ORDER = (
    ScreeningVerdict.HIT,
    ScreeningVerdict.WATCHLIST,
    ScreeningVerdict.MANUAL_REVIEW_REQUIRED,
    ScreeningVerdict.UNAVAILABLE,
)


class DesignEventLog(Protocol):
    def append_event(self, stream_id: str, event: DomainEvent) -> str: ...


class GovernanceEventLog(Protocol):
    def append_event(self, stream_id: str, event: DomainEvent) -> str: ...


class ScreeningAdapterLike(Protocol):
    provider_id: str

    def screen(self, request: ScreeningRequest) -> ScreeningResult | ScreeningError: ...

    def screen_batch(self, requests: Iterable[ScreeningRequest]) -> BatchScreeningOutcome: ...


class ScreeningOrchestrationError(ValueError):
    """Raised when a screening orchestration request is internally inconsistent."""


class ScreeningSignoffRejected(PermissionError):
    """Raised when a screening sign-off decision record fails policy checks."""


@dataclass(frozen=True)
class ScreeningRunRequest:
    batch_id: str
    requests: tuple[ScreeningRequest, ...]
    event_id: str
    occurred_at_utc: datetime
    actor_id: str = MODULE_ID

    def __post_init__(self) -> None:
        if not self.batch_id:
            raise ScreeningOrchestrationError("batch_id cannot be empty")
        if not self.requests:
            raise ScreeningOrchestrationError("screening batch requires at least one request")
        if not self.event_id:
            raise ScreeningOrchestrationError("event_id cannot be empty")
        if not self.actor_id:
            raise ScreeningOrchestrationError("actor_id cannot be empty")
        if self.occurred_at_utc.tzinfo is None:
            raise ScreeningOrchestrationError("occurred_at_utc must be timezone-aware")
        session_ids = {request.session_id for request in self.requests}
        if len(session_ids) != 1:
            raise ScreeningOrchestrationError("screening batch must belong to one session")

    @property
    def session_id(self) -> str:
        return self.requests[0].session_id


@dataclass(frozen=True)
class ScreeningRunResult:
    event: ScreeningCompleted
    outcomes: BatchScreeningOutcome
    aggregate_verdict: ScreeningVerdict
    audit_entry_id: AuditEntryId | None = None


@dataclass(frozen=True)
class ScreeningSignoffRequest:
    signed_decision_record: SignedDecisionRecord
    screening_batch_id: str
    verdict: ScreeningVerdict
    decision_status: str
    institution_id: str
    event_id: str
    occurred_at_utc: datetime
    actor_id: str | None = None

    def __post_init__(self) -> None:
        if not self.screening_batch_id:
            raise ScreeningSignoffRejected("screening_batch_id cannot be empty")
        if not self.decision_status:
            raise ScreeningSignoffRejected("decision_status cannot be empty")
        if not self.institution_id:
            raise ScreeningSignoffRejected("institution_id cannot be empty")
        if not self.event_id:
            raise ScreeningSignoffRejected("event_id cannot be empty")
        if self.occurred_at_utc.tzinfo is None:
            raise ScreeningSignoffRejected("occurred_at_utc must be timezone-aware")

    @property
    def resolved_actor_id(self) -> str:
        return self.actor_id or str(self.signed_decision_record.signing_principal_id)


class ScreeningOrchestrator:
    def __init__(
        self,
        adapter: ScreeningAdapterLike,
        *,
        design_event_log: DesignEventLog,
        governance_event_log: GovernanceEventLog | None = None,
        audit_append_port: AuditAppendPort | None = None,
        audit_caller: ServicePrincipal | None = None,
        decision_record_verifier: DecisionRecordVerifier | None = None,
    ) -> None:
        self._adapter = adapter
        self._design_event_log = design_event_log
        self._governance_event_log = governance_event_log
        self._audit_append_port = audit_append_port
        self._audit_caller = audit_caller or ServicePrincipal(
            service_name=ServiceName.SCREENING_ORCHESTRATOR,
            token=b"screening-orchestrator-phase-local",
        )
        self._decision_record_verifier = decision_record_verifier

    def screen_batch(self, request: ScreeningRunRequest) -> ScreeningRunResult:
        outcomes = self._adapter.screen_batch(request.requests)
        if len(outcomes) != len(request.requests):
            raise ScreeningOrchestrationError("adapter returned a different batch length")
        verdict = aggregate_screening_verdict(outcomes)
        event = ScreeningCompleted(
            event_id=request.event_id,
            occurred_at_utc=request.occurred_at_utc,
            actor_id=request.actor_id,
            session_id=request.session_id,
            batch_id=request.batch_id,
            verdict_payload=_verdict_payload(
                batch_id=request.batch_id,
                verdict=verdict,
                outcomes=outcomes,
            ),
        )
        self._design_event_log.append_event(request.session_id, event)
        audit_entry_id = self._append_audit_entry(request, outcomes, verdict)
        return ScreeningRunResult(
            event=event,
            outcomes=outcomes,
            aggregate_verdict=verdict,
            audit_entry_id=audit_entry_id,
        )

    def screen(self, request: ScreeningRunRequest) -> ScreeningRunResult:
        if len(request.requests) != 1:
            raise ScreeningOrchestrationError("screen() accepts exactly one request")
        return self.screen_batch(request)

    def record_reviewer_signoff(self, request: ScreeningSignoffRequest) -> ReviewerSignedOff:
        if request.verdict not in REVIEW_SIGNOFF_VERDICTS:
            raise ScreeningSignoffRejected(
                f"{request.verdict.value} does not support reviewer sign-off"
            )
        if self._decision_record_verifier is not None:
            verification = self._decision_record_verifier.verify(request.signed_decision_record)
            if not verification.success:
                reason = "decision record verification failed"
                if verification.error is not None:
                    reason = str(verification.error)
                raise ScreeningSignoffRejected(reason)

        payload = _signoff_payload(request)
        event = ReviewerSignedOff(
            event_id=request.event_id,
            occurred_at_utc=request.occurred_at_utc,
            actor_id=request.resolved_actor_id,
            institution_id=request.institution_id,
            decision_record_payload=payload,
            decision_record_hash=str(canonical_sha256(request.signed_decision_record)),
        )
        if self._governance_event_log is not None:
            self._governance_event_log.append_event(request.institution_id, event)
        return event

    def _append_audit_entry(
        self,
        request: ScreeningRunRequest,
        outcomes: BatchScreeningOutcome,
        verdict: ScreeningVerdict,
    ) -> AuditEntryId | None:
        if self._audit_append_port is None:
            return None
        entry = AuditEntry(
            entry_type="screening.completed",
            payload={
                "aggregate_verdict": verdict.value,
                "batch_id": request.batch_id,
                "outcomes_json": _outcomes_json(outcomes),
                "provider_id": self._adapter.provider_id,
                "session_id": request.session_id,
            },
            occurred_at_utc=request.occurred_at_utc,
        )
        return self._audit_append_port.append(entry, self._audit_caller)


def aggregate_screening_verdict(outcomes: BatchScreeningOutcome) -> ScreeningVerdict:
    if any(isinstance(outcome, ScreeningError) for outcome in outcomes):
        return ScreeningVerdict.UNAVAILABLE
    result_verdicts = tuple(
        outcome.verdict for outcome in outcomes if isinstance(outcome, ScreeningResult)
    )
    for verdict in BLOCKING_VERDICT_ORDER:
        if verdict in result_verdicts:
            return verdict
    if result_verdicts and all(
        verdict is ScreeningVerdict.NOT_APPLICABLE for verdict in result_verdicts
    ):
        return ScreeningVerdict.NOT_APPLICABLE
    if result_verdicts:
        return ScreeningVerdict.CLEAR
    return ScreeningVerdict.UNAVAILABLE


def _verdict_payload(
    *,
    batch_id: str,
    verdict: ScreeningVerdict,
    outcomes: BatchScreeningOutcome,
) -> tuple[tuple[str, str], ...]:
    payload = {
        "batch_id": batch_id,
        "canonical_provider_count": str(
            sum(
                1
                for outcome in outcomes
                if isinstance(outcome, ScreeningResult) and outcome.canonical_at_this_scope
            )
        ),
        "error_count": str(sum(1 for outcome in outcomes if isinstance(outcome, ScreeningError))),
        "outcomes_json": _outcomes_json(outcomes),
        "provider_ids": ",".join(sorted(_provider_ids(outcomes))),
        "realisation_count": str(len(outcomes)),
        "verdict": verdict.value,
    }
    return tuple(sorted(payload.items()))


def _provider_ids(outcomes: BatchScreeningOutcome) -> frozenset[str]:
    return frozenset(outcome.provider_id for outcome in outcomes)


def _outcomes_json(outcomes: BatchScreeningOutcome) -> str:
    return canonical_json([outcome.to_payload() for outcome in outcomes]).decode("utf-8")


def _signoff_payload(request: ScreeningSignoffRequest) -> tuple[tuple[str, str], ...]:
    signed = request.signed_decision_record
    payload = {
        "decision_record_id": signed.decision.decision_id,
        "decision_status": request.decision_status,
        "decision_type": signed.decision.decision_type,
        "screening_batch_id": request.screening_batch_id,
        "signature_valid": "true",
        "signed_decision_record_json": canonical_json(signed).decode("utf-8"),
        "signed_payload_hash": str(signed.signed_payload_hash),
        "signing_key_version": str(signed.signing_key_version),
        "signing_principal_id": str(signed.signing_principal_id),
        "verdict": request.verdict.value,
    }
    return tuple(sorted(payload.items()))
