"""
module_id: domain.types.review_queue
file: src/domain/types/review_queue.py
task_id: T-315

Authorisation review-queue value objects.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum
from typing import NewType

from domain.canonicalisation import canonical_json, canonical_sha256
from domain.security.authorisation_profile import CoveredBiologicalScope
from domain.security.identifiers import (
    ExportClass,
    InstitutionId,
    PrincipalId,
    SopLibraryId,
    UserId,
    require_non_empty,
)
from domain.security.operational_role import OperationalRole
from domain.sequence import Sha256
from domain.types.enums import BiosafetyTier, ChassisClass, DownstreamUse
from domain.types.ids import AssemblyMethodId

AuthorisationRequestId = NewType("AuthorisationRequestId", str)
ReviewQueueItemId = NewType("ReviewQueueItemId", str)
ReviewQueueDecisionId = NewType("ReviewQueueDecisionId", str)
CanonicalTextPayload = tuple[tuple[str, str], ...]


class ReviewQueueRequestKind(Enum):
    USER_EXTENSION = "user_extension"
    BLOCKED_AUTHORISATION = "blocked_authorisation"


class ReviewQueueStatus(Enum):
    PENDING = "pending"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    DENIED = "denied"
    EXPIRED = "expired"


@dataclass(frozen=True)
class AuthorisationRequest:
    request_id: AuthorisationRequestId
    request_kind: ReviewQueueRequestKind
    subject_user_id: UserId
    institution_id: InstitutionId
    requested_scope: CoveredBiologicalScope
    justification: str
    created_at_utc: datetime
    related_session_id: str | None = None
    supporting_evidence: CanonicalTextPayload = ()
    block_reason: str | None = None

    def __post_init__(self) -> None:
        require_non_empty(str(self.request_id), "request_id")
        require_non_empty(str(self.subject_user_id), "subject_user_id")
        require_non_empty(str(self.institution_id), "institution_id")
        _require_aware(self.created_at_utc, "created_at_utc")
        _require_non_empty_text(self.justification, "justification")
        _require_payload(self.supporting_evidence, "supporting_evidence")
        if self.request_kind is ReviewQueueRequestKind.BLOCKED_AUTHORISATION:
            _require_non_empty_text(self.related_session_id or "", "related_session_id")
            _require_non_empty_text(self.block_reason or "", "block_reason")

    @property
    def item_id(self) -> ReviewQueueItemId:
        return ReviewQueueItemId(str(self.request_id))

    def to_payload(self) -> dict[str, object]:
        return {
            "block_reason": self.block_reason,
            "created_at_utc": _datetime_to_json(self.created_at_utc),
            "institution_id": str(self.institution_id),
            "justification": self.justification,
            "related_session_id": self.related_session_id,
            "request_id": str(self.request_id),
            "request_kind": self.request_kind.value,
            "requested_scope": self.requested_scope.to_payload(),
            "subject_user_id": str(self.subject_user_id),
            "supporting_evidence": _payload_to_json(self.supporting_evidence),
        }

    @classmethod
    def from_payload(cls, payload: dict[str, object]) -> AuthorisationRequest:
        return cls(
            request_id=AuthorisationRequestId(_expect_str(payload, "request_id")),
            request_kind=ReviewQueueRequestKind(_expect_str(payload, "request_kind")),
            subject_user_id=UserId(_expect_str(payload, "subject_user_id")),
            institution_id=InstitutionId(_expect_str(payload, "institution_id")),
            requested_scope=_scope_from_payload(_expect_dict(payload, "requested_scope")),
            justification=_expect_str(payload, "justification"),
            created_at_utc=_parse_datetime(_expect_str(payload, "created_at_utc")),
            related_session_id=_optional_str(payload.get("related_session_id")),
            supporting_evidence=_payload_from_json(_expect_list(payload, "supporting_evidence")),
            block_reason=_optional_str(payload.get("block_reason")),
        )

    def canonical_json(self) -> bytes:
        return canonical_json(self.to_payload())

    def content_hash(self) -> Sha256:
        return canonical_sha256(self.to_payload())


@dataclass(frozen=True)
class ReviewQueueItemDecision:
    decision_id: ReviewQueueDecisionId
    item_id: ReviewQueueItemId
    decision_status: ReviewQueueStatus
    decided_by_admin_id: PrincipalId
    justification: str
    decided_at_utc: datetime
    decision_record_payload: CanonicalTextPayload
    decision_record_hash: Sha256
    assigned_admin_id: PrincipalId | None = None

    def __post_init__(self) -> None:
        require_non_empty(str(self.decision_id), "decision_id")
        require_non_empty(str(self.item_id), "item_id")
        require_non_empty(str(self.decided_by_admin_id), "decided_by_admin_id")
        if self.decision_status is ReviewQueueStatus.PENDING:
            raise ValueError("review queue decisions cannot set pending status")
        _require_non_empty_text(self.justification, "justification")
        _require_aware(self.decided_at_utc, "decided_at_utc")
        _require_payload(self.decision_record_payload, "decision_record_payload")
        require_non_empty(str(self.decision_record_hash), "decision_record_hash")
        if self.decision_status is ReviewQueueStatus.UNDER_REVIEW:
            require_non_empty(str(self.assigned_admin_id or ""), "assigned_admin_id")

    def to_payload(self) -> dict[str, object]:
        return {
            "assigned_admin_id": None
            if self.assigned_admin_id is None
            else str(self.assigned_admin_id),
            "decided_at_utc": _datetime_to_json(self.decided_at_utc),
            "decided_by_admin_id": str(self.decided_by_admin_id),
            "decision_id": str(self.decision_id),
            "decision_record_hash": str(self.decision_record_hash),
            "decision_record_payload": _payload_to_json(self.decision_record_payload),
            "decision_status": self.decision_status.value,
            "item_id": str(self.item_id),
            "justification": self.justification,
        }

    @classmethod
    def from_payload(cls, payload: dict[str, object]) -> ReviewQueueItemDecision:
        assigned_admin_id = _optional_str(payload.get("assigned_admin_id"))
        return cls(
            decision_id=ReviewQueueDecisionId(_expect_str(payload, "decision_id")),
            item_id=ReviewQueueItemId(_expect_str(payload, "item_id")),
            decision_status=ReviewQueueStatus(_expect_str(payload, "decision_status")),
            decided_by_admin_id=PrincipalId(_expect_str(payload, "decided_by_admin_id")),
            justification=_expect_str(payload, "justification"),
            decided_at_utc=_parse_datetime(_expect_str(payload, "decided_at_utc")),
            decision_record_payload=_payload_from_json(
                _expect_list(payload, "decision_record_payload")
            ),
            decision_record_hash=Sha256(_expect_str(payload, "decision_record_hash")),
            assigned_admin_id=None if assigned_admin_id is None else PrincipalId(assigned_admin_id),
        )

    def content_hash(self) -> Sha256:
        return canonical_sha256(self.to_payload())


@dataclass(frozen=True)
class ReviewQueueItem:
    item_id: ReviewQueueItemId
    request: AuthorisationRequest
    status: ReviewQueueStatus
    created_at_utc: datetime
    updated_at_utc: datetime
    assigned_admin_id: PrincipalId | None = None
    decision: ReviewQueueItemDecision | None = None

    def __post_init__(self) -> None:
        require_non_empty(str(self.item_id), "item_id")
        _require_aware(self.created_at_utc, "created_at_utc")
        _require_aware(self.updated_at_utc, "updated_at_utc")
        if self.status is ReviewQueueStatus.PENDING and self.decision is not None:
            raise ValueError("pending review queue items cannot carry a decision")
        if self.status is not ReviewQueueStatus.PENDING and self.decision is None:
            raise ValueError("non-pending review queue items require a decision")
        if self.decision is not None and self.decision.decision_status is not self.status:
            raise ValueError("review queue item status must match latest decision")

    def to_payload(self) -> dict[str, object]:
        return {
            "assigned_admin_id": None
            if self.assigned_admin_id is None
            else str(self.assigned_admin_id),
            "created_at_utc": _datetime_to_json(self.created_at_utc),
            "decision": None if self.decision is None else self.decision.to_payload(),
            "item_id": str(self.item_id),
            "request": self.request.to_payload(),
            "status": self.status.value,
            "updated_at_utc": _datetime_to_json(self.updated_at_utc),
        }

    @property
    def is_open(self) -> bool:
        return self.status in {ReviewQueueStatus.PENDING, ReviewQueueStatus.UNDER_REVIEW}


def _scope_from_payload(payload: dict[str, object]) -> CoveredBiologicalScope:
    insert_size = payload.get("insert_size_range_bp")
    return CoveredBiologicalScope(
        covered_biosafety_tiers=frozenset(
            BiosafetyTier(item) for item in _expect_str_list(payload, "covered_biosafety_tiers")
        ),
        covered_host_classes=frozenset(
            ChassisClass(item) for item in _expect_str_list(payload, "covered_host_classes")
        ),
        covered_assembly_chemistries=frozenset(
            AssemblyMethodId(item)
            for item in _expect_str_list(payload, "covered_assembly_chemistries")
        ),
        covered_downstream_uses=frozenset(
            DownstreamUse(item) for item in _expect_str_list(payload, "covered_downstream_uses")
        ),
        covered_sop_libraries=frozenset(
            SopLibraryId(item) for item in _expect_str_list(payload, "covered_sop_libraries")
        ),
        covered_vendor_submission=_expect_bool(payload, "covered_vendor_submission"),
        covered_export_classes=frozenset(
            ExportClass(item) for item in _expect_str_list(payload, "covered_export_classes")
        ),
        role_of_operation_allowed=frozenset(
            OperationalRole(item) for item in _expect_str_list(payload, "role_of_operation_allowed")
        ),
        cargo_classes=frozenset(_expect_str_list(payload, "cargo_classes")),
        vector_system_classes=frozenset(_expect_str_list(payload, "vector_system_classes")),
        replication_competence=frozenset(_expect_str_list(payload, "replication_competence")),
        insert_size_range_bp=None
        if insert_size is None
        else _expect_int_pair(insert_size, "insert_size_range_bp"),
        target_organisms=frozenset(_expect_str_list(payload, "target_organisms")),
        screening_exception_classes=frozenset(
            _expect_str_list(payload, "screening_exception_classes")
        ),
        institutional_protocol_ids=frozenset(
            _expect_str_list(payload, "institutional_protocol_ids")
        ),
        jurisdictions=frozenset(_expect_str_list(payload, "jurisdictions")),
        component_lineage_trust=frozenset(_expect_str_list(payload, "component_lineage_trust")),
    )


def _payload_to_json(payload: CanonicalTextPayload) -> list[list[str]]:
    return [[key, value] for key, value in payload]


def _payload_from_json(payload: list[object]) -> CanonicalTextPayload:
    parsed: list[tuple[str, str]] = []
    for item in payload:
        pair = _expect_list_item(item, "payload item")
        if len(pair) != 2:
            raise TypeError("payload items must be key/value pairs")
        key = _expect_str_item(pair[0], "payload key")
        value = _expect_str_item(pair[1], "payload value")
        parsed.append((key, value))
    return tuple(parsed)


def _require_payload(payload: CanonicalTextPayload, field_name: str) -> None:
    for key, value in payload:
        require_non_empty(key, f"{field_name} key")
        require_non_empty(value, f"{field_name} value")


def _expect_dict(payload: dict[str, object], key: str) -> dict[str, object]:
    value = payload.get(key)
    if not isinstance(value, dict):
        raise TypeError(f"{key} must be a JSON object")
    return dict(value)


def _expect_str(payload: dict[str, object], key: str) -> str:
    return _expect_str_item(payload.get(key), key)


def _expect_str_item(value: object, field_name: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be a string")
    return value


def _expect_bool(payload: dict[str, object], key: str) -> bool:
    value = payload.get(key)
    if not isinstance(value, bool):
        raise TypeError(f"{key} must be a boolean")
    return value


def _expect_list(payload: dict[str, object], key: str) -> list[object]:
    return _expect_list_item(payload.get(key), key)


def _expect_list_item(value: object, field_name: str) -> list[object]:
    if not isinstance(value, list):
        raise TypeError(f"{field_name} must be a list")
    return value


def _expect_str_list(payload: dict[str, object], key: str) -> list[str]:
    return [_expect_str_item(item, key) for item in _expect_list(payload, key)]


def _expect_int_pair(value: object, field_name: str) -> tuple[int, int]:
    items = _expect_list_item(value, field_name)
    if len(items) != 2:
        raise TypeError(f"{field_name} must contain two integers")
    lower, upper = items
    if not isinstance(lower, int) or not isinstance(upper, int):
        raise TypeError(f"{field_name} must contain two integers")
    return lower, upper


def _optional_str(value: object) -> str | None:
    if value is None:
        return None
    return _expect_str_item(value, "optional string")


def _require_non_empty_text(value: str, field_name: str) -> None:
    if not value.strip():
        raise ValueError(f"{field_name} cannot be empty")


def _require_aware(value: datetime, field_name: str) -> None:
    if value.tzinfo is None:
        raise ValueError(f"{field_name} must be timezone-aware")


def _datetime_to_json(value: datetime) -> str:
    return value.astimezone(UTC).isoformat().replace("+00:00", "Z")


def _parse_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)
