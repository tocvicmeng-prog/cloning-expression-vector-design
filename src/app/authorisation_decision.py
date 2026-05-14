"""
module_id: app.authorisation_decision
file: src/app/authorisation_decision.py
task_id: T-806b

Operational-protocol authorisation decision service.
"""

from __future__ import annotations

import json
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Protocol

from adapter.screening import ScreeningScope, ScreeningTrustPolicy, ScreeningVerdict
from app.advisory_acknowledgement import all_required_advisories_acknowledged
from app.review_queue_service import ReviewQueueService, ReviewQueueSubmissionResult
from domain.canonicalisation import canonical_sha256
from domain.events import (
    AuthorisationAttemptDenied,
    CanonicalPayload,
    DomainEvent,
    GovernanceEvent,
    OperationalProtocolAuthorised,
    ReviewerSignedOff,
    ScreeningCompleted,
)
from domain.ports.profile_signing import AuthorisationProfileVerifier
from domain.security import (
    AuthorisationProfile,
    CoveredBiologicalScope,
    ExportClass,
    OperationalRole,
    ServiceName,
    ServicePrincipal,
    SopLibraryId,
    UserDeclaration,
)
from domain.types import AssemblyMethodId, BiosafetyTier, ChassisClass, DownstreamUse
from domain.types.review_queue import CanonicalTextPayload
from domain.types.risk_advisory import RiskAdvisoryReport

MODULE_ID = "app.authorisation_decision"
OWNING_TASKS = ("T-806b",)

SCREENING_OPEN_VERDICTS = frozenset({ScreeningVerdict.CLEAR, ScreeningVerdict.NOT_APPLICABLE})
SCREENING_SIGNOFF_VERDICTS = frozenset(
    {
        ScreeningVerdict.WATCHLIST,
        ScreeningVerdict.MANUAL_REVIEW_REQUIRED,
        ScreeningVerdict.UNAVAILABLE,
    }
)
SCREENING_HARD_BLOCK_VERDICTS = frozenset({ScreeningVerdict.HIT})
APPROVED_SIGNOFF_STATUSES = frozenset({"approved", "cleared", "authorised", "authorized"})
BIOSAFETY_APPROVAL_CONSTRAINTS = frozenset(
    {"biosafety_approval_required", "requires_biosafety_approval"}
)
SOP_LIBRARY_CONSTRAINTS = frozenset({"sop_library_required", "requires_sop_library"})
INSTITUTIONAL_PROTOCOL_CONSTRAINTS = frozenset(
    {"institutional_protocol_id_required", "requires_institutional_protocol_id"}
)


class DesignEventLog(Protocol):
    def append_event(self, stream_id: str, event: DomainEvent) -> str: ...


class GovernanceEventLog(Protocol):
    def append_event(self, stream_id: str, event: DomainEvent) -> str: ...


class AuthorisationDecisionError(ValueError):
    """Raised when an authorisation decision request is structurally invalid."""


@dataclass(frozen=True)
class OperationalAuthorisationScope:
    biosafety_tier: BiosafetyTier
    host_class: ChassisClass
    assembly_chemistry: AssemblyMethodId
    downstream_use: DownstreamUse
    sop_library_id: SopLibraryId | None
    export_class: ExportClass
    vendor_submission: bool
    role_of_operation: OperationalRole
    cargo_classes: frozenset[str] = frozenset()
    vector_system_classes: frozenset[str] = frozenset()
    insert_size_bp: int | None = None
    institutional_protocol_id: str | None = None

    def __post_init__(self) -> None:
        if not str(self.assembly_chemistry):
            raise AuthorisationDecisionError("assembly_chemistry cannot be empty")
        if not str(self.export_class):
            raise AuthorisationDecisionError("export_class cannot be empty")
        if self.insert_size_bp is not None and self.insert_size_bp < 0:
            raise AuthorisationDecisionError("insert_size_bp cannot be negative")
        if self.institutional_protocol_id is not None and not self.institutional_protocol_id:
            raise AuthorisationDecisionError("institutional_protocol_id cannot be empty")


@dataclass(frozen=True)
class AuthorisationDecisionRequest:
    design_session_id: str
    event_id: str
    occurred_at_utc: datetime
    actor_id: str
    screening_event: ScreeningCompleted
    user_declaration: UserDeclaration
    authorisation_profile: AuthorisationProfile
    requested_scope: OperationalAuthorisationScope
    risk_advisory_report: RiskAdvisoryReport
    governance_events: tuple[GovernanceEvent, ...]
    screening_trust_policy: ScreeningTrustPolicy | None = None

    def __post_init__(self) -> None:
        if not self.design_session_id:
            raise AuthorisationDecisionError("design_session_id cannot be empty")
        if not self.event_id:
            raise AuthorisationDecisionError("event_id cannot be empty")
        if not self.actor_id:
            raise AuthorisationDecisionError("actor_id cannot be empty")
        if self.occurred_at_utc.tzinfo is None:
            raise AuthorisationDecisionError("occurred_at_utc must be timezone-aware")
        if self.screening_event.session_id != self.design_session_id:
            raise AuthorisationDecisionError("screening event does not belong to this session")
        if self.risk_advisory_report.design_session_id != self.design_session_id:
            raise AuthorisationDecisionError("risk advisory report does not belong to this session")


@dataclass(frozen=True)
class AuthorisationDecisionResult:
    allowed: bool
    blocked_by: tuple[str, ...]
    authorised_event: OperationalProtocolAuthorised | None = None
    denial_event: AuthorisationAttemptDenied | None = None
    review_queue_submission: ReviewQueueSubmissionResult | None = None


class AuthorisationDecisionService:
    def __init__(
        self,
        *,
        design_event_log: DesignEventLog,
        governance_event_log: GovernanceEventLog | None = None,
        profile_verifier: AuthorisationProfileVerifier | None = None,
        review_queue_service: ReviewQueueService | None = None,
        service_principal: ServicePrincipal | None = None,
    ) -> None:
        self._design_event_log = design_event_log
        self._governance_event_log = governance_event_log
        self._profile_verifier = profile_verifier
        self._review_queue_service = review_queue_service
        self._service_principal = service_principal or ServicePrincipal(
            service_name=ServiceName.AUTHORISATION_DECISION,
            token=b"authorisation-decision-phase-local",
        )
        if self._service_principal.service_name is not ServiceName.AUTHORISATION_DECISION:
            raise AuthorisationDecisionError(
                "AuthorisationDecisionService requires the authorisation service principal"
            )

    def decide(self, request: AuthorisationDecisionRequest) -> AuthorisationDecisionResult:
        reasons = _decision_block_reasons(request, self._profile_verifier)
        if reasons:
            return self._deny(request, reasons)
        event = _authorised_event(request)
        self._design_event_log.append_event(request.design_session_id, event)
        return AuthorisationDecisionResult(
            allowed=True,
            blocked_by=(),
            authorised_event=event,
        )

    def _deny(
        self,
        request: AuthorisationDecisionRequest,
        reasons: tuple[str, ...],
    ) -> AuthorisationDecisionResult:
        event = AuthorisationAttemptDenied(
            event_id=f"{request.event_id}:denied",
            occurred_at_utc=request.occurred_at_utc,
            actor_id=request.actor_id,
            institution_id=str(request.authorisation_profile.institution),
            subject_user_id=str(request.authorisation_profile.subject_user_id),
            missing_or_failed_reasons=reasons,
        )
        if self._governance_event_log is not None:
            self._governance_event_log.append_event(event.institution_id, event)
        submission: ReviewQueueSubmissionResult | None = None
        if self._review_queue_service is not None:
            submission = self._review_queue_service.route_blocked_authorisation(
                request.design_session_id,
                ",".join(reasons),
                self._service_principal,
                subject_user_id=request.authorisation_profile.subject_user_id,
                institution_id=request.authorisation_profile.institution,
                requested_scope=_requested_review_scope(request),
                supporting_evidence=_supporting_evidence(request, reasons),
            )
        return AuthorisationDecisionResult(
            allowed=False,
            blocked_by=reasons,
            denial_event=event,
            review_queue_submission=submission,
        )


def _decision_block_reasons(
    request: AuthorisationDecisionRequest,
    profile_verifier: AuthorisationProfileVerifier | None,
) -> tuple[str, ...]:
    reasons: list[str] = []
    reasons.extend(_profile_reasons(request, profile_verifier))
    reasons.extend(_scope_reasons(request))
    reasons.extend(_screening_reasons(request))
    advisories_acknowledged, missing = all_required_advisories_acknowledged(
        request.risk_advisory_report,
        request.governance_events,
    )
    if not advisories_acknowledged:
        reasons.extend(f"risk_advisory_acknowledgement_missing:{item}" for item in sorted(missing))
    return tuple(dict.fromkeys(reasons))


def _profile_reasons(
    request: AuthorisationDecisionRequest,
    profile_verifier: AuthorisationProfileVerifier | None,
) -> tuple[str, ...]:
    profile = request.authorisation_profile
    declaration = request.user_declaration
    reasons: list[str] = []
    if declaration.declared_by != profile.subject_user_id:
        reasons.append("user_declaration_subject_mismatch")
    if declaration.declared_at.astimezone(UTC) > request.occurred_at_utc.astimezone(UTC):
        reasons.append("user_declaration_after_decision_time")
    decision_time = request.occurred_at_utc.astimezone(UTC)
    if decision_time < profile.valid_from.astimezone(UTC):
        reasons.append("authorisation_profile_not_yet_valid")
    if decision_time >= profile.valid_until.astimezone(UTC):
        reasons.append("authorisation_profile_expired")
    if profile.revoked_at is not None and decision_time >= profile.revoked_at.astimezone(UTC):
        reasons.append("authorisation_profile_revoked")
    if profile_verifier is not None:
        verification = profile_verifier.verify(profile)
        if not verification.success:
            detail = (
                type(verification.error).__name__ if verification.error is not None else "error"
            )
            reasons.append(f"authorisation_profile_signature_invalid:{detail}")
    return tuple(reasons)


def _scope_reasons(request: AuthorisationDecisionRequest) -> tuple[str, ...]:
    scope = request.authorisation_profile.covered_scope
    declared = request.user_declaration
    requested = request.requested_scope
    reasons: list[str] = []
    if requested.biosafety_tier not in scope.covered_biosafety_tiers:
        reasons.append(f"scope_biosafety_tier_not_covered:{requested.biosafety_tier.value}")
    if requested.host_class not in scope.covered_host_classes:
        reasons.append(f"scope_host_class_not_covered:{requested.host_class.value}")
    if requested.assembly_chemistry not in scope.covered_assembly_chemistries:
        reasons.append(f"scope_assembly_chemistry_not_covered:{requested.assembly_chemistry}")
    if requested.downstream_use not in scope.covered_downstream_uses:
        reasons.append(f"scope_downstream_use_not_covered:{requested.downstream_use.value}")
    if requested.role_of_operation not in scope.role_of_operation_allowed:
        reasons.append(f"scope_role_not_covered:{requested.role_of_operation.value}")
    if declared.role_of_operation not in scope.role_of_operation_allowed:
        reasons.append(f"user_declaration_role_not_covered:{declared.role_of_operation.value}")
    if declared.role_of_operation is not requested.role_of_operation:
        reasons.append("user_declaration_role_mismatch")
    if declared.sop_library_id is not None and declared.sop_library_id not in (
        scope.covered_sop_libraries
    ):
        reasons.append(f"sop_library_not_covered:{declared.sop_library_id}")
    if requested.sop_library_id is not None and requested.sop_library_id not in (
        scope.covered_sop_libraries
    ):
        reasons.append(f"requested_sop_library_not_covered:{requested.sop_library_id}")
    if declared.intended_export_class not in scope.covered_export_classes:
        reasons.append(f"export_class_not_covered:{declared.intended_export_class}")
    if declared.intended_export_class != requested.export_class:
        reasons.append("user_declaration_export_class_mismatch")
    if declared.intended_vendor_submission != requested.vendor_submission:
        reasons.append("user_declaration_vendor_submission_mismatch")
    if declared.intended_vendor_submission and not scope.covered_vendor_submission:
        reasons.append("vendor_submission_not_covered")
    if scope.cargo_classes and not requested.cargo_classes.issubset(scope.cargo_classes):
        missing = ",".join(sorted(requested.cargo_classes - scope.cargo_classes))
        reasons.append(f"cargo_class_not_covered:{missing}")
    if scope.vector_system_classes and not requested.vector_system_classes.issubset(
        scope.vector_system_classes
    ):
        missing = ",".join(sorted(requested.vector_system_classes - scope.vector_system_classes))
        reasons.append(f"vector_system_class_not_covered:{missing}")
    if scope.insert_size_range_bp is not None and requested.insert_size_bp is not None:
        lower, upper = scope.insert_size_range_bp
        if not lower <= requested.insert_size_bp <= upper:
            reasons.append(f"insert_size_not_covered:{requested.insert_size_bp}")
    reasons.extend(_constraint_reasons(request))
    return tuple(reasons)


def _constraint_reasons(request: AuthorisationDecisionRequest) -> tuple[str, ...]:
    constraints = frozenset(request.authorisation_profile.additional_constraints)
    declared = request.user_declaration
    requested = request.requested_scope
    scope = request.authorisation_profile.covered_scope
    reasons: list[str] = []
    if constraints & BIOSAFETY_APPROVAL_CONSTRAINTS and declared.biosafety_approval_id is None:
        reasons.append("biosafety_approval_id_required")
    if constraints & SOP_LIBRARY_CONSTRAINTS and declared.sop_library_id is None:
        reasons.append("sop_library_id_required")
    if (
        constraints & INSTITUTIONAL_PROTOCOL_CONSTRAINTS
        and requested.institutional_protocol_id is None
    ):
        reasons.append("institutional_protocol_id_required")
    if (
        requested.institutional_protocol_id is not None
        and scope.institutional_protocol_ids
        and requested.institutional_protocol_id not in scope.institutional_protocol_ids
    ):
        reasons.append(
            f"institutional_protocol_id_not_covered:{requested.institutional_protocol_id}"
        )
    return tuple(reasons)


def _screening_reasons(request: AuthorisationDecisionRequest) -> tuple[str, ...]:
    verdict = _screening_verdict(request.screening_event.verdict_payload)
    reasons: list[str] = []
    if verdict is None:
        reasons.append("screening_verdict_missing_or_unsupported")
        return tuple(reasons)
    reasons.extend(_screening_trust_reasons(request, verdict))
    if verdict in SCREENING_OPEN_VERDICTS:
        return tuple(reasons)
    if verdict in SCREENING_HARD_BLOCK_VERDICTS:
        reasons.append(f"screening_verdict_blocks:{verdict.value}")
        return tuple(reasons)
    if verdict in SCREENING_SIGNOFF_VERDICTS and not _has_approved_reviewer_signoff(
        request.screening_event,
        request.governance_events,
    ):
        reasons.append(f"screening_reviewer_signoff_missing:{verdict.value}")
    return tuple(reasons)


def _screening_trust_reasons(
    request: AuthorisationDecisionRequest,
    aggregate_verdict: ScreeningVerdict,
) -> tuple[str, ...]:
    policy = request.screening_trust_policy
    if policy is None:
        return ()
    reasons: list[str] = []
    outcomes = _screening_outcomes(request.screening_event.verdict_payload)
    if not outcomes and aggregate_verdict is ScreeningVerdict.CLEAR:
        reasons.append("screening_provider_evidence_missing")
        return tuple(reasons)
    for outcome in outcomes:
        provider_id = str(outcome.get("provider_id") or "")
        verdict_text = str(outcome.get("verdict") or "")
        scope_text = str(outcome.get("scope") or ScreeningScope.ASSEMBLED_PRODUCT.value)
        if not provider_id:
            reasons.append("screening_provider_id_missing")
            continue
        try:
            outcome_verdict = ScreeningVerdict(verdict_text)
            outcome_scope = ScreeningScope(scope_text)
            provider = policy.provider_policy(provider_id, outcome_scope)
        except ValueError:
            reasons.append(f"screening_provider_not_trusted:{provider_id}:{verdict_text}")
            continue
        if outcome_verdict not in provider.accepted_verdicts:
            reasons.append(f"screening_provider_not_trusted:{provider_id}:{outcome_verdict.value}")
        if (
            aggregate_verdict in SCREENING_OPEN_VERDICTS
            and outcome_verdict is ScreeningVerdict.CLEAR
            and not bool(outcome.get("canonical_at_this_scope"))
        ):
            reasons.append(f"screening_provider_not_canonical:{provider_id}")
    return tuple(reasons)


def _screening_verdict(payload: CanonicalPayload) -> ScreeningVerdict | None:
    text = _payload_value(payload, "verdict")
    if text is None:
        return None
    try:
        return ScreeningVerdict(text.upper())
    except ValueError:
        return None


def _screening_outcomes(payload: CanonicalPayload) -> tuple[dict[str, object], ...]:
    outcomes_json = _payload_value(payload, "outcomes_json")
    if not outcomes_json:
        return ()
    try:
        raw = json.loads(outcomes_json)
    except json.JSONDecodeError:
        return ()
    if not isinstance(raw, list):
        return ()
    return tuple(item for item in raw if isinstance(item, dict))


def _has_approved_reviewer_signoff(
    screening_event: ScreeningCompleted,
    events: Iterable[GovernanceEvent],
) -> bool:
    verdict = _screening_verdict(screening_event.verdict_payload)
    for event in events:
        if not isinstance(event, ReviewerSignedOff):
            continue
        payload = dict(event.decision_record_payload)
        if payload.get("screening_batch_id") != screening_event.batch_id:
            continue
        if payload.get("signature_valid") != "true":
            continue
        if verdict is not None and payload.get("verdict") != verdict.value:
            continue
        if payload.get("decision_status", "").lower() in APPROVED_SIGNOFF_STATUSES:
            return True
    return False


def _authorised_event(request: AuthorisationDecisionRequest) -> OperationalProtocolAuthorised:
    return OperationalProtocolAuthorised(
        event_id=request.event_id,
        occurred_at_utc=request.occurred_at_utc,
        actor_id=request.actor_id,
        session_id=request.design_session_id,
        profile_id=str(request.authorisation_profile.profile_id),
        decision_record_hash=str(_decision_record_hash(request)),
    )


def _decision_record_hash(request: AuthorisationDecisionRequest) -> object:
    acknowledged_event_ids = tuple(
        sorted(
            event.event_id
            for event in request.governance_events
            if event.event_type == "RiskAdvisoryAcknowledged"
        )
    )
    return canonical_sha256(
        {
            "advisory_acknowledgement_event_ids": acknowledged_event_ids,
            "actor_id": request.actor_id,
            "declared_by": str(request.user_declaration.declared_by),
            "decision_at_utc": request.occurred_at_utc,
            "profile_content_hash": str(request.authorisation_profile.profile_content_hash),
            "profile_id": str(request.authorisation_profile.profile_id),
            "requested_scope": _scope_payload(request.requested_scope),
            "risk_advisory_report_hash": str(request.risk_advisory_report.report_content_hash),
            "screening_batch_id": request.screening_event.batch_id,
            "screening_verdict": _payload_value(request.screening_event.verdict_payload, "verdict")
            or "",
            "session_id": request.design_session_id,
        }
    )


def _requested_review_scope(request: AuthorisationDecisionRequest) -> CoveredBiologicalScope:
    requested = request.requested_scope
    return CoveredBiologicalScope(
        covered_biosafety_tiers=frozenset({requested.biosafety_tier}),
        covered_host_classes=frozenset({requested.host_class}),
        covered_assembly_chemistries=frozenset({requested.assembly_chemistry}),
        covered_downstream_uses=frozenset({requested.downstream_use}),
        covered_sop_libraries=frozenset({item for item in (requested.sop_library_id,) if item}),
        covered_vendor_submission=requested.vendor_submission,
        covered_export_classes=frozenset({requested.export_class}),
        role_of_operation_allowed=frozenset({requested.role_of_operation}),
        cargo_classes=requested.cargo_classes,
        vector_system_classes=requested.vector_system_classes,
        insert_size_range_bp=None
        if requested.insert_size_bp is None
        else (requested.insert_size_bp, requested.insert_size_bp),
        institutional_protocol_ids=frozenset(
            {item for item in (requested.institutional_protocol_id,) if item}
        ),
    )


def _supporting_evidence(
    request: AuthorisationDecisionRequest,
    reasons: tuple[str, ...],
) -> CanonicalTextPayload:
    return (
        ("blocked_by", ",".join(reasons)),
        ("profile_id", str(request.authorisation_profile.profile_id)),
        ("profile_content_hash", str(request.authorisation_profile.profile_content_hash)),
        ("risk_advisory_report_hash", str(request.risk_advisory_report.report_content_hash)),
        ("screening_batch_id", request.screening_event.batch_id),
        (
            "screening_verdict",
            _payload_value(request.screening_event.verdict_payload, "verdict") or "",
        ),
    )


def _scope_payload(scope: OperationalAuthorisationScope) -> dict[str, object]:
    return {
        "assembly_chemistry": str(scope.assembly_chemistry),
        "biosafety_tier": scope.biosafety_tier.value,
        "cargo_classes": sorted(scope.cargo_classes),
        "downstream_use": scope.downstream_use.value,
        "export_class": str(scope.export_class),
        "host_class": scope.host_class.value,
        "insert_size_bp": scope.insert_size_bp,
        "institutional_protocol_id": scope.institutional_protocol_id,
        "role_of_operation": scope.role_of_operation.value,
        "sop_library_id": "" if scope.sop_library_id is None else str(scope.sop_library_id),
        "vector_system_classes": sorted(scope.vector_system_classes),
        "vendor_submission": scope.vendor_submission,
    }


def _payload_value(payload: CanonicalPayload, key: str) -> str | None:
    for payload_key, value in payload:
        if payload_key == key:
            return value
    return None


__all__ = [
    "AuthorisationDecisionError",
    "AuthorisationDecisionRequest",
    "AuthorisationDecisionResult",
    "AuthorisationDecisionService",
    "OperationalAuthorisationScope",
]
