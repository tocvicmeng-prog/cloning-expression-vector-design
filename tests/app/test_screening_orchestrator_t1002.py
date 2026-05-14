"""
module_id: tests.app.test_screening_orchestrator_t1002
file: tests/app/test_screening_orchestrator_t1002.py
task_id: T-1002
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import UTC, datetime

import pytest

from adapter.screening import (
    BatchScreeningOutcome,
    ScreeningAdapterFailureClass,
    ScreeningError,
    ScreeningRequest,
    ScreeningResult,
    ScreeningScope,
    ScreeningVerdict,
    load_screening_trust_policy,
)
from app.screening_orchestrator import (
    ScreeningOrchestrationError,
    ScreeningOrchestrator,
    ScreeningRunRequest,
    ScreeningSignoffRejected,
    ScreeningSignoffRequest,
    aggregate_screening_verdict,
)
from domain.events import DomainEvent, EventStream, ReviewerSignedOff, ScreeningCompleted
from domain.ports.audit_append import AuditEntry, AuditEntryId
from domain.ports.decision_record_signing import SignedDecisionRecord
from domain.security import ServicePrincipal
from domain.sequence import DnaSequence
from domain.types.signing_errors import (
    DecisionRecordTamperDetectedError,
    DecisionRecordVerificationResult,
    Result,
)
from tests.fakes.security.profile_signing.fixtures import decision_record, reviewer_principal
from tests.fakes.security.profile_signing.signers import FakeDecisionRecordSigner

NOW = datetime(2026, 5, 14, 12, tzinfo=UTC)


@dataclass
class InMemoryEventLog:
    events: dict[str, list[DomainEvent]] = field(default_factory=dict)

    def append_event(self, stream_id: str, event: DomainEvent) -> str:
        self.events.setdefault(stream_id, []).append(event)
        return event.event_id


@dataclass
class FakeAuditAppendPort:
    entries: list[tuple[AuditEntry, str]] = field(default_factory=list)

    def append(self, entry: AuditEntry, caller: ServicePrincipal) -> AuditEntryId:
        self.entries.append((entry, caller.service_name.value))
        return AuditEntryId(f"audit-{len(self.entries):06d}")


class FakeScreeningAdapter:
    provider_id = "fake_provider"

    def __init__(self, outcomes: BatchScreeningOutcome) -> None:
        self._outcomes = outcomes

    def screen(self, request: ScreeningRequest) -> ScreeningResult | ScreeningError:
        del request
        return self._outcomes[0]

    def screen_batch(self, requests: Iterable[ScreeningRequest]) -> BatchScreeningOutcome:
        del requests
        return self._outcomes


class RejectingDecisionVerifier:
    def verify(self, signed: SignedDecisionRecord) -> DecisionRecordVerificationResult:
        del signed
        return Result.fail(DecisionRecordTamperDetectedError("tampered decision"))


def test_screen_batch_emits_design_event_and_audit_entry() -> None:
    result = _result("req-1", ScreeningVerdict.WATCHLIST)
    design_log = InMemoryEventLog()
    audit = FakeAuditAppendPort()
    service = ScreeningOrchestrator(
        FakeScreeningAdapter((result,)),
        design_event_log=design_log,
        audit_append_port=audit,
    )

    run = service.screen_batch(_run_request((_request("req-1"),)))

    assert run.aggregate_verdict is ScreeningVerdict.WATCHLIST
    assert isinstance(run.event, ScreeningCompleted)
    assert run.event.stream is EventStream.DESIGN
    assert design_log.events["session-1"] == [run.event]
    assert dict(run.event.verdict_payload)["verdict"] == "WATCHLIST"
    assert run.audit_entry_id == "audit-000001"
    assert audit.entries[0][0].entry_type == "screening.completed"
    assert audit.entries[0][1] == "ScreeningOrchestrator"


def test_orchestrator_never_aggregates_partial_errors_to_clear() -> None:
    clear = _result("clear", ScreeningVerdict.CLEAR)
    error = ScreeningError(
        provider_id="fake_provider",
        request_id="error",
        session_id="session-1",
        failure_class=ScreeningAdapterFailureClass.PROVIDER_UNAVAILABLE,
        message="provider down",
        retryable=True,
    )

    assert aggregate_screening_verdict((clear, error)) is ScreeningVerdict.UNAVAILABLE


def test_adapter_batch_length_mismatch_is_rejected() -> None:
    service = ScreeningOrchestrator(
        FakeScreeningAdapter((_result("only", ScreeningVerdict.CLEAR),)),
        design_event_log=InMemoryEventLog(),
    )

    with pytest.raises(ScreeningOrchestrationError, match="different batch length"):
        service.screen_batch(_run_request((_request("first"), _request("second"))))


def test_reviewer_signoff_emits_governance_event_with_signed_payload() -> None:
    governance_log = InMemoryEventLog()
    signed = FakeDecisionRecordSigner().sign(decision_record(), reviewer_principal())
    service = ScreeningOrchestrator(
        FakeScreeningAdapter((_result("req-1", ScreeningVerdict.WATCHLIST),)),
        design_event_log=InMemoryEventLog(),
        governance_event_log=governance_log,
    )

    event = service.record_reviewer_signoff(
        ScreeningSignoffRequest(
            signed_decision_record=signed,
            screening_batch_id="batch-1",
            verdict=ScreeningVerdict.WATCHLIST,
            decision_status="approved_for_reviewed_continuation",
            institution_id="inst",
            event_id="signoff-1",
            occurred_at_utc=NOW,
        )
    )

    assert isinstance(event, ReviewerSignedOff)
    assert event.stream is EventStream.GOVERNANCE
    assert governance_log.events["inst"] == [event]
    payload = dict(event.decision_record_payload)
    assert payload["signature_valid"] == "true"
    assert "signed_decision_record_json" in payload
    assert payload["verdict"] == "WATCHLIST"


def test_reviewer_signoff_rejects_clear_or_invalid_decisions() -> None:
    signed = FakeDecisionRecordSigner().sign(decision_record(), reviewer_principal())
    service = ScreeningOrchestrator(
        FakeScreeningAdapter((_result("req-1", ScreeningVerdict.CLEAR),)),
        design_event_log=InMemoryEventLog(),
        decision_record_verifier=RejectingDecisionVerifier(),
    )

    with pytest.raises(ScreeningSignoffRejected, match="does not support"):
        service.record_reviewer_signoff(_signoff_request(signed, verdict=ScreeningVerdict.CLEAR))

    with pytest.raises(ScreeningSignoffRejected, match="tampered decision"):
        service.record_reviewer_signoff(
            _signoff_request(signed, verdict=ScreeningVerdict.WATCHLIST)
        )


def _run_request(requests: tuple[ScreeningRequest, ...]) -> ScreeningRunRequest:
    return ScreeningRunRequest(
        batch_id="batch-1",
        requests=requests,
        event_id="screening-event-1",
        occurred_at_utc=NOW,
    )


def _request(request_id: str) -> ScreeningRequest:
    return ScreeningRequest(
        request_id=request_id,
        sequence=DnaSequence("G" * 210),
        session_id="session-1",
        construct_id="construct-1",
        construct_checksum="checksum-1",
        scope=ScreeningScope.ASSEMBLED_PRODUCT,
    )


def _result(request_id: str, verdict: ScreeningVerdict) -> ScreeningResult:
    policy = load_screening_trust_policy("catalogues", schema_root="schemas")
    provider_policy = policy.provider_policy("igsc_v3", ScreeningScope.ASSEMBLED_PRODUCT)
    request = _request(request_id)
    return ScreeningResult(
        provider_id="igsc_v3",
        request_id=request.request_id,
        session_id=request.session_id,
        construct_id=request.construct_id,
        construct_checksum=request.construct_checksum,
        sequence_hash=request.sequence_hash,
        verdict=verdict,
        provider_version="test",
        policy_id=policy.policy_id,
        policy_version=policy.policy_version,
        policy_content_hash=policy.policy_content_hash,
        canonical_at_this_scope=provider_policy.canonical_at_this_scope,
        scope=request.scope,
    )


def _signoff_request(
    signed: SignedDecisionRecord,
    *,
    verdict: ScreeningVerdict,
) -> ScreeningSignoffRequest:
    return ScreeningSignoffRequest(
        signed_decision_record=signed,
        screening_batch_id="batch-1",
        verdict=verdict,
        decision_status="approved",
        institution_id="inst",
        event_id=f"signoff-{verdict.value}",
        occurred_at_utc=NOW,
    )
