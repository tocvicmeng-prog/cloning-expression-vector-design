"""
module_id: tests.app.test_authorisation_decision_t806b
file: tests/app/test_authorisation_decision_t806b.py
task_id: T-806b
"""

from __future__ import annotations

from dataclasses import replace
from datetime import UTC, date, datetime
from pathlib import Path

import pytest

from app.advisory_acknowledgement import (
    AdvisoryAcknowledgementService,
    AdvisoryActionRequest,
    AdvisoryPresentationRequest,
)
from app.authorisation_decision import (
    AuthorisationDecisionRequest,
    AuthorisationDecisionService,
    OperationalAuthorisationScope,
)
from domain.events import (
    DomainEvent,
    GovernanceEvent,
    OperationalProtocolAuthorised,
    RiskAdvisoryAcknowledged,
)
from domain.events.design import ScreeningCompleted
from domain.security import (
    AdminPrincipal,
    AuthorisationProfile,
    BiosafetyApprovalId,
    ExportClass,
    InstitutionId,
    KeyVersionId,
    OperationalRole,
    PrincipalId,
    ProfileSignature,
    SecurityRole,
    SopLibraryId,
    UserDeclaration,
    UserId,
)
from domain.sequence import sha256_text
from domain.types import AssemblyMethodId, BiosafetyTier, ChassisClass, DownstreamUse
from domain.types.citation import GradedCitation
from domain.types.governance import DecisionRecord, RoleSnapshot
from domain.types.review_queue import ReviewQueueStatus
from domain.types.risk_advisory import RiskAdvisory, RiskAdvisoryReport, RiskAdvisorySeverity
from domain.types.signing_errors import ProfileTamperDetectedError, ProfileVerificationResult
from tests.app.review_queue.helpers import review_queue_stack
from tests.fakes.security.profile_signing.fixtures import unsigned_profile, unsigned_profile_draft

NOW = datetime(2026, 5, 14, 13, 0, tzinfo=UTC)
SESSION_ID = "session-806b"


def test_authorisation_decision_emits_operational_authorisation_after_ack_chain() -> None:
    design_log = MemoryDesignEventLog()
    governance_log = MemoryGovernanceEventLog()
    report = _report()
    advisory_events = _acknowledged_advisory_events(report)
    service = AuthorisationDecisionService(
        design_event_log=design_log,
        governance_event_log=governance_log,
        profile_verifier=AcceptingProfileVerifier(),
    )

    result = service.decide(
        _request(
            screening_event=_screening_completed("CLEAR"),
            report=report,
            governance_events=advisory_events,
        )
    )

    assert result.allowed
    assert result.blocked_by == ()
    assert isinstance(result.authorised_event, OperationalProtocolAuthorised)
    assert result.authorised_event.decision_record_hash
    assert design_log.events[SESSION_ID] == [result.authorised_event]
    assert governance_log.events == {}


def test_authorisation_decision_blocks_passive_presentation_and_routes_review_queue(
    tmp_path: Path,
) -> None:
    design_log = MemoryDesignEventLog()
    governance_log = MemoryGovernanceEventLog()
    review_queue, _store, _queue_log, _audit = review_queue_stack(tmp_path)
    report = _report()
    presentation = AdvisoryAcknowledgementService().present(_presentation_request(report, _admin()))
    service = AuthorisationDecisionService(
        design_event_log=design_log,
        governance_event_log=governance_log,
        review_queue_service=review_queue,
    )

    result = service.decide(
        _request(
            screening_event=_screening_completed("CLEAR"),
            report=report,
            governance_events=(presentation,),
        )
    )

    assert not result.allowed
    assert result.authorised_event is None
    assert result.denial_event is not None
    assert "risk_advisory_acknowledgement_missing:risk.caution" in result.blocked_by
    assert governance_log.events["inst"][0].event_type == "AuthorisationAttemptDenied"
    assert result.review_queue_submission is not None
    assert result.review_queue_submission.created
    assert result.review_queue_submission.item.status is ReviewQueueStatus.PENDING
    assert result.review_queue_submission.item.request.request_kind.value == "blocked_authorisation"
    assert design_log.events == {}


def test_authorisation_decision_blocks_screening_hit_without_authorising() -> None:
    design_log = MemoryDesignEventLog()
    report = _report()
    service = AuthorisationDecisionService(design_event_log=design_log)

    result = service.decide(
        _request(
            screening_event=_screening_completed("HIT"),
            report=report,
            governance_events=_acknowledged_advisory_events(report),
        )
    )

    assert not result.allowed
    assert "screening_verdict_blocks:HIT" in result.blocked_by
    assert result.authorised_event is None
    assert design_log.events == {}


@pytest.mark.parametrize(
    "case_name",
    (
        "short_justification",
        "unsigned_acknowledgement",
        "report_hash_mismatch",
        "declined_advisory",
        "escalated_advisory",
        "construct_checksum_mismatch",
        "programmatic_authorisation_without_governance_chain",
    ),
)
def test_authorisation_decision_blocks_advisory_bypass_variants(case_name: str) -> None:
    design_log = MemoryDesignEventLog()
    report = _report()
    service = AuthorisationDecisionService(design_event_log=design_log)

    result = service.decide(
        _request(
            screening_event=_screening_completed("CLEAR"),
            report=report,
            governance_events=_advisory_bypass_events(report, case_name),
        )
    )

    assert not result.allowed
    assert "risk_advisory_acknowledgement_missing:risk.caution" in result.blocked_by
    assert result.authorised_event is None
    assert design_log.events == {}


def test_authorisation_decision_blocks_tampered_profile_signature() -> None:
    design_log = MemoryDesignEventLog()
    report = _report()
    service = AuthorisationDecisionService(
        design_event_log=design_log,
        profile_verifier=RejectingProfileVerifier(),
    )

    result = service.decide(
        _request(
            screening_event=_screening_completed("CLEAR"),
            report=report,
            governance_events=_acknowledged_advisory_events(report),
        )
    )

    assert not result.allowed
    assert "authorisation_profile_signature_invalid:ProfileTamperDetectedError" in result.blocked_by
    assert result.authorised_event is None
    assert design_log.events == {}


def test_authorisation_decision_enforces_profile_scope_and_required_approval() -> None:
    design_log = MemoryDesignEventLog()
    report = _report()
    constrained_profile = _profile_with_constraints(("biosafety_approval_required",))
    declaration = _declaration(include_default_biosafety_approval=False)
    request = _request(
        profile=constrained_profile,
        declaration=declaration,
        requested_scope=replace(_requested_scope(), biosafety_tier=BiosafetyTier.BSL_3),
        screening_event=_screening_completed("CLEAR"),
        report=report,
        governance_events=_acknowledged_advisory_events(report),
    )

    result = AuthorisationDecisionService(design_event_log=design_log).decide(request)

    assert not result.allowed
    assert "scope_biosafety_tier_not_covered:BSL-3" in result.blocked_by
    assert "biosafety_approval_id_required" in result.blocked_by
    assert result.authorised_event is None
    assert design_log.events == {}


class MemoryDesignEventLog:
    def __init__(self) -> None:
        self.events: dict[str, list[DomainEvent]] = {}

    def append_event(self, stream_id: str, event: DomainEvent) -> str:
        self.events.setdefault(stream_id, []).append(event)
        return event.event_id


class MemoryGovernanceEventLog:
    def __init__(self) -> None:
        self.events: dict[str, list[GovernanceEvent]] = {}

    def append_event(self, stream_id: str, event: DomainEvent) -> str:
        assert isinstance(event, GovernanceEvent)
        self.events.setdefault(stream_id, []).append(event)
        return event.event_id


class AcceptingProfileVerifier:
    def verify(self, profile: AuthorisationProfile) -> ProfileVerificationResult:
        return ProfileVerificationResult.ok(None)


class RejectingProfileVerifier:
    def verify(self, profile: AuthorisationProfile) -> ProfileVerificationResult:
        return ProfileVerificationResult.fail(ProfileTamperDetectedError("tampered profile"))


def _request(
    *,
    screening_event: ScreeningCompleted,
    report: RiskAdvisoryReport,
    governance_events: tuple[GovernanceEvent, ...],
    profile: AuthorisationProfile | None = None,
    declaration: UserDeclaration | None = None,
    requested_scope: OperationalAuthorisationScope | None = None,
) -> AuthorisationDecisionRequest:
    return AuthorisationDecisionRequest(
        design_session_id=SESSION_ID,
        event_id="authorise-1",
        occurred_at_utc=NOW,
        actor_id="app.authorisation_decision",
        screening_event=screening_event,
        user_declaration=declaration or _declaration(),
        authorisation_profile=profile or unsigned_profile(),
        requested_scope=requested_scope or _requested_scope(),
        risk_advisory_report=report,
        governance_events=governance_events,
    )


def _screening_completed(verdict: str) -> ScreeningCompleted:
    return ScreeningCompleted(
        event_id=f"screening-{verdict.lower()}",
        occurred_at_utc=NOW,
        actor_id="app.screening_orchestrator",
        session_id=SESSION_ID,
        batch_id=f"batch-{verdict.lower()}",
        verdict_payload=(
            ("batch_id", f"batch-{verdict.lower()}"),
            ("provider_ids", "igsc"),
            ("verdict", verdict),
        ),
    )


def _declaration(
    *,
    biosafety_approval_id: BiosafetyApprovalId | None = None,
    include_default_biosafety_approval: bool = True,
) -> UserDeclaration:
    resolved_approval = biosafety_approval_id
    if resolved_approval is None and include_default_biosafety_approval:
        resolved_approval = BiosafetyApprovalId("IBC-2026-001")
    return UserDeclaration(
        declared_at=NOW,
        declared_by=UserId("user-1"),
        sop_library_id=SopLibraryId("institutional-sop"),
        biosafety_approval_id=resolved_approval,
        role_of_operation=OperationalRole.DESIGNER,
        intended_export_class=ExportClass("internal-review"),
        intended_vendor_submission=False,
    )


def _requested_scope() -> OperationalAuthorisationScope:
    return OperationalAuthorisationScope(
        biosafety_tier=BiosafetyTier.BSL_1,
        host_class=ChassisClass.BACTERIAL,
        assembly_chemistry=AssemblyMethodId("golden-gate"),
        downstream_use=DownstreamUse.EXPRESSION,
        sop_library_id=SopLibraryId("institutional-sop"),
        export_class=ExportClass("internal-review"),
        vendor_submission=False,
        role_of_operation=OperationalRole.DESIGNER,
    )


def _acknowledged_advisory_events(report: RiskAdvisoryReport) -> tuple[GovernanceEvent, ...]:
    event_log = MemoryGovernanceEventLog()
    service = AdvisoryAcknowledgementService(event_log)
    presentation = service.present(_presentation_request(report, _admin()))
    service.acknowledge(
        AdvisoryActionRequest(
            report=report,
            advisory_id="risk.caution",
            actor=_admin(),
            presentation_event=presentation,
            justification="Reviewed by administrator with institutional context.",
            decision_record=_decision_record("ack-1"),
            occurred_at_utc=NOW,
            event_id="ack-1",
        )
    )
    return tuple(event_log.events["inst"])


def _advisory_bypass_events(
    report: RiskAdvisoryReport,
    case_name: str,
) -> tuple[GovernanceEvent, ...]:
    if case_name == "programmatic_authorisation_without_governance_chain":
        return ()
    if case_name == "report_hash_mismatch":
        return _acknowledged_advisory_events(_report(seed="other-report"))
    if case_name == "declined_advisory":
        return _advisory_action_events(report, decision="decline")
    if case_name == "escalated_advisory":
        return _advisory_action_events(report, decision="escalate")
    acknowledged = _acknowledged_advisory_events(report)
    if case_name == "short_justification":
        return _replace_acknowledgement_payload(acknowledged, justification="short")
    if case_name == "unsigned_acknowledgement":
        return _replace_acknowledgement_payload(acknowledged, signature_valid="false")
    if case_name == "construct_checksum_mismatch":
        return _replace_acknowledgement_payload(
            acknowledged,
            construct_checksum=str(sha256_text("changed-construct")),
        )
    raise AssertionError(f"unknown bypass case: {case_name}")


def _advisory_action_events(
    report: RiskAdvisoryReport,
    *,
    decision: str,
) -> tuple[GovernanceEvent, ...]:
    event_log = MemoryGovernanceEventLog()
    service = AdvisoryAcknowledgementService(event_log)
    presentation = service.present(_presentation_request(report, _admin()))
    request = AdvisoryActionRequest(
        report=report,
        advisory_id="risk.caution",
        actor=_admin(),
        presentation_event=presentation,
        justification="Route this construct through the institutional review path.",
        decision_record=_decision_record(decision),
        occurred_at_utc=NOW,
        event_id=f"{decision}-1",
        institutional_approval_id="IBC-2026-001" if decision == "escalate" else None,
    )
    if decision == "decline":
        service.decline(request)
    elif decision == "escalate":
        service.escalate(request)
    else:
        raise AssertionError(f"unknown advisory decision: {decision}")
    return tuple(event_log.events["inst"])


def _replace_acknowledgement_payload(
    events: tuple[GovernanceEvent, ...],
    **updates: str,
) -> tuple[GovernanceEvent, ...]:
    replaced: list[GovernanceEvent] = []
    for event in events:
        if isinstance(event, RiskAdvisoryAcknowledged):
            payload = dict(event.acknowledgement_payload)
            payload.update(updates)
            replaced.append(replace(event, acknowledgement_payload=tuple(sorted(payload.items()))))
            continue
        replaced.append(event)
    return tuple(replaced)


def _presentation_request(
    report: RiskAdvisoryReport,
    recipient: AdminPrincipal,
) -> AdvisoryPresentationRequest:
    return AdvisoryPresentationRequest(
        report=report,
        recipient=recipient,
        presenting_surface="cli==0.3.2",
        occurred_at_utc=NOW,
        event_id=f"present-{recipient.role.value}",
    )


def _report(seed: str = "construct") -> RiskAdvisoryReport:
    citation = GradedCitation(
        text="Institutional biosafety guidance",
        grade="A1",
        accessed=date(2026, 5, 14),
        url="https://example.org/biosafety",
    )
    return RiskAdvisoryReport(
        design_session_id=SESSION_ID,
        construct_id="construct-806b",
        construct_checksum=sha256_text(seed),
        construct_version="1",
        report_content_hash=sha256_text(f"report:{seed}"),
        advisory_catalogue_version="risk-v1",
        advisory_catalogue_content_hash=sha256_text("catalogue"),
        advisories=(
            RiskAdvisory(
                advisory_id="risk.info",
                severity=RiskAdvisorySeverity.INFO,
                category="info",
                message="Informational advisory",
                citation=citation,
            ),
            RiskAdvisory(
                advisory_id="risk.caution",
                severity=RiskAdvisorySeverity.CAUTION,
                category="biosafety",
                message="Caution advisory",
                citation=citation,
            ),
        ),
    )


def _decision_record(seed: str) -> DecisionRecord:
    snapshot = RoleSnapshot(
        principal_id=PrincipalId("admin-1"),
        role=SecurityRole.ADMINISTRATOR,
        institution_id="inst",
        captured_at_utc=NOW,
        credentials_verified_at_utc=NOW,
    )
    return DecisionRecord(
        decision_id=f"decision-{seed}",
        decision_type="risk_advisory_acknowledgement",
        role_snapshot=snapshot,
        profile_content_hash=sha256_text("profile"),
        policy_version="policy-v1",
        signed_payload_hash=sha256_text(f"payload:{seed}"),
        signature_bytes=b"signature",
        signed_at_utc=NOW,
    )


def _admin() -> AdminPrincipal:
    return AdminPrincipal(
        id=PrincipalId("admin-1"),
        role=SecurityRole.ADMINISTRATOR,
        institution=InstitutionId("inst"),
        credentials_verified_at=NOW,
    )


def _profile_with_constraints(constraints: tuple[str, ...]) -> AuthorisationProfile:
    draft = replace(unsigned_profile_draft(), additional_constraints=constraints)
    signature = ProfileSignature(
        signed_payload_hash=draft.content_hash(),
        signature_bytes=b"placeholder-signature",
        signing_key_version=KeyVersionId("profile-test-key-v1"),
        signed_at_utc=NOW,
    )
    return AuthorisationProfile.from_draft(draft, signature)
