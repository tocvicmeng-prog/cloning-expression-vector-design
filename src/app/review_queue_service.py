"""
module_id: app.review_queue_service
file: src/app/review_queue_service.py
task_id: T-315

User/service review-queue submission and admin-side resolution helpers.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime

from adapter.persistence import JsonlEventLog
from adapter.persistence.sqlite_review_queue_store import ReviewQueueItemNotFoundError
from domain.canonicalisation import canonical_sha256
from domain.events import (
    AuthorisationAttemptDenied,
    AuthorisationExtensionRequested,
    CanonicalPayload,
    ReviewQueueItemAssigned,
    ReviewQueueItemCreated,
    ReviewQueueItemResolved,
)
from domain.ports.audit_append import AdminAuditAppendPort, AuditAppendPort, AuditEntry
from domain.ports.decision_record_signing import DecisionRecordSigner, SignedDecisionRecord
from domain.ports.review_queue_admin import ReviewQueueAdminPort, ReviewQueueStore
from domain.security import (
    AdminPrincipal,
    CoveredBiologicalScope,
    InstitutionId,
    Principal,
    PrincipalId,
    SecurityRole,
    ServiceName,
    ServicePrincipal,
    UserId,
    UserPrincipal,
)
from domain.types.governance import DecisionRecord, RoleSnapshot
from domain.types.review_queue import (
    AuthorisationRequest,
    AuthorisationRequestId,
    CanonicalTextPayload,
    ReviewQueueDecisionId,
    ReviewQueueItem,
    ReviewQueueItemDecision,
    ReviewQueueItemId,
    ReviewQueueRequestKind,
    ReviewQueueStatus,
)


@dataclass(frozen=True)
class ReviewQueueSubmissionResult:
    item: ReviewQueueItem
    audit_entry_id: str | None
    governance_event_ids: tuple[str, ...]
    created: bool


@dataclass(frozen=True)
class ReviewQueueResolutionResult:
    item: ReviewQueueItem
    audit_entry_id: str
    governance_event_id: str


class ReviewQueueService:
    """User/service submission use cases; intentionally no admin resolution method."""

    def __init__(
        self,
        *,
        review_queue_store: ReviewQueueStore,
        audit_append: AuditAppendPort,
        governance_event_log: JsonlEventLog,
        service_principal: ServicePrincipal,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        if service_principal.service_name is not ServiceName.REVIEW_QUEUE:
            raise ValueError("ReviewQueueService must use the review-queue service principal")
        self._store = review_queue_store
        self._audit_append = audit_append
        self._governance_event_log = governance_event_log
        self._service_principal = service_principal
        self._clock = clock or (lambda: datetime.now(UTC))
        self._event_sequence = 0

    def submit_extension_request(
        self,
        user: UserPrincipal,
        requested_scope: CoveredBiologicalScope,
        justification: str,
        *,
        supporting_evidence: CanonicalTextPayload = (),
    ) -> ReviewQueueSubmissionResult:
        now = self._clock()
        request = AuthorisationRequest(
            request_id=_request_id(
                "user-extension",
                str(user.id),
                str(canonical_sha256(requested_scope.to_payload())),
                justification,
                _datetime_to_json(now),
            ),
            request_kind=ReviewQueueRequestKind.USER_EXTENSION,
            subject_user_id=UserId(str(user.id)),
            institution_id=user.institution,
            requested_scope=requested_scope,
            justification=justification,
            created_at_utc=now,
            supporting_evidence=supporting_evidence,
        )
        return self._add_request(
            request,
            audit_entry_type="AuthorisationExtensionRequested",
            event_types=("AuthorisationExtensionRequested", "ReviewQueueItemCreated"),
            audit_caller=self._service_principal,
        )

    def route_blocked_authorisation(
        self,
        session_id: str,
        reason: str,
        caller: ServicePrincipal,
        *,
        subject_user_id: UserId,
        institution_id: InstitutionId,
        requested_scope: CoveredBiologicalScope,
        supporting_evidence: CanonicalTextPayload = (),
    ) -> ReviewQueueSubmissionResult:
        if not session_id:
            raise ValueError("session_id cannot be empty")
        now = self._clock()
        request = AuthorisationRequest(
            request_id=_request_id(
                "blocked-authorisation",
                session_id,
                str(subject_user_id),
                str(canonical_sha256(requested_scope.to_payload())),
                reason,
            ),
            request_kind=ReviewQueueRequestKind.BLOCKED_AUTHORISATION,
            subject_user_id=subject_user_id,
            institution_id=institution_id,
            requested_scope=requested_scope,
            justification=f"Operational protocol withheld pending administrator approval: {reason}",
            created_at_utc=now,
            related_session_id=session_id,
            supporting_evidence=supporting_evidence,
            block_reason=reason,
        )
        return self._add_request(
            request,
            audit_entry_type="ReviewQueueItemCreated",
            event_types=("ReviewQueueItemCreated",),
            audit_caller=caller,
        )

    def _add_request(
        self,
        request: AuthorisationRequest,
        *,
        audit_entry_type: str,
        event_types: tuple[str, ...],
        audit_caller: ServicePrincipal,
    ) -> ReviewQueueSubmissionResult:
        created = not _store_has_item(self._store, str(request.item_id))
        self._store.add(request)
        item = self._store.get(str(request.item_id))
        if not created:
            return ReviewQueueSubmissionResult(
                item=item,
                audit_entry_id=None,
                governance_event_ids=(),
                created=False,
            )
        occurred_at = self._clock()
        audit_entry_id = self._audit_append.append(
            AuditEntry(
                entry_type=audit_entry_type,
                payload={
                    "item_id": str(item.item_id),
                    "request_content_hash": str(request.content_hash()),
                    "request_id": str(request.request_id),
                    "request_kind": request.request_kind.value,
                    "subject_user_id": str(request.subject_user_id),
                },
                occurred_at_utc=occurred_at,
            ),
            audit_caller,
        )
        event_ids = tuple(
            self._append_submission_event(event_type, request, occurred_at)
            for event_type in event_types
        )
        return ReviewQueueSubmissionResult(
            item=item,
            audit_entry_id=str(audit_entry_id),
            governance_event_ids=event_ids,
            created=True,
        )

    def _append_submission_event(
        self,
        event_type: str,
        request: AuthorisationRequest,
        occurred_at: datetime,
    ) -> str:
        if event_type == "AuthorisationExtensionRequested":
            return self._governance_event_log.append_event(
                str(request.institution_id),
                AuthorisationExtensionRequested(
                    event_id=self._next_event_id(event_type),
                    occurred_at_utc=occurred_at,
                    actor_id=str(request.subject_user_id),
                    institution_id=str(request.institution_id),
                    item_id=str(request.item_id),
                    request_payload=_request_payload(request),
                    request_content_hash=str(request.content_hash()),
                ),
            )
        return self._governance_event_log.append_event(
            str(request.institution_id),
            ReviewQueueItemCreated(
                event_id=self._next_event_id(event_type),
                occurred_at_utc=occurred_at,
                actor_id=str(request.subject_user_id),
                institution_id=str(request.institution_id),
                item_id=str(request.item_id),
                request_kind=request.request_kind.value,
                request_payload=_request_payload(request),
                request_content_hash=str(request.content_hash()),
            ),
        )

    def _next_event_id(self, prefix: str) -> str:
        self._event_sequence += 1
        return f"{prefix}-{self._event_sequence:06d}"


class ReviewQueueAdminResolutionService:
    """Admin-service composition helper for ReviewQueueAdminPort."""

    def __init__(
        self,
        *,
        review_queue_store: ReviewQueueStore,
        review_queue_admin_port: ReviewQueueAdminPort,
        decision_record_signer: DecisionRecordSigner,
        audit_append: AdminAuditAppendPort,
        governance_event_log: JsonlEventLog,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._store = review_queue_store
        self._admin_port = review_queue_admin_port
        self._decision_record_signer = decision_record_signer
        self._audit_append = audit_append
        self._governance_event_log = governance_event_log
        self._clock = clock or (lambda: datetime.now(UTC))
        self._event_sequence = 0

    def resolve_item(
        self,
        admin: Principal,
        item_id: str,
        decision_status: ReviewQueueStatus,
        *,
        justification: str,
        assigned_admin_id: PrincipalId | None = None,
    ) -> ReviewQueueResolutionResult:
        acting_admin = self._require_admin(admin, "resolve_review_queue_item")
        item = self._store.get(item_id)
        signed = self._signed_decision_record(
            admin=acting_admin,
            item=item,
            decision_status=decision_status,
            justification=justification,
        )
        decision = ReviewQueueItemDecision(
            decision_id=ReviewQueueDecisionId(signed.decision.decision_id),
            item_id=ReviewQueueItemId(item_id),
            decision_status=decision_status,
            decided_by_admin_id=acting_admin.id,
            justification=justification,
            decided_at_utc=self._clock(),
            decision_record_payload=_signed_decision_payload(signed),
            decision_record_hash=canonical_sha256(signed),
            assigned_admin_id=assigned_admin_id,
        )
        self._admin_port.resolve(item_id, decision, acting_admin)
        resolved = self._store.get(item_id)
        audit_entry_id = self._audit_append.append(
            AuditEntry(
                entry_type=_resolution_event_type(decision_status),
                payload={
                    "decision_id": str(decision.decision_id),
                    "decision_status": decision_status.value,
                    "item_id": item_id,
                    "request_content_hash": str(item.request.content_hash()),
                    "subject_user_id": str(item.request.subject_user_id),
                },
                occurred_at_utc=decision.decided_at_utc,
            ),
            acting_admin,
        )
        event_id = self._append_resolution_event(acting_admin, resolved, decision)
        return ReviewQueueResolutionResult(
            item=resolved,
            audit_entry_id=str(audit_entry_id),
            governance_event_id=event_id,
        )

    def _signed_decision_record(
        self,
        *,
        admin: AdminPrincipal,
        item: ReviewQueueItem,
        decision_status: ReviewQueueStatus,
        justification: str,
    ) -> SignedDecisionRecord:
        decided_at = self._clock()
        decision_payload = {
            "decision_status": decision_status.value,
            "item_id": str(item.item_id),
            "justification": justification,
            "request_content_hash": str(item.request.content_hash()),
            "subject_user_id": str(item.request.subject_user_id),
        }
        decision = DecisionRecord(
            decision_id=_decision_id(str(item.item_id), decision_status.value, decided_at),
            decision_type="review_queue_item_resolution",
            role_snapshot=RoleSnapshot(
                principal_id=admin.id,
                role=admin.role,
                institution_id=str(admin.institution),
                captured_at_utc=decided_at,
                credentials_verified_at_utc=admin.credentials_verified_at,
            ),
            profile_content_hash=item.request.content_hash(),
            policy_version="review-queue-v1",
            signed_payload_hash=canonical_sha256(decision_payload),
            signature_bytes=b"pending-review-queue-decision-signature",
            signed_at_utc=decided_at,
        )
        return self._decision_record_signer.sign(decision, admin)

    def _append_resolution_event(
        self,
        admin: AdminPrincipal,
        item: ReviewQueueItem,
        decision: ReviewQueueItemDecision,
    ) -> str:
        payload = _decision_payload(decision)
        if decision.decision_status is ReviewQueueStatus.UNDER_REVIEW:
            return self._governance_event_log.append_event(
                str(admin.institution),
                ReviewQueueItemAssigned(
                    event_id=self._next_event_id(_resolution_event_type(decision.decision_status)),
                    occurred_at_utc=decision.decided_at_utc,
                    actor_id=str(admin.id),
                    institution_id=str(admin.institution),
                    item_id=str(item.item_id),
                    assigned_admin_id=str(decision.assigned_admin_id),
                    decision_payload=payload,
                    decision_record_hash=str(decision.decision_record_hash),
                ),
            )
        return self._governance_event_log.append_event(
            str(admin.institution),
            ReviewQueueItemResolved(
                event_id=self._next_event_id(_resolution_event_type(decision.decision_status)),
                occurred_at_utc=decision.decided_at_utc,
                actor_id=str(admin.id),
                institution_id=str(admin.institution),
                item_id=str(item.item_id),
                decision_status=decision.decision_status.value,
                decision_payload=payload,
                decision_record_hash=str(decision.decision_record_hash),
            ),
        )

    def _require_admin(self, principal: Principal, operation: str) -> AdminPrincipal:
        if isinstance(principal, AdminPrincipal) and principal.can_act_as(
            SecurityRole.ADMINISTRATOR
        ):
            return principal
        event = AuthorisationAttemptDenied(
            event_id=self._next_event_id("AuthorisationAttemptDenied"),
            occurred_at_utc=self._clock(),
            actor_id=str(principal.id),
            institution_id=str(principal.institution),
            subject_user_id=str(principal.id),
            missing_or_failed_reasons=(f"{operation}:administrator-required",),
        )
        self._governance_event_log.append_event(str(principal.institution), event)
        raise PermissionError("review queue resolution requires administrator")

    def _next_event_id(self, prefix: str) -> str:
        self._event_sequence += 1
        return f"{prefix}-{self._event_sequence:06d}"


def _store_has_item(store: ReviewQueueStore, item_id: str) -> bool:
    try:
        store.get(item_id)
    except (KeyError, ReviewQueueItemNotFoundError):
        return False
    return True


def _request_id(prefix: str, *parts: str) -> AuthorisationRequestId:
    digest = canonical_sha256({"parts": list(parts), "prefix": prefix})
    return AuthorisationRequestId(f"{prefix}-{digest}")


def _decision_id(item_id: str, status: str, decided_at: datetime) -> str:
    digest = canonical_sha256(
        {
            "decided_at": _datetime_to_json(decided_at),
            "item_id": item_id,
            "status": status,
        }
    )
    return f"review-decision-{digest}"


def _request_payload(request: AuthorisationRequest) -> CanonicalPayload:
    return (
        ("request_id", str(request.request_id)),
        ("request_kind", request.request_kind.value),
        ("subject_user_id", str(request.subject_user_id)),
        ("institution_id", str(request.institution_id)),
        ("related_session_id", request.related_session_id or ""),
        ("block_reason", request.block_reason or ""),
        ("justification", request.justification),
        ("requested_scope_json", _json_text(request.requested_scope.to_payload())),
        ("supporting_evidence_json", _json_text(dict(request.supporting_evidence))),
    )


def _decision_payload(decision: ReviewQueueItemDecision) -> CanonicalPayload:
    return (
        ("decision_id", str(decision.decision_id)),
        ("item_id", str(decision.item_id)),
        ("decision_status", decision.decision_status.value),
        ("decided_by_admin_id", str(decision.decided_by_admin_id)),
        (
            "assigned_admin_id",
            "" if decision.assigned_admin_id is None else str(decision.assigned_admin_id),
        ),
        ("justification", decision.justification),
        ("decision_record_hash", str(decision.decision_record_hash)),
        ("decision_record_payload_json", _json_text(dict(decision.decision_record_payload))),
    )


def _signed_decision_payload(signed: SignedDecisionRecord) -> CanonicalPayload:
    decision = signed.decision
    snapshot = decision.role_snapshot
    return (
        ("decision_id", decision.decision_id),
        ("decision_type", decision.decision_type),
        ("policy_version", decision.policy_version),
        ("role_principal_id", str(snapshot.principal_id)),
        ("role", snapshot.role.value),
        ("signing_principal_id", str(signed.signing_principal_id)),
        ("signing_key_version", str(signed.signing_key_version)),
        ("signed_payload_hash", str(signed.signed_payload_hash)),
        ("signature_bytes_hex", signed.signature_bytes.hex()),
    )


def _resolution_event_type(status: ReviewQueueStatus) -> str:
    if status is ReviewQueueStatus.UNDER_REVIEW:
        return "ReviewQueueItemAssigned"
    return "ReviewQueueItemResolved"


def _json_text(payload: object) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def _datetime_to_json(value: datetime) -> str:
    return value.astimezone(UTC).isoformat().replace("+00:00", "Z")
